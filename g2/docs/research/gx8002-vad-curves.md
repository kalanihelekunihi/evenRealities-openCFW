# GX8002 FFT VAD curve reconstruction

Date: 2026-09-07. All five `gx_audio_in_set_fftvad_curve_*` functions now
compile from C and replace their nine authenticated occurrences in the codec
candidate. SDK commit `8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5` supplies the
public 16-bit argument prototypes in `gx_audio_in_v2.h`; original instructions
establish limits and exact register-access order.

| Curve | First input | Second input | Register |
| --- | --- | --- | --- |
| 1 | unsigned 0–3072 | unsigned 0–17920 | `0xA0A00184` |
| 2 | unsigned 0–3072 | unsigned 0–7680 | `0xA0A00188` |
| 3 | signed 0–4096 | signed −5120–5120 | `0xA0A0018C` |
| 4 | unsigned 0–5120 | unsigned 0–5120 | `0xA0A00190` |
| 5 | unsigned 0–8192 | none | `0xA0A00194` |

Bounds are inclusive. Invalid inputs return −1 without MMIO access. Valid
inputs return zero. Curves 1–4 read/write the low halfword, then independently
read/write the high halfword. Curve 3 encodes its signed second argument in
two's-complement form. Curve 5 updates only the low halfword. Inputs follow the
public 16-bit ABI; unsupported noncanonical register values are not assigned
new C semantics.

The implementation uses local union bitfields with explicit whole-word
volatile accesses, as qualified for the I2S tranche. In the host fixture,
separate read callbacks supply different values to ensure the second update
cannot silently reuse the first read. Native C-SKY compilation remains a
mandatory part of admission because bitfield layout is compiler-dependent.

## Evidence

`verify_gx8002_vad_curves.py` authenticates the SDK and stock candidates,
compiles the C, rejects undefined symbols/relocations and size/alignment
violations, and compares return values plus ordered MMIO traces against the
original target instructions. Its restricted interpreter fails on unsupported
instructions or addresses. It checks 22,480 boundary/random target cases.
The host C suite independently checks 11,860 cases, including signed limits,
invalid-input absence of writes, preserved bits, and independent readbacks.
The [verification report](gx8002-vad-source-verification.json) records the
source and emitted-section hashes and the original offsets.

## Placement and accounting

The five generated sections total 220 bytes. Their nine occurrences supply
384 compiled bytes in the codec; 42 additional bytes are explicit zero fill
after the generated function/literal sections. Every qualified control-flow
path returns before the fill. The builder reports this as
`generated_unreachable_fill`, not compiled C or recovered functionality.
Tests check separate ownership and reject modified fill.

Compiled section alignment is checked at each original offset, preserving
PC-relative literal-pool alignment. The C-SKY function instructions and all
literal values come from the compiler; no original instruction bytes supply
these replacements. Other codec regions remain retained and authenticated.

The experimental package now contains seventeen compiled functions. Its codec
has 948 compiled C bytes, 80 generated header bytes, 42 generated fill bytes,
and 325,022 retained bytes. Whole-device operation remains unqualified.
