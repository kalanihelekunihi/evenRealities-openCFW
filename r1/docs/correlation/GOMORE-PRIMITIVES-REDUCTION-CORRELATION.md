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
`0x000928E0`. The two-byte Goodix-classified alternate entry at `0x000928CA` is now also
source-admitted to this same C symbol rather than duplicating the loop in another module.

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

Eight independently closed utilities add 766 declared bytes. At that checkpoint the module
reconstructed 43 GoMore functions / 1,732 declared bytes.

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

## Leaf and initializer closure

Twenty-two additional entries add 340 declared bytes. The primitive module now reconstructs 65
GoMore functions / 2,072 declared bytes; with six tensor executors, 71 entries compile locally and
291 remain gated.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x00091080` | `gomore_primitives_noop_91080` | empty callback |
| `0x0006476C` | `gomore_primitives_set_second_word` | byte-identical twin store at word `+4` |
| `0x00072ACE` | `gomore_primitives_return_zero` | second return-zero leaf |
| `0x00071B24` | `gomore_primitives_clear_72` | clear exactly `0x48` bytes |
| `0x000720C8` | `gomore_primitives_store_first_word` | store word zero and return stock status zero |
| `0x0007170A`, `0x00071D96` | `gomore_primitives_clear_first_byte` | byte-identical first-byte reset twins |
| `0x000711AA` | `gomore_primitives_triplet_initialize` | store words `+4`, `+0`, and `+8` from the recovered argument positions |
| `0x0002F614` | `gomore_primitives_interpolate` | `second + weight * (first - second)` |
| `0x0004AAC0` | `gomore_primitives_byte_in_70_100` | inclusive unsigned byte range 70...100 |
| `0x0005D360` | `gomore_primitives_clear_flag_1000` | change byte `+1000` from one to zero, preserving all other values |
| `0x00067470` | `gomore_primitives_cubic_scale` | exact `0x3E1704FF * x^3` arithmetic order |
| `0x0006773C` | `gomore_primitives_linear_evaluate` | `intercept + slope * x` |
| `0x000484E8` | `gomore_primitives_shift_u8_window5` | shift five bytes left and append one byte |
| `0x0008F674` | `gomore_primitives_nullable_strlen` | byte string length, returning zero for null |
| `0x0004B598` | `gomore_primitives_u16_in_30000_50000` | inclusive unsigned 16-bit range 30000...50000 |
| `0x00071154` | `gomore_primitives_clear_36` | recovered redundant `0x24`/`0x12` clears reduce to exact first-36-byte zeroing |
| `0x00071D9E` | `gomore_primitives_step_record_initialize` | clear 28 bytes and store word value five at `+0x10` |
| `0x00058464` | `gomore_primitives_clear_124` | clear two 60-byte banks and the word at `+0x78` |
| `0x0007116C` | `gomore_primitives_float_state_initialize` | preceding 124-byte clear plus exact word `0x3C54FDF4` at `+0x7C` |
| `0x00070758` | `gomore_primitives_half_to_float_bits` | recovered direct 1/5/10-bit to float32 field expansion |
| `0x00071A10` | `gomore_primitives_store_half_as_float_bits` | convert the low 16-bit value and store its float32 bits |

The fixed float values are named source literals/words, not firmware-table addresses. Checked APIs
reject undersized records and null destinations; every valid stock byte/word offset and arithmetic
ordering is preserved. Tests cover both range endpoints, twin entries, exact initializer words,
all cleared extents, conversion examples, and failure paths.

## Record/math utility and paired-initializer closure

Fifteen additional entries add 474 declared bytes. The primitive module now reconstructs 80
GoMore functions / 2,546 declared bytes; with six tensor executors, 86 entries compile locally and
276 remain gated.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x00064B06` | `gomore_primitives_find_next_nonnegative_i16` | find the first nonnegative signed halfword before the stock-exclusive final slot, or return `-1` |
| `0x000484CA` | `gomore_primitives_shift_two_u8_windows5` | shift two independent five-byte windows and append one byte to each |
| `0x00068238` | `gomore_primitives_normalized_position` | `(value - low) / (high - low)`, with exact zero-span result zero |
| `0x00069500` | `gomore_primitives_packed_2bit_get` | modulo-`0xB40` packed two-bit lookup over the 720-byte backing array |
| `0x00090E68` | `gomore_primitives_energy_state_reset` | reset selected words at `+0x0C/+0x4C/+0x50/+0x54`, store `1.0f` at `+0x14`, and clear `+0x18` |
| `0x000720CE` | `gomore_primitives_large_default_state_initialize` | clear `0x404` bytes, then store `3` at `+0x3F8` and `0.5f` at `+0x3FC` |
| `0x000764DC` | `gomore_primitives_scale_milli` | scale a float vector by the exact source word `0x3A83126F` |
| `0x000883B0` | `gomore_primitives_sps_state_reset` | clear the recovered eight selected word/halfword fields through `+0x54` |
| `0x00094250` | `gomore_primitives_shift_status_windows` | paired history shift with appended `0xFE`/zero and output triplet `FF FE 00` |
| `0x000327E4` | `gomore_primitives_count_byte_plus_one` | count bytes equal to the target and return the count plus one |
| `0x000484A8` | `gomore_primitives_accumulate_pair` | add two floats into `+4/+8` and increment the wrapping halfword at `+0x0C` |
| `0x0005D2EC` | `gomore_primitives_selected_state_reset` | clear the selected header fields and twenty words at `+0x14...+0x60` |
| `0x00071188` | `gomore_primitives_pattern17_initialize` | initialize five `0xFE` bytes, ten zero bytes, and two trailing one bytes |
| `0x000715D4` | `gomore_primitives_energy_record_initialize` | clear 92 bytes, apply the recovered energy reset, set word zero to one, and bind word `+0x58` |
| `0x000715F8` | `gomore_primitives_large_state_initialize` | clear `0x33C` bytes, publish the record through an explicit caller binding, and store word `+0x338` |

The stock `0x000715F8` body wrote the record address through a fixed SRAM pointer. The local API
instead requires the caller to provide that pointer slot, preserving the state publication while
removing the absolute RAM dependency. All record access is bounds checked, multi-byte unaligned
fields use explicit little-endian loads/stores, and the packed accessor exposes its backing-array
length rather than assuming the stock allocation. Tests pin the exclusive terminal-index behavior,
modulo wrapping, exact float words, selective-versus-complete clears, history order, halfword wrap,
and explicit active-record publication.

## Pure constructor, lookup, reset, and transform closure

Sixteen additional entries add 576 declared bytes. The primitive module now reconstructs 96
GoMore functions / 3,122 declared bytes; with six tensor executors, 102 entries compile locally
and 260 remain gated.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x00033330` | `gomore_primitives_low24_binding_initialize` | copy a little-endian 24-bit value and store an explicit second-word binding |
| `0x00074C48` | `gomore_primitives_pack4_binding_initialize` | pack four low bytes and store an explicit second-word binding |
| `0x000722EC` | `gomore_primitives_i16_mean` | signed-halfword mean with zero result for an empty vector |
| `0x000883FC` | `gomore_primitives_float_floor_update` | preserve the existing float when the candidate is lower, using the exact subtract/add order |
| `0x00057C20` | `gomore_primitives_validate_selector` | invalidate selectors one or two when their corresponding state byte is clear |
| `0x00058D26` | `gomore_primitives_nullable_compare` | unsigned-byte string comparison, returning zero if either pointer is null |
| `0x0005CBC0` | `gomore_primitives_compact_u32_stride` | compact every Nth 32-bit word in place |
| `0x00069F80` | `gomore_primitives_status_record_extract` | clear the 68-byte result and return `-1008` on source status, otherwise copy the terminal halfword |
| `0x00071594` | `gomore_primitives_half_span_initialize` | expand a half-float bit pattern and construct four base pointers at 20-byte strides |
| `0x00071D3E` | `gomore_primitives_parameter_state_initialize` | clear `0x20FC` bytes and store the caller binding at `+0x20F8` |
| `0x000967A0` | `gomore_primitives_count_encoded_i32` | count words satisfying unsigned `(word + 0xBF200000) < 0x00E80001` |
| `0x0007316C` | `gomore_primitives_scaled_ratio` | `(numerator * 200.0f) / (denominator * 2.8f)`, zero on a zero scaled denominator |
| `0x0004AA98` | `gomore_primitives_piecewise_clamp_70_100` | rescale around 96 by 0.5 below or 0.8 above, then clamp to 70...100 |
| `0x00058480` | `gomore_primitives_missing_window_initialize` | clear 56 bytes and fill the following six bytes with `0xFF` |
| `0x0006951E` | `gomore_primitives_modulo_value_get` | modulo-`0xB40` direct-byte or packed-two-bit lookup |
| `0x000710D4` | `gomore_primitives_mode8_state_initialize` | clear `0x26E` bytes and store mode eight in byte zero |

The stock constructors at `0x00033330` and `0x00074C48` loaded fixed Thumb function pointers
(`0x00035D13` and `0x0007CA95`) from adjacent literals. Their local APIs require the caller to
supply those bindings, so no code address or provider implementation is hidden in the reconstructed
module. The float constants use exact source words (`0x40333333` and `0x43480000`), the integer
predicate deliberately does not reinterpret `0xBF200000` as a float, and every fixed-layout API
checks its extent. The compactor rejects the stock infinite-loop case of a zero stride.

## Pure vector, record, and predicate closure

Twenty-one additional entries add 1,074 declared bytes. The primitive module now reconstructs 117
GoMore functions / 4,196 declared bytes; with six tensor executors, 123 entries compile locally
and 239 remain gated.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x00056C2A` | `gomore_primitives_vector_pair_transform` | two-float transform with exact divide/multiply/add ordering |
| `0x00059D70` | `gomore_primitives_encode_short_record` | clear 17 bytes, encode the length/active byte, and copy up to 16 payload bytes |
| `0x0007D0A8` | `gomore_primitives_accumulate_i8x4_milli` | add four signed-byte increments scaled by exact word `0x3C23D70A` |
| `0x00048960` | `gomore_primitives_shift_presence_history` | shift the five-byte history and return the recovered one-/two-gap transition code |
| `0x000641C4` | `gomore_primitives_fill_float_progression` | fill a float subrange with `first + local_index * step` |
| `0x00072420` | `gomore_primitives_time_record_valid` | validate signed/unsigned record fields against 15...60, 240, and 23 bounds |
| `0x0004EC6C` | `gomore_primitives_float_argmax_range` | strict first-maximum search over a selected range with stock low-byte update |
| `0x0004ECE0` | `gomore_primitives_float_argmax_above_floor` | strict argmax above exact `-1.0e9f` floor |
| `0x000568F0` | `gomore_primitives_i16_range` | signed-halfword range capped at 32000 |
| `0x0008ED2C` | `gomore_primitives_packed_2bit_set` | modulo-`0xB40` packed two-bit field update |
| `0x000568AC` | `gomore_primitives_rational_transform` | exact four-literal rational transform (`0x3E16277C`, `0x3E20FBA9`, 100, 60) |
| `0x0008F4B4` | `gomore_primitives_i16_mean_absolute_difference` | mean absolute adjacent signed-halfword difference |
| `0x0004B560` | `gomore_primitives_u16_all_within_300` | require every configured halfword to be within 300 of the target |
| `0x00056980` | `gomore_primitives_nonzero_i16_mean8` | mean of nonzero values in a fixed eight-halfword vector |
| `0x00067750` | `gomore_primitives_circular_u8_dot18` | 18-term float dot product over a circular byte window indexed by sample/30 |
| `0x00077162` | `gomore_primitives_filtered_u8_mean` | mean nonzero bytes within an absolute tolerance of the center |
| `0x00058C40` | `gomore_primitives_complex_multiply` | two-float complex multiplication |
| `0x0007EAF6` | `gomore_primitives_count_hysteresis_crossings` | count armed rises above 1200, rearming below 1000 |
| `0x00058CE8` | `gomore_primitives_nullable_compare_n` | bounded unsigned-byte comparison with stock `0xFFFF` invalid result |
| `0x00072AF0` | `gomore_primitives_recent_interval_predicate` | enabled 900...86400 interval ending before `now` and beginning within one day |
| `0x00093DCC` | `gomore_primitives_record_quality_classify` | exact signed flag and encoded-word classification to `-1`, one, or two |

All constants are represented directly as typed values or exact float words. The record encoder
bounds the stock copy to its 16-byte payload, the filtered mean bounds the signed-byte count domain,
and invalid spans/pointers fail without touching output. No neighboring model table, allocator,
sqrt implementation, or callback target is pulled into this closure.

## Explicit-provider and recovered-formula closure

Twenty additional entries add 1,024 declared bytes. The primitive module now reconstructs 137
GoMore functions / 5,220 declared bytes; with six tensor executors, 143 entries compile locally
and 219 remain gated.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x0006AAC0` | `gomore_primitives_seeded_random_offset` | store the seed, prepare the provider, and return signed `random % 100 + 23` |
| `0x00028B8A`, `0x00048D22` | `gomore_primitives_allocate_mode2_state` / `allocate_mode1_state` | zero-allocate `0x23C`/`0x238`, store mode two/one, then invoke the typed initializer |
| `0x0004FB44` | `gomore_primitives_decimal_parse` | unchecked decimal accumulation over the nullable byte string |
| `0x000651A4` | `gomore_primitives_tensor_call_optional_finish` | unpack three descriptor words, call the five-argument tensor provider, optionally finish |
| `0x000295DE`, `0x0002960C` | `gomore_primitives_all_class_0x20` | byte-identical twins requiring every caller-table classification byte to equal `0x20` |
| `0x00071CA0` | `gomore_primitives_filter_state_initialize` | clear `0x18C` bytes and initialize 2x2 state with exact words `0x3C83126F/0x3E23D70A` |
| `0x000908AC` | `gomore_primitives_quality_samples_copy` | copy three nonnegative samples whose signed metadata is below `0x3727C5AC` |
| `0x00068F8C` | `gomore_primitives_dual_stage` | invoke identical five-argument stages at output offsets zero and `0x1C` |
| `0x00071B42` | `gomore_primitives_composite_record_initialize` | initialize the tail, clear the packed `+0x28...+0x2E` fields, then clear two 20-byte heads |
| `0x0005A40E` | `gomore_primitives_quality_code` | apply signed sentinel gates and the locally reconstructed quality classifier |
| `0x000723B6` | `gomore_primitives_i16_standard_deviation` | wrapping signed-square accumulation, sample divisor, and typed square-root provider |
| `0x00069D20`, `0x00069D80` | `gomore_primitives_energy_core` / `energy_scaled` | complete exact-word energy formula and its state/9.81/60 scaling wrapper |
| `0x00068728` | `gomore_primitives_daily_resting_kcal` | exact double-precision sex-specific height/weight/age equations over the recovered ten-byte profile prefix |
| `0x00067D48` | `gomore_primitives_substrate_fat_fraction` | contracted-reference normalization, exponential transform, nonnegative fat/carbohydrate terms, and zero-denominator fraction rule through an explicit exponential provider |
| `0x0002F108` | `gomore_primitives_energy_zone_thresholds` | seven-boundary generator from five admitted logistic evaluations and exact recovered coefficients |
| `0x000763D8` | `gomore_primitives_energy_zone_accumulate` | four energy-zone totals plus the stock 600-second sustained-high-zone accumulator and its duration-retention asymmetry |
| `0x0005D3F8` | `gomore_primitives_energy_projection` | exact double-to-float milli scaling, paired nonnegative energy components, MET ratio, and four-word projection |
| `0x00075D88` | `gomore_primitives_energy_nonlinear_scale` | recovered scale-derived base clamp and ordered double-precision `base + primary*((1-base)/0.4)` calculation |
| `0x00090ACC` | `gomore_primitives_energy_mode_rate` | mode-specific 20/30 input clamp, 0.9/0.1 running state, bounded high/low counters, derived-rate branches, and profile scaling |
| `0x00088DB4` | `gomore_primitives_energy_interpolate_pair` | two recovered exponential/nonlinear interpolation modes producing the paired energy-model inputs through direct double division and an explicit exponential provider |
| `0x00088BD0` | `gomore_primitives_energy_estimator_family_a` | normalized input clamp, long-running/fall counters and reset, adaptive average/factor, interpolation-mode selection, and four-word projection |
| `0x0005A448` | `gomore_primitives_energy_estimator_family_b` | normalized three-region estimator using the recovered ordered double-division/log/exp shaping chain and final four-word projection through explicit logarithm and exponential providers |
| `0x0002F488` | `gomore_primitives_energy_dispatch` | recovered mode routing, normalized `[0.1,1]` clamp, mode-3 logarithmic rate, mode-26 affine rate, and direct specialized/table estimator calls |
| `0x0007DA30` | `gomore_primitives_energy_table_estimator` | complete 27-mode table-driven estimator with all three 27-float tables represented as exact transparent C data, paired baseline projections, nonlinear scaling, nested ordered-division chain, and final profile product |
| `0x0005F56C` | `gomore_primitives_energy_update` | complete top-level producer: typed 92-byte state, reference aging and ten-value history, all three variant × six mode paths, resting/active rate smoothing, exact 11-float output, substrate split, MET, and five zone accumulators; the stock nested reference pointer becomes a direct typed float |
| `0x00061274` | `gomore_primitives_activity_accumulate` | local-day derivation from wrapping Unix seconds plus signed timezone minutes, forward-day-only 52-byte state/44-byte output reset, nonnegative step/active/total accumulation, truncating signed output conversion, and selected-speed/3600 distance accumulation |
| `0x00071E34` | `gomore_primitives_profile_convert` | seven-float profile validation with exact unsigned encoded bounds, last-error status precedence `-101...-107`, age/sex/height/weight and sentinel defaults, duplicated raw/normalized fields, and the recovered two-value persistent-cache fallback behavior |
| `0x00068FD4` | `gomore_primitives_sleep_interval_statistics` | bounded modulo-2880 direct/packed stage scan with leading/middle/trailing awake accounting, unknown-nonzero sleep classification, exact seven-value half-minute interval/efficiency output, and stock all-`-1.0` invalid sentinel |
| `0x00069128` | `gomore_primitives_sleep_stage_statistics` | bounded modulo-2880 direct/packed stage scan producing the exact twelve-value stage fraction, ratio, and half-minute duration block; every zero denominator maps to zero |
| `0x0006778C` | `gomore_primitives_sleep_score` | typed 19-float statistics input, seven raw-bit duration bands, double-tanh duration shape, two-branch `powf(1.1, ...)` wake divisor, exact REM/deep additive weights, raw-bit 0...100 clamp, and preserved exact-540-minute zero-parameter branch hole |
| `0x00074D60` | `gomore_primitives_sleep_peak_rate_interpolate` | bounded low-15-bit peak positions and output span, 60-BPM initialization, high-bit-invalid anchor skipping, leading-slot fill from first spacing, and exact grid interpolation of `scale*60/spacing` between valid anchors |
| `0x00088AAC` | `gomore_primitives_sleep_peak_window_update` | invalidate 10...37-outside peak spacings, select generation or 30-float rotation by the exact mode-specific 6/9/12 counter cadence, normalize the generated tail by `(BPM-60)*0.2`, and increment the wrapping counter |
| `0x00076502` | `gomore_primitives_sleep_peak_tail_rebase` | retain the contiguous suffix of low-15-bit peak positions above 749, compact it to the front, subtract 750 from each position, and preserve every high-bit invalid marker |
| `0x00064A28` | `gomore_primitives_sleep_valley_candidates` | clear twelve output bytes, detect the recovered asymmetric `center <= left && center < right` local valleys, require positive second-difference curvature, and append at most twelve UInt8 indices |
| `0x0008EE3A` | `gomore_primitives_sleep_optical_history_advance` | typed 396-byte state; for each of one/two elapsed blocks shift the 75-float window by 25 and compact/rebase persisted positions, while greater than two invokes the exact admitted filter-state initializer |
| `0x00069F3C` | `gomore_primitives_state_word_24` | read word `+0x18` through an explicit state binding |
| `0x00090EFC` | `gomore_primitives_split_signed_root` | route `pow(abs(value), 0.5)` into the positive or negative output slot |
| `0x000676E0` | `gomore_primitives_clamped_rational` | exact VFP-order rational transform with signed raw-bit clamp at `0x435C0000` |
| `0x000684B4` | `gomore_primitives_table_record11` | select and copy an 11-byte record from an explicit caller-owned table |
| `0x0005D31E` | `gomore_primitives_status_or_random` | return the first negative status, otherwise run the recovered mode-four RNG path |

The stock allocator, random, tensor, filter, stage, root, state, and table addresses are all typed
arguments. No adjacent code pointer, SRAM address, classification table, or model record is copied
into the implementation. Checked APIs reject undersized state and output records; tests exercise
provider order, exact allocation sizes/modes, both twin entries, literal words, signed sentinels,
selective copies, state publication, table offsets, and the complete `0x5D31E -> 0x6AAC0` chain.

## Initializer-chain, resample, compaction, and predicate closure

Twelve additional entries add 752 declared bytes. At this checkpoint the primitive module
reconstructed 149 GoMore functions / 5,972 declared bytes; with six tensor executors, 155 entries
compiled locally and 207 remained gated.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x00071D62` | `gomore_primitives_mode_state_configure` | dispatch modes below two or mode two to typed initializers, set count, clear four-word windows `+0x30/+0x40` |
| `0x00071DD8` | `gomore_primitives_large_filter_state_initialize` | clear `0x6C8`, store `-1.0f` tails, clear 250 floats, then configure exact `0.04f/0.32f` mode-two state |
| `0x00071DB6` | `gomore_primitives_engine_state_initialize` | clear `0x3894`, store binding at `+0x3890`, invoke explicit large-state initializer |
| `0x0008245C`, `0x0008247E` | `gomore_primitives_resample25_and_filter` / `_tail` | resample into 25 floats and apply the typed filter; preserve the status-return/tail variants |
| `0x00058AB8` | `gomore_primitives_prepare_filter_input` | clear the 100-byte input window or run the 25-sample resample/filter path at `+0x118` |
| `0x0007260C` | `gomore_primitives_commit_valid_time_record` | validate the eight-byte record, copy to explicit destination `+2`, optionally cache at context `+0x130` |
| `0x00077E48` | `gomore_primitives_signed_power_third` | preserve sign around `pow(abs(x), 0x3EAAAAAB)` and clear the second float |
| `0x00088264` | `gomore_primitives_trim_below_reference_tail` | count bytes no greater than the reference tail and compact the remaining suffix |
| `0x00080FF4` | `gomore_primitives_selector_transition` | activate selector one from positive state, invalidate one/two on negative sentinel fields |
| `0x00064174` | `gomore_primitives_fill_packed_time_gap` | clear after 86400 ticks or fill intermediate 30-tick packed-two-bit slots |
| `0x00074880` | `gomore_primitives_centered_ratio` | exact wrapped integer denominator, raw-float-bit zero threshold, and centered ratio |

