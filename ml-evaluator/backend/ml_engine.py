import pandas as pd
import numpy as np
import io
import re
import time
from concurrent.futures import ThreadPoolExecutor
from sentence_transformers import SentenceTransformer, CrossEncoder, util

# --- Model Configuration ---
BI_ENCODER_MODEL = 'all-MiniLM-L6-v2'
CROSS_ENCODER_MODEL = 'cross-encoder/ms-marco-MiniLM-L-6-v2'
CROSS_ENCODER_PAIR_LIMIT = 500

device = 'cpu'
bi_encoder = None
cross_encoder = None

try:
    print(f"[1/2] Loading Bi-Encoder: {BI_ENCODER_MODEL}")
    bi_encoder = SentenceTransformer(BI_ENCODER_MODEL, device=device)
    bi_encoder.encode(["warm-up"], normalize_embeddings=True, show_progress_bar=False)
    print("      Bi-Encoder ready (warmed)")
except Exception as e:
    print(f"      Bi-Encoder failed: {e}")

try:
    print(f"[2/2] Loading Cross-Encoder: {CROSS_ENCODER_MODEL}")
    cross_encoder = CrossEncoder(CROSS_ENCODER_MODEL, device=device)
    cross_encoder.predict([("warm", "up")], show_progress_bar=False)
    print("      Cross-Encoder ready (warmed)")
except Exception as e:
    print(f"      Cross-Encoder unavailable: {e}")


TECH_TERMS = {
    'python', 'java', 'javascript', 'typescript', 'golang', 'go', 'rust',
    'c++', 'cpp', 'c#', 'csharp', 'ruby', 'php', 'swift', 'kotlin', 'scala',
    'r', 'matlab', 'perl', 'shell', 'bash', 'powershell', 'lua', 'haskell',
    'elixir', 'clojure', 'dart',
    'react', 'reactjs', 'angular', 'vue', 'vuejs', 'svelte', 'django',
    'flask', 'fastapi', 'spring', 'springboot', 'express', 'expressjs',
    'node', 'nodejs', 'next', 'nextjs', 'nuxt', 'rails', 'laravel',
    'dotnet', 'asp.net', 'gin', 'fiber', 'actix', 'phoenix',
    'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'sklearn', 'pandas',
    'numpy', 'transformers', 'huggingface', 'opencv', 'spacy', 'nltk',
    'xgboost', 'lightgbm', 'machine learning', 'deep learning',
    'neural network', 'nlp', 'computer vision', 'reinforcement learning',
    'generative ai', 'llm', 'gpt', 'bert',
    'sql', 'nosql', 'postgres', 'postgresql', 'mysql', 'mongodb', 'redis',
    'memcached', 'cassandra', 'dynamodb', 'elasticsearch', 'opensearch',
    'sqlite', 'oracle', 'mariadb', 'neo4j', 'influxdb', 'cockroachdb',
    'supabase', 'firebase',
    'docker', 'kubernetes', 'k8s', 'aws', 'amazon web services', 'azure',
    'gcp', 'google cloud', 'terraform', 'ansible', 'puppet', 'chef',
    'cloudformation', 'pulumi', 'helm', 'istio', 'envoy',
    'jenkins', 'ci/cd', 'cicd', 'github actions', 'gitlab ci', 'circleci',
    'argocd', 'spinnaker', 'tekton',
    'kafka', 'rabbitmq', 'sqs', 'sns', 'nats', 'pulsar', 'kinesis',
    'event-driven', 'pub/sub', 'pubsub', 'message queue', 'streaming',
    'rest', 'restful', 'graphql', 'grpc', 'websocket', 'api',
    'microservices', 'serverless', 'lambda', 'oauth', 'jwt', 'openapi',
    'distributed systems', 'distributed', 'scalable', 'architecture',
    'design patterns', 'solid', 'clean architecture', 'domain driven',
    'ddd', 'cqrs', 'event sourcing', 'saga', 'circuit breaker',
    'load balancing', 'high availability', 'fault tolerance',
    'cap theorem', 'eventual consistency',
    'tdd', 'test driven', 'bdd', 'unit test', 'integration test', 'e2e',
    'selenium', 'cypress', 'jest', 'pytest', 'junit', 'testing',
    'code review', 'quality assurance', 'qa',
    'security', 'encryption', 'authentication', 'authorization', 'ssl',
    'tls', 'https', 'firewall', 'waf', 'penetration testing', 'owasp',
    'sso', 'saml', 'rbac', 'zero trust',
    'monitoring', 'logging', 'observability', 'prometheus', 'grafana',
    'datadog', 'splunk', 'elk', 'kibana', 'jaeger', 'opentelemetry',
    'agile', 'scrum', 'kanban', 'devops', 'sre', 'gitops',
    'containers', 'orchestration', 'deployment', 'pipeline',
    'performance', 'optimization', 'caching', 'cdn', 'profiling',
    'nginx', 'apache', 'linux', 'networking',
    'etl', 'data pipeline', 'data warehouse', 'data lake', 'spark',
    'hadoop', 'airflow', 'dbt', 'snowflake', 'redshift', 'bigquery',
    'git', 'github', 'gitlab', 'bitbucket',
    'ios', 'android', 'react native', 'flutter', 'mobile',
}

