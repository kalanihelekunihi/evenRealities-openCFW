# Continued source work after SDK setup

The original **18 and 20** counts denote two fully passing integration suites,
not 18 successes out of 20 attempts. Subsequent queue source integration added
an explicit empty-queue check; the current combined suite passes **21 calls**.

## Current concrete deliverables

| Component | Source / current saved result | Proven scope |
|---|---|---|
| Queue + runtime-state query | `g2/components/bootloader/queue/`; `queue-runtime/comparison-first.json` | 45 original/source cases, 450 stock instruction bytes; independent rerun passed. Runtime query `0x418B56` now source-defined, kernel calls synthetic. |
| NOR read command | `g2/components/bootloader/nor_read/`; `nor-read-components/comparison-first.json` | 10 cases, 174 stock bytes; exact command layout, helper order, argument/status behavior. Local setup and lower HAL synthetic. |
| MRAM control + ROM bridge + critical save | `g2/components/bootloader/platform_control/`; `platform-control-critical-rom-compatible/comparison-first.json` | 496 cases, 308 stock bytes; real `MRS PRIMASK; CPSID I; BX LR` source replaces critical-save stub. ROM/clock/platform callbacks remain synthetic. |
| Linked source chain | `filesystem` target `arm-nor-queue-runtime-task-library`; `nor-queue-runtime-task-integrated-compatible/integration-first.json` | 21 passing calls; real NOR-command source, queue/runtime, DFU task, littlefs, TLSF, update and handoff. 122 lower PIO reads observed through synthetic NOR, two kernel receive calls. |

Result paths above are relative to ignored `g2/build/bootloader-completion/`.
Old snapshots remain preserved and superseded; do not add their case/byte counts
together. The current combined result authenticates current source hashes.
The integration installs a 9,001-byte logical image into a synthetic storage
region, then uses prepopulated application-vector fixtures to observe handoff;
it does not establish that the programmed bytes supply actual working vectors.

The NOR wrapper checks only its start address, not request end. It submits one
24-byte RX PIO command (`0x6C`, turnaround 1), without chunking or alignment
guard. Its timeout literal is 1,000,000; the matched public HAL declaration calls
that parameter microseconds, while stock lower-HAL timing is still untested.
The littlefs callback maps any nonzero read status to `LFS_ERR_IO`.

## Exact remaining component boundaries

This is partial implementation, not bootloader completion. The baseline static
catalogue has 903 candidate functions, 54 failed decompilations and 245 gaps /
28,167 uncatalogued bytes. Those are baseline evidence counts, not a freshly
reconciled remaining-work total; two context helpers and further source leaves
were recovered afterward. Do not interpret gaps as all executable code.

Still required: reset/vector-table producer and relocation closure; constructor
tables/calls; full clocks/power/peripheral initialization; boot-specific RTOS
kernel/scheduler/IRQ behavior; NOR program/erase and read setup/teardown plus
full MSPI transfer implementation; logger/runtime/data/configuration closure;
all residual omitted code and noncode classification. Exact source toolchain,
configuration, linker/compression/resource inputs and whole-payload byte match
are separate from behavioral tests. ROM programming entry `0x0200FF21` and
external SBL are not contained in this OTA payload; do not claim their source
from that image or let their absence stop recoverable local source work.

Next source batch: recover the NOR read setup/teardown or MSPI blocking transfer
provider that still bounds the new command source, alongside NOR program/erase
siblings. These are now precise callable interfaces rather than broad unknowns.
No proprietary SDK binary reverse engineering is needed to continue the
already permitted Apollo510 source and firmware-instruction work.

## Installation status at 15:16 UTC

The relevant completed Downloads inventory still contains the same supplied
SDKs/tool packages. No completed `cxarm-10.10.2.27058.deb` or new GX8002/MetaWare
package appeared in the targeted refresh. C-SKY v3.10.15 / GCC 6.3.0 is now
locally installed/extracted under ignored `local-vendor/toolchains` and executes
in the existing Ubuntu 24.04 amd64 container. A freestanding `-mcpu=ck804`
compilation succeeded and readelf identified ELF32 little-endian CSKY.
Full GX8002 device SDK and stock compiler flags are still missing.

IAR Linux installation awaits the compiler DEB, applicable agreement decision
and valid subscription; activation is a separate secure handoff. EM agreement
decision is pending. Exact links, local files, restrictions and the absence of
prior-acceptance evidence are in `third-party/downloaded/AGREEMENTS.md` and the
independent `review-worker/downloaded-tools/acceptance-evidence.md`. Existing
acceptance, if confirmed, should be used rather than requested twice.
