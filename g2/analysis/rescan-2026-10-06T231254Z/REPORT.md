# Source and evidence rescan

Snapshot: 2026-10-06T23:12:54.603727+00:00. Compared with `g2/analysis/rescan-2026-10-06T222801Z` (22:28 UTC). Read-only inspection of sources/builds; only this scan directory was written. No build, generator, emulator, staging, commit or hardware operation ran. Live source work and previous receipts were preserved.

## What changed

Bootloader C/header/assembly inventory **192 → 221**: **30 added, 4 modified, 1 removed**. Foundation remains **89**. Counts include headers, vendored code and fixture code; they measure files, not completed firmware. Across both source roots, 280 files are tracked/indexed and 30 untracked. All 30 newly added source files remain untracked and visible to Git. **Zero source files match ignore rules** using `git check-ignore --no-index -v`.

Substantive new implementations and existing differential receipts:

| Family | Evidence | Integration status |
| --- | --- | --- |
| Instruction/data cache enable | 1,440 PASS; ordered writes/barriers and register state | Native in d79e source image; physical cache coherence unverified |
| Register-ID read | 224 accepted IDs + 6 edge cases PASS | Native in d79e; raw register base 0x40010000, peripheral identity unresolved |
| Mode publication | 563 PASS, including original ABI return behavior | Native in d79e |
| MSPI requests 26/27/29 | 172 PASS | Dispatcher routes them to native state/clock handlers in shared image |
| MSPI request30 / request34 / queue helpers | 33 / 19 / 37 PASS | New standalone sources/fixtures; **30/34 still reach the unrecovered provider in shared dispatcher** |
| Initializer runner/qsort | 98 sorting + 5 runner + 5 comparator cases PASS | Real qsort source replaces deleted `sort_cut.S`; runner remains a numerical alias in shared image |
| Initializer callbacks/services/ADC/platform finishing | 31 callback + 60 mode-register cases PASS | Separate source-linked fixture; child providers remain; six original floating-point slots have emulated effects |
| NOR serial mode / address mode / timing scan / linked timing wrapper | 16 / 15 / 6 / 3 PASS | Separate native fixtures; shared bindings420c5c/420890/4201ba still numerical aliases |

These are bounded original/source comparisons with synthetic external inputs. Case totals across suites are not a firmware completeness metric. Callback ADC readiness/samples, asynchronous queue progress and MMIO are modeled; no hardware result follows.

## Validation now tied to a newer immutable image

The **d79edbcb73ffd445fa3da1f3bce847e611af7b2525b214d86ebdd2b94324e6c1** immutable ELF has seven PASS cases: two normal/update, three malformed update, two interruption/reboot. Union observed original trace bytes is **31,344**, up from the earlier8cd9 checkpoint's30,814. This is observed path coverage, not whole-image code coverage. The scan freshly hashed the pinned ELF, seed and all three receipt files: all five match their recorded identities.

The seed remains `e6ba6916ee417e9efec1f4dc90a50f8ce7777f0e2ad8f976e6d2e27856072b78`. Interruption happens immediately before/after an atomic synthetic ROM page operation; it does not prove physical partial-write recovery or application execution. See `g2/analysis/bootloader-completion-2026-10-06/integrated-status/same-image-validation-d79e.json`.

The mutable `bootloader-source-test.elf` and its normal/malformed receipts still identify **044b12f8…**; `bootloader-source-test-repro.elf` identifies **d79edbcb…**. Therefore follow the immutable d79e checkpoint, rather than treating every similarly named current build as the same image. This scan did not promote or overwrite any artifact.

## What is still incomplete

The d79e manifest lists **38 numerical linker bindings**, including duplicate names at shared addresses and three legitimate resident-ROM APIs absent from the OTA. This is not a count of38 missing functions. Exact binding names/addresses are preserved in `source-image-manifest-d79e.json` and copied into this snapshot.

Internal work remains: integrate request30/34; bind the tested NOR timing/address/serial-mode chain; bind initializer runner and complete callback children; startup orchestration41fa50; filesystem mutex/runtime-control paths; ISR queue/notification/event, deferred/cancellation/termination paths; logging/fatal paths; accepted non-NULL power configuration422ba8. Full payload vectors, assets/data definitions, layout, compiler reproduction and whole-payload/source build remain open. Physical timing/IRQ/cache/ROM behavior and hardware boot are separate evidence boundaries.

