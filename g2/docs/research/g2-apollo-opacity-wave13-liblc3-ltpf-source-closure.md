# G2 Apollo opacity Wave 13: liblc3 LTPF source closure

Status date: 2026-08-28  
Target: official G2 `s200_v2.2.6.10` Apollo-main image  
Mode: software-only, read-only

## Result

Wave 13 closes the largest post-Wave-12 residual root at `0x00438FB8` and
the complete actionable LTPF graph reached through both static calls and the
seven-slot `resample_12k8[]` function-pointer table.

| Partition | Functions/entries | Official opaque bytes |
|---|---:|---:|
| Apache-2.0 liblc3-compatible source identities | 10 | 4,016 |
| Prior IAR `memmove` reconciliation | 1 | 0 |
| Dispatch-authenticated non-corpus boundaries | 2 | 0 |
| **Selected residual delta** | **11 functions** | **4,016** |

The authoritative residual moves from **1,308 functions / 140,498 bytes** to
**1,297 functions / 136,482 bytes**. The next largest entry is
`0x005AC66E` / 1,684 bytes. No aggregate, package, overlay, Makefile, or
production-routing artifact is changed.

## Positive source evidence

The checked-in snapshot is Google liblc3 tag `v1.1.3`, commit
`96a3af0beb5487aca3b98a4b992a539a1f6d80d1`, under Apache-2.0. The graph maps
to `src/ltpf.c` as follows:

- `lc3_ltpf_analyse`, with compiler-inlined `detect_pitch`, `refine_pitch`,
  `argmax`, and `argmax_weighted` logic;
- `dot`, `correlate`, `interpolate`, and `interpolate_corr`;
- `resample_8k_12k8`, `resample_24k_12k8`, `resample_32k_12k8`,
  `resample_96k_12k8`, and the shared `resample_x192k_12k8` helper.

Evidence combines exact call topology, source-order semantics, pitch and
activation constants, the Q6 dot-product rule, the Q15 phase recurrence, and
eight byte-exact private tables: six sample-rate coefficient tables,
`h4_q15`, and the 4x8 float `h4` table. Compiler-generated MVE bodies do not
change the retained upstream license.

The snapshot provenance explicitly says it is not an exact public-source or
private-checkout proof. Wave 13 therefore uses the disposition
`source-attributed-compatible-baseline-research-only`; it does not claim
byte-exact source/codegen equivalence.

## Indirect and incomplete boundaries

The dispatch table at `0x00439680` contains seven authenticated Thumb entries:
8K, 16K, 24K, 32K, 48K, 48K-HR, and 96K-HR. Four corpus targets have positive
residual bytes. The 24K and 96K wrappers share the selected 410-byte helper.

Ghidra did not emit corpus functions for the 16K entry at `0x00438400` or the
48K entry at `0x00438604`. Their bounded physical intervals are SHA-pinned
(260 and 364 bytes), and their coefficient tables match upstream exactly, but
the next authenticated entry is not sufficient proof of exact compiler body
extent. They remain explicit source-compatible boundaries and add zero census
bytes. This is the fail-closed answer; no missing semantics are invented.

The only static terminal relation is IAR DLIB `sqrtf` at `0x004397A8`. The
root contains three call sites, while the function graph records one unique
relation. It was already typed unavailable and adds zero Wave-13 bytes.

## Byte accounting

Two selected functions have non-contiguous Ghidra ranges. Eleven gaps total
46 physical bytes: seven Thumb NOP gaps, two decompiler-omitted executable
fragments whose precise instruction role remains unresolved, and two
NOP-plus-float literal pools. Every interval is SHA-pinned and already lies
inside an official selected envelope.

Eighteen non-overlapping data spans total 2,204 physical bytes. They cover all
direct `DAT_` labels, the dispatch table, coefficient pointers, literals, and
the eight exact upstream table targets. They are evidence, not additional
function-envelope bytes.

## Production admission

The production-capable source boundary is now implemented by
`components/shared/liblc3/runtime_liblc3_ltpf_provider.c`. It pins the complete
1160-byte state ABI, fixed-width request/result ABI, sample history and
alignment for all seven dispatch slots, Cortex-M55 compile profile, external
`memmove`/`sqrtf` seams, and object-size budgets. Host tests compare the bounded
entry with pristine upstream behavior at every rate, and the target-object test
proves that the maintained source emits all seven resamplers.

The bounded source route is now admitted at
`components/apollo_main/liblc3_ltpf`. The authenticated stock `lc3_encode` BL
at `0x0059145C` is the only patched ingress. The default Apple build targets
maintained `lc3_ltpf_analyse` text at `0x00445664`; its 5,596 text bytes and
1,980 table bytes occupy authenticated reclaimed NOP tails at `0x00445664`
and `0x004FC648`, preserving both donor redirects and the fixed component
size. The Linux profile has ample update-flag headroom and appends its entry at
`0x007C63C4`. The component-local mini-linker
accepts exactly 16 absolute MOVW/MOVT table references, seven absolute Thumb
dispatch cells, and 11 discarded canonical CANTUNWIND rows; it rejects any
undefined runtime symbol or additional allocated section.

`memmove` is closed by the component's overlap-safe Apache-2.0 source provider.
The only admitted square-root ingress is the nonnegative product of two LTPF
self-dot-products; its Apache-2.0 provider emits Cortex-M55 `VSQRT.F32` and
returns a quiet NaN for unsupported negative ingress. The linked payload has
zero unresolved runtime symbols.

Both available compiler families are independently reviewed and pinned:

| Profile | Source bytes | Canonical relocated payload SHA-256 |
|---|---:|---|
| Apple Clang 21, reclaimed caves | 7,576 | `5861f72d7bb2bd1be590fc7fb3f660a075b229f7f92f80079d3262c93b6cda98` |
| Homebrew Clang 22, appended | 7,596 | `c522044887a8ea7082c43a380825ca9ca6444d5dd994530347b6c0dba39062da` |

The Apple component remains 3,952,346 bytes with 438,910 source-owned,
401,494 generated-patch, 3,111,910 retained, and 32 wrapper bytes. Its SHA-256
is `47aabec489ba8882b84591e80ca0f105ff26e3739f4eb639b2d91b88fa2de701`;
the canonical package is 4,745,418 bytes with SHA-256
`b0748df36cbcba58a0bf04ca4de4fa27887f8db0ddb87de61755d830c2ddae58`.
Byte identity with the historical
compiler output is neither claimed nor required. The two Ghidra-omitted stock
16K/48K bodies at `0x00438400` and `0x00438604` remain byte-for-byte unchanged
and individually unrouted; maintained upstream source supplies their dispatch
semantics only inside the newly linked subsystem. Hardware qualification is
still deliberately deferred.

## Reproduction

```sh
python3 g2/tools/analyze_g2_apollo_opacity_wave13.py --pretty
python3 -m unittest g2.tests.test_analyze_g2_apollo_opacity_wave13
python3 -m unittest g2.tests.test_runtime_liblc3_ltpf_provider
python3 -m unittest g2.tests.test_runtime_liblc3_ltpf_overlay
```
