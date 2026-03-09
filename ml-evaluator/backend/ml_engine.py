import pandas as pd
import numpy as np
import io
import re
import time
from sentence_transformers import SentenceTransformer, CrossEncoder, util

# ─── Model Configuration ──────────────────────────────────────────────────────
# Fast + accurate bi-encoder (80MB, 6× faster than mpnet on CPU)
BI_ENCODER_MODEL = 'all-MiniLM-L6-v2'
# Lightweight cross-encoder for precise re-ranking
CROSS_ENCODER_MODEL = 'cross-encoder/ms-marco-MiniLM-L-6-v2'

# Cross-encoder is expensive: skip it when candidates × criteria > this limit
CROSS_ENCODER_PAIR_LIMIT = 300

device = 'cpu'
bi_encoder = None
cross_encoder = None

try:
    print(f"[1/2] Loading Bi-Encoder: {BI_ENCODER_MODEL} …")
    bi_encoder = SentenceTransformer(BI_ENCODER_MODEL, device=device)
    print(f"      ✓ Bi-Encoder ready")
except Exception as e:
    print(f"      ✗ Bi-Encoder failed: {e}")

try:
    print(f"[2/2] Loading Cross-Encoder: {CROSS_ENCODER_MODEL} …")
    cross_encoder = CrossEncoder(CROSS_ENCODER_MODEL, device=device)
    print(f"      ✓ Cross-Encoder ready")
except Exception as e:
    print(f"      ✗ Cross-Encoder unavailable (falling back to bi-encoder only): {e}")


# ─── Comprehensive Technical Keyword Dictionary ───────────────────────────────
TECH_TERMS = {
    # Programming Languages
    'python', 'java', 'javascript', 'typescript', 'golang', 'go', 'rust',
    'c++', 'cpp', 'c#', 'csharp', 'ruby', 'php', 'swift', 'kotlin', 'scala',
    'r', 'matlab', 'perl', 'shell', 'bash', 'powershell', 'lua', 'haskell',
    'elixir', 'clojure', 'dart',
    # Web Frameworks
    'react', 'reactjs', 'angular', 'vue', 'vuejs', 'svelte', 'django',
    'flask', 'fastapi', 'spring', 'springboot', 'express', 'expressjs',
    'node', 'nodejs', 'next', 'nextjs', 'nuxt', 'rails', 'laravel',
    'dotnet', 'asp.net', 'gin', 'fiber', 'actix', 'phoenix',
    # ML / AI
    'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'sklearn', 'pandas',
    'numpy', 'transformers', 'huggingface', 'opencv', 'spacy', 'nltk',
    'xgboost', 'lightgbm', 'machine learning', 'deep learning',
    'neural network', 'nlp', 'computer vision', 'reinforcement learning',
    'generative ai', 'llm', 'gpt', 'bert',
    # Databases
    'sql', 'nosql', 'postgres', 'postgresql', 'mysql', 'mongodb', 'redis',
    'memcached', 'cassandra', 'dynamodb', 'elasticsearch', 'opensearch',
    'sqlite', 'oracle', 'mariadb', 'neo4j', 'influxdb', 'cockroachdb',
    'supabase', 'firebase',
    # Cloud & Infra
    'docker', 'kubernetes', 'k8s', 'aws', 'amazon web services', 'azure',
    'gcp', 'google cloud', 'terraform', 'ansible', 'puppet', 'chef',
    'cloudformation', 'pulumi', 'helm', 'istio', 'envoy',
    # DevOps / CI-CD
    'jenkins', 'ci/cd', 'cicd', 'github actions', 'gitlab ci', 'circleci',
    'argocd', 'spinnaker', 'tekton',
    # Messaging / Streaming
    'kafka', 'rabbitmq', 'sqs', 'sns', 'nats', 'pulsar', 'kinesis',
    'event-driven', 'pub/sub', 'pubsub', 'message queue', 'streaming',
    # Web & API
    'rest', 'restful', 'graphql', 'grpc', 'websocket', 'api',
    'microservices', 'serverless', 'lambda', 'oauth', 'jwt', 'openapi',
    # Architecture
    'distributed systems', 'distributed', 'scalable', 'architecture',
    'design patterns', 'solid', 'clean architecture', 'domain driven',
    'ddd', 'cqrs', 'event sourcing', 'saga', 'circuit breaker',
    'load balancing', 'high availability', 'fault tolerance',
    'cap theorem', 'eventual consistency',
    # Testing & Quality
    'tdd', 'test driven', 'bdd', 'unit test', 'integration test', 'e2e',
    'selenium', 'cypress', 'jest', 'pytest', 'junit', 'testing',
    'code review', 'quality assurance', 'qa',
    # Security
    'security', 'encryption', 'authentication', 'authorization', 'ssl',
    'tls', 'https', 'firewall', 'waf', 'penetration testing', 'owasp',
    'sso', 'saml', 'rbac', 'zero trust',
    # Observability
    'monitoring', 'logging', 'observability', 'prometheus', 'grafana',
    'datadog', 'splunk', 'elk', 'kibana', 'jaeger', 'opentelemetry',
    # Methodologies
    'agile', 'scrum', 'kanban', 'devops', 'sre', 'gitops',
    # Infra misc
    'containers', 'orchestration', 'deployment', 'pipeline',
    'performance', 'optimization', 'caching', 'cdn', 'profiling',
    'nginx', 'apache', 'linux', 'networking',
    # Data Eng
    'etl', 'data pipeline', 'data warehouse', 'data lake', 'spark',
    'hadoop', 'airflow', 'dbt', 'snowflake', 'redshift', 'bigquery',
    # Version Control
    'git', 'github', 'gitlab', 'bitbucket',
    # Mobile
    'ios', 'android', 'react native', 'flutter', 'mobile',
}