The two stock initializer implementations and the resample/filter operations are typed callbacks;
the context-owned destination pointer in `0x0007260C` is an explicit buffer rather than a 32-bit
host-invalid address stored in the record. Fixed filter parameters use their source words, packed
writes reuse the locally reconstructed modulo setter, and all record extents are checked. Tests
cover both mode branches, full large clears, exact tails/parameters, callback ordering, clear-only
and processing paths, cache flags, signed transforms, compaction, selector activation/invalidation,
packed gap slots, and the zero/nonzero ratio boundary.

## Filter execution, compact-status, and run-processing closure

Nine additional entries add 858 declared bytes. At this checkpoint the primitive module
reconstructed 158 GoMore functions / 6,830 declared bytes; with six tensor executors, 164 entries
compiled locally and 198 remained gated.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x000641F0` | `gomore_primitives_iir_filter_apply` | bounded order-zero-through-eleven float IIR step over explicit coefficient/input/output histories, then publish status one |
| `0x00076120` | `gomore_primitives_thresholded_mean5` | average the five values whose paired comparisons are greater than or equal to the threshold |
| `0x0008F688` | `gomore_primitives_magnitude_score10` | accumulate ten magnitudes clipped by signed raw-word comparison at `0x400851EC`, scaled by exact word `0x4273E706` |
| `0x000569BC` | `gomore_primitives_circular_count_predicate` | count values in an inclusive range over a signed-index circular lookback and apply comparison selector `0x3E` or `0x3C` |
| `0x0008F728` | `gomore_primitives_run_length_encode_2bit` | encode two-bit symbols with six-bit run counts and split runs at the caller-selected maximum chunk |
| `0x0007266A` | `gomore_primitives_propagate_packed_status` | consume the pending flag, read the prior 30-tick packed slot, publish it to the preceding output slot, and clear the flag |
| `0x00071C38` | `gomore_primitives_filter_bank_initialize` | configure one exact `0.0104f/0.96f` mode-two record and three `0.96f` mode-zero records through typed initializers |
| `0x00069546` | `gomore_primitives_target_runs` | collect up to forty caller-selected target runs as `[start,end)` pairs and return their total matched length |
| `0x000748D4` | `gomore_primitives_shift_marked_history` | right-shift the bounded byte history, clear its prefix, then promote at most 21 nonzero entries to marker two until an existing marker |

The IIR implementation treats every recovered coefficient and history word as IEEE-754 binary32;
the stock fixed-address filter configuration is represented by checked caller-owned state. The
filter-bank constructor uses typed initializer callbacks, and packed-slot operations reuse the
local modulo-two-bit helpers. Tests cover filter order zero/one and exact state publication,
inclusive thresholding, literal clipping/scaling, circular wrap and selector behavior, encoded
run splitting, status propagation and flag consumption, all four filter records, target-run
capacity, and marked-history stopping behavior.

## Registration, validation, and state-adapter closure

Eight additional entries add 344 declared bytes. At this checkpoint the primitive module
reconstructed 166 GoMore functions / 7,174 declared bytes; with six tensor executors, 172 entries
compiled locally and 190 remained gated.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x0004B698` | `gomore_primitives_register_mode_topics` | register topic four and then topic three with one context and two explicit handler tokens |
| `0x00061720` | `gomore_primitives_exponential_affine` | evaluate `exp((value - center) * scale) + offset` through the admitted toolchain-math binding |
| `0x00065028` | `gomore_primitives_seed_and_test_text_class` | copy and publish the record seed, then require every byte's explicit classification-table entry to equal `0x20` |
| `0x00065050` | `gomore_primitives_validate_record_bytes` | compare the candidate with the record's byte sequence/length and clear destination `+0x0C` on error `-1005` |
| `0x00065070` | `gomore_primitives_validate_su_signature` | require exact three-byte `SU\0`, clearing destination `+0x0C` on error `-1007` |
| `0x00071100` | `gomore_primitives_sps_engine_initialize` | write the exact zero/one/binding/eight defaults, invoke the local SPS reset, then the explicit final initializer |
| `0x0008EC7C` | `gomore_primitives_state_mode_dispatch` | dispatch modes zero through three to checked state offsets `0xD14/0x13F8/0xD98/0x391C` and normalize status to zero or minus one |
| `0x0008ED10` | `gomore_primitives_commit_valid_time_record_adapter` | replace the stock global engine pointer with a checked caller buffer and commit through its `+0x1130` context |

The stock registration handlers, SRAM engine root, classification table, seed provider, final SPS
initializer, and four mode operations are explicit typed inputs. No absolute RAM/code pointer or
private table enters the C module. The exponential callback corresponds to the separately admitted
Arm `expf` runtime function. Tests cover both topic calls and ordering, expression order, copied
seed and success/error classifications, exact signature and record mismatch effects, initialized
field bytes, every dispatcher route plus status normalization, and nested record/cache placement.

## Manual-supplement and scalar-formula leaves

Four additional entries add 198 declared bytes. At this checkpoint the primitive module
reconstructed 170 GoMore functions / 7,372 declared bytes; with six tensor executors, 176 entries
compiled locally and 186 remained gated. The subsequent tensor-runtime closure raises the overall
local total to 180 and leaves 182 gated without changing the primitive count.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x0007D09C` | `gomore_primitives_one_minus` | return exact single-precision `1.0f - value` |
| `0x0008F49C` | `gomore_primitives_logistic` | return `1.0f / (expf(-value) + 1.0f)` through the admitted exponential binding |
| `0x000304D8` | `gomore_primitives_scaled_product` | preserve the stock float-to-double conversions and ordered `(first * 2.8 * second) / 200.0` operations before converting back to float |
| `0x00056920` | `gomore_primitives_linear_sign_classify` | apply four caller-owned coefficients and bias in stock order, returning minus one for nonnegative score and one otherwise |

The first two entries remain pinned as manual provenance supplements because they begin inside
ranges omitted by Ghidra's function inventory; their 12/24-byte bodies and SHA-256 hashes remain
mandatory in the verifier. The linear coefficients and bias are explicit caller inputs, so the
reconstruction contains no private classifier table. Tests cover exact one-minus behavior,
logistic call/sign order, the recovered double constants, and the classifier's zero/negative split.

## Configuration, status, and runtime-validation closure

Three additional entries add 228 declared bytes. The primitive module now reconstructs 173
GoMore functions / 7,600 declared bytes; with ten tensor executors, 183 entries compile locally
and 179 remain gated.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x00057C44` | `gomore_primitives_validate_key_and_update_status` | compare the configured key bytes, increment the state counter, publish `-1005` on mismatch, run the local status/random reducer, and clear the value word only on failure |
| `0x00057C84` | `gomore_primitives_decimal_config_update` | parse the decimal text, increment the counter, apply the exact `0x6953F6FF/0x688A4180` validation window when enabled, publish `-1006` on failure, and otherwise store the parsed word |
| `0x000967C8` | `gomore_primitives_runtime_version_validate` | apply the same validation lower bound, reject a required missing runtime with minus one, and give the configured/runtime version mismatch `-1008` priority |

The stock configuration and engine roots are explicit caller-owned records. The already-local
nullable compare, decimal parser, and status/random reducer provide the immediate closure; RNG
preparation and generation remain typed provider callbacks. Tests cover success and mismatch,
counter-four random publication, signed status bytes, value clearing/preservation, disabled and
enabled decimal validation, the inclusive lower boundary, missing-runtime policy, and version
mismatch precedence.

## Dominant sorted-run leaf

`0x00070AF8..<0x00070B5A` adds 98 declared bytes as
`gomore_primitives_dominant_sorted_i32`. The primitive module now reconstructs 174 GoMore
functions / 7,698 declared bytes; with ten tensor executors, 184 entries compile locally and 178
remain gated.

The local function sorts caller-owned signed 32-bit values in ascending order and reproduces the
stock run scan exactly: later equal-length runs replace earlier winners, while a final value that
starts a new singleton run is not reconsidered after the previous run is published. This removes
the fixed comparator pointer at `0x00058A63`. Tests pin the sorted output and later-run tie result.

## Circular-vote and sign-crossing leaves

Two additional entries add 218 declared bytes. The primitive module now reconstructs 176 GoMore
functions / 7,916 declared bytes; with ten tensor executors, 186 entries compile locally and 176
remain gated.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x00058256` | `gomore_primitives_circular_signal_predicate` | walk the bounded circular lookback, count primary samples strictly above 200 and three-channel signed sums strictly above 180, and return one only when both counts reach three |
| `0x00069FA8` | `gomore_primitives_average_sign_crossing_spacing` | record strict-negative adjacent products and return `(last-first)/(crossings-1)` only for at least two crossings; otherwise return `-1.0f` |

Both APIs use caller-owned arrays and explicit lengths. The circular implementation retains the
stock single-wrap signed-byte index domain through a checked maximum count of 127; the crossing
implementation excludes zero products and unordered comparisons. Tests cover wraparound, both
strict thresholds, the three-match gate, three-crossing spacing, and the one-crossing sentinel.

## Decimal rounding and time-engine initialization

Two additional entries add 202 declared bytes. The primitive module now reconstructs 178 GoMore
functions / 8,118 declared bytes; with ten tensor executors, 188 entries compile locally and 174
remain gated.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x00080F88` | `gomore_primitives_round_decimal_places` | compute `powf(10, places)`, apply the stock positive `+0.5f` or negative exact-word `-0.4f` adjustment, convert through signed int32, and divide by the scale |
| `0x00071CD8` | `gomore_primitives_time_engine_initialize` | clear `0x13C`, populate the zero-tag default configuration, publish the binding and 600-tick timeout, invoke the local 90/72-byte clears, and copy configuration words `+2/+6` |

The power operation is a typed callback to the separately admitted Arm runtime. The stock
configuration pointer is represented by an explicit 32-bit binding token, keeping host and target
layouts deterministic without embedding the SRAM address. Tests cover positive and negative
rounding plus every default configuration, timeout, copied-word, and binding byte.

## Bounded interval argmax leaf

`0x000649BC..<0x00064A1E` adds 98 declared bytes as
`gomore_primitives_interval_nonzero_argmax`. The primitive module now reconstructs 179 GoMore
functions / 8,216 declared bytes; with ten tensor executors, 189 entries compile locally and 173
remain gated.

The implementation walks adjacent caller-owned byte boundaries, retains intervals whose signed
difference is above the stock double constant 7.5, calls the local range argmax, and appends the
selected byte index only when its float value is not exactly zero. Explicit value/output extents
replace unchecked firmware buffers. Tests pin an accepted nonzero interval and suppression of a
zero-valued interval.

## Sequence replay controller

`0x00096E0C..<0x00096E6E` adds 98 declared bytes as
`gomore_primitives_sequence_replay`. The primitive module now reconstructs 180 GoMore functions /
8,314 declared bytes; with thirteen tensor-runtime routines, 193 entries compile locally and 169 remain gated.

The controller initializes an unset base sequence, accepts gaps 2...15 by replaying the exact
count from `base+1`, treats equal/next sequence as one iteration, increments multi-replay records
after every callback, and publishes the resulting sequence. Other discontinuities store and
return `-1027`. The larger per-record processor remains an explicit typed callback. Tests pin a
three-record replay, every observed sequence, final publication, and the discontinuity error bytes.

## Four-field CSV prefix comparator

`0x0005D560..<0x0005D5CC` adds 108 declared bytes as
`gomore_primitives_csv4_prefix_compare`. The primitive module now reconstructs 181 GoMore
functions / 8,422 declared bytes; with thirteen tensor-runtime routines, 194 entries compile
locally and 168 remain gated.

The recovered body zeroes a 48-byte local, copies at most 47 candidate bytes, requires exactly
four comma-separated fields, selects the first nonempty token with comma delimiter semantics,
and returns the low signed byte of the pattern-length prefix comparison. The API makes pattern
length explicit. Stock passed the untruncated input length to the comma counter and could read
beyond its local buffer; the reconstruction counts only the admitted 47 bytes. Tests pin both
recovered SDK-auth identifiers' prefix shape, mismatch and field-count results, leading-delimiter
token selection, prefix acceptance, and the bounded overlength divergence.

## Sleep-engine open/reset

`0x00090F44..<0x00090FA6` adds 98 declared bytes as
`gomore_primitives_sleep_engine_open`. The primitive module now reconstructs 182 GoMore
functions / 8,520 declared bytes; with thirteen tensor-runtime routines, 195 entries compile
locally and 167 remain gated.

The initializer applies the already-local active-flag close when reopening, clears the exact
`0x1B90`-byte tensor-pool region, constructs the literal two-dimensional `{1,90}` descriptor,
stores its explicit 32-bit binding at `+0x20EC`, clears the two neighboring owner words, restores
the active/cursor fields at `+0x3E6...+0x3EA`, and clears the 136-entry halfword history at
`+0x2D6`. A typed constructor callback replaces the stock absolute descriptor allocator while
retaining the caller-owned pool extent. Tests pin every offset, shape, callback argument, pool
zeroing before construction, binding bytes, re-open state, and short-state/provider failures.

## History, logger, and accelerometer preprocessing closure

