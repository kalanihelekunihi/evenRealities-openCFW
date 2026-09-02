# G2 bootloader platform-finalizer source closure

The authenticated entry `[0x00430502,0x00430610)` is a 270-byte eight-slot
hardware-context and event-service finalizer. It creates missing per-slot event
objects, binds two callbacks, applies and enables active contexts, performs the
bounded retry step, enables interrupt 10, and creates the global event-flags
object. Allocation or callback failure returns status one; global event-object
failure is logged. The sole caller is `0x004301EC`.

`runtime_platform_finish_430502.c` is first-party MIT clean-room source. Apple
clang 21 and Homebrew clang 22 reproduce all bytes under twelve strict calls.
Relocated SHA-256 is
`f92c35acae4e7f10f79008020f00bb4607f39ff6b09545fbbbc93348b6873195`;
unrelocated SHA-256 is
`bad372fa5e2a442fcbf1d4e7a767aed113b369aeeaffb8d5cb4e3fd107da4b99`.
The Apollo-main analogue at `0x0050423A` shares 196/270 bytes. Seven portable
tests cover empty and multi-slot success, object and callback failures, global
event failure, status propagation, and invalid input.

No hardware operation occurred. Live SRAM, MMIO, interrupt/concurrency,
peripheral, reset, and cold-boot qualification is blocked by unavailable
physical evidence. Firmware-wide completeness is not claimed.
