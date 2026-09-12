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

## 2026-09-11 follow-up pass (XC-002, fleet run 20260911-133849)

HEAD `284b98a7` (13:26) folded a large batch of fleet work without re-pinning
several ledgers. This pass re-pinned everything mechanical and left two
genuine content conflicts for their owners. Integration lock was held by a
dead `AM-009` run (row `failed`, no live process, age >3600s); the lock's own
`CA_LOCK_STALE_SEC` override was used to break and acquire it, then released
at the end of the pass.

### Fixed: bootloader 4-byte source admission (59009/87985 -> 59013/87981)

HEAD routed one new 4-byte in-place data leaf
(`open_cfw_bootloader_critical_transfer_base`, SRAM staging-base literal
`0x200270C8` at runtime `0x00430B0C`, file offset 133900) with a byte-exact
builder check (`expected.sha256 == stock_sha256 == 9e8039...`, enforced by
`build_component.py`, build passes). A stale 13:04 `build-report.json`
(transient pre-commit tree) initially masked this as a provider-hash
mismatch; a clean `make -C g2 bootloader-component` rebuild from HEAD
reproduced the manifest provider (`163840/13e2ce...`) exactly and exposed the
real 4-byte `official_blob -> source_compiled` drift. Re-pinned, all
apple-clang only (linux-clang historical pins untouched):

* `manifests/g2-2.2.6.10-core-source.json`: interval
  `bootloader_mode_wrapper_word_transfer_gap_430b0c_430b10` flipped to
  `source_compiled` (name/output/function text kept byte-identical: two other
  tools key on the name, see below), plus provider `source_owned_bytes` /
  `opaque_base_bytes`.
* `tools/analyze_g2_completion_readiness.py` retained-complement pin and its
  test (`87_985 -> 87_981`, test `59_009 -> 59_013`).
* `tools/analyze_g2_bootloader_mspi_control_4251c0.py`,
  `analyze_g2_bootloader_mspi_lifecycle_425066.py`,
  `analyze_g2_bootloader_mspi_transfer_interrupt_4262e0.py`,
  `analyze_g2_bootloader_post_mspi_frontier.py` (plus its test and
  `tests/test_runtime_littlefs_alloc_lookahead.py`).
* The frontier tool keys manifest intervals by name
  (`by_name["bootloader_mode_wrapper_word_transfer_gap_430b0c_430b10"]`), so
  the name was deliberately NOT renamed; only its expected status tuple went
  `official_blob -> source_compiled`. The BL owner's integrate tool
  (`integrate_g2_bootloader_redirect_init_overlay.py:3058`) still templates
  the old opaque description — rename/reword is deferred to the next BL
  integration pass that re-runs that generator.
* Verified: `mspi_control` and `post_mspi_frontier` gates pass;
  `transfer_interrupt` reports 404 production C bytes admitted;
  `test_transparent_reviewed_source` (8 tests) passes.
* Evidence gap (no bytes claimed on it): the overlay entry cites
  `docs/research/g2-bootloader-critical-transfer-base-literal-430b0c-source-closure.md`,
  which does not exist in the tree. Byte-accounting rests on the builder's
  byte-exact check, not on that doc, but the BL owner should write it.

### Fixed: Touch generation receipt (startup.c re-pin via write path)

HEAD reworked `components/touch/source_image/startup.c` (named NVIC config,
`psoc4000t_nvic.h`) without re-running the Touch generator. No Touch item is
live, so `analyze_g2_touch_final_frontier.py --write-manifests` was run: only
receipt hashes changed in the two summary JSONs, classification metrics
identical. `tests.test_analyze_g2_touch_final_frontier` (13 tests) passes.

### Fixed (pending one live file): license community census (+13 MIT files)

Registered 13 committed MIT GX8002 files (analog LDO/config-update, stage-1
header/body-pad/tail pairs, SPL reset entry, stage-2 libc pair, UART stage-2
diagnostics) in
`tools/manifests/g2-project-mit-normalization-community-controllers.txt`
(sorted position, SPDX verified per file) and bumped
`EXPECTED_COMMUNITY_CONTROLLER_PROJECT_PATH_COUNT` 285 -> 298 and
`EXPECTED_DISTRIBUTED_TARGET_COUNT` 1097 -> 1110, plus the three companion
test pins (community+adapter files 288 -> 301, MIT-compatible 285 -> 298,
distributed targets 1097 -> 1110). Residual failure is exactly
one file: CD-001's live untracked
`components/shared/gx8002/runtime_gx8002_uart_stage1_divmod.c` (MIT, still
being edited) — registering it now would pin uncommitted work, so it stays a
followup: +1 manifest line, 298 -> 299, 1110 -> 1111 once CD-001 lands.

### NOT fixed (owner content conflicts, gate working as designed)

* Raw-encoding gate: `components/bootloader/core_overlay/runtime_spotmgr_shared_literals_42a078.c`
  (HEAD, 13 naked-asm literal pools, six `.short 0x0000` alignment pads) trips
  `public source contains raw instruction halfwords`. The pads are documented
  alignment zeros, not transcribed instructions — but the fail-closed gate
  bans `.short`/`.hword`/`.byte` in all public source with no census path
  (only `.word` literals are censusable), so neither a manifest edit nor a
  unilateral gate exception is honest. The BL owner must re-express the pads
  without `.short` or propose a reviewed gate extension with tests. The file
  is correctly NOT production-routed (absent from `overlay.json`).
* BL-006 (live, same fleet run) edited `overlay.json` (+9 `in_place_data`
  entries, +192 source / -192 opaque => 59205/87789) and added untracked
  `runtime_bl006_*.c` files at 13:49-13:52, after this pass's rebuild. Its
  numbers were deliberately NOT pinned: pinning transient uncommitted work
  would corrupt the committed ledger. BL-006 must re-pin the manifest,
  provider stats, and the five apple-clang pins above (now 59205/87789) when
  it lands. The lifecycle tool (clean-temp rebuild) already reflects the new
  worktree and fails until that re-pin happens — correct fail-closed
  behavior, not a regression.
* `docs/reports/openCFW-completion-2026-08-28/assessment-data.json` was NOT
  regenerated: `generate_g2_completion_report.py` runs `readiness.analyze()`,
  which is still red (spotmgr). Regenerating against a red audit would
  publish a stale/failing snapshot; re-run `completion-assessment` after the
  two blockers above clear.
* `docs/transparent-source-ledger.md` was NOT regenerated: the ledger renders
  from `build/transparent/source|image` stages, which do not exist in the
  tree (only today's harvest DB: 7449 functions, matching the ledger's
  inputs). A full rebuild is XC-004's failed-item pipeline with known
  envelope-fitting failures. Verified instead that ledger inputs are
  unchanged: `reviewed_sources.json` untouched since Sep 7 (4 functions, 34
  bytes — matches ledger line "4 placed functions use reviewed C") and no new
  reviewed Apollo C exists to register (`components/shared/cortex_m55/` still
  exactly the 4 registered files). The committed ledger remains an accurate
  rendering of its inputs.

No hardware operation occurred; hardware qualification remains blocked by
unavailable physical evidence. This item has no flash-range component.

## 2026-09-11 evening pass (XC-002, fleet run 20260911-154540)

Readiness is still red, but the failure queue behind the fail-fast checks
has been worked through for the first time: earlier passes never got past
the community-disk check, so the case/EM9305 disk checks had never been
verified against the live tree. They are now.

### Fixed: EM9305 MIT census (+2 committed toolchain files)

`components/em9305/source_overlay/toolchain/TOOLCHAIN.md` and
`fetch_arc_toolchain.sh` (the XC-003 macOS-native ARC toolchain pin,
committed at HEAD `284b98a7`) were missing from
`tools/manifests/g2-project-mit-normalization-em9305-source-image.txt`.
Both carry inline `SPDX-License-Identifier: MIT` (verified with the same
regex the tool enforces), are disjoint from every other MIT set, and are
package files, not support files. Registered in sorted manifest position;
`EXPECTED_EM9305_SOURCE_IMAGE_PROJECT_PATH_COUNT` 19 -> 21,
`EXPECTED_DISTRIBUTED_TARGET_COUNT` 1110 -> 1112 (union recomputed:
749+22+298+10+8+21+2+4 with 2 overlaps = 1112, exact). Companion test pins
updated (`em9305_source_image_project_mit_files` 19 -> 21, package files
11 -> 13, exact path set +2, distributed targets 1110 -> 1112).

### Fixed: Case census vs gitignored `build/` outputs (gate clarification)

The Case source-image build left 14 gitignored artifacts under
`components/case/source_image/build/` (ELF, `.bin`, objects, map,
summary JSON; built ~12:50, still on disk). The case disk census had no
`build` exclusion, so it would fail once reached. Deleting another
workstream's fresh build outputs was rejected; instead the census now
excludes the `build` path component via a `_is_case_package_source`
helper, mirroring the EM9305 census's long-standing `build` exclusion in
the same tool. Build products are not distributed MIT targets, so this
narrows the gate to its documented intent rather than weakening it.
`CasePackageSourceStaticTests` (2 tests, pass) pins the helper on a tmp
tree and on the live tree, and asserts no `/build/` entry is ever
registered in the case manifest. Verified post-edit: case disk == manifest
(8 == 8), EM9305 21 == 21, Touch 10 == 10.

### Left alone (owner lanes, gate working as designed)

* Raw-encoding gate: `runtime_spotmgr_shared_literals_42a078.c` (committed
  at HEAD, still not production-routed, still 6 `.short 0x0000` pads)
  keeps `make completion-readiness` and the whole
  `test_analyze_g2_completion_readiness` suite red at `analyze()` entry.
  Re-expressing another component's committed pads, or carving a gate
  exception unilaterally, is not this item's call; still BL owner's.
* Community-disk census: live CD-001 (in-progress, same fleet run) now has
  TWO untracked files on disk —
  `components/shared/gx8002/runtime_gx8002_uart_stage1_divmod.c` (MIT) and
  the newer `runtime_gx8002_uart_boot_stage1_reset.S`. Both stay
  unregistered until CD-001 lands; registering uncommitted work would pin a
  moving target. This single check keeps the full license tool and its
  test class red, which in turn keeps every check behind it unverified
  through `analyze()` (verified instead by direct set computation above).
* Bootloader pins need no action: the manifest still reads
  `source_owned_bytes` 59013 / `opaque_base_bytes` 87981, matching the tool
  and test pins. BL-006's live `overlay.json` edits (+9 `in_place_data`)
  are uncommitted and unbuilt; re-pin remains BL-006's landing chore.
* `reviewed_sources.json` needs no action (negative result, verified not
  assumed): unchanged since Sep 7; `components/shared/cortex_m55/` still
  exactly the 4 registered files; the only new Apollo C on disk
  (`lvgl_grid_engine.c`, `lvgl_layout_style_getters.c`, BL-006 files) is
  untracked and unreferenced by the overlay and the transparent builder.
  `test_transparent_reviewed_source` 8/8 passes.
* `docs/reports/openCFW-completion-2026-08-28/assessment-data.json` NOT
  regenerated: the generator runs `readiness.analyze()`, still red on
  spotmgr. Its one stale count (`em9305_source_image_project_mit_files`
  19) refreshes with the next green snapshot. Never hand-edited.
* `docs/transparent-source-ledger.md` NOT regenerated: the report needs
  `build/transparent/source|image` stages, which do not exist in this
  worktree (report-only run to a private dir fails on missing
  `source/MANIFEST.json`; no shared files touched). Full rebuild is
  XC-004's failed pipeline. Verified instead that ledger inputs match the
  committed rendering: function-db 7,449 functions / 1,394,848 code bytes,
  tiers 1467/253716 + 3002/709102 + 2643/345004 + 337/87026, gaps
  data 2106/2107056 + pointer-table 282/19332 + constant-fill 2/2 +
  ota-staging-header 1/32 — all identical to the ledger.

### Test evidence this pass

* New `CasePackageSourceStaticTests`: 2/2 pass.
* `test_transparent_reviewed_source`: 8/8 pass.
* `test_analyze_g2_touch_final_frontier`: 13/13 pass (Touch receipt clean).
* `test_analyze_g2_project_license_normalization`: full-class
  `setUpClass` errors on the CD-001 community drift (2 files); the 4
  runnable tests pass.
