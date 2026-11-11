# R1 software-TWI delay arithmetic review

REA/Ghidra 12.1.4 checked the two busy-delay wrappers at `0x7A6DC` and
`0x7A6EC` and their subtract-three kernels at `0x9A640` and `0x9A650`
against the locked R1 application. The analysis-only ELF contains the complete
unchanged application bytes at their original load address, with explicit
Thumb seeds for these four small functions. The historical function CSV
omits these entries; this review does not silently add them to accepted
pseudocode coverage.

Each wrapper returns immediately for zero input. Otherwise it shifts the
32-bit input left by six and tail-calls its kernel. Each kernel subtracts
three at least once and repeats while the subtraction's unsigned-HI condition
holds. Thus, for nonzero input `x`, let `n = (x << 6) mod 2^32`: the iteration
count is `max(1, ceil(n / 3))`. A nonzero input that shifts to zero still runs
one iteration. The existing C provider in `software-twi/sdk_gpio.c` preserves
this arithmetic, including wraparound; no body change was required.

Direct Unicorn execution compared both stock wrappers with the actual
compiled C provider for 93 inputs each, covering zero, 1 through 64, and
large inputs with small effective shifted values. All 186 comparisons passed
for loop counts and observed residual r0. Stack-pointer and r4 preservation
also passed. Residual r0 is an observed machine detail, not a promised return
value of the C `void` API. Large effective iteration counts were not executed
exhaustively.

This does **not** establish timing equivalence. Stock keeps its countdown in
r0 and uses `subs; bhi`; the configured Clang C provider additionally reads
and writes its volatile stack counter on every iteration. Replacing that
counter with an ordinary variable could let the compiler eliminate the loop.
The recovered name and input unit do not establish a calibrated microsecond
delay. Exact compiler output and physical SCL/SDA timing remain necessary
before treating this provider as timing-correct hardware support.

## Distinct i2c_5 callback repaired

The two no-countdown callbacks differ at the instruction level: `0x7081C`
is `bx lr`, whereas `0x54AF0` is five NOPs followed by `bx lr`. REA emits the
same empty pseudocode for both; assembly and the observed 2-byte versus
12-byte bodies preserve the distinction. The old C combined both as an empty
function and discarded the five NOPs.

The existing provider now exposes `r1_twi_i2c5_delay_noop` using five Nordic
CMSIS `__NOP()` intrinsics, and the `i2c_5` record uses that distinct callback.
The configured Clang object emits exactly the stock 12 bytes. The `i2c_4`
callback remains the direct-return provider. Both compiled record relocations
were checked at offset +0x28 in their respective 112-byte records. Another
186 execution comparisons cover these two callbacks for the same 93 inputs.
This repairs the lost instruction slots without claiming calibrated wire
timing or qualifying the enclosing GPIO/delay translation unit.

The complete R1 rebuild still compiles all 560 units and composes both
payloads. Application imports rise from 253 to 254 solely because the corrected
record now names this distinct excluded provider; bootloader imports remain
34. The new import has a compiled source definition, but remains explicit
until that provider is admitted to composition.

The delay provider now lives in `sdk_delay.c` and remains excluded from normal
composition. The six GPIO wrappers separately passed the
[MMIO review](twi-gpio-review.md) and now participate in relocatable composition.
Compact REA observations, hashes and execution
results are in [twi-delay-review.json](twi-delay-review.json); probes and the
neutral REA snapshot remain under ignored `build/goal-r1-twi-delay/`.

The subsequent [leaf closure](twi-leaf-closure-review.md) separates the
unchanged busy countdown from the two stock-identical leaf callbacks. The
leaves now participate in composition; only the busy provider stays excluded.
