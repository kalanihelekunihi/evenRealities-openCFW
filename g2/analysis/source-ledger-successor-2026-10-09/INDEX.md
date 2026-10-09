# Corrected G2 source-ledger successor

This additive index supersedes stale pending rows in
`source-ledger-audit-2026-10-09`; prior sealed evidence remains unchanged.

| Family | Current status |
|---|---|
| UART transfer/copy/completion/HAL initialization | Already resolved by `audio-uart-tx-ownership-2026-10-09`: 665 bounded cases, including synchronous-copy/borrow lifetime and initialized-channel composition. |
| UART first-party worker wrapper `0x541A2E` | Newly resolved by `audio-uart-instance-closure-2026-10-09`: 16 comparisons; exact static control block, stack and priority recovered. Created-task execution remains outside scope. |
| INFO1, MCU memory, SRAM, oscillator | Already resolved by `audio-info-memory-providers-2026-10-08`: 1,182 comparisons. Factory contents and physical readiness remain supplied/runtime inputs. |
| PCM2.2 transition producers 7/21 and all table entries | Already resolved by `audio-transition-producers-closure-2026-10-08`: all 27 table entries and 12,019 comparisons. Earlier transition-ledger pending rows were stale. |
| GPIO configuration/state/IRQ | Already source-backed by the October 5/8 GPIO batches; electrical/NVIC behavior remains external. |
| Logger flag `0x20074F4E` | Initial zero is proven by the first scatter clear. The conditional disable consumer is recovered. No later writer was established by exact/near literal searches; computed writes and live binding remain unproved. |

## Remaining useful static leads

1. Pinned PCM0.7/2.0/2.1 variant bodies and their actual CPU power-mode
   wrappers/callers remain distinct from the completed PCM2.2 family.
2. UART RX `0x58E618`, callback `0x5415E6`, and channel receive helper
   `0x55E4EC` remain useful for caller storage and application stream ownership;
   the codec channel-3 IRQ subset is resolved, not the entire UART RX family.
3. Logger flag initialization beyond proven scatter-zero now needs a computed
   write/data-flow result or runtime startup trace. Repeating literal scans
   cannot establish absence.

## Boundaries

Private IAR/Ambiq producing inputs, NemaGFX implementation, EM9305 controller
source, and resident ROM remain source-blocked. Exception delivery, live task
selection, physical UART/GPIO/clock behavior, authentic calibration, and real
concurrency remain runtime/device-only. Therefore the whole source goal is
**not exhausted**, but the originally queued UART TX, INFO/memory/oscillator,
and PCM2.2 rows are exhausted within their documented static bounds.

The unmatched `third-party/reference/ambiqhal-audio-5.1.0` gitlink remains
recorded and untouched. No `.gitmodules`, index, Git configuration, production
firmware, or device state was changed.
