# Cross-cutting source-only manifest and package gate (XC-001)

Date: 2026-09-11. This closes the *tooling* half of the source-only goal:
a manifest that names a `source_build` provider for every one of the six
EVENOTA components, a `make source-only` target that assembles and
self-verifies the resulting package on macOS, and a fail-closed
`--require-source-only` gate that reports exactly which components, and how
many bytes per component, still block source-only status. It does **not**
close any component; touch, case, and the codec remain source-incomplete
today, and the gate is expected to fail until they are not. That failure is
the deliverable, not a defect.

## What was added

| Artifact | Role |
| --- | --- |
| `manifests/g2-2.2.6.10-source-only.json` | Extends `g2-2.2.6.10-core-source.json`; overrides `codec`, `touch`, and `case` to `source_build` providers (Apollo main/bootloader/EM9305 are inherited unmodified — core-source already routes them to `source_build`) |
| `tools/build_g2_source_only_manifest.py` | Repins the three overridden providers' size/SHA-256 from the current on-disk builds (`build/gx8002-source-candidate/firmware_codec.hybrid-candidate.bin`, `build/touch-source-image/firmware_touch.bin`, `build/case-source-image/firmware_box.bin`) and its own `regions` partitions, then computes and pins `package.expected_size`/`expected_sha256` by a real (non-strict) assembly pass |
| `make -C g2 source-only` | `codec-source-experimental touch-source-image case-source-image` (build), repin, `open_cfw.py build` + `open_cfw.py verify` against the manifest (assemble/self-verify) |
| `tools/analyze_g2_completion_readiness.py --require-source-only` | New `source_only_gate()` function and CLI flag; exit code 6 on failure, with an unconditional (JSON or not) per-component byte report |
| `make -C g2 source-only-gate` | Runs the gate above |

## Why this is not the same as "component done"

The completion goal (`docs/source-only-goal.md`, "Completion conditions")
explicitly excludes two things that a naive "does the manifest point at a
`.c` file" check would miss:

1. **Retained bytes inside an otherwise source-built provider.** The codec
   provider here is the experimental GX8002 hybrid
   (`manifests/g2-2.2.6.10-codec-source-experimental.json`'s provider,
   reused verbatim): 214 C functions and source-authored IRQ/reset/NPU
   assembly, but per `docs/research/gx8002-source-candidate-build.json`
   (kind `retained_stock`) it still has 190,912 retained executable bytes,
   5,124 runtime-data bytes, 9,164 accelerator-command bytes, and 120,800
   model bytes -- 326,000 of 326,092 total. Selecting this provider makes
   the manifest structurally "all `source_build`", but does not make the
   codec byte-complete.
2. **A source candidate that is not production-routed.** The touch and case
   `source_build` providers here are real, link-complete, FWPK/EVEN-wrapped
   images built entirely from `components/shared/touch` and
   `components/shared/case` source
   (`components/touch/source_image/build_image.py`,
   `components/case/source_image/build_image.py`) -- 15,592 and 18,948
   bytes respectively, both far smaller than the 34,464/55,784-byte stock
   images because most of stock touch/case functionality has not yet been
   reconstructed. `tools/manifests/g2-touch-source-image-summary.json` and
   `g2-case-source-image-summary.json` both record
   `"production_routed": false` and
   `"hardware_validation": "blocked by unavailable physical evidence"` --
   these are software-link-complete candidates, not the shipped provider,
   by the project's own accounting.

`source_only_gate()` therefore requires, per component, both
`source_complete` (`release_blocking_bytes == 0`, i.e. no retained
`official_blob`/typed-external/candidate-not-routed byte left uncovered)
**and** `production_routed`. A component with zero blocking bytes but
`production_routed: false` still fails the gate -- this is the exact
"candidate source that is not production-routed" exclusion from the
completion goal, and is covered by
`tests.test_analyze_g2_completion_readiness_source_only::SourceOnlyGateTests::test_unrouted_candidate_blocks_even_with_zero_blocking_bytes`.

## Two different `--require-source-only` flags

