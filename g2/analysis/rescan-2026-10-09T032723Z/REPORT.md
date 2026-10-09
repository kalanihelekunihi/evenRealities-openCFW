# OpenCFW change scan — 2026-10-09 03:27 UTC

Compared with the [02:32 UTC scan](../rescan-2026-10-09T023256Z/REPORT.md), component C/header/assembly inventory grew **721 → 735: 14 added, 1 modified, 0 removed**. **723 indexed, 12 untracked; zero ignored source files**. Counts describe files, not unique functions or complete firmware. The modified file is `g2/components/audio/uart_power_config_offline/compat.h`; its previous hash and current hash are retained in the two snapshots. This scan does not classify that change as regression merely from a hash difference.

## Concrete new understanding

| Evidence batch | Recorded validation | Result and practical meaning |
| --- | --- | --- |
| [Grouped UART power](../audio-uart-group-power-2026-10-09/REPORT.md) | 240 PASS | Shared status mask is not an individual UART acknowledgement. Direct traces correct an earlier decompiler inference: both stock and native interrupt-clear paths write IEC then read MIS. |
| [UART power composition](../audio-uart-power-composition-2026-10-09/REPORT.md) | 408 + 16 PASS | Recovered callback registration and enclosing enable/disable behavior; failed polls do not imply rollback. |
| [Newer callback](../audio-uart-newer-callback-composition-2026-10-09/REPORT.md) and [planner](../audio-uart-newer-planner-composition-2026-10-09/REPORT.md) | 96 and 116 PASS | Reused source reaches selected revision-dependent planners and PCM2.2 apply/selector; synthetic calibration remains distinct from measured hardware. |
| [RX consumer](../audio-uart-rx-consumer-2026-10-09/REPORT.md) | 391 + 216 + 4 PASS | Stream receive copies caller-owned bytes; UART3 ring keeps the newest 63 bytes under synthetic overflow. UART3 is GX8002 codec control/DFU, not temple sync. |
| [ISR notifier](../audio-uart-rx-notifier-2026-10-09/REPORT.md) | 1,440 + 36 PASS | Waiting task moves to ready or pending-ready lists. Yield flag is established; actual context switching is not. |
| [Codec drain](../audio-codec-uart-rx-drain-2026-10-09/REPORT.md) | 320 PASS | Codec read returns drained byte count and independently copies staging-ring data. |
| [Codec deadline](../audio-codec-uart-deadline-2026-10-09/REPORT.md) | 112 PASS | One-byte helper checks deadline before reading; timeout zero rejects even staged data. Near-wrap arithmetic is bounded software evidence, not a measured hardware hang. |
| [Transition composition](../audio-uart-transition-provider-composition-2026-10-09/REPORT.md) | 32 cases, **DIFFERENCES** | 24 match complete access traces; eight expose an extra source timer-status read. All 32 match ordered writes/state/provider arguments up to the boundary. Eight complete; 24 stop before delay provider. |

These are recorded author validations inspected here, **not rerun tests or independent corpus review**. Passing case counts include bounded provider cuts and synthetic fixtures. Existing transition bodies were reused; composition is not new recovery of all those functions. The extra timer read needs an additive corrected reconstruction and strict access-trace validation before stronger equivalence claims. Codec response framing/CRC and actual scheduler handover remain concrete gaps.

## Visibility and preservation

`.gitignore` remains unchanged; `git check-ignore -v` matches none of the 735 component sources. No nested component ignores or configured global excludes were found; `.git/info/exclude` remains absent. The index now includes 69 more source files than the prior scan (654 → 723), so much prior untracked work has become indexed. This does not establish that it was committed. HEAD remains `36337d9b39ff36d318b0531f2968ca7e0554a7b1`.

Verified **2,826 dictionary-form sealed manifest entries: zero mismatches**, all **110 audit inputs unchanged**, and all **four retained checkpoints unchanged**. The index changed since the previous scan through concurrent work, but its hash stayed unchanged throughout this scan. No restore/reset/staging was performed. Non-dictionary manifest formats are explicitly excluded from this count.

Workflow remains **P2_EXECUTING**; completion, freeze, source completeness and identical-build gates remain not_run. Useful source-backed knowledge increased, but there is no complete source-built firmware claim.

[Full inventory delta, result statuses, Git visibility and preservation evidence](snapshot.json). Only this new scan directory was written; existing campaign, sources and sealed history were preserved.
