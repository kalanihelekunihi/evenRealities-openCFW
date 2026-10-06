# NOR read command source

Recovered from locked bootloader `0x420F70` (SHA-256
`f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5`).
Owned worker originals, disassembly and evidence remain in
`g2/analysis/bootloader-completion-2026-10-06/inventory-worker/nor-read/`.
This reusable copy adjusts verifier/build paths only. Build with `-fshort-enums`
for the recovered 24-byte PIO ABI; compile-time layout assertions check it.

The function requires an active handle at RAM `0x200270DC`, a nonnull buffer,
and nonzero length, otherwise status 6. It requires start address below
`0x02000000`, otherwise status 5. It then runs four setup/teardown helpers
around one RX PIO command: opcode `0x6C`, four-byte addressing, turnaround 1,
unchanged address/buffer/count, and timeout literal 1,000,000. The pinned public
Apollo510 HAL header documents that timeout parameter as microseconds; actual
stock lower-HAL timing has not been executed. No alignment, end-address,
length-overflow or chunking guard was added to the source.

Component-local Cortex-M55 original/source comparison: **PASS 10 cases / 174
original instruction bytes**, including a crossing-the-end request accepted by
the wrapper and unchanged lower-HAL failure status. That acceptance is wrapper
behavior, not proof a physical out-of-range read succeeds.

`filesystem` target `arm-nor-queue-runtime-task-library` executes this command
source inside the DFU/littlefs/TLSF/update/handoff integration. Fixture flag
`--real-nor-read` observes complete command bytes at `0x4262E0` and copies data
from an offline NOR byte model there. The local read wrapper is no longer a
returning stub. Setup/teardown helpers, lower HAL, physical program/erase and
kernel scheduling remain explicit synthetic boundaries.