# ──────────────────────────────────────────────────────────────────────────────
#  Helper functions  (optimised for speed)
# ──────────────────────────────────────────────────────────────────────────────

# Pre-split terms into single-word (set lookup) vs multi-word (compiled regex)
_SINGLE_TERMS = {t for t in TECH_TERMS if ' ' not in t and '/' not in t}
_MULTI_TERMS  = sorted([t for t in TECH_TERMS if ' ' in t or '/' in t], key=len, reverse=True)
_MULTI_RE     = re.compile('|'.join(re.escape(t) for t in _MULTI_TERMS), re.IGNORECASE) if _MULTI_TERMS else None
_CAP_RE       = re.compile(r'\b[A-Z][a-zA-Z0-9]{2,}\b')
_FILLER_WORDS = frozenset({
    'the', 'and', 'for', 'with', 'that', 'this', 'from', 'have',
    'has', 'are', 'was', 'were', 'been', 'being', 'not', 'but',
    'all', 'can', 'will', 'may', 'who', 'how', 'our', 'their',
    'also', 'than', 'just', 'very', 'much', 'some', 'any', 'each',
    'such', 'about', 'should', 'would', 'could', 'into', 'over',
    'under', 'between', 'through', 'during', 'before', 'after',
    'above', 'below', 'both', 'other', 'only', 'same', 'then',
    'when', 'where', 'what', 'which', 'while', 'most',
})

def extract_tech_keywords(text: str) -> set:
    """Fast keyword extraction using set-lookup + one compiled regex."""
    found = set()
    # Single-word terms: tokenise once, intersect with set (O(n) not O(n*m))
    words = set(re.findall(r'[a-zA-Z0-9#+.]+', text.lower()))
    found.update(words & _SINGLE_TERMS)
    # Multi-word terms: single compiled regex pass
    if _MULTI_RE:
        found.update(m.lower() for m in _MULTI_RE.findall(text))
    # Capitalised product names not already matched
    for cap in _CAP_RE.findall(text):
        cl = cap.lower()
        if cl not in _FILLER_WORDS:
            found.add(cl)
    return found


