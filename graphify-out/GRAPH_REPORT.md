# Graph Report - ScamShield  (2026-05-08)

## Corpus Check
- 28 files · ~33,953 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 217 nodes · 506 edges · 15 communities detected
- Extraction: 57% EXTRACTED · 43% INFERRED · 0% AMBIGUOUS · INFERRED: 217 edges (avg confidence: 0.55)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 17|Community 17]]

## God Nodes (most connected - your core abstractions)
1. `User` - 30 edges
2. `MessageResponse` - 23 edges
3. `ScanResult` - 18 edges
4. `ScamReport` - 17 edges
5. `UserOut` - 16 edges
6. `AdminTokenResponse` - 13 edges
7. `AdminUserItem` - 13 edges
8. `AdminScanItem` - 13 edges
9. `AdminReportItem` - 13 edges
10. `AdminStats` - 13 edges

## Surprising Connections (you probably didn't know these)
- `migrate_admin_columns.py Safely adds is_admin and is_active columns to the user` --uses--> `User`  [INFERRED]
  backend\migrate_admin_columns.py → backend\app\models.py
- `Add a column only if it doesn't already exist.` --uses--> `User`  [INFERRED]
  backend\migrate_admin_columns.py → backend\app\models.py
- `setup_admin.py  –  Creates or promotes shantanu15feb0000@gmail.com as admin. Ru` --uses--> `User`  [INFERRED]
  backend\setup_admin.py → backend\app\models.py
- `register()` --calls--> `hash_password()`  [INFERRED]
  backend\app\routers\auth_router.py → backend\app\auth.py
- `Shared FastAPI dependencies – current-user extraction and rate limiter.` --uses--> `User`  [INFERRED]
  backend\app\dependencies.py → backend\app\models.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.18
