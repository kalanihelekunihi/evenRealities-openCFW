# OpenCFW rescan — 2026-10-08 14:10 UTC

Compared with the 12:57 UTC snapshot, **nine C/header files were added**, bringing the same `g2/components` source inventory from **537 to 546**. No prior source hash changed and no prior source file was removed. There are 532 files in the Git index and 14 untracked source files; none of the 546 is ignored. Index membership does not prove committed content or equality between index and disk.

## New source and knowledge

| New component | Added files | Existing validation evidence |
| --- | --- | --- |
| LP launch/filter lifecycle | `touch/lp_scan_offline/scan.c,h` | 1,952 PASS original/source cases; filter parameters and launch/reuse paths |
| Application LP sleep/wake phase | `touch/lp_application_offline/application.c,h` | 120 PASS cases; 44 completed phases, 52 bounded busy waits, 20 synthetic ISR deliveries |
| Active timer and scan lifecycle | `touch/active_timer_offline/active.c,timer.c,timer.h` | 1,160 PASS cases; timer setter, active launch, LP-to-active sequences and budget tail |
| ILO compensation and measurement | `touch/ilo_compensation_offline/ilo.c,h` | 1,489 PASS three-way cases recorded; **unsealed**, with no report/DELIVERABLES manifest yet at this scan |

The previously present LP history work now has a sealed report and records **766 PASS cases**, versus the prior snapshot's unsealed 594. Those include tests of a newly designed offline decoder, so they are not all stock-equivalence tests. Public-source dispatcher attribution adds six PASS comparisons and 12 exact stock bytes. The completed application batch records exact public-source reproduction of the 20-byte LP wrapper and 104-byte DeepSleep function. Its report and the active-timer report place cumulative selected public-source attribution at **438 distinct bytes**; that does not establish whole-image equality. The unsealed ILO results make no additional exact-byte attribution claim.

Concrete findings relevant to firmware changes: LP launch enables baseline/signal detection but leaves the raw-IIR enable bit clear; an encoded raw coefficient alone does not enable filtering. The application discards LP launch errors before its busy/sleep loop. Active interval requests of 7773 and 31211 are SDK-documented microseconds, while budgets 640/160 are software counts, not established elapsed milliseconds. ILO compensation retries all nonzero measurement statuses without an explicit timeout in the selected body, then refreshes active/LP timer caches and the selected live timer. Synthetic readiness/count inputs do not establish oscillator frequency, physical cadence, or hardware failure.

## Preservation and visibility

All **656 sealed manifest entries**, **110 audit inputs**, and **four bootloader candidate checkpoints** still match their recorded hashes. HEAD remains `36ff5930a4e832156f9ee3111e83480756ebef37`. Existing staged and unstaged work was preserved. This scan performed no generator execution, suite reruns, commits or index changes; PASS counts are read from existing results and reports.

`git check-ignore -v --no-index` finds no matching rule for any of the nine added source files. The scratch probe `g2/build/probe.elf` remains excluded by `.gitignore:15:build/`. There are no nested component `.gitignore` files, `.git/info/exclude` is absent, `core.excludesFile` is unset, and one worktree is registered. **Ignore rules are not concealing this new source work.**

## Remaining boundary and navigation

These are bounded offline reconstructions and helpers, not a complete source-built firmware image. Physical IRQ/wake delivery, analog behavior, generated history allocation, full power-management callback/prevention-lock lifecycle and whole-image source/byte equality remain unproven. The immediate ILO batch still needs its report/provenance/sealing; its PASS receipt is usable with the explicit synthetic and dependency limits in `results.json`.

- [LP history](../touch-lp-history-closure-2026-10-08/REPORT.md)
- [LP filter/launch](../touch-lp-filter-closure-2026-10-08/REPORT.md)
- [Application sleep/wake](../touch-lp-application-closure-2026-10-08/REPORT.md)
- [Active timer/launch](../touch-active-timer-closure-2026-10-08/REPORT.md)
- [ILO results, unsealed](../touch-ilo-compensation-closure-2026-10-08/results.json)
- [Exact source hashes, Git visibility and preservation evidence](snapshot.json)
