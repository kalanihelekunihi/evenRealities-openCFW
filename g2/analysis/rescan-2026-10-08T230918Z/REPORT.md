# OpenCFW change scan — 2026-10-08 23:09 UTC

Compared with the [22:25 scan](../rescan-2026-10-08T222551Z/REPORT.md), component C/header/assembly inventory grew **650 → 661 files: 11 added, none modified or removed**. These are actual files on disk: **654 indexed, seven untracked, zero ignored**. Counts include historical and partial helpers; they do not measure firmware completeness.

## New source and knowledge

| Batch | Complete native functions recorded | Recorded validation | Newly recovered behavior |
|---|---:|---|---|
| [Clock ownership](../audio-clock-manager-ownership-2026-10-08/REPORT.md) | 6 | 514 comparisons; 24 original-only assertions | Idempotent user bits, XTAL last-user release and command-state/readiness distinction |
| [XTAL/HFRC closure](../audio-xtal-request-closure-2026-10-08/REPORT.md) | 5 | 836 comparisons; 12 original-only assertions | Exact 20-byte board layout, stock reference defaults, software waits and HFRC configuration |
| [HFRC/SYSPLL requests](../audio-hfrc-syspll-closure-2026-10-08/REPORT.md) | 8 | 848 comparisons; 8 original-only assertions | Reference ownership, setup cleanup, discarded/overwritten errors and late lock failure |
| [Driver/configuration](../audio-clock-driver-config-2026-10-08/REPORT.md) | 9 | 3,403 comparisons including reused regressions | SYSPLL driver lifecycle, configuration validation and stock-default call sequences |
| [Clock/power leaves](../audio-clock-leaf-providers-2026-10-08/REPORT.md) | 13 | 1,374 direct + 12 sequences + 3,403 reused comparisons | GPIO15 ownership, power commands, HFRC2 retry behavior and numerical/FPSCR effects |

These five batches record **41 complete native function bodies** in the 11 added C/header files. Each has a seal and final-build validation receipt. This scan verified their sealed artifact hashes and inspected results; it did not rerun comparisons or independently review function correctness. Regression fixtures overlap and must not be summed as distinct coverage.

The [INFO1/memory/oscillator batch](../audio-info-memory-providers-2026-10-08/REPORT.md), which was unfinished at the prior scan, is now sealed and records all **1,182 comparisons against one final ELF** (`4a81046ae3ddb64e443d3e9c6ab9c71bdad34fa09ed6a49ae76ecd47d97a89cc`). Its earlier mixed-build validation gap is resolved in the delivered records.

## Practical findings and corrections

Stock board initialization installs HS frequency0, LS32768 and external12MHz. Missing HS therefore rejects fresh XTAL-reference configuration before ownership acquisition; earlier seeded XTAL scenarios remain synthetic. Address0x4C38A0 is HFRC configuration, correcting the previous ownership report's board-initialization identification. The actual board setter is0x4C45E2.

Through stock-compatible offline configuration sequences, HFRC2 can discard an actual force-on timeout and retain ownership. SYSPLL late lock timeout retains ownership/handle; repeat request returns cached success without checking lock. Setup failure instead removes ownership and cleans up. These are demonstrated original-instruction control flows with synthetic readiness fields, not observed hardware failures.

External-clock last release writes GPIO15 configuration3 rather than restoring the prior pad word. Clock power/force bits express commands, not measured readiness. HFRC2 ratio source now includes explicit numerical/FPSCR comparison profiles. SYSPLL postdivider/min-VCO generation is still an original-code dependency; there is no completed sealed native generator batch on disk in this scan.

## Visibility, preservation and limits

`git check-ignore -v --no-index` found **zero matches for all661 component source files**. Root rules ignore build directories, objects/ELFs and decompiler databases, but do not hide these new sources. No nested component ignore file or global excludes setting was found; `.git/info/exclude` is absent. One registered worktree remains. Seven source files are untracked and four newly added source files are staged; the snapshot lists exact paths. Nothing was staged by this scan.

All **2,316 hash entries in inspected dictionary-form analysis/component seals**, **110 audit inputs** and **four candidate checkpoints** match. Three other manifest formats are explicitly excluded from this seal-verification scope. HEAD remains `36337d9b39ff36d318b0531f2968ca7e0554a7b1`. At capture there were61 staged additions and82 individual untracked files across the repository; the index hash remained unchanged during inspection.

The workflow still records P2 executing, with whole-corpus completion/freeze and complete-source/byte-identical-build gates not run. These offline source helpers are concrete progress, but no complete firmware source build or byte-identical OTA is established. Physical clock settling, scheduler/IRQ behavior and resident-ROM dependencies remain limits. Only this new report/snapshot were written in the checkout; no behavioral tests, generator, production change, commit or device operation ran.

[Exact source delta, hashes, result identities and preservation evidence](snapshot.json).
