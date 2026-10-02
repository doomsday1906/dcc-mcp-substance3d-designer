# DOWNSTREAM.md — retained divergence ledger

Each entry records one retained downstream divergence. This is a ledger, not history.

- Status values: NOT_SUBMITTED | SUBMITTED | MERGED | RELEASED_UPSTREAM | PERMANENT_DOWNSTREAM.
- Update `downstream commit` and evidence when the patch lands.
- Remove an entry only when its removal condition is met.

## D001 — digit-led native Designer property identifiers

- ID: D001
- Title: accept digit-led native Designer property identifiers
- Upstream base commit: 1bbcb6739969c785beb449ace3609f55f1bd7578 (v0.8.1)
- Downstream commit: 281dd9e9f3378c41d603df7bfbc671cf71716d82 (`fix: allow digit-led Designer property identifiers`)
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

## D002 — read-only shipped resource edge-property inspection

- ID: D002
- Title: describe exact native edge properties of one shipped resource instance via isolated inspection
- Upstream base commit: 1bbcb6739969c785beb449ace3609f55f1bd7578 (v0.8.1)
- Downstream commit: ff01fb6df8481c0c02863640d5cddf818917dfe7 (`feat: describe shipped resource edge properties without instantiation`)
- Affected files:
  - `src/dcc_mcp_substance3d_designer/graph_resources.py`
  - `src/dcc_mcp_substance3d_designer/skills/designer-session/scripts/describe_shipped_resource_properties.py`
  - `src/dcc_mcp_substance3d_designer/skills/designer-session/tools.yaml`
  - `tests/test_shipped_resource_properties.py`
- Demonstrated reason: Whole-batch structural preflight must distinguish
  "property exists" from "property can legally accept a graph edge" for nodes
  created earlier in the same batch (e.g. `spline_tools.sbs:spline_append`
  `spline_amount_1` is declared `isConnectable=1` in shipped XML yet the native
  instance refuses `PROPERTY_READ_ONLY` while `spline_coords_1`/`spline_data_1`
  texture inputs succeed). Static XML alone is insufficient and the production
  graph must never be mutated merely for discovery. The new read-only tool
  reports native `isConnectable()`, `isReadOnly()`, and property types for a
  shipped graph resource instance. The production graph and its package are
  never touched: the resource is instanced once in an isolated temporary
  package/graph that is deleted and unloaded before return.
- Tests/evidence:
  - focused `test_shipped_resource_properties` incl. texture vs scalar
    read-only distinction, isolated-scratch proof, and fail-closed boundaries;
  - existing `test_graph_contracts` + `test_graph_resources` + `test_graph_authoring`
    still pass; `ruff check src tests tools` passes;
  - install-lifecycle failures on Linux are pre-existing environmental
    (verified on clean tree) and unrelated to this change;
  - live-host readback evidence recorded at Lab qualification time via
    disposable canaries using the exact `spline_append` contract.
- Upstream status: NOT_SUBMITTED
- Upstream issue/PR: none (no submission authorized in this mission)
- Removal condition: upstream accepts an equivalent read-only resource-property
  inspection and a released upstream version containing it becomes the
  Lab-supported base.
