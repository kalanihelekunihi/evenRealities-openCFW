# Bootloader queue source

`queue_wrappers.c/h` are preserved source candidates from the independently
owned `g2/analysis/bootloader-completion-2026-10-06/inventory-worker/queue-wrappers/`
batch, relocated here for reusable component integration. Root-path and build
output paths in the copied verifier/Makefile were adjusted; the worker originals
remain intact. Original addresses and limits are in that batch's `evidence.md`.

Current component-local Cortex-M55 `real-runtime` build and original/source
comparison pass **45 cases, 450 distinct original instruction bytes**. Kernel
providers remain synthetic; runtime-mode query executes source. Nonzero IPSR is statically
recovered but not injected. Timeout units and actual scheduling remain unknown.

`filesystem` target `arm-queue-task-library` links these wrappers into the real
source DFU → littlefs/TLSF → update → architectural handoff chain. Its fixture
`verify_arm.py --real-allocator --real-task --real-queue` returns deterministic
messages at the kernel receive boundary `0x41A114`, rather than intercepting
the CMSIS wrapper at `0x416920`. The later `arm-queue-runtime-task-library`
profile also executes `runtime_mode.c`, replacing the `0x418B56` provider.
That query reads `0x20027150`: zero returns 1; otherwise `0x2002716C` zero
returns 2, nonzero returns 0. These remain raw state words, without claiming
semantic kernel ownership. The enlarged differential suite passes 45 cases /
450 original bytes with only kernel providers stubbed.

The final integration separately calls the wrapper on an empty queue, checks
resource error `-3` and unchanged destination, then receives command 1 within
the task and reaches handoff. That proves the wrapper paths in the linked source
profile, without claiming a source-defined RTOS kernel or an empty-drain path
after the nonreturning successful handoff.

Locked original bootloader SHA-256:
`f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5`.
No firmware flashing, hardware queue, scheduling or byte-equality proof.
