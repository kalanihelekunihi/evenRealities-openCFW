# Native cache startup providers

Locked bootloader SHA256: `f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5`.
Source: `g2/components/bootloader/platform_control/cache_enable.c` and interface `cache_enable.h`.

`41e1e8` enables instruction caching, returning1 without writes when raw `e001e300` bits8/9 are set. Otherwise, if CCR bit17 is clear, it executes DSB/ISB, writes0 to ICIALLU `e000ef50`, repeats DSB/ISB, sets CCR bit17, and repeats DSB/ISB. Already enabled returns0 without writes.

`41e266` checks the same guard, then packs three configuration bytes at `20000078` into `e001e004`. When CCR bit16 is clear it selects cache0, executes DSB, invalidates every modeled set/way through `e000ef60`, executes DSB, sets CCR bit16 and executes DSB/ISB. The set count comes from CCSIDR bits27:13 and way count from bits12:3; both loops descend through zero. Operands preserve the stock mask `((set<<5)&3fe0)|(way<<30)`, including aliasing for larger synthetic geometries. If the low byte of its argument is nonzero, it independently selects cache0 and performs a clean pass via `e000ef6c`, followed by DSB/ISB. This pass also happens when the cache was already enabled.

Direct original-instruction versus compiled-source validation passes1,440 cases /296 distinct original instruction bytes. It compares return value, ordered writes and barriers, SP and all callee-saved registers across guard bits, enabled states, descriptor geometries, packed-byte edge values and low-byte argument truncation. No original executable bytes are loaded on the source side. Synthetic SCB/MMIO does not establish physical cache coherence or timing.

Reproduce: `make -C g2/components/bootloader/platform_control cache-enable-compatible`. This compiles `cache_enable.c` with ARM Clang Cortex-M33, freestanding C11 `-O2`, link with `cache_enable.ld`, then run `verify_cache_enable.py --elf <elf> --output <receipt>` using the installed OpenCFW Python environment. The shared source-image Makefile separately builds and links these providers. Their new segment contains compiled source, not stock opcode data; the ELF loader still enforces a64KiB maximum per load segment.
