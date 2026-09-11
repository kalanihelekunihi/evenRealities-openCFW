# Cross-cutting tooling: keeping the completion-readiness and license-policy censuses truthful

Status date: 2026-09-11 (XC-002)

## Scope

`make -C g2 completion-readiness` and the community-distribution gates it feeds
are self-checking: several of their sub-analyzers hard-pin the *set* of files
they expect to see a given property in (a "census"), and fail closed the
moment the tree drifts from that pinned set. That is correct behavior — an
unclassified new file must never silently count as reviewed or as MIT — but it
means the gate goes red every time unrelated, legitimate work lands a file the
census doesn't know about yet. This note records two such drifts found and
fixed while the AM/BL/CD/CS/TC/XC fleet was landing GX8002 and Touch
source-image work on 2026-09-11, and one that was found but deliberately left
for its owning workstream.

## Fixed: false-positive raw-directive detection in `analyze_g2_production_raw_encoding_quality.py`

`tools/analyze_g2_production_raw_encoding_quality.py` scans every `.c/.h/.S/.s/.asm`
file under `components/` for GNU-assembler `.byte/.short/.hword/.word`
directives, to prove that no production-routed source still carries raw
transcribed instruction bytes. Its regex, `\.(byte|short|hword|word)\s+([^"\\]+)`,
matched not only real directives (always followed by an operand list, e.g.
`".word 0x1234\n"` inside an inline-asm string) but also ordinary C99
designated-initializer and union-member syntax such as
`{.word = AUDIO_WORD(0)}` or `register_value.word = x` — both spelled
`.word` immediately followed by whitespace, exactly like a directive.

Two newly landed, plain-C, MIT-licensed GX8002 register-access files
(`components/shared/gx8002/runtime_gx8002_i2s.c`,
`components/shared/gx8002/runtime_gx8002_vad_curves.c`) use a `union { uint32_t
word; ... }` pattern for typed register access and tripped this false
positive, failing the `public component raw-directive source census changed`
check even though neither file contains a byte of transcribed instruction.

Fix: the directive is never followed by `=` (a real assembler operand list
never starts with `=`; a designated initializer or assignment always does), so
`DIRECTIVE` now excludes that shape:
`\.(byte|short|hword|word)\s+(?!=)([^"\\]+)`. Verified against both known real
directives (`components/apollo_main/core_overlay/duration_delay.c`,
`components/bootloader/core_overlay/runtime_thread_pointer_422874.c` — same
match counts before/after) and both new false positives (zero matches after).
Added `tests.test_analyze_g2_production_raw_encoding_quality
.test_designated_initializers_are_not_mistaken_for_directives` as a narrow
regression guard.

## Fixed: stale community-controller and Touch source-image censuses in `analyze_g2_project_license_normalization.py`

The same GX8002 landing (175 new reviewed C/H/S files under
`components/shared/gx8002/`, all carrying `SPDX-License-Identifier: MIT`) and
a new Touch NVIC header (`components/touch/source_image/psoc4000t_nvic.h`,
also MIT) were not yet listed in the hand-maintained manifests
`tools/manifests/g2-project-mit-normalization-community-controllers.txt` and
`tools/manifests/g2-project-mit-normalization-touch-source-image.txt`, which
the analyzer compares the live directory scan against verbatim. Both censuses
are additive facts (a new file with a correct SPDX header, not a
reclassification), so the fix was to append the missing paths and update the
four pinned counts that depend on them:

| Constant | Old | New |
|---|---:|---:|
| `EXPECTED_COMMUNITY_CONTROLLER_PROJECT_PATH_COUNT` | 109 | 284 |
| `EXPECTED_TOUCH_SOURCE_IMAGE_PROJECT_PATH_COUNT` | 9 | 10 |
| `EXPECTED_DISTRIBUTED_TARGET_COUNT` | 919 | 1095 |
| (test) `community_controller_and_adapter_source_files` | 112 | 287 |

All 175 + 1 newly-censused files were confirmed to already carry
`SPDX-License-Identifier: MIT` before being added — the fix registers an
already-true fact, it does not relicense anything. `make -C g2
completion-source-ownership-gate`-adjacent unit tests
(`tests.test_analyze_g2_project_license_normalization`, 16 cases) and the tool
run clean afterward (`distributed_project_files_normalized_mit == 1095 ==
distributed_project_mit_normalization_targets`, zero pending).

## Fixed: stale Case source-image census (`board_config.h`)