Two broad receipt source-hash mismatches identify `control_request_transactions.c` and `xip_address_mode.c`. Those files have subsequent isolated fixture evidence, but neither is selected by the current shared compile list/native binding. This mismatch cannot invalidate the pinned ELF's executed behavior or establish that current source rebuilds it; the report does not transfer d79e results to these unlinked files.

## Git ignore interpretation

`.gitignore:15:build/` hides the build ELFs and build-local JSON receipts. The general `*.elf` rule also targets loose binaries. It does **not** hide the new C/header/assembly files or this delivered analysis. No nested ignores were found under the inspected source/analysis roots; `.git/info/exclude` is absent and no `core.excludesFile` is configured. Build outputs therefore exist beyond ordinary Git status, while source progress is visible as untracked additions. There is no evidence that ignore rules are concealing source generation in these roots.

## Changed source paths

- `g2/components/bootloader/clock_manager/mode_publisher.c` — added
- `g2/components/bootloader/clock_manager/mode_publisher.h` — added
- `g2/components/bootloader/clock_manager/mode_publisher_abi.S` — added
- `g2/components/bootloader/init_table/init_table.c` — modified
- `g2/components/bootloader/init_table/init_table.h` — modified
- `g2/components/bootloader/init_table/qsort.c` — added
- `g2/components/bootloader/initializer_callbacks/initializer_callbacks.c` — added
- `g2/components/bootloader/initializer_callbacks/initializer_callbacks.h` — added
- `g2/components/bootloader/initializer_callbacks/mode_register.c` — added
- `g2/components/bootloader/initializer_callbacks/platform_bringup.c` — added
- `g2/components/bootloader/initializer_callbacks/platform_finish.c` — added
- `g2/components/bootloader/initializer_callbacks/post_bringup.c` — added
- `g2/components/bootloader/nor_mspi_init/control_remaining.c` — modified
- `g2/components/bootloader/nor_mspi_init/control_remaining.h` — modified
- `g2/components/bootloader/nor_mspi_init/control_request34.c` — added
- `g2/components/bootloader/nor_mspi_init/control_request34.h` — added
- `g2/components/bootloader/nor_mspi_init/control_request_clock.c` — added
- `g2/components/bootloader/nor_mspi_init/control_request_clock.h` — added
- `g2/components/bootloader/nor_mspi_init/control_request_helpers.c` — added
- `g2/components/bootloader/nor_mspi_init/control_request_helpers.h` — added
- `g2/components/bootloader/nor_mspi_init/control_request_state.c` — added
- `g2/components/bootloader/nor_mspi_init/control_request_state.h` — added
- `g2/components/bootloader/nor_mspi_init/control_request_transactions.c` — added
- `g2/components/bootloader/nor_mspi_init/control_request_transactions.h` — added
- `g2/components/bootloader/nor_mspi_init/register_id.c` — added
- `g2/components/bootloader/nor_mspi_init/register_id.h` — added
- `g2/components/bootloader/nor_mspi_power/serial_mode_switch.c` — added
- `g2/components/bootloader/nor_mspi_power/serial_mode_switch.h` — added
- `g2/components/bootloader/nor_mspi_power/timing_scan.c` — added
- `g2/components/bootloader/nor_mspi_power/timing_scan.h` — added
- `g2/components/bootloader/nor_mspi_power/xip_address_mode.c` — added
- `g2/components/bootloader/nor_mspi_power/xip_address_mode.h` — added
- `g2/components/bootloader/platform_control/cache_enable.c` — added
- `g2/components/bootloader/platform_control/cache_enable.h` — added

Removed: `g2/components/bootloader/init_table/sort_cut.S` (replaced by reconstructed `qsort.c`). The staged historical addition is preserved; Git shows AD, rather than this scan modifying the index.

`snapshot.json` contains file hashes, timestamps, tracked/ignored views, selected full receipts, artifact identities and verification results. `git-status.txt` captures the checkout view at scan time. The source inventory is a point-in-time observation; concurrent work can advance after it.