SENIOR_INDICATORS = frozenset({
    'architect', 'lead', 'principal', 'senior', 'staff', 'director',
    'design', 'scale', 'mentor', 'strategy', 'ownership', 'roadmap',
    'enterprise', 'production', 'mission critical',
    'distributed systems', 'high availability', 'fault tolerance', 'large scale',
})
JUNIOR_INDICATORS = frozenset({
    'learning', 'beginner', 'basic', 'simple', 'tutorial', 'course',
    'intern', 'junior', 'entry', 'student', 'familiar with',
    'some experience', 'a little', 'getting started', 'not built', 'never used',
})

_SINGLE_TERMS = frozenset(t for t in TECH_TERMS if ' ' not in t and '/' not in t)
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
    found = set()
    words = set(re.findall(r'[a-zA-Z0-9#+.]+', text.lower()))
    found.update(words & _SINGLE_TERMS)
    if _MULTI_RE:
        found.update(m.lower() for m in _MULTI_RE.findall(text))
    for cap in _CAP_RE.findall(text):
        cl = cap.lower()
        if cl not in _FILLER_WORDS:
            found.add(cl)
    return found


def detect_experience_level(text: str) -> dict:
    lower = text.lower()
    words = set(re.findall(r'[a-z]+', lower))
    sr = len(SENIOR_INDICATORS & words)
    jr = len(JUNIOR_INDICATORS & words)
    for phrase in SENIOR_INDICATORS:
        if ' ' in phrase and phrase in lower:
            sr += 2
    for phrase in JUNIOR_INDICATORS:
        if ' ' in phrase and phrase in lower:
            jr += 2
    total = sr + jr or 1
    level = "Senior" if sr > jr + 1 else "Junior" if jr > sr + 1 else "Mid-Level"
    confidence = abs(sr - jr) / total
    return {"level": level, "senior_signals": sr, "junior_signals": jr,
            "confidence": round(min(confidence, 1.0), 2)}


def parse_rubric_criteria(rubric_text: str) -> list:
    raw = re.split(r'\n+|\s*[\*\-\u2022\u2013]\s+|\s*\d+[\.\)]\s+', rubric_text)
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
        must_kw = ['must', 'required', 'essential', 'critical', 'mandatory', 'strong']
        nice_kw = ['preferred', 'nice to have', 'bonus', 'plus', 'ideally', 'optional']
        if any(k in lower for k in must_kw):
            priority, weight = 'must-have', 1.5
        elif any(k in lower for k in nice_kw):
            priority, weight = 'nice-to-have', 0.7
        else:
            priority, weight = 'normal', 1.0
        criteria.append({
            'text': point, 'priority': priority,
            'keywords': extract_tech_keywords(point), 'weight': weight,
        })
    if not criteria:
        return [{'text': rubric_text.strip(), 'priority': 'normal',
                 'keywords': extract_tech_keywords(rubric_text), 'weight': 1.0}]
    return criteria


def detect_columns(df):
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


def build_full_response(row, name_col, text_cols):
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
    return np.where(x >= 0, 1 / (1 + np.exp(-x)), np.exp(x) / (1 + np.exp(x)))


