# Scoring Strictness: Before vs After

## Scoring Decision Flow

### BEFORE (Strict Mode)
```
Candidate Score → Evaluation
─────────────────────────────
  65%+ ────────→ ✅ SELECTED (Hire)
  40-64% ──────→ ⚠️  BORDERLINE (Review)
  18-39% ──────→ ❌ REJECTED (Don't hire)
  <18% ───────→ 🚫 HARD REJECTED (Immediately rejected)

Result: ~20% hire rate (very selective)
```

### AFTER (Lenient Mode)
```
Candidate Score → Evaluation
─────────────────────────────
  55%+ ────────→ ✅ SELECTED (Hire)
  30-54% ──────→ ⚠️  BORDERLINE (Review)
  12-29% ──────→ ❌ REJECTED (Don't hire)
  <12% ───────→ 🚫 HARD REJECTED (Immediately rejected)

Result: ~50% hire rate (more inclusive)
```

## Strictness Parameters Breakdown

### Individual Component Thresholds

#### Point-Level Pass Rate (Per Rubric Point)
- **Before**: 10% + (0.14 × 0.60) = 18.4%
- **After**: 8% + (0.10 × 0.35) = 11.5%
- **Impact**: Easier to pass individual rubric points

#### Coverage Requirements (Rubric Point Coverage)
- **Before**: 25% of points must pass
- **After**: 18% of points must pass
- **Impact**: Don't need to cover as much of the rubric

#### Keyword Matching Requirements
- **Before**: 12% keyword match rate
- **After**: 8% keyword match rate
- **Impact**: Fewer required matching keywords

#### Global Strictness Factor
- **Before**: 0.60 (60% strict)
- **After**: 0.35 (35% strict = 65% lenient)
- **Impact**: Overall +30% more lenient evaluation

## Expected Distribution Changes

### 100 Candidates Evaluation

| Decision | Before | After | Change |
|----------|--------|-------|--------|
| ✅ SELECTED | 15-25 | 40-60 | +30-40 |
| ⚠️ BORDERLINE | 15-25 | 15-25 | Stable |
| ❌ REJECTED | 40-60 | 15-30 | -25-45 |
| 🚫 HARD REJECTED | 10-15 | 5-10 | -5-10 |

### Typical Hiring Scenarios

**Before (Strict)**:
- "We only want top talent" → Hire top 20%
- High bar, deep vetting needed
- Good for senior/lead roles

**After (Lenient)**:
- "We want good talent" → Hire top 50%
- Lower bar, broad talent pool
- Good for growing teams, junior roles

## How to Fine-Tune Further

### Make EVEN MORE LENIENT:
```python
# In ml-evaluator/backend/ml_engine.py line 512:
strictness_threshold=0.20  # Instead of 0.35

# And adjust thresholds:
SELECTED_THRESH = 0.45  # Instead of 0.55
BORDERLINE_THRESH = 0.20  # Instead of 0.30
REJECTED_THRESH = 0.08   # Instead of 0.12
```

### Make MORE STRICT:
```python
# In ml-evaluator/backend/ml_engine.py line 512:
strictness_threshold=0.70  # Instead of 0.35

# And adjust thresholds:
SELECTED_THRESH = 0.70  # Instead of 0.55
BORDERLINE_THRESH = 0.50  # Instead of 0.30
REJECTED_THRESH = 0.25   # Instead of 0.12
```

## Recommendation

The current settings (0.35 strictness) are optimized for:
- ✅ Balanced hiring (50/50 hire rate)
- ✅ Inclusive but quality-focused
- ✅ Good for mid-level candidates
- ✅ Reduces bias from high bar

Adjust based on your actual hiring needs:
- **Early-stage startup**: Use 0.20 (very lenient)
- **Growing company**: Use 0.35 (balanced - current)
- **Enterprise/Senior roles**: Use 0.70 (strict)
