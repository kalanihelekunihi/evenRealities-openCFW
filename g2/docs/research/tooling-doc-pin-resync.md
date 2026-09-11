# Cross-cutting tooling: re-pinning the four SHA-256-pinned reference docs (XC-008)

Status date: 2026-09-11 (XC-008)

## Scope

`docs/source-coverage.md`, `docs/memory-map.md`, `docs/upstream-inventory.md`,
and `docs/linux-reproducible-build.md` are SHA-256 pinned by
`tests/test_runtime_nanopb_decode_svarint_production.py`
(`STAGED_CONSUMER_PINS`) — see `docs/README.md`. Per-item agents are directed
not to edit these four files or their pins directly; XC-008's job is to
periodically diff the committed content of the four docs against their pins
and, where a landed change to one of them was legitimate but its pin wasn't
carried along, re-pin through the documented test path
(`python3 -m unittest tests.test_runtime_nanopb_decode_svarint_production`).

## Found: stale pin on `docs/linux-reproducible-build.md`

Comparing the SHA-256 of the four docs' current committed content against
`STAGED_CONSUMER_PINS` found one mismatch:

| Doc | Pinned digest matched current content? |
| --- | --- |
| `docs/memory-map.md` | yes |
| `docs/source-coverage.md` | yes |
| `docs/upstream-inventory.md` | yes |
| `docs/linux-reproducible-build.md` | **no** |

`git log --oneline -- docs/linux-reproducible-build.md` traces the drift to
commit `d794c28e` ("Add experimental GX8002 source firmware pipeline",
2026-09-08), which touched the doc's `CORE_CANONICAL_OBSERVATION_DIR` example
paths (`build/canonical-observation-g2-final97/...` →
`...-final99/...`, a private local scratch-directory rename, used
consistently across all six occurrences in the file) without updating the
`STAGED_CONSUMER_PINS` entry in
`tests/test_runtime_nanopb_decode_svarint_production.py`. That left
`test_production_runtime_and_overlay_contract_is_exact` failing closed
(sha256 mismatch) ever since, independent of any per-item agent's own work.

The content change itself is benign (a cosmetic, internally consistent
scratch-directory rename; no claim, procedure, or evidence pin in the
document changed), so this is a re-pin, not a content edit: updated the
`docs/linux-reproducible-build.md` entry in `STAGED_CONSUMER_PINS` from
`a80f6971972877c624cf93c97488ab6d33d54e65d933ae62f98be8bfd09ef58a` to
`8932944744a7ff88f4f7a5f2bb3b3b66da512d28ea8c398a1b263ad06ba2c123`, the
document's actual current SHA-256.

Checked for the same class of drift elsewhere: grepped every test under
`tests/` that references any of the four doc paths
(`test_analyze_g2_dual_profile_ownership.py`,
`test_analyze_g2_project_license_normalization.py`,
`test_community_distribution.py`,
`test_runtime_cmbacktrace_get_cur_thread_name_production.py`,
`test_runtime_nanopb_decode_svarint_production.py`,
`test_runtime_nanopb_decode_varint_production.py`,
`test_runtime_nanopb_decode_varint32_production.py`); only
`test_runtime_nanopb_decode_svarint_production.py` pins a full-file SHA-256
for these docs, and only the one entry above was stale.

## Verified, not fixed (out of scope for this item)

Running both documented pin-check paths
(`tests.test_runtime_nanopb_decode_svarint_production`,
`tests.test_runtime_nanopb_decode_varint32_production`) surfaced two
unrelated, pre-existing failure classes that are **not** part of the
four-doc pin surface and were left untouched:

- Six `test_runtime_nanopb_decode_varint32_production` failures because the
  local Xcode toolchain has drifted to
  `Apple clang version 21.0.0 (clang-2100.3.34.2)`, one point release past
  the pinned/reviewed `REVIEWED_COMPILERS` entry
  (`clang-2100.3.33.1`). That is a compiler-identity pin, not a doc-content
  pin, and re-pinning it would mean admitting a not-yet-reviewed compiler
  build without review — outside XC-008's charter.
- One `test_qualified_candidate_names_are_excluded_from_production_surfaces`
  failure: `manifests/g2-2.2.6.10-source-only.json` and
  `manifests/g2-2.2.6.10-touch-source-experimental.json` (both newly landed,
  uncommitted, by concurrent items) aren't yet registered in that test's
  `ACTIVE_PRODUCTION_SURFACES` census. That census isn't one of the four
  SHA-256-pinned docs either; registering new manifests is the landing
  item's own responsibility (the same pattern XC-002 documented in
  `tooling-completion-readiness-truthfulness.md`), not XC-008's.

Also noticed, not touched: an untracked scratch file
`manifests/tmpi4nqojp4.scratch.json` appeared in the manifests directory
during this session (not produced by anything in this doc-pin closure);
left for its owner to clean up, per the concurrent-fleet rule against
touching files outside this item's scope.

## What this closes

The one confirmed pin/content mismatch across the four SHA-256-pinned docs
is fixed and reverified. No prose in the four docs themselves needed
folding-in beyond what was already committed — `memory-map.md`,
`source-coverage.md`, and `upstream-inventory.md` all already matched their
pins, so there was no unfolded research content to add this pass. This is a
tooling/process item with no flash bytes and no functional-coverage claim.
