# OpenCFW rescan — 2026-10-08 05:33 UTC

Compared with [the 04:27 scan](../rescan-2026-10-08T042729Z/REPORT.md). Read-only inspection of existing work; only this scan directory was written. No generators, builds, tests, commits, index changes or devices were invoked. Counts and input hashes were freshly checked; test results below are existing receipts, not new test runs. Concurrent campaigns may advance after capture.

## Source and ignore comparison

The same canonical scope, `g2/components/bootloader` and `g2/components/foundation`, still contains **475 C/header/assembly files**: **0 added, 0 modified, 0 removed** since 04:27. **384 are tracked/indexed, 91 untracked, 0 ignored**. This is a deliberately narrow inventory, not a whole-firmware completeness measure.

All **110 locked audit inputs** and **196 sealed analysis files** across eight delivered batches match their recorded SHA-256 values. The four checkpoints recorded in the previous scan also still match their accepted hashes. The integrated-status report currently opens with the older `129a` checkpoint; that heading alone should not override the newer separately recorded `fe6b` platform-log checkpoint. Neither a larger checkpoint nor firmware integration of the new touch analysis is inferred.

New readable source exists in standalone analysis rather than the canonical component directories. `git check-ignore -v` reports no ignore rule for `touch-history-closure-2026-10-08/history.c` or `touch-commands-2026-10-08/app_event.c`. `.gitignore:15` hides `g2/build/` outputs; `*.elf` also hides loose linked artifacts. There is no configured global excludes file, no matching nested ignore in these areas, and Git lists one worktree. A tracked-only view omits the untracked analysis C. No blanket ignore change is needed.

At capture Git has 6,205 added/indexed paths, 25 indexed modifications, four paths with both indexed additions and working-copy changes, and 2,785 untracked files. These counts include documents, receipts and other campaigns; they are not source or firmware progress percentages.

## Concrete understanding added since the prior scan

- [Touch commands](../touch-commands-2026-10-08/REPORT.md): independent C for all nine command-table branches and deferred configuration dispatch. Command7 accepts a nonzero little-endian parameter and prepares `07 00 17`; the acknowledgement precedes deferred persistence. Recorded 13,440 bounded command cases and composed IRQ/deferred suites have explicit limits.
- [Case STOP mode](../case-stop-mode-2026-10-08/REPORT.md) and [voltage polling](../case-clock-poll-2026-10-08/REPORT.md): recover STOP0/STOP1 behavior and distinguish VOSF voltage readiness from historical clock labels. Wake/time responses remain controlled.
- [EEPROM direction](../touch-eeprom-dispatch-2026-10-08/REPORT.md): historical Read label at `0x8aac` actually dispatches writes; true read dispatcher is `0x8a78`.
- [Flash providers](../touch-flash-provider-2026-10-08/REPORT.md): installed row adapters discard flash-driver errors. They synchronously copy borrowed input before SROM requests; physical SROM execution is outside the inspected OTA and modeled offline.
- [Extended rows](../touch-extended-rows-2026-10-08/REPORT.md): sequence/address/length/checksum layout and wear-row advance/wrap recovered.
- New [history C](../touch-history-closure-2026-10-08/history.c) replaces the three remaining integrity/history test cuts. Existing receipts record **1,148 helper**, **1,728 full extended-write**, and **800 complete command7** native/original comparisons, with no function-entry cuts in those suites. They share ELF SHA `216bca061ebbfb01e4e112149ec0d7dfa457e1e87cb311a12b6800aa5ed9971c`. Flash response and torn-write effects remain synthetic; contexts and input domains are bounded. This directory has results and C but no completed report/manifest at capture.

The recovered history scan compares sequence numbers as unsigned integers: `0xffffffff` outranks small wrapped values. Valid redundant history returns status `0x093e0004`; missing/invalid history can return `0x093e0001`. A successful synthetic flash request does not imply every higher-level history operation succeeds.

Most useful app finding: **command7 ACK and deferred status do not establish durable persistence**. Fifty recorded stock readback fixtures demonstrate that injected load/program failures can leave zero configuration bytes even with accepted ACK and deferred status zero. This follows actual error-discarding instructions under constructed flash responses, not a measured hardware failure rate. Commands6/8 read RAM configuration and cannot certify flash durability. The 50-case readback suite executes stock read bodies only; it does not establish native-source equivalence for the 620-byte extended read function.

## Remaining work

A worthwhile next closure is independent reconstruction of the true extended read path and comparison against original instructions using the same history fixtures. Actual EEPROM configuration/captured storage and a resident SROM implementation or physical traces are needed to assess durable device behavior. These standalone results do not prove integrated firmware execution, whole-image source completeness or byte equality with the official OTA.