* `test_analyze_g2_completion_readiness`: suite errors in `setUpClass` on
  the BL-owned spotmgr pads; 0 tests ran.

No hardware operation occurred; hardware qualification remains blocked by
unavailable physical evidence. This item has no flash-range component.

## 2026-09-11 late pass (XC-002, fleet run 20260911-180340)

HEAD is still `284b98a7`; every tree change since the evening pass is
uncommitted concurrent work. Nothing new is pinnable, so this pass made no
tool, manifest, or test edits — only re-verification. All blockers below are
unchanged in signature; each names its owner.

### Still red (owner lanes, gate working as designed)

* `python3 tools/analyze_g2_completion_readiness.py` fails at the same
  fail-fast entry: `public source contains raw instruction halfwords:
  components/bootloader/core_overlay/runtime_spotmgr_shared_literals_42a078.c`
  (6 `.short 0x0000` alignment pads, committed at HEAD, file still not
  production-routed). `tests.test_analyze_g2_completion_readiness` errors in
  `setUpClass` with the identical traceback; 0 tests ran. Re-expressing the
  pads without `.short` (or a reviewed gate extension with tests) is still
  the BL owner's call.
* License community census: live disk exceeds the manifest by exactly the
  same 2 CD-001 files (`runtime_gx8002_uart_stage1_divmod.c`,
  `runtime_gx8002_uart_boot_stage1_reset.S`), both still untracked and both
  still carrying `SPDX-License-Identifier: MIT` (verified). Still
  unregistered: pinning paths CD-001 is actively editing would target a
  moving file set, and CD-001's own landing edit will touch the same
  manifest. Followup once both are committed: +2 manifest lines in sorted
  position, tool `298 -> 300` / `1112 -> 1114`, test `301 -> 303` /
  `298 -> 300` / `1112 -> 1114`.

### Re-verified clean (direct set computation with the tool's exact logic)

* Touch disk == manifest (10 == 10), Case disk == manifest (8 == 8, `build/`
  exclusion holds), EM9305 disk == manifest (21 == 21; a naive first diff
  false-alarmed on 8 gitignored `build/`/`__pycache__`/`.pyc` artifacts the
  tool correctly excludes).
* `reviewed_sources.json` needs no action (negative result, verified not
  assumed): `components/shared/cortex_m55/` still exactly the 4 registered
  files; the 2 untracked LVGL files have 0 references in the Apollo overlay;
  the 6 untracked BL-006 files are referenced only by BL-006's uncommitted
  working-tree bootloader overlay (68 mentions), never by the transparent
  Apollo image. `test_transparent_reviewed_source` 8/8 and
  `test_analyze_g2_touch_final_frontier` 13/13 pass (21/21 combined).
* Bootloader pins need no action: committed manifest still reads
  `source_owned_bytes` 59013 / `opaque_base_bytes` 87981, matching the tool
  and test pins. BL-006's working-tree overlay edits remain unbuilt and
  uncommitted; re-pin stays BL-006's landing chore.
* `docs/reports/openCFW-completion-2026-08-28/assessment-data.json` NOT
  regenerated: the generator runs `readiness.analyze()`, still red on
  spotmgr (its `em9305_source_image_project_mit_files` 19 stays stale until
  the next green snapshot; never hand-edited).
* `docs/transparent-source-ledger.md` NOT regenerated: `build/transparent/`
  holds only `function-db.json`/`region-map.json`/`DB-SUMMARY.json`, no
  `source|image` stages (full rebuild is XC-004's failed pipeline). Ledger
  inputs verified identical to the committed rendering: 7,449 functions /
  1,394,848 code bytes, gaps data 2106/2107056 + pointer-table 282/19332 +
  constant-fill 2/2 + ota-staging-header 1/32.

No hardware operation occurred; hardware qualification remains blocked by
unavailable physical evidence. This item has no flash-range component.

## 2026-09-11 night pass (XC-002, fleet run 20260911-191248)

HEAD is still `284b98a7`; every tree change since the late pass is
uncommitted concurrent work, now substantially larger: the bootloader
overlay grows by 1035 additive lines (BL-006, 7 new untracked
`runtime_bl006_*.c` files) and the Apollo overlay by 11550+/3557-
(AM-040 64-leaf landing). Nothing new is pinnable, so this pass again
made no tool, manifest, or test edits -- only re-verification with the
tools' own logic. One gate signature changed; the rest are unchanged.

### Changed signature: BL partition check now fails before the spotmgr check

`python3 tools/analyze_g2_completion_readiness.py` now fails at
`bootloader current interval partition disagrees with its builder`
(`analyze_g2_completion_readiness.py:794`) instead of at the spotmgr
raw-halfwords entry. Cause, quantified: the working-tree manifest is
internally consistent (regions partition 59013 source / 87981 opaque,
matching the provider pins), but the gitignored
`components/bootloader/core_overlay/build/build-report.json` was rebuilt
at 18:11 from BL-006's uncommitted overlay and now reads 59557 / 87437
(delta exactly +544 source / -544 opaque). A gitignored build artifact
rebuilt from uncommitted work now shadows the committed ledger -- the
re-pin (manifest regions, provider stats, the five apple-clang pins) is
BL-006's landing chore, as before; pinning it now would target a moving
file set. `tests.test_analyze_g2_completion_readiness` errors in
`setUpClass` with the identical message; 0 tests ran.

### Still red behind it (verified directly, masked by fail-fast order)

* Raw-encoding gate: `tools/analyze_g2_production_raw_encoding_quality.py`
  run directly still fails on exactly
  `components/bootloader/core_overlay/runtime_spotmgr_shared_literals_42a078.c`
  (committed pads, file still not production-routed). In `analyze()` this
  check sits at line 1483, after the partition check, so it is currently
  masked -- still the BL owner's call, unchanged.
* License community census: drift grew 2 -> 4 files, all CD-001's
  untracked MIT work (`runtime_gx8002_uart_stage1_divmod.c`,
  `runtime_gx8002_uart_boot_stage1_reset.S`, plus the newer
  `runtime_gx8002_uart_stage1_pmubits.c` and
  `runtime_gx8002_uart_stage1_pmusbit.S`; SPDX MIT verified on the two
  new files). Followup once CD-001 lands: +4 manifest lines in sorted
  position, tool `298 -> 302` / `1112 -> 1116`, same bumps in the
  companion test pins. `tests.test_analyze_g2_project_license_normalization`
  runs 4 tests with 1 census error, as expected.

### Re-verified clean (tool's own logic, not hand-rolled sets)

* Touch disk == manifest (10 == 10), Case disk == manifest (8 == 8,
  `build/` exclusion holds), EM9305 disk == manifest (21 == 21),
  computed by importing the tool's own roots, helpers, and support sets.
* `reviewed_sources.json` needs no action (negative result, verified not
  assumed): unchanged since Sep 7 (4 functions, 34 bytes); the committed
  (HEAD) Apollo overlay references none of the new untracked Apollo or
  BL-006 files (0 mentions); `components/shared/cortex_m55/` untouched.
  The fleet's new reviewed C (AM-040 overlay leaves, BL-006 pools, CD-001
  stage-1 leaves) routes through component overlays/candidates, not the
  transparent Apollo image, so no transparent registration is due.
* `docs/reports/openCFW-completion-2026-08-28/assessment-data.json` NOT
  regenerated: the generator runs `readiness.analyze()`, still red (its
  `em9305_source_image_project_mit_files` 19 stays stale until the next
  green snapshot; never hand-edited).
* `docs/transparent-source-ledger.md` NOT regenerated: `build/transparent/`
  still holds only `function-db.json`/`region-map.json`/`DB-SUMMARY.json`
  (no `source|image` stages; full rebuild stays XC-004's failed
  pipeline). Ledger inputs verified identical to the committed rendering:
  function-db code bytes 1,394,848 matches the ledger's 7,449 functions /
  1,394,848 bytes.

### Test evidence this pass

* `tests.test_transparent_reviewed_source` + Touch frontier: 21/21 pass.
* `tests.test_analyze_g2_completion_readiness`: setUpClass error on the
  BL partition disagreement; 0 ran (owner: BL-006).
* `tests.test_analyze_g2_project_license_normalization`: 4 ran, 1 census
  error on the 4 CD-001 files (owner: CD-001).
* Raw-encoding tool direct run: fails only on the known spotmgr file
  (owner: BL).

No hardware operation occurred; hardware qualification remains blocked by
unavailable physical evidence. This item has no flash-range component.

## 2026-09-11/12 handoff pass (XC-002, fleet run 20260911-194503)

HEAD is still `284b98a7`; every tree change since the night pass is
uncommitted concurrent work (AM-040 Apollo overlay growth, BL-006
bootloader overlay growth, CD-001 stage-1 leaves). Nothing newly
committed is pinnable, so this pass made no tool, manifest, or test
edits -- only re-verification with the tools' own logic. One drift
count changed; all blockers keep their owners.

### Unchanged signatures (owner lanes, gates working as designed)

* `python3 tools/analyze_g2_completion_readiness.py` still fails at
  `bootloader current interval partition disagrees with its builder`:
  working-tree manifest pins 59013 source / 87981 opaque (this item's
  earlier re-pin, intact), while the gitignored
  `components/bootloader/core_overlay/build/build-report.json` was
  rebuilt again (now 19:33) from BL-006's uncommitted overlay. Re-pin
  stays BL-006's landing chore. `tests.test_analyze_g2_completion_readiness`
  errors in `setUpClass` with the identical message; 0 tests ran.