`tools/build_gx8002_source_candidate.py` already had its own, narrower
`--require-source-only` flag (codec-only, checks `byte_ownership.retained_stock`
in its own build report). That flag predates this item and is unrelated;
it is not the cross-cutting, six-component gate this item asked for. The
one this item adds lives on `tools/analyze_g2_completion_readiness.py`,
which already composed the per-component byte ledger for all six
components (`components["<name>"]["release_blocking_bytes"]`,
`["production_routed"]`) that every other completion gate
(`--require-classified`, `--require-source-complete`, ...) reads from.
Reusing that ledger, rather than re-deriving it, is what lets the gate print
an *exact* per-component byte report instead of a coarse yes/no.

## Manifest mechanics (why the two-pass repin exists)

`tools/open_cfw.py`'s `build`/`verify` commands validate every provider's
declared `size`/`sha256` against the file on disk, and (in `build`, via
`strict_release=True`) require `package.expected_size`/`expected_sha256` to
be present and correct. Those package-level pins cannot be known before the
providers are assembled, so `build_g2_source_only_manifest.py` runs in two
passes: (1) patch the three owned providers' `size`/`sha256` from disk and
the touch/case `regions` partitions from the new provider size, (2) assemble
via a scratch copy of the manifest with `strict_release=False` to learn the
resulting image's bytes, then write `package.expected_size`/`expected_sha256`
into the real file. A subsequent `open_cfw.py build` (`strict_release=True`)
then round-trips byte-identically -- verified live on 2026-09-11 via a
private output directory (`build/continue-analysis/XC-001/source-only-check`,
not the shared `build/source-only/`):

```
Built package/g2-openCFW-s200_v2.2.6.10-source-only.evenota.bin
  size: 4695072 bytes
  sha256: d940b0025228d799b9e19a68be959efe8c79a0a29a676d171cb7735463ac587f
  reference: byte-identical
  placed flash regions: 7822
  unresolved flash regions: 0
```

(This exact size/hash will drift as touch, case, and the codec are rebuilt
by ongoing work -- see the "concurrent session fleet" note below -- so it is
recorded here as evidence the mechanism works, not as a pin to defend.)

The Apollo main, Apollo bootloader, and EM9305 providers are **not**
overridden by this manifest; they are inherited from
`g2-2.2.6.10-core-source.json` as-is, so this manifest never edits
core-source's own provider pins (only its own three, new,
`g2-2.2.6.10-source-only.json`-owned overrides).

## Live gate output

`make -C g2 source-only-gate` (`analyze_g2_completion_readiness.py
--require-source-only`) currently fails before even reaching the
source-only computation: `analyze()` raised `Touch analysis input identity
changed: components/touch/source_image/startup.c`, because another agent's
in-flight touch work (`git status`: `M
g2/components/touch/source_image/startup.c`, plus new
`manifests/g2-2.2.6.10-touch-source-experimental.json`) had not yet
regenerated `tools/manifests/g2-touch-source-image-summary.json` at the
moment this was run. This is the same fragility every other
`analyze_g2_completion_readiness.py` gate already has against concurrent
touch/case/codec work (see the "openCFW concurrent session fleet" pattern);
it is not introduced by this item and this item does not fix it (out of
scope -- XC-001 owns the gate, not touch's generation-receipt binding). Once
the tree is quiescent, `--require-source-only` is expected to still exit 6
and print all six components as blocking, since none are both source-complete
and production-routed yet. `source_only_gate()` itself is exercised directly,
independent of that live fragility, by
`tests/test_analyze_g2_completion_readiness_source_only.py`.

## What remains

- **codec**: replace the 326,000 retained bytes in the GX8002 hybrid with
  source (NationalChip grus / C-SKY route; see `docs/source-only-goal.md`
  and `docs/research/gx8002-upstream-object-candidates.md`).
- **touch**, **case**: the source images are link-complete and package
  correctly, but are not `production_routed`; both are blocked on
  resident-ABI hardware qualification per their summaries
  (`hardware_validation: blocked by unavailable physical evidence`), and
  touch/case still have large `typed_external_or_unsupported` /
  `still_unclassified` byte buckets per `analyze_g2_completion_readiness.py`.
- **apollo_bootloader**, **apollo_main**, **ble_em9305**: already
  `production_routed`, but still carry nonzero `release_blocking_bytes`
  (retained/candidate bytes) per the live readiness report; see
  `docs/source-coverage.md` for their current per-function status.
- Re-run `make -C g2 source-only-gate` after each component closure lands;
  it will name exactly which components (and how many bytes) still block,
  with no manual byte accounting required.
