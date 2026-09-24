# Testing & Validation Guide

The project includes an automated test suite implemented with `pytest` and `pytest-asyncio`, covering unit, integration, and API security boundary tests.

---

## 1. Running the Automated Test Suite

From the repository root or backend directory:

```bash
# Run all tests with verbose reporting
cd backend
pytest -v

# Run specific test modules
pytest app/tests/test_rule_engine.py -v
pytest app/tests/test_ml_classifier.py -v
pytest app/tests/test_firewall_pipeline.py -v
pytest app/tests/test_api.py -v
```

---

## 2. Test Coverage Matrix

The suite verifies all 24 required academic project scenarios:

| Test Module | Coverage Scope | Status |
|---|---|---|
| `test_health.py` | Liveness `/api/health` and component readiness probes | PASSED |
| `test_normalizer.py` | Unicode NFKC, zero-width characters, homoglyphs, base64, token fragmentation | PASSED |
| `test_rule_engine.py` | Direct injection, jailbreaks, system leaks, tool execution, pattern evaluation | PASSED |
| `test_ml_classifier.py` | Model loading, probability distributions, benign/attack prediction, explainability | PASSED |
| `test_firewall_pipeline.py` | End-to-end two-layer decision engine, risk scoring, **LLM barrier guarantee** | PASSED |
| `test_api.py` | Admin JWT login, protected endpoints, batch analysis, chat gateway, rule CRUD | PASSED |

**Total passing test cases**: 31 / 31 (100% pass rate in ~1.5s execution time).
