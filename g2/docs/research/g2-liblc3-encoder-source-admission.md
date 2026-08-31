# G2 liblc3 encoder source admission

Status date: 2026-08-30  
Target: official G2 `s200_v2.2.6.10` Apollo-main image  
Mode: software-only; no signing, flashing, erase, or hardware operation

## Result

The largest actionable liblc3 remainder in the `0x59xxxx` frontier is now a
production-capable source boundary. The boundary is the complete encoder
subsystem, rather than an artificial SNS- or spectrum-only ABI:

| Partition | Functions | Official opaque bytes |
|---|---:|---:|
| Source-attributed liblc3 encoder internals | 41 | 16,128 |
| High / medium / low evidence | 15 / 9 / 17 | 16,128 |
| Investigation-required, without liblc3 evidence | 31 | 3,440 |

The last row is not silently claimed as codec source. Its call graph still
points to first-party handle objects, runtime math, overlapping/dead entries,
and peripheral helpers. This admission closes maintained source availability
for the attributed encoder set; it does not rewrite ownership evidence for the
31 unrelated or ambiguous functions.

`components/shared/liblc3/runtime_liblc3_encoder_provider.c` adds a bounded
fixed-width boundary over the pristine upstream encoder. It validates the
stock G2 private state layout, eight-byte storage alignment, exact storage
size, PCM scalar width and stride, input/output byte capacities, provider and
encoder-storage aliasing, and an initialization seal covering the normalized
configuration and plan. The provider accepts caller-owned storage and performs
no allocation or hardware I/O.

## Source and evidence bound

The implementation uses the checked-in Google liblc3 tag `v1.1.3`, commit
`96a3af0beb5487aca3b98a4b992a539a1f6d80d1`, under Apache-2.0. All 11 encoder
translation units are authenticated against `third_party/liblc3/SNAPSHOT.sha256`.
The stock field offsets, four PCM loader slots, dispatch order, and private
tables support compatibility with this baseline.

The evidence does **not** prove that the public tag is the exact private
generating checkout or that maintained code is byte-identical to the IAR stock
output. The admitted claim is source-compatible production C with a bounded
G2 ABI, not historical compiler reproduction.

## Deterministic qualification

Host qualification compares the bounded route with independent pristine
upstream encoder states for S16, S24, packed little-endian S24, and float PCM.
It covers every non-HR duration/rate geometry, downsampled 48 kHz PCM, stride
gaps, short buffers, alignment, aliases, state tampering, and lifecycle close.

The Apple Clang 21 Cortex-M55 profile compiles all 11 encoder units and the
provider with warnings as errors. A section-GC relocatable qualification link,
rooted only at the four provider entries, removes decoder/PLC sections and
leaves exactly these reviewed external seams:

- `memcpy`, `memmove`, and `memset`;
- `fabsf`, `floorf`, `fmaxf`, `fminf`, `roundf`, `sqrtf`, and `truncf`; and
- `__aeabi_memclr` and `__aeabi_memclr4`.

`__aeabi_uldivmod` and the three `lc3_plc_*` relations occur only in discarded
sections and are proven absent from the retained encoder closure. The retained
relocatable object is bounded at 190,000 bytes. Object budgets, the exact
compile profile, source hashes, fixed ABI, allowed relocations, and the
discard-only classifications live in
`components/shared/liblc3/encoder_source_admission.json`.

The build-only integration component at
`components/apollo_main/liblc3_encoder` now compiles those exact units and
performs the section-GC link under the reviewed Apple Clang 21 / Homebrew LLD
23 profile. Two clean builds produced byte-identical artifacts and reports:

| Artifact | Size | SHA-256 |
|---|---:|---|
| Relocation-bearing ARM object | 145,264 | `5143ab77e2496cdd13de674affc22ed030a1a65e2027c4c916da72fd944cb820` |
| Unplaced text | 43,248 | `05ae1d3713f04782702a6574c59b57edf555e4aa711ecd55ac025343eac5688b` |
| Unplaced read-only tables | 85,088 | `607f0246aa2b873a97b7a465bb1adbad63bfe3ede19a650eee1128d21651c8a3` |
| Unplaced writable tables | 404 | `3b0364c5376ebca0b3e789f1c56a66137472fa1f1f32788903bd6d3a3fe8f7be` |

The retained object contains 567 unresolved placement relocations and exactly
the admitted 12 runtime imports. It is a deterministic input to a future
placement layer, not a loadable firmware image.

Run the focused checks with:

```sh
python3 g2/tools/analyze_g2_liblc3_encoder_source_admission.py --pretty
python3 -m unittest -v \
  g2.tests.test_analyze_g2_liblc3_encoder_source_admission \
  g2.tests.test_runtime_liblc3_encoder_provider \
  g2.tests.test_apollo_liblc3_encoder_component
```

## Production integration still required

No stock Apollo image is changed by this research closure. The build-only
component closes reproducible compilation and section-GC linking. A production
placement/routing layer must still:

1. bind every allowed runtime relocation to reviewed target providers and
   reject every additional undefined symbol;
2. assign authenticated placement for 43,248 bytes of retained text, 85,088
   bytes of read-only tables, and 404 bytes of writable tables, then resolve all
   567 relocation records against those selected addresses;
3. route the two `lc3_setup_encoder` calls and the `lc3_frame_samples`,
   `lc3_frame_bytes`, and `lc3_encode` calls owned by recovered
   `service_audio.c`, or replace that service boundary with the bounded provider;
4. reconcile the existing analysis-only `liblc3_ltpf` patch so the complete
   encoder route has one authoritative LTPF implementation; and
5. measure target stack and worst-case execution time before enabling the audio
   cadence.

These are explicit routing, placement, and target-runtime tasks, not missing
codec algorithms. `overlay_routed` remains false until all of them are closed.

## Physical evidence blocker

No authorized G2 hardware was available. Microphone cadence, acoustic output,
BLE peer interoperability, thermal/power behavior, and sustained encode timing
therefore remain blocked by unavailable physical evidence. Passing software
qualification is not a claim of live-device behavior or functional firmware
completeness.
