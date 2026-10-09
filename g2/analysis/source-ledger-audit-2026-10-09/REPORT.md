# G2 source-ledger audit after codec IRQ closure

The whole source goal is **not exhausted**. The direct codec interrupt chain has
reached its legitimate runtime boundary, while two useful static provider
families remain actionable from official source already present in the working
tree. [The machine-readable ledger](ledger.json) separates resolved,
source-blocked, runtime-only, and actionable entries.

## Resolved or superseded entries

GPIO is not an open source-acquisition gap. Configuration getter/setter, state
write, interrupt status/clear/registration/service, board consumers, and audio
GPIO providers already have stock/source evidence in the 2026-10-05 and
2026-10-08 GPIO reports. Those reports stop correctly before electrical pin,
NVIC, or physical timing claims. Repeating the GPIO frontend would not add
knowledge.

The CMSIS memory-pool lead from the prior dependency index is also superseded:
the 2026-10-09 pool batch recovered constructor, allocation/free, free-list,
semaphore, and heap dependencies through their real failure/handover boundary.
Likewise, codec UART power/configuration and direct receive delivery now have
245 and 112 passing original/source comparisons respectively.

## Official source still worth using

The canonical Apollo510 source is already pinned at Ambiq commit
`5efc0228528a8adce5eae0d226fac85d2551eb3b`. Its `am_hal_uart.c` contains
initialize, power, configure, FIFO, transfer, interrupt-status/clear/service,
and abort/flush implementations. It is the next useful source for the open
blocking/nonblocking TX and completion leads around `0x58E454`, `0x58E4E8`,
and application initializer `0x541A2E`. The source file SHA-256 is
`db0807cbd0ff5df110afde4a8e8561857e2e669529da290289919516ec12799a`.

The same pin already provides `am_hal_info.c`, `am_hal_pwrctrl.c`, and
`am_hal_mcuctrl.c` for the INFO1, MCU-memory, SRAM, and oscillator leads at
`0x47F954`, `0x47F204`, `0x47F46A`, and `0x4809C4`. Static comparison can
recover their exact software error flow. Actual trim contents, readiness, and
physical clock behavior remain supplied inputs.

No new package was downloaded because the useful official code is already
present at the selected commit. Another checkout would duplicate it and would
not resolve the missing private application code, proprietary libraries,
resident ROM, or live runtime state.

## Provenance defect found without changing Git

The index contains 53 gitlinks, while `.gitmodules` declares 52 paths.
`third-party/reference/ambiqhal-audio-5.1.0` is the unmatched gitlink. Its
checkout and gitlink both point to the same `5efc0228` commit as canonical
`third-party/upstream/ambiqhal-apollo510`. This is a registry inconsistency,
not missing source. It was recorded only; repairing `.gitmodules` or removing
the duplicate would mutate shared Git state and is outside this task.

## Remaining boundaries

Application-owned transition producers and logger initialization have no
official upstream package; they remain locked-image decompilation work.
Exact IAR runtime/build inputs, private Ambiq producing checkout, NemaGFX
implementation, EM9305 SDK/controller source, and authenticated resident ROM
remain source-blocked. PendSV/NVIC delivery, initialized scheduler state,
physical UART/GPIO/clock behavior, and real factory calibration are runtime or
device inputs. These categories must not be collapsed into one “source
exhausted” claim.

The next source-ledger batch should bind Apollo510 UART transfer/copy/completion
against locked instructions. In parallel sequence, INFO1/MCU/SRAM/oscillator
providers can close the remaining common-initializer dependencies. Neither
batch can establish physical completion without the runtime inputs above.