Three exact bodies add 304 declared bytes:

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x000948D8` | `gomore_primitives_shift_negated_filter_history` | shift the 250-float history left by 25, fill the tail with zero or negated input, and filter the active tail only |
| `0x000823D8` | `gomore_primitives_log_u32` | apply the two recovered bit masks, prefix `[GoMoRe]`, format one unsigned value into the 248-byte tail, append CRLF, and emit through `%s` |
| `0x00060990` | `gomore_primitives_accelerometer_resample25` | clear three 25-float outputs, return status `0x20`/failure one for zero samples, otherwise resample/filter three axes at `0x50` filter-state strides, then log status |

That preprocessing checkpoint reconstructed 185 GoMore primitive functions / 8,824 declared
bytes. The later energy reduction adds `0x00068728` / 214 bytes, `0x00067D48` / 198 bytes,
`0x0002F108` / 246 bytes, `0x000763D8` / 250 bytes, `0x0005D3F8` / 220 bytes,
`0x00075D88` / 132 bytes, `0x00090ACC` / 334 bytes, and the five residual dispatcher/estimator
bodies (`0x00088DB4`, `0x00088BD0`, `0x0005A448`, `0x0002F488`, `0x0007DA30`) / 1,902 bytes,
bringing the primitive module to 197 functions / 12,320 declared bytes. The later top-level
energy-producer reduction adds `0x0005F56C` / 2,102 bytes, bringing the primitive module to
198 functions / 14,422 declared bytes. The daily activity accumulator at `0x00061274` adds 272
bytes, bringing the primitive module to 199 functions / 14,694 declared bytes. With thirteen
tensor-runtime routines, 212 entries compile locally. The 436-byte profile converter at
`0x00071E34` brings the primitive module to 200 functions / 15,130 declared bytes and the combined
local total to 213 entries. The 430-byte sleep-stage statistics block at `0x00069128` brings the
primitive module to 201 functions / 15,560 declared bytes and the combined local total to 214
entries. The adjacent 326-byte sleep-interval statistics block at `0x00068FD4` brings the primitive
module to 202 functions / 15,886 declared bytes and the combined local total to 215 entries, with
147 remaining gated. The 580-byte sleep score at `0x0006778C` brings the primitive module to 203
functions / 16,466 declared bytes and the combined local total to 216 entries, with 146 remaining
gated. The 444-byte sleep peak-rate interpolator at `0x00074D60` brings the primitive module to 204
functions / 16,910 declared bytes and the combined local total to 217 entries, with 145 remaining
gated. Its 280-byte window-update caller at `0x00088AAC` brings the primitive module to 205
functions / 17,190 declared bytes and the combined local total to 218 entries, with 144 remaining
gated. The 110-byte peak-tail carryover at `0x00076502` brings the primitive module to 206 functions /
17,300 declared bytes and the combined local total to 219 entries, with 143 remaining gated.
The 112-byte valley-candidate extractor at `0x00064A28` brings the primitive module to 207 functions /
17,412 declared bytes and the combined local total to 220 entries, with 142 remaining gated. The
128-byte optical-history advance at `0x0008EE3A` brings the primitive module to 208 functions /
17,540 declared bytes and the combined local total to 221 entries, with 141 remaining gated. The
192-byte linear resampler at `0x000882EC` and 140-byte optical-to-peak coordinator at `0x00060AF4`
bring the primitive module to 210 functions / 17,872 declared bytes and the combined local total
to 223 entries, with 139 remaining gated. The resampler preserves the stock equal-length copy and
Float32 linear-interpolation paths. The coordinator composes history advancement, input preparation,
75-value valley extraction, greater-than-7.5 interval argmax selection, prior-tail deduplication,
17-byte record encoding, and exact 12-byte scratch persistence without an opaque callee. Five
additional leaves add 558 declared bytes: complex power `0x00058C7A`, ten-value quantized
magnitude `0x00059E60`, range center/span `0x00064A98`, a typed three-feature linear model
`0x00068DE0`, and the deep/awake boundary repair `0x000881F4`. They bring the primitive module
to 215 functions / 18,430 declared bytes and the combined local total to 228 entries, with 134
remaining gated. The complex math functions are explicit typed bindings, the quantizer retains
the stock raw-Float32-bit thresholds, the linear model consumes a caller-owned coefficient record,
and the stage repair bounds the stock six-position rewrite at the caller's buffer start. Eight more
history/model leaves add 1,076 declared bytes: circular feature-slot advance `0x000484FC`, triple
circular Int16 mean `0x00056BA8`, positive-fill circular mean `0x00058AEE`, SPS state initializer
`0x00071714`, rolling mean `0x00090A50`, nearest nonzero selector `0x00068420`, scaled quadratic
difference `0x000695A8`, and reciprocal-affine model `0x00069E94`. They bring the primitive
module to 223 functions / 19,506 declared bytes and the combined local total to 236 entries, with
126 remaining gated. All global coefficient/state dependencies are now literal words or typed
caller-owned records; bounds checks cover the stock circular and slot-index assumptions. The
bounded complement `0x00056C54`, autocorrelation wrapper `0x00056D78`, direct-versus-estimated
heart-rate selector `0x000605DC`, and SPS model dispatcher `0x000684FC` add 436 declared bytes.
They bring the primitive module to 227 functions / 19,942 declared bytes and the combined local
total to 240 entries, with 122 remaining gated. The autocorrelation core and model/commit steps
are typed providers; unavailable heart-rate output is an explicit zero/zero/source-`0x40` record.
The four-byte Base64 block decoder `0x0005C064`, five-value dominant quantized mean
`0x00067B24`, and update-failure counter/reset policy `0x0006C1C0` add 412 declared bytes. They
bring the primitive module to 230 functions / 20,354 declared bytes and the combined local total
to 243 entries, with 119 remaining gated. The decoder preserves the stock character mapping and
three-byte block writes while adding explicit length and capacity checks; the counter's stock
log and reset calls are typed providers rather than hidden globals.
The five-sample Int16 trend gate `0x000583C8`, SPS affine-pair refresh `0x00070F44`, positive
quadratic-root updater `0x0006818C`, and motion-variability score adjustment `0x00093FAC` add 642
declared bytes. They bring the primitive module to 234 functions / 20,996 declared bytes and the
combined local total to 247 entries, with 115 remaining gated. Caller-owned histories, coefficient
pairs, root slots, and three axis arrays replace stock pointer/global state; typed power and square-
root bindings preserve the exact arithmetic and repeated-call order.
The civil-time converter `0x00059CB0`, 27-field algorithm-output snapshot copier `0x00059D9C`,
and 15-slot sleep-descriptor initializer `0x00071B74` add 554 declared bytes. They bring the
primitive module to 237 functions / 21,550 declared bytes and the combined local total to 250
entries, with 112 remaining gated. Exact epoch arithmetic, byte offsets, thresholds, circular-slot
selection, and scan limits are tested over caller-owned records with no stock global bindings.
The padded sliding-window mean `0x00091A60`, profile-state dispatcher `0x000916C8`, interpolated
sorted percentile `0x0007ED30`, and first-available SPS selector `0x000610C8` add 700 declared
bytes. They bring the primitive module to 241 functions / 22,250 declared bytes and the combined
local total to 254 entries, with 108 remaining gated. The profile dispatcher composes the already
local slot-transition primitive; sort and diagnostic hooks remain explicit typed providers.
The statistics accumulator `0x000949A8` adds 156 declared bytes, bringing the primitive module to
242 functions / 22,406 declared bytes and the combined local total to 255 entries, with 107
remaining gated. Instruction-level review resolves the decompiler ambiguity: the mean input is
accepted when its raw Float32 word lies in the inclusive `40.0...240.0` interval.
The interval-descriptor merge `0x00072024`, stateful step accumulator `0x00061198`, and packed
half-minute timeline extractor `0x00068354` add 554 declared bytes. They bring the primitive
module to 245 functions / 22,960 declared bytes and the combined local total to 258 entries, with
104 remaining gated. These bodies directly compose the already source-owned presence-history and
packed-2-bit accessors; all former global records are caller-owned typed state.
The sleep-interval refinement `0x00058B70`, interval builder `0x000692E4`, and composing wrapper
`0x00067558` add 848 declared bytes. They bring the primitive module to 248 functions / 23,808
declared bytes and the combined local total to 261 entries, with 101 remaining gated. Tests pin
history backscan, hour windows, raw Float32 thresholds, merge statuses, and 30-second alignment;
the wrapper directly composes both reconstructed leaves.
The interval selector `0x00072572` and typed dispatch wrapper `0x00067BBC` add 264 declared bytes,
bringing the primitive module to 250 functions / 24,072 declared bytes and the combined local
total to 263 entries, with 99 remaining gated. This batch also corrects `0x000726C4` status
propagation: the recovered caller compares the underlying consumer's `r0`, now preserved through
the typed stage callback instead of being discarded by a void abstraction.
The one-shot interval reducer `0x0007244E` and compact global-state wrapper `0x0005D370` add 388
declared bytes, bringing the primitive module to 252 functions / 24,460 declared bytes and the
combined local total to 265 entries, with 97 remaining gated. The reducer composes the already
local interval builder/refiner and 40-byte descriptor merge, refreshes the eight-byte policy from
an explicit caller-owned source, and preserves the stock one-shot control transition. The wrapper
exports the exact compact start/end plus flags/auxiliary/status/tail byte selection and composes
the already local packed-status propagation leaf.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x0007244E` | `gomore_primitives_sleep_interval_run` | execute the one-shot interval compose/near-clamp/commit/descriptor-merge sequence, refresh the unaligned policy record, and disable the control |
| `0x0005D370` | `gomore_primitives_sleep_interval_update` | clear pending/output state, run the interval reducer, export the exact compact 12-byte view, and conditionally propagate the prior packed status |

The health-sample feature converter `0x0006ABF8` and five-sample scaled publisher `0x0004B4B0`
add 324 declared bytes, bringing the primitive module to 254 functions / 24,784 declared bytes
and the combined local total to 267 entries, with 95 remaining gated. Stored data and event output
are explicit typed inputs/callbacks; the exact unsigned/signed conversions, zero-to-minus-one
sentinels, binary64 scaling constants, bounded 50-value capture, and eight-byte event payload are
tested without fixed firmware globals.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x0006ABF8` | `gomore_primitives_health_sample_features` | convert four packed bytes and three signed halfwords into seven floats, substituting `-1.0f` for zero halfwords, then apply the local plausibility predicate |
| `0x0004B4B0` | `gomore_primitives_scaled_sample_publish` | average five unsigned samples, apply exact `0.01`/`0.1` binary64 scaling, append a bounded capture value, and optionally publish the zero-padded topic-nine payload |

The PPG resampling wrapper `0x00060A14` adds 200 declared bytes, bringing the primitive module to
255 functions / 24,984 declared bytes and the combined local total to 268 entries, with 94
remaining gated. It composes the already local 25-sample resample/filter tail and typed logger,
processes the stock maximum of one channel while retaining division by the requested channel
count, and exposes filter state, sources, output, failure byte, and status as bounded inputs.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x00060A14` | `gomore_primitives_ppg_resample25` | clear the 25-float destination, fail with `0x40` on zero channels/samples, otherwise resample/filter at most the first channel and scale every output by reciprocal channel count |

The fourth-order integer IIR state update `0x0008F3C8` adds 206 declared bytes, bringing the
primitive module to 256 functions / 25,190 declared bytes and the combined local total to 269
entries, with 93 remaining gated. Both five-word coefficient profiles are explicit signed
integers recovered from the pinned image; the implementation preserves the stock wrapped 32-bit
multiply/accumulate behavior, four-slot history shift, and signed truncation by 1000.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x0008F3C8` | `gomore_primitives_integer_iir4_update` | select one of two exact fourth-order coefficient profiles, update wrapped integer input/output histories, and publish the divided current output |

The stable trimmed-median estimator `0x0004B5B0` and dual dominant selector `0x00067A40` add 448
declared bytes, bringing the primitive module to 258 functions / 25,638 declared bytes and the
combined local total to 271 entries, with 91 remaining gated. Both bodies operate over bounded
caller-owned five/50-element records and compose only source-owned sorting, dominant-run, and
filtered-mean logic; the exact 10% trimming, odd/even median, 100-unit stability limit,
binary64 scaling word, category sentinel, and 35/50 quantization profiles are pinned by tests.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x0004B5B0` | `gomore_primitives_stable_trimmed_median` | sort 12–50 halfwords, compare the 10%-trimmed mean with the exact median, reject divergence above 100, store their midpoint, and return its exact `0.1` scaling |
| `0x00067A40` | `gomore_primitives_dual_dominant_u8_select` | derive a strict-majority signed category and a separately quantized dominant value, then filter the original five bytes around the selected center |

The identifier-status validator `0x00057B38` and state-2 cadence estimator `0x00057F8C`
add 362 declared bytes, bringing the primitive module to 260 functions / 26,000 declared bytes
and the combined local total to 273 entries, with 89 remaining gated. The validator composes
only the already reconstructed nullable-string, character-class, and status/random helpers; its
three embedded 16-digit identifiers and exact `-1004`/`-1020` branches are explicit. The cadence
estimator preserves the unsigned raw-Float32 encoding range strictly above 120 and below 220,
Float32 subtraction followed by binary64 absolute comparison, the two strict `<10.0` consensus
checks, and the stock middle-sample fallback when the latest encoding is outside that range.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x00057B38` | `gomore_primitives_validate_identifier_status` | increment validation state, apply the exact nullable/class and three-identifier decisions, commit stock status/error words, and preserve the nullable-input success path |
| `0x00057F8C` | `gomore_primitives_state2_cadence_estimate` | classify three raw cadence encodings, report strict adjacent consensus, and select the latest or firmware-defined middle fallback sample |

The three-axis circular-window gate `0x000582C4` adds 260 declared bytes, bringing the primitive
module to 261 functions / 26,260 declared bytes and the combined local total to 274 entries, with
88 remaining gated. Its bounded interface makes the stock eight-slot ring assumption explicit.
The implementation preserves signed Int16 sampling, backward wrap, three signed sums, strict
first/second ranking and tie order, byte crossing counters, and the final requirement that the
highest-sum axis cross the primary threshold at least three times while the second-highest-sum
axis crosses the secondary threshold at least three times.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x000582C4` | `gomore_primitives_three_axis_window_gate` | sum a bounded backward circular window on three axes, retain the stock strict top-two ordering, and return `1` only when both ranked axes meet their respective three-crossing gates |

The fixed fourth-order motion filter `0x00074914` adds 260 declared bytes, bringing the primitive
module to 262 functions / 26,520 declared bytes and the combined local total to 275 entries, with
87 remaining gated. The ten Float32 coefficient words are explicit constants independently pinned
by the sleep-algorithm audit. The bounded implementation retains the stock 30-sample scratch
limit, five-sample input/output histories, feedforward-first traversal, feedback subtraction,
history replacement, and in-place filtered output without reading an opaque coefficient table.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x00074914` | `gomore_primitives_motion_iir4_filter` | apply the exact fixed five-tap numerator and four-tap feedback recurrence to 5–30 samples, persist the trailing five raw/filtered samples, and replace the input in place |

The six-bin weighted histogram accumulator `0x00094698` adds 326 declared bytes, bringing the
primitive module to 263 functions / 26,846 declared bytes and the combined local total to 276
entries, with 86 remaining gated. Its recovered pointer-bearing record is represented directly as
five boundaries and six-element sum/count arrays. The implementation preserves the positive-only
denominator gate, normalized contribution, separately weighted below-range bin, half-open interior
bins, inclusive final bin, and one-count increment without any firmware state or table dependency.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x00094698` | `gomore_primitives_weighted_histogram6_accumulate` | normalize one numerator by its positive denominator, select one of six threshold bins, apply the below-range weight only to bin zero, and update the selected sum/count pair |

The dormant speed smoother `0x0004C6DC` adds 312 declared bytes, bringing the primitive module to
264 functions / 27,158 declared bytes. Together with the newly admitted pooling executor in the
tensor-runtime companion report, the combined local total is 278 entries, with 84 remaining
gated. Its explicit 32-byte state preserves exact enable/configuration guards, accepted 700–1300
millisecond interval, raw and output slew limits, ten-sample prefix mean, fixed `0.35`/`0.65` EMA,
unclamped previous-raw storage, four status words, and stable-or-clamped flag behavior. No inactive
state writer or physical speed meaning is inferred.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x0004C6DC` | `gomore_primitives_speed_smoother_update` | validate the exact state/interval/limit gates, apply raw slew limiting, prefix-mean or EMA smoothing, apply output slew limiting, and publish the stock status and stable/clamped flag |

The active-only flag-dependent speed gate `0x000908E0` adds 352 declared bytes, bringing the
primitive module to 265 functions / 27,510 declared bytes and the combined local total to 279
entries, with 83 remaining gated. Its bounded six-float history interface preserves the ordered
first-sample rejection, unflagged five-value rolling average, exact `27.690000534` and
`2.900000095` selection thresholds, flag mask `0x1444`, dynamic nonnegative rise cap
`5.5 - previous * 0.458299994`, flagged six-value prefix/rolling average, strict flagged rise
selection, and stock NaN behavior. Negative indices and null history are rejected without memory
access; no active firmware route or physical speed meaning is inferred.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x000908E0` | `gomore_primitives_speed_gate` | mutate the aliased five/six-value history under the exact flag-dependent windows and select either the raw candidate or average using the pinned ordered thresholds and dynamic rise cap |

The dormant estimator wrapper `0x0005FEB8` adds 216 declared bytes, bringing the primitive module
to 266 functions / 27,726 declared bytes and the combined local total to 280 entries, with 82
remaining gated. The typed wrapper preserves the stock-disabled early return, first-update elapsed
suppression, later unsigned elapsed accumulation, exact nine-field iteration record, ARM
float-to-signed conversion saturation, forced-invalid substitution, mode-one replay and status
extraction, other-nonzero bypass, and update-count ordering. The still-unreconstructed per-iteration
body is an explicit typed callback; no opaque executable or implicit absolute state pointer is
linked into the local implementation.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x0005FEB8` | `gomore_primitives_dormant_estimator_update` | gate the dormant modes, compose the exact iteration inputs, replay through a typed step binding, extract the status record after both replay success and failure, and retain the stock state-counter ordering |

The three-axis sleep-motion feature `0x0005F3D8` adds 222 declared bytes, bringing the primitive
module to 267 functions / 27,948 declared bytes and the combined local total to 281 entries, with
81 remaining gated. Its exact 128-byte state exposes six five-float IIR histories, warm-up count,
and magnitude threshold. The implementation retains 25-to-30 linear resampling, milli scaling,
the fixed fourth-order filter, stride-three compaction, both ten-sample magnitude paths, three-axis
sum-of-squares, five-update missing-output warm-up, mode-reset behavior, and distinct `0x40`/`0x41`
statuses. Floor and square-root toolchain operations are explicit typed bindings.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x0005F3D8` | `gomore_primitives_sleep_motion_feature` | reduce three 25-sample channels through the exact resample/filter/compact pipeline, preserve the paired magnitude accumulators and warm-up/reset state, and publish the recovered status/output pair |

