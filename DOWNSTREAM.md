# DOWNSTREAM.md — retained divergence ledger

Each entry records one retained downstream divergence. This is a ledger, not history.

- Status values: NOT_SUBMITTED | SUBMITTED | MERGED | RELEASED_UPSTREAM | PERMANENT_DOWNSTREAM.
- Update `downstream commit` and evidence when the patch lands.
- Remove an entry only when its removal condition is met.

## D001 — digit-led native Designer property identifiers

- ID: D001
- Title: accept digit-led native Designer property identifiers
- Upstream base commit: 1bbcb6739969c785beb449ace3609f55f1bd7578 (v0.8.1)
- Downstream commit: _pending (filled on patch commit)_
- Affected files:
  - `src/dcc_mcp_substance3d_designer/graph_authoring.py`
  - `tests/test_typed_graph_authoring.py`
- Demonstrated reason: Designer 16.0.6 exposes legitimate native node property
  identifiers `2d_shape_size` and `2d_shape_size_random`. The adapter rejected
  them with `INVALID_PROPERTY_ID` before the Designer SDK setter. A one-line
  host patch to the `_PROPERTY_ID` first-character class allowed the same public
  Lab operation to commit, with native readback near `[1.2, 0.9]` and
  `[0.15, 0.25]` respectively.
- Tests/evidence:
  - focused `require_property` accept/reject coverage incl. boundary cases;
  - full `python -m pytest`, `ruff check src tests tools`, `python -m build`;
  - live-host readback evidence recorded at qualification time.
- Upstream status: NOT_SUBMITTED
- Upstream issue/PR: none (no submission authorized in this mission)
- Removal condition: upstream accepts an equivalent fix and a released upstream
  version containing it becomes the Lab-supported base.
