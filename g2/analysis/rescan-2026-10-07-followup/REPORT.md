# OpenCFW follow-up scan — 2026-10-07 09:28 UTC

Compared with the 05:42 UTC scan, the change is concrete reconstructed source and validation, not newly installed SDK content. This scan reads existing receipts; it does not rerun emulation or promote candidates. Existing work and index were preserved. Only this report and inventory are new.

## Source and checkpoint changes

The prior scan examined candidate `be4ede3b` (635 inputs/161 objects) while the status report still named `9affaa59`. The current verified report names `5539579c` (667 inputs/171 objects), with seven integration cases and 25 direct suites reported PASS. Clock configuration, generators/math, UART RX, run/power policy and ITM/debug-release work now have source and focused evidence. These are component reconstructions, not proof of a complete firmware rebuild.

| Representative source | Bytes on disk | Git status |
|---|---:|---|
| `uart_rx.c` | 3,727 | ?? g2/components/bootloader/initializer_callbacks/uart_rx.c |
| `clock_generators.c` | 3,530 | ?? g2/components/bootloader/initializer_callbacks/clock_generators.c |
| `startup_shutdown.c` | 3,520 | ?? g2/components/bootloader/initializer_callbacks/startup_shutdown.c |
| `startup_power_config.c` | 3,787 | ?? g2/components/bootloader/initializer_callbacks/startup_power_config.c |

The newer `761be470` startup-power candidate has 697 passing original-instruction comparisons for configuration, temperature callback and logging-sink behavior. At scan time its normal two-case and malformed three-case receipts report PASS; the expected `powerloss.json` is absent. The candidate remains unpromoted, and the current verified checkpoint remains `5539579c`. The selected linker has removed three OTA aliases for this candidate, but the verified ledger still correctly records 13 OTA addresses, four synthetic cuts and three ROM boundaries.

## Inventory and ignore visibility

`g2/components` contains 208 C files, 139 headers and 19 assembly files (366 total). The scoped R1 source inventory has 21 C files and 22 headers. These are current counts, not historical source deltas or completion percentages.

The Git views contain 1,330 staged paths (64 C/header/assembly), 16 unstaged paths (three source paths), and 4,408 untracked paths (140 source paths). Categories can overlap; untracked vendor references do not all represent reconstructed firmware. No index changes were made by this scan.

The original Ambiq, EM and IAR SDK roots have unchanged file and extension counts versus the prior scan. `.gitignore` still excludes local vendor SDKs and build outputs. `git check-ignore -v` identifies `build/` for the bootloader ELF and returns no matching rule for `startup_power_config.c` or its analysis receipt. No global excludes file is configured and no active `info/exclude` rules were found. The only nested ignore in the inspected source/analysis roots is the asset-extraction directory rule. Thus ignores affect artifact visibility, but do not explain an absence of reconstructed C.

## Newly recovered references and remaining limits

The shortcut outputs now include real IAR archive-function comparisons, EM function compatibility probes, GX model-boundary validation and a held-out graphics descriptor. Historical Git recovery has also made Ambiq draw, Google liblc3 and Nema header/reference snapshots available at `../rescan-2026-10-07/implemented/resources/reference-snapshots/`. The local-input report records 91 recovered files and manifest checks. The checklist still says those paths are absent: that statement is stale. Availability does not establish stock-version compatibility or native integration.

The complete physical glasses NOR image and foreground font remain absent from the documented paths searched by the prior resource investigation. IAR compiler access and MetaWare remain separate toolchain boundaries. Real scheduling/drain, integration startup/logger models, external ROM, full source completeness and byte identity remain unresolved. The seven-case observed instruction footprint of 26.08631% must not be read as a source-completion percentage.

## Next concrete work

Finish and reconcile the `761be470` interruption/reboot receipt and remaining candidate-specific regression/hash checks before promotion. Then the unresolved startup initializer at `0x41c4b4` is a bounded next source dependency. The shared campaign and existing status/checklist files were left untouched by this scan.

Machine-readable counts and candidate receipt observations: [inventory.json](inventory.json).

## Subsequent implementation completion

After this read-only snapshot, interruption/reboot validation completed. Candidate761be470 was promoted only after all7 integration cases,26 direct/regression receipts,670 input hashes/172 object hashes and frozen copies reconciled,493 mappings PASS and zero manifest mismatches.33 referenced receipt hashes independently rechecked. The earlier missing-powerloss observation is historical. The shared status/checklist was then explicitly updated under the continued implementation request. See [current status](../bootloader-completion-2026-10-06/integrated-status/REPORT.md) and [next initializer deliverable](../bootloader-completion-2026-10-06/inventory-worker/startup-initialize/REPORT.md).