The fifteen-slot minute accumulator `0x000947DE` adds 248 declared bytes, bringing the primitive
module to 268 functions / 28,196 declared bytes and the combined local total to 282 entries, with
80 remaining gated. Its exact 72-byte state preserves modulo-15 minute placement, completed-minute
zero fractions, previous-value fallback, bounded short-gap fill, the 900-second full reset,
signed byte counters, truncating integer accumulation with modular addition, and ordered NaN and
negative-sample rejection.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x000947DE` | `gomore_primitives_minute_accumulator_update` | close a crossed minute into the modulo-15 history, fill skipped short-gap minutes, reset long gaps, and accumulate the current nonnegative sample with exact zero-count and integer-sum behavior |

The tensor-bank constructor `0x00071618` adds 230 declared bytes, bringing the primitive module to
269 functions / 28,426 declared bytes and the combined local total to 283 entries, with 79
remaining gated. The bounded interface makes the variable overlapping pointer-table geometry,
20-byte backing-record stride, optional paired and secondary banks, sparse tensor-binding slots,
rank-one dimension load, zero-fill request, and runtime/pool bindings explicit. On the Cortex-M4
target `uintptr_t` retains the recovered 32-bit pointer layout; host tests validate the same logical
topology without narrowing pointers.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x00071618` | `gomore_primitives_tensor_bank_initialize` | build the exact primary/optional-secondary pointer plan over 20-byte records and lazily create missing rank-one zero-filled tensor bindings through an explicit transparent-runtime callback |

The fixed sleep IIR `0x00064274` adds 264 declared bytes, bringing the primitive module to 270
functions / 28,690 declared bytes and the combined local total to 284 entries, with 78 remaining
gated. The five recovered coefficient words are exact raw-bit constants. The local body preserves
zeroed per-call two-sample input/output histories, Float32 multiplication, double-precision
accumulation order, final Float32 rounding, and in-place replacement without retaining hidden
state or reading the stock coefficient object.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x00064274` | `gomore_primitives_sleep_iir2_filter` | apply the exact stateless second-order feedforward/feedback recurrence with recovered raw-bit coefficients and the stock Float32-product/double-accumulation rounding sequence |

The sleep-step orchestrator `0x00094070` adds 202 declared bytes, bringing the primitive module
to 271 functions / 28,892 declared bytes and the combined local total to 285 entries, with 77
remaining gated. Its explicit 184-byte state composes the now-local minute accumulator and
90-byte decimated ring while preserving optional UTC-offset civil-time conversion, the exact
local-hour window comparison, activity/latch selection, control-dependent 300/1200-second
countdown reload, and saturating elapsed decrement. Previously ambiguous hard-float inputs are
represented as typed sample arguments.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x00094070` | `gomore_primitives_sleep_step_update` | perform one exact ring/minute update, optionally derive the local-hour flag, resolve the activity latch, and reload/decrement the recovered countdown state |

The composite engine initializer `0x00071A32` adds 242 declared bytes, bringing the primitive
module to 272 functions / 29,134 declared bytes and the combined local total to 286 entries, with
76 remaining gated. Its sixteen recovered child calls are all mapped to transparent local
initializers. The stock base-plus-offset relationships are preserved as explicit 32-bit bindings,
the stock configuration pointer at base `+0x290` is replaced by a bounded caller-supplied buffer,
and private filter operations are represented by typed callbacks rather than absolute firmware
addresses. Tests cover every recovered status-byte offset, callback count, default configuration
word, nested binding, returned interior pointer, and mutation-free short-buffer rejection.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x00071A32` | `gomore_primitives_composite_engine_initialize` | initialize the complete `0x3894`-byte engine layout by composing all recovered local substates, propagate five exact binding offsets, and return the stock `+0x37FD` result pointer |

The Cardano candidate assembler `0x000675DC` adds 250 declared bytes, bringing the primitive
module to 273 functions / 29,384 declared bytes and the combined local total to 287 entries, with
75 remaining gated. Its complete call closure was already transparent: real signed cube roots,
principal complex powers, complex multiplication, adjusted pair sums, and the signed-raw-bit
candidate writer. The local body retains the exact `0x3EAAAAAB` one-third exponent, the
`0x358637BD` real-discriminant imaginary bias, both root-of-unity rotations, and the stock rule
that invalid candidate slots retain their prior destination values. Math-library operations are
explicit typed callbacks; no absolute firmware targets or opaque coefficient objects remain.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x000675DC` | `gomore_primitives_cardano_candidates` | form all three adjusted Cardano candidates from paired real or complex cube roots and commit only candidates passing the recovered real/nonnegative and signed-imaginary-bit gates |

The state-two SPS secondary model `0x00068E5C` adds 254 declared bytes, bringing the primitive
module to 274 functions / 29,638 declared bytes and the combined local total to 288 entries, with
74 remaining gated. Its ten used model words are no longer an opaque pointer into the stock image:
they are explicit named Float32 center, scale, weight, signed-root amplitude, and output-offset
constants. The local body preserves Float32 normalization and linear accumulation followed by the
stock binary64 `sqrt(abs(normalized)) * sign * amplitude` term and final Float32 conversion. The
only external operation is a typed double square-root callback routed to the admitted toolchain
runtime.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x00068E5C` | `gomore_primitives_sps_secondary_model` | evaluate the exact three-feature affine-plus-signed-square-root model using ten transparent raw-bit coefficients and an explicit binary64 square-root provider |

The half-position control-point expander `0x00067C30` adds 274 declared bytes, bringing the
primitive module to 275 functions / 29,912 declared bytes and the combined local total to 289
entries, with 73 remaining gated. Ghidra's fourth-argument type obscured the hard-float ABI; the
disassembly proves it is the output array, while each interpolation step is computed internally
from adjacent control values and a rounded half-position span. The reconstruction bounds every
span and output index, uses the already local Float32 progression helper, exposes only the admitted
binary64 `round` provider, and retains constant prefix/tail fills plus per-segment step resets.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x00067C30` | `gomore_primitives_expand_half_positions` | expand ordered control values into a bounded output using rounded half-position spans, segment-local Float32 interpolation, and constant prefix/tail fill |

The pKey flash validator `0x0006AD80` adds 282 declared bytes, bringing the primitive module to
276 functions / 30,194 declared bytes and the combined local total to 290 entries, with 72
remaining gated. The fixed record is represented transparently as an eight-byte little-endian
`{length, crc32c}` header plus a 64-byte key. Absolute FAL partition/device pointers and the
indirect flash vtable are replaced by an explicit initialized store object and typed read callback;
the checksum is computed by the existing local `r1_crc32_castagnoli` implementation. The result
retains stored length, stored checksum, computed checksum, and a typed failure reason. Tests cover
lazy initialization, valid load, CRC mismatch with retained key bytes, absent record, failed flash
read, undersized output, and unavailable storage.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x0006AD80` | `gomore_primitives_pkey_load` | lazily bind an explicit pKey store, read the fixed header/key record, compute the exact non-reflected CRC32C, and accept only a 64-byte record with matching checksum |

The previous-state restorer `0x0006AFB0` adds 180 declared bytes, bringing the primitive module
to 277 functions / 30,374 declared bytes and the combined local total to 291 entries, with 71
remaining gated. After the now-local pKey validation, it probes the recovered four state slots in
newest-first order `3,2,1,0`. Slot addresses use the exact relative formula
`72 + slot * (align4(state_length) + 8)`, headers are eight bytes, and only a non-erased exact
length match is accepted. The local implementation exposes slot and record-offset results, checks
provider read failures, and retains state output on no-match paths without any absolute FAL or
device-vtable dependency.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x0006AFB0` | `gomore_primitives_previous_state_restore` | validate the fixed pKey record, probe four aligned previous-state slots newest-first, and restore the first exact-length payload through the explicit store binding |

The cubic coefficient solver `0x0006808C` adds 256 declared bytes, bringing the primitive module
to 278 functions / 30,630 declared bytes and the combined local total to 292 entries, with 70
remaining gated. It preserves the stock Float32 reduction into the depressed-cubic `q`, `p³`, and
discriminant terms; constructs the exact `(-0.5, sqrt(3)/2)` root of unity; splits the signed
discriminant root; and delegates the final three candidates to the now-local Cardano assembler.
All power/trigonometric operations remain explicit typed toolchain bindings. A triple-root fixture
pins all nine power calls and all three candidate words exactly.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x0006808C` | `gomore_primitives_cubic_candidates` | reduce four cubic coefficients into paired Cardano radicals, build the complex roots of unity, and commit the three filtered candidate roots through transparent local primitives |

The complete sleep-algorithm initializer `0x0006FEA0` adds 302 declared bytes, bringing the
primitive module to 279 functions / 30,932 declared bytes and the combined local total to 293
entries, with 69 remaining gated. The reconstruction replaces the stock engine/seed global with
explicit configuration, separates the 32-bit target binding from the host previous-state pointer,
and retains the exact seed-clear-random-authorization order. It scans all 736 previous-state bytes
when the leading word is nonnegative, rejects any nonzero byte with status `-5`, or marks an all-zero
record active through bit 31. The four filter banks, 0x3894-byte nested state, runtime word,
previous-state cache, scattered user-profile fields, composite child initializer chain, and default
profile transition are all composed from already-transparent local bodies. Tests cover successful
restore and clean-state activation, dirty-state retry, version rejection, profile rejection, exact
status/random/binding fields, child callback counts, output pointers, and preflight bounds.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x0006FEA0` | `gomore_primitives_sleep_algorithm_initialize` | authorize and initialize the complete sleep engine using explicit random, version, previous-state, target-binding, time-configuration, and child-initializer dependencies |

The sleep-stage run-edge smoother `0x0008F0F0` adds 320 declared bytes, bringing the primitive
module to 280 functions / 31,252 declared bytes and the combined local total to 296 entries, with
66 remaining gated. It composes the already-local 40-slot target-run extractor, retains both
target-zero edge policies and the target-one long-run rewrite, and makes the recovered
`0x80000001` odd-remainder test explicit as parity over nonnegative spans. Tests pin overlapping
leading/trailing replacement for a short zero run, both 14-element stage-2 edges around a 43-value
stage-1 run, and invalid input bounds.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x0008F0F0` | `gomore_primitives_smooth_target_run_edges` | find up to forty target runs and apply the exact policy-dependent leading/trailing stage replacement rules |

The dormant speed-dynamics baseline `0x00090C54` adds 334 declared bytes, bringing the primitive
module to 281 functions / 31,586 declared bytes and the combined local total to 297 entries, with
65 remaining gated. Its public contract replaces the stock 40-byte state record with explicit
first/second parameters and a flag word. The implementation retains the subunit normalization,
`0x0440` calibration switch at the raw Float32 `1.25` boundary, cubic/linear/quadratic operation
order, five-place rounding, and final scale. The already-local decimal rounder now also exposes the
recovered VFP saturation behavior for NaN and signed overflow. Tests cover ordinary and flagged
production-emulation fixtures, both sides of the exact threshold, negative/NaN rejection,
rounder saturation, and a missing power binding.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x00090C54` | `gomore_primitives_speed_dynamics_baseline` | combine explicit calibration parameters with the normalized input and auxiliary value using the exact flag-dependent dynamics formula and decimal reduction |

The mode-zero graph-state wrapper `0x00072BE0` adds 104 declared bytes, bringing the primitive
module to 282 functions / 31,690 declared bytes and the combined local total to 298 entries, with
64 remaining gated. It allocates and clears the exact 0x2DC-byte record, invokes the still-explicit
graph dispatcher binding, carries the initialized word at `+0x1E0` to the descriptor base at
`+0x238`, and remaps descriptor payload bindings with the recovered stride formula. Host pointers
and target 32-bit bindings are deliberately separate; malformed counts, source extents, target
slots, and binding overflow fail before allocation. Tests pin two remaps, the carried word, callback
ordering, exact allocation size, and preflight rejection.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x00072BE0` | `gomore_primitives_allocate_mode0_state_remap` | allocate the mode-zero graph state through explicit providers and remap caller-owned descriptor payload bindings into its 41-slot output table |

The locomotion crossing wrapper `0x00056CF4` adds 124 declared bytes, bringing the primitive
module to 283 functions / 31,814 declared bytes and the combined local total to 301 entries, with
61 remaining gated. It composes the local eight-slot carried-positive baseline, invokes the
remaining estimator through a typed callback in exact mode-2 then mode-1 order with `-1.0`, and
applies the recovered unsigned Float32-bit gate that accepts the encoded 60...240 interval.
Tests pin baseline propagation, mode order, inclusive endpoints, invalid output replacement with
zero, short input/cursor preflight, and absence of provider calls on rejection.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x00056CF4` | `gomore_primitives_locomotion_crossing_wrapper` | derive the eight-sample baseline, run both crossing-estimator modes, and retain only raw-Float32 outputs in the exact encoded interval |

The final sleep-record publication wrapper `0x0004A704` adds 134 declared bytes, bringing the
primitive module to 284 functions / 31,948 declared bytes and the combined local total to 302
entries, with 60 remaining gated. Its provider structure makes the record resolver, three exact
log-mode samples, two diagnostic sinks, existing R1 acceptance predicate, event publisher, and
release operation explicit. The implementation retains the stock record fields at `+0x00`,
`+0x0C`, `+0x10`, and `+0x1E`, event `0x000D`, conditional diagnostic order, and unconditional
release after a successful lookup. It deliberately preserves the production `UXTH` length:
`0xFFE0 + 0x20` publishes a zero-length event rather than being silently rejected. Tests pin the
34-byte accepted record, drop-and-free path, exact provider order, wrapped zero length, disabled
no-op, and provider preflight.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x0004A704` | `gomore_primitives_final_sleep_record_publish` | resolve a final compact sleep record, replay its conditional diagnostics, apply an explicit acceptance predicate, publish event 13 with the exact wrapping UInt16 length, and always release the resolved record |

The dormant heart-rate/ratio wrapper `0x00094270` adds 142 declared bytes, bringing the primitive
module to 285 functions / 32,090 declared bytes and the combined local total to 303 entries, with
59 remaining gated. It clears the stock two-word filter output, calls the still-explicit integer
filter on state `+0x278` with exactly 1,000 ms, and selects its filtered first word only for status
1; every other status retains the raw integer HR at state `+0x1C`. The typed ratio descriptor
preserves the signed-integer-to-Float32 conversion, selected-speed choice at `+0x24` versus
`+0x2C`, threshold/bin pointers, zero fields, and the exact `0x4203` / `0x040C` call gate. Tests
pin filtered and fallback selection, descriptor offsets and values, gated non-invocation, callback
counts, interval, status, and short-state preflight.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x00094270` | `gomore_primitives_dormant_heart_rate_ratio_wrapper` | run the explicit dormant integer-HR filter, select filtered output only on status 1, build the exact typed ratio descriptor, and invoke its accumulator only under the recovered flag masks |

The dormant speed-root builder `0x00068D18` adds 176 declared bytes, bringing the primitive
module to 286 functions / 32,266 declared bytes and the combined local total to 304 entries, with
58 remaining gated. It reconstructs the exact six embedded Float32 constants and arithmetic order
that assemble the root coefficients from the two leading state parameters, primary value, and
auxiliary value. Mode zero dispatches the recovered three-coefficient quadratic form; every
nonzero mode dispatches the four-coefficient cubic form with leading bits `0x3E1704FF`. The power
operation and both already-reconstructed solver boundaries remain explicit typed callbacks. Tests
pin all coefficient words for ordinary mode-zero/mode-one fixtures, exact dispatch selection,
power-call count, state identity, and preflight without provider invocation.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x00068D18` | `gomore_primitives_dormant_speed_root_build` | assemble the exact dormant speed-dynamics polynomial coefficients and dispatch the quadratic or cubic solver according to whether mode is zero |

The motion-classifier composition wrapper `0x0005F4B6` adds 180 declared bytes, bringing the
primitive module to 287 functions / 32,446 declared bytes and the combined local total to 305
entries, with 57 remaining gated. It composes five already-local history/quality/selector helpers;
its formerly gated `0x0009413C` finalizer is now local and the wrapper accepts only that
finalizer's state-one estimator seam. The implementation
retains output byte `0xFE` initialization, elapsed 2...5 repeated gap shifts, elapsed >5 history
reset, exact eight-Float zero detection (including signed zero and NaN behavior), source-invalid
byte `+0x0C`, fallback output `{0xFF,0xFE,0}`, and the valid-path call order. Tests pin a valid
finalizer call, elapsed-three multi-shift state, elapsed-six reset/fallback, callback suppression,
and mutation-free preflight.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x0005F4B6` | `gomore_primitives_motion_classifier_update` | advance or reset the two five-byte histories for elapsed gaps, route invalid/zero features to the exact fallback, and otherwise run the local selector gates and finalizer |

The motion-classifier finalizer `0x0009413C` adds 270 declared bytes, bringing the primitive
module to 295 functions / 34,262 declared bytes and the combined local total to 313 entries,
with 49 remaining gated. It closes the classifier wrapper's former opaque finalizer seam. Its
typed state-one cadence-estimator callback can now bind the local `0x00058060` implementation. The
implementation preserves signed selector handling, truncating VFP Float32-to-Int32 conversion,
the state-two 121...219 and state-one 51...149 inclusive ranges, the raw Float32-bit comparison
against `80.0f`, both prior-cadence octave corrections, the 51...65 previous-feature correction,
and the preliminary/state/cadence five-sample history order. Tests pin truncation, the exact
`80.0f` boundary and one-ULP-above behavior, previous-feature correction, state-two smoothing,
callback suppression, and mutation-free preflight.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x0009413C` | `gomore_primitives_motion_classifier_finalize` | select and range-gate the state-specific cadence estimate, apply prior and previous-feature corrections, update all three five-sample histories, and publish the dominant mode/cadence pair |

The activity-state classifier `0x00096E74` adds 282 declared bytes, bringing the primitive
module to 296 functions / 34,544 declared bytes and the combined local total to 314 entries,
with 48 remaining gated. Its 249-Float first-difference workspace is caller-owned, the already
local sign-crossing-spacing and range-center/span helpers are composed directly; the four-output
statistics reducer `0x0006859C` is now local too and retains its existing typed callback seam. The
implementation preserves both mode branches and all seven raw Float32 comparison words:
`12.43`, `3.5`, `0.57`, `7.26`, `7.7`, `11.38`, and `25.5`. Tests pin callback order, modes and
cardinalities, exact difference construction, the low-statistic crossing/normalized-offset path,
the high-statistic secondary-statistic path, ordinary-mode acceptance, and mutation-free
preflight.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x00096E74` | `gomore_primitives_activity_state_classify250` | derive 249 adjacent differences from a 250-sample window and classify the ordinary or alternate activity state using explicit local features and a typed four-statistic reducer |

The dormant estimator cycle `0x000721B4` adds 304 declared bytes, bringing the primitive module
to 297 functions / 34,848 declared bytes and the combined local total to 315 entries, with 47
remaining gated. It composes the local speed smoother, both local dormant target veneers, speed
gate, rolling mean, and heart-rate/ratio wrapper through a typed logical input and provider bundle;
no stock pointer or opaque state blob is embedded. The implementation preserves all copied state
offsets, `0x1444`/bit-2/bit-3 routing, forced zero smoother input, 1000 ms smoother interval,
sample-index heart-rate fallback, prior-output commits, and the early signed `-1016` status. Tests
pin mode-zero and mode-one target routing, math/reducer call modes, smoothing, heart-rate filtering
and ratio accumulation, exact state commits, early callback suppression, and mutation-free
preflight.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x000721B4` | `gomore_primitives_dormant_estimator_cycle` | compose one bounded dormant speed and heart-rate estimator update, including target selection, rolling gates, early validation, and prior-state commits |

The sleep force-wake orchestrator `0x0006B50C` adds 318 declared bytes, bringing the primitive
module to 298 functions / 35,166 declared bytes and the combined local total to 316 entries, with
46 remaining gated. It replaces the stock implicit heap/global surface with typed allocation,
release, interval-preparation, optional mode-control, interval-dispatch, and final-publication
bindings. The 56-byte result record, 88-byte report workspace, and 2,880-byte timeline allocation
are explicit and zeroed, while the bit-3 publication gate and release ordering remain exact. Tests
pin complete publication, no-publication, first- and second-allocation failures, mode-control
selection, zeroed callback inputs, reverse allocation release order, and provider-free preflight.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x0006B50C` | `gomore_primitives_sleep_force_wake` | allocate and prepare a forced sleep interval, optionally disable mode four, and dispatch/publish a final record only when result flag bit three is set |

The central dormant root resolver `0x0008141C` adds 322 declared bytes, bringing the primitive
module to 299 functions / 35,488 declared bytes; after the adjacent tensor-cell and ratio-accumulator
reductions, the combined local total is 319 entries, with 43 remaining gated. It directly composes the already-local dynamics baseline, rational transform,
ordinary root builder, alternate root solver, and nearest-root selector. The implementation
preserves exact `0.554f` normalization, the `0x0440` flag mask, signed raw-bit `1.25f` branch,
positive baseline ratio, mode-zero two-root mean, nonzero-mode three-root mean, zero-root fallback,
and ordered-positive final clamp. Tests pin both flagged solver routes, unflagged ratio selection,
two- and three-root averaging, callback cardinalities, and mutation-free preflight.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x0008141C` | `gomore_primitives_dormant_root_resolve` | normalize a dormant target and resolve it through the flag-selected baseline, ordinary-root, or alternate-root path with exact root aggregation semantics |

The dormant ratio accumulator `0x00096634` adds 344 declared bytes, bringing the primitive module
to 300 functions / 35,832 declared bytes; after the locomotion-summary reduction, the combined
local total is 320 entries, with 42 remaining gated. Its typed state replaces the stock `+0x210...+0x257` SRAM layout while retaining
the all-sample mean, strict signed-raw-bit speed-above-4 gate, exact `1.22f`/`1.32f` profile
weights, qualified square sum and two running means, raw-bit 30-sample/dispersion decisions,
secondary-bin emission, and four-field reset. The only math seam is an explicit power callback;
both histogram writes compose the already-local six-bin accumulator. Tests pin the strict speed
boundary, both profile weights, exact primary sums, stable 30-sample reset, lower-all-mean
secondary route, provider cardinality, and mutation-free preflight.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x00096634` | `gomore_primitives_dormant_ratio_accumulator` | maintain all/qualified HR-speed moments, update the primary ratio histogram, and reset or emit to the secondary histogram at the exact 30-sample dispersion boundary |

The locomotion summary updater `0x0004834A` adds 350 declared bytes, bringing the primitive module
to 301 functions / 36,182 declared bytes; after the sensor-update reduction, the combined local
total is 321 entries, with 41 remaining gated. It replaces the recovered 622-byte offset layout with typed four-channel,
eight-slot histories. Four integer means, four sample standard deviations, the fourth-channel
range, and four adjacent-difference means compose the already-local primitives in exact stock
call/store order before the modulo-eight cursor advances. The recovered caller's fixed 25-sample
domain is explicit, and square root remains a typed toolchain binding. Tests pin all thirteen
outputs, square-root inputs/order, slot-seven wrap, next-slot reuse, and mutation-free preflight.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x0004834A` | `gomore_primitives_locomotion_summary_update` | append four means, four sample deviations, one range, and four adjacent-difference means to thirteen synchronized eight-slot histories |

The sensor-update orchestrator `0x00094384` adds 350 declared bytes, bringing the primitive module
to 302 functions / 36,532 declared bytes and the combined local total to 321 entries, with 41
remaining gated. Its explicit state/configuration replaces the stock engine globals and previous
update record. Diagnostics, input application, error reporting, and output snapshotting are typed
providers; runtime/version validation and nearby timestamp clamping compose already-local
functions. The implementation preserves diagnostics-before-status ordering, negative initializer
exit, first-timestamp `candidate - 1` seeding, stale `-4`, unconditional snapshot/commit after an
attempted update, and the recovered high-bit-preserving counter increment. Tests pin success,
negative apply status, ±3-second substitution, stale rejection, initializer/runtime failures,
callback order, high-bit behavior, and provider-free preflight.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x00094384` | `gomore_primitives_sensor_update_orchestrate` | diagnose, validate, normalize, apply, snapshot, and atomically commit one timestamped sensor update with exact stale/error semantics |

The motion-gate accumulator `0x0005F264` adds 352 declared bytes, bringing the primitive module
to 303 functions / 36,884 declared bytes and the combined local total to 322 entries, with 40
remaining gated. Its typed state replaces the stock 36-byte record: eighteen one-byte circular
buckets, a pending Float32 sum, signed pending count, and last emitted bucket. A crossed 30-second
boundary emits the pending average clamped to `[0, 255]`; with no pending sample it repeats the
last bucket. Gaps below 540 seconds fill every crossed bucket with that last value, while gaps of
540 seconds or more clear the whole record through the already-local 36-byte reset behavior. The
score composes `gomore_primitives_circular_u8_dot18`, and readiness/polarity preserve the stock
output-byte contract and exact `0x3FBF9D06` (`1.496979475f`) positive-bias predicate. After a
boundary, the pending accumulator resets before the current nonnegative sample is ingested.

The stock weight pointer at `0x0005F3D0` resolves to the explicit eighteen-word Float32 vector at
`0x000BD2E4`: `BC74E45F BC307364 BC3AABE4 BC425615 BC36586D BC2E6D76
BC2ABB77 BC3C334A BC5C10B1 BC43123B BC3D049D BC5251C5 BC50B8CE BC795147
BC92BF25 BCD9F826 BD120A28 BD8D8A4A`. The reconstructed API takes that vector as a checked typed
input, so no hidden model region or stock binary blob is required. Tests pin boundary and
non-boundary updates, short-gap repetition, the 540-second clear, both clamp limits, unchanged
non-updated outputs, current-sample ordering, and mutation-free invalid-input rejection.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x0005F264` | `gomore_primitives_motion_gate_accumulate` | aggregate nonnegative samples into 30-second circular motion buckets, fill or reset elapsed history, and publish the exact weighted gate score and bias predicate |

The authorization-parameter setup `0x0006B27C` adds 374 declared bytes, bringing the primitive
module to 304 functions / 37,258 declared bytes and the combined local total to 323 entries, with
39 remaining gated. It composes the already-local cached-or-derived device UUID and 64-byte pKey
copy helpers, an explicit timestamp binding, and a typed authorization callback for the still-gated
SDK parser at `0x0008EA0C`. The local 28-byte UUID and 68-byte key records are zero-initialized,
the derived UUID retains the exact `address/device-id-0/device-id-1` lowercase-hex order, the UUID
length is measured only after a valid key is obtained, and timestamp acquisition precedes the
authorization call. A pKey-load failure returns stock status `-1` without acquiring time or
calling authorization; otherwise the callback status is returned unchanged.

The typed authorization record exposes only key pointer, UUID pointer, one-byte UUID length, and
timestamp. The reconstruction deliberately omits the stock plaintext `%s` pKey diagnostic: tests
copy sensitive stack data only inside the callback fixture and the production API provides no key
log or export sink. Tests pin derived and cached UUID routes, loader and cached pKey routes, exact
parameter contents, callback order/cardinality, result forwarding, the `-1` failure path, and
mutation-free provider preflight.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x0006B27C` | `gomore_primitives_auth_parameters_setup` | assemble zeroed UUID/pKey records, obtain timestamp, and invoke the typed authorization provider with exact failure and status-forwarding behavior |

The local-maximum statistics reducer `0x0006859C` adds 382 declared bytes, bringing the primitive
module to 305 functions / 37,640 declared bytes and the combined local total to 324 entries, with
38 remaining gated. It scans indices `radius...count-radius-1`; a candidate remains a peak unless
some value in its inclusive `±radius` neighborhood is strictly greater, so equal plateaus retain
every candidate exactly as the stock `VCMPE`/`BLE` loop does. The four outputs are mean peak
spacing, population deviation of peak spacings, mean peak value, and population deviation of peak
values. Fewer than two peaks yield `-1` for both spacing outputs; zero peaks also yields `-1` for
both value outputs. `powf(value, 2.0f)` and `sqrtf` remain checked typed math bindings, including
the stock integer conversion after each accumulated squared spacing.

Tests pin three known peaks and two equal spacings, exact means and variance inputs, the one-peak
sentinels, callback cardinality, and mutation-free invalid geometry. The already-local activity
window classifier can now bind this reducer directly; no model data or private classifier state is
embedded in the implementation.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x0006859C` | `gomore_primitives_peak_statistics` | identify non-strict local maxima and emit exact spacing/value means and population deviations with stock cardinality sentinels |

The direction-change statistics reducer `0x0008F4E8` adds 390 declared bytes, bringing the
primitive module to 306 functions / 38,030 declared bytes and the combined local total to 325
entries, with 37 remaining gated. It consumes `difference_count + 1` samples through one of the
three recovered modes (Float32, Int16, or Int32), derives consecutive differences, and groups only
strictly positive-with-positive or negative-with-negative pairs into a continuing run. Zero,
unordered, or opposite-sign comparisons close the prior run. Each closure increments the signed
one-byte direction count, adds the signed one-byte run length to the signed 16-bit completed-run
sum, and accumulates `abs(current - previous) / run_length`. A second one-byte count increments
only when the normalizer is positive and `abs(current)` strictly exceeds
`normalizer * threshold_scale`.

The outputs preserve the exact stock contracts: fewer than six differences writes `-1` to both
counts and both Float32 values; otherwise normalized variation is zero for a zero normalizer and
the completed-run mean is zero when no transition closed. Tests pin the Int32 mixed-sign route,
strict threshold boundary, run-length weighting, Int16 no-transition route, Float32 short-input
sentinels, all output values, and mutation-free invalid-mode rejection. No model data or external
algorithm dependency is involved.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x0008F4E8` | `gomore_primitives_direction_change_statistics` | compute typed consecutive-difference sign runs, transition variation, completed-run length, and strict threshold counts with exact short-input sentinels |

The active-only dormant heart-rate filter `0x00070498` adds 390 declared bytes, bringing the
primitive module to 307 functions / 38,420 declared bytes and the combined local total to 326
entries, with 36 remaining gated. Its typed state is exactly 100 bytes: five control bytes,
missing counter, last effective integer input, Float32 average, and twenty Float32 history slots.
The implementation preserves the inclusive 700...1300-ms gate; enable byte; statuses `0x1771`
through `0x1775`; three-positive streak; maximum three missing updates; maximum twenty unchanged
updates; strict raw-bit rise/fall clamps at `+6` and `-7`; and the recovered lagging average while
the history fills. At nineteen stored samples it reproduces the unusual stock shift/update order:
average the prior nineteen plus the current effective input, shift, then duplicate the current
value into history slots eighteen and nineteen while retaining count nineteen.

The final average-to-integer conversion uses the established dormant-estimator truncating VFP
semantics (`71.5f -> 71`), confirmed by the pinned production-Thumb emulator fixture. Tests mirror
that evidence for interval boundaries, inactive and initial-invalid paths, exact rise/fall clamps,
four-sample fill behavior, missing reset/re-entry, unchanged-run statuses, twenty-two-sample rolling
history, duplicate tail slots, and raw-output preservation. The already-local heart-rate/ratio
wrapper can now bind this function directly.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x00070498` | `gomore_primitives_dormant_heart_rate_filter_update` | validate cadence/enable state, clamp and average integer heart rate through the exact twenty-slot state machine, and publish stock statuses plus filtered/raw outputs |

The six-channel circular-window scorer `0x00056A0C` adds 390 declared bytes, bringing the
primitive module to 308 functions / 38,810 declared bytes and the combined local total to 327
entries, with 35 remaining gated. It sums the exact preceding `window_count` samples in each of
six signed-Int16 circular channels. The first three sums retain their channel order, while the
last three are sorted into maximum, middle, and minimum before the linear score is evaluated.

No stock model blob is admitted. The clean API instead requires an explicit typed model containing
six Float32 weights, bias, scale, empty-window value, and minimum output. The output uses the
established dormant-estimator truncating Float32-to-Int32 conversion and clamps to that explicit
minimum and the stock hard maximum of 32,000. Tests pin circular wraparound, channel ordering and
descending extrema, the empty-window path, both output clamps, and mutation-free invalid-window
rejection.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x00056A0C` | `gomore_primitives_six_channel_ring_score` | sum six preceding circular channels, order the final three extrema, apply an explicit six-weight linear model, truncate, and clamp to the recovered output bounds |

The state-one cadence estimator `0x00058060` adds 390 declared bytes, bringing the primitive
module to 309 functions / 39,200 declared bytes and the combined local total to 328 entries,
with 34 remaining gated. Its three Float32 inputs are the classifier's first, middle, and latest
cadence features. Exact unsigned bit arithmetic admits first/latest strictly between 50 and 140
and middle strictly between 40 and 140; adjacent differences below ten set the consensus byte.

The selector returns middle by default. A consensus above 80 returns immediately. Below 80 it
recognizes a latest sample near twice middle, using strict ten and fifteen thresholds plus the
first/latest consistency check. A final low-middle crossing correction selects first when first
is within six of twice latest. All subtraction occurs in Float32 before the stock absolute-double
comparison. Production-Thumb fixtures and host tests pin the exact range edges, consensus
threshold, both octave thresholds, crossing correction, and null-consensus fallback. The classifier
finalizer now treats a null callback as an explicit request for this local implementation, so its
default build path has no opaque estimator dependency.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x00058060` | `gomore_primitives_state1_cadence_estimate` | range-gate three cadence features, report strict adjacent consensus, and apply the recovered octave, prior-sample, and low-middle crossing selections |

The locomotion transition accumulator `0x000761F8` adds 426 declared bytes, bringing the
primitive module to 310 functions / 39,626 declared bytes and the combined local total to 329
entries, with 33 remaining gated. Its explicit typed state contains the accumulated integer,
initialized flag, and Float32 estimate; no model data or private state is involved. Before
initialization it requires the recovered Float32 shape ratio, integer current/accumulated ratio,
target-times-2.5 ceiling, and previous-value consistency within two. The shape ratio's 0.6 and
integer ratio's strict 0.7 raw-bit thresholds retain the stock boundary behavior.

Once initialized, the next accumulated value must lie strictly between 0.9 and 1.1 times the
estimate and retain the same ±2 consistency gate. Accepted updates replace the integer total and
compute the estimate as `new_total * 0.25 + prior_estimate * 0.75` in binary64 before the final
Float32 conversion. The pinned production-Thumb fixture and host tests cover successful initial
and steady-state updates, both ratio gates, target rejection, consistency rejection, steady-state
range rejection, exact estimate bits, and mutation-free invalid-input rejection.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x000761F8` | `gomore_primitives_locomotion_transition_accumulate` | initialize or advance a typed locomotion transition total through the recovered shape, integer-ratio, target, consistency, and steady-state estimate gates |

The locomotion control-point extractor `0x00056DC0` adds 426 declared bytes, bringing the
primitive module to 311 functions / 40,052 declared bytes and the combined local total to 330
entries, with 32 remaining gated. The stock `0x6C8`-byte parent-state offsets are replaced by an
explicit array of at most forty `{position, first, second}` samples plus typed configuration and
workspace. The workspace exposes the exact forty UInt16 positions, forty Float32 controls, 250
expanded Float32 samples, and paired twenty-byte feature-index arrays; no absolute pointer or
opaque state block remains.

Adjacent positions are retained only when their magnitude lies strictly between `0.6` and `1.5`
times the Float32 sample period. Mode one stores the signed position delta. Every other mode stores
the Float32 first-minus-second difference, replacing it with the explicit scale when its magnitude
is at most one quarter scale or it is not below twice scale. The recovered minimum retained count
is `0.7 * (500.0f / sample_period)`. Insufficient input returns stock status one with outputs
`{-1, 0}`; sufficient input composes the already-local half-position expander and invokes the
still-gated `0x00068840` feature reducer only through a typed callback seam.

Production-Thumb fixtures pin both mode-one and mode-two filtering, controls, status, and output
sentinels. Host tests additionally pin successful expansion/provider routing, exact workspace
contents, insufficient-provider suppression, and mutation-free capacity rejection.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x00056DC0` | `gomore_primitives_locomotion_control_extract` | filter adjacent typed locomotion samples, form mode-specific controls, enforce the recovered minimum count, expand 250 values, and dispatch the typed feature reducer |

The final public sleep-record serializer `0x0008FA3C` adds 456 declared bytes, bringing the
primitive module to 312 functions / 40,508 declared bytes and the combined local total to 331
entries, with 31 remaining gated. Its stock heap allocation is replaced by a bounded caller-owned
buffer, and the already-local stable temperature reducer is represented by an explicit UInt16
input. The typed record exposes start/end timestamps, sleep type, efficiency, score, REM/light/deep
fractions, five minute totals, and the bounded stage timeline; no parent-state offsets, allocator,
absolute address, or opaque record remain.

The implementation preserves the stock negative-start clamp, exact Float32 `100.0f` and `60.0f`
scales, unsigned conversion toward zero, low-byte/low-halfword storage, derived wake percentage,
zeroed reserved/timezone fields, and mode-one-only detailed payload. It composes the already-local
two-bit stage encoder and stores its exact UInt16 compact count. A production-Thumb fixture pins
the complete 35-byte long record, the header-only short record, the 64-sample run split, and the
stock allocation length. Host tests additionally pin caller-capacity rejection without mutation.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x0008FA3C` | `gomore_primitives_final_sleep_record_serialize` | serialize the final public sleep header and mode-one detail fields into caller-owned storage, then compact the bounded stage timeline through the local two-bit run encoder |

The GoMore output/lifecycle orchestrator `0x0006C294` adds 456 declared bytes, bringing the
primitive module to 313 functions / 40,964 declared bytes and the combined local total to 332
entries, with 30 remaining gated. The seven stock 16-byte slot records become a seven-bit active
mask; engine offsets `+0x70`, `+0x62`, `+0x78`, and `+0xA8` become typed lifecycle, PPG-request,
activity, and explicit no-op paths. Input refresh, engine update, activity publication, R1 sleep
status publication, final-record composition/publication, and slot authorization are explicit
typed bindings. The two input-ready flags are caller-owned Booleans rather than fixed RAM bytes.

The implementation preserves ascending slot dispatch, slots one/four/five/six having no route,
slot two's recovered no-op, period-on precedence over period-off/final, the final-result branch
nested under period-off, signed PPG-request comparison, inverted prior-request authorization for
slot four, successful-result input clearing, and allocation-failure suppression of the same-cycle
PPG transition. Production-Thumb fixtures pin off/final, on-precedence, unchanged PPG, and failed
workspace paths. Host tests add activity ordering, result-not-ready retention, and callback
preflight.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x0006C294` | `gomore_primitives_output_lifecycle_dispatch` | refresh and update the typed engine, dispatch active activity/sleep slots, compose final sleep output, reconcile the PPG authorization request, and clear successful input readiness |

The dormant alternate-root solver `0x00069DC8` adds 180 declared bytes, bringing the primitive
module to 288 functions / 32,626 declared bytes and the combined local total to 306 entries, with
56 remaining gated. It composes the already-local rational transform and nearest-nonzero root
selector with the already-local quadratic/cubic solver boundary. The implementation preserves
the exact Float32 coefficient order, mode-zero quadratic versus every-nonzero-mode cubic dispatch,
root slots at state offsets `0x18...0x20`, and the unusual signed-raw-bit comparison against
`0x3FA00000`: only a selected root whose bit pattern compares greater is multiplied by
`0x3F333333`, after which nonpositive and unordered values become zero. Tests pin production
coefficient words for both modes, exact `1.25` retention, one-ULP-above attenuation, negative and
NaN clamping, and mutation-free provider preflight.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x00069DC8` | `gomore_primitives_dormant_alternate_root_solve` | derive the rational root target, solve the exact alternate quadratic/cubic coefficient form, select the nearest retained root, and apply the stock raw-bit attenuation and positivity rules |

The mode-one dormant speed target `0x00067488` adds 196 declared bytes, bringing the primitive
module to 289 functions / 32,822 declared bytes and the combined local total to 307 entries, with
55 remaining gated. It composes the already-local flagged auxiliary transform with typed reducer
and finalizer callbacks for the two still-gated descendants. The implementation preserves root
clearing on every call, first-call history seeding, sequential current-minus-previous input,
arbitrary nonzero initialized-byte handling, mode forwarding, exact `3.6` divide/multiply words,
and the stock ordered-negative-only output clamp that retains NaN. Tests pin unflagged and flagged
auxiliary paths, first and later calls, all mutated state words, callback order and inputs,
negative/NaN outputs, and mutation-free preflight.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x00067488` | `gomore_primitives_dormant_speed_mode1_target_update` | update the mode-one dormant speed history, run the exact local auxiliary selection and typed reduction/finalization chain, then scale and clamp the written result |

The fixed-mode veneer `0x0002938A` adds 204 scatter-loaded declared bytes, bringing the primitive
module to 290 functions / 33,026 declared bytes and the combined local total to 308 entries, with
54 remaining gated. Its entire entry behavior is the recovered argument move, constant mode-one
injection, and tail dispatch into the local `0x00067488` target. The focused target fixtures invoke
the veneer and pin the forwarded mode and all target effects.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x0002938A` | `gomore_primitives_dormant_speed_mode1_target_veneer` | forward the dormant speed target inputs with the exact constant mode value one |

The mode-zero dormant speed target `0x0006825C` and its fixed-mode veneer `0x00029382` add 470
declared bytes, bringing the primitive module to 292 functions / 33,496 declared bytes and the
combined local total to 310 entries, with 52 remaining gated. The target preserves the exact
`atan(first/100)` geometry, cosine/sine projection of `selected/3.6`, first-call projected-power
history, root clearing, flagged auxiliary conversion, shared reducer/finalizer order, final scaling,
and ordered-negative-only clamp. The veneer supplies the recovered constant mode zero. Tests pin
first/subsequent provider call counts, projected inputs and history words, mode forwarding, output
clamping, and mutation-free preflight.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x0006825C` | `gomore_primitives_dormant_speed_mode0_target_update` | project the dormant speed inputs through the exact angle geometry, seed first-use history, and run the shared reduction/finalization chain |
| `0x00029382` | `gomore_primitives_dormant_speed_mode0_target_veneer` | forward the dormant speed target inputs with the exact constant mode value zero |

The sleep-graph family dispatcher `0x000340A0` adds 236 declared bytes, bringing the primitive
module to 293 functions / 33,732 declared bytes and the combined local total to 311 entries, with
51 remaining gated. The two large graph builders remain typed callbacks; the family selection,
three-by-eight dimension binding, five exact 24-byte output slots, arena-cursor flow, recurrent
executor word, and mode-two-only softmax word are transparent. Tests pin mode-zero and mode-two
builder selection, every constructor argument and slot, cursor sequencing, conditional softmax
mutation, and invalid-family preflight without callback invocation.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x000340A0` | `gomore_primitives_sleep_graph_family_dispatch` | select the zero/nonzero model builder and assemble the exact family-dimensioned recurrent/dense output descriptor stack with explicit executor bindings |

The common host-input adapter `0x00094590` adds 260 declared bytes, bringing the primitive module
to 294 functions / 33,992 declared bytes and the combined local total to 312 entries, with 50
remaining gated. It composes the two already-local raw-optical/accelerometer resamplers and leaves
only the main `0x0005FF94` update core as a typed callback. Caller-owned scratch and explicit target
bindings replace stock stack addresses while preserving every engine field: timestamp/timezone,
raw output/source pointers, failure and wear flags, sample/channel/invalid fields, three
accelerometer outputs, direct heart rate, legacy word, mode-two bytes, and elapsed-time core call.
The HRV pointer/count remain present in the typed input and intentionally unread. Tests pin all
mutated offsets, four resample/filter calls, scratch results, mode-two behavior, elapsed time, and
preflight without core invocation.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x00094590` | `gomore_primitives_host_input_adapter_update` | translate the complete host input ABI into exact engine fields and caller-owned resampled scratch before invoking the typed main update core |

The logger's global
configuration, varargs formatter, and output code pointer are explicit typed bindings. Stock can
overflow its 256-byte aggregate message when a formatter reports 246 or 247 characters and CRLF
is appended; the local body appends the suffix only when it fits. Tests pin enabled/disabled mask
paths, exact prefix/suffix/wrapper format, all three filter-state offsets and outputs, zero-sample
status, 225-value history retention, negated/zero tails, callback counts, and provider bounds.

The final-sleep report builder `0x00069644` adds 488 declared bytes, bringing the primitive
module to 314 functions / 41,452 declared bytes and the combined local total to 333 entries,
with 29 remaining gated. Its stock engine, interval, 88-byte report, configuration-table record,
and heap-owned stage vector become typed interval/configuration input plus caller-owned output and
stage storage. The now-source-owned `0x00081040` stage refiner remains an explicit callback; packed
timeline extraction, interval validation, sleep statistics, score calculation, and leading-awake
history extension compose already-local behavior directly.

The implementation preserves the short-versus-long wire type, configuration-byte range extension,
30-second stage geometry, refinement duration, all report statistics and score fields, and the
stock leading-awake adjustment: halve the leading run, clamp its Float32 bit pattern to
`[0.5, 10.0]`, convert it to half-minute slots, move the start timestamp backward, and recalculate
the report after prepending awake stages. Production-Thumb evidence pins a 30-stage all-light
report over `900...1800`, one refiner call, every exposed statistics field, and score
`43.7471466`. Host tests additionally pin two-slot leading-awake extension, the short-report path,
invalid-interval status, caller-capacity preflight, and output-pointer preservation.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x00069644` | `gomore_primitives_final_sleep_build` | validate the selected interval, extract and refine its bounded stage timeline, calculate the final report and score, and apply the stock leading-awake start extension in caller-owned storage |

The dual-moving-average extrema collector `0x000647C4` adds 498 declared bytes, bringing the
primitive module to 315 functions / 41,950 declared bytes and the combined local total to 334
entries, with 28 remaining gated. The stock Float32 input, window sizes, two 20-byte index lists,
and byte counts become bounded caller-owned inputs and outputs. It maintains both edge-replicated
rolling sums, uses the strict short-average-greater-than-long-average state, tracks a maximum while
that state is active and a minimum while inactive, and publishes an extremum only when the state
changes. The final incomplete run is intentionally not emitted.

Production-Thumb fixtures pin both stock caller window pairs (`25/6` and `38/12`): a 250-sample
triangle produces twelve maxima at `10, 30, ... 230` and thirteen minima at `0, 20, ... 240`.
A high-frequency square wave pins the stock 20-entry overflow status and zeroed published counts.
The local implementation additionally stages results internally so an overflow cannot expose the
stock routine's partially written index lists, and preflights capacities without mutation.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x000647C4` | `gomore_primitives_moving_average_extrema_indices` | collect bounded maximum/minimum indices at strict transitions between two edge-replicated moving averages |

The shared dormant-root reducer `0x000888A0` adds 500 declared bytes, bringing the primitive
module to 316 functions / 42,450 declared bytes and the combined local total to 335 entries,
with 27 remaining gated. The state record is a typed-length byte boundary and the Arm math leaves
(`atanf`, `cosf`, and `powf`) are explicit callbacks. Every algorithm descendant is already local:
the energy core/scaler, flag-dependent speed baseline, rational clamp, kinetic quadratic
difference, cubic mode term, and decimal rounding.

The implementation preserves the zero-secondary fast path, twice-evaluated cosine, projected
primary, small-derivative suppression below twice the energy core, signed raw-bit `primary <= 1`
branch, flag-dependent `1.26` baseline, exact `165` and `9.8` constants, prior-kinetic downweight,
baseline delta gate, optional cubic term, two-pass positive rounding to three decimal places, and
history writes only on the high-primary path. Production-Thumb fixtures pin exact low-zero,
suppressed-derivative, retained-derivative, high-primary, mode-one, and flagged-mode output words,
including projected-primary and kinetic state. Host tests add callback counts and mutation-free
provider/length preflight.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x000888A0` | `gomore_primitives_dormant_root_reduce` | project the speed vector, suppress insignificant derivatives, compose the flag/mode-dependent energy terms, round the positive result, and update high-primary kinetic history |

The authorization/shared-stream dispatcher `0x00049410` adds 506 declared bytes, bringing the
primitive module to 317 functions / 42,956 declared bytes and the combined local total to 336
entries, with 26 remaining gated. The stock global record array becomes seven typed slots with
explicit enable/disable callbacks; the four sensor-stream handles, idle timer, HR/HRV cleanup
state, and two auxiliary handles are caller-owned. Named sensor-stream registration/unregistration
and deferred-timer creation/deletion remain explicit provider operations over the already-local
framework rather than embedded function pointers or absolute RAM.

The implementation preserves unchanged/invalid/uninitialized rejection, four ascending shared
requirements, first-user registration, last-user teardown, enable callback before the active-bit
store, disable callback after teardown, HR reset on the third stream, HRV/auxiliary reset on the
fourth, and the inverted 1,000 ms idle timer: create only when every slot is inactive and delete
when activity resumes. Production-Thumb fixtures pin exact `acc`, `raw_hr`, `hr`, `hrv` order,
handle retention across two slots, all cleanup fields, timer transitions, and return values. Host
tests additionally pin callback order and provider preflight.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x00049410` | `gomore_primitives_authorization_dispatch` | change one authorization slot, reconcile its four shared sensor streams, run slot callbacks, reset released HR/HRV state, and maintain the all-idle timer |

The manager's four exact topic callbacks and readiness barrier are now reduced through the typed
`gomore_primitives_topic_*` state/API. This adds the recovered `-Y/X/Z` accelerometer transform,
raw-optical UInt32 conversion, direct-HR Float32 staging, four-value HRV lane, acc/raw barrier, and
successful-update cleanup without embedding stock pointers. The available Zephyr `"acc"` stream
can feed a dormant exact `"gomore"` batch listener; the other three producers and engine execution
remain fail-closed. Full byte hashes, packet layouts, safety divergences, and tests are in
[`GOMORE-TOPIC-INPUT-CORRELATION.md`](GOMORE-TOPIC-INPUT-CORRELATION.md).

The 25-sample locomotion window preprocessor `0x0005ED14` adds 518 declared bytes, bringing the
primitive module to 318 functions / 43,474 declared bytes and the combined local total to 337
entries, with 25 remaining gated. Three Float32 axis pointers and the unavailable flag become
typed input; the `0x26E` state and `0x3E` output are bounded caller-owned records. The downstream
`0x00067E4C` classifier remains an explicit callback, while circular-slot advance, missing-window
initialization, mode-eight reset, summary statistics, and all history transformations are local.

The implementation preserves elapsed-window padding, the unavailable-input extra advance,
`>8` hard reset, signed warm-up counter decrement, Float32-to-Int16 axis conversion, wrapped
three-square magnitude and square root, 200-sample 25-position shift, reverse-tail mirror padding,
all exact raw summary offsets and cursor movement, seven-block first-window replication, zero-mean
slot recount, and the fewer-than-five-missing classifier gate. The existing production-Thumb
locomotion fixture now asserts five steady updates, exact magnitude tails, gap/missing mirror
behavior, output flags, and reset state. Host tests pin constant 3/4/0 magnitude, raw offsets,
classifier routing, missing output, and mutation-free length preflight.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x0005ED14` | `gomore_primitives_locomotion_window_preprocess` | pad elapsed locomotion windows, convert one 25-sample axis frame, maintain magnitude/summary histories, and route complete windows to the typed classifier |

The SDK authorization parser `0x0008EA0C` adds 528 declared bytes, bringing the primitive module
to 319 functions / 44,002 declared bytes and the combined local total to 338 entries, with 24
remaining gated. The stock absolute decrypt-key addresses and mutable RAM dispatch tables become
two caller-supplied 32-byte decrypt keys plus typed message-match, four field-parser, and three
validator callbacks. No stock key, authorization token, executable bytes, or absolute firmware
pointer is incorporated.

The implementation preserves the exact trailing-16-of-24 UUID selection and `a`...`f` uppercase
normalization, bounded 64-byte pKey copy and Base64 decode, first/second decrypt fallback, exact
four-field gate, stock `-1005` invalid-UUID and `-1002` rejected-payload results, negative parser
propagation, and validator-greater-than-one result selection. Host tests cover both decrypt paths,
dispatch ordering, normalized UUID/timestamp arguments, malformed fields, parser failure, and
mutation-free provider preflight. Production-Thumb fixtures execute the stock body with synthetic
keys and plaintext callbacks, pin the same results and callback traces, and emit no stock
authorization material.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x0008EA0C` | `gomore_primitives_sdk_auth_parse` | normalize the device identifier, decode and try two explicit decrypt configurations, enforce a four-field token, and dispatch it through typed field parsers and validators |

The complete locomotion-window classifier `0x00067E4C` adds 558 declared bytes, bringing the
primitive module to 320 functions / 44,560 declared bytes and the combined local total to 339
entries, with 23 remaining gated. Its raw `0x26E` state and `0x3E` result remain bounded
caller-owned records. The stock embedded six-channel and linear-sign models become explicit typed
configuration, and autocorrelation/crossing estimation remain callbacks; no model blob,
executable bytes, or absolute firmware pointer is retained.

The implementation composes the already-local nonzero means, circular predicates, autocorrelation
and crossing wrappers, hysteresis counter, six-channel scorer, linear-sign classifier, trend gate,
and three-axis gate. It preserves the four feature means, both crossing fields, five scattered
autocorrelation fields, six one-byte classifier results, untouched reserved word at output `+0x24`,
and the five-entry trend history at state `+0x264...+0x26D`. The stock circular three-mean helper's
dead local results are deliberately omitted because they neither mutate state nor reach the output.

Production-Thumb fixtures execute the stock body directly with inactive and active magnitude
histories. They pin exact Float32 output words, all six flags, the preserved `0xA5A5A5A5` reserved
word, and trend-history shifts ending in stock model scores `2274` and `1732`. Host tests use
explicit models and callbacks to pin the same layout and decision composition, the mode-one
crossing halving rule, exact `{1001,1002,1003,1004,1005}` to
`{1002,1003,1004,1005,1}` trend mutation, and mutation-free provider preflight.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x00067E4C` | `gomore_primitives_locomotion_window_classify` | compose one complete locomotion result from circular feature histories, explicit models, and typed autocorrelation/crossing providers while advancing the dedicated trend history |

The sleep-stage proportion corrector `0x00064CC8` adds 548 declared bytes, bringing the primitive
module to 321 functions / 45,108 declared bytes and the combined local total to 340 entries, with
22 remaining gated. Its stage timeline is caller-owned and bounded to the stock UInt16 index
domain. The sole child is the already-local 40-run target extractor; no model data, executable
bytes, or absolute firmware pointer is retained.

The implementation preserves the signed `-6...6` dead zone, target-one forward versus other-target
reverse negative traversal, whole-run replacement below thirteen epochs, six-epoch edge
replacement for longer negative runs, positive trailing expansion through twelve light epochs,
and the centered twelve-epoch fallback inside the first light run of at least forty epochs. It
also preserves two stock quirks visible in Thumb: short negative replacement subtracts its span
from the remaining adjustment, and positive leading expansion includes the target run's own first
epoch in its light-stage test.

Seven direct production-Thumb fixtures pin the dead zone, long and short negative paths, positive
trailing expansion, centered fallback, stage-two self-target behavior, and reverse target-three
traversal. Host tests cover the same mutations and return adjustments plus mutation-free invalid
input rejection.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x00064CC8` | `gomore_primitives_sleep_stage_proportion_adjust` | apply the stock signed target-stage proportion correction over bounded run descriptors and return the unconsumed adjustment |

The packed sleep-stage decision reducer `0x0005C19C` adds 602 declared bytes, bringing the
primitive module to 322 functions / 45,710 declared bytes and the combined local total to 341
entries, with 21 remaining gated. The stock `0xB7` state prefix becomes a bounded byte record and
the four-byte stage/transition/reason/reserved result plus signed adjustment becomes a typed
caller-owned structure. Its sole child is the already-local 300-tick state-window predicate.

The implementation preserves forced-stage, countdown, external-active, elapsed-over-600,
43,200-second prior-stage timeout, and transition-block paths. The metric path retains fifteen
Float32 threshold observations, fifteen valid `40...240` byte samples, exact `0.4`, `0.3`, and
`100` gates, the unsigned minute-ring index, the 300-second start holdoff, and the duration/flag
override. A caller-supplied preceding fraction makes the stock `ring_index - 1` edge read explicit
and bounded rather than reading before the state record.

Nine direct production-Thumb fixtures pin every top-level reason family and exact packed output,
including adjustments `-10` and `-15`, start/stop transitions, and reserved-byte clearing. Host
tests cover the same decisions, Float32 metric branches, the explicit prehistory seam, and
mutation-free state-length preflight.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x0005C19C` | `gomore_primitives_sleep_stage_decide` | reduce bounded sleep state, elapsed/reference timing, and fifteen-slot metrics into the exact packed stage decision and signed adjustment |

The complete sleep-cycle coordinator `0x00060B80` adds 578 declared bytes, bringing the primitive
module to 323 functions / 46,288 declared bytes and the combined local total to 342 entries, with
20 remaining gated. Its recovered `0x138`-byte owned state exposes the sleep-step prefix, packed
prior decision, overlapping 40-byte statistics/sleep/interval record, previous descriptor,
previous interval, and eight-byte policy as typed caller-owned data. The stock pointer at state
`+0x138` is removed: the clean API owns the policy value directly and retains no absolute firmware
pointer or opaque configuration record.

The implementation composes all nine already-local direct children. It preserves the activity and
clamp timestamp latches, countdown initialization, recent-activity suppression, sleep-step and
stage-decision order, descriptor open transitions `2`/`4`, interval close transition `1`, accepted
interval retention, 30-second end alignment, descriptor merge/reset, statistics accumulation, and
packed decision/output flag publication. Explicit union members document the stock 40-byte record
overlays without incompatible pointer casts, while the decision reducer's preceding-fraction edge
remains a bounded input.

Five direct production-Thumb fixtures execute the stock coordinator at `0x00060B80` with synthetic
RAM only. They pin exact 312-byte state hashes and 32-byte outputs for no-transition, forced-open,
metric-open, metric-close, and active-clamp-clear paths. Host fixtures cover the same branches,
including every interval result field, timestamp behavior, record overlays, statistics, and
mutation-free invalid-argument rejection.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x00060B80` | `gomore_primitives_sleep_cycle_update` | coordinate one complete sleep step, stage transition, interval open/close, statistics update, and output publication over a typed owned state |

The low/high-pass IIR coefficient designer `0x000717AC` adds 602 declared bytes, bringing the
primitive module to 324 functions / 46,890 declared bytes and the combined local total to 343
entries, with 19 remaining gated. The formerly implicit output is a 48-byte typed record containing
the caller-owned order word, cleared reserved word, five feedback coefficients, and five
feedforward coefficients. Orders outside one through four, modes outside low/high, invalid cutoff
domains, and missing math providers fail before mutation.

The implementation preserves the stock Float32 pi word, conjugate pole construction, real
polynomial expansion, odd-order gain term, low-pass sine versus high-pass cosine gain, binomial
feedforward expansion, and alternating high-pass signs. `cosf`, `sinf`, and `powf` remain typed
toolchain bindings; no coefficient table, executable bytes, model data, or absolute firmware
pointer is retained.

Five direct production-Thumb fixtures pin every written and preserved word for low-pass orders one,
two, and three and high-pass orders two and four. Host tests pin the stock order-two low-pass and
order-four high-pass records, untouched fields, and mutation-free invalid-input rejection. Because
the host libm and the production Arm math runtime differ slightly, the host comparison allows at
most three ULPs while the production emulator retains the exact bit oracle.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x000717AC` | `gomore_primitives_iir_low_high_coefficients` | generate bounded order-one-through-four low/high-pass feedback and feedforward coefficients using explicit toolchain math providers |

The band-pass IIR coefficient designer `0x000711B4` adds 982 declared bytes, bringing the primitive
module to 325 functions / 47,872 declared bytes and the combined local total to 344 entries, with
18 remaining gated. The recovered stack geometry is made explicit as one or two pole pairs; stock
uses two and therefore fills all five feedback and five feedforward coefficients in the same
48-byte typed record used by the low/high-pass designer.

The implementation preserves the center/width angle construction, tangent normalization, complex
quadratic poles, paired real-polynomial expansion, gain recurrence, and the alternating even-only
numerator for `(1 - z^-2)^order`. Invalid cutoff ordering/domains, unsupported orders, and missing
`cosf`/`sinf`/`tanf` providers fail before mutation. No coefficient table, executable bytes, model
data, or absolute firmware pointer is retained.

Three direct production-Thumb fixtures pin every record word for an order-one synthetic band and
the two stock order-two bands `0.016/0.16` and `0.0104/0.96`. Host tests pin the sleep-peak band,
untouched fields, and invalid-input immutability, allowing at most four ULPs for host-libm variance
while the production emulator retains exact bits.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x000711B4` | `gomore_primitives_iir_bandpass_coefficients` | generate bounded one/two-pole-pair band-pass feedback and even-only feedforward coefficients using explicit toolchain math providers |

The paired sleep-classifier graph builders `0x0002874C` and `0x0002966C` add 1,776 declared
bytes, bringing the primitive/shared-runtime portion to 327 functions / 49,648 declared bytes and
the combined local GoMore total to 346 entries, with 16 executable functions remaining gated.
Both builders now consume caller-owned model words and an explicit 32-bit target base address;
the stock absolute configuration pointer at `0x000BD668` and implicit model-arena pointers are not
retained.

The family-zero builder emits its recovered default quantizer `{0.0f, 1.0f}` and consumes exactly
1,714 model words. The nonzero builder consumes its first two model words as quantizer bounds and
then consumes exactly 952 words for family one or 1,092 for family two. Both emit the complete
440-byte target ABI block: seven aligned convolution descriptors, three pooling descriptors, two
model-sourced add descriptors, two fixed tensor bindings, six generic neural descriptors, the
external graph vectors, and the final local activation descriptor. Three stock padding words are
initialized deterministically in the checked C representation.

Production-Thumb emulation executes both original bodies and all their local constructor children
against synthetic RAM. It pins exact complete graph SHA-256 values for family zero, one, and two,
exact returned arena ends, quantizer words, both model-sourced add records, family-specific output
channels, and the three untouched stock padding words. Host tests bind every source-owned/external
executor token explicitly, assert all model cursor counts and representative record offsets, and
verify mutation-free rejection of invalid families, short model arrays, and unaligned target
bases. The two 21,824-byte trained parameter regions remain a separately documented model-data
provenance boundary; this admission covers executable topology construction only.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x0002874C` | `quantized_runtime_gomore_sleep_graph_family_zero_build` | build the fixed family-zero sleep graph prefix from an explicit model array and target address, returning the exact 1,714-word arena end |
| `0x0002966C` | `quantized_runtime_gomore_sleep_graph_family_nonzero_build` | build the family-one/two sleep graph prefix with model-sourced quantizer bounds and exact selector-dependent output geometry |

The complete accelerometer-derived SPS candidate updater `0x0005EF1C` adds 780 declared bytes,
bringing the primitive/shared-runtime portion to 328 functions / 50,428 declared bytes and the
combined local GoMore total to 347 entries, with 15 executable functions remaining gated. Its
exact 88-byte state is now typed as two smoothed values, paired 28-byte model accumulators, an
explicit non-dereferenced configuration binding, latest model values, missing-update counter,
eight-call startup cooldown, and reserved storage.

The implementation composes the already-local four model leaves, model dispatcher, calibration
adjuster/commit seams, and pair accumulator. It preserves raw-versus-smoothed state equality, the
strict cadence-relative `< 0.2` gate, signed state `-1` rejection, state-zero result, elapsed
`2...7` replay, cooldown decrement, state-one `0.15/0.85` and state-two `0.25/0.75` double-precision
smoothing, and calibration-dependent clamps `{4,7}/{2,7}` and `{6,14}/{6,20}`. The checked API
preflights every provider before mutation and leaves the result's three reserved bytes untouched.

The assertion-bearing production-Thumb harness pins initialization, direct primary/secondary
model words, default and calibrated results, both smoothing sequences, exact `0.2` rejection,
state mismatch/`0xFF`/zero handling, missing-count evolution, and cooldown behavior. Host tests
independently cover the typed topology, replay accumulator counts and sums, clamps, smoothing,
reserved-byte preservation, and mutation-free invalid-provider rejection.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x0005EF1C` | `gomore_primitives_sps_accelerometer_candidate_update` | update the complete bounded accelerometer SPS candidate state from explicit motion, feature, profile, and model-provider inputs |

The health lifecycle initializer `0x0004BD98` adds 768 declared bytes, bringing the
primitive/shared-runtime portion to 329 functions / 51,196 declared bytes and the combined local
GoMore total to 348 entries, with 14 executable functions remaining gated. Stock globals become
an exact 32-byte lifecycle record, caller-owned 736-byte previous-data and 28-byte profile inputs,
an exact 264-byte output descriptor, and explicit provider callbacks.

The implementation preserves both authorization attempts and their flag transitions, previous
data restore/defaulting, optional exact-length crash restore and clear, user-profile fallback,
force-default mode, timestamped health initialization, the special `-5` clear-and-retry path,
failure exits, exact four output-storage addresses plus output-record binding, profile/state mode
configuration, and one-time event subscription. All callbacks are preflighted before mutation;
absolute stock RAM and flash pointers are eliminated.

Host fixtures cover authorization retry/success, authorization failure with retained pending flag,
previous-data absence, exact crash restore/clear, default profile selection, `-5` initialization
retry, exact output descriptor words, successful mode/subscription calls, output preservation on
early failure, and address-overflow rejection.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x0004BD98` | `gomore_primitives_health_lifecycle_initialize` | coordinate authorization, prior-state/profile recovery, health initialization retry, output binding, mode activation, and event subscription through explicit providers |

The pKey-page previous-state appender `0x0006BBB0` adds 824 declared bytes, bringing the
primitive/shared-runtime portion to 330 functions / 52,020 declared bytes and the combined local
GoMore total to 349 entries / 54,712 declared bytes, with 13 executable functions remaining
gated. Its flash dependencies are explicit read, write, erase, and initialization callbacks;
the stock heap allocation used during page compaction is replaced by caller-owned scratch.

The implementation preserves four-byte key/state alignment, the shared eight-byte key header,
three eight-byte slot headers, first-erased-slot selection, slot-two compaction trigger, exact
4,096-byte erase, aligned key-record preservation, `{unaligned_length, 0}` slot header, and
aligned payload write ordering. It also makes the stock aligned-source-buffer contract explicit,
rejects arithmetic overflow, and surfaces read/write/erase failures that the void stock routine
ignored. No flash address, partition descriptor, allocator, or executable firmware byte is
retained.

The isolated production-Thumb harness intercepts all storage and allocation calls against a
synthetic 4 KiB page. It pins the first, second, and third slot offsets, the duplicate slot-two
probe, the exact 72-byte key-record compaction for a 64-byte key, erase/rewrite ordering, allocator
size/free call, oversized-record rejection, and null-input early exit. Host tests cover the same
topology plus uninitialized storage, short aligned source capacity, insufficient scratch, and
read/write/erase failures.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x0006BBB0` | `gomore_primitives_previous_state_append` | append one aligned previous-state record to the shared pKey page and preserve the key record across explicit page compaction |

The complete sleep-stage refiner `0x00081040` adds 908 declared bytes, bringing the
primitive/shared-runtime portion to 331 functions / 52,928 declared bytes and the combined local
GoMore total to 350 entries / 55,620 declared bytes, with 12 executable functions remaining
gated. Its public shape matches the existing typed final-report callback: an explicit 11-byte
profile, caller-owned stage storage/capacity/count, and duration.

The implementation preserves the centered moving-majority pass and awake-three-vote override,
descending stage tie priority, bounded streaming vote buffer, awake and long-REM edge repair,
deep/awake transition repair, midpoint targets of 0.18 deep and 0.225 REM, ten bounded proportion
passes with the stock low-fraction sign reversal, fixed-width chunk majority, reverse 0.35 deep
cap, forward 0.25 REM cap, and optional last-epoch awake flag. It composes already source-owned
statistics, run collection, edge smoothing, transition repair, and proportion adjustment. The
stock one-past-end deep-cap read is clipped to the declared array, and invalid stages/capacities
fail before mutation.

An isolated production-Thumb harness executes four distinct production profiles against the same
120-epoch mixed-stage stream and pins exact complete FNV-1a outputs. Host tests reproduce those
four exact digests and independently assert mutation-free invalid-stage rejection.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x00081040` | `gomore_primitives_sleep_stage_refine` | refine a bounded stage stream through the complete profile-selected majority, repair, proportion, chunk, and terminal-cap pipeline |

The activity-window state machine `0x0006138C` adds 834 declared bytes, bringing the
primitive/shared-runtime portion to 332 functions / 53,762 declared bytes and the combined local
GoMore total to 351 entries / 56,454 declared bytes, with 11 executable functions remaining
gated. Its exact 1,028-byte state contains the conditioned score, seven-state code, one 250-float
window, transition/accumulation/hold counters, adaptive reset threshold, and positive/negative
window votes.

The implementation preserves the 0.9 score decay, alternate double-precision 0.05 offset, quality
override, accepted 23...27 sample-count band, one-channel clamp, 25-sample accumulation cadence,
250-sample decision point with a 125-sample carry, per-state vote thresholds, transitional holds,
state-2/state-5 1.2 hold adaptation, state-5 0.95 threshold decay, exact caps/floors, score-reset
paths, and two-byte activity/confidence mapping. The stock equal-rate-copy defect is represented
through the bounded full state object: counts 23/24 leave old tail values and counts 26/27 overwrite
the first one/two metadata words without an out-of-bounds C access.

Host tests cover positive and negative decisions, adaptive holds, transitional completion, score
reset, zero-channel threshold behavior, invalid-input immutability, window shifting, and metadata
spill. The isolated production-Thumb harness pins the same transitions and outputs while hooking
only the private decision leaf to choose deterministic votes; production conditioning and window
copy code execute unchanged.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x0006138C` | `gomore_primitives_activity_window_update` | condition, shift, accumulate, classify, and transition the complete bounded seven-state activity-window record |

The optical respiratory-rate wrapper `0x00060680` adds 734 declared bytes, bringing the
primitive/shared-runtime portion to 333 functions / 54,496 declared bytes and the combined local
GoMore total to 352 entries / 57,188 declared bytes, with 10 executable functions remaining
gated. The still-residual spectral period estimator at `0x00069834` is an explicit typed callback;
its 48-byte caller-owned prefix contains paired five-float rate/confidence histories, the modulo-20
selector cadence, four primary codes, and two secondary codes.

The implementation preserves at most twenty synthetic gap records, unavailable/estimator/clamp/
gap status bits, the exact encoded 7...25 rate test, positive invalid-rate clamp, negative
confidence rejection, RMS code penalties using double square root and two ordered subtractions,
history clearing and shift order, valid-rate counting, reverse confidence argmax, adaptive
`max_confidence * 0.8` or fixed `0.5` inclusion threshold, selected-rate mean, and final
`0.7 * max_confidence + 0.3 * included/5` confidence. Direct disassembly also corrected the
source-owned `0x00076120` helper ABI: it writes the mean and returns the included count in `r0`,
which this caller consumes.

The production-Thumb harness hooks only `0x00069834` and pins ordinary, gap/unavailable/clamped,
and invalid-rate paths down to complete Float32 output bits, status masks, histories, selector
slots, and callback inputs. Host tests reproduce the same outputs and mutation-free provider
validation.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x00060680` | `gomore_primitives_respiratory_rate_update` | maintain and select the complete bounded five-sample respiratory-rate/confidence history around an explicit spectral-estimator callback |

The optical-interval merge root `0x0004857C` adds 944 declared bytes, bringing the
primitive/shared-runtime portion to 334 functions / 55,440 declared bytes and the combined local
GoMore total to 353 entries / 58,132 declared bytes, with 9 executable functions remaining
gated. Its exact 1,736-byte state contains an 81-byte prefix, interval count/current-window fields,
forty 16-byte interval records, a 250-float optical window, and the two recovered tolerance scales.

The implementation preserves 25-sample window rebasing through the existing compactor, the
window-20-and-later base of 250, adjacent-rise peak selection, global position construction,
ordered insertion, terminal replacement when either coordinate does not advance, a strict
40-record cap, post-merge monotonic validation, and the Float32 mean of retained end-minus-start
amplitudes. The stock tolerance/amplitude branch chooses only between stack-local copies and never
commits either copy, so the bounded source omits that unobservable block. It also replaces the
stock exact-duplicate infinite retry with one bounded retained copy, initializes the record padding
that stock copies from uninitialized stack storage, and rejects reversed or out-of-window candidate
positions before any mutation instead of permitting out-of-bounds signal reads.

The production-Thumb harness
[`emulate_r1_optical_interval_merge.py`](../../tools/evidence/emulate_r1_optical_interval_merge.py)
executes empty-bank construction, insertion before two existing records, terminal replacement,
and current-window-21 compaction. It pins every position/value and the exact `500.0`,
`341.3333435058594`, and `200.0` Float32 result bits. Host tests reproduce those paths and
additionally pin mutation-free invalid-input rejection and failure-clearing of an inconsistent
retained ordering.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x0004857C` | `gomore_primitives_optical_interval_merge` | compact, merge, validate, and summarize the bounded forty-record optical peak-interval bank |

