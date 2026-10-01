# AGENTS.md — downstream compatibility fork

This is a thin downstream compatibility/reliability fork of
`dcc-mcp/dcc-mcp-substance3d-designer`. Preserve upstream architecture by default.

## Branch contract

- `main` mirrors upstream and takes no downstream-only commits.
- Downstream work lives on supported branches (e.g. `lab-supported/0.8.1`).
- Upstream history stays visible; do not rewrite shared history.

## Change discipline

1. One demonstrated problem → one minimal change.
2. No opportunistic refactors, renames, formatting sweeps, modernization,
   new abstractions, unrelated cleanup, or documentation rewrites.
3. SubstanceDesignerLab concepts do NOT belong here: no Potter, Threadmark,
   Hestia, morphology gates, Lab session/checkpoint policy, artistic recipes,
   or evaluation policy.
4. Every downstream behavioral patch needs an exact reproducer, a focused
   regression test, negative/boundary coverage, and honest live-host evidence
   when the claim is host-dependent.
5. Never weaken validation merely to make one Lab input pass. A broader
   accepted form requires evidence that Designer actually supports it.
6. Do not fabricate future generality. Fix only the proven compatibility class.
7. Existing tests may not be weakened to accommodate a patch unless the
   accepted public behavior itself is proven wrong.
8. If a tiny bug produces a large diff, stop and justify before proceeding.
9. Keep the downstream delta small enough to review against upstream directly.

## Upstream posture

10. Upstream-facing commits are minimal and independently cherry-pickable.
11. Commit subjects follow upstream's observed compact style:
    `fix: ...`, `feat: ...`, `fix(scope): ...`.
12. Upstream-facing PR prose (only when authorized) describes the generic
    Designer/adapter problem. No Lab history or internal product narrative.
13. The default response to upstream friction is: repair, wrap, or upstream a
    minimal fix — NOT replacement.
14. No agent may authorize or initiate a custom adapter rewrite, a
    fork-of-the-fork architecture, a large framework migration, or replacement
    of upstream. Such a decision requires a separate owner-approved design
    decision supported by repeated evidence.

Divergences are recorded in `DOWNSTREAM.md`.
