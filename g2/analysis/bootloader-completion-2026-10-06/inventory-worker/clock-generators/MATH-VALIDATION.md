# Native PLL math and generator validation

Resource hold released; drafts compiled and compared against original instructions. Corrected candidate SHA-256 **f3ca176e492a1770ee1838bdd990e6519e3b435ca75d8c44d690233b11087ade**. Direct receipts are under `../../integrated-status/clock-generators-f3ca/`: `math.json` **4311 PASS**, `generators.json` **688 PASS**, `native-config.json` **48 PASS**. These are separate suites with overlapping paths, not unique-function counts. All seven integration cases now PASS; inputs/objects and frozen copies reconcile. Candidate-specific alignment/manifest/affected regressions PASS, so f3ca176e is promoted; e1049dc3 remains preserved.

The math suite runs native stock floor/round/ceil/fmod/GCD/integer/fraction/VCO/minimum-VCO/selector and source ELF implementations. No child answer stubs or stock executable fallback are used in the source machine. A15 math tests compare result bits, selected output bytes, domain word and FPSCR exception bits0x9f; compiler-dependent final comparison NZCV is excluded. CortexM33 class5/6 supplement activates FP and executes original copy/config/generators, retaining only identical request/release side-effect cuts. Synthetic SRAM/MMIO and FPSCR initially0; other rounding modes and hardware are not certified.

| Native family | Cases |
|---|---:|
| floor, round, ceil | 256 each |
| fmod | 2560 |
| GCD, integer, fraction | 173 each |
| VCO | 176 |
| minimum-VCO | 192 |
| outer PLL selector | 96 |

Raw math cases include signedzero, subnormals, +/-0.5 boundaries, large exponents, random bitpatterns, infinities and quiet/signaling NaNs. Upper-layer cases include zero/negative/NaN/infinity inputs, NULL VCO output, 60/240/960MHz boundaries and integer/fraction fallback. Valid source behavior is defined by the observed stock contract, not host `libm` answers.

Eight math families account1122 original body bytes;1118 visited. The four unvisited bytes are integer-mode rejection at426e94/426e96 after feedback-range checking. They remain explicitly uncovered, not declared dead. All642 HF2/minimum-VCO/selection body bytes are visited in the bounded generator suite; its PLL children are cut, whereas math suite and M33 supplement run the native descendants. Thus1760/1764 body bytes have direct observed evidence across these families; this is component coverage, not whole-firmware completion. Error-store helper instructions are additional evidence outside that body accounting.

## Newly established remainder behavior

`clock_pll_mod.c` reconstructs exact binary32 remainder with integer mantissa/exponent operations, including subnormal normalization and signedzero. Finite numerator with zero divisor stores33 at **20027194** and returns canonical positive NaN bits **7fffffff**. Infinity/NaN numerator also canonicalizes to7fffffff but does not take that finite/zero domain store. NaN divisor canonicalizes; infinite divisor with finite numerator returns the numerator. No allocation or scheduler ownership is involved. Exceptional behavior is tested against the actual stock integer remainder body and its actual error-store path; no errno answer stub.

GCD performs at most16 nonfused floor/remainder iterations; exhausted search returns-1. Integer PLL requires divider1..63 and feedback4..960. Fractional mode requires divider<=63 and integer feedback10..96; fractional feedback is rounded remainder*2^24 and is not separately carry-normalized by these bodies. VCO first tries integer, then fractional; success writes only offsets1,2,3,6,8. Descriptor reference and post-dividers remain caller-managed at this level.

## Concrete stock configuration examples

At reference **12MHz**, native caller comparisons produce:

| Requested clock | HF2 Q15 word (shift2) | PLL descriptor0..11 |
|---|---|---|
| 196.608MHz | 0020c49b | 0001000102012000c09bc400 |
| 250MHz | 0029aaaa | 0001010601017d0000000000 |

The196.608MHz PLL candidate selects high VCO, fractional mode, reference divider1, post-dividers2/1, integer feedback32 and fraction00c49bc0. The250MHz case selects high VCO, integer mode, reference divider6, post-dividers1/1 and integer feedback125. These recover software policy useful for configuring future audio/display clock consumers. They are not physical jitter/lock/performance measurements or a recommendation to alter stock clocks on hardware.

## Candidate placement and preserved failure

First candidate71a4741f was rejected by all integration runners before execution because temporary object basenames missed linker placement rules, placing new code into the already nearly-full64KiB text slot. Corrected basenames route the four objects to the existing source-cache slot. No loader constraint was relaxed; corrected text/cache sizes are0xfbf0/0xa21c, each within64KiB. Snapshot71a4741f and `validation-blocker.json` are retained. Corrected snapshotf3ca176e freezes654 files/168 objects with actual copies before integration. Source-image Makefile/linker now use the validated source names; the mutable verified ELF was promoted only after all seven cases and reconciliation passed.

The initial draft marker comments in source describe status at creation. These hashed files were kept unchanged during frozen-image tests; this report and candidate-specific receipts supersede those initial unvalidated markers.

Next after successful integration: remaining RX/runtime/clock-power startup child boundaries, IAR formatter backend, platform/ROM coverage and real scheduling/drain. PLL generation itself no longer needs floating libm or numeric stock aliases. Clean standalone source build and byte equality remain separate unresolved goals.