def evaluate_with_strict_model(candidates_df, rubric_text, strictness_threshold=0.60):
    if bi_encoder is None:
        raise RuntimeError("Bi-encoder model failed to load.")
    t_start = time.time()

    criteria = parse_rubric_criteria(rubric_text)
    all_rubric_kw = set()
    for c in criteria:
        all_rubric_kw.update(c['keywords'])

    name_col, resp_col = detect_columns(candidates_df)
    text_cols = [c for c in candidates_df.columns if candidates_df[c].dtype == object]
    names = candidates_df[name_col].fillna("Unknown").astype(str).tolist()
    responses = [build_full_response(row, name_col, text_cols) for _, row in candidates_df.iterrows()]
    if not responses:
        return [], 0.0

    n_cand = len(responses)
    n_crit = len(criteria)
    crit_texts = [c['text'] for c in criteria]
    crit_weights = np.array([c['weight'] for c in criteria])

    # Bi-Encoder (batched, fast)
    t0 = time.time()
    crit_emb = bi_encoder.encode(crit_texts, batch_size=64, convert_to_tensor=True, normalize_embeddings=True)
    resp_emb = bi_encoder.encode(responses, batch_size=512, convert_to_tensor=True, normalize_embeddings=True, show_progress_bar=False)
    bi_scores = util.dot_score(resp_emb, crit_emb).cpu().numpy()
    t_bi = time.time() - t0

    # Cross-Encoder (precise)
    total_pairs = n_cand * n_crit
    use_cross = cross_encoder is not None and total_pairs <= CROSS_ENCODER_PAIR_LIMIT
    cx_scores = np.zeros((n_cand, n_crit))
    t_cx = 0.0
    if use_cross:
        t1 = time.time()
        pairs = [(responses[i], crit_texts[j]) for i in range(n_cand) for j in range(n_crit)]
        raw = cross_encoder.predict(pairs, batch_size=256, show_progress_bar=False)
        cx_scores = sigmoid(np.array(raw).reshape(n_cand, n_crit))
        t_cx = time.time() - t1

    # Parallel keyword + experience extraction
    t2 = time.time()
    with ThreadPoolExecutor(max_workers=min(8, n_cand)) as pool:
        all_cand_kw = list(pool.map(extract_tech_keywords, responses))
        all_exp_levels = list(pool.map(detect_experience_level, responses))
    t_kw = time.time() - t2

    # Calibrated thresholds per PRD (multi-gate) - LENIENT MODE
    POINT_PASS    = 0.08 + strictness_threshold * 0.10  # Reduced from 0.10 + 0.14
    SELECTED_THRESH = 0.55      # Lowered from 0.65 - SELECTED
    BORDERLINE_THRESH = 0.30    # Lowered from 0.40 - BORDERLINE  
    REJECTED_THRESH = 0.12      # Lowered from 0.18 - REJECTED (anything below is HARD REJECTED)
    MIN_COVERAGE_HIRE   = 0.18  # Lowered from 0.25
    MIN_KW_HIRE         = 0.08  # Lowered from 0.12
    MIN_COVERAGE_BORDER = 0.08  # Lowered from 0.10
    MIN_QUALIFY         = 0.12  # Lowered from 0.18 - Hard reject floor

    results = []
    for i in range(n_cand):
        cand_kw = all_cand_kw[i]
        exp_info = all_exp_levels[i]
        point_details = []
        weighted_pts = []

        for j in range(n_crit):
            bi_s  = float(bi_scores[i][j])
            cx_s  = float(cx_scores[i][j])
            ckw   = criteria[j]['keywords']
            kw_ov = (len(ckw & cand_kw) / len(ckw)) if ckw else 0.0

            if use_cross:
                pt_score = 0.45 * cx_s + 0.30 * bi_s + 0.25 * kw_ov
            else:
                pt_score = 0.50 * bi_s + 0.50 * kw_ov

            point_details.append({
                'rubric_point': crit_texts[j], 'score': round(pt_score, 4),
                'bi_score': round(bi_s, 4), 'cross_score': round(cx_s, 4),
                'keyword_overlap': round(kw_ov, 4),
                'matched_keywords': sorted(ckw & cand_kw),
                'passed': pt_score >= POINT_PASS, 'priority': criteria[j]['priority'],
            })
            weighted_pts.append(pt_score * crit_weights[j])

        pt_arr = np.array([p['score'] for p in point_details])
        w_mean    = np.sum(weighted_pts) / np.sum(crit_weights)
        coverage  = np.mean([1.0 if p['passed'] else 0.0 for p in point_details])
        top_k     = max(1, n_crit // 2)
        strength  = float(np.mean(sorted(pt_arr, reverse=True)[:top_k]))
        global_kw = (len(all_rubric_kw & cand_kw) / len(all_rubric_kw)) if all_rubric_kw else 0.0
        depth     = min(1.0, len(responses[i].split()) / 25.0)
        consistency = 1.0 - min(1.0, float(np.std(pt_arr)) * 2.5)

        must_have_pts = [p for p in point_details if p['priority'] == 'must-have']
        must_have_pass_rate = (
            np.mean([1.0 if p['passed'] else 0.0 for p in must_have_pts])
            if must_have_pts else 1.0
        )

        final = (
            0.22 * w_mean + 0.15 * coverage + 0.25 * strength +
            0.18 * global_kw + 0.08 * depth + 0.07 * consistency +
            0.05 * must_have_pass_rate
        )
        final = min(final, 0.99)

        # Multi-gate decision (PRD thresholds)
        if final >= SELECTED_THRESH:
            decision = "SELECTED"
        elif final >= BORDERLINE_THRESH:
            decision = "BORDERLINE"
        elif final >= REJECTED_THRESH:
            decision = "REJECTED"
        else:
            decision = "HARD_REJECTED"

        matched_kw_all = sorted(all_rubric_kw & cand_kw)
        missing_kw_all = sorted(all_rubric_kw - cand_kw)
        passed_pts = [p for p in point_details if p['passed']]
        failed_pts = [p for p in point_details if not p['passed']]
        sorted_pts = sorted(point_details, key=lambda x: x['score'], reverse=True)
        strengths_list = [f"{p['rubric_point'][:80]} ({p['score']*100:.0f}%)" for p in sorted_pts if p['passed']]
        weaknesses_list = [f"{p['rubric_point'][:80]} ({p['score']*100:.0f}%)" for p in sorted(failed_pts, key=lambda x: x['score'])]
        gaps_list = []
        for fp in failed_pts:
            j_idx = point_details.index(fp)
            miss = sorted(criteria[j_idx]['keywords'] - cand_kw)
            if miss:
                gaps_list.append(f"{fp['rubric_point'][:50]}: needs {', '.join(miss[:5])}")

        results.append({
            "id": str(i + 1), "name": names[i],
            "score": round(final * 100, 2), "rank": 0, "decision": decision,
            "reason": "", "strengths": strengths_list, "weaknesses": weaknesses_list,
            "gaps": gaps_list, "matched_keywords": matched_kw_all,
            "missing_keywords": missing_kw_all, "recommendation": "",
            "response_snippet": (responses[i][:150] + "\u2026") if len(responses[i]) > 150 else responses[i],
            "point_scores": point_details,
            "coverage": round(coverage * 100, 1),
            "keyword_match_rate": round(global_kw * 100, 1),
            "consistency_score": round(consistency * 100, 1),
            "experience_level": exp_info['level'],
            "experience_confidence": exp_info['confidence'],
            "must_have_pass_rate": round(must_have_pass_rate * 100, 1),
            "response_depth": round(depth * 100, 1),
            "criteria_passed": len(passed_pts),
            "criteria_total": n_crit,
            "technical_breadth": len(matched_kw_all),
            "technical_depth_score": round(min(1.0, len(matched_kw_all) / max(len(all_rubric_kw), 1)) * 100, 1),
            "_raw": final, "_w_mean": w_mean, "_coverage": coverage,
            "_strength": strength, "_kwCov": global_kw, "_depth": depth, "_consistency": consistency,
        })

    # Relative ranking + smart promotion
    results.sort(key=lambda r: r['_raw'], reverse=True)
    top_score = results[0]['_raw'] if results else 0
    n_total = len(results)
    for idx, r in enumerate(results):
        r['rank'] = idx + 1
        ratio = r['_raw'] / top_score if top_score > 0 else 0
        if r['_raw'] < MIN_QUALIFY:
            r['decision'] = 'HARD_REJECTED'
            continue
        # Promote rank #1 to SELECTED if they have reasonable coverage and lead clearly
        if idx == 0 and r['decision'] != 'SELECTED':
            if r['_coverage'] >= MIN_COVERAGE_HIRE and r['_kwCov'] >= MIN_KW_HIRE:
                r['decision'] = 'SELECTED'
            elif r['_coverage'] >= MIN_COVERAGE_BORDER:
                r['decision'] = 'BORDERLINE'
        # Promote rank #2 to SELECTED if very close to #1, or BORDERLINE
        if idx == 1 and ratio >= 0.82:
            if r['decision'] == 'REJECTED' and r['_coverage'] >= MIN_COVERAGE_HIRE:
                r['decision'] = 'SELECTED'
            elif r['decision'] == 'REJECTED' and r['_coverage'] >= MIN_COVERAGE_BORDER:
                r['decision'] = 'BORDERLINE'
        elif idx == 1 and ratio >= 0.65:
            if r['decision'] == 'REJECTED' and r['_coverage'] >= MIN_COVERAGE_BORDER:
                r['decision'] = 'BORDERLINE'
        # Rank #3 can be BORDERLINE if reasonably close
        if idx == 2 and ratio >= 0.60:
            if r['decision'] == 'REJECTED' and r['_coverage'] >= MIN_COVERAGE_BORDER:
                r['decision'] = 'BORDERLINE'

    # Percentile
    scores_arr = np.array([r['score'] for r in results])
    for r in results:
        r['percentile'] = round(float(np.sum(scores_arr <= r['score']) / len(scores_arr) * 100), 1)

    # Confidence score
    for r in results:
        s = r['score'] / 100
        cov = r['coverage'] / 100
        kw = r['keyword_match_rate'] / 100
        signal_agreement = 1.0 - float(np.std([s, cov, kw]) * 2)
        data_richness = min(1.0, len(r.get('response_snippet', '')) / 80)
        r['confidence'] = round(max(0, min(100, signal_agreement * 60 + data_richness * 40)), 1)

    # Stars & grades (calibrated for realistic score distribution)
    for r in results:
        s = r['score']
        if s >= 50:   r['star_rating'] = 5
        elif s >= 38: r['star_rating'] = 4
        elif s >= 26: r['star_rating'] = 3
        elif s >= 16: r['star_rating'] = 2
        else:         r['star_rating'] = 1
        if s >= 55:   r['grade'] = 'A+'
        elif s >= 45: r['grade'] = 'A'
        elif s >= 38: r['grade'] = 'B+'
        elif s >= 32: r['grade'] = 'B'
        elif s >= 26: r['grade'] = 'C+'
        elif s >= 20: r['grade'] = 'C'
        elif s >= 14: r['grade'] = 'D'
        else:         r['grade'] = 'F'

    # Borderline analysis
    selected_thresh_pct = SELECTED_THRESH * 100
    for r in results:
        if r['decision'] == 'BORDERLINE':
            proximity = min(99, round(r['score'] / selected_thresh_pct * 100, 1))
            gap_pct = round(max(0, selected_thresh_pct - r['score']), 1)
            interview_qs = []
            weak_pts = sorted([p for p in r['point_scores'] if not p['passed']], key=lambda p: p['score'])
            for wp in weak_pts[:3]:
                interview_qs.append(f"Describe your hands-on experience with: {wp['rubric_point'][:60].rstrip('.')}")
            if r['missing_keywords']:
                interview_qs.append(f"Walk us through a project involving: {', '.join(r['missing_keywords'][:4])}")
            improvements = [f"Demonstrate depth in: {wp['rubric_point'][:55].rstrip('.')}" for wp in weak_pts[:3]]
            closeness = "Very close" if proximity >= 85 else "Moderately close" if proximity >= 65 else "Needs improvement"
            r['borderline_analysis'] = {
                'proximity_to_hire': proximity, 'gap_percentage': gap_pct,
                'interview_questions': interview_qs, 'improvement_areas': improvements,
                'verdict': f"{closeness} - {gap_pct:.1f}% gap to hire threshold",
            }
        else:
            r['borderline_analysis'] = None

    # Reasons & recommendations
    for r in results:
        cov = r['coverage']; score = r['score']; dec = r['decision']
        sr = r.get('star_rating', 0)
        lines = []
        if dec == 'SELECTED':
            lines.append(f"TOP PICK - Rank #{r['rank']} | {r.get('grade','')} | {sr}/5 stars")
            lines.append(f"Strong match with {cov:.0f}% rubric coverage and {score:.1f}% overall alignment.")
            lines.append(f"{r['criteria_passed']}/{r['criteria_total']} criteria passed | Confidence: {r['confidence']}%")
            if r['strengths']:
                lines.append(f"Excels in: {'; '.join(r['strengths'][:3])}")
        elif dec == 'BORDERLINE':
            ba = r['borderline_analysis']
            lines.append(f"BORDERLINE - Rank #{r['rank']} | {r.get('grade','')} | {sr}/5 stars")
            lines.append(f"{cov:.0f}% coverage, {score:.1f}% fit - {ba['proximity_to_hire']:.0f}% toward hire threshold.")
            lines.append(f"{r['criteria_passed']}/{r['criteria_total']} criteria passed | Exp: {r['experience_level']}")
            if r['strengths']:
                lines.append(f"Shows promise in: {'; '.join(r['strengths'][:2])}")
            lines.append(f"Gap to close: {ba['gap_percentage']:.1f}% - could be bridged with a focused interview.")
        else:
            lines.append(f"NOT RECOMMENDED - Rank #{r['rank']} | {r.get('grade','')} | {sr}/5 stars")
            lines.append(f"Only {cov:.0f}% coverage and {score:.1f}% overall fit.")
            lines.append(f"{r['criteria_passed']}/{r['criteria_total']} criteria passed | Exp: {r['experience_level']}")
        if r['matched_keywords']:
            lines.append(f"Skills detected: {', '.join(r['matched_keywords'][:10])}")
        if r['missing_keywords'] and dec != 'SELECTED':
            lines.append(f"Missing: {', '.join(r['missing_keywords'][:6])}")
        if dec == 'SELECTED':
            best_area = r['strengths'][0].split('(')[0].strip() if r['strengths'] else 'general competency'
            r['recommendation'] = f"Proceed to interview - Top {r['rank']} candidate. Covers {cov:.0f}% of requirements with {len(r['matched_keywords'])} matching skills."
        elif dec == 'BORDERLINE':
            gap_areas = [w.split('(')[0].strip() for w in r['weaknesses'][:2]]
            r['recommendation'] = f"Worth a screening call - {r['borderline_analysis']['proximity_to_hire']:.0f}% toward hire threshold. Probe: {'; '.join(gap_areas) if gap_areas else 'technical depth'}."
        else:
            total_kw = len(r['matched_keywords']) + len(r['missing_keywords'])
            r['recommendation'] = f"Does not meet requirements - missing {len(r['missing_keywords'])} of {total_kw} expected skills."
        r['reason'] = "\n".join(lines)

    # Clean internal keys
    for r in results:
        for k in ('_raw', '_w_mean', '_coverage', '_strength', '_kwCov', '_depth', '_consistency'):
            r.pop(k, None)

    total_time = time.time() - t_start
    print(f"Total: {total_time:.2f}s for {n_cand} candidates (bi={t_bi:.2f}s cx={t_cx:.2f}s kw={t_kw:.2f}s)")
    return results, round(total_time, 2)


def process_evaluation_request(candidates_file_bytes, rubric_text, candidates_filename):
    try:
        if candidates_filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(candidates_file_bytes))
        else:
            df = pd.read_excel(io.BytesIO(candidates_file_bytes))
        text = rubric_text.decode('utf-8', errors='ignore')
        results, eval_time = evaluate_with_strict_model(df, text, strictness_threshold=0.35)  # Lowered from 0.60 for more lenient scoring
        return {
            "status": "success",
            "data": results,
            "summary": {
                "total": len(results),
                "hired": sum(1 for r in results if r['decision'] == 'SELECTED'),
                "borderline": sum(1 for r in results if r['decision'] == 'BORDERLINE'),
                "rejected": sum(1 for r in results if r['decision'] == 'REJECTED' or r['decision'] == 'HARD_REJECTED'),
            },
            "eval_time_seconds": eval_time,
        }
    except Exception as e:
        import traceback; traceback.print_exc()
        return {"status": "error", "message": str(e)}