While re-verifying after the fixes above, a third drift appeared live: a
concurrently landing Case workstream added
`components/case/source_image/board_config.h` (MIT-licensed board-routing
configuration) to the tree, which is not yet in
`tools/manifests/g2-project-mit-normalization-case-source-image.txt`. Same
shape, same fix: appended the path, bumped
`EXPECTED_CASE_SOURCE_IMAGE_PROJECT_PATH_COUNT` 7→8 and
`EXPECTED_DISTRIBUTED_TARGET_COUNT` 1095→1096, and updated the matching test
assertions. This is a good illustration of why this item is a repeating
chore rather than a one-time fix: the fleet is landing new, already-compliant
files faster than the hand-maintained censuses can be updated by hand, and
each landing needs exactly this kind of small, additive registration.

A fourth drift (one more GX8002 file, `runtime_gx8002_dcache_disable.c`, also
MIT) appeared and was fixed the same way seconds later while re-verifying the
third fix — `EXPECTED_COMMUNITY_CONTROLLER_PROJECT_PATH_COUNT` 284→285,
`EXPECTED_DISTRIBUTED_TARGET_COUNT` 1096→1097. The manifest `.txt` itself was
found modified on disk between this pass's read and write (another
concurrent edit landed in the same file); the census was re-diffed from
scratch after writing to confirm no entries were lost or duplicated before
trusting the new pinned counts. At the rate the fleet is landing new,
already-compliant GX8002 files, a fully drift-free instant is unlikely to
last; this item's job is to keep re-closing the gap, not to reach a
permanently static census.

## Left alone: Touch analysis-input receipt (`components/touch/source_image/startup.c`)

`analyze_g2_completion_readiness.py`'s `_touch_generation_receipt` check
hash-pins `components/touch/source_image/startup.c` (and 68 other Touch
inputs) via `tools/manifests/g2-touch-final-classification-summary.json`.
At the time of this pass, `startup.c`, `README.md`, and
`tools/manifests/g2-touch-source-image-summary.json` were all showing as
locally modified (`git status`) by a concurrent Touch workstream (fleet run
`20260911-123100`, item `XC-004` is transparent-image envelope fitting; the
Touch classification/receipt regeneration is a different, actively-running
item's own write path). Re-pinning that receipt is that workstream's
responsibility, not this item's — XC-002 does not touch Touch-owned inputs or
their generation receipt. `make completion-readiness` and
`tests.test_analyze_g2_completion_readiness` will stay red on this one check
until that workstream's edit lands and re-runs its own generator; re-run this
item after that to confirm the aggregate gate. No transparent-source-ledger or
`docs/reports/.../assessment-data.json` regeneration was attempted while this
was unresolved, since both transitively call `analyze_g2_completion_readiness
.analyze()` and would fail the same way, and `docs/reports/.../assessment-data.json`
must only be written by `tools/generate_g2_completion_report.py`, never by hand.

## Reviewed-source registration (`tools/transparent/reviewed_sources.json`)

Checked for drift: as of this pass, no AM item in `remaining-work.md` is
`done` yet (fleet run just started), and `docs/research/` has exactly one
reviewed-source audit (`g2-cortex-m55-reviewed-source.md`, the four Cortex-M55
atomic/barrier functions already registered). `tools/transparent
/reviewed_sources.json` matches that audit exactly — no new reviewed,
production-routed C exists yet that isn't already registered. This is a
negative result, not a no-op: it was verified, not assumed.

## What remains

* Re-run `make -C g2 completion-readiness` once the Touch analysis-input
  receipt is refreshed by its owning workstream, then run `make -C g2
  completion-assessment` (writes `docs/reports/openCFW-completion-2026-08-28
  /assessment-data.json` via its own tool) to publish a fresh snapshot.
* `make -C g2 transparent-ledger` was not run this pass: `XC-004`
  ("transparent-image envelope fitting", fleet run `20260911-123100`) is
  concurrently regenerating exactly this pipeline
  (`build/transparent/function-db.json` and `region-map.json` are already
  fresher than the checked-in `docs/transparent-source-ledger.md`, dated from
  this same session). Regenerating the ledger now would race that item's
  shared `build/transparent/` output and would immediately go stale again once
  it lands. Re-run `make -C g2 transparent-ledger` (under the integration
  lock) after `XC-004` completes.
* Re-check both fixed censuses and the reviewed-source registration again on
  the next XC-002 pass — this is inherently a repeating chore as more AM/CS
  items land reviewed C and community-controller sources.
