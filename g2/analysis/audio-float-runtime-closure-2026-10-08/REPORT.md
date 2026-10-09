# Native binary32 math-runtime providers

Four reconstructed functions pass **13,920 direct original-instruction comparisons**: floor,round,ceil andfmod. The same final ELF passes **2,530 reused SYSPLL generator comparisons** and **3,403 reused clock composition cases**. Total19,853 describes this artifact, not distinct whole-firmware coverage. ELF SHA256 `85e69f0005a7b1bf5e0a400e9849777a1deeba001f178c85aafb39d9ed71739d`. [Readable C](../../components/audio/float_runtime_offline/math.c), [interface](../../components/audio/float_runtime_offline/math.h), [pseudocode](pseudocode.md), [exact build validation](exact-build-validation.json), [addresses/hash/disassembly](function-bindings.json).

## The source opportunity and what was recovered

Pinned Ambiq SDK supplies the SYSPLL caller algorithms but no implementation for these math providers. Bounded repository source lookup found no matching standalone newlib/picolibc/provider source. The actual wrappers and integer cores are small enough to reconstruct defensibly from authenticated bytes. This is bespoke recovered C, **not a claimed pristine public-source match or unique runtime-version attribution**. Weak historical link-order labels do not establish a first-party implementation.

Floor0x43A5A0/core0x43A5B0,round0x577D08/core0x577D18 andceil0x577D40/core0x577D50 manipulate exponent/significand bits. They preserve signed zero and nonfinite input payload bits; no floating arithmetic orFPSCR flag update occurs in these routines. Round handles half cases away from zero. This remains true for signalingNaN and default-NaN/flush-to-zero modes because these are bit moves, notFP arithmetic.

Fmod0x577C3C/core0x577C4C performs normalized integer remainder, reducing exponent gaps in8-bit chunks via unsigned division/remainder, then normalizes the result. It handles subnormal operands without relying on host libm or theFPSCR rounding mode. Exact zero retains numerator sign; smaller finite magnitude returns the numerator. A finite numerator modulo infinity also returns numerator; this path was first reconstructed incorrectly, rejected by direct tests, corrected and all final suites rerun.

## Domain behavior and errno

Invalid results use bit pattern0x7FFFFFFF. Finite numerator modulo signed zero stores **33** to stock errno word **0x20074F14** through original domain-error veneer0x577C34→0x439CA4 in the stock guest; native source reproduces that write directly. Infinite/NaN numerator orNaN denominator returns canonicalNaN without that errno write. These routines do **not** setFPSCR invalid themselves. Do not assume host libc’s errno/exception/NaN behavior is identical. No thread-local errno or scheduler behavior is inferred from this static global accessor.

Tests compare exact output bits, fullFPSCR, errno word and ordered writes, and restoredSP. They cover both signs/all256 exponents with representative mantissas, subnormals/zeros/infinities/quiet and signalingNaNs, all rounding modes,FZ/DN/combined mode, preexisting cumulative flags, pairwise edge cases and800 seeded randomfmod pairs. Native routines call neither original math code nor host math answers; no return stubs or opcode arrays are used.

## Generator and clock implications

The previously sealed SYSPLL source now resolves all four math calls to native providers. Exact numerical outputs, provider call arguments, fullFPSCR and partially written failure configs continue matching originals. In particular, unchecked base generatorNaN input can still return0 with zero divider/feedback and invalid-operation flag raised later byVFP conversion. That is preserved malformed behavior, not a supported app/CFW configuration; validate finite positive frequencies/parameters.

Low-speed/public clock dispatch and oscillator remain native in this combined artifact. Delay/status waits and IRQ helper still execute original code here; their actual pinned-source closure is next. Source-only math/clock software behavior under these fixtures does not establish physical PLL frequency/lock, real scheduling/IRQ ordering, completeM55 behavior or a complete byte-identical firmware build.

Prior seals,110 inputs,four checkpoints and concurrent staging are preserved. No commits, production changes, shared gates or device writes. [Preservation](preservation.json). [Source assessment and remaining concrete leads](source-assessment.json).
