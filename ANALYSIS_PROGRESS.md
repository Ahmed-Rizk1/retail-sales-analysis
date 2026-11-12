# Retail Sales Analysis — Execution Progress Tracker
**Project:** `data-analysis-1-retail/` (AdventureWorks Internet Sales)  
**Last updated:** 2026-11-12

---

## 📋 Session State

| Item | Status |
|---|---|
| Audit completed | ✅ Done |
| Tuning plan created (`ANALYSIS_TUNING_PLAN.md`) | ✅ Done |
| Execution completed | ✅ Done (All Phases 1–5 complete & verified) |

---

## 🗂️ Audit Summary (Key Findings — Do Not Lose This Context)

The following issues were identified during the audit and are targeted in the tuning plan:

| # | Issue | Severity | File |
|---|---|---|---|
| 1 | `queries.sql` is a raw terminal session dump — shell commands, duplicate DDL, Indonesian comment, hardcoded local paths | 🔴 Critical | `SQL/queries.sql` |
| 2 | `requirements.txt` missing 4 deps (`python-dotenv`, `sqlalchemy`, `pymysql`, `openpyxl`), no versions pinned | 🔴 Critical | `requirements.txt` |
| 3 | `width='stretch'` is not a valid Streamlit parameter (should be `use_container_width=True`) — 7 occurrences | 🟠 High | `app.py` |
| 4 | Profit Margin KPI uses `.mean()` on per-row percentages instead of `total_profit / total_revenue` | 🟠 High | `app.py` |
| 5 | No empty-DataFrame guard — deselecting all filters causes silent broken charts | 🟠 High | `app.py` |
| 6 | Nested duplicate directory `retail-sales-analysis/` doubles all files | 🟡 Medium | repo structure |
| 7 | README Key Findings has only 4 vague bullets — needs specific, numbered insights with real figures | 🟡 Medium | `README.md` |
| 8 | `BirthDate` join in SQL done by customer name instead of `CustomerKey` (fragile) — fixed in view rewrite | 🟡 Medium | `SQL/queries.sql` |
| 9 | `RIGHT JOIN` bug in one intermediate view version — corrected in final view | 🟡 Medium | `SQL/queries.sql` |

---

## ✅ Phase Execution Tracker

### Phase 1 — Structural Cleanup
- [x] **Step 1.1** — Delete nested `retail-sales-analysis/` directory
- [x] **Step 1.2** — Rewrite `requirements.txt` with 7 pinned packages

### Phase 2 — Refactor `SQL/queries.sql`
- [x] **Step 2.1** — Replace entire file with clean, sectioned, commented SQL script

### Phase 3 — Fix `app.py` Bugs
- [x] **Step 3.1** — Replace all `width='stretch'` → `use_container_width=True` (7 occurrences)
- [x] **Step 3.2** — Fix `avg_margin` formula (line ~203)
- [x] **Step 3.3** — Add empty-DataFrame guard with `st.warning()` + `st.stop()`

### Phase 4 — Enhance `README.md`
- [x] **Step 4.1** — Replace "Key Findings" section with 5 structured, numbered subsections

### Phase 5 — Final Verification
- [x] Run the final checklist in `ANALYSIS_TUNING_PLAN.md` Phase 5
- [x] Verify script compilation, data loading, and clean workspace state

---

## 📝 Execution Log

| Timestamp | Phase | Step | Action | Result |
|---|---|---|---|---|
| 2026-11-12 | — | — | Audit completed, plan locked | ✅ |
| 2026-11-12 | Phase 1 | 1.1 | Deleted redundant nested `retail-sales-analysis/` directory | ✅ |
| 2026-11-12 | Phase 1 | 1.2 | Pinned 7 dependencies in `requirements.txt` | ✅ |
| 2026-11-12 | Phase 2 | 2.1 | Rewrote `SQL/queries.sql` into 8 clean, production-grade sections | ✅ |
| 2026-11-12 | Phase 3 | 3.1 | Replaced all `width='stretch'` calls with `use_container_width=True` in `app.py` | ✅ |
| 2026-11-12 | Phase 3 | 3.2 | Corrected `avg_margin` KPI calculation to portfolio total profit / total revenue | ✅ |
| 2026-11-12 | Phase 3 | 3.3 | Added empty-DataFrame filter guard with `st.warning()` and `st.stop()` | ✅ |
| 2026-11-12 | Phase 4 | 4.1 | Expanded `README.md` Key Findings into 5 structured, figure-backed subsections | ✅ |
| 2026-11-12 | Phase 5 | 5.1 | Executed complete Phase 5 verification checklist across all files | ✅ |
| 2026-11-12 | Phase 5 | 5.2 | Verified zero syntax/compile errors on all Python scripts and clean dataset load | ✅ |

---

## 🎯 Definition of Done

This project is considered **CV-ready** when:
1. All checkboxes above are ticked.
2. `streamlit run app.py` runs with no Python warnings or errors.
3. All 7 `st.plotly_chart()` calls use `use_container_width=True`.
4. `SQL/queries.sql` contains zero shell commands and zero duplicate DDL statements.
5. `requirements.txt` has exactly 7 pinned packages covering all runtime dependencies.
6. `README.md` Key Findings section has ≥ 5 numbered subsections with real dollar figures.

