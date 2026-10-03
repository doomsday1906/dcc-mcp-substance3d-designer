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
- Demonstrated reason: Whole-batch structural preflight needs exact native
  `isConnectable()`, `isReadOnly()`, and property types for shipped resources
  created earlier in a batch. Static XML alone does not expose this full native
  contract, and the production graph must not be mutated for discovery. This
  read-only tool instances the requested resource in a temporary package/graph,
  reports those flags, then deletes and unloads the temporary package before
  return. D002 establishes metadata only. The native edge proof in D003 shows
  that connectable, read-only integer `spline_amount_1` accepts an edge;
  `isReadOnly()` protects value setting, not edge wiring.
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

## D003 — read-only connectable scalar inputs accept graph edges

- ID: D003
- Title: allow edges to connectable inputs whose values are read-only
- Upstream base commit: 1bbcb6739969c785beb449ace3609f55f1bd7578 (v0.8.1)
- Downstream commit: pending (candidate uncommitted; publication pending)
- Affected files:
  - `src/dcc_mcp_substance3d_designer/graph_connections.py`
  - `tests/test_graph_contracts.py`
- Demonstrated reason: the previous adapter rejected read-only non-texture
  inputs before calling the SDK, despite `isConnectable() == true`. The candidate
  removes only that extra edge veto and retains connectability, compatible type,
  input occupancy, cycle checks, and exact edge readback. Designer 16.0.6 native
  execution committed and read back all nine edges in a disposable graph. The
  three integer targets `spline_append.spline_amount_1`,
  `spline_append.spline_amount_2`, and `spline_render.spline_amount` each
  reported `connectable=true`, `read_only=true`, type `int`, modifier `Auto`.
  Readback confirmed `spline_source_1 -> spline_append.spline_amount_1`,
  `spline_source_2 -> spline_append.spline_amount_2`, and
  `spline_append -> spline_render.spline_amount`, alongside six texture edges.
  `isReadOnly()` still blocks value setting; it does not prohibit wiring.
- Tests/evidence:
  - `test_read_only_connectable_integer_input_accepts_and_verifies_edge` checks
    stub flags, exact readback, and idempotence; native flags are recorded in the
    separate SDK artifact below, and the value-setter read-only rejection test
    remains in the suite;
  - native Designer session `42fb8cb1-597b-4af9-8868-5967a229fb76`, job
    `sdj-20261003-28e0b71b74`, operation
    `scalar-connector-canary-001`, checkpoint
    `checkpoint-0001-715a97a9131c`, graph UID `1583031989`, signature
    `433b8ff96984f4c9f598b716e851eacf2653eae7135915fdbb08e05fc83e2a74`;
  - evidence workspace `ws_d4847f1bf8ec347192bc27a5`:
    `/evidence/scalar-connector-native-contracts.json` SHA-256
    `7fb386d64b9d4fe52960adefa5c2c6b75e3e62ffae8e1bec56cbfe0a553a5bf6`,
    `/evidence/native-0001.json` SHA-256
    `b4491fb7a0e0147fdc3e14fee5f384fa6623d95ff38d935aeb57b2d544dc341b`,
    and `/evidence/scalar-connector-canary.changes.json` SHA-256
    `8dcb60a13addae1d8ec0b818828f1dd3eb0cf11e8d7d4a1775485159b17fe6bd`;
  - qualified candidate source SHA-256:
    `da832b5fcaeab11d879c68badf8510190874a83cbabf9ee165d89f14d7fbb2e6`.
- Upstream status: NOT_SUBMITTED
- Upstream issue/PR: none (no submission authorized in this mission)
- Removal condition: upstream accepts an equivalent connection-validation fix and
  a released upstream version containing it becomes the Lab-supported base.
