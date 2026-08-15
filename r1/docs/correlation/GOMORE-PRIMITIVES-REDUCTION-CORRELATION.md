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
difference is below the stock double constant 7.5, calls the local range argmax, and appends the
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

The primitive module now reconstructs 185 GoMore functions / 8,824 declared bytes; with thirteen
tensor-runtime routines, 198 entries compile locally and 164 remain gated. The logger's global
configuration, varargs formatter, and output code pointer are explicit typed bindings. Stock can
overflow its 256-byte aggregate message when a formatter reports 246 or 247 characters and CRLF
is appended; the local body appends the suffix only when it fits. Tests pin enabled/disabled mask
paths, exact prefix/suffix/wrapper format, all three filter-state offsets and outputs, zero-sample
status, 225-value history retention, negated/zero tails, callback counts, and provider bounds.
