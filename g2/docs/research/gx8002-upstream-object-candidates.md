# GX8002 upstream driver candidate locations

Date: 2026-09-07. This is binary-attribution evidence, not source admission.

The public [NationalChip LVP KWS SDK](https://github.com/NationalChip/lvp_kws)
was inspected at commit
[`8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5`](https://github.com/NationalChip/lvp_kws/tree/8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5).
Its source includes the grus boot/platform layer, public driver interfaces,
and CK804 support headers. Its
[Makefile](https://github.com/NationalChip/lvp_kws/blob/8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5/Makefile)
selects `csky-abiv2-elf-`, `-mcpu=ck804ef`, and hard-float, but also selects
prebuilt driver, speech, decoder, and DSP libraries. `drivers_lib/` contains
relocatable C-SKY objects. The SDK is therefore not a complete source-only
codec replacement despite its root MIT license and useful public C.

## Reproducible comparison

`tools/analyze_gx8002_upstream_objects.py` authenticates the SDK commit and each
compared Git blob, the existing codec image SHA-256, and the readiness ledger.
It searches only executable ledger spans for complete `.text.*` sections of
at least 16 bytes with no relocations. It does not emit instruction bytes or
select any object as a firmware provider.

The [checked result](gx8002-upstream-object-candidates.json) records:

- 151 eligible sections compared;
- 102 matching occurrences bearing 68 distinct symbol names;
- 5,374 unique package bytes covered by those candidate matches;
- zero source-admitted or emitted firmware bytes.

The raw sum is 5,448 bytes, but one repeated 74-byte sequence from two SDK
objects would double-count coverage. The result uses the interval union.
A named section match is a candidate identity, not proof of a complete
callable boundary, historical generating commit, or equivalent configuration.

Candidates cover analog/ADC/LDO, audio input/output, data and instruction
cache, clock, GPIO, interrupts, flash/SPI, pad multiplexing, power management,
RTC, UART, and UART DMA. The identical original image-A and image-B instances
are recorded separately. These are concrete starting points for recovering
C functions instead of treating the entire codec runtime as one opaque body.

```sh
python3 g2/tools/analyze_gx8002_upstream_objects.py \
  --sdk g2/build/upstream-nationalchip-lvp-kws \
  --output g2/build/gx8002-upstream-object-candidates.json
python3 -m unittest g2.tests.test_gx8002_upstream_objects
```

The four tests cover region confinement, overlapping/aliased coverage,
upstream mutation rejection, and exact local replay of the checked candidate
report. The replay skips if the optional SDK checkout or official codec is
absent; no download runs during tests.

## Next implementation boundary

The current macOS LLVM installation does not advertise a C-SKY backend.
[C-SKY's upstream toolchain builder](https://github.com/c-sky/toolchain-build)
provides the bare-metal GNU route. A native macOS compiler/disassembler now
builds successfully, and the [first seven analog leaves](gx8002-analog-source.md)
compile and pass restricted target trace comparisons. Whole-codec integration
remains unqualified. Linux support is not required for the active goal.

Use the public boot/platform C and driver headers where their behavior fits.
Recover the missing driver implementations from the now-named candidates,
then verify target code, register effects, and integration. Do not link the
SDK's `.o`/`.a` files into the final source-only firmware. Trained model and
accelerator-command reconstruction remain separate work, and the 326,000
retained codec payload bytes remain source-incomplete.