Nodes (43): delete_report(), delete_user(), get_stats(), list_all_reports(), list_all_scans(), list_users(), Admin router – /api/admin/* All endpoints require a valid JWT from a user with, Return all registered users with scan/report counts. (+35 more)

### Community 1 - "Community 1"
Cohesion: 0.19
Nodes (14): adminLogout(), apiFetch(), authHeaders(), confirm_action(), deleteReport(), deleteUser(), loadReports(), loadScans() (+6 more)

### Community 2 - "Community 2"
Cohesion: 0.15
Nodes (15): _extract_indicators(), _generate_explanation(), _load_model(), predict_risk(), ML predictor – loads a trained model or falls back to rule-based scoring., Try to load persisted ML model; return (model, vectorizer) or (None, None)., Return a prediction dict:     { risk_level, risk_score, explanation, indicators, _rule_based_score() (+7 more)

### Community 3 - "Community 3"
Cohesion: 0.21
Nodes (15): Base, dashboard_stats(), Dashboard router – /api/dashboard/stats, Aggregate stats + recent activity for the logged-in user's dashboard., ScamReport, _humanize_timedelta(), Convert a datetime delta into a short human string like 'Today · 10:20'., create_report() (+7 more)

### Community 4 - "Community 4"
Cohesion: 0.19
Nodes (13): _build_prompt(), get_precaution_advice(), Google Gemini advisor – generates human-friendly precautionary advice when a sc, Call Google Gemini API and return a precautionary advice string.     Falls back, SQLAlchemy ORM models for ScamShield., ScanResult, history(), predict() (+5 more)

### Community 5 - "Community 5"
Cohesion: 0.32
Nodes (12): $(), getAuthToken(), hideSpinner(), initNav(), initYear(), loadUser(), populateHeaderUser(), populateReportHistory() (+4 more)

### Community 6 - "Community 6"
Cohesion: 0.15
Nodes (12): admin_login(), create_access_token(), decode_access_token(), hash_password(), JWT token helpers and password hashing utilities., Return the token payload or None if invalid / expired., verify_password(), get_current_admin() (+4 more)

### Community 7 - "Community 7"
Cohesion: 0.25
Nodes (13): build_dataset(), download_hf_enron_ham(), download_hf_enron_spam(), download_kaggle_spam(), download_smishing(), download_uci_sms(), _fetch(), _pick_text_from_example() (+5 more)

### Community 8 - "Community 8"
Cohesion: 0.38
Nodes (12): $(), evaluatePasswordStrength(), handleLoginSubmit(), handleRedirectToast(), handleRegisterSubmit(), hideSpinner(), initNav(), initYear() (+4 more)

### Community 9 - "Community 9"
Cohesion: 0.38
Nodes (9): $(), callPredictApi(), getAuthToken(), handleScanSubmit(), hideSpinner(), initNav(), initYear(), showSpinner() (+1 more)

### Community 10 - "Community 10"
Cohesion: 0.33
Nodes (4): BaseSettings, Config, Application configuration via environment variables (Pydantic Settings)., Settings

### Community 11 - "Community 11"
Cohesion: 0.4
Nodes (3): ScamShield Backend - FastAPI application entry point., Catch-all GET route that serves files from the assets/ directory.     Registere, serve_frontend()

### Community 12 - "Community 12"
Cohesion: 0.5
Nodes (3): add_column_if_missing(), migrate_admin_columns.py Safely adds is_admin and is_active columns to the user, Add a column only if it doesn't already exist.

### Community 13 - "Community 13"
Cohesion: 0.5
Nodes (3): get_db(), SQLAlchemy database engine, session factory, and Base class., FastAPI dependency that yields a DB session and ensures it is     closed after

### Community 17 - "Community 17"
Cohesion: 1.0
Nodes (1): setup_admin.py  –  Creates or promotes shantanu15feb0000@gmail.com as admin. Ru

## Knowledge Gaps
- **27 isolated node(s):** `JWT token helpers and password hashing utilities.`, `Return the token payload or None if invalid / expired.`, `Config`, `Application configuration via environment variables (Pydantic Settings).`, `SQLAlchemy database engine, session factory, and Base class.` (+22 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 17`** (2 nodes): `setup_admin.py`, `setup_admin.py  –  Creates or promotes shantanu15feb0000@gmail.com as admin. Ru`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `Community 0` to `Community 3`, `Community 4`, `Community 6`, `Community 12`, `Community 17`?**
  _High betweenness centrality (0.099) - this node is a cross-community bridge._
- **Why does `predict()` connect `Community 4` to `Community 2`?**
  _High betweenness centrality (0.094) - this node is a cross-community bridge._
- **Why does `ScanResult` connect `Community 4` to `Community 0`, `Community 3`?**
  _High betweenness centrality (0.052) - this node is a cross-community bridge._
- **Are the 28 inferred relationships involving `User` (e.g. with `migrate_admin_columns.py Safely adds is_admin and is_active columns to the user` and `Add a column only if it doesn't already exist.`) actually correct?**
  _`User` has 28 INFERRED edges - model-reasoned connections that need verification._
- **Are the 21 inferred relationships involving `MessageResponse` (e.g. with `Admin router – /api/admin/* All endpoints require a valid JWT from a user with` and `Authenticate as admin. Returns a JWT only if the user has is_admin == True.`) actually correct?**
  _`MessageResponse` has 21 INFERRED edges - model-reasoned connections that need verification._
- **Are the 16 inferred relationships involving `ScanResult` (e.g. with `Admin router – /api/admin/* All endpoints require a valid JWT from a user with` and `Authenticate as admin. Returns a JWT only if the user has is_admin == True.`) actually correct?**
  _`ScanResult` has 16 INFERRED edges - model-reasoned connections that need verification._
- **Are the 15 inferred relationships involving `ScamReport` (e.g. with `Admin router – /api/admin/* All endpoints require a valid JWT from a user with` and `Authenticate as admin. Returns a JWT only if the user has is_admin == True.`) actually correct?**
  _`ScamReport` has 15 INFERRED edges - model-reasoned connections that need verification._