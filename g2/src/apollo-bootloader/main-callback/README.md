# Initialized main callback

This component reconstructs the bounded callback at `0x42E39C`, which the
scatter table publishes as the Thumb pointer `0x42E39D` in RAM at
`0x200004F4`. The callback passes entry `0x42E2F9`, argument `0`, and the
36-byte manager attribute record at `0x433024` to runtime helper `0x4160FE`.
It stores the returned word at `0x200004FC` (`0x200004F4 + 8`), then calls
`0x4160B0` for a nonzero result. A zero result takes the observed priority
helper `0x41B2F8` and invalid word store to `0xFFFFFFFF`.

`make verify-compatible` compares the callback in isolation. The
`verify-startup-integrated-compatible` target also runs source startup through
the compiled scatter table and helpers, main init, the actual published
callback pointer, and terminal spin. Its source callback text is linked at
`0x42E39C`; the test does not replace the initialized pointer. Both targets
use Cortex-M4-compatible ELFs for offline Unicorn emulation.

Runtime helpers, allocator/NOR/filesystem/log providers, and the manager body
at `0x42E2F9` remain external cuts. The three compressed startup payload spans
remain authenticated input fixtures. These comparisons establish neither
hardware behavior, complete source coverage, nor byte identity with the locked
firmware.