* Raw-encoding tool run directly still fails on exactly
  `components/bootloader/core_overlay/runtime_spotmgr_shared_literals_42a078.c`
  (committed pads, file still not production-routed; still the BL
  owner's call, masked behind the partition check in `analyze()`).
* `reviewed_sources.json` needs no action (negative result, verified
  not assumed): untouched since Sep 7, `components/shared/cortex_m55/`
  still exactly the 4 registered files, and no transparent-builder
  reference (tools/transparent + build/transparent) mentions any new
  untracked Apollo/BL-006/CD-001 file. The fleet's new reviewed C
  routes through component overlays/candidates, not the transparent
  Apollo image, so no transparent registration is due.
* `docs/reports/openCFW-completion-2026-08-28/assessment-data.json`
  NOT regenerated: the generator runs `readiness.analyze()`, still red
  (its `em9305_source_image_project_mit_files` 19 stays stale until the
  next green snapshot; never hand-edited).
* `docs/transparent-source-ledger.md` NOT regenerated:
  `build/transparent/` still holds only
  `function-db.json`/`region-map.json`/`DB-SUMMARY.json` (no
  `source|image` stages; full rebuild stays XC-004's failed pipeline).
  Ledger inputs verified identical to the committed rendering:
  7,449 functions / 1,394,848 code bytes.

### Changed: license community drift grew 4 -> 6 files (still CD-001's lane)

Live disk now exceeds the manifest by 6 untracked files (was 4): the
known `runtime_gx8002_uart_stage1_divmod.c`,
`runtime_gx8002_uart_boot_stage1_reset.S`,
`runtime_gx8002_uart_stage1_pmubits.c`, `runtime_gx8002_uart_stage1_pmusbit.S`,
plus two newer stage-1 leaves `runtime_gx8002_uart_stage1_putsync.S`
and `runtime_gx8002_uart_stage1_serial.c`. Both new files carry
`SPDX-License-Identifier: MIT` (verified). All six stay unregistered
until CD-001 lands; followup once committed: +6 manifest lines in
sorted position, tool `298 -> 304` / `1112 -> 1118`, same bumps in the
companion test pins.

### Test evidence this pass

* `tests.test_transparent_reviewed_source` + Touch frontier: 21/21 pass.
* `CasePackageSourceStaticTests`: 2/2 pass (case `build/` exclusion holds).
* `tests.test_analyze_g2_completion_readiness`: setUpClass error on the
  BL partition disagreement; 0 ran (owner: BL-006).
* `tests.test_analyze_g2_project_license_normalization`: 4 ran, 1 census
  error on the 6 CD-001 files (owner: CD-001).
* Raw-encoding tool direct run: fails only on the known spotmgr file
  (owner: BL).

No hardware operation occurred; hardware qualification remains blocked by
unavailable physical evidence. This item has no flash-range component.

## 2026-09-12 morning pass (XC-002, re-verification only)

HEAD is still `284b98a7`; every tree change remains uncommitted
concurrent work (AM-040 Apollo overlay growth, BL-006 bootloader overlay
growth, CD-001 stage-1 leaves including the newer `idbit`/`serial`
tranche). Nothing newly committed is pinnable, so this pass made no
tool, manifest, or test edits -- only re-verification with the tools'
own logic.

### Still red (owner lanes, gates working as designed)

* `python3 tools/analyze_g2_completion_readiness.py` still fails at
  `bootloader current interval partition disagrees with its builder`
  (working-tree manifest pins 59013 source / 87981 opaque; the gitignored
  bootloader `build-report.json` is rebuilt from BL-006's uncommitted
  overlay). Re-pin stays BL-006's landing chore.
  `tests.test_analyze_g2_completion_readiness` errors in `setUpClass`
  with the identical message; 0 ran.
* Raw-encoding tool run directly still fails on exactly
  `runtime_spotmgr_shared_literals_42a078.c` (committed pads, file still
  not production-routed; BL owner's call, masked behind the partition
  check in `analyze()`).
* License community census: drift grew 6 -> 7 files, all CD-001's
  untracked MIT stage-1 leaves (the known 6 plus new
  `runtime_gx8002_uart_stage1_idbit.c`; SPDX MIT verified on all 7).
  Followup once CD-001 lands: +7 manifest lines in sorted position,
  tool `298 -> 305` / `1112 -> 1119`, same bumps in the companion test
  pins. `tests.test_analyze_g2_project_license_normalization`: 4 ran,
  1 census error, as expected.

### Re-verified clean (tool's own logic, not hand-rolled sets)

* Touch disk == manifest (10 == 10), EM9305 manifest 21 == expected 21.
* `reviewed_sources.json` needs no action (negative result, verified not
  assumed): 4 functions / 34 bytes, `components/shared/cortex_m55/`
  still exactly the 4 registered files; no transparent-builder reference
  mentions any new untracked Apollo/BL-006/CD-001 file. The fleet's new
  reviewed C routes through component overlays/candidates, not the
  transparent Apollo image.
* `docs/reports/openCFW-completion-2026-08-28/assessment-data.json`
  NOT regenerated: generator runs `readiness.analyze()`, still red (its
  `em9305_source_image_project_mit_files` 19 stays stale until the next
  green snapshot; never hand-edited).
* `docs/transparent-source-ledger.md` NOT regenerated:
  `build/transparent/function-db.json` still 7,449 functions, matching
  the ledger's 7,449 / 1,394,848 bytes. Full rebuild stays XC-004's
  failed pipeline.

### Test evidence this pass

* `tests.test_transparent_reviewed_source` + Touch frontier: 21/21 pass.
* `tests.test_analyze_g2_completion_readiness`: setUpClass error on the
  BL partition disagreement; 0 ran (owner: BL-006).
* `tests.test_analyze_g2_project_license_normalization`: 4 ran, 1 census
  error on the 7 CD-001 files (owner: CD-001).
* Raw-encoding tool direct run: fails only on the known spotmgr file
  (owner: BL).

No hardware operation occurred; hardware qualification remains blocked by
unavailable physical evidence. This item has no flash-range component.

## 2026-09-12 midday pass (XC-002, re-verification only)

HEAD is still `284b98a7`; every tree change remains uncommitted
concurrent work. Nothing newly committed is pinnable, so this pass made
no tool, manifest, or test edits -- only re-verification with the tools'
own logic. One drift count changed; all blockers keep their owners.

### Still red (owner lanes, gates working as designed)

* `python3 tools/analyze_g2_completion_readiness.py` still fails at
  `bootloader current interval partition disagrees with its builder`
  (manifest pins 59013 source / 87981 opaque; the gitignored bootloader
  `build-report.json` is rebuilt from BL-006's uncommitted overlay).
  Re-pin stays BL-006's landing chore.
  `tests.test_analyze_g2_completion_readiness` errors in `setUpClass`
  with the identical message; 0 ran.
* Raw-encoding tool run directly still fails on exactly
  `runtime_spotmgr_shared_literals_42a078.c` (committed pads, file still
  not production-routed; BL owner's call, masked behind the partition
  check in `analyze()`).
* License community census: drift grew 7 -> 8 files, all CD-001's
  untracked MIT stage-1 leaves (the known 7 plus new
  `runtime_gx8002_uart_stage1_xip.c`, the XIP read/write leaf from
  CD-001's 670/8192B tranche progress entry; SPDX MIT verified on all
  8). Followup once CD-001 lands: +8 manifest lines in sorted position,
  tool `298 -> 306` / `1112 -> 1120`, same bumps in the companion test
  pins. `tests.test_analyze_g2_project_license_normalization`: setUpClass
  census error, as expected.

### Re-verified clean (tool's own logic, not hand-rolled sets)

* Touch disk == manifest (10 == 10), Case disk == manifest (8 == 8,
  `build/` exclusion holds), EM9305 disk == manifest (21 == 21).
* `reviewed_sources.json` needs no action (negative result, verified not
  assumed): 4 functions / 34 bytes, `components/shared/cortex_m55/`
  still exactly the 4 registered files; no transparent-builder or Apollo
  overlay reference mentions any new untracked Apollo/BL-006/CD-001
  file. The fleet's new reviewed C routes through component
  overlays/candidates, not the transparent Apollo image.
  `tests.test_transparent_reviewed_source` + Touch frontier: 21/21 pass.
* `docs/reports/openCFW-completion-2026-08-28/assessment-data.json`
  NOT regenerated: generator runs `readiness.analyze()`, still red (its
  `em9305_source_image_project_mit_files` 19 stays stale until the next
  green snapshot; never hand-edited).
* `docs/transparent-source-ledger.md` NOT regenerated:
  `build/transparent/function-db.json` still 7,449 functions /
  1,394,848 code bytes, matching the ledger line. Full rebuild stays
  XC-004's failed pipeline.

No hardware operation occurred; hardware qualification remains blocked by
unavailable physical evidence. This item has no flash-range component.

## 2026-09-12 afternoon pass (XC-002, re-verification only)

HEAD is still `284b98a7`; every tree change remains uncommitted
concurrent work (AM-040 Apollo overlay growth + 4 untracked LVGL/helper
leaves, BL-006 bootloader overlay growth + 16 untracked
`runtime_bl006_*.c` files, CD-001 stage-1 leaves including the newer
pmufill tranche, 5 new untracked GX8002 NOTICE files). Nothing newly
committed is pinnable, so this pass made no tool, manifest, or test
edits -- only re-verification with the tools' own logic. One delta grew
and one drift count grew; all blockers keep their owners.

### Still red (owner lanes, gates working as designed)

* `python3 tools/analyze_g2_completion_readiness.py` still fails at
  `bootloader current interval partition disagrees with its builder`.
  The working-tree manifest still pins this item's earlier 4B re-pin
  (59013 source / 87981 opaque, intact), while the gitignored
  bootloader `build-report.json` (rebuilt 20:12 from BL-006's
  uncommitted overlay) now reads component 60135 / 86859: delta grew
  +544/-544 to +1122/-1122 as BL-006 landed more overlay work. Re-pin
  stays BL-006's landing chore; pinning a moving file set would corrupt
  the committed ledger.
  `tests.test_analyze_g2_completion_readiness` errors in `setUpClass`
  with the identical message; 0 tests ran.
* Raw-encoding tool run directly still fails on exactly
  `runtime_spotmgr_shared_literals_42a078.c` (committed pads, file still
  not production-routed; BL owner's call, masked behind the partition
  check in `analyze()`).
* License community census: drift grew 8 -> 9 files, all CD-001's
  untracked MIT stage-1 leaves (the known 8 plus new
  `runtime_gx8002_uart_stage1_pmufill.c` from CD-001's 850/8192B PMU-fill
  tranche; SPDX MIT verified). Computed with the tool's own manifest
  loader and disk-scan logic (actual 310 vs manifest 301, 0 missing).
  Followup once CD-001 lands: +9 manifest lines in sorted position,
  tool `298 -> 307` / `1112 -> 1121`, same bumps in the companion test
  pins. `tests.test_analyze_g2_project_license_normalization`: 4 ran,
  1 census error, as expected.

### Re-verified clean (tool's own logic, not hand-rolled sets)

* Touch disk == manifest (10 == 10), Case `build/` exclusion holds
  (`CasePackageSourceStaticTests` 2/2 pass), EM9305 disk == manifest
  (21 == 21, exact tool logic including `build`/`__pycache__`/`.pyc`
  exclusions; a naive first diff false-alarmed on one `.pyc` the tool
  correctly excludes).
* `reviewed_sources.json` needs no action (negative result, verified not
  assumed): 4 functions / 34 bytes, `components/shared/cortex_m55/`
  still exactly the 4 registered files; no file under
  `tools/transparent/` or `build/transparent/` references any new
  untracked Apollo/BL-006/CD-001 file. The fleet's new reviewed C
  routes through component overlays/candidates, not the transparent
  Apollo image.
  `tests.test_transparent_reviewed_source` + Touch frontier: 21/21 pass.
* `docs/reports/openCFW-completion-2026-08-28/assessment-data.json`
  NOT regenerated: generator runs `readiness.analyze()`, still red (its
  `em9305_source_image_project_mit_files` 19 stays stale until the next
  green snapshot; never hand-edited).
* `docs/transparent-source-ledger.md` NOT regenerated:
  `build/transparent/function-db.json` still 7,449 functions against
  the same stock image
  (`ota_s200_firmware_ota.bin`, sha256 `36c5b0e4...a27863`),
  matching the ledger's 7,449 / 1,394,848 bytes. Full rebuild stays
  XC-004's failed pipeline.

No hardware operation occurred; hardware qualification remains blocked by
unavailable physical evidence. This item has no flash-range component.

## 2026-09-12 evening pass (XC-002, re-verification only)

HEAD is still `284b98a7`; every tree change remains uncommitted
concurrent work. Nothing newly committed is pinnable, so this pass made
no tool, manifest, or test edits -- only re-verification with the tools'
own logic. One delta grew and one drift count grew; all blockers keep
their owners. A standing review note: this pass was asked whether the
two red censuses should simply be "fixed" by re-pinning to the live
tree. The answer remains no -- both drifts are other workstreams'
uncommitted in-flight work (BL-006 overlay edits, CD-001 stage-1
leaves), and pinning a moving file set would corrupt the committed
ledger this item just re-pinned. Re-pin stays each owner's landing
chore; this item reports `partial` with exact followup numbers.

### Still red (owner lanes, gates working as designed)

* `python3 tools/analyze_g2_completion_readiness.py` still fails at
  `bootloader current interval partition disagrees with its builder`.
  The working-tree manifest still pins this item's earlier 4B re-pin
  (59013 source / 87981 opaque, intact), while the gitignored
  bootloader `build-report.json` now reads component 60221 / 86773:
  delta grew +1122/-1122 to +1208/-1208 as BL-006 landed more overlay
  work (matches BL-006's own 1208/5892 progress claim). Re-pin stays
  BL-006's landing chore.
  `tests.test_analyze_g2_completion_readiness` errors in `setUpClass`
  with the identical message; 0 tests ran.
* Raw-encoding tool run directly still fails on exactly
  `components/bootloader/core_overlay/runtime_spotmgr_shared_literals_42a078.c`
  (committed pads, file still not production-routed; BL owner's call,
  masked behind the partition check in `analyze()`).
* License community census: drift grew 9 -> 10 files, all CD-001's
  untracked MIT stage-1 leaves (the known 9 plus new
  `runtime_gx8002_uart_stage1_vectors.S` from CD-001's vectors-table
  tranche; SPDX MIT verified on the new file). Computed with the
  tool's own manifest loader and disk-scan logic (manifest 298,
  actual 311, 0 missing). Followup once CD-001 lands: +10 manifest
  lines in sorted position, tool `298 -> 308` / `1112 -> 1122`, same
  bumps in the companion test pins.
  `tests.test_analyze_g2_project_license_normalization`: 4 ran,
  1 census error, as expected.

### Re-verified clean (tool's own logic, not hand-rolled sets)

* Touch disk == manifest (delta 0), Case disk == manifest (delta 0,
  `build/` exclusion holds, `CasePackageSourceStaticTests` 2/2 pass),
  EM9305 disk == manifest (delta 0, exact tool logic including
  `build`/`__pycache__`/`.pyc` exclusions).
* `reviewed_sources.json` needs no action (negative result, verified
  not assumed): 4 functions / 34 bytes, `components/shared/cortex_m55/`
  still exactly the 4 registered files; no file under
  `tools/transparent/` or `build/transparent/` references any new
  untracked Apollo/BL-006/CD-001 file. New untracked Apollo leaves
  (`runtime_string_helpers.c`, `runtime_peripheral_state_helpers.c`)
  are referenced only by the working-tree Apollo overlay (AM-040's
  uncommitted growth), never by the transparent builder, so no
  transparent registration is due. `tests.test_transparent_reviewed_source`
  + Touch frontier: 21/21 pass.
* `docs/reports/openCFW-completion-2026-08-28/assessment-data.json`
  NOT regenerated: the generator runs `readiness.analyze()`, still red
  (its `em9305_source_image_project_mit_files` 19 stays stale until the
  next green snapshot; never hand-edited).
* `docs/transparent-source-ledger.md` NOT regenerated:
  `build/transparent/` still holds only
  `function-db.json`/`region-map.json`/`DB-SUMMARY.json` (no
  `source|image` stages; full rebuild stays XC-004's failed
  pipeline). Ledger inputs verified identical to the committed
  rendering: DB-SUMMARY 7,449 functions / 1,394,848 code bytes.

### Test evidence this pass

* `tests.test_transparent_reviewed_source` + Touch frontier: 21/21 pass.
* `CasePackageSourceStaticTests`: 2/2 pass.
* `tests.test_analyze_g2_completion_readiness`: setUpClass error on the
  BL partition disagreement (+1208/-1208); 0 ran (owner: BL-006).
* `tests.test_analyze_g2_project_license_normalization`: 4 ran, 1 census
  error on the 10 CD-001 files (owner: CD-001).
* Raw-encoding tool direct run: fails only on the known spotmgr file
  (owner: BL).

No hardware operation occurred; hardware qualification remains blocked by
unavailable physical evidence. This item has no flash-range component.

## 2026-09-12 late pass (XC-002, re-verification only, fleet run 20260911-211301)

HEAD is still `284b98a7`; this pass runs minutes after the evening
pass, so the tree is unchanged in every pinnable dimension. No tool,
manifest, or test edits were made -- only re-verification with the
tools' own logic. One delta grew by a small step; everything else is
byte-identical in signature. All blockers keep their owners.

### Still red (owner lanes, gates working as designed)

* `python3 tools/analyze_g2_completion_readiness.py` still fails at
  `bootloader current interval partition disagrees with its builder`.
  The working-tree manifest still pins this item's earlier 4B re-pin
  (59013 source / 87981 opaque, intact), while the gitignored
  bootloader `build-report.json` (rebuilt 21:04 from BL-006's
  uncommitted overlay) now reads component 60255 / 86739: delta grew
  +1208/-1208 to +1242/-1242 as BL-006 landed more overlay work
  (+34 source this step). Re-pin stays BL-006's landing chore;
  pinning a moving file set would corrupt the committed ledger.
  `tests.test_analyze_g2_completion_readiness` errors in `setUpClass`
  with the identical message; 0 tests ran.
* Raw-encoding tool run directly still fails on exactly
  `components/bootloader/core_overlay/runtime_spotmgr_shared_literals_42a078.c`
  (committed pads, file still not production-routed; BL owner's call,
  masked behind the partition check in `analyze()`).
* License community census: drift holds at exactly the same 10
  CD-001 untracked MIT stage-1 leaves (reset.S, divmod.c, idbit.c,
  pmubits.c, pmufill.c, pmusbit.S, putsync.S, serial.c, vectors.S,
  xip.c -- MIT SPDX verified on all 10, 0 missing from the working
  manifest). Computed with the tool's own manifest loader and
  disk-scan logic (manifest 298, disk 311). Followup once CD-001
  lands: +10 manifest lines in sorted position, tool `298 -> 308` /
  `1112 -> 1122`, same bumps in the companion test pins.
  `tests.test_analyze_g2_project_license_normalization`: 4 ran,
  1 census error, as expected.
* Working-tree note: the tree still carries this item's own earlier
  uncommitted re-pins (community +13 lines 285 -> 298, EM9305 +2,
  Touch receipt refresh, and the matching tool/test constant bumps).
  They were left intact for human commit review -- this pass neither
  reverted nor re-pinned them.

### Re-verified clean (tool's own logic, not hand-rolled sets)

* Touch disk == manifest (10 == 10, exact tool logic), Case
  disk == manifest (8 == 8, `build/` exclusion holds), EM9305
  disk == manifest (21 == 21, exact tool logic with
  `build`/`__pycache__`/`.pyc` exclusions).
* `reviewed_sources.json` needs no action (negative result, verified
  not assumed): 4 functions / 34 bytes, `components/shared/cortex_m55/`
  still exactly the 4 registered files with no diff, and no file under
  `tools/transparent/` or `build/transparent/` references any new
  untracked Apollo/BL-006/CD-001 file. The fleet's new reviewed C
  routes through component overlays/candidates, not the transparent
  Apollo image, so no transparent registration is due.
  `tests.test_transparent_reviewed_source` + Touch frontier: 21/21 pass.
* `docs/reports/openCFW-completion-2026-08-28/assessment-data.json`
  NOT regenerated: the generator runs `readiness.analyze()`, still red
  (its `project_license_policy/em9305_source_image_project_mit_files`
  19 stays stale until the next green snapshot; never hand-edited).
* `docs/transparent-source-ledger.md` NOT regenerated:
  `build/transparent/function-db.json` still 7,449 entries, matching
  the ledger's 7,449 / 1,394,848 bytes. Full rebuild stays XC-004's
  failed pipeline.

### Test evidence this pass

* `tests.test_transparent_reviewed_source` + Touch frontier: 21/21 pass.
* `tests.test_analyze_g2_completion_readiness`: setUpClass error on the
  BL partition disagreement (+1242/-1242); 0 ran (owner: BL-006).
* `tests.test_analyze_g2_project_license_normalization`: 4 ran, 1 census
  error on the same 10 CD-001 files (owner: CD-001).
* Raw-encoding tool direct run: fails only on the known spotmgr file
  (owner: BL).

No hardware operation occurred; hardware qualification remains blocked by
unavailable physical evidence. This item has no flash-range component.

## 2026-09-12 night pass (XC-002, re-verification only)

HEAD is still `284b98a7`; every tree change remains uncommitted
concurrent work. Nothing newly committed is pinnable, so this pass made
no tool, manifest, or test edits -- only re-verification with the tools'
own logic. One delta grew and one drift count grew; all blockers keep
their owners.

### Still red (owner lanes, gates working as designed)

* `python3 tools/analyze_g2_completion_readiness.py` still fails at
  `bootloader current interval partition disagrees with its builder`.
  The working-tree manifest still pins this item's earlier 4B re-pin
  (59013 source / 87981 opaque, intact), while the gitignored
  bootloader `build-report.json` (mtime Sep 11 21:52, rebuilt from
  BL-006's uncommitted overlay) now reads component 60339 / 86655:
  delta grew +1242/-1242 to +1326/-1326 as BL-006 landed more overlay
  work (+84 source this step, matching BL-006's own 84B progress
  claim). Re-pin stays BL-006's landing chore; pinning a moving file
  set would corrupt the committed ledger.
  `tests.test_analyze_g2_completion_readiness` errors in `setUpClass`
  with the identical message; 0 tests ran.
* Raw-encoding tool run directly still fails on exactly
  `components/bootloader/core_overlay/runtime_spotmgr_shared_literals_42a078.c`
  (committed pads, file still not production-routed; BL owner's call,
  masked behind the partition check in `analyze()`).
* License community census: drift grew 10 -> 12 files, all CD-001's
  untracked MIT stage-1 leaves (the known 10 plus new
  `runtime_gx8002_uart_stage1_mdelay.c` and
  `runtime_gx8002_uart_stage1_pmudispatch.c`; SPDX MIT verified on
  both new files via grep). Computed with the tool's own manifest
  loader and disk-scan logic (manifest 298, actual 313 incl. adapters,
  12 extra, 0 missing). Followup once CD-001 lands: +12 manifest
  lines in sorted position, tool `298 -> 310` / `1112 -> 1124`, same
  bumps in the companion test pins.
  `tests.test_analyze_g2_project_license_normalization`: 4 ran,
  1 census error, as expected (`CasePackageSourceStaticTests` 2/2
  pass).

### Re-verified clean (tool's own logic, not hand-rolled sets)

* `reviewed_sources.json` needs no action (negative result, verified
  not assumed): 4 functions / 34 bytes, `components/shared/cortex_m55/`
  still exactly the 4 registered files. The fleet's new reviewed C
  routes through component overlays/candidates, not the transparent
  Apollo image, so no transparent registration is due.
  `tests.test_transparent_reviewed_source` + Touch frontier: 21/21
  pass.
* `docs/reports/openCFW-completion-2026-08-28/assessment-data.json`
  NOT regenerated: the generator runs `readiness.analyze()`, still red
  (never hand-edited).
* `docs/transparent-source-ledger.md` NOT regenerated:
  `build/transparent/DB-SUMMARY.json` still 7,449 functions /
  1,394,848 code bytes, matching the ledger line. Full rebuild stays
  XC-004's failed pipeline.

No hardware operation occurred; hardware qualification remains blocked by
unavailable physical evidence. This item has no flash-range component.

## 2026-09-12 late pass (XC-002, re-verification only)

HEAD is still `284b98a7`; every tree change remains uncommitted
concurrent work (AM-040 Apollo overlay growth, BL-006 bootloader overlay
growth, CD-001 stage-1 leaves including the newer mdelay/pmudispatch
tranche plus 8 new untracked GX8002 NOTICE files). Nothing newly
committed is pinnable, so this pass made no tool, manifest, or test
edits -- only re-verification with the tools' own logic. BL delta and
license drift both hold; all blockers keep their owners.

### Still red (owner lanes, gates working as designed)

* `python3 tools/analyze_g2_completion_readiness.py` still fails at
  `bootloader current interval partition disagrees with its builder`.
  The working-tree manifest still pins this item's earlier 4B re-pin
  (59013 source / 87981 opaque, intact -- the diff against HEAD shows
  only that re-pin plus its provider-hash update), while the gitignored
  bootloader `build-report.json` reads component 60339 / 86655:
  delta holds at +1326/-1326. Re-pin stays BL-006's landing chore;
  pinning a moving file set would corrupt the committed ledger.
  `tests.test_analyze_g2_completion_readiness` errors in `setUpClass`
  with the identical message; 0 tests ran.
* Raw-encoding tool run directly still fails on exactly
  `components/bootloader/core_overlay/runtime_spotmgr_shared_literals_42a078.c`
  (committed pads, file still not production-routed; BL owner's call,
  masked behind the partition check in `analyze()`).
* License community census: drift holds at 12 files, all CD-001's
  untracked stage-1 leaves (the known 10 plus newer
  `runtime_gx8002_uart_stage1_mdelay.c` and
  `runtime_gx8002_uart_stage1_pmudispatch.c`; SPDX MIT verified on
  both new files). Computed with the tool's own manifest loader and
  disk-scan logic (manifest 298, actual 313, 0 missing). Followup once
  CD-001 lands: +12 manifest lines in sorted position, tool
  `298 -> 310` / `1112 -> 1124`, same bumps in the companion test
  pins. `tests.test_analyze_g2_project_license_normalization`: 4 ran,
  1 census error, as expected.

### Re-verified clean (tool's own logic, not hand-rolled sets)

* Touch disk == manifest (10 == 10, exact tool logic including
  support paths), Case disk == manifest (8 == 8, `build/` exclusion
  holds), EM9305 disk == manifest (21 == 21, exact tool logic
  including `build`/`__pycache__`/`.pyc` exclusions).
* `reviewed_sources.json` needs no action (negative result, verified
  not assumed): 4 functions, `components/shared/cortex_m55/` still
  exactly the 4 registered files; `build/transparent/function-db.json`
  still 7,449 functions, matching the committed ledger. The fleet's
  new reviewed C routes through component overlays/candidates, not
  the transparent Apollo image, so no transparent registration is due.
  `tests.test_transparent_reviewed_source` + Touch frontier: 21/21
  pass.
* `docs/reports/openCFW-completion-2026-08-28/assessment-data.json`
  NOT regenerated: the generator runs `readiness.analyze()`, still
  red (never hand-edited).
* `docs/transparent-source-ledger.md` NOT regenerated: no
  `source|image` stages exist (full rebuild stays XC-004's failed
  pipeline); ledger inputs verified identical to the committed
  rendering.

No hardware operation occurred; hardware qualification remains blocked by
unavailable physical evidence. This item has no flash-range component.

## 2026-09-12 railc pass (XC-002, re-verification only)

HEAD is still `284b98a7`; every tree change remains uncommitted
concurrent work. Nothing newly committed is pinnable, so this pass made
no tool, manifest, or test edits -- only re-verification with the tools'
own logic. License drift grew by one file; the BL delta holds;
all blockers keep their owners.

### Still red (owner lanes, gates working as designed)

* `python3 tools/analyze_g2_completion_readiness.py` still fails at
  `bootloader current interval partition disagrees with its builder`.
  The working-tree manifest still pins this item's earlier 4B re-pin
  (59013 source / 87981 opaque, intact), while the gitignored
  bootloader `build-report.json` (mtime Sep 11 21:52, unchanged since
  the last pass) still reads component 60339 / 86655: delta holds at
  +1326/-1326. Re-pin stays BL-006's landing chore; pinning a moving
  file set would corrupt the committed ledger.
  `tests.test_analyze_g2_completion_readiness` errors in `setUpClass`
  with the identical message; 0 tests ran.
* Raw-encoding tool run directly still fails on exactly
  `components/bootloader/core_overlay/runtime_spotmgr_shared_literals_42a078.c`
  (committed pads, file still not production-routed; BL owner's call,
  masked behind the partition check in `analyze()`).
* License community census: drift grew 12 -> 13 files, all CD-001's
  untracked MIT stage-1 leaves (the known 12 plus new
  `runtime_gx8002_uart_stage1_railc.c`, the 266-byte rail-op leaf from
  CD-001's own 1,492/8,192B progress entry; `SPDX-License-Identifier:
  MIT` verified, file still untracked). Computed with the tool's own
  manifest loader and disk-scan logic (manifest 298, actual 314 incl.
  adapters, 13 extra, 0 missing). Followup once CD-001 lands: +13
  manifest lines in sorted position, tool `298 -> 311` /
  `1112 -> 1125`, same bumps in the companion test pins.
  `tests.test_analyze_g2_project_license_normalization`: 4 ran,
  1 census error, as expected (`CasePackageSourceStaticTests` 2/2
  pass).

### Re-verified clean (tool's own logic, not hand-rolled sets)

* Touch disk == manifest (10 == 10), Case disk == manifest (8 == 8,
  `build/` exclusion holds), EM9305 disk == manifest (21 == 21, exact
  tool logic including `build`/`__pycache__`/`.pyc` exclusions; an
  initial probe that omitted the support-path unions false-alarmed on
  Case and was corrected against the tool's exact comparison before
  trusting any count).
* `reviewed_sources.json` needs no action (negative result, verified
  not assumed): 4 functions, `components/shared/cortex_m55/` still
  exactly the 4 registered files; no file under `tools/transparent/`
  or `build/transparent/` references `railc` or any other new
  untracked leaf. The fleet's new reviewed C (including CD-001's rail
  op) routes through component overlays/candidates, not the
  transparent Apollo image, so no transparent registration is due.
  `tests.test_transparent_reviewed_source` + Touch frontier: 21/21
  pass.
* `docs/reports/openCFW-completion-2026-08-28/assessment-data.json`
  NOT regenerated: the generator runs `readiness.analyze()`, still red
  (never hand-edited).
* `docs/transparent-source-ledger.md` NOT regenerated:
  `build/transparent/DB-SUMMARY.json` still 7,449 functions /
  1,394,848 code bytes, matching the ledger line. Full rebuild stays
  XC-004's failed pipeline.

No hardware operation occurred; hardware qualification remains blocked by
unavailable physical evidence. This item has no flash-range component.

## 2026-09-12 railb pass (XC-002, re-verification only)

HEAD is still `284b98a7`; every tree change remains uncommitted
concurrent work. Nothing newly committed is pinnable, so this pass made
no tool, manifest, or test edits -- only re-verification with the tools'
own logic. The BL delta grew and the license drift grew by one file;
all blockers keep their owners.

### Still red (owner lanes, gates working as designed)

* `python3 tools/analyze_g2_completion_readiness.py` still fails at
  `bootloader current interval partition disagrees with its builder`.
  The working-tree manifest still pins this item's earlier 4B re-pin
  (provider `source_owned_bytes` 59013 / `opaque_base_bytes` 87981,
  intact), while the gitignored bootloader `build-report.json`
  (rebuilt from BL-006's uncommitted overlay) now reads component
  60515 / 86479: delta grew +1326/-1326 to +1502/-1502 (+176 source
  this step, matching BL-006's own 1,502B progress claim). Re-pin
  stays BL-006's landing chore; pinning a moving file set would
  corrupt the committed ledger.
  `tests.test_analyze_g2_completion_readiness` errors in `setUpClass`
  with the identical message; 0 tests ran.
* Raw-encoding tool run directly still fails on exactly
  `components/bootloader/core_overlay/runtime_spotmgr_shared_literals_42a078.c`
  (committed pads, file still not production-routed; BL owner's call,
  masked behind the partition check in `analyze()`).
* License community census: drift grew 13 -> 14 files, all CD-001's
  untracked MIT stage-1 leaves (the known 13 plus new
  `runtime_gx8002_uart_stage1_railb.S`, the 350-byte rail-B leaf from
  CD-001's own 1,842/8,192B progress entry; `SPDX-License-Identifier:
  MIT` verified, file still untracked). Computed with the tool's own
  manifest loader and disk-scan logic (manifest 298, actual 315 incl.
  adapters, 14 extra, 0 missing). Followup once CD-001 lands: +14
  manifest lines in sorted position, tool `298 -> 312` /
  `1112 -> 1126`, same bumps in the companion test pins.
  `tests.test_analyze_g2_project_license_normalization`: 4 ran,
  1 census error, as expected.

### Re-verified clean (tool's own logic, not hand-rolled sets)

* Touch disk == manifest (10 == 10), Case disk == manifest (8 == 8,
  `build/` exclusion holds), EM9305 disk == manifest (21 == 21, exact
  tool logic with nested per-root `build`/`__pycache__`/`.pyc`
  exclusions; a first probe that collapsed the comprehension's
  `relative_to` onto the last root false-alarmed 12/13 and was
  corrected against the tool's exact nested loop before trusting any
  count).
* `reviewed_sources.json` needs no action (negative result, verified
  not assumed): 4 functions / 34 bytes, `components/shared/cortex_m55/`
  still exactly the 4 registered files; no file under
  `tools/transparent/` or `build/transparent/` references `railb` or
  any other new untracked leaf. The fleet's new reviewed C (including
  CD-001's rail-B op and BL-006's pools) routes through component
  overlays/candidates, not the transparent Apollo image, so no
  transparent registration is due.
  `tests.test_transparent_reviewed_source` + Touch frontier: 21/21
  pass.
* `docs/reports/openCFW-completion-2026-08-28/assessment-data.json`
  NOT regenerated: the generator runs `readiness.analyze()`, still red
  (never hand-edited).
* `docs/transparent-source-ledger.md` NOT regenerated:
  `build/transparent/DB-SUMMARY.json` still 7,449 functions /
  1,394,848 code bytes, matching the ledger line. Full rebuild stays
  XC-004's failed pipeline.

### Test evidence this pass

* `tests.test_transparent_reviewed_source` + Touch frontier: 21/21 pass.
* `tests.test_analyze_g2_completion_readiness`: setUpClass error on the
  BL partition disagreement (+1502/-1502); 0 ran (owner: BL-006).
* `tests.test_analyze_g2_project_license_normalization`: 4 ran, 1 census
  error on the 14 CD-001 files (owner: CD-001).
* Raw-encoding tool direct run: fails only on the known spotmgr file
  (owner: BL).

No hardware operation occurred; hardware qualification remains blocked by
unavailable physical evidence. This item has no flash-range component.

## 2026-09-12 raila pass (XC-002, re-verification only)

HEAD is still `284b98a7`; every tree change remains uncommitted
concurrent work (AM-040 Apollo overlay growth, BL-006 bootloader overlay
growth, CD-001 stage-1 leaves including the newer raila tranche now at
2,306/8,192B with its own audit). Nothing newly committed is pinnable,
so this pass made no tool, manifest, or test edits -- only
re-verification with the tools' own logic. The BL delta grew and the
license drift grew by one file; all blockers keep their owners.

### Still red (owner lanes, gates working as designed)

* `python3 tools/analyze_g2_completion_readiness.py` still fails at
  `bootloader current interval partition disagrees with its builder`.
  The working-tree manifest still pins this item's earlier 4B re-pin
  (provider `source_owned_bytes` 59013 / `opaque_base_bytes` 87981,
  intact), while the gitignored bootloader `build-report.json`
  (mtime Sep 11 23:13, rebuilt from BL-006's uncommitted overlay) now
  reads component 60585 / 86409: delta grew +1502/-1502 to
  +1572/-1572 (+70 source this step). Re-pin stays BL-006's landing
  chore; pinning a moving file set would corrupt the committed ledger.
  `tests.test_analyze_g2_completion_readiness` errors in `setUpClass`
  with the identical message; 0 tests ran.
* Raw-encoding tool run directly still fails on exactly
  `components/bootloader/core_overlay/runtime_spotmgr_shared_literals_42a078.c`
  (committed pads, file still not production-routed; BL owner's call,
  masked behind the partition check in `analyze()`).
* License community census: drift grew 14 -> 15 files, all CD-001's
  untracked MIT stage-1 leaves (the known 14 plus new
  `runtime_gx8002_uart_stage1_raila.S`; `SPDX-License-Identifier: MIT`
  verified, file still untracked). Computed with the tool's own
  manifest loader and disk-scan logic (manifest 298, actual 316 incl.
  adapters, 15 extra, 0 missing). Followup once CD-001 lands: +15
  manifest lines in sorted position, tool `298 -> 313` /
  `1112 -> 1127`, same bumps in the companion test pins.
  `tests.test_analyze_g2_project_license_normalization`: 4 ran,
  1 census error, as expected.

### Re-verified clean (tool's own logic, not hand-rolled sets)

* Touch disk == manifest (10 == 10), Case disk == manifest (8 == 8,
  `build/` exclusion holds), EM9305 disk == manifest (21 == 21, exact
  tool logic with nested per-root `build`/`__pycache__`/`.pyc`
  exclusions; a first probe that omitted the support-path unions
  false-alarmed on Case and was corrected against the tool's exact
  nested comparison before trusting any count).
* `reviewed_sources.json` needs no action (negative result, verified
  not assumed): 4 functions / 34 bytes, untouched since `d794c28e`;
  `components/shared/cortex_m55/` still exactly the 4 registered
  files; no file under `tools/transparent/` or `build/transparent/`
  references `raila` or any other new untracked leaf. The fleet's new
  reviewed C (including CD-001's raila op and BL-006's pools) routes
  through component overlays/candidates, not the transparent Apollo
  image, so no transparent registration is due.
  `tests.test_transparent_reviewed_source` + Touch frontier: 21/21
  pass.
* `docs/reports/openCFW-completion-2026-08-28/assessment-data.json`
  NOT regenerated: the generator runs `readiness.analyze()`, still red
  (never hand-edited).
* `docs/transparent-source-ledger.md` NOT regenerated:
  `build/transparent/DB-SUMMARY.json` still 7,449 functions /
  1,394,848 code bytes, matching the ledger line. Full rebuild stays
  XC-004's failed pipeline.

### Test evidence this pass

* `tests.test_transparent_reviewed_source` + Touch frontier: 21/21 pass.
* `CasePackageSourceStaticTests`: 2/2 pass.
* `tests.test_analyze_g2_completion_readiness`: setUpClass error on the
  BL partition disagreement (+1572/-1572); 0 ran (owner: BL-006).
* `tests.test_analyze_g2_project_license_normalization`: 4 ran, 1 census
  error on the 15 CD-001 files (owner: CD-001).
* Raw-encoding tool direct run: fails only on the known spotmgr file
  (owner: BL).

No hardware operation occurred; hardware qualification remains blocked by
unavailable physical evidence. This item has no flash-range component.

## 2026-09-12 pmudisp pass (XC-002, re-verification only)

HEAD is still `284b98a7`; every tree change remains uncommitted
concurrent work (AM-040 Apollo overlay growth, BL-006 bootloader overlay
growth, CD-001 stage-1 leaves now including the pmudispatch tranche at
2,570/8,192B with its own audit). Nothing newly committed is pinnable,
so this pass made no tool, manifest, or test edits -- only
re-verification with the tools' own logic. The BL delta grew and the
license drift holds; all blockers keep their owners.

### Still red (owner lanes, gates working as designed)

* `python3 tools/analyze_g2_completion_readiness.py` still fails at
  `bootloader current interval partition disagrees with its builder`.
  The working-tree manifest still pins this item's earlier 4B re-pin
  (provider `source_owned_bytes` 59013 / `opaque_base_bytes` 87981,
  intact), while the gitignored bootloader `build-report.json`
  (mtime Sep 11 23:56, rebuilt from BL-006's uncommitted overlay) now
  reads component 60655 / 86339: delta grew +1572/-1572 to
  +1642/-1642 (+70 source this step). Re-pin stays BL-006's landing
  chore; pinning a moving file set would corrupt the committed ledger.
  `tests.test_analyze_g2_completion_readiness` errors in `setUpClass`
  with the identical message; 0 tests ran.
* Raw-encoding tool run directly still fails on exactly
  `components/bootloader/core_overlay/runtime_spotmgr_shared_literals_42a078.c`
  (committed pads, file still not production-routed; BL owner's call,
  masked behind the partition check in `analyze()`).
* License community census: drift holds at 15 files, all CD-001's
  untracked MIT stage-1 leaves (reset.S, divmod.c, idbit.c, mdelay.c,
  pmubits.c, pmudispatch.S, pmufill.c, pmusbit.S, putsync.S, raila.S,
  railb.S, railc.c, serial.c, vectors.S, xip.c; `SPDX-License-Identifier:
  MIT` verified present in every one via grep, zero files reported
  without it). Computed with the tool's own manifest loader and
  disk-scan logic (manifest 298, disk 316 incl. adapters, 15 extra,
  0 missing). Followup once CD-001 lands: +15 manifest lines in sorted
  position, tool `298 -> 313` / `1112 -> 1127`, same bumps in the
  companion test pins.
  `tests.test_analyze_g2_project_license_normalization`: 4 ran,
  1 census error (`community controller/build-adapter source census
  changed`), as expected.

### Re-verified clean (tool's own logic, not hand-rolled sets)

* Touch/Case/EM9305 component trees carry no new status changes, and
  this item's own earlier uncommitted re-pins (community +13, EM9305
  +2, Touch receipt refresh, matching tool/test bumps) remain intact
  for human commit review -- neither reverted nor re-pinned.
* `reviewed_sources.json` needs no action (negative result, verified
  not assumed): 4 functions / 34 bytes, untouched; `components/shared/
  cortex_m55/` still exactly the 4 registered files; no file under
  `tools/transparent/` or `build/transparent/` references `pmudispatch`
  or any other new untracked leaf. The fleet's new reviewed C routes
  through component overlays/candidates, not the transparent Apollo
  image, so no transparent registration is due.
  `tests.test_transparent_reviewed_source` + Touch frontier: 21/21
  pass.
* `docs/reports/openCFW-completion-2026-08-28/assessment-data.json`
  NOT regenerated: the generator runs `readiness.analyze()`, still red
  (never hand-edited).
* `docs/transparent-source-ledger.md` NOT regenerated:
  `build/transparent/DB-SUMMARY.json` still 7,449 functions /
  1,394,848 code bytes, matching the ledger line. Full rebuild stays
  XC-004's failed pipeline.

### Test evidence this pass

* `tests.test_transparent_reviewed_source` + Touch frontier: 21/21 pass.
* `tests.test_analyze_g2_completion_readiness`: setUpClass error on the
  BL partition disagreement (+1642/-1642); 0 ran (owner: BL-006).
* `tests.test_analyze_g2_project_license_normalization`: 4 ran, 1 census
  error on the 15 CD-001 files (owner: CD-001).
* Raw-encoding tool direct run: fails only on the known spotmgr file
  (owner: BL).

No hardware operation occurred; hardware qualification remains blocked by
unavailable physical evidence. This item has no flash-range component.

## 2026-09-12 postamble pass (XC-002, re-verification only)

HEAD is still `284b98a7`; every tree change remains uncommitted
concurrent work (AM-040 Apollo overlay growth, BL-006 bootloader overlay
growth, CD-001 stage-1 leaves now at 2,630/8,192B with the newly closed
rail-postamble leaf). Nothing newly committed is pinnable, so this pass
made no tool, manifest, or test edits -- only re-verification with the
tools' own logic. The BL delta holds and the license drift grew by one
file; all blockers keep their owners.

### Still red (owner lanes, gates working as designed)

* `python3 tools/analyze_g2_completion_readiness.py` still fails at
  `bootloader current interval partition disagrees with its builder`.
  The working-tree manifest still pins this item's earlier 4B re-pin
  (provider `source_owned_bytes` 59013 / `opaque_base_bytes` 87981,
  intact), while the gitignored bootloader `build-report.json`
  (mtime Sep 11 23:56, unchanged since the last pass) still reads
  component 60655 / 86339: delta holds at +1642/-1642. Re-pin stays
  BL-006's landing chore; pinning a moving file set would corrupt the
  committed ledger.
  `tests.test_analyze_g2_completion_readiness` errors in `setUpClass`
  with the identical message; 0 tests ran.
* Raw-encoding tool run directly still fails on exactly
  `components/bootloader/core_overlay/runtime_spotmgr_shared_literals_42a078.c`
  (committed pads, file still not production-routed; BL owner's call,
  masked behind the partition check in `analyze()`).
* License community census: drift grew 15 -> 16 files, all CD-001's
  untracked MIT stage-1 leaves (the known 15 plus new
  `runtime_gx8002_uart_stage1_postamble.S`, the 60-byte rail-postamble
  leaf from CD-001's own 2,630/8,192B progress entry;
  `SPDX-License-Identifier: MIT` verified, file still untracked).
  Computed with the tool's own manifest loader and disk-scan logic
  (manifest 298, disk 317 incl. adapters, 16 extra, 0 missing).
  Followup once CD-001 lands: +16 manifest lines in sorted position,
  tool `298 -> 314` / `1112 -> 1128`, same bumps in the companion
  test pins. `tests.test_analyze_g2_project_license_normalization`:
  4 ran, 1 census error, as expected.

### Re-verified clean (tool's own logic, not hand-rolled sets)

* Touch disk == manifest (10 == 10), Case disk == manifest (8 == 8,
  `build/` exclusion holds), EM9305 disk == manifest (21 == 21, exact
  tool logic with nested per-root `build`/`__pycache__`/`.pyc`
  exclusions).
* `reviewed_sources.json` needs no action (negative result, verified
  not assumed): 4 functions, untouched since `d794c28e`;
  `components/shared/cortex_m55/` still exactly the 4 registered
  files; grep over `tools/transparent/` and `build/transparent/`
  finds no reference to `postamble`, `pmudispatch`, `raila`,
  `railb`, or `railc`. The fleet's new reviewed C (including CD-001's
  postamble leaf and BL-006's pools) routes through component
  overlays/candidates, not the transparent Apollo image, so no
  transparent registration is due.
  `tests.test_transparent_reviewed_source` + Touch frontier: 21/21
  pass.
* `docs/reports/openCFW-completion-2026-08-28/assessment-data.json`
  NOT regenerated: the generator runs `readiness.analyze()`, still red
  (never hand-edited).
* `docs/transparent-source-ledger.md` NOT regenerated:
  `build/transparent/` still holds only
  `function-db.json`/`region-map.json`/`DB-SUMMARY.json` (DB-SUMMARY
  7,449 functions / 1,394,848 code bytes, matching the ledger line;
  no `source|image` stages; full rebuild stays XC-004's failed
  pipeline).

### Test evidence this pass

* `tests.test_transparent_reviewed_source` + Touch frontier: 21/21 pass.
* `tests.test_analyze_g2_completion_readiness`: setUpClass error on the
  BL partition disagreement (+1642/-1642); 0 ran (owner: BL-006).
* `tests.test_analyze_g2_project_license_normalization`: 4 ran, 1 census
  error on the 16 CD-001 files (owner: CD-001).
* Raw-encoding tool direct run: fails only on the known spotmgr file
  (owner: BL).

No hardware operation occurred; hardware qualification remains blocked by
unavailable physical evidence. This item has no flash-range component.

## XC-002 pass 2026-09-12 (~02:00): HEAD unchanged, no re-pin due

* HEAD still `284b98a7`; committed ledgers untouched. Working-tree
  movement is all uncommitted owner-lane work, so re-pinning stays
  deferred (pinning a moving file set would corrupt the ledger).
* Readiness still red at the first gate, as required:
  `bootloader current interval partition disagrees with its builder`
  (tool direct run + `tests.test_analyze_g2_completion_readiness`
  setUpClass error, 0 ran; owner: BL-006). Partition recomputed with
  the tool's own `_region_partition` logic: official_blob +4576 /
  source_compiled -4576 (was +1642/-1642). The gitignored
  `components/bootloader/core_overlay/build/build-report.json` was
  rebuilt 01:42 from uncommitted BL overlay work while the
  core-source manifest (modified, uncommitted) was not regenerated
  to match; re-pin remains BL-006's landing chore.
* Raw-encoding tool run directly still fails on exactly
  `components/bootloader/core_overlay/runtime_spotmgr_shared_literals_42a078.c`
  (committed pads, file still not production-routed; BL owner's call).
* License community census: drift grew 16 -> 17 files, all CD-001's
  untracked MIT stage-1 leaves (the known 16 plus new
  `runtime_gx8002_uart_stage1_xip.c`;
  `SPDX-License-Identifier: MIT` verified, file still untracked).
  Computed with the tool's own manifest loader and disk-scan logic
  (manifest 298, disk 318, 17 extra, 0 missing).
  Followup once CD-001 lands: +17 manifest lines in sorted position,
  tool `298 -> 315` / companion test pins. `tests.test_analyze_g2_project_license_normalization`:
  4 ran, 1 census error, as expected.

### Re-verified clean (tool's own logic, not hand-rolled sets)

* Touch disk == manifest (10 == 10), Case disk == manifest (8 == 8),
  EM9305 disk == manifest (21 == 21, exact tool logic with nested
  per-root `build`/`__pycache__`/`.pyc` exclusions).
* `reviewed_sources.json` needs no action (negative result, verified
  not assumed): 4 functions, untouched since `d794c28e`;
  `components/shared/cortex_m55/` still exactly the 4 registered
  files; grep over `tools/transparent/` and `build/transparent/`
  finds no reference to `postamble`, `pmudispatch`, or `stage1_rail`.
  The fleet's new reviewed C (CD-001 stage-1 leaves, BL-006 pools,
  Apollo overlay helpers) routes through component
  overlays/candidates, not the transparent Apollo image, so no
  transparent registration is due.
  `tests.test_transparent_reviewed_source`: 8/8 pass.
* `docs/reports/openCFW-completion-2026-08-28/assessment-data.json`
  NOT regenerated: the generator runs `readiness.analyze()`, still red
  (never hand-edited).
* `docs/transparent-source-ledger.md` NOT regenerated:
  `build/transparent/` still holds only
  `function-db.json`/`region-map.json`/`DB-SUMMARY.json` (DB-SUMMARY
  7,449 functions / 1,394,848 code bytes, matching the ledger line;
  no `source|image` stages).

### Test evidence this pass

* `tests.test_transparent_reviewed_source`: 8/8 pass.
* `tests.test_analyze_g2_completion_readiness`: setUpClass error on the
  BL partition disagreement (+4576/-4576); 0 ran (owner: BL-006).
* `tests.test_analyze_g2_project_license_normalization`: 4 ran, 1 census
  error on the 17 CD-001 files (owner: CD-001).
* Raw-encoding tool direct run: fails only on the known spotmgr file
  (owner: BL).

No hardware operation occurred; hardware qualification remains blocked by
unavailable physical evidence. This item has no flash-range component.

## XC-002 pass 2026-09-12 (~02:40): manifest↔builder agree again, re-pin deferred

HEAD is still `284b98a7`; all tree movement is uncommitted owner-lane
work (BL overlay growth + manifest regen, CD-001 stage-1 leaves now at
3,106/8,192B per its progress entry). This pass made no tool,
manifest, or test edits -- re-verification plus a pin-vs-defer decision
with evidence. The decision is DEFER, for a new structural reason
below; all blockers keep their owners.

### Changed signature: BL manifest regenerated via write path, partition passes

Between the ~02:00 pass and this one, the BL lane ran a full landing
pipeline in the working tree: overlay 02:04 → builder report 02:14 →
core-source manifest 02:18 (all uncommitted). The manifest now pins
provider `696a6baf…`, 64905 source / 82089 opaque, byte-identical to
the builder's own component accounting, so `analyze()`'s
manifest↔builder partition check PASSES (verified with the tool's own
`_region_partition`: `official_blob` 82089 / `source_compiled` 64905
both sides). The gate now fails one step later at
`bootloader retained complement changed`: pin 87_981 vs live 82_089.
`tests.test_analyze_g2_completion_readiness` setUpClass-errors with
the identical message; 0 ran. (BL-006's own
`test_bootloader_core_overlay.py` already carries the new provider
sha plus two new range/divzero constants -- BL hands are in these
files now.)

### Why not re-pin: interval names changed, not just counts

Running the four companion BL gates directly shows the re-pin is no
longer mechanical. Three fail on renamed manifest intervals, i.e. the
tools key regions by name and the names no longer exist:

* `analyze_g2_bootloader_mspi_lifecycle_425066.py:282` --
  `KeyError: 'bootloader_mspi_enable_unreachable_tail_4250e6_4250f0_official'`
* `analyze_g2_bootloader_mspi_transfer_interrupt_4262e0.py:196` --
  `KeyError: 'bootloader_mspi_control_unreachable_tail_42612c_4262e0_official'`
* `analyze_g2_bootloader_post_mspi_frontier.py:8736` --
  `KeyError` in the same `by_name[name]` lookup (its stale
  `(59_013, 87_981, 2_594, 41_190, 16_830)` tuple at line 8749 is
  behind a second, structural mismatch)
* `analyze_g2_bootloader_mspi_control_4251c0.py` fails cleanest at
  `apple-clang provider changed` (its `PROFILE_PINS` still carry the
  old `(163840, 13e2ce…, 59013, 87981)` plus in-place 41190 vs live
  45746)

Adapting name-keyed frontier analysis to BL-006's restructured
intervals is BL-domain work on an uncommitted, still-moving overlay;
bumping only the numeric pins would leave the gates red on the
KeyErrors anyway. Re-pin and rename adaptation stay BL-006's landing
chore. Followup values once it lands and settles: retained 82_089,
source 64_905, in_place 45_746, provider `696a6baf…`, plus the new
interval names in the three frontier tools and their tests.

### Still red (owner lanes, gates working as designed)

* Raw-encoding gate now has TWO failing files. The committed spotmgr
  pads persist (41 directive hits in
  `runtime_spotmgr_shared_literals_42a078.c`, still not
  production-routed), plus BL-006's untracked
  `runtime_bl006_spot_trim_span_427e54.c` (3 `.word` hits at lines
  361-363 embedding float bit-patterns `0xC3888000/0x42480000/
  0x447A0000` as literal-pool words). The tool fail-fasts on the
  first file in scan order, so the second was confirmed with the
  tool's own `DIRECTIVE` regex. Both are the BL owner's call.
* License community census: drift grew 17 -> 18 files, all CD-001's
  untracked MIT stage-1 leaves (the known 17 plus new
  `runtime_gx8002_uart_stage1_pmusecond.S` and
  `runtime_gx8002_uart_stage1_uartcfg.S`; `SPDX-License-Identifier:
  MIT` verified in all 18, 0 missing). Computed with the tool's own
  manifest loader and disk-scan logic (manifest 298, disk 319 incl.
  adapters, 18 extra, 0 missing). Followup once CD-001 lands: +18
  manifest lines in sorted position, tool `298 -> 316` /
  `1112 -> 1130`, same bumps in the companion test pins.
  `tests.test_analyze_g2_project_license_normalization`: 4 ran, 1
  census error, as expected.

### Re-verified clean (tool's own logic, not hand-rolled sets)

* Touch disk == manifest (10 == 10), Case disk == manifest (8 == 8,
  `build/` exclusion holds, `CasePackageSourceStaticTests` 2/2 pass),
  EM9305 disk == manifest (21 == 21).
* `reviewed_sources.json` needs no action (negative result, verified
  not assumed): 4 functions / 34 bytes, untouched since `d794c28e`;
  `components/shared/cortex_m55/` still exactly the 4 registered
  files; grep over `tools/transparent/` finds no reference to any new
  untracked leaf (`stage1_rail`, `postamble`, `pmudispatch`,
  `spot_trim`). The fleet's new reviewed C routes through component
  overlays/candidates, not the transparent Apollo image, so no
  transparent registration is due.
  `tests.test_transparent_reviewed_source` 8/8 and
  `tests.test_analyze_g2_touch_final_frontier` 13/13 pass (21/21
  combined).
* `docs/reports/openCFW-completion-2026-08-28/assessment-data.json`
  NOT regenerated: the generator runs `readiness.analyze()`, still
  red (never hand-edited).
* `docs/transparent-source-ledger.md` NOT regenerated:
  `build/transparent/DB-SUMMARY.json` still 7,449 functions /
  1,394,848 code bytes, matching the ledger line; no `source|image`
  stages exist (full rebuild stays XC-004's failed pipeline).

### Test evidence this pass

* `tests.test_transparent_reviewed_source`: 8/8 pass.
* `tests.test_analyze_g2_touch_final_frontier`: 13/13 pass.
* `CasePackageSourceStaticTests`: 2/2 pass.
* `tests.test_analyze_g2_completion_readiness`: setUpClass error on
  the retained complement (87_981 vs 82_089); 0 ran (owner: BL-006).
* `tests.test_analyze_g2_project_license_normalization`: 4 ran, 1
  census error on the 18 CD-001 files (owner: CD-001).
* Raw-encoding tool direct run: fails on spot_trim_span (first in
  scan order); spotmgr pads confirmed still offending via the tool's
  own regex (owner: BL).

No hardware operation occurred; hardware qualification remains blocked by
unavailable physical evidence. This item has no flash-range component.

## XC-002 pass 2026-09-12 (~03:15): BL-009 landing visible, re-pin still deferred

HEAD is still `284b98a7`; all tree movement is uncommitted owner-lane
work (BL-009 gap literals per its own progress entry, CD-001 stage-1
leaves now including traptails). This pass made no tool, manifest, or
test edits -- re-verification plus a pin-vs-defer decision with
evidence. The decision is DEFER again: the BL lane is actively
rebuilding in this tree (core-source manifest 03:07, bootloader
build-report 03:10, minutes before this pass), so pinning targets a
moving file set, and the structural rename mismatch persists. All
blockers keep their owners.

### Changed signatures (owner lanes, gates working as designed)

* `python3 tools/analyze_g2_completion_readiness.py` still fails at
  `bootloader retained complement changed` (line 795), but the live
  numbers moved: manifest and builder now AGREE at provider size
  163840 / sha `696a6bafaea1`, 65239 source / 81755 opaque
  (verified with the tool's own `_region_partition`: status
  `official_blob` 81755 / `source_compiled` 65239 both sides, plus
  16 generated_alignment / 16830 generated_source_entry_replacement).
  That is +334 source / -334 opaque since the ~02:40 pass
  (64905/82089), matching BL-009's own 334B gap-literal claim
  (958 regions; opaque 82089 -> 81755). Delta vs this item's
  committed 4B re-pin (59013/87981) is now +6226/-6226.
  `tests.test_analyze_g2_completion_readiness` setUpClass-errors
  with the identical message; 0 ran (owner: BL-009/BL-006).
* The structural deferral reason persists: the two old
  name-keyed intervals
  (`..._mspi_enable_unreachable_tail_4250e6_4250f0_official`,
  `..._mspi_control_unreachable_tail_42612c_4262e0_official`) are
  still absent from the 958-region manifest, so the three frontier
  tools would still `KeyError` after a numeric-only bump. Rename
  adaptation stays the BL owner's landing chore. Followup values
  once it lands and settles: retained 81_755, source 65_239,
  provider `696a6bafaea1`, plus the new interval names in the three
  frontier tools and their tests (in_place/provider pins move too).
* Raw-encoding gate still has TWO failing files, confirmed with the
  tool's own `DIRECTIVE` regex (unchanged,
  `\.(byte|short|hword|word)\s+(?!=)`): committed
  `runtime_spotmgr_shared_literals_42a078.c` (41 hits, still not
  production-routed) plus BL-006's untracked
  `runtime_bl006_spot_trim_span_427e54.c` (3 `.word` hits, float
  bit-patterns). Tool fail-fasts on the latter in scan order.
  Both are the BL owner's call.
* License community census: drift grew 18 -> 19 files, all CD-001's
  untracked MIT stage-1 leaves (the known 18 plus new
  `runtime_gx8002_uart_stage1_traptails.S`, the trap-tail leaf from
  CD-001's own 3,414/8,192B progress entry;
  `SPDX-License-Identifier: MIT` verified, file still untracked;
  19 untracked non-verifier/NOTICE files on disk == 19 computed
  extras). Computed with the tool's exact logic including the
  `COMMUNITY_BUILD_ADAPTERS` union (manifest 298, disk 320 incl.
  adapters, 19 extra, 0 missing). Followup once CD-001 lands: +19
  manifest lines in sorted position, tool `298 -> 317` /
  `1112 -> 1131`, same bumps in the companion test pins.
  `tests.test_analyze_g2_project_license_normalization`: 4 ran,
  1 census error, as expected.

### Re-verified clean (tool's own logic, not hand-rolled sets)

* Touch disk == manifest (10 == 10, exact logic incl. support
  paths), Case disk == manifest (8 == 8, `_is_case_package_source`
  + `build/` exclusion holds, `CasePackageSourceStaticTests` 2/2
  pass), EM9305 disk == manifest (21 == 21, exact logic with
  `build`/`__pycache__`/`.pyc` exclusions).
* `reviewed_sources.json` needs no action (negative result, verified
  not assumed): 4 functions / 34 bytes, untouched;
  `components/shared/cortex_m55/` still exactly the 4 registered
  files; grep over `tools/transparent/` and `build/transparent/`
  finds no reference to `traptails`, `stage1_rail`, `postamble`, or
  `pmudispatch`. The fleet's new reviewed C (BL-009 gap literals,
  CD-001 stage-1 leaves, Apollo overlay helpers) routes through
  component overlays/candidates, not the transparent Apollo image,
  so no transparent registration is due.
  `tests.test_transparent_reviewed_source` (8/8) +
  `tests.test_analyze_g2_touch_final_frontier` (13/13) pass (21/21
  combined).
* `docs/reports/openCFW-completion-2026-08-28/assessment-data.json`
  NOT regenerated: the generator runs `readiness.analyze()`, still
  red (never hand-edited).
* `docs/transparent-source-ledger.md` NOT regenerated:
  `build/transparent/DB-SUMMARY.json` still 7,449 functions /
  1,394,848 code bytes, matching the ledger line; no
  `source|image` stages exist (full rebuild stays XC-004's failed
  pipeline).

### Test evidence this pass

* `tests.test_transparent_reviewed_source` +
  `tests.test_analyze_g2_touch_final_frontier`: 21/21 pass.
* `CasePackageSourceStaticTests`: 2/2 pass.
* `tests.test_analyze_g2_completion_readiness`: setUpClass error on
  the retained complement (live 81_755 vs pin 87_981); 0 ran
  (owner: BL-009/BL-006).
* `tests.test_analyze_g2_project_license_normalization`: 4 ran, 1
  census error on the 19 CD-001 files (owner: CD-001).
* Raw-encoding tool direct run: fails on spot_trim_span (first in
  scan order); spotmgr pads confirmed still offending via the
  tool's own regex (owner: BL).

No hardware operation occurred; hardware qualification remains blocked by
unavailable physical evidence. This item has no flash-range component.

## XC-002 pass 2026-09-12 (~04:00): BL +246B, license drift 19 -> 20, re-pin deferred

HEAD is still `284b98a7`; all tree movement is uncommitted owner-lane
work (BL overlay growth + manifest regen 03:33 / builder report 03:27,
CD-001 stage-1 leaves now including a beacon tranche). This pass made
no tool, manifest, or test edits -- re-verification plus a pin-vs-defer
decision with evidence. The decision is DEFER again: the BL lane
rebuilt both pinned files minutes before this pass, so pinning targets
a moving file set, and the structural rename mismatch persists. All
blockers keep their owners.

### Changed signatures (owner lanes, gates working as designed)

* `python3 tools/analyze_g2_completion_readiness.py` still fails at
  `bootloader retained complement changed` (line 795), but the live
  numbers moved: manifest and builder AGREE at provider size
  163840 / sha `696a6bafaea1`, 65485 source / 81509 opaque
  (verified with the tool's own `_region_partition`: status
  `official_blob` 81509 / `source_compiled` 65485 both sides, plus
  16 generated_alignment / 16830 generated_source_entry_replacement;
  978 regions). That is +246 source / -246 opaque since the ~03:15
  pass (65239/81755). Delta vs this item's committed 4B re-pin
  (59013/87981) is now +6472/-6472.
  `tests.test_analyze_g2_completion_readiness` setUpClass-errors
  with the identical message; 0 ran (owner: BL-009/BL-006).
* The structural deferral reason persists: the two old
  name-keyed intervals
  (`..._mspi_enable_unreachable_tail_4250e6_4250f0_official`,
  `..._mspi_control_unreachable_tail_42612c_4262e0_official`) are
  still absent from the 978-region manifest, so the three frontier
  tools would still `KeyError` after a numeric-only bump. Rename
  adaptation stays the BL owner's landing chore. Followup values
  once it lands and settles: retained 81_509, source 65_485,
  provider `696a6bafaea1`, plus the new interval names in the three
  frontier tools and their tests (in_place/provider pins move too).
* Raw-encoding gate still has TWO failing files: the tool
  fail-fasts on BL-006's untracked
  `runtime_bl006_spot_trim_span_427e54.c` (first in scan order),
  and the committed `runtime_spotmgr_shared_literals_42a078.c`
  still offends (41 directive hits via the tool's own `DIRECTIVE`
  regex, file still not production-routed). Both are the BL
  owner's call.
* License community census: drift grew 19 -> 20 files, all CD-001's
  untracked MIT stage-1 leaves (the known 19 plus new
  `runtime_gx8002_uart_stage1_beacon.S`;
  `SPDX-License-Identifier: MIT` verified, file still untracked).
  Computed with the tool's exact comparison logic (manifest 298,
  disk+adapters 321, union 301, 20 extra, 0 missing). Followup once
  CD-001 lands: +20 manifest lines in sorted position, tool
  `298 -> 318` / `1112 -> 1132`, same bumps in the companion test
  pins. `tests.test_analyze_g2_project_license_normalization`:
  4 ran, 1 census error, as expected.

### Re-verified clean (tool's own logic, not hand-rolled sets)

* Touch disk == manifest (10 == 10), Case disk == manifest (8 == 8,
  `_is_case_package_source` + `build/` exclusion holds,
  `CasePackageSourceStaticTests` 2/2 pass), EM9305 disk == manifest
  (21 == 21, exact nested per-root exclusions).
* `reviewed_sources.json` needs no action (negative result, verified
  not assumed): schema v1, functions unchanged; `components/shared/
  cortex_m55/` still exactly the 4 registered files with no diff;
  grep over `tools/transparent/` and `build/transparent/` finds no
  reference to `beacon`, `stage1_rail`, `traptails`, or
  `pmudispatch`. The fleet's new reviewed C routes through component
  overlays/candidates, not the transparent Apollo image, so no
  transparent registration is due.
  `tests.test_transparent_reviewed_source` (8/8) +
  `tests.test_analyze_g2_touch_final_frontier` (13/13) pass (21/21
  combined).
* `docs/reports/openCFW-completion-2026-08-28/assessment-data.json`
  NOT regenerated: the generator runs `readiness.analyze()`, still
  red (never hand-edited).
* `docs/transparent-source-ledger.md` NOT regenerated:
  `build/transparent/DB-SUMMARY.json` still 7,449 functions /
  1,394,848 code bytes, matching the ledger line; no
  `source|image` stages exist (full rebuild stays XC-004's failed
  pipeline).

### Test evidence this pass

* `tests.test_transparent_reviewed_source` +
  `tests.test_analyze_g2_touch_final_frontier`: 21/21 pass.
* `CasePackageSourceStaticTests`: 2/2 pass.
* `tests.test_analyze_g2_completion_readiness`: setUpClass error on
  the retained complement (live 81_509 vs pin 87_981); 0 ran
  (owner: BL-009/BL-006).
* `tests.test_analyze_g2_project_license_normalization`: 4 ran, 1
  census error on the 20 CD-001 files (owner: CD-001).
* Raw-encoding tool direct run: fails on spot_trim_span (first in
  scan order); spotmgr pads confirmed still offending (41 hits) via
  the tool's own regex (owner: BL).

No hardware operation occurred; hardware qualification remains blocked by
unavailable physical evidence. This item has no flash-range component.

## XC-002 pass 2026-09-12 (~04:30): BL +230B, license drift 20 -> 21, re-pin deferred

HEAD is still `284b98a7`; all tree movement is uncommitted owner-lane
work (BL-009 manifest re-tile 983 regions per its own progress entry,
CD-001 stage-1 announce tranche at 3,810/8,192B per its checkpoint).
This pass made no tool, manifest, or test edits -- re-verification
plus a pin-vs-defer decision with evidence. The decision is DEFER
again: the BL lane rebuilt both pinned files minutes before this pass
(build-report mtime 04:10), so pinning targets a moving file set, and
the structural rename mismatch persists. All blockers keep their
owners.

### Changed signatures (owner lanes, gates working as designed)

* `python3 tools/analyze_g2_completion_readiness.py` still fails at
  `bootloader retained complement changed` (line 796), but the live
  numbers moved: manifest and builder AGREE at provider size
  163840 / sha `696a6bafaea1`, 65715 source / 81279 opaque
  (verified with the tool's own `_region_partition`: status
  `official_blob` 81279 / `source_compiled` 65715 both sides, plus
  16 generated_alignment / 16830 generated_source_entry_replacement;
  983 regions). That is +230 source / -230 opaque since the ~04:00
  pass (65485/81509), matching BL-009's own re-tile claim. Delta vs
  this item's committed 4B re-pin (59013/87981) is now +6702/-6702.
  `tests.test_analyze_g2_completion_readiness` setUpClass-errors
  with the identical message; 0 ran (owner: BL-009/BL-006).
* The structural deferral reason persists: the two old
  name-keyed intervals
  (`..._mspi_enable_unreachable_tail_4250e6_4250f0_official`,
  `..._mspi_control_unreachable_tail_42612c_4262e0_official`) are
  still absent from the 983-region manifest (checked by name set),
  so the three frontier tools would still `KeyError` after a
  numeric-only bump. Rename adaptation stays the BL owner's landing
  chore. Followup values once it lands and settles: retained 81_279,
  source 65_715, in_place_data 1_718, provider `696a6bafaea1`, plus
  the new interval names in the three frontier tools and their tests.
* Raw-encoding gate still has TWO failing files, confirmed with the
  tool's own `DIRECTIVE` regex: the committed
  `runtime_spotmgr_shared_literals_42a078.c` (41 hits, still not
  production-routed) plus BL-006's untracked
  `runtime_bl006_spot_trim_span_427e54.c` (3 `.word` hits, float
  bit-patterns). Tool fail-fasts on the latter in scan order.
  Both are the BL owner's call.
* License community census: drift grew 20 -> 21 files, all CD-001's
  untracked MIT stage-1 leaves (the known 20 plus new
  `runtime_gx8002_uart_stage1_announce.S`, the 124-byte announce
  leaf from CD-001's own 3,810/8,192B checkpoint;
  `SPDX-License-Identifier: MIT` verified in head lines, file still
  untracked; 18 sibling NOTICE `.txt` files are suffix-excluded from
  the census). Computed with the tool's exact comparison logic
  (manifest 298, disk+adapters 322, 21 extra, 0 missing). Followup
  once CD-001 lands: +21 manifest lines in sorted position, tool
  `298 -> 319` / `1112 -> 1133`, same bumps in the companion test
  pins. `tests.test_analyze_g2_project_license_normalization`:
  4 ran, 1 census error, as expected.

### Re-verified clean (tool's own logic, not hand-rolled sets)

* Touch disk == manifest (10 == 10, exact logic incl. support
  paths), Case disk == manifest (8 == 8, `_is_case_package_source`
  + `build/` exclusion holds), EM9305 disk == manifest (21 == 21,
  exact nested per-root exclusions).
* `reviewed_sources.json` needs no action (negative result, verified
  not assumed): schema v1, functions unchanged;
  `components/shared/cortex_m55/` still exactly the 4 registered
  files; the single `announce` hit in `build/transparent/
  function-db.json` is pre-existing decompiler prose
  ("announces lifecycle state 7", function 1913 map evidence),
  unrelated to the new GX8002 `stage1_announce.S` leaf. The fleet's
  new reviewed C (BL-009 gaps, CD-001 announce leaf, Apollo overlay
  helpers) routes through component overlays/candidates, not the
  transparent Apollo image, so no transparent registration is due.
  `tests.test_transparent_reviewed_source` (8/8) +
  `tests.test_analyze_g2_touch_final_frontier` (13/13) pass (21/21
  combined).
* `docs/reports/openCFW-completion-2026-08-28/assessment-data.json`
  NOT regenerated: the generator runs `readiness.analyze()`, still
  red (never hand-edited).
* `docs/transparent-source-ledger.md` NOT regenerated:
  `build/transparent/DB-SUMMARY.json` still 7,449 functions /
  1,394,848 code bytes, matching the ledger line; no
  `source|image` stages exist (full rebuild stays XC-004's failed
  pipeline).

### Test evidence this pass

* `tests.test_transparent_reviewed_source` +
  `tests.test_analyze_g2_touch_final_frontier`: 21/21 pass.
* `tests.test_analyze_g2_completion_readiness`: setUpClass error on
  the retained complement (live 81_279 vs pin 87_981); 0 ran
  (owner: BL-009/BL-006).
* `tests.test_analyze_g2_project_license_normalization`: 4 ran, 1
  census error on the 21 CD-001 files (owner: CD-001).
* Raw-encoding tool direct run: fails on spot_trim_span (first in
  scan order); spotmgr pads confirmed still offending (41 hits) via
  the tool's own regex (owner: BL).

No hardware operation occurred; hardware qualification remains blocked by
unavailable physical evidence. This item has no flash-range component.