The sleep-stage stream orchestrator `0x00060DC4` adds 762 declared bytes, bringing the
primitive/shared-runtime portion to 335 functions / 56,202 declared bytes and the combined local
GoMore total to 354 entries / 58,894 declared bytes, with 8 executable functions remaining
gated. Its aligned 8,440-byte typed state exposes the 720-byte two-bit history, timestamp and
previous code, 136 signed peaks, window/update counters, 90-float stage window, caller-owned tensor
storage/binding, selected stage, and mode. The still-residual stage classifier `0x00088450` is an
explicit typed callback; the mode table and tensor constructor are explicit caller inputs.

The implementation preserves gap filling, active/inactive engine transitions, inactive packed
status writes, strictly increasing peak accumulation in 25-sample batches, the 32-batch peak-window
update and tail rebase, iterative classifier completion, 30-float window shift, three-candidate
argmax, all four table-selected status/threshold policies, packed publication at the preceding
30-second slot, the mode-100/101/102 availability cadence, and final timestamp/code commit. It also
preserves the observable stock behavior that output byte zero remains untouched when no stage is
published. Clean preflight bounds the 16-byte input peak record, validates the mode-table row and
required callbacks before mutation, and rejects classifier stage codes outside zero through three.

The production-Thumb harness
[`emulate_r1_sleep_stage_stream.py`](../../tools/evidence/emulate_r1_sleep_stage_stream.py) hooks
only `0x00088450` and pins inactive packing, active peak accumulation, completed publication, and
32-window rollover down to packed bytes, counters, rebased peaks, output flags, and window shift.
Host tests reproduce all four paths and add mutation-free oversized-input rejection.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x00060DC4` | `gomore_primitives_sleep_stage_stream_update` | maintain and publish the complete bounded sleep-stage peak/history stream around one explicit private classifier callback |

The peak-candidate matcher `0x00064380` adds 958 declared bytes, bringing the
primitive/shared-runtime portion to 336 functions / 57,160 declared bytes and the combined local
GoMore total to 355 entries / 59,852 declared bytes, with 7 executable functions remaining
gated. Its public contract uses a bounded 250-float signal, paired twenty-byte candidate/reference
banks, one 25-float caller workspace, and explicit transparent sort/power/square-root providers.

The implementation preserves the sample-standard-deviation versus mean outlier gate, in-place
Float32 ordering, floor-selected 0.25/0.75 quartiles, inclusive trimmed mean, strict three-range
candidate cutoff, median candidate spacing, reference advancement at `0.75 * median`, direct
near-reference pairing, the `0.75...1.25` spacing band, quantized signal argmin, the strict
`0.1...0.5` valley-tail band, paired output counts, and final median recomputation. All threshold
products retain the stock binary64 comparison path. Clean preflight bounds both banks and every
signal index before mutation; defined stock algorithm failure still clears both counts and the
median exactly.

The production-Thumb harness
[`emulate_r1_peak_candidate_match.py`](../../tools/evidence/emulate_r1_peak_candidate_match.py)
pins direct reference alignment, valley reconstruction, quartile/outlier removal, exact Float32
median bits, and insufficient-input clearing. Host tests reproduce those paths and add
mutation-free out-of-range signal-index rejection.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x00064380` | `gomore_primitives_peak_candidate_match` | filter and align bounded peak candidates to references or recovered signal valleys with exact median-spacing gates |

The complete sleep-stage classifier `0x00088450` adds 1,090 declared bytes, bringing the
primitive/shared-runtime portion to 337 functions / 58,250 declared bytes and the combined local
GoMore total to 356 entries / 60,942 declared bytes, with 6 executable functions remaining
gated. The stock absolute model tables at `0x000B1C4C` and `0x000B2048` become two explicit
`gomore_primitives_sleep_stage_classifier_model` inputs. Each model exposes seven typed
Float16 convolution/normalization blocks, four signed-Int8 affine transforms with Float16 bias,
and two recurrent layers whose input/recurrent matrices and biases are separate bounded spans.
Square-root, exponential, logistic, and hyperbolic-tangent arithmetic are explicit transparent
providers.

The implementation executes the fixed topology directly: seven padded width-three convolutions,
batch normalization and the recovered `0x31D1` Float16 leaky-ReLU slope; average-pooling reductions
`90 -> 45 -> 15`; dense projection `120 -> 32 -> 32`; two persistent 32-unit gated recurrent
cells; dense output `32 -> 32 -> 4`; softmax; the signed four-byte mode adjustment at exact
Float32 scale `0.01`; and first-maximum selection. The existing 7,056-byte tensor pool is reused as
checked ping-pong workspace, a 192-float converted-weight span, and two persistent hidden states,
eliminating the stock descriptor allocator and all absolute firmware bindings. Non-first
iterations preserve the stock `{1,0,0,0; selected=0}` completion record.

The production-Thumb harness
[`emulate_r1_sleep_stage_classifier.py`](../../tools/evidence/emulate_r1_sleep_stage_classifier.py)
executes both stock model families against zero, ramp, and sine windows, pins all output Float32
bits and selected stages, repeats zero-window inference to pin recurrent-state persistence, and
checks the non-first-iteration default. Host tests run the complete source graph against a bounded
synthetic model, pin mode adjustment and argmax behavior, and verify mutation-free rejection of a
missing selected-family model. No trained parameter bytes or executable payload are embedded in
this admission; the two model regions remain explicit data inputs for the final model-provenance
closure.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x00088450` | `gomore_primitives_sleep_stage_classify` | execute the complete fixed convolution/pooling/dense/recurrent/softmax sleep graph over explicit typed model and math inputs |

The locomotion feature reducer `0x00068840` adds 1,190 declared bytes, bringing the
primitive/shared-runtime portion to 338 functions / 59,440 declared bytes and the combined local
GoMore total to 357 entries / 62,132 declared bytes, with 5 executable functions remaining
gated. Its two code extents `0x00068840..<0x00068C68` and
`0x00068C94..<0x00068D12`, intervening literal bank, and direct callers at `0x00056F62` and
`0x00069B50` remain pinned by the algorithm-domain audit. The stock six-argument ABI becomes one
250-float caller-owned signal, two bounded twenty-byte extrema banks, forty floats of caller
scratch, paired Float32 outputs, and an explicit sort/power/square-root provider record.

The implementation preserves the sample-standard-deviation normalization, zero-deviation fill,
fixed second-order IIR, `38/12` moving-average extrema pass, 75th/25th percentile thresholds at
binary64 scale `0.2`, and both symmetric one-opposite-extremum pairing scans. Each accepted sample
distance is converted through the recovered `12.5 / distance * 60.0` expression. The sparse-event
fallback retains distances strictly above 50 and below the literal
`114.99999999999999`; it also deliberately retains the production body's observable duplicate
scan of the second extrema bank. Final reduction uses strict mean-plus/minus-two-sample-deviation
outlier bounds, requires at least three included periods, computes population dispersion through
the explicit binary64 providers, and applies the already-local bounded linear complement to
`1 - count / (2 * mean * Float32(1/3))`. Empty or overflowing extrema are handled without the
stock body's zero-count percentile reads.

The production-Thumb harness
[`emulate_r1_locomotion_feature_reduce.py`](../../tools/evidence/emulate_r1_locomotion_feature_reduce.py)
pins the complete six-argument body on constant, uniform-triangle, and irregular-triangle inputs,
including exact extrema indices, scratch period bits, default outputs, final output bits, and all
five arithmetic literals. Host tests reproduce the irregular triangle exactly (`0x41760E19`,
`0x3F2AC478`), pin constant-input defaults, exercise the typed control-extractor composition, and
verify mutation-free rejection of a missing math record.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x00068840` | `gomore_primitives_locomotion_feature_reduce` | normalize and filter 250 locomotion samples, pair bounded extrema into cadence periods, reject outliers, and emit rate/quality through explicit math providers |

## Optical-period estimator state machine

The optical-period estimator `0x00069834` adds 1,196 declared bytes, bringing the
primitive/shared-runtime portion to 339 functions / 60,636 declared bytes and the combined local
GoMore total to 358 entries / 63,328 declared bytes, with 4 executable functions remaining
gated. Its code-only extent `0x00069834..<0x00069C50` has SHA-256
`cc4afba99d15e84367104fbbc83935393babb701ac7ccf2b25ef3d65edb24bec`; the literal bank and tail
code through the declared function end remain pinned by the existing algorithm-domain and output-
producer audits. The recovered six-argument stock ABI becomes a typed 1,736-byte interval state,
elapsed-window and flag inputs, a bounded 25-float sample window, explicit filter/math providers,
caller-owned workspace, paired outputs, and a separate status result.

The implementation preserves output defaults, saturating window advancement, the nine-window
cooldown, multi-window zero insertion, and full reset after gaps above twenty windows. Once ten
windows are available it composes the already-local `25/6` moving-extrema pass, peak/reference
matching, interval merging, and both control-extraction modes. Position and amplitude tolerances
retain the initial-positive-measurement rule and subsequent binary64 `0.75/0.25` smoothing.
Sparse interval histories construct the exact mirrored 250-sample fallback using Float32
`1/60`, then call the local locomotion feature reducer. Candidate selection retains close-rate
averaging, binary64 `1.2` confidence scaling and saturation, quality-based mode selection, and the
strict `0.5` fallback-quality, `0.3` selected-quality, and rate-at-most-25 override gates.

The production-Thumb harness
[`emulate_r1_optical_period_estimator.py`](../../tools/evidence/emulate_r1_optical_period_estimator.py)
pins ten zero-input warm-up calls, exact default/tolerance bits, a three-window gap, a greater-than-
twenty reset, both control modes, sparse-history fallback invocation, close-candidate averaging,
and fallback override. Host tests reproduce the warm-up state transitions, exercise the candidate
selector independently, and verify mutation-free rejection of an incomplete provider record. No
filter implementation, math function, model table, or executable firmware payload is embedded in
this admission.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x00069834` | `gomore_primitives_optical_period_estimate` | advance the optical interval state machine and select a period/quality result from two interval modes plus a sparse-history fallback |

## Floating-point convolution executor

The indirect neural-layer executor `0x00076BDC` adds 1,234 declared bytes, bringing the
primitive/shared-runtime portion to 340 functions / 61,870 declared bytes and the combined local
GoMore total to 359 entries / 64,562 declared bytes, with 3 executable functions remaining
gated. Its exact extent `0x00076BDC..<0x000770AE` has SHA-256
`61c6cdae7f85eb4096726de5fe67c5c7f85ce4bc6991ef4d45a19825779875ea`. The stock Thumb pointer
`0x00076BDD` at `0x00074B40`, the generic 24-byte constructor at `0x00074AAC`, and all sixteen
constructor callsites remain pinned by the neural-runtime audit.

The recovered descriptor exposes kernel width, stride, left/right padding, input/output channels,
groups, activation, alpha, weights, and biases. The implementation preserves channel-major
Float32 accumulation for specialized width-one, width-three, and width-five kernels; the stock
kernel-three depthwise grouping layout; per-output bias; ReLU/leaky-ReLU; and sigmoid with the
signed-bit `88.0f` exponent cap. The checked form validates every tensor/model extent, implements
padding virtually instead of moving the input in place, and uses explicit caller workspace when
output overlaps input. Constructor `0x00074AAC` now stores the local target adapter, so the fixed
firmware address is no longer an executable dependency.

The production-Thumb harness
[`emulate_r1_float_conv1d.py`](../../tools/evidence/emulate_r1_float_conv1d.py) pins exact output
bits for ordinary and depthwise width-three convolution, width-five leaky-ReLU, and width-one
sigmoid, plus restoration of the stock body's temporary input padding. Host tests reproduce all
four families, exercise overlap workspace, and verify mutation-free malformed-descriptor
rejection. Model weights and biases remain explicit caller-supplied spans; no trained parameter
or executable bytes are embedded.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x00076BDC` | `quantized_runtime_float_conv1d_execute` | execute bounded channel-major Float32 convolution with recovered padding, grouping, bias, and activation semantics |

## Locomotion autocorrelation analyzer

The locomotion autocorrelation body `0x0005C5F0` adds 1,326 declared bytes, bringing the
primitive/shared-runtime portion to 341 functions / 63,196 declared bytes and the combined local
GoMore total to 360 entries / 65,888 declared bytes, with 2 executable functions remaining
gated. Its exact extent `0x0005C5F0..<0x0005CB1E` has SHA-256
`751b1991279337f88b5558ea7a287b930d9e7452df7a229489cb90abf7bb2ca0`; the sole direct callsite at
`0x00056DB2` and its existing typed callback path remain pinned by the algorithm-domain audit.

The implementation computes the integer mean and all 100 lags of the centered UInt16
autocorrelation with explicit modulo-2^32 multiply/add behavior. It preserves both strict and
non-strict local-maximum passes, the capped ten/eleven-byte peak banks, `0.55/0.40` spacing-quality
decision, `0.03` peak threshold, strongest/secondary peaks below lag 51, harmonic tolerances
`4/5/6`, and the `0.17`, `0.35`, and `-0.1` correlation gates. It composes the already-local
direction-change statistics with exact `0.3`, `0.45`, and `0.35` thresholds, then retains the
third-peak `4500/lag` estimate and both parabolically refined `1500/lag` estimates through the
local centered-ratio helper. The selected lag deliberately remains zero unless the secondary path
has at least three peaks, matching the stock period-35 behavior.

The production-Thumb harness
[`emulate_r1_locomotion_autocorrelation.py`](../../tools/evidence/emulate_r1_locomotion_autocorrelation.py)
pins six sinusoidal periods, a ten-sample alternating waveform, constant and ramp rejection, and
an extreme UInt16 input that exercises wrapped arithmetic. Host tests reproduce all six sine
result vectors and the alternating result bit-for-bit, including turning counts and shape fields,
and verify deterministic default outputs for a constant window. The caller-facing callback now
returns an explicit status and consumes UInt16 samples, eliminating the old signed cast and opaque
analyzer dependency.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x0005C5F0` | `gomore_primitives_locomotion_autocorrelation_analyze` | classify a fixed 100-sample UInt16 autocorrelation and emit two validity flags, three refined rates, and direction-shape diagnostics |

## Locomotion crossing-period estimator

The locomotion crossing-period body `0x00056F94` adds 1,544 declared bytes, bringing the
primitive/shared-runtime portion to 342 functions / 64,740 declared bytes and the combined local
GoMore total to 361 entries / 67,432 declared bytes, with only the output orchestrator at
`0x0005FF94` remaining gated. Its exact extent `0x00056F94..<0x000575B4` has SHA-256
`10619cf14c4a1ba49ebe63924728a5d738414c86331b36c932d8ec3fe3d7efe2`; direct calls
`0x00056D2C` and `0x00056D3C` select profiles 2 and 1 after the caller derives an eight-slot
positive-fill magnitude baseline.

The reconstruction computes the stock modulo-2^32 RMS scale over exactly 200 UInt16 magnitudes,
normalizes each centered sample by 1,000, and feeds the already-local fourth-order integer IIR.
Profile 2 compares centered 12/6-sample moving means and accepts same-phase extrema intervals from
6.25 through 25 samples. Profile 1 uses 20/10-sample means and accepts intervals from 20 through
50, while composing the local transition-consistency helper with the exact 0.8 target scaling,
separate two-byte raw-interval histories, shared adaptive estimate, and 70-percent pruning rule.
Both paths cap the interval bank at 80 bytes. The final reducer preserves the 25th/75th-percentile
indices, 0.3 relative-spread gate, wrapped Int16 interquartile sum, and exact Float32 operation
order: `(25 / period) * 60` for profile 2 and the same result multiplied by two for profile 1.
Invalid modes and undersized spans fail without publishing a result.

The production-Thumb harness
[`emulate_r1_locomotion_crossing.py`](../../tools/evidence/emulate_r1_locomotion_crossing.py)
pins all 96 output words from sinusoidal periods 8 through 55, a ten-sample alternating waveform,
constant rejection, and a wrapped extreme input. A direct host-versus-Thumb comparison reproduces
all 96 sine outputs bit-for-bit; host tests additionally pin the alternating pair
`0x43160000`/`0x42C8F4FA`, constant default, and checked-input failures. The wrapper callback now
returns an explicit status, and no executable firmware address, coefficient blob, allocation, or
opaque model input is required.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x00056F94` | `gomore_primitives_locomotion_crossing_period_estimate` | filter a fixed 200-sample UInt16 magnitude history into one bounded profile-specific cadence estimate |

## Complete output-stage orchestrator

The final GoMore body `0x0005FF94` adds 1,606 declared bytes, completing the
primitive/shared-runtime portion at 343 functions / 66,346 declared bytes and the combined local
GoMore inventory at all 362 entries / 69,038 declared bytes. Its declared extent
`0x0005FF94..<0x000605DA` has SHA-256
`316edbabcbe75e09edbfc16176e77aa0e6938e21ba63199015b0f1f47ee993c1`; the sole direct
caller remains `0x0009468A`. Every one of its sixteen stage targets was already source-admitted
before this root.

The reconstruction exposes the complete schedule as a fixed typed descriptor table. Each entry
names the local stage role and preserves its exact substate offset, control byte, result-status
byte, stock diagnostic number, ordered argument offsets, and execution order. Control zero runs a
stage for the caller's elapsed-update count; control one forces exactly one update and resets to
zero; control two transitions to held state three without executing; all other controls remain
held. Each stage's low status byte is stored at the exact stock offset, and successful completion
returns the existing `+0x37FD` result record. The checked API validates the complete `0x3894`-byte
engine and all sixteen source callbacks before mutation, propagates callback failure, and never
uses a firmware address or untyped function pointer. The activity-window adapter receives the
same update count and performs the stock UInt32-to-Float32 conversion at its typed boundary.

The production-Thumb harness
[`emulate_r1_output_orchestrator.py`](../../tools/evidence/emulate_r1_output_orchestrator.py)
replaces only the already-recovered stage bodies with isolated return hooks and pins the exact
execution order, all sixteen substate addresses, normal elapsed values, forced-one behavior,
control `2 -> 3`, held-state behavior, status bytes, diagnostic stage numbers, and result pointer.
Host tests independently pin the descriptor routing and all four control paths, and verify that a
missing source binding fails before the engine is changed. This admission completes the executable
GoMore census; explicit model/data inputs and production hardware adoption remain separately
audited integration concerns.

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x0005FF94` | `gomore_primitives_output_orchestrate` | schedule all sixteen source-owned output stages through exact engine offsets, controls, statuses, and elapsed-update semantics |
