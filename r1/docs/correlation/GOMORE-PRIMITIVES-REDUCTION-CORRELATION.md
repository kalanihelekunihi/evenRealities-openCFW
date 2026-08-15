# GoMore primitive reduction correlation

Status: owner-authorized clean-room reconstruction, 2026-08-14. This is not GoMore source.

The source evidence is the Ghidra export and fresh Thumb-2 disassembly of the byte-exact R1
application rebuild (SHA-256
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1`). Full range hashes and
callers are pinned by `tools/evidence/summarize_r1_frontier_sub32.py`.

## Reconstructed entries

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x0006AD04` | `gomore_primitives_records_all_clear` | test bit 0 in seven records at 16-byte stride |
| `0x000715B8` | `gomore_primitives_record5_initialize` | store words `+4/+8/+0x0C/+0x10`, optional base plus `0x14` |
| `0x000883D4` | `gomore_primitives_clear_two_records` | clear adjacent 20-byte records |
| `0x00071B2A` | `gomore_primitives_fill_missing_pair` | store two `-1.0f` sentinels and return zero in stock ABI |
| `0x00068FBC` | `gomore_primitives_prepare_and_score` | call five-argument preparation routine, score workspace, store float |
| `0x00072AD4` | `gomore_primitives_float_in_encoded_range` | unsigned `(float_bits + 0xBDE00000) <= 0x01500000` |
| `0x000928DA` | `gomore_primitives_scale` | scalar multiply a float vector |
| `0x00094A4C` | `gomore_primitives_callback_record_initialize` | clear `+0xB4`, store words at `+0xB8/+0xBC` |
| `0x00071A20` | `gomore_primitives_span_initialize` | store base and optional base plus `0x14` |
| `0x00087600` | `gomore_primitives_sort_float_subrange` | qsort inclusive float subrange with four-byte elements |
| `0x00091A56` | `gomore_primitives_max_index` | unpack float pointer/count and invoke max-index provider |
| `0x00068720` | `gomore_primitives_size_736` | return `0x2E0` |
| `0x0006841A` | `gomore_primitives_size_14816` | return `0x39E0` |
| `0x00071704` | `gomore_primitives_clear_90` | clear `0x5A` bytes |
| `0x00064770` | `gomore_primitives_set_second_word` | store word at `+4` |
| `0x0005A442` | `gomore_primitives_return_zero` | return zero |
| `0x00076500` | `gomore_primitives_noop_76500` | empty callback |
| `0x000578C8` | `gomore_primitives_noop_578c8` | empty callback |
| `0x00049E58` | `gomore_primitives_noop_49e58` | empty callback |

These first 19 entries comprise 254 bytes of declared inventory extent.

The `0x000928DA` Ghidra entry is a tail-recognized body: its loop head is the shared code at
`0x000928CC`, while `0x000928DA..<0x000928E0` contains the count test/back-edge/return. Fresh
disassembly proves `vldmia`, `vmul.f32`, and `vstmia`; the earlier evidence label that called this a
sum-of-squares helper was wrong and is corrected. The distinct sum-of-squares body begins at
`0x000928E0`.

## Deliberate safety and transparency changes

- Calls to the preparation, scoring, qsort, comparator, and max-index routines are explicit typed
  provider bindings. No target address or hidden table is embedded in the source.
- Null providers, undersized records, invalid sort ranges, and invalid pointers fail explicitly.
  Stock callers guaranteed those preconditions and otherwise could fault or loop on a negative
  count.
- Callback record words are emitted little-endian explicitly, preserving the nRF52840 record ABI
  on the host test build as well as the target.

`tests/test_reconstructed_gomore_primitives.c` exercises every operation, exact constants and byte
offsets, encoded-float boundaries, vector scaling, provider sequencing, inclusive sorting, and all
three distinct no-op symbols. Host, ASan/UBSan, and freestanding Cortex-M4 builds use the same C.

## 32...63-byte tier

The next 16 entries add 712 declared bytes.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x00072B34` | `gomore_primitives_state_window_predicate` | state request predicate with unsigned 300-tick elapsed window |
| `0x0006AB88` | `gomore_primitives_key_or_cached_copy` | copy cached bytes or format three words as 24 lowercase hex characters |
| `0x0008ECD8` | `gomore_primitives_slot_state_transition` | guarded state-byte transition, including `4 + request 5 -> 1` |
| `0x0006AD28` | `gomore_primitives_copy_key_blob` | copy cached or loader-produced 64-byte key blob; return 64 or `-2` |
| `0x000726C4` | `gomore_primitives_stage_32_and_consume` | stage exactly 32 bytes before a five-argument consumer call |
| `0x00062000` | `gomore_primitives_mean` | float mean, returning zero for an empty input |
| `0x000760EC` | `gomore_primitives_argmax_from_zero` | reverse argmax with zero baseline and last-index tie behavior |
| `0x0004C37C` | `gomore_primitives_reset_provider_state` | optional mode clear, release, clear `0x2E0`, initialize mode 1 |
| `0x0006C640` | `gomore_primitives_sample_plausible` | strict bounds over four sample bytes |
| `0x0006ACD8` | `gomore_primitives_stamp_time_record` | timestamp `+0`, UTC offset `+4`, flags `+0x1D/+0x30` |
| `0x00068570` | `gomore_primitives_clamp_hysteresis` | zero-to-one and ±3 baseline hysteresis |
| `0x000726FA` | `gomore_primitives_parameter_commit` | validate then store byte at `+0x20F5`; statuses 0/`0x40` |
| `0x0006AB60` | `gomore_primitives_records_any_bit2` | seven-record scan requiring bits 0 and 2 |
| `0x0006AB38` | `gomore_primitives_records_any_bit4` | seven-record scan requiring bits 0 and 4 |
| `0x0006AB10` | `gomore_primitives_records_any_bit3` | seven-record scan requiring bits 0 and 3 |
| `0x0006AAE8` | `gomore_primitives_records_any_bit1` | seven-record scan requiring bits 0 and 1 |

Fresh disassembly corrected two Ghidra/evidence ambiguities. The format at `0x0006ABC8` is
`%08x%08x%08x` with no underscores, and the four scan shifts (`29`, `27`, `28`, `30`) test
original bits 2, 4, 3, and 1 respectively—not the earlier descriptive labels 2/5/4/6. Every scan
also requires enable bit 0. The authentication/key routines expose cached or loader-owned bytes;
they do not embed the stock key blob, flash contents, device identity, or an opaque binary.

## Selected 64...127-byte utilities

Eight independently closed utilities add 766 declared bytes. The module now reconstructs 43
GoMore functions / 1,732 declared bytes, leaving 319 opaque GoMore functions.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x0004EC9C` | `gomore_primitives_quantized_argmin` | truncate running threshold to int32 and update on lower float over `[begin,end)` |
| `0x00064774` | `gomore_primitives_max_difference_index` | index of first maximum adjacent difference over `[begin,end)` |
| `0x00062034` | `gomore_primitives_median` | in-place float qsort, middle element or mean of middle pair |
| `0x0006208C` | `gomore_primitives_standard_deviation` | mean, `powf(delta,2)`, sample variance, `sqrtf`; singleton result zero |
| `0x000728D4` | `gomore_primitives_logistic_score` | `0.15/(exp((feature-64)*scale)+1)+0.775+bias+feature*coefficient` |
| `0x00094938` | `gomore_primitives_modulo5_record` | 20-step counter, modulo-5 primary/secondary slots, `0xFF -> 1` folding |
| `0x0008EEBA` | `gomore_primitives_compact_25_windows` | drop leading records below window 25, compact 16-byte records, subtract 25 from three uint16 fields |
| `0x00094300` | `gomore_primitives_decimated_ring_write` | 90-byte / 10-tick ring write, exact encoded-float clamp, gap fill, old-window clear |

Fresh VFP disassembly corrected `0x0004EC9C`: despite the previous “argmax” label, it converts the
initial float to signed int, compares subsequent floats against that quantized threshold, and
updates only on a lower value. The reconstruction preserves this unusual behavior. Math, qsort,
and comparison functions remain explicit typed providers; no host libm or opaque algorithm binary
is silently introduced into the freestanding firmware.