def parse_rubric_criteria(rubric_text: str) -> list:
    """
    Parse rubric text into individual criteria with priority detection.
    Returns list of dicts: {text, priority, keywords, weight}
    """
    # Split on bullets / numbers / newlines
    raw = re.split(r'\n+|\s*[\*\-•–]\s+|\s*\d+[\.\)]\s+', rubric_text)
    raw = [p.strip() for p in raw if len(p.strip()) > 5]

    skip_starts = [
        'we are looking', 'the ideal candidate', 'looking for',
        'about the role', 'job description', 'requirements include',
        'the candidate should', 'the candidate must',
    ]

    criteria = []
    for point in raw:
        if len(point.split()) < 3:
            continue
        lower = point.lower()
        if any(lower.startswith(s) for s in skip_starts):
            continue

        # Priority detection
        must_kw = ['must', 'required', 'essential', 'critical', 'mandatory', 'strong']
        nice_kw = ['preferred', 'nice to have', 'bonus', 'plus', 'ideally', 'optional']
        if any(k in lower for k in must_kw):
            priority, weight = 'must-have', 1.5
        elif any(k in lower for k in nice_kw):
            priority, weight = 'nice-to-have', 0.7
        else:
            priority, weight = 'normal', 1.0

        criteria.append({
            'text': point,
            'priority': priority,
            'keywords': extract_tech_keywords(point),
            'weight': weight,
        })

    if not criteria:
        return [{
            'text': rubric_text.strip(),
            'priority': 'normal',
            'keywords': extract_tech_keywords(rubric_text),
            'weight': 1.0,
        }]
    return criteria


def detect_columns(df: pd.DataFrame):
    """Return (name_col, response_col) after smart auto-detection."""
    text_cols = [c for c in df.columns if df[c].dtype == object]
    name_col = response_col = None

    for col in text_cols:
        cl = str(col).lower().strip()
        if any(t in cl for t in ['name', 'candidate', 'applicant', 'person']):
            name_col = col
        if any(t in cl for t in ['response', 'answer', 'text', 'description',
                                  'resume', 'summary', 'experience', 'skills',
                                  'qualification', 'background', 'about']):
            response_col = col

    if not name_col:
        name_col = text_cols[0] if text_cols else df.columns[0]
    if not response_col:
        best, best_len = None, 0
        for col in text_cols:
            if col == name_col:
                continue
            avg = df[col].astype(str).apply(len).mean()
            if avg > best_len:
                best, best_len = col, avg
        response_col = best or (text_cols[-1] if len(text_cols) > 1 else text_cols[0])
    return name_col, response_col


def build_full_response(row, name_col: str, text_cols: list) -> str:
    """Merge every text column (except name) into one string."""
    parts = []
    for col in text_cols:
        if col == name_col:
            continue
        val = str(row[col]).strip()
        if val and val.lower() not in ('nan', 'none', '', 'n/a', '-'):
            parts.append(val)
    return ' '.join(parts)


def sigmoid(x):
    x = np.asarray(x, dtype=np.float64)
    return np.where(x >= 0,
                    1 / (1 + np.exp(-x)),
                    np.exp(x) / (1 + np.exp(x)))


# ──────────────────────────────────────────────────────────────────────────────
#  Core evaluation
# ──────────────────────────────────────────────────────────────────────────────

