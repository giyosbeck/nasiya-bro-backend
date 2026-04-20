# Backend Deep Review — 2026-04-20

Comprehensive audit of FastAPI backend at `/Users/zubayr/giyos/projects/nasiya_bro/backend/` against the new mobile app's requirements. Status: 🟢 ~80% ready, 20% gaps documented below.

## Traffic-light summary

| Area | Status | Priority |
|---|---|---|
| Endpoints (60+ across 11 resources) | 🟢 Complete | LOW |
| Data model (8 tables) | 🟡 Missing `audit_log`, `seller_permissions`, `restock_history`, `currency_rates` | HIGH |
| Security | 🔴 SECRET_KEY hardcoded, file-serve open, no per-request subscription check | **P0** |
| Subscription enforcement | 🟡 Login-only gate, leaky | HIGH |
| Notifications | 🟡 Basic Expo push OK; reminders + low-stock missing | MED |
| Schema migrations | 🟡 No Alembic versioning; ad-hoc scripts | HIGH |
| Code quality | 🟡 Good layout, ~70% typed, <5% test coverage | MED |
| Production readiness | 🔴 No structured logging, error tracking, Docker, health checks | **P0** |
| Mobile-app gaps | 🔴 Granular perms, audit log, refresh token, soft-delete, demo endpoint | **P0** |
| API versioning | 🟡 v1 only; v2 needed for new mobile to avoid breaking legacy | MED |

## P0 — Launch blockers (must fix before new mobile ships)

| # | Item | Effort | Risk |
|---|---|---|---|
| P0-1 | Granular seller permissions table + enforcement in 5+ endpoints | 2d | Med |
| P0-2 | File-serve auth gate — passport images are publicly readable by path | 4h | Med |
| P0-3 | JWT refresh endpoint + token rotation | 1d | Low |
| P0-4 | Auto-grant 3-month trial on registration (currently admin must approve) | 2h | Low |
| P0-5 | Subscription middleware — per-request check for expired status | 4h | Med |
| P0-6 | Rotate `SECRET_KEY` + admin creds — currently hardcoded in `app/core/config.py:16,33-34` | 2h | Med |
| P0-7 | Alembic migration versioning (replace ad-hoc `*.py` scripts) | 2d | High |
| P0-8 | Docker + docker-compose for reproducible deploys | 1d | Low |
| P0-9 | Timezone fix — scheduler runs UTC, Uzbekistan is UTC+5, cron jobs fire at wrong local times | 1h | Low |

## P1 — Within one sprint

| # | Item | Effort |
|---|---|---|
| P1-1 | Audit log table + seller-action tracking | 1d |
| P1-2 | Onboarding `/onboarding/demo` endpoint | 1d |
| P1-3 | Payment reminder scheduler (3d + 1d + day-of per payment) | 1d |
| P1-4 | Low-stock threshold per product + push trigger | 1d |
| P1-5 | CBU currency-rate proxy with cache | 1d |
| P1-6 | Restock history table | 1d |
| P1-7 | Phone format validation (+998XXXXXXXXX) | 2h |
| P1-8 | API v2 namespace (run v1 + v2 in parallel for legacy mobile overlap) | 2d |
| P1-9 | Test suite skeleton (pytest + fixtures + auth coverage) | 1d |

## Missing tables to add

1. `audit_log` — id, user_id, action, entity_type, entity_id, before_json, after_json, created_at
2. `seller_permissions` — user_id + 10 flag/limit columns from roles matrix
3. `restock_history` — product_id, quantity, unit_cost, restocked_by, notes, created_at
4. `currency_rates` — currency, rate_to_uzs, timestamp, source
5. `refresh_tokens` — user_id, token_hash, expires_at, revoked

## Missing indexes (performance gaps)

- `(loan_payments.loan_id, due_date)` — upcoming payment queries
- `(loan_payments.due_date, status)` — overdue scans
- `(loans.magazine_id, created_at)` — report aggregations
- `(sales.magazine_id, created_at)` — report queries
- `(clients.magazine_id)` via join on manager — GADGETS listing

## Security red flags

1. **`SECRET_KEY` hardcoded** in `app/core/config.py:16` — `"nasiya-bro-secret-key-2025-change-in-production-please"` — anyone who reads repo can forge JWTs.
2. **Admin credentials hardcoded** in `config.py:33-34` — phone `01234567`, password `23154216`.
3. **`/files/serve/{file_path}` has NO auth** — passport images accessible by anyone who guesses/obtains the UUID path.
4. **Path traversal** surface in `/files/serve/{file_path:path}` — `..` sequences not sanitized.
5. **Seller permissions not enforced** — `/loans/` POST allows any seller to create nasiya of any amount; `/clients/` PUT allows any seller to edit any client.
6. **JWT expiry 8 days, no refresh** — long-lived tokens + no rotation.
7. **Rate limit middleware commented out** in `main.py:21` — endpoints unprotected from brute force.
8. **CORS `methods: ["*"]` and `headers: ["*"]`** — permissive.

## Nasiya formula verification — ✅ CONFIRMED MATCHES

Backend `loans.py:268-300` computes:
```
financed = loan_price - initial_payment
total_interest = financed * (interest_rate / 100)
monthly = (loan_price + total_interest - initial_payment) / loan_months
```
Matches mobile passport spec §6. No code change needed for formula itself; document in OpenAPI.

## API v2 strategy (recommended)

Run `/api/v1` (legacy, frozen) and `/api/v2` (new mobile) in parallel for 3 months:
- v2 includes new endpoints (`/onboarding/demo`, `/auth/refresh`, `/audit-log`, `/currency-rates`, `/subscriptions/*`) and strictly enforces seller permissions.
- v1 continues for legacy mobile app; receives security patches only.
- Deprecation banner in v1 responses.
- v1 removed month 4-5 after both stores update.

## Recommended folder restructure

Endpoints `loans.py` (998 lines) and `auto_loans.py` (657 lines) should split by concern:
```
api_v2/endpoints/loans/{loans.py, payments.py, calculations.py}
api_v2/endpoints/auto_loans/{similar}
```
Plus new files `subscriptions.py`, `audit_logs.py`, `currency_rates.py`, `onboarding.py`, `sellers.py`.

Add `app/services/{auth_service, loan_service, permission_service, file_service}.py` to pull logic out of endpoint files.

Add `tests/` with pytest + fixtures + integration.

## Production readiness checklist (none currently)

- [ ] Structured JSON logging (Sentry DSN via env)
- [ ] Health checks: `/health` (DB ping), `/health/live` (liveness)
- [ ] Prometheus metrics endpoint
- [ ] Docker + docker-compose
- [ ] GitHub Actions / CI for lint + test + build
- [ ] Staging environment matching prod
- [ ] Automated backup of Postgres
- [ ] Log aggregation (Datadog / CloudWatch / ELK)
- [ ] Alerting on error spike / latency p95

## Full inventory of current endpoints

Saved as reference. See the full agent report in memory/session transcript (2026-04-20). 60+ endpoints across: auth, users, clients, products, auto_products, sales, auto_sales, loans, auto_loans, magazines, notifications, files, reports, transactions.

## Decision points (await PM input)

1. Run v1 + v2 in parallel, or hard-cut v1 at mobile launch?
2. Auto-grant trial on self-register (brief §3 says yes), or keep admin-approval gate as extra fraud check?
3. Build own OAuth / passwordless flow, or continue phone+password?
4. Sentry + log aggregation — use free Sentry tier + self-hosted Loki, or paid tier?
5. Docker-compose staging environment or direct-to-prod (current)?