def evaluate_with_strict_model(
    candidates_df: pd.DataFrame,
    rubric_text: str,
    strictness_threshold: float = 0.55,
):
    """
    Multi-signal evaluation pipeline:
      Bi-Encoder (fast semantic) + Cross-Encoder (precise) + Keyword overlap
      → per-criterion scores → weighted aggregate → calibrated decision.
    """
    if bi_encoder is None:
        raise RuntimeError("Bi-encoder model failed to load — cannot evaluate.")

    # ── 1. Parse rubric ──────────────────────────────────────────────────
    criteria = parse_rubric_criteria(rubric_text)
    all_rubric_kw = set()
    for c in criteria:
        all_rubric_kw.update(c['keywords'])

    print(f"\n{'=' * 60}")
    print(f"Parsed {len(criteria)} rubric criteria:")
    for idx, c in enumerate(criteria):
        print(f"  [{idx+1}] (w={c['weight']:.1f}) {c['text'][:80]}")
        print(f"       kw: {c['keywords']}")
    print(f"All rubric keywords ({len(all_rubric_kw)}): {all_rubric_kw}")
    print(f"{'=' * 60}\n")

    # ── 2. Detect columns & build texts ──────────────────────────────────
    name_col, resp_col = detect_columns(candidates_df)
    text_cols = [c for c in candidates_df.columns if candidates_df[c].dtype == object]

    names = candidates_df[name_col].fillna("Unknown").astype(str).tolist()
    responses = [
        build_full_response(row, name_col, text_cols)
        for _, row in candidates_df.iterrows()
    ]
    if not responses:
        return []

    n_cand = len(responses)
    n_crit = len(criteria)
    crit_texts = [c['text'] for c in criteria]
    crit_weights = np.array([c['weight'] for c in criteria])

    # ── 3. Bi-Encoder embeddings (fast — batched) ────────────────────────
    t0 = time.time()
    crit_emb = bi_encoder.encode(crit_texts, batch_size=64,
                                  convert_to_tensor=True,
                                  normalize_embeddings=True)
    resp_emb = bi_encoder.encode(responses, batch_size=256,
                                  convert_to_tensor=True,
                                  normalize_embeddings=True,
                                  show_progress_bar=False)
    bi_scores = util.dot_score(resp_emb, crit_emb).cpu().numpy()
    print(f"⚡ Bi-encoder done in {time.time()-t0:.2f}s  ({n_cand} candidates × {n_crit} criteria)")

    # ── 4. Cross-Encoder (precise but slow — auto-skip for large sets) ───
    total_pairs = n_cand * n_crit
    use_cross = cross_encoder is not None and total_pairs <= CROSS_ENCODER_PAIR_LIMIT
    cx_scores = np.zeros((n_cand, n_crit))
    if use_cross:
        t1 = time.time()
        pairs = [(responses[i], crit_texts[j])
                 for i in range(n_cand) for j in range(n_crit)]
        raw = cross_encoder.predict(pairs, batch_size=128,
                                    show_progress_bar=False)
        cx_scores = sigmoid(np.array(raw).reshape(n_cand, n_crit))
        print(f"⚡ Cross-encoder done in {time.time()-t1:.2f}s  ({total_pairs} pairs)")
    else:
        reason = "too many pairs" if cross_encoder else "unavailable"
        print(f"⏩ Cross-encoder skipped ({reason}: {total_pairs} pairs > {CROSS_ENCODER_PAIR_LIMIT}) — bi-encoder only")

    # ── 5. Adaptive thresholds (tuned by strictness 0–1) ────────────────
    POINT_PASS    = 0.25 + strictness_threshold * 0.20   # 0.25 – 0.45
    HIRE_THRESH   = 0.42 + strictness_threshold * 0.18   # 0.42 – 0.60
    BORDER_THRESH = 0.28 + strictness_threshold * 0.14   # 0.28 – 0.42

    print(f"Thresholds  (strictness={strictness_threshold:.2f}):")
    print(f"  POINT_PASS={POINT_PASS:.2f}  HIRE={HIRE_THRESH:.2f}  "
          f"BORDERLINE={BORDER_THRESH:.2f}")

    # ── 6. Pre-extract all candidate keywords (batch, once) ────────────
    t2 = time.time()
    all_cand_kw = [extract_tech_keywords(r) for r in responses]
    print(f"⚡ Keyword extraction done in {time.time()-t2:.2f}s")

    # ── 7. Score each candidate ──────────────────────────────────────────
    results = []
    for i in range(n_cand):
        cand_kw = all_cand_kw[i]
        point_details = []
        weighted_pts = []

        for j in range(n_crit):
            bi_s  = float(bi_scores[i][j])
            cx_s  = float(cx_scores[i][j])
            ckw   = criteria[j]['keywords']
            kw_ov = (len(ckw & cand_kw) / len(ckw)) if ckw else 0.0

            # Combine signals — adapt weights based on whether cross-encoder ran
            if use_cross:
                pt_score = 0.50 * cx_s + 0.30 * bi_s + 0.20 * kw_ov
            else:
                pt_score = 0.55 * bi_s + 0.45 * kw_ov

            point_details.append({
                'rubric_point': crit_texts[j],
                'score': round(pt_score, 4),
                'bi_score': round(bi_s, 4),
                'cross_score': round(cx_s, 4),
                'keyword_overlap': round(kw_ov, 4),
                'matched_keywords': sorted(ckw & cand_kw),
                'passed': pt_score >= POINT_PASS,
            })
            weighted_pts.append(pt_score * crit_weights[j])

        pt_arr = np.array([p['score'] for p in point_details])

        # --- Aggregate signals ---
        w_mean    = np.sum(weighted_pts) / np.sum(crit_weights)
        coverage  = np.mean([1.0 if p['passed'] else 0.0 for p in point_details])
        top_k     = max(1, n_crit // 2)
        strength  = float(np.mean(sorted(pt_arr, reverse=True)[:top_k]))
        global_kw = (len(all_rubric_kw & cand_kw) / len(all_rubric_kw)) if all_rubric_kw else 0.0
        depth     = min(1.0, len(responses[i].split()) / 20.0)

        final = (
            0.35 * w_mean +
            0.25 * coverage +
            0.20 * strength +
            0.10 * global_kw +
            0.10 * depth
        )
        final = min(final, 0.99)

        # Decision
        if final >= HIRE_THRESH:
            decision = "Hire"
        elif final >= BORDER_THRESH:
            decision = "Borderline"
        else:
            decision = "Reject"

        # --- Build reasoning ---
        matched_kw_all = sorted(all_rubric_kw & cand_kw)
        sorted_pts = sorted(point_details, key=lambda x: x['score'], reverse=True)

        reason_lines = []
        if decision == "Hire":
            reason_lines.append(
                f"✅ Strong candidate — {coverage*100:.0f}% rubric coverage, "
                f"{final*100:.1f}% overall alignment."
            )
        elif decision == "Borderline":
            reason_lines.append(
                f"⚠️ Borderline — {coverage*100:.0f}% rubric coverage, "
                f"{final*100:.1f}% alignment. Some gaps present."
            )
        else:
            reason_lines.append(
                f"❌ Below threshold — {coverage*100:.0f}% coverage, "
                f"{final*100:.1f}% alignment."
            )

        if matched_kw_all:
            reason_lines.append(f"Matched terms: {', '.join(matched_kw_all[:10])}.")
        else:
            reason_lines.append("No key technical terms matched.")

        if sorted_pts:
            best = sorted_pts[0]
            reason_lines.append(
                f"Strongest area: \"{best['rubric_point'][:70]}\" "
                f"({best['score']*100:.0f}%)."
            )
        if len(sorted_pts) > 1:
            worst = sorted_pts[-1]
            if not worst['passed']:
                reason_lines.append(
                    f"Weakest area: \"{worst['rubric_point'][:70]}\" "
                    f"({worst['score']*100:.0f}%)."
                )

        results.append({
            "id": str(i + 1),
            "name": names[i],
            "score": round(final * 100, 2),
            "decision": decision,
            "reason": "\n".join(reason_lines),
            "response_snippet": (responses[i][:150] + "…")
                if len(responses[i]) > 150 else responses[i],
            "point_scores": point_details,
            "coverage": round(coverage * 100, 1),
            "keyword_match_rate": round(global_kw * 100, 1),
        })

        # Debug log
        print(f"\n{'─' * 55}")
        print(f"  Candidate {i+1}: {names[i]}")
        print(f"  wMean={w_mean:.3f}  coverage={coverage:.2f}  "
              f"strength={strength:.3f}  kwCov={global_kw:.2f}  depth={depth:.2f}")
        print(f"  ★ FINAL={final:.4f}  →  {decision}")
        for pd_ in point_details:
            tag = "✓" if pd_['passed'] else "✗"
            print(f"    {tag} [{pd_['score']:.3f}] bi={pd_['bi_score']:.2f} "
                  f"cx={pd_['cross_score']:.2f} kw={pd_['keyword_overlap']:.2f}  "
                  f"{pd_['rubric_point'][:55]}")

    total_time = time.time() - t0
    print(f"\n🏁 Total evaluation: {total_time:.2f}s for {n_cand} candidates")
    return results


# ──────────────────────────────────────────────────────────────────────────────
#  Entry point called from FastAPI
# ──────────────────────────────────────────────────────────────────────────────

def process_evaluation_request(
    candidates_file_bytes: bytes,
    rubric_text: bytes,
    candidates_filename: str,
):
    try:
        if candidates_filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(candidates_file_bytes))
        else:
            df = pd.read_excel(io.BytesIO(candidates_file_bytes))

        text = rubric_text.decode('utf-8', errors='ignore')
        results = evaluate_with_strict_model(df, text, strictness_threshold=0.55)

        return {
            "status": "success",
            "data": results,
            "summary": {
                "total": len(results),
                "hired": sum(1 for r in results if r['decision'] == 'Hire'),
                "borderline": sum(1 for r in results if r['decision'] == 'Borderline'),
                "rejected": sum(1 for r in results if r['decision'] == 'Reject'),
            },
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}
