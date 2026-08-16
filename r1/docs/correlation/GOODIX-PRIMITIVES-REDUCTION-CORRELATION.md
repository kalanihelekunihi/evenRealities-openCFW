# Goodix primitive reduction correlation

Status: owner-authorized clean-room reconstruction, 2026-08-14. This is not Goodix source.

The application image is the byte-exact rebuild with SHA-256
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1` at load base
`0x00027000`. Ghidra bodies were cross-checked against fresh Thumb-2 disassembly. Full
per-range hashes and caller lists remain executable evidence in
`tools/evidence/summarize_r1_frontier_sub32.py`.

## Reconstructed entries

| Stock entry | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x0006EB00` | `goodix_primitives_copy_preprocess_version` | bounded `pre_pv_v1.1.0` copy, maximum 14 bytes, final NUL |
| `0x0006CC34` | `goodix_primitives_copy_process_version` | bounded `pv_v1.1.0` copy, maximum 10 bytes, final NUL |
| `0x00029C74` | `goodix_primitives_dispatch_state` | dispatch `record[0]` through seven handlers |
| `0x0002ACF4` | `goodix_primitives_record_initialize_once` | flag-gated record defaults at `+1`, `+0x0B`, and `+0x13` |
| `0x0002D16C` | `goodix_primitives_initialize_device` | call initializer and map zero/nonzero to `0`/`-1` |
| `0x00029D34` | `goodix_primitives_select_fixed_pair` | exact two-way 24-bit fixed-point constant selection |
| `0x00029F88` | `goodix_primitives_record_initialize` | clear bytes 0/1, preserve byte 2, fill 32 bytes at `+3` with `0xFF` |
| `0x0002A474` | `goodix_primitives_reset_state_record` | `0xFF` at byte 0; clear `+1`, `+0x0E..0x0F`, `+0x14..0x17` |
| `0x0006F9D4` | `goodix_primitives_call_hook` | nullable indirect hook call |
| `0x0002ABEC` | `goodix_primitives_clear_state_flags` | clear bytes 5, 6, and 7 |
| `0x0006A140` | `goodix_primitives_library_code` | return `0x12F9` |
| `0x0006A130` | `goodix_primitives_table_9d640` | table binding accessor |
| `0x0006A138` | `goodix_primitives_table_a04cc` | table binding accessor |
| `0x0006A148` | `goodix_primitives_table_a50b0` | table binding accessor |
| `0x0006A150` | `goodix_primitives_table_a692c` | table binding accessor |
| `0x0006A018` | `goodix_primitives_table_ad1ac` | table binding accessor |
| `0x0006CC2C` | `goodix_primitives_table_ad13c` | table binding accessor |
| `0x0006EAF8` | `goodix_primitives_table_ad160` | table binding accessor |
| `0x0002E8C8` | `goodix_primitives_constant_one_a` | return 1 |
| `0x0002E8C4` | `goodix_primitives_constant_four` | return 4 |
| `0x0002AE00` | `goodix_primitives_constant_one_b` | return 1 |

These 21 entries comprise 294 bytes of declared Ghidra function extents. Three were previously
inside the opaque Goodix closure, seventeen had public-democode mappings, and one was an R1
provider adapter. All now compile from local C; the provider-family labels remain intact so the
ledger does not erase their provenance.

## Deliberate safety and transparency changes

- The seven stock accessors returned absolute pointers into firmware-resident tables. The C API
  returns caller-supplied typed bindings, so the firmware build cannot silently depend on those
  opaque addresses.
- The state dispatcher similarly accepts its seven handlers explicitly instead of copying a hidden
  jump table from `0x000BCF78`.
- Version-copy capacity zero, invalid state indices, missing callbacks, undersized records, and null
  pointers fail or no-op safely. Stock code would fault or write before the destination in several
  of those cases.
- The fixed-pair literals were read directly from `0x00029D4C..0x00029D58`: false selects
  `0x00ECCCCD/0x00A66666`; true selects `0x00F33333/0x00C00000`.

`tests/test_reconstructed_goodix_primitives.c` covers every public operation, both fixed-pair
branches, all table bindings, bounded copies, dispatch validation, record layouts, constants, and
the indirect hook. Host, ASan/UBSan, and freestanding Cortex-M4 builds compile the same source.

## Shared float-vector scale alternate entry

| Stock entry / size | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x000928CA` / 2 | `gomore_primitives_scale` | alternate tail entry into the same elementwise float-vector scaling loop already admitted at `0x000928DA` |

Fresh Thumb-2 disassembly shows that `0x928CA` branches into the shared loop head at `0x928CC`;
the Ghidra-recognized `0x928DA` entry is the count test/back-edge/return tail. Both entries therefore
map to the single bounded implementation in `reconstructed/gomore_primitives/`. Its `size_t` count
and pointer validation deliberately reject the negative/non-null-invalid cases that stock callers
were required to exclude.

## NADT result and conditional-mean leaves

| Stock entry / size | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x0006E540` / 4 | `goodix_primitives_nadt_result_binding` | return the NADT result vector that stock fixed at RAM address `0x0009D604`; local C requires the caller to supply it explicitly |
| `0x00029656` / 22 | `goodix_primitives_float_buffer_mean` | when the buffer count is nonzero, calculate its float mean into the caller result; a zero count leaves the result untouched |

The result accessor no longer embeds a private RAM address. The mean wrapper reuses the already
reconstructed `0x87A78` mean kernel and adds checked descriptor, data, and result pointers. Tests
cover pointer identity, a four-value mean, zero-count no-write behavior, and null rejection.

## HRV binding and sample-deviation closure

| Stock entry / size | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x0006DA9C` / 4 | `goodix_primitives_hrv_configuration_binding` | return the 24-byte HRV configuration that stock fixed at RAM address `0x0009D5EC`; local C takes an explicit binding |
| `0x0002F224` / 56 | `goodix_primitives_sample_variance` | mean-centered squared differences divided by `count - 1` |
| `0x00034A58` / 14 | `goodix_primitives_sample_standard_deviation` | sample variance followed by the admitted `sqrtf` behavior through a typed callback |
| `0x0003738C` / 22 | `goodix_primitives_float_buffer_standard_deviation` | conditionally calculate sample standard deviation for a nonempty float-buffer descriptor |

The local variance preserves the stock accumulation and `count - 1` divisor for valid inputs.
Counts below two, invalid pointers, or a missing square-root binding now fail without writing the
result instead of reaching stock division-by-zero or fault behavior. Tests cover exact variance,
standard deviation, the descriptor wrapper, singleton rejection, and configuration identity.

## Zero-safe NADT and SpO2 variance twins

| Stock entry / size | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x0007DCD8` / 60 | `goodix_primitives_sample_variance_or_zero` | sample variance for counts above one; zero for empty and singleton inputs |
| `0x00061FD4` / 22 | `goodix_primitives_sample_standard_deviation_or_zero` | NADT sample-variance result followed by typed `sqrtf` behavior |
| `0x0007DD18` / 58 | `goodix_primitives_population_variance_or_zero` | population variance with divisor `count`, substituting one for an empty input |
| `0x00061FEA` / 22 | `goodix_primitives_population_standard_deviation_or_zero` | SpO2 population-variance result followed by typed `sqrtf` behavior |

These remain separate from the strict GH_HR sample-variance API because the recovered denominator
rules differ. Tests cover four-value sample/population results, empty and singleton zero behavior,
both standard-deviation wrappers, missing data, and the shared square-root seam.

## GH_HR integrity word closure

| Stock entry / size | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x0005A5EC` / 54 | `goodix_primitives_integrity_encode` | select one of four explicit parity masks from bits 1..2, XOR it with bits 1..23, compute its popcount parity, and replace input bit 0 while preserving every other bit |
| `0x000759F4` / 20 | `goodix_primitives_integrity_invalid` | run the local encoder and return true exactly when the encoded word differs from the input |
| `0x00028E70`, `0x000294BC` / 54 each | `goodix_primitives_integrity_encode` | exact sibling encoder instantiations; each referenced table contains the same four words as `0x5A5EC` |
| `0x00028E14` / 66 | `goodix_primitives_integrity_invalid` | inline form of the same encode-and-compare validator over a fourth byte-identical mask table |

The four recovered masks are represented as named C constants in the algorithm body rather than
as opaque firmware tables. The four stock table copies at `0xB19D4`, `0xBCF18`, `0xB0EFC`, and
`0xB149C` are byte-identical (`6B851EB7 4147AE13 28F5C28F 15C28F5B`). Tests cover every mask
selector, both valid and invalid parity, representative 24-bit values, and preservation of the
high byte.

## Packed floating-point conversion closure

| Stock entry / size | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x00028DE0` / 6-byte head | `goodix_primitives_packed_5_10_to_f32_bits` | select the shared conversion tail's 5-exponent/10-fraction format and return the exact float32 bit pattern |
| `0x00028DE6` / 106-byte head/shared-tail extent | `goodix_primitives_packed_6_9_to_f32_bits` | select the 6-exponent/9-fraction format; the Ghidra extent includes the shared tail at `0x4FDF8` |
| `0x00028DEC` / 40 | `goodix_primitives_u32_to_u16_transform` | transform each uint32 source word through an explicit callback and store its low 16-bit result |

Both packed formats preserve the sign bit, map normal exponent/fraction fields directly into
float32, and reconstruct subnormals through the recovered unsigned-to-float bit adjustment
(`0xF4000000` or `0xEC800000`). The local API returns raw float32 bits so NaNs or host floating
environment choices cannot alter the stock representation. The vector helper's hidden code
pointer becomes an explicit typed callback.

## Buffer, scan, version, window, and score additions

Six more previously opaque entries / 248 bytes are reconstructed, bringing the module to 27
functions and reducing the opaque Goodix frontier to 310.

| Stock entry / size | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x0002963A` / 28 | `goodix_primitives_buffer_record_initialize` | allocate and zero 64-byte buffer; clear record flags |
| `0x00096A20` / 32 | `goodix_primitives_buffer_record_create` | allocate one buffer record and initialize it through the preceding routine |
| `0x000929B6` / 32 | `goodix_primitives_integer_max_index` | first maximum and its zero-based index over an int32 vector |
| `0x000667E4` / 48 | `goodix_primitives_copy_dlcom_version` | construct exact `dlCom_pre2exc_pv_v1.3.0_c00c91c9` string |
| `0x000664F4` / 54 | `goodix_primitives_word_window_push` | append until full, then evict oldest uint32 and append |
| `0x0003EFD8` / 54 | `goodix_primitives_logistic_score` | choose lower/upper scale at threshold and compute `100/(exp(-k*(x-t))+1)` |

Heap allocation becomes an explicit typed callback; the C record stores a native pointer rather
than assuming a 32-bit host address. The target layout remains the recovered eight-byte layout,
while allocation failure returns false instead of reaching stock null-pointer clearing. Version
construction is capacity checked, and the exponential provider is explicit.

## Leaf-math, descriptor, and ABI additions

Twenty-seven more previously opaque entries / 498 bytes are reconstructed, bringing the module
to 54 functions and reducing the opaque Goodix frontier to 283. Exact SHA-256 values for every
extent are retained by the generated ownership evidence; the repeated empty, zero, and sum bodies
also retain their distinct stock entry addresses below.

| Stock entry / size | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x0002A9D2` / 2 | `goodix_primitives_noop_a` | empty hook |
| `0x0002E950` / 2 | `goodix_primitives_noop_b` | second empty hook |
| `0x0002A54C` / 4 | `goodix_primitives_zero_a` | return zero |
| `0x0002A610` / 4 | `goodix_primitives_zero_b` | second return-zero leaf |
| `0x0002D458` / 4 | `goodix_primitives_second_word` | read word at offset four |
| `0x000294F8` / 20 | `goodix_primitives_transformed_differs` | compare value with callback transform |
| `0x0002950C` / 14 | `goodix_primitives_transform_in_place` | replace value with callback transform |
| `0x0002CAC6` / 18 | `goodix_primitives_initialize_status` | map callback status zero/nonzero to zero/minus one |
| `0x00034A66` / 22 | `goodix_primitives_is_evenly_divisible` | test exact divisibility of two record dimensions |
| `0x00036718` / 26 | `goodix_primitives_unsigned_power` | repeated float multiplication for an 8-bit exponent |
| `0x00037710` / 16 | `goodix_primitives_float_buffer_full` | compare count and capacity |
| `0x00037720` / 24 | `goodix_primitives_float_buffer_get` | bounded float accessor with explicit fallback |
| `0x00037B68` / 24 | `goodix_primitives_centered_i8` | clamp/center unsigned sample into signed 8-bit range |
| `0x00038030` / 28 | `goodix_primitives_float_sum` | float-vector sum from zero |
| `0x00056828` / 20 | `goodix_primitives_decrement_counter` | decrement positive record counter |
| `0x0005D5D0` / 16 | `goodix_primitives_tensor_descriptor_initialize` | initialize five-word tensor descriptor and return data pointer |
| `0x00061EF2` / 16 | `goodix_primitives_filter_code` | retain code 5, map all other codes to zero |
| `0x00061FB4` / 28 | `goodix_primitives_float_sum` | second byte-identical float-vector sum |
| `0x00066394` / 28 | `goodix_primitives_word_window_last` | return last rolling-vector word or explicit fallback |
| `0x00066490` / 4 | `goodix_primitives_word_window_count` | return rolling-vector 16-bit count |
| `0x00066890` / 14 | `goodix_primitives_store_version_qualifier` | store exact recovered qualifier `0x636E` (`"nc"`) |
| `0x0006DAA4` / 30 | `goodix_primitives_copy_process_version_v1_1` | bounded `pv_v1.1.0` copy |
| `0x0006E548` / 30 | `goodix_primitives_copy_process_version_v1_0` | bounded `pv_v1.0.0` copy |
| `0x00085CA4` / 22 | `goodix_primitives_reverse_low_bits` | reverse a bounded low-bit field |
| `0x00087A78` / 26 | `goodix_primitives_float_mean` | float-vector mean |
| `0x000928E0` / 26 | `goodix_primitives_sum_squares` | float-vector sum of squares |
| `0x00092900` / 30 | `goodix_primitives_dot_product` | float-vector dot product |

Stock fallback words at `0x00037738` and `0x000663B0` are both recovered `0.0f`, but are
caller parameters in the C API so bounds behavior is explicit. Null pointers, zero divisors,
out-of-range bit counts, and zero-length means fail safely instead of preserving stock faults or
undefined shifts. The target tensor descriptor remains the recovered 20-byte five-word ABI; host
builds naturally use a wider native data pointer.

## Packed-record and extrema additions

Eighteen more previously opaque entries / 720 bytes are reconstructed, bringing the module to 72
functions / 1,760 declared bytes and reducing the opaque Goodix frontier to 265.

| Stock entry / size | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x00028E5C` / 20 | `goodix_primitives_transformed_differs` | second transform/compare wrapper |
| `0x00029090` / 40 | `goodix_primitives_copy_indexed_record` | bounds-check and copy one 32-byte record |
| `0x000290DC` / 34 | `goodix_primitives_round_nearest` | signed round-to-nearest with halves away from zero |
| `0x0002A168` / 48 | `goodix_primitives_transform_packed24_lsb` | visit four-byte records, transform bytes 1..3, store result low byte |
| `0x0002A1CC` / 42 | `goodix_primitives_visit_packed24` | visit each packed 24-bit record value |
| `0x0002ADD0` / 40 | `goodix_primitives_swap_u16_bytes` | swap each adjacent byte pair |
| `0x000357A2` / 44 | `goodix_primitives_i32_range` | return max-minus-min with optional extrema outputs |
| `0x00036BD4` / 38 | `goodix_primitives_processing_record_initialize` | copy 76-byte prefix and append recovered five-word geometry |
| `0x00036C32` / 46 | `goodix_primitives_update_transition` | update state/flag/counter bytes from two input states |
| `0x00037574` / 48 | `goodix_primitives_sort_floats` | ascending in-place bubble sort |
| `0x0004304C` / 50 | `goodix_primitives_sorted_insert` | insert into ascending float vector |
| `0x00061F94` / 30 | `goodix_primitives_float_mean_or_zero` | vector mean with denominator one for empty input |
| `0x000662DA` / 16 | `goodix_primitives_word_window_full` | compare 16-bit count and capacity |
| `0x00066458` / 52 | `goodix_primitives_i16_mean` | signed 16-bit vector mean |
| `0x000668DC` / 36 | `goodix_primitives_i16_min_index` | first minimum index in signed 16-bit vector |
| `0x00092988` / 46 | `goodix_primitives_float_min_index` | first float minimum and index |
| `0x000929D6` / 46 | `goodix_primitives_float_max_index` | first float maximum and index |
| `0x00092B68` / 44 | `goodix_primitives_float_mean_or_zero` | second mean leaf, including recovered empty-input zero |

The indexed-copy error value is the exact literal `0x10000003`. The source APIs add explicit
buffer lengths and capacities; incomplete packed records, odd byte-swap lengths, full insertion
buffers, and empty extrema vectors fail without out-of-bounds access.

## Allocator and descriptor leaf additions

Ten more previously opaque entries / 262 bytes are reconstructed, bringing the module to 82
functions / 2,022 declared bytes and reducing the opaque Goodix frontier to 255.

| Stock entry / size | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x00028EAC` / 20 | `goodix_primitives_release_and_clear` | release non-null allocation and clear its slot |
| `0x00036230` / 12 | `goodix_primitives_release_if_present` | guarded release, return zero |
| `0x0003757C` / 12 | `goodix_primitives_release_if_present` | second byte-identical guarded release |
| `0x00034A3C` / 28 | `goodix_primitives_allocate_record_pair` | allocate `count * 24` record storage and one 24-byte scratch record |
| `0x00036C60` / 26 | `goodix_primitives_release_context_pair` | release optional owned allocation, then its context |
| `0x000662EA` / 26 | `goodix_primitives_buffer_descriptor_initialize` | initialize/allocate 4-byte-element descriptor |
| `0x00066304` / 26 | `goodix_primitives_buffer_descriptor_initialize` | initialize/allocate 2-byte-element descriptor |
| `0x0006631E` / 28 | `goodix_primitives_extended_descriptor_initialize` | initialize/allocate byte descriptor with cleared auxiliary field |
| `0x0006633A` / 34 | `goodix_primitives_extended_descriptor_initialize` | initialize/allocate 2-byte descriptor with flag/status fields |
| `0x0006635C` / 50 | `goodix_primitives_float_descriptor_initialize` | initialize/allocate float descriptor; supplied storage starts full |

Every allocation and release crosses an explicit typed provider. Size multiplication is checked,
allocation failures are reported, and no Goodix heap address, pool header, free-list pointer, or
allocator binary is linked into the build.

## Descriptor lifecycle additions

Four more previously opaque entries / 180 bytes are reconstructed, bringing
`goodix_primitives` to 98 exact-address mappings. These routines are the bounded descriptor and
record layer immediately above the reconstructed heap; they do not implement biometric math.

| Stock entry / size | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x0005683C` / 36 | `goodix_primitives_dual_buffer_descriptor_initialize` | store six recovered fields and zero both `count * 4 + 4` buffers |
| `0x00056874` / 56 | `goodix_primitives_float_storage_initialize` | bind supplied float storage as full, or allocate/clear storage with zero count and limit |
| `0x000667C6` / 52 | `goodix_primitives_pair_buffer_initialize` | halve the source count, allocate/clear eight-byte records, and retain one-byte count plus metadata |
| `0x00093E3A` / 36 | `goodix_primitives_release_two_and_clear` | free and clear both owned pointers in the single recovered 24-byte record iteration |

The C structures use native pointers while preserving the target field semantics; target offsets
remain evidence, not a 64-bit-host ABI. Count multiplication is checked, the stock one-byte pair
count is bounded explicitly, allocation failure is returned, and no hidden storage address is
retained. Focused tests cover supplied versus allocated float storage, the stock extra-word clear,
pair-count halving, metadata retention, and two-slot release.

## Channel/session lifecycle additions

Four paired constructor/destructor entries / 338 bytes are reconstructed, bringing
`goodix_primitives` to 102 exact-address mappings. This closes the recovered six-descriptor
channel state and its enclosing two-channel, four-tail-descriptor session state.

| Stock entry / size | Reconstructed symbol | Recovered contract |
|---|---:|---|
| `0x0003DF18` / 104 | `goodix_primitives_channel_state_initialize` | allocate six zeroed float descriptors with capacities `25`, `primary_divisor + 12`, `25`, `1`, `125 / primary_divisor`, and `125 / secondary_divisor` |
| `0x000304A0` / 54 | `goodix_primitives_channel_state_release` | release and clear those six descriptor allocations in target order |
| `0x0005CD90` / 102 | `goodix_primitives_session_state_initialize` | initialize two channel states plus three 125-float tails and one 125-element 16-bit tail |
| `0x00091890` / 78 | `goodix_primitives_session_state_release` | release both channel states and the four tail allocations in target order |

Native typed structures replace target byte offsets while retaining the recovered nesting and
capacity formulas. Both divisors are checked before division; all allocator callbacks are
explicit; allocated storage is cleared even when a caller supplies a non-zeroing allocator; and a
partial construction releases every successfully acquired block. Tests cover exact capacities,
zero initialization, sixteen-release session teardown, invalid divisors, and mid-construction
allocation failure cleanup.

## Owned float-record lifecycle

The adjacent two-function / 100-byte owned-record pair is reconstructed, bringing
`goodix_primitives` to 104 exact-address mappings.

| Stock entry / size | Reconstructed symbol | Recovered contract |
|---|---:|---|
| `0x000362B6` / 62 | `goodix_primitives_owned_float_record_create` | allocate one record, select the maximum of the two recovered capacity bytes, and initialize its owned float descriptor with flag one |
| `0x00033800` / 38 | `goodix_primitives_owned_float_record_destroy` | release the nested descriptor allocation, then release the record |

The outer target record was 68 bytes because it contained additional stock-reserved space. The
transparent C type retains only the recovered live field, uses its native pointer width, clears
the allocation explicitly, and rolls back the outer record if nested allocation fails. The test
pins maximum-capacity selection and the two-release destructor order.

## Per-channel record-array lifecycle

The two-function / 148-byte per-channel record-array pair is reconstructed, bringing
`goodix_primitives` to 106 exact-address mappings.

| Stock entry / size | Reconstructed symbol | Recovered contract |
|---|---:|---|
| `0x00034AA0` / 98 | `goodix_primitives_channel_record_array_create` | when enabled, allocate `count` records; clear status, set both float defaults to `0.0f`, retain the recovered tag byte, and create one owned 15-float descriptor per record |
| `0x000305D8` / 50 | `goodix_primitives_channel_record_array_destroy` | when enabled, release every record descriptor and then release the array |

The `0.0f` default is pinned by literal bytes `00 00 00 00` at `0x00034B04` in the rebuilt
application image, not inferred from decompiler naming. The native C record retains every live
field without target padding. Checked array sizing, explicit zeroing, disabled-mode behavior, and
partial-construction rollback replace the stock allocator-fatal assumption. Tests cover a
three-record lifecycle and failure after the first nested descriptor allocation.

## Aggregate session lifecycle

Three more entries / 192 bytes are reconstructed, bringing `goodix_primitives` to 109
exact-address mappings and closing the aggregate directly used by the outer algorithm session.

| Stock entry / size | Reconstructed symbol | Recovered contract |
|---|---:|---|
| `0x00031914` / 48 | `goodix_primitives_dual_i16_storage_initialize` | clear the marker and allocate 16-bit buffers with capacities `125` and `125 / auxiliary_divisor` |
| `0x0003727C` / 100 | `goodix_primitives_session_aggregate_create` | create the two-channel session state, dual 16-bit auxiliary storage, and a pair of 20-word descriptors |
| `0x00037E8A` / 44 | `goodix_primitives_session_aggregate_destroy` | release the descriptor pair, auxiliary buffers, complete nested session, and their outer allocations |

The marker literal is independently pinned as `00 00 00 00` at `0x00031944`. The native
aggregate replaces the target `0x104`/`0x18` allocation sizes with typed structure sizes while
retaining the complete 22-allocation ownership topology. Invalid divisors and partial construction
fail cleanly. Tests pin all recovered capacities, the 22-release complete teardown, and failure
immediately after the outer session allocation.

## Buffer-record destructor closure

Goodix entry `0x0007CBA0` / 38 bytes now maps to
`goodix_primitives_buffer_record_destroy`, bringing `goodix_primitives` to 110 exact-address
mappings. It completes the previously reconstructed `0x00096A20` constructor pair: release and
clear the record's owned 64-byte buffer, release the outer record, and clear the caller's pointer.
The focused test pins the two-release order and null final state.

## Outer preprocessing-session lifecycle

The final two entries in this wave add 222 bytes and bring `goodix_primitives` to 112
exact-address mappings. `0x0006EB94` creates the target-`0xD4` outer session only for a 76-byte
configuration and exact `pre_pv_v1.1.0` ABI tag; `0x0006EB30` releases its record pair,
aggregate, owned float record, generated-model owner, channel-record array, buffer record, and
outer allocation in recovered order. The dotted ABI spelling is pinned directly by bytes at
`0x0006EB20`/`0x0006EC18`; the earlier underscore spelling came from Ghidra's sanitized string
label and has been corrected in both version-copy helpers.

The native-pointer structure has target offset assertions for `+0x0C`, `+0x6C`, `+0x88`,
`+0xA8`, `+0xAC`, `+0xB0`, and `+0xD0`. The constructor composes only already reconstructed
subobjects, accepts the model words/base explicitly, and rolls back every successful nested
allocation on failure. Tests pin all derived processing geometry, record count/tag propagation,
the complete 34-release teardown, exact-version rejection before allocation, and partial
record-pair failure cleanup.

## SpO2 version-report closure

Two further entries / 228 bytes bring `goodix_primitives` to 114 exact-address mappings:
`0x00066840` emits `dsp_pv_v1.3.0_30234f22`, and `0x0006EC90` composes the complete 126-byte
SpO2 report from its fixed component strings plus an explicitly supplied weights version. The
reconstruction requires a 127-byte destination, reports truncation instead of overflowing, and
does not reproduce stock `0x0006A020`'s 50-byte copy past the weights string's NUL terminator.
The test pins the entire report byte-for-byte, including its three newlines, `_nc_` qualifier,
component hashes, and short-buffer failure.

## Recurrent destructor-vector accessor

Entry `0x00074AA4` / 4 bytes returned stock Thumb pointer `0x00028EC9`.
`goodix_primitives_release_context_pair_vector` now returns the local
`goodix_primitives_release_context_pair` address, removing the final opaque
literal from the seven-function recurrent closure. The focused test pins the
function identity; target toolchains supply their own Thumb-bit representation.

## Quartic and bounded peak selection

Two adjacent formerly opaque entries / 428 bytes are also local:

| Stock entry / size | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x0007412C` / 94 | `goodix_primitives_quartic_evaluate` | evaluate signed int32 coefficients at record words 2..6 as `a*x^4+b*x^3+c*x^2+d*x+e`, then divide by exact literal `10000.0f` |
| `0x00074190` / 334 | `goodix_primitives_peak_select` | scan a bounded neighborhood, threshold against the global maximum, retain the strongest indices in descending-value order, and materialize their values |

The peak API adds explicit vector/range/capacity checks; stock assumed all
buffers and signed bounds were valid. Its tests pin ordering, capacity,
selected values, the quartic result, and invalid-range rejection.

## Float-sort branch alias

The two-byte entry `0x0003754A` is exactly `b 0x00037574` in the recovered
disassembly. It therefore maps to the same tested
`goodix_primitives_sort_floats` C body as its already reconstructed target,
without adding a duplicate implementation or an opaque machine-code shim.
At that checkpoint this brought `goodix_primitives` to 115 exact-address
mappings.

## Mode-one buffer-clear closure

Entry `0x00036BFA` / 44 bytes reads three pointer/count pairs from recovered
state offsets `0x1C0/0x1BC`, `0x1DC/0x1D8`, and `0x1F4/0x1F0`, clears exactly
`count * sizeof(float)` bytes for each only when mode is one, and otherwise
returns without mutation. The four-byte entry `0x0002F65C` is exactly a branch
thunk to that body. `goodix_primitives_clear_mode_buffers` exposes the three
bindings as bounded typed spans, validates every binding before mutation, and
is tested for the inactive mode, all three clear extents, and an invalid
nonempty binding. These two entries bring `goodix_primitives` to 117
exact-address mappings, with 156 formerly opaque Goodix candidates compiled
locally and 164 remaining.

## Selected-slot elapsed accounting

Entry `0x00043B30` / 62 bytes reads a selected timestamp from the recovered
slot array at state offset `0x238`. A zero timestamp returns failure. A
nonzero slot-zero timestamp returns success without mutation; for every other
slot it replaces the baseline at `0x1E0` and advances both counters at
`0x1E4` and `0x1E8` by `timestamp - baseline` using the target's modular
32-bit arithmetic. The four-byte entry `0x00099010` is exactly a branch thunk
to the same body. `goodix_primitives_update_elapsed_slot` makes the timestamp
table and its extent explicit and adds an out-of-range rejection. Tests pin
all four paths. These two entries bring `goodix_primitives` to 119
exact-address mappings, with 158 formerly opaque Goodix candidates compiled
locally and 162 remaining.

## GH_HRV context teardown

Entry `0x0006DAD0` / 126 bytes is the complete lifecycle cleanup for the
GH_HRV preprocessing context, and `0x0006DB58` / 4 bytes branches exactly to
it. The body clears eleven owned subobjects through the already local
`goodix_primitives_release_and_clear`, releases the two directly owned work
areas, releases the enclosing context, and clears its owner binding: fourteen
releases in all when every binding is populated. The typed
`goodix_primitives_hrv_context_destroy` preserves the recovered release order
and adds null-safe idempotence. Tests pin the full release count, owner clear,
repeat call, and invalid-owner rejection. These entries bring
`goodix_primitives` to 121 exact-address mappings, with 160 formerly opaque
Goodix candidates compiled locally and 160 remaining.

## GH_HRV version identity

Entry `0x0006DF60` / 58 bytes initializes `GH_HRV_pre`, then appends the
recovered `_pv`, `_v1.0.1.0`, `_`, and `ed953ff3` fragments. The bounded
`goodix_primitives_build_hrv_version` emits the exact resulting identity
`GH_HRV_pre_pv_v1.0.1.0_ed953ff3` and rejects destinations shorter than its
32 bytes including NUL. This brings `goodix_primitives` to 122 exact-address
mappings, with 161 formerly opaque Goodix candidates compiled locally and
159 remaining.

## Complete GH_HRV initializer and wrappers

The final three GH_HRV entries / 1,048 bytes are now transparent:

| Stock entry / size | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x0006DB5C` / 926 | `goodix_primitives_hrv_context_create` | validate the exact 24-byte configuration and `pv_v1.1.0` ABI, derive the 25/50/100/200-family geometry, allocate eleven float subobjects and two typed work records, and scale four signed calibration values by `1/10000` |
| `0x0006DF14` / 76 | `goodix_primitives_hrv_initialize_for_sample_count` | copy the explicit configuration binding, override its sample count, and invoke the complete initializer with the recovered ABI |
| `0x0002CC5C` / 46 | `goodix_primitives_hrv_initialize_dispatch` | obtain the sample count through an explicit binding, set result status `0x7F` on success, and clear both former activity globals |

The initializer preserves exact stock status values `0x10000001`,
`0x10000002`, and `0x10000004`, every recovered capacity and work-record
field, and the last-two calibration ordering at offsets `0xF4`/`0xF0`. Its
deliberate safety divergence is failure-clean rollback: every successful
allocation is released if a later allocation fails, whereas stock retained a
partial global context. Tests pin all four recognized geometry families, the
default path, eleven capacities, both work records, calibration scaling,
already-initialized rejection, partial rollback, both wrappers, and the
paired teardown. The complete nine-function / 1,288-byte GH_HRV lifecycle is
therefore locally compiled. These entries bring `goodix_primitives` to 125
exact-address mappings, with 164 formerly opaque Goodix candidates compiled
locally and 156 remaining.

## Strided incremental sample deviation

Entry `0x00061F04` / 138 bytes performs two recovered incremental passes over
a strided float vector: the first derives the mean, the second derives the
population moment, then the exact `count/(count-1)` correction is applied
before toolchain `sqrtf`. Entry `0x00066430` / 34 bytes invokes it with stride
one for a nonempty float-buffer descriptor. The typed reconstruction adds
explicit source extent/stride validation and rejects count one instead of
executing stock's divide-by-zero path. Tests pin contiguous and strided
results plus short-extent and count-one rejection. These entries bring
`goodix_primitives` to 127 exact-address mappings, with 166 formerly opaque
Goodix candidates compiled locally and 154 remaining.

## Rolling-buffer lifecycle closure

Six adjacent entries / 536 bytes implement the reusable bounded-window layer
shared by GH_SPO2/dlCom and GH_NADT:

| Stock entry / size | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x00066470` / 68 | `goodix_primitives_float_window_mean` | direct mean of the populated float window |
| `0x00066494` / 92 | `goodix_primitives_float_window_remove` | remove an indexed float, compact storage, retreat the cursor, and subtract it from the running sum |
| `0x0006652A` / 54 | `goodix_primitives_i16_window_push` | append until full, then shift and replace the oldest signed-16 sample |
| `0x00066560` / 64 | `goodix_primitives_byte_window_push` | byte-window push plus capacity-wrapped cursor advance |
| `0x000665A0` / 104 | `goodix_primitives_decimated_i16_window_push` | accept on phase zero, advance phase modulo the configured period, and maintain the wrapped accepted-sample cursor |
| `0x00066608` / 154 | `goodix_primitives_decimated_float_window_push` | the float twin with exact append/evict running-sum maintenance |

The native C descriptors retain the recovered count, capacity, phase, period,
cursor, and sum semantics while replacing raw target pointers with typed
pointers. Zero capacities or periods, corrupt counts/cursors/phases, empty
means, and invalid removals fail without the stock divide-by-zero or
out-of-bounds behavior. Tests cover fill, eviction order, cursor wrap,
decimation, skipped samples, sum maintenance, mean/removal, and invalid-period
rejection. These entries bring `goodix_primitives` to 133 exact-address
mappings, with 172 formerly opaque Goodix candidates compiled locally and 148
remaining.

## Numerical post-processing closure

Five reusable GH_SPO2/dlCom leaves / 270 bytes now compose entirely from
already admitted primitive behavior:

| Stock entry / size | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x00035F44` / 44 | `goodix_primitives_truncate_decimal` | multiply by `10^places`, convert to signed integer with truncation toward zero, and divide by the same scale |
| `0x00036EB4` / 72 | `goodix_primitives_bit_reverse_permute_pairs` | reorder `2^bit_count` two-word records by the admitted low-bit reversal helper, swapping only when the source index is lower |
| `0x00037DB4` / 56 | `goodix_primitives_finalize_warmup_average` | complete one-, two-, or three-sample warm-up state and set phase four; the three-sample sum retains target modular addition before signed division |
| `0x000668A4` / 50 | `goodix_primitives_normalize_by_max` | find the first maximum and scale the vector by its reciprocal unless it is below exact float bits `0x358637BD` |
| `0x00066C18` / 48 | `goodix_primitives_percentile_lookup` | truncate `(percentage / 100) * count` and return that float-vector element |

The typed APIs add explicit extents and reject decimal conversions outside
the signed-32 domain, undersized bit-reversal spans, empty normalization,
and percentile indices at or beyond the caller-owned vector. Tests pin
positive and negative decimal truncation, the complete three-bit
permutation, every warm-up phase plus modular overflow, exact reciprocal and
below-threshold normalization, and 25/50/75/99-percent lookups with the
100-percent overrun rejected. These entries bring `goodix_primitives` to 138
exact-address mappings, with 177 formerly opaque Goodix candidates compiled
locally and 143 remaining.

## NADT feature/statistics closure

Four NADT leaves / 280 bytes now use bounded caller-owned inputs:

| Stock entry / size | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x0005144C` / 66 | `goodix_primitives_i32_mean` | accumulate signed-32 samples through the recovered signed-64 path, convert to float, and divide by count |
| `0x000361D8` / 88 | `goodix_primitives_i32_squared_deviation_sum` | round the preceding mean through an explicit provider, sum squared integer deviations, and saturate at `0x3FFFFFFF` |
| `0x0003623C` / 70 | `goodix_primitives_indexed_i16_trimmed_mean` | gather signed-16 samples by signed-16 indices, retain 16-bit accumulation/subtraction wrapping, and remove one maximum and minimum when count exceeds two |
| `0x00029AA0` / 56 | `goodix_primitives_mask_columns_any` | scan a row-major packed-bit matrix and set each output column having any asserted row bit |

The reconstruction exposes the stock `round` dependency as a typed callback
and adds source extents, index validation, multiplication-overflow checks,
and empty-input rejection. Tests cover exact means/deviations, saturation,
two-element and trimmed aggregation, signed-16 wrap, invalid indices,
row-major mask addressing, preserved false-column bytes, and short packed
storage. These entries bring `goodix_primitives` to 142 exact-address
mappings, with 181 formerly opaque Goodix candidates compiled locally and
139 remaining.

## Feature-preparation and extrema-history closure

Four Goodix/NADT helpers / 258 bytes now have explicit typed state and former
private globals replaced by caller inputs:

| Stock entry / size | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x00032744` / 86 | `goodix_primitives_channel_scale_copy` | mode one multiplies each channel by the private scale vector and reports its private factor; every other mode copies and reports one |
| `0x00043860` / 28 | `goodix_primitives_i16_descriptor_mean` | calculate the signed-16 mean of the populated embedded descriptor and store the low signed-16 result |
| `0x0009775C` / 58 | `goodix_primitives_reverse_clamped_weighted_sum` | multiply coefficients by reverse history indices, clamping every exhausted reverse index to zero |
| `0x00097984` / 86 | `goodix_primitives_extrema_history_update` | alternate rising/falling extrema when the configured distance is crossed, retain extremum/sample counters, emit `1` or `-1` transitions, and increment the sample counter with target-width wrapping |

The channel scale vector and factor are explicit caller bindings rather than
opaque absolute addresses. All vectors and descriptors carry extents, while
the 20-byte extrema state preserves the recovered field layout. Tests cover
scale and copy modes, missing scale rejection, signed descriptor averaging,
reverse and clamped history indices, both extrema transitions and signed
counter wrap. These entries bring `goodix_primitives` to 146 exact-address
mappings, with 185 formerly opaque Goodix candidates compiled locally and
135 remaining.

## Array transformation, record history, and mask-row selection

Three helpers / 284 bytes now use checked caller-owned storage:

| Stock entry / size | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x00029394` / 96 | `goodix_primitives_normalize_rows_by_range` | for every row, find its minimum and maximum and divide every element by `maximum - minimum` only when the range is strictly above exact float bits `0x358637BD`; the minimum is not subtracted |
| `0x0004FDB8` / 64 | `goodix_primitives_record32_history_push` | append fixed 32-byte records until capacity, then evict the oldest record by shifting left and append the new record |
| `0x00066AB2` / 124 | `goodix_primitives_select_mask_row` | score packed mask rows addressed by one-based labels and return the first label with the maximum set-bit count |

The typed APIs add explicit matrix, history, and packed-bit extents. They
reject zero columns, impossible history capacities, undersized packed masks,
label zero, and inverted label ranges. Tests pin the exact normalization
threshold path, constant-row preservation, record eviction order, one-based
row selection, and first-maximum tie behavior. These entries bring
`goodix_primitives` to 149 exact-address mappings, with 191 formerly opaque
Goodix candidates compiled locally across all reconstructed modules and 129
remaining.

## Counted history, capped running means, and Int16 deviation

Three statistical/state helpers / 312 bytes now operate on typed caller-owned
records:

| Stock entry / size | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x0002F260` / 74 | `goodix_primitives_counted_word_history_push` | append UInt32 values until full, then evict the oldest value; increment the independent 32-bit lifetime push count with target-width wrapping |
| `0x00030090` / 128 | `goodix_primitives_running_triplet_update` | increment the sample count until capacity, update three running means using `(sample + old * (count - 1)) / count`, and store the explicit current timestamp |
| `0x00036394` / 110 | `goodix_primitives_i16_sample_standard_deviation` | accumulate signed-16 values with 32-bit wrapping, form centered deviations using the signed low half of the count, accumulate signed squares through the recovered 64-bit path, then compute `sqrt(sum / (count - 1)) / count` |

The native records retain the recovered 32-bit count/capacity/counter fields
and the exact 24-byte triplet layout. Checked APIs reject zero capacities,
corrupt count/capacity relationships, unavailable square-root providers, and
unrepresentable loop counts; the stock zero result is retained for absent or
singleton Int16 input. Tests cover append, eviction, lifetime-counter wrap,
mean saturation, post-capacity updates, timestamps, invalid states, ordinary
and constant signed samples, and zero-input behavior. These entries bring
`goodix_primitives` to 152 exact-address mappings, with 194 formerly opaque
Goodix candidates compiled locally and 126 remaining.

## Single-record transition veneer

The 52-byte entry at `0x00036282` performs exactly one iteration and delegates
to the already admitted `0x00036C32` transition update after dereferencing its
three enclosing record pointers. The typed reconstruction removes the raw
`0x2C`/`0x44` enclosing strides and aliases the entry to
`goodix_primitives_update_transition`, whose tests already pin state zero,
state one, source-flag clearing, and counter increment behavior. This brings
`goodix_primitives` to 153 exact-address mappings, with 195 formerly opaque
Goodix candidates compiled locally and 125 remaining.

## Sort, top-selection, extrema-index, and reverse packed-float leaves

Four numerical leaves / 470 declared bytes now have transparent bounded C:

| Stock entry / size | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x00035812` / 62 | `goodix_primitives_insertion_sort_floats` | stable ascending insertion sort using the stock `previous <= value` stop comparison, including its NaN placement behavior |
| `0x00036EFC` / 118 | `goodix_primitives_top_descending_strided` | retain the largest requested strided samples in descending order, inserting newer equal values before older equal values |
| `0x00098E4C` / 126 | `goodix_primitives_i16_local_extrema_indices` | independently collect strict signed-16 local maxima and minima indices with optional output/count families and UInt8 counts |
| `0x00028DDA` / 164 | `goodix_primitives_f32_bits_to_packed_6_9` | six-byte selector head plus shared tail converting raw Float32 bits to the recovered sign/6-exponent/9-fraction format, including rounding, subnormals, overflow, infinities, and NaN payload bits |

The packer operates only on raw integer bits, so host floating-point NaN and
rounding choices cannot alter its result. The selection and extrema APIs add
explicit source/output extents and reject overflow that the stock routines
would otherwise express through wrapped indices or unchecked writes. Tests
cover finite ordering, duplicates, strided top selection, extent failures,
strict signed peaks/valleys, optional empty scans, zero/sign/subnormal/normal
packing, infinity, and NaN. These entries bring `goodix_primitives` to 157
exact-address mappings, with 199 formerly opaque Goodix candidates compiled
locally and 121 remaining.

## Grouped weighted sums and event-pair alignment

Two call-free array transforms / 250 bytes now use explicit typed geometry:

| Stock entry / size | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x00034490` / 106 | `goodix_primitives_grouped_row_weighted_sums` | for each coefficient group and input row, dot the group with the column-major row slice and emit group-major row outputs |
| `0x000481A4` / 144 | `goodix_primitives_align_event_pairs` | for each selected primary event, advance past older secondary events, consume a secondary event strictly before the next primary (or any remaining secondary for the final primary), otherwise duplicate the primary; add the recovered wrapping `(5 - mode) * 25` offset to both outputs |

The native APIs replace embedded pointer/count/start tuples with explicit
extents and reject malformed cursors, multiplication overflow, undersized
inputs, and undersized outputs. Tests pin both group/row layouts, source
extent failures, interval pairing, final-event pairing, offset application,
missing-secondary fallback, nonzero primary starts, and output-capacity
rejection. These entries bring `goodix_primitives` to 159 exact-address
mappings, with 201 formerly opaque Goodix candidates compiled locally and
119 remaining.

## UInt8 deviation, positive cosine, and extrema-index collection

Three statistical/state entries / 474 bytes now use typed caller-owned inputs:

| Stock entry / size | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x000663B4` / 120 | `goodix_primitives_u8_population_standard_deviation` | compute the Float32 mean of a UInt8 descriptor, accumulate squared deviations, divide by the UInt16 count, and apply the explicit square-root provider |
| `0x000377D8` / 178 | `goodix_primitives_positive_cosine_similarity` | divide the vector dot product by the product of the two Euclidean norms and return only a strictly positive result; empty, zero-norm, and non-positive correlations produce zero |
| `0x00087618` / 176 | `goodix_primitives_collect_extrema_indices` | initialize the 20-byte alternating-extrema state from the first signed-32 sample, delegate every sample to the admitted `0x00097984` state update, and collect rising, falling, and combined signed-16 indices with the stock `count / 2` storage cap |

The APIs make the stock descriptor widths and implicit array capacity explicit,
reject unavailable square-root providers and unrepresentable loop counts, and
preserve the stock distinction between uncapped rising/falling totals and the
combined count that advances only while its optional output is present and has
room. Tests cover ordinary and zero-count deviation, parallel, opposing,
zero-norm, and empty vectors, three successive alternating extrema, the
combined-list cap, omitted outputs, and undersized storage. These entries bring
`goodix_primitives` to 162 exact-address mappings, with 204 formerly opaque
Goodix candidates compiled locally and 116 remaining.

## Gated triplet copy and threshold-crossing history

Two state helpers / 192 bytes now have explicit bounded records:

| Stock entry / size | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x00030E1C` / 72 | `goodix_primitives_copy_fresh_gated_triplet` | copy three Float32 fields when the unsigned wrapping source-timestamp delta is greater than 20 and the gate is strictly greater than zero and less than exact Float32 `30.0`; do not update the destination timestamp |
| `0x000419C8` / 120 | `goodix_primitives_accumulate_threshold_crossings` | form the wrapping signed-32 offset `(mode - 5) * 25`, append every adjusted sample strictly above the history value that was last at entry, compensate the cursor for full-window eviction, count this call's emissions in UInt16, then advance the cursor past stored values below the offset |

The threshold accumulator delegates storage mutation to the already admitted
`0x000664F4` fixed-capacity word-window body. Its typed API rejects corrupt or
zero-capacity histories and unrepresentable loop counts while retaining
32-bit offset/sample wrap and 16-bit emission wrap. Tests pin the age and gate
boundaries, timestamp wraparound, triplet preservation, multiple crossings,
full-window eviction/cursor compensation, offset-based cursor advancement,
and corrupt history rejection. These entries bring `goodix_primitives` to 164
exact-address mappings, with 206 formerly opaque Goodix candidates compiled
locally and 114 remaining.

## Strict local-peak selection and six-float state merge

Two call-free numerical/state entries / 258 bytes are reconstructed directly:

| Stock entry / size | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x00031774` / 82 | `goodix_primitives_strict_local_peak_max` | scan UInt8-addressable interior Float32 samples, retain the greatest candidate strictly above both neighbors and strictly above the current zero-initialized result, and return zero/index zero when none qualifies |
| `0x000299EC` / 176 | `goodix_primitives_merge_six_float_state` | in continuation mode, zero-clamp `state[2] - incoming[1]`, add `incoming[2]`, and accumulate the two trailing incoming fields; in advance mode, zero-clamp the reverse gap and roll all six state fields in the recovered statement order |

The peak API rejects the stock zero-count underflow case and counts that cannot
be represented by the recovered eight-bit loop ordinal. The merge API exposes
the fixed six-/five-float extents without assigning unsupported semantic field
names. Tests cover strict neighbors, plateau rejection, the positive-only
baseline, count-width rejection, both merge branches, both gap signs, and null
inputs. These entries bring `goodix_primitives` to 166 exact-address mappings,
with 208 formerly opaque Goodix candidates compiled locally and 112 remaining.

## Masked contiguous sign-run zeroing

The call-free 222-byte entry at `0x00072FB8` scans a Float32 source and byte
marker vector. A marker value of one on a strictly positive or strictly
negative sample zeroes the complete contiguous run of the same sign in the
output, including samples before the marker that may already have been copied.
Unmarked samples are copied bit-for-bit; a marked zero or unordered value
leaves its output slot untouched. `goodix_primitives_zero_masked_sign_runs`
makes all three extents explicit, accepts the stock empty operation, and
rejects counts outside the recovered signed loop width. Tests cover forward
and backward propagation, both signs, marked zero preservation, a tail marker,
and empty input. This entry brings `goodix_primitives` to 167 exact-address
mappings, with 209 formerly opaque Goodix candidates compiled locally and 111
remaining.

## Signed running min/max, mean, and squared deviation

Thumb inspection corrects Ghidra's parameter annotation for the call-free
158-byte entry at `0x0005CED4`: register `r1` contains a signed-32 sample, not
a Float32 value. The stock body selects one of four interleaved lanes through
a byte ordinal in the enclosing object; the typed
`goodix_primitives_running_i32_statistics_update` API exposes one lane as
signed minimum/maximum plus Float32 mean and squared-deviation state. Ordinal
one initializes all four fields. Later ordinals update extrema, add
`ordinal / (ordinal + 1) * (sample - prior_mean)^2`, and then update the mean
with the recovered `(sample - prior_mean) / (ordinal + 1)` order. Tests pin
initialization, rising and falling extrema, exact ordinary Float32 results,
zero-ordinal rejection, and null-state rejection. This entry brings
`goodix_primitives` to 168 exact-address mappings, with 210 formerly opaque
Goodix candidates compiled locally and 110 remaining.

## Difference equation and command/status polling

Two entries / 190 bytes now replace their remaining runtime indirections with
explicit typed providers:

| Stock entry / size | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x00028B18` / 114 | `goodix_primitives_second_order_difference_output` | evaluate `b1*x0 + b2*x1 + b0*input - (a1*y0 + a2*y1)` in the recovered Float32 order; when raw `a0` is not exact `+1.0f`, divide by `a0`, convert to double, call the standard `round` provider, and convert back to Float32 |
| `0x00034B08` / 76 | `goodix_primitives_command_status_poll` | when flag bit `0x2000` is set, issue command `0xA6`; otherwise issue `0xAE`, then read address `0xAE` one unit at a time until status clears or unsigned wrapping elapsed time reaches `0x140`, returning `-3` only for nonzero status at timeout |

The math API permits an absent round provider only on the exact `a0 == 1.0f`
bypass. The polling API binds command, register-read, and clock operations plus
their context without embedding a vendor vtable or address. Tests pin exact
equation order, bypass and rounded paths, missing-provider rejection, command
failure propagation, immediate success, bit selection, timeout status, and
clock wraparound. These entries bring `goodix_primitives` to 170 exact-address
mappings, with 212 formerly opaque Goodix candidates compiled locally and 108
remaining.

## Context teardown, record-family teardown, and median

Three entries / 346 bytes close a source-ready ownership and numerical layer:

| Stock entry / size | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x0003E6B0` / 68 | `goodix_primitives_algorithm_context_destroy` | release target field `+0x260`, then tail-enter the internal `0x00029354` destructor, which conditionally releases `+0x1C0`, `+0x1DC`, and `+0x1F4` before releasing the root context |
| `0x00029BBC` / 184 | `goodix_primitives_record_family_teardown` | release nine 16-byte descriptor payloads in physical order `0..6, 8, 7`, then release-and-clear nine 8-byte slots and seven 16-byte slots |
| `0x000567C4` / 94 | `goodix_primitives_float_median` | select all Float32 samples in descending order and return the center sample or the Float32 half-sum of the two center samples; empty input returns exact `+0.0f` |

Raw Thumb-2 is authoritative for `0x0003E6B0`: Ghidra attached calls from the
missed internal boundary at `0x00029354` to this later function and consequently
rendered a misleading inlined destructor. The reconstruction exposes only the
four ownership bindings instead of retaining undocumented target padding. For
the median, caller-owned bounded scratch replaces the stock transient heap
allocation while preserving the already reconstructed descending-selection
semantics. Tests pin root-last destruction, all release order and clearing
effects, the non-monotonic descriptor order, odd/even medians, zero length, and
insufficient scratch rejection. These entries bring `goodix_primitives` to 173
exact-address mappings, with 215 formerly opaque Goodix candidates compiled
locally and 105 remaining.

## Explicit table dispatch and fixed payload send

Two entries / 100 bytes remove their final absolute-table dependencies:

| Stock entry / size | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x00028AD4` / 62 | `goodix_primitives_dispatch_indexed_operation` | return zero for a null record; otherwise select one of seven six-argument operations through `record[0]` and propagate its signed result |
| `0x0002A65C` / 38 | `goodix_primitives_send_fixed_aa_pair` | invoke an explicitly bound provider operation with its explicit selector, the two-byte payload `AA AA`, length two, and the two caller words |

The dispatcher accepts the seven-entry operation table directly instead of
copying 28 bytes from stock ROM. It additionally rejects an out-of-range index
or null selected operation, which are undefined stock states. The payload API
replaces both the global selector table and provider-vtable address with typed
arguments; the stock ignored the provider return value, so the callback is
intentionally `void`. Tests pin all five forwarded words, result propagation,
the null-record zero path, index validation, exact payload bytes and length,
selector forwarding, and the missing-provider guard. These entries bring
`goodix_primitives` to 175 exact-address mappings, with 217 formerly opaque
Goodix candidates compiled locally and 103 remaining.

## NADT normalized peak quality

The call-free 180-byte entry at `0x0003497C` appends signed index
`period - 1` to a UInt8-counted history. For every retained index it computes
`(index + 1) / period`, computes `abs(sample[index]) / amplitude_scale`, and
accumulates the absolute difference in the exact Float32 instruction order.
One retained index forces error `0.5`; otherwise the sum is divided by
`count - 1`. Error above `0.5` (including the positive NaN produced by invalid
stock divisors) clamps to `0.5`, and the result is the truncating unsigned
conversion of `100 - 2 * error * 100`.

`goodix_primitives_peak_quality_update` exposes sample and index extents,
requires positive divisors, rejects negative/out-of-range retained indices
before mutating the history, and preserves the UInt8 count and signed-Int16
index representation. Tests cover the one-entry zero-quality case, an exact
100-quality trajectory, absolute negative amplitude, a 50-quality mismatch,
the 0.5 clamp, and capacity rejection. This entry brings
`goodix_primitives` to 176 exact-address mappings, with 218 formerly opaque
Goodix candidates compiled locally and 102 remaining.

## Shared-state Int16 and Int32 autocorrelation transforms

The 192-byte entries at `0x00031624` and `0x00035F70` have identical control
flow and share target state address `0x20007C88`; only the input load width
differs. For every lag, both accumulate the low 32 bits of
`(sample[i-lag] - mean) * (sample[i] - mean)`. Lag zero becomes the baseline.
A positive baseline maps each correlation through the exact Float32 order
`correlation / (baseline / scale)`, converts toward zero, and narrows to
signed Int16. When that value repeats the prior output, it decrements if the
correlation fell and increments otherwise. Nonpositive baseline writes zero
without tie adjustment. Both variants update the shared prior-output/prior-
correlation pair at every lag and reverse the completed Int16 output array.

The reconstruction uses unsigned low-word multiplication/addition to make the
stock modular Int32 arithmetic defined in C, explicit bit conversions for
signed target representations, checked Float32-to-Int32 range, and an explicit
caller-owned shared state. Tests pin the `[21, 57, 100]` reversed trajectory,
both input widths, falling and rising tie adjustment, shared final state,
nonpositive-baseline zeroing, empty input, and zero-scale rejection. These two
entries bring `goodix_primitives` to 178 exact-address mappings, with 220
formerly opaque Goodix candidates compiled locally and 100 remaining.

## Ordered register reset wrapper

The callerless 28-byte entry at `0x0002E8CC` contains no hidden algorithm or
table: Thumb-2 proves an ordered call to `GH3X2X_WriteReg(0x0502, 0)` followed
by the tail call `GH3X2X_WriteRegBitField(0, 10, 10, 0)`. Both callees already
route to pinned public-democode source. The local
`goodix_primitives_reset_register_fields` function expresses their interfaces
as typed write-register and write-bit-field operations and retains the exact
constants and order without embedding the stock ops table. Tests capture both
operations, all arguments, ordering, and missing-operation rejection. This
entry brings `goodix_primitives` to 179 exact-address mappings, with 221
formerly opaque Goodix candidates compiled locally and 99 remaining.

## Input-word copy and typed dispatch wrapper

The 40-byte entry at `0x0005CEA8` first copies the caller's input word to the
output and then invokes the recovered seven-way dispatcher at `0x00028AD4`.
The stock call forwards the owner context fields at offsets `0x64` and `0x68`,
the input and output pointers, and a final zero in their exact order; its
Boolean result is whether the signed dispatcher result is nonzero. The local
`goodix_primitives_dispatch_word_copy` replaces the absolute owner pointer and
operation table with a typed context and callback array. Host tests pin the
copy-before-dispatch behavior, pointer-width-safe forwarding, all five bound
arguments, nonzero/zero result conversion, and null-record behavior. This
entry brings `goodix_primitives` to 180 exact-address mappings, with 222
formerly opaque Goodix candidates compiled locally and 98 remaining.

## Float32 half-away rounding

The 84-byte entry at `0x00035084` converts its Float32 input exactly to
binary64, adds `0.5` and calls the toolchain `floor` function for positive
inputs, or subtracts `0.5` and calls `ceil` for nonpositive inputs, before the
exact binary64-to-Float32 conversion. The transparent
`goodix_primitives_round_float_half_away_from_zero` implements the equivalent
operation directly from the IEEE-754 Float32 sign, exponent, and fraction, so
it requires no hidden table or libm body. Tests cover values on both sides of
each half boundary, signed zero, the largest fractional Float32 magnitude,
infinity, and NaN. This entry brings `goodix_primitives` to 181 exact-address
mappings, with 223 formerly opaque Goodix candidates compiled locally and 97
remaining.

## Processing-context teardown

The 88-byte entry at `0x0006CC60` destroys two explicitly bound owner roots in
stock order. It first invokes the admitted 25-slot record-family teardown at
`0x00029BBC` and releases that root. It then dispatches the three recovered
state destructors at context offsets `0x6C`, `0x70`, and `0x84`, clears owned
slots `0xB0`, `0xBC`, `0xCC`, and `0xD8` through the admitted guarded-release
contract, and finally releases the processing root. The local
`goodix_primitives_processing_context_destroy` replaces both absolute globals
and the copied state table with typed owner records, handlers, and a release
binding. Tests pin all 31 releases, the three dispatches and their order, the
four clearing effects, root-last ownership, and invalid-binding rejection.
This entry brings `goodix_primitives` to 182 exact-address mappings, with 224
formerly opaque Goodix candidates compiled locally and 96 remaining.

## GH_NADT preprocessing identity builder

The 126-byte entry at `0x0006E788` concatenates only recovered identity text:
`GH_NADT_pre`, `_pv`, `_v1.0.2.0`, the nonempty shared qualifier `nc`, hash
`548d894d`, a newline, and the admitted DSP identity
`dsp_pv_v1.3.0_30234f22`. The local
`goodix_primitives_build_nadt_version` uses the same checked append primitive
as the SpO2 builder and reuses `goodix_primitives_copy_dsp_version`; it clears
the destination on insufficient capacity. Tests pin the exact 58-byte text,
the exact 59-byte minimum capacity including NUL, short-buffer clearing, and
null rejection. This entry brings `goodix_primitives` to 183 exact-address
mappings, with 227 formerly opaque Goodix candidates compiled locally and 93
remaining.

## Elapsed-gated dispatch and scaled output

The 150-byte entry at `0x0005CDF8` first invokes the selected-slot elapsed
accounting veneer with the caller's second argument intact in `r1`. A rejected
timestamp returns one without changing the output. Otherwise it conditionally
clears the three mode-one Float32 buffers, dispatches through the recovered
seven-way operation table with owner fields `+0x64` and `+0x68`, the caller
input, a pointer to the local output-pointer slot, and final zero. A nonzero
operation result clears the output to exact `+0.0f` and returns one.

On success, raw VFP instructions prove the exact Float32 sequence
`((((15 + output) * 60) * 25) / 3) * 0.00390625`. The leading 15 is the
compile-time equivalent of the stock binary64 `floor(15.859999656677246)` and
signed-integer conversion. The local
`goodix_primitives_timed_dispatch_scaled_output` replaces the absolute owner
root and copied ROM callback table with explicit elapsed, buffer, mode,
dispatch-record, owner-word, and operation bindings. Tests pin both failure
classes, unchanged elapsed-gate output, all callback arguments including the
indirect output pointer, elapsed-state mutation, mode-one buffer clearing, and
the exact successful result `42.96875f`. This entry brings
`goodix_primitives` to 184 exact-address mappings, with 229 formerly opaque
Goodix candidates compiled locally and 91 remaining.

## Seven-word NADT graph-executor veneer

The 18-byte entry at `0x0002907C` preserves `r0` through `r3`, loads the three
caller stack words, stores them unchanged into the outgoing argument area,
calls `0x00037890`, and returns its signed result. The local
`goodix_primitives_nadt_graph_execute_veneer` replaces that absolute executor
address with an explicit seven-word callback while leaving the executor
itself independently source-gated. Tests pin all four register arguments, all
three stack arguments, signed result propagation, and missing-binding
rejection. This entry brings `goodix_primitives` to 185 exact-address
mappings, with 230 formerly opaque Goodix candidates compiled locally and 90
remaining.

## NADT sample statistics, summary, and downstream dispatch

Three entries / 380 bytes close the complete summary path before the remaining
NADT downstream stage:

| Stock entry / size | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x0003F89C` / 316 | `goodix_primitives_nadt_sample_statistics` | cap the populated Int16 input at 125 samples; compute Float32 mean and population deviation; clamp `factor * deviation` through configured minimum/maximum thresholds; emit truncating mean, low threshold byte, and strict outlier count |
| `0x00091870` / 32 | `goodix_primitives_nadt_sample_summary_build` | invoke the statistics body, append the already admitted secondary Int16 descriptor mean at output `+4`, and return zero |
| `0x000290BC` / 32 | `goodix_primitives_nadt_summary_dispatch` | build the six-byte summary, then forward owner fields `+0` and `+0x1C`, the two caller words, and summary pointer to the downstream stage; propagate its signed result |

The transparent context replaces target padding with explicit threshold,
primary/secondary descriptor, and downstream-word bindings. A typed callback
keeps only the independently gated `0x00077D2C` stage outside this closure.
Compile-time assertions pin the four- and six-byte output ABIs. Host tests pin
the exact mean/deviation threshold trajectory, strict outlier count, secondary
mean, all five downstream arguments, signed result propagation, and invalid
binding rejection. These entries bring `goodix_primitives` to 188
exact-address mappings, with 233 formerly opaque Goodix candidates compiled
locally and 87 remaining.

## Caller-scratch transform-prefix adapter

The 48-byte entry at `0x00035772` copies `input_count` Float32 values into the
scratch pointer carried as the eighth AAPCS argument, invokes
`0x00075E1C(scratch, input_count, transform_count)`, then tail-copies exactly
`output_count` Float32 values into the destination referenced by the fourth
argument. Raw code proves that the legacy fifth and sixth arguments are not
read. The local `goodix_primitives_float_transform_prefix_copy` replaces the
absolute transform address and indirect output slot with an explicit typed
callback, bounded scratch, and bounded destination. Tests pin copy-before-call
ordering, both callback counts, provider mutation, prefix-only output, retained
destination tail, and capacity/provider rejection. The underlying transform
remains independently gated. This entry brings `goodix_primitives` to 189
exact-address mappings, with 234 formerly opaque Goodix candidates compiled
locally and 86 remaining.

## Interpolated quantile, signed mask, and difference summary

Five entries / 982 bytes close the complete NADT mask/difference-summary
callgraph:

| Stock entry / size | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x00030CD8` / 312 | `goodix_primitives_float_quantile_interpolated` | copy and sort into transient scratch; use type-5 positions `(i + 0.5) / count`; clamp outside the first/last positions and linearly interpolate inside |
| `0x0007309C` / 130 | `goodix_primitives_nadt_quartile_mask` | obtain 0.75/0.25 quantiles; form `upper = q3 + multiplier*(q3-q1)` and `lower = q1 - multiplier*(q3-q1)`; emit `+1`, `-1`, or zero |
| `0x00030970` / 108 | `goodix_primitives_nadt_nonuniform_mask_count` | convert the configuration byte to tenths, count nonzero signed-mask bytes, and reset the count when every outlier has the same sign |
| `0x0002F2F8` / 378 | `goodix_primitives_nadt_positive_difference_statistics` | retain positive indexed differences; for a final zero, accept the suffix-minimum replacement only when it lies within 0.85..1.15 of the prior value; emit mean, relative variance, UInt8 count, and five-sixths coverage flag |
| `0x0007311E` / 54 | `goodix_primitives_nadt_difference_summary_execute` | compose the signed-mask count and positive-difference summary and return zero |

Caller-owned Float32 and Int8 scratch replace all three stock transient heap
allocations. Literal bytes pin the terminal band to binary64 0.85 and 1.15 and
the quantile half-position to binary64 0.5. The transparent twenty-byte result
retains stock offsets `+0`, `+8`, `+0xC`, `+0x10`, and `+0x11`, with compile-time
ABI assertions and reserved bytes left untouched. Tests cover exact quartile
interpolation, two-sided and uniform-sign masks, successful terminal recovery,
mean/relative variance, coverage, composition, and invalid indices/capacities.
These entries bring `goodix_primitives` to 194 exact-address mappings, with
239 formerly opaque Goodix candidates compiled locally and 81 remaining.

## NADT rolling accumulation and vector geometry

Five entries / 1,070 bytes close the stateful accumulation branch reached by
the NADT preprocessing root:

| Stock entry / size | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x00036DD4` / 216 | `goodix_primitives_nadt_rolling_feature_update` | push one Float32 sample through the recovered 25-tap smoothing kernel, delayed residual, 25-tap residual kernel, and cadence-average window |
| `0x0002FEE2` / 114 | `goodix_primitives_nadt_feature_pair_update` | compose the rolling feature with the shared `0x0002F2AC` cadence accumulator and average-emission tail |
| `0x0002F660` / 354 | `goodix_primitives_nadt_channel_ratio_update` | update two 100-byte-equivalent feature branches, form primary/secondary and bounded combined ratios, and append the half-scale primary sample |
| `0x00061C48` / 318 | `goodix_primitives_nadt_vector_geometry_update` | derive three-axis magnitude, signed-16 magnitude delta, polar angle in degrees, and the cadence-averaged angle |
| `0x000357CE` / 68 | `goodix_primitives_nadt_accumulation_execute` | compose channel and geometry updates and return ready only when `sample % 25 == 24` after the 125-sample warm-up |

The dropped decompiler argument on the second pair call is restored from raw
Thumb-2 as `state + 0x64`. The two consecutive 25-tap tables formerly reached
through the absolute word at `0x00036EAC` are explicit bit-exact hex-float C
arrays; the ratio floor (`1e-6`), ratio divisor threshold (`1e-7`), inclusive
`0.2..2.0` bit-range test, `180 / pi` conversion, negative-Z correction, and
zero-Z 90-degree fallback are all source-visible. Typed states replace the
stock 32-bit pointer/padding layout without changing operation order.

Tests cover two-sample accumulator reset and endpoint emission, all five
rolling stages, both channel branches and three ratio windows, half-scale
decimation, zero/negative-Z geometry, magnitude deltas, angle averaging,
invalid cadence rejection, and the exact status transition at samples 24 and
124. These entries bring `goodix_primitives` to 199 exact-address mappings,
with 244 formerly opaque Goodix candidates compiled locally and 76 remaining.

## Complete NADT accumulation boundary

The final five entries / 1,800 bytes close the historical thirty-function NADT
accumulation/decision boundary:

| Stock entry / size | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x00072DCC` / 490 | `goodix_primitives_nadt_batch_accumulate` | reset one period, accumulate 24-byte channel pairs and three wrapping signed words, then emit per-channel, cross-channel, and vector averages with status three until the endpoint |
| `0x00076A68` / 252 | `goodix_primitives_nadt_record_encode` | serialize a completed record into sixteen scaled UInt32 words using the recovered positive half-up conversion and fixed zero fields |
| `0x00036974` / 460 | `goodix_primitives_nadt_output_record_build` | populate source/reference metrics, preserve the record's earlier history state, and emit the live-record marker at word twelve |
| `0x00044A78` / 348 | `goodix_primitives_nadt_output_record_quality_update` | maintain two saturating/reset counters, append metric history, select the default or threshold-switched tail span, and emit short-history/unstable-spread bits |
| `0x00077D2C` / 250 | `goodix_primitives_nadt_channel_analysis_execute` | align event pairs in caller scratch, summarize both 125-sample ratio tails, compute pair-window means and cosine percent, and compose the analysis record |

The former transient allocation in `0x00077D2C` is replaced by bounded caller
index scratch; its two summary invocations reuse explicit Float32 sort and Int8
mask scratch. All scales (`1`, `100`, `10,000`, and `100,000`), the fallback
spread sentinel, saturating counter rules, quality bits, 125-sample tail, and
status values are source-visible. Tests pin reset/finalize behavior, wrapping
signed sums, both record marker modes, reference gating, counter saturation and
reset, threshold half-up selection, stable/unstable flags, aligned indices,
both summaries, means, cosine percentage, and all capacity failures.

All 30 entries / 5,126 bytes in the original NADT accumulation boundary now
compile transparently. These entries bring `goodix_primitives` to 204
exact-address mappings, with 249 formerly opaque Goodix candidates compiled
locally and 71 remaining.

## Complete NADT peak-mask boundary

The final five entries / 918 bytes close the historical seven-function NADT
peak-mask boundary; `0x00066AB2` and `0x00029AA0` were already local:

| Stock entry / size | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x00030178` / 494 | `goodix_primitives_nadt_extrema_neighborhood_mask` | construct the LSB-first row-major strict-extrema mask, including edge fill and the recovered equal-plateau depth suppression |
| `0x00076B78` / 100 | `goodix_primitives_nadt_peak_mask_columns` | allocate logically as `floor(rows*columns/8)+1`, select the highest-scoring label from the configured range, and reduce its row prefix to column flags |
| `0x00047FA8` / 112 | `goodix_primitives_nadt_peak_index_collect` | collect zero-flag extrema and retain the newest fixed-capacity indices by shifting on overflow |
| `0x0003441C` / 116 | `goodix_primitives_nadt_peak_histories_update` | run both extrema polarities through shared scratch and append their indices to paired threshold-crossing histories |
| `0x00030114` / 96 | `goodix_primitives_nadt_primary_ratio_peak_update` | process the last 125 primary-ratio samples with descriptor `{36,2,1}`, index capacity 20, and the caller's mode |

Caller-owned packed, column, and index scratch replaces both stock heap
allocations. Tests pin exact plateau bytes, maxima/minima polarity, the stock
extra-byte allocation rule, newest-index eviction, paired history mutation,
and the fixed entry configuration. At that checkpoint the complete Goodix
reconstruction had 273 compiled mappings: 254 formerly opaque candidates,
seventeen public-democode replacements, and two product entries.

## NADT local-maximum/index closure

The next two entries / 574 bytes complete the multiscale local-maximum branch
used by the dual-window feature extractor:

| Stock entry / size | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x00066900` / 434 | `goodix_primitives_nadt_local_maximum_prefix_counts` | build the strict local-maximum mask at every configured separation, score each row by non-maximum count, select the first minimum-score row, and reduce rows zero through that row into per-column Int16 counts |
| `0x00036734` / 140 | `goodix_primitives_nadt_local_peak_indices` | accept zero-count peaks beyond `warmup+1`, retain the recovered adjacent-one/equal-value plateau continuation, and stop appending at the caller's fixed capacity |

The already-local `0x000668DC` supplies first-minimum selection. Caller-owned
packed, row-score, and column-count scratch replaces both stock zero-allocations;
VFP unordered comparisons are preserved explicitly. Tests cover exact mask
bytes, row scores, ordinary and plateau peaks, warm-up exclusion, capacity
truncation, zero capacity, and NaNs.

At that checkpoint the complete Goodix reconstruction had 275 compiled
mappings: 256 formerly opaque candidates, seventeen public-democode
replacements, and two product entries.

## NADT centered-correlation closure

Two entries / 446 bytes complete the normalized autocorrelation branch:

| Stock entry / size | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x00092A04` / 336 | `goodix_primitives_centered_cross_correlation` | emit the complete centered `2*max(n,m)-1` cross-correlation with index `max(n,m)-1+i-j`, preserving untouched outer slots when the input lengths differ |
| `0x000666A4` / 110 | `goodix_primitives_nadt_normalized_autocorrelation` | compute equal-input correlation in caller scratch, retain its leading `count` values, select the first maximum, and normalize only when the maximum's signed Float32 bits are at least `0x358637BD` |

The complete unequal-length behavior is retained even though the stock caller
passes one input twice. Tests cover both input-length orientations, untouched
outer slots, equal-input output order, normalization, sub-threshold behavior,
NaN propagation, and capacity failures. The stock `2*count-1` allocation is
replaced by bounded caller-owned Float32 scratch.

The complete Goodix reconstruction now has 277 compiled mappings: 258 formerly
opaque candidates, seventeen public-democode replacements, and two product
entries. The remaining Goodix candidate gate is 62 functions / 34,506 bytes;
locally reconstructed candidate bodies cover 31,542 declared stock bytes.

## GH_HR cardinal-spline closure

Two entries / 542 bytes complete the spline helper pair used by the recovered
GH_HR feature/event code:

| Stock entry / size | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x00048018` / 392 | `goodix_primitives_cardinal_spline_point` | evaluate one two-dimensional point from four controls using the recovered 4x4 cardinal-spline coefficient matrix and signed shape parameter |
| `0x0003773C` / 150 | `goodix_primitives_sample_cardinal_spline` | emit `subdivisions + 1` evenly spaced samples from parameter zero through one, including both endpoints |

The static table at stock address `0x000B14AC` is represented as transparent
matrix construction rather than copied firmware bytes. The local evaluator
retains the stock Float32 conversion and multiply/add ordering, while the
sampler exposes explicit output capacity. Tests cover Catmull-Rom endpoints
and midpoint, the alternate zero-half-tension shape, zero subdivisions, null
input, and insufficient capacity.

The complete Goodix reconstruction now has 279 compiled mappings: 260 formerly
opaque candidates, seventeen public-democode replacements, and two product
entries. The remaining Goodix candidate gate is 60 functions / 33,964 bytes;
locally reconstructed candidate bodies cover 32,084 declared stock bytes.

## GH_HR event-pair rebalancing leaf

Entry `0x00037DEC` / 158 bytes is reconstructed as
`goodix_primitives_hr_rebalance_record_pair`. It reads the two recovered
32-byte event records at offsets `0x14` (Float32 center) and `0x18` (eligibility
word), compares their midpoint and individual baseline distances against the
scaled tolerance, and retains the stock gate-order and unordered-comparison
behavior. A qualifying pair is split about the baseline after removing two
history slots; a rejected pair removes one slot and retains only the second
record. Both paths reuse the already admitted fixed-32-byte history append.

The public API separates the stock context's baseline/gate values from its
record storage and validates history capacity before mutation. Tests cover the
qualifying split, gate rejection, exact stored records, NaN rejection, null
state, and history-count transitions.

The complete Goodix reconstruction now has 280 compiled mappings: 261 formerly
opaque candidates, seventeen public-democode replacements, and two product
entries. The remaining Goodix candidate gate is 59 functions / 33,806 bytes;
locally reconstructed candidate bodies cover 32,242 declared stock bytes.

## Quartile-band median replacement leaf

Entry `0x000368D0` / 160 bytes is reconstructed as
`goodix_primitives_replace_far_from_median`. It copies the input to bounded
caller scratch, sorts the copy through the already admitted `0x0003754A`
alias/`0x00037574` target, selects the 25th, 75th, and 50th percentile entries,
and replaces source values whose absolute median distance exceeds the signed
factor times the interquartile spread. The stock signed raw-Float32 comparison
that clamps spreads below `5.0` is retained exactly.

The stock heap allocation is replaced by explicit scratch capacity. The API
also rejects aliasing scratch, zero/oversized counts, and insufficient storage.
Tests cover the recovered discrete percentile indices, minimum-spread clamp,
far-value replacement, sorted scratch, capacity rejection, and alias rejection.

The complete Goodix reconstruction now has 281 compiled mappings: 262 formerly
opaque candidates, seventeen public-democode replacements, and two product
entries. The remaining Goodix candidate gate is 58 functions / 33,646 bytes;
locally reconstructed candidate bodies cover 32,402 declared stock bytes.

## SpO2 packed-workspace triplication leaf

Entry `0x0003F740` / 168 bytes is reconstructed as
`goodix_primitives_spo2_expand_packed_triplicate`. When the recovered disabled
byte is zero and ready byte is one, the stock code evaluates `ceil(60.0)`,
derives a 180-value bank, converts the same packed 6/9 vector three times, and
writes the banks at Float32 workspace indices 720, 900, and 1,080. The final
write ends at index 1,259, matching the later 7x180 normalization workspace.

The fixed literal and layout are transparent named constants; packed conversion
reuses the already admitted bit-exact `0x00028DE6` implementation. The API
replaces the two absolute RAM bindings with explicit source/workspace spans and
capacity checks. Tests compare every output bit in all three banks, preserve
the 720-value prefix, exercise the inactive no-op gate, and reject insufficient
workspace capacity.

The complete Goodix reconstruction now has 282 compiled mappings: 263 formerly
opaque candidates, seventeen public-democode replacements, and two product
entries. The remaining Goodix candidate gate is 57 functions / 33,478 bytes;
locally reconstructed candidate bodies cover 32,570 declared stock bytes.

## GH_HR clamped-deviation outlier counter

Entry `0x00070B60` / 178 bytes is reconstructed as
`goodix_primitives_hr_count_mean_outliers`. It obtains the active buffer mean
and sample standard deviation through the already admitted `0x00029656` and
`0x0003738C` contracts, multiplies deviation by the recovered configuration
factor, clamps the result between the minimum and maximum thresholds, then
counts samples whose absolute mean distance exceeds that threshold. A second
counter covers the same predicate from index 100 onward. Both counters wrap as
UInt8 before the stock stores them in 32-bit fields.

The former absolute context fields are explicit typed inputs and outputs; the
square-root provider remains an explicit binding. Tests cover ordinary and
tail outliers, maximum/NaN threshold behavior, the exact index-100 boundary,
and scan-capacity rejection.

The complete Goodix reconstruction now has 283 compiled mappings: 264 formerly
opaque candidates, seventeen public-democode replacements, and two product
entries. The remaining Goodix candidate gate is 56 functions / 33,300 bytes;
locally reconstructed candidate bodies cover 32,748 declared stock bytes.

## Exact GH_HR composite identity builder

Entry `0x0006D424` / 180 bytes is reconstructed as
`goodix_primitives_build_hr_version`. It emits the exact composite identity
`GH_HR_exc_pv_v2.0.3.0_CONF_nc_21d2063d_002271a1`, followed by newline-separated
`dsp_pv_v1.3.0_30234f22` and `dlCom_pre2exc_pv_v1.3.0_c00c91c9` identities.
The qualifier, DSP identity, and dlCom identity reuse already admitted local
contracts; all remaining fragments are transparent string literals.

The local API replaces the stock unbounded `strcat` sequence with explicit
capacity checks and clears the destination on truncation. Tests assert the
complete byte-for-byte string and the exact one-byte-short failure boundary.

The complete Goodix reconstruction now has 284 compiled mappings: 265 formerly
opaque candidates, seventeen public-democode replacements, and two product
entries. The remaining Goodix candidate gate is 55 functions / 33,120 bytes;
locally reconstructed candidate bodies cover 32,928 declared stock bytes.

## Three-stage UInt8 tensor workspace pipeline

Entry `0x0006F838` / 190 bytes is reconstructed as
`goodix_primitives_three_stage_u8_pipeline`. It builds three five-word tensor
descriptors from six recovered dimension bytes, executes three record-bound
operators in order, and propagates the caller auxiliary binding. Stages one
and three use the workspace base; stage two uses the exact `+0x3E0` byte bank.
The third descriptor replaces the caller state descriptor after execution.

The three hidden record callbacks and two pointer/word pairs become explicit
typed bindings. Workspace size is validated for both base-backed stages and
the middle bank. Tests capture all three callback inputs/outputs, descriptor
shapes, data addresses, auxiliary values, execution order, final replacement,
and insufficient-workspace rejection.

The complete Goodix reconstruction now has 285 compiled mappings: 266 formerly
opaque candidates, seventeen public-democode replacements, and two product
entries. The remaining Goodix candidate gate is 54 functions / 32,930 bytes;
locally reconstructed candidate bodies cover 33,118 declared stock bytes.

## 256-sample FFT magnitude closure

Three entries / 906 bytes reconstruct the complete transform called by the
NADT spectrum-preparation path:

| Stock entry / size | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x000768B8` / 396 | `goodix_primitives_fft_complex_128_dif` | execute the fixed 128-point complex radix-2 decimation-in-frequency transform over 256 interleaved Float32 words, leaving pairs in bit-reversed order |
| `0x00075E1C` / 318 | `goodix_primitives_fft_real_magnitude_256` | zero-pad the input, execute the complex core and seven-bit pair permutation, recombine the real spectrum, emit bins 0..128, and intentionally replace the DC magnitude with zero |
| `0x000765E4` / 192 | `goodix_primitives_fft_magnitude_prepare` | select Float32 or packed-5/10 input, execute the magnitude transform in caller scratch, optionally apply the binary64 `2/input_count` normalization, and copy a bounded output prefix |

The stock pointer at `0x00075F5C` resolves to a 65-value quarter-wave table.
Local C expresses it transparently as the exact binary32 rounding of
`cos(pi * index / 128)` for indices 0..64; there is no retained firmware blob
or absolute table address. The square-root operation is an explicit typed
binding. Caller-owned scratch replaces the stock allocate/reallocate/free
handoff. The local recombination starts at bin one because the stock bin-zero
partner read and padding write are discarded before the explicit DC/Nyquist
stores; this preserves all observable bins while removing that out-of-range
intermediate access.

Tests pin the DIF transform of a constant complex sequence, the full impulse
spectrum, the Nyquist-only alternating sequence, both Float32 and packed-5/10
input paths, exact normalized amplitude, DC suppression, and every capacity
and binding rejection. The complete Goodix reconstruction now has 288
compiled mappings: 269 formerly opaque candidates, seventeen public-democode
replacements, and two product entries. The remaining Goodix candidate gate is
51 functions / 32,024 bytes; locally reconstructed candidate bodies cover
34,024 declared stock bytes.

## Capped NADT inference-input normalization

Entry `0x00095750` / 198 bytes is reconstructed as
`goodix_primitives_nadt_clip_normalize`. It finds the maximum absolute input,
caps the divisor at the exact Float32 word `0x3CA3D70A` (approximately 0.02),
and emits zeros when the selected divisor's signed Float32 bits are below
`0x33D6BF95` (approximately 1e-7). Otherwise each input is clamped to the
symmetric divisor and divided into `[-1, 1]`.

The implementation preserves the stock raw-bit threshold comparisons and VFP
unordered-compare result: a NaN is ignored during maximum selection and clamps
to `+1` when another sample establishes a usable divisor. Tests cover the
capped and uncapped paths, exact normalized values, sub-threshold zeroing,
isolated and mixed NaNs, and output-capacity rejection.

The complete Goodix reconstruction now has 289 compiled mappings: 270 formerly
opaque candidates, seventeen public-democode replacements, and two product
entries. The remaining Goodix candidate gate is 50 functions / 31,826 bytes;
locally reconstructed candidate bodies cover 34,222 declared stock bytes.

## SpO2 running mean and periodic scale

Entry `0x00028CF4` / 200 bytes is reconstructed as
`goodix_primitives_spo2_smoothed_scale`. It accumulates samples in binary64
through sample 60, divides once by 60 at that boundary, and thereafter applies
the exact update `(59 * accumulator + sample) / 60`. After warm-up, positive
means emit `trunc((rate / 10000.0f) * mean)` only when the sample count is an
exact multiple of 25; every other call returns zero.

The hidden per-channel accumulator and global rate become explicit typed
arguments. Tests pin the sum-to-mean transition, first smoothed update,
25-sample gate, Float32 rate scaling and truncation, nonpositive suppression,
and missing-state rejection. The complete Goodix reconstruction now has 290
compiled mappings: 271 formerly opaque candidates, seventeen public-democode
replacements, and two product entries. The remaining Goodix candidate gate is
49 functions / 31,626 bytes; locally reconstructed candidate bodies cover
34,422 declared stock bytes.

## GH_NADT default and context initialization closure

The paired entries `0x00032788` / 88 bytes and compiler-scattered
`0x0006E664` / 712 bytes are reconstructed as
`goodix_primitives_nadt_default_initialize` and
`goodix_primitives_nadt_context_initialize`. The wrapper clears the public
result status, builds the already recovered NADT identity and exact
`pv_v1.0.0` process version, expresses the stock 60-byte default record as a
typed C initializer, overrides its sample rate, and invokes the context
initializer. No stock configuration blob or absolute data address is retained.

The context initializer validates that exact 60-byte configuration/version
contract, allocates the recovered 52-byte private record, initializes the
observable 92-byte state, clears the 400-, 400-, 600-, and 68-byte work banks
plus sixteen counters, binds the existing dual-buffer descriptor with count
three, and derives every recovered field of the 118-byte runtime configuration.
The supported sample rates are 25, 50, 100, and 200; invalid rates fall back to
25 and invalid modes fall back to one while returning status three. Exact
Float32 constants are preserved for 0.01, 0.02, and the descriptor's
`0x457A1000` word.

Hidden global work banks and table addresses are explicit caller-owned typed
bindings. The host-safe implementation validates all capacities, rejects an
allocation failure instead of continuing through a null private record, and
deterministically clears reserved bytes that stock leaves unobserved. Tests pin
the complete default state and runtime byte images, every cleared bank and
descriptor field, invalid-rate and invalid-mode fallbacks, exact-version and
workspace rejection, allocation exhaustion, and the wrapper's result-status
contract.

The complete Goodix reconstruction now has 292 compiled mappings: 273 formerly
opaque candidates, seventeen public-democode replacements, and two product
entries. The remaining Goodix candidate gate is 47 functions / 30,826 bytes;
locally reconstructed candidate bodies cover 35,222 declared stock bytes.

## GH_NADT selective state reset

Entry `0x0006E574` / 210 bytes is reconstructed as
`goodix_primitives_nadt_context_reset`. It clears the exact mutable state fields
written by stock while deliberately preserving the unmodified reserved bytes,
word `+0x30`, and limit word `+0x34`. It resets the threshold byte to `0x32`,
clears the same 400-, 400-, 200+400-, and 68-byte work-bank extents and sixteen
counters, rebinds the three-element dual-buffer descriptor, releases the
52-byte private record created by the initializer, restores marker `0xBF`, and
returns zero.

The stock globals and Goodix allocator call are explicit workspace and release
bindings. The local reset validates all bank and descriptor capacities before
mutation and nulls the released pointer to prevent a repeated-reset double
release; stock leaves that now-invalid pointer unobserved. Tests begin from a
fully nonzero byte image to prove the precise cleared-versus-preserved state,
pin every work-bank and descriptor result, verify one-shot release behavior,
and cover null/capacity rejection.

The complete Goodix reconstruction now has 293 compiled mappings: 274 formerly
opaque candidates, seventeen public-democode replacements, and two product
entries. The remaining Goodix candidate gate is 46 functions / 30,616 bytes;
locally reconstructed candidate bodies cover 35,432 declared stock bytes.

## NADT peak dispersion and phase quality

Entry `0x00037A84` / 220 bytes is reconstructed as
`goodix_primitives_nadt_peak_dispersion_quality`. It appends a terminal value
of one and phase index `period - 1`, then visits the resulting `count + 1`
records. Positive values contribute their difference from
`(phase_index + 1) / period`; nonpositive and unordered values are skipped.
The first output is the square root of the mean squared difference. The second
is `100 - 200 * mean_absolute_difference`, with the mean absolute difference
capped at 0.5 by the stock raw-Float32 comparison.

The toolchain `sqrtf` call is an explicit unary provider and the two writable
arrays carry capacities. The local boundary additionally rejects a zero period
and a count whose stock 32-bit `count + 1` would wrap. Tests pin a perfect phase
sequence, a known nonzero RMS/quality result, quality saturation, NaN and
nonpositive exclusion, terminal-record mutation, and rejection without partial
mutation.

The complete Goodix reconstruction now has 294 compiled mappings: 275 formerly
opaque candidates, seventeen public-democode replacements, and two product
entries. The remaining Goodix candidate gate is 45 functions / 30,396 bytes;
locally reconstructed candidate bodies cover 35,652 declared stock bytes.

## NADT Gaussian interval integration

Entry `0x0003E6C8` / 216 bytes is reconstructed as
`goodix_primitives_nadt_gaussian_interval_probability`. Its five VFP arguments
are lower bound, upper bound, mean, standard deviation, and step. Beginning at
`lower + step`, it samples right endpoints through the inclusive upper bound,
evaluates the normal density with exact Float32 `2*pi` word `0x40C90FDB`, and
adds `density * step`. The exponent enters the toolchain binary64 `exp`, and
the normalization, exponential result, step, and running addition use the
same binary64 intermediate conversions before each Float32 accumulator store.

Both `sqrtf` and `exp` are explicit typed providers. A zero deviation preserves
the stock zero result; a nonpositive or non-advancing step is rejected to avoid
the stock zero-step infinite loop. Tests capture all four exact exponent
arguments for a known interval, pin the normalization result and endpoint
count, and cover empty intervals, zero deviation, and rejected zero step.

The complete Goodix reconstruction now has 295 compiled mappings: 276 formerly
opaque candidates, seventeen public-democode replacements, and two product
entries. The remaining Goodix candidate gate is 44 functions / 30,180 bytes;
locally reconstructed candidate bodies cover 35,868 declared stock bytes.

## GH_HR median-absolute-deviation inlier mask

Entry `0x0003DE20` / 234 bytes is reconstructed as
`goodix_primitives_hr_mad_inlier_mask`. It obtains the recovered descending-
selection median, writes each absolute deviation into transient storage,
computes their Float32 mean, and emits one byte per sample for the predicate
`absolute_deviation <= mean_deviation * 1.4826 * multiplier`. The scale word is
the exact stock binary64 value `0x3FF7B8BAC710CB29`; multiplication and the
final comparison remain binary64 as in the Arm EABI sequence.

Caller-owned scratch replaces the stock Goodix allocate/free pair, and the
local boundary rejects counts above the stock wrapping UInt8 loop range.
Tests pin the median, complete deviation scratch image, ordinary inlier/outlier
mask, zero-deviation and negative-zero comparison behavior, negative scaling,
and capacity rejection without output mutation.

The complete Goodix reconstruction now has 296 compiled mappings: 277 formerly
opaque candidates, seventeen public-democode replacements, and two product
entries. The remaining Goodix candidate gate is 43 functions / 29,946 bytes;
locally reconstructed candidate bodies cover 36,102 declared stock bytes.

## NADT reflected-boundary signed-int FIR kernel

Entry `0x00066B30` / 222 bytes is reconstructed as
`goodix_primitives_nadt_symmetric_fir_i32`. For an odd kernel of length
`2*half + 1`, it builds the exact stock mirror padding: input indices
`half..1`, the complete input, then indices `count-2` downward. Each output is
the ordered Float32 multiply-accumulate of one padded window and the kernel,
followed by the stock signed truncating conversion.

Caller-owned signed-int scratch replaces the transient Goodix allocation. The
local boundary validates odd kernel length, mirror geometry, scratch/output
capacities, overflow, and nonrepresentable Float32-to-Int32 results. Tests pin
the complete padded image, a three-tap smoothing result, identity filtering,
fractional truncation, and every geometry/capacity rejection.

The complete Goodix reconstruction now has 297 compiled mappings: 278 formerly
opaque candidates, seventeen public-democode replacements, and two product
entries. The remaining Goodix candidate gate is 42 functions / 29,724 bytes;
locally reconstructed candidate bodies cover 36,324 declared stock bytes.

## SpO2/dlCom scattered biquad cascade

The two executable segments `0x0006671C..<0x000667BA` and
`0x0009285E..<0x000928CA` / 266 bytes are reconstructed as
`goodix_primitives_spo2_biquad_cascade_process`. The typed state exposes the
stage count, two Float32 delay words per stage, five Float32 coefficients per
stage, and previous input. Each stage computes
`filtered = state0 + c0*input`, then updates
`state0 = state1 + c1*input + c3*filtered` and
`state1 = c2*input + c4*filtered`; its output feeds the next stage.

When requested, the recovered prepass compares the input delta against a
signed limit or accepts the explicit force mode, adjusts the first stage by
`(c1+c2)*delta` and `c2*delta`, and stores the new previous input. The unusual
raw-bit `64000.0f`/zero branch for an exact-zero delta is preserved. Tests pin
a general coefficient/state update, two-stage chaining, forced correction,
limited small-delta behavior, previous-input preservation, and stage-capacity
rejection.

The complete Goodix reconstruction now has 298 compiled mappings: 279 formerly
opaque candidates, seventeen public-democode replacements, and two product
entries. The remaining Goodix candidate gate is 41 functions / 29,458 bytes;
locally reconstructed candidate bodies cover 36,590 declared stock bytes.

## Complete seven-bank SpO2 packed workspace expansion

Entry `0x00037F54` / 206 bytes is reconstructed as
`goodix_primitives_spo2_expand_packed_banks`. The stock `ceil(60.0)` and
multiplication by three resolve to exactly 180 values per bank. Four pointers
from the strided `+0x94..+0xAC` records and the three pointers at `+0xB4`,
`+0xBC`, and `+0xC4` become an explicit seven-pointer binding. Each complete
bank is converted in order into one contiguous 180-value slice of the
1,260-value output workspace using the already reconstructed exact packed-6/9
to Float32 bit conversion.

All seven bindings and the complete destination capacity are validated before
the first write. Tests generate distinct data for every bank and compare all
1,260 output bit patterns against the conversion primitive, then verify null-
bank and short-workspace rejection without partial mutation.

The complete Goodix reconstruction now has 299 compiled mappings: 280 formerly
opaque candidates, seventeen public-democode replacements, and two product
entries. The remaining Goodix candidate gate is 40 functions / 29,252 bytes;
locally reconstructed candidate bodies cover 36,796 declared stock bytes.

## SpO2 scaled decimal residual extraction

Entry `0x000372B0` / 214 bytes is reconstructed as
`goodix_primitives_spo2_decimal_residual`. Values whose absolute raw Float32
word is below `0x358637BD` (approximately `1e-6`) leave the destination
untouched. Otherwise the helper takes `log10f(abs(value))`, truncates the
positive result to select `10^(exponent+1)`, scales the signed input, obtains
four- and eight-decimal truncations, and multiplies their absolute difference
by `10,000`. The parity of a second `10,000` scaling selects the residual sign.

The toolchain `log10f` call is an explicit typed provider; the already admitted
unsigned-power and decimal-truncation primitives close the remaining calls.
Tests reproduce the complete formula from the two truncation results, capture
the absolute logarithm argument, cover negative input, pin the unchanged
sub-threshold contract, and reject a missing provider.

The complete Goodix reconstruction now has 300 compiled mappings: 281 formerly
opaque candidates, seventeen public-democode replacements, and two product
entries. The remaining Goodix candidate gate is 39 functions / 29,038 bytes;
locally reconstructed candidate bodies cover 37,010 declared stock bytes.

## SpO2 rolling percentile selector

Entry `0x00041F4C` / 210 bytes is reconstructed as
`goodix_primitives_spo2_rolling_percentile_select`. It takes the newest source
sample, removes the prior anchor from the first `source_count` sorted values
when present, inserts the candidate in ascending order, advances the anchor to
the oldest source sample, and evaluates the 25th, 50th, and 75th percentiles.
The interquartile spread is raised to five when its signed raw Float32 word is
smaller, then the candidate is retained only when its absolute distance from
the median is within `spread * tolerance_scale`; otherwise the median wins.

All hidden window records become explicit arrays, counts, capacities, and an
anchor pointer. Tests pin removal and insertion, the complete resulting sorted
image, candidate and median branches, absent-anchor growth, and rejection when
that growth would exceed capacity.

The complete Goodix reconstruction now has 301 compiled mappings: 282 formerly
opaque candidates, seventeen public-democode replacements, and two product
entries. The remaining Goodix candidate gate is 38 functions / 28,828 bytes;
locally reconstructed candidate bodies cover 37,220 declared stock bytes.

## NADT two-stage optical sample transform

Entry `0x000373A4` / 216 bytes is reconstructed as
`goodix_primitives_nadt_optical_sample_transform`. Its formerly private
context is now an explicit binding for two consecutive three-coefficient
numerator banks, two matching denominator banks, two pairs of input history,
two pairs of output history, and the Float32 correction threshold. Each stage
calls the admitted second-order difference equation, shifts its own histories,
and forwards its Float32 result to the next stage; the final value is converted
to binary64, passed through the explicit standard `round` provider, and
converted back to Float32.

Before filtering, the first input-history pair is translated by the new-sample
delta when the truncated signed magnitude reaches the configured threshold.
The reconstruction preserves the target-width `VCVT`/`RSBS` behavior,
including wrapped `INT32_MIN`, as well as the exact-zero branch's signed raw
Float32 comparison against `0x467A0000` (`16000.0f`) and zero test. Tests pin
both-stage input/output history movement, final rounding, correction at the
threshold, suppression below it, and complete binding/provider validation.

The complete Goodix reconstruction now has 302 compiled mappings: 283 formerly
opaque candidates, seventeen public-democode replacements, and two product
entries. The remaining Goodix candidate gate is 37 functions / 28,612 bytes;
locally reconstructed candidate bodies cover 37,436 declared stock bytes.

## SpO2 transient-history dispatch and logistic scoring

Entry `0x000367C4` / 230 bytes is reconstructed as
`goodix_primitives_spo2_dispatch_logistic_score`. It snapshots a four-word
recent-input history into caller scratch, shifts three words, inserts the new
Float32 word, and exposes that transient view to the explicitly selected
indexed operation. The exact stock binary64 floors resolve a second operation:
copy all 99 Float32 values from the first workspace bank into the adjacent
99-value bank. The history is restored after dispatch, including on a provider
status result, while the workspace copy remains visible.

The operation's Float32 result is mapped to `100 / (1 + expf(-value))` through
an explicit `expf` provider. The unusual signed raw-word comparison caps the
exponent at the exact `88.0f` word, and a nonzero provider status overwrites
the score with zero and returns the recovered true status. Typed workspace,
history, dispatch-record, and `+0x64`/`+0x68` bindings replace all private RAM
addresses; four caller-owned words replace the stock transient allocation.
Tests pin the callback-visible history, restoration, all 99 copied values,
ordinary scoring, the raw cap, status zeroing, and capacity rejection.

The complete Goodix reconstruction now has 303 compiled mappings: 284 formerly
opaque candidates, seventeen public-democode replacements, and two product
entries. The remaining Goodix candidate gate is 36 functions / 28,382 bytes;
locally reconstructed candidate bodies cover 37,666 declared stock bytes.

## GH_HR five-history weighted-feature pipeline

Entry `0x00030368` / 286 bytes is reconstructed as
`goodix_primitives_hr_weighted_feature_update`. At input rates divisible by
25, each sample enters the periodic Float32-word history directly; other rates
enter the raw history and call the locally reconstructed
`0x00037588` interpolation stage. When the periodic history's wrapping push
count reaches a capacity boundary, its Float32 mean enters a third history.
Once that mean history is full, the routine computes its mean, reads index
`(midpoint_window - 1) / 2` with the stock zero fallback, and appends the
selected value minus the mean to a fourth history.

The final pass traverses the centered history newest-first and the selected
mode coefficient bank forward, preserving the recovered Float32 accumulation
order, then appends the result to the fifth history. Modes zero through three
are caller-bound coefficient spans replacing the private tables at
`0x000B0F8C`, `0x000B1090`, `0x000B1194`, and `0x000B1298`; an out-of-range
mode preserves the stock zero accumulation. Tests pin a complete four-cycle
pipeline with periodic means 5 and 9, mean-of-means 7, centered value 2, and
weighted value 6, plus both interpolation outcomes, raw-bit history storage,
and coefficient-capacity rejection.

The complete Goodix reconstruction now has 304 compiled mappings: 285 formerly
opaque candidates, seventeen public-democode replacements, and two product
entries. The remaining Goodix candidate gate is 35 functions / 28,096 bytes;
locally reconstructed candidate bodies cover 37,952 declared stock bytes.

## One-lane NADT generated-model inference bridge

Entry `0x000968C4` / 290 bytes is reconstructed as
`goodix_primitives_nadt_inference_bridge`. The four recovered dimension bytes
select tail windows from explicit primary and secondary Float32 descriptors.
The primary tail is copied verbatim; the secondary tail passes through the
admitted exact clip/normalize helper into the complete 2,244-byte generated-
model workspace. Caller-owned buffers replace both stock transient allocations.

Two pointer bundles reproduce the graph ABI: primary scratch, normalized
workspace, scalar output, and zero for the input bundle; output and zero for
the result bundle. The generated executor, its three context words, and the
per-lane selector are all typed caller bindings. A nonzero executor result or
short descriptor returns stock status 5. On success the scalar follows the
recovered negative-to-zero and signed-raw-word above-two clamp. Tests pin both
tail windows, normalized values `0.5, 1, 1`, all seven graph arguments, both
pointer bundles, both clamp boundaries, executor failure, and short scratch.

The complete Goodix reconstruction now has 305 compiled mappings: 286 formerly
opaque candidates, seventeen public-democode replacements, and two product
entries. The remaining Goodix candidate gate is 34 functions / 27,806 bytes;
locally reconstructed candidate bodies cover 38,242 declared stock bytes.

## NADT 23-sample boundary/interior window filter

Entry `0x00030B6C` / 300 bytes is reconstructed as
`goodix_primitives_nadt_window_filter_i32`. Flag bit one enables eleven left
boundary outputs, each applying one row of the recovered 11x23 Float32 matrix
to input samples 22 down to zero. The middle `count-22` outputs use the exact
`0x3D321643` (`1/23`) uniform kernel through the admitted reflected-boundary
signed-int FIR. Flag bit zero enables eleven right boundary outputs using rows
ten down to zero, coefficients 22 down to zero, and the final 23 input samples.

The complete boundary matrix is an explicit typed span replacing the private
`0x000B154C` address. Caller-owned filtered-output and reflected-input scratch
replace both allocation layers, while every accumulation and Float32-to-Int32
conversion retains the recovered order. Tests use a diagonal boundary matrix
to pin every left/right row and reversed-column mapping, compare every interior
destination with the FIR result retained in scratch, verify disabled boundaries
remain untouched, and reject a window shorter than 23 samples.

The complete Goodix reconstruction now has 306 compiled mappings: 287 formerly
opaque candidates, seventeen public-democode replacements, and two product
entries. The remaining Goodix candidate gate is 33 functions / 27,506 bytes;
locally reconstructed candidate bodies cover 38,542 declared stock bytes.

## NADT periodic-peak rate estimator

Entry `0x00042BD0` / 316 bytes is reconstructed as
`goodix_primitives_nadt_periodic_peak_rate`. It first computes the complete
Float32 amplitude mean and selects positions whose amplitude's signed raw word
is at least `0x3DCCCCCD` (`0.1f`). If seven or more positions survive, the
stock second gate compacts those saved positions according to the first
selected-count amplitudes and the mean truncated to signed Int32 then converted
back to Float32. This unusual source/index pairing is preserved exactly.

Three through thirteen retained positions are accepted. Consecutive position
differences are written to caller scratch; any adjacent interval change above
three, or a nonpositive first-to-last span, produces zero. Otherwise the rate
is `(count-1)*1500/span`, promoted to binary64, increased by exact `0.5`,
truncated to signed Int32, and clamped to 40..200. Both stock allocations are
replaced by bounded caller arrays. Tests pin rate 150, both clamps, all scratch
contents, the four-unit instability rejection, insufficient-count zeroing,
and capacity rejection.

### SpO2 spectral concentration (`0x0002FF10`)

`goodix_primitives_spo2_spectral_peak_concentration_db` scans strict positive
interior maxima over indices `1..count-3` while accumulating that same
interior's Float32 energy. It selects the strongest peak, sums an inclusive
`peak +/- radius` energy window, and for peak bins 31 through 56 also sums the
matching `2*peak +/- radius` harmonic window. The expected energy is the
interior mean times the exact odd window width, doubled when the harmonic band
is active.

The recovered raw-word gates require expected energy above exact
`0x322BCC77` (approximately `1e-8`), concentration at least exact
`0x3DCCCCCD` (`0.1f`), and a nonzero peak. Accepted output is
`10 * log10(local_energy / expected_energy)` through an explicit math
provider; peak index is always emitted as Float32. The bounded API rejects
counts and radii that would trigger stock's uint8 index wrap. Tests pin the
31..56 harmonic path, exact provider argument, score and peak outputs,
zero-spectrum rejection, and unsafe-count rejection.

### SpO2 report acceptance and event latch (`0x00029AD8`)

The analyzer it invokes is now independently reconstructed too. The compiler-scattered 1,102-byte
body at `0x00034500` compiles as `goodix_primitives_spo2_report_analyze`; its concatenated
executable-segment SHA-256 is
`bc76647d6dc27ce40c9742402fc03ed2a819c12381e489ab7057d04d78fc0350`.
The exact 36-byte analysis record exposes four spectral candidates, concentration, candidate
population deviation, concentration sample deviation, metric mean, and the ten recovered gates.
Four bounded rolling-window descriptors replace the private state offsets while preserving
candidate/reference history, decimated concentration/metric history, and three stability streaks.

The local analyzer retains the three 78-bin peak scans, exact `1.953125` bin-to-candidate scale,
128-bin concentration calculation with radius two, two harmonic searches below candidate 50,
raw Float32 threshold comparisons at 4/5/7/100, wrapping unsigned difference bands, all-history
counter loops, prior-candidate stability, and secondary consistency rules. Tests run three complete
frames to fill the histories and pin all candidate conversions, statistics, counters, flags,
streaks, and pre-mutation extent rejection.

The discontiguous 340-byte stock body is admitted as
`goodix_primitives_spo2_report_state_update`. It clears the 36-byte analysis
record and invokes the now-local `0x00034500` analyzer through its typed provider seam,
and conditionally performs the exact 512-byte channel-4-to-channel-0 spectrum
copy when both source-history flags are set. That condition also selects the secondary
rather than primary candidate byte.

When no result was already accepted, the wrapper combines the recovered
three quality-byte gate, raw Float32 score-below-5 check, and wrapping signed
distance below six. Acceptance clamps the selected value upward to the state
minimum, writes its low byte, latches acceptance, and clears the transient
event. The fallback state machine preserves phases `0 -> 1 -> 2 -> 0`, the
score-below-2 activation gate, hold conditions, event output, and sticky
event-seen byte. Tests cover both candidate sources, distinct source/destination
copy spans, minimum clamp, acceptance, activation/hold/release/reset sequence, and typed
analyzer invocation and the independently tested local analyzer body.

### SpO2 packed-channel deviations (`0x00034B54`)

`goodix_primitives_spo2_packed_channel_standard_deviations` replaces the
stock `ceil(60.0) * sizeof(float)` allocation with a checked caller-owned
60-float workspace. Four packed sign/6-bit-exponent/9-bit-fraction channels
are decoded through the already admitted converter. The first three select
indices `0,3,6,...`; the fourth selects every value. Each selected vector is
passed to the admitted zero-safe population-standard-deviation routine with
an explicit square-root provider.

The typed span contract admits up to 180 source words for each stride-three
channel and 60 for the full-rate channel, exactly matching the stock scratch
capacity without permitting its unchecked overflow. Tests pin stride
selection, nonzero and zero deviations, full-rate behavior, packed conversion,
and insufficient-scratch rejection.

The complete Goodix reconstruction now has 311 compiled mappings: 292 formerly
opaque candidates, seventeen public-democode replacements, and two product
entries. The remaining Goodix candidate gate is 28 functions / 25,830 bytes;
locally reconstructed candidate bodies cover 40,218 declared stock bytes.

## Packed three-group channel record assembly (`0x00061DA4`)

The SHA-pinned 334-byte body is admitted as
`goodix_primitives_spo2_channel_records_assemble`. The stock prologue enables a
`3 * channel_count` integrity scan: every nonzero presence byte selects the
parallel encoded word for the recovered transform/difference check, and a
difference replaces that word with exact `0x00800000`. The otherwise-unused
difference counter is intentionally kept uint8 and discarded.

The assembly then reads three consecutive channel masks in MSB-first order.
Groups zero and one write the current record's first and second two-float
slots. A present group-two bit optionally writes the third slot and always
advances both the wrapped uint8 record index and the output header's existing
uint8 count. Provider calls stop at the caller's expected count, while the
index continues so the final mismatch result remains stock-equivalent.
Sequence subtraction wraps at signed-32 limits, and the three source metadata
words are copied into the output header.

The 522-byte scaling routine at `0x000335B4` was initially retained as a typed
`goodix_primitives_spo2_channel_decode_fn` boundary. Its exact calls at
`0x00061E42`, `0x00061E86`, and `0x00061ECA` receive only the source binding,
channel byte, group halfword, and destination float pair. The later reduction
below reconstructs that body with explicit table and toolchain-math bindings.
Tests pin mask order,
five-call destination layout, integrity replacement, metadata, capacity
truncation, mismatch, count preservation/increment, signed wrap, and bounds.

## GH_HR 25-phase periodic resampler (`0x00037588`)

`goodix_primitives_hr_interpolate_periodic_sample` completes the previously
typed interpolation boundary inside the five-history HR feature pipeline. For
a positive input rate it reproduces the stock binary64 ceiling of
`rate / trunc(rate / 25)` and its binary64-to-Float32 division by exact 25.0.
Whenever the raw history's wrapping push count reaches a capacity boundary,
the helper averages that history, advances the recovered phase counter, and
searches phases one through 25 for the unique boundary in `(phase-1, phase]`.
The emitted periodic value preserves the recovered operation order:
`previous * (1-fraction)`, then `current * fraction`.

At an exact input-rate boundary the latest raw sample is emitted directly,
the raw push count resets to zero, and the phase cursor remains unchanged.
The stock absolute banks at `0x20007C6C` and `0x200377CC` are replaced by the
caller's `interpolation_count`, `interpolation_phase`, and
`previous_interpolation_sample` fields. Tests pin a no-match phase, the
`128 Hz -> 25` fractional emission, direct boundary emission, previous-sample
updates, counter reset, and rejection of rates below 25. The enclosing
`goodix_primitives_hr_weighted_feature_update` now calls this local routine
directly and has no opaque interpolation callback.

The complete Goodix reconstruction now has 312 compiled mappings: 293 formerly
opaque candidates, seventeen public-democode replacements, and two product
entries. The remaining Goodix candidate gate is 27 functions / 25,458 bytes;
locally reconstructed candidate bodies cover 40,590 declared stock bytes.

## GH_HR secondary-context constructor (`0x00072C48`)

`goodix_primitives_hr_secondary_context_initialize` reconstructs the complete
logical 0x158-byte subcontext allocated by the still-gated `pv_v1.1.0` primary
initializer. After zeroing the context, it creates nine pair buffers. Each
halves the recovered source count eight into four zeroed eight-byte records and
binds the caller's coefficient record instead of stock address `0x000B0F0C`.
The VFP values approximately one third and exact four passed by the stock
caller are demonstrably unused by the admitted pair-buffer veneer.

The constructor then creates eight zeroed 180-element Int16 buffers, one
60-element Int16 buffer, and seven zeroed 20-element Float32 histories with
flag one. The capacity 180 is recovered exactly as
`3 * (int16_t)ceil(60.0)`. The transparent form checks every allocation and
unwinds all earlier allocations on failure; a paired release routine clears
the caller-owned context. Tests pin all 25 allocations, capacities, flags,
zero initialization, coefficient bindings, complete release, and partial
failure cleanup.

The complete Goodix reconstruction now has 313 compiled mappings: 294 formerly
opaque candidates, seventeen public-democode replacements, and two product
entries. The remaining Goodix candidate gate is 26 functions / 25,086 bytes;
locally reconstructed candidate bodies cover 40,962 declared stock bytes.

## NADT three-lane sample preparation (`0x00036034`)

`goodix_primitives_nadt_sample_prepare` replaces the stock globals at
`0x20007CB8` / `+0x30` and `+0x34` with caller-owned previous-sequence and
previous-scale-code fields. The output change flag becomes one only when a
nonzero prior sequence changes or a prior scale code other than `0xFF`
changes; both remembered values update on every call.

The direct path selects input indices zero, `lane_stride`, and
`2 * lane_stride`, applying the recovered arithmetic right shift by seven
only to lane zero. Calibrated mode three validates three scale codes against
the exact recovered table `{10,25,50,100,250,500,1000}` and preserves the
stock Float32 order: calibration divided by 1,000,000, multiplied by the
selected scale and 8,388,608, divided by 900, then increased by 8,388,608 and
truncated to signed Int32. Invalid modes or codes fill all outputs with exact
9,000,000 and report failure.

Tests pin first-call sentinels, sequence/scale changes, negative arithmetic
shift, all three lane indices, calibrated numeric outputs, invalid-code
fallback, and unsupported-mode fallback. No absolute state or private table
address remains.

The complete Goodix reconstruction now has 314 compiled mappings: 295 formerly
opaque candidates, seventeen public-democode replacements, and two product
entries. The remaining Goodix candidate gate is 25 functions / 24,692 bytes;
locally reconstructed candidate bodies cover 41,356 declared stock bytes.

## GH_HR four-candidate position-band selector (`0x00086BAC`)

`goodix_primitives_hr_candidate_window_select` scans typed candidate records
newest-first for positions in `[origin-3*step, origin-2*step)`. Unsuppressed
matches fill four slots from the end toward the front. Record zero and records
whose primary tag is one use their explicit alternate tag. After warmup, the
upper and lower value bounds are respectively the maxima of the raw bounds and
`3*scale` / `0.5*scale`; a clamp replaces the tag with eight.

The first position below the band ends the scan. If no match was retained and
that position is also below `origin-4*step`, its value is retained with tag
seven. A final stable compaction keeps only strictly positive values, clears
the remaining slots and tags, and records the retained count. The stock global
call counter and geometry fields are now explicit caller state; the stock
overlapping 32-byte record reads are represented as non-overlapping typed
position, value, primary/alternate-tag, and suppression fields.

Tests pin newest-to-oldest ordering, all four tag paths, upper/lower clamps,
wrapping call-count increment, older fallback, suppression, positive-only
compaction, and zero-filled tails.

## GH_HR primary/private-context constructor

| Stock entry | Bytes | Local mapping | Recovered contract |
| --- | ---: | --- | --- |
| `0x0006D204` | 406 | `goodix_primitives_hr_primary_context_create` | validate the exact 36-byte configuration and `pv_v1.1.0` ABI; construct the primary and secondary logical contexts; bind graph selectors 0, 1, and 6; allocate four three-element histories; seed exact tail literals |

The stock function stored its 0x150-byte primary owner at `0x20007C68` and
its 0x158-byte secondary owner in the record at `0x200377A4`. The local
`goodix_primitives_hr_context_owner` replaces both globals. It also replaces
the copied seven-entry constructor table rooted at `0x000BCF40` with three
typed graph bindings. The recovered records are preserved exactly: selector
zero receives `table_a692c`, `0x12F9 << 2`, and `table_a04cc`; selector one
receives `table_9d640`; selector six receives `table_a50b0`.

Configuration mode defaults are 20, 15, and 30 for selectors zero, one, and
two. Explicit primary/secondary window overrides, UInt16 sample-rate
truncation before division by 25, minimum-batch clamp followed by UInt8
truncation, feature-stride/default-202 fallback, and candidate-limit cap at 20
all follow the recovered Thumb-2 order. The six graph control bytes are
`{1,5,0x80,1,4,1}`, followed by `0x164`, 2, and 1. Four initial Float32
accumulators use exact bits `0x48800000` (`262144.0f`), and the four Float64
baselines are zero.

Construction owns 31 allocations: the two context objects, all 25 secondary
allocations, and four three-element histories. The paired teardown releases
all of them and invokes optional graph destructors in reverse selector order.
Tests pin validation before allocation, all defaults and table arguments,
31-allocation success/release, exact control and tail values, and last-step
allocation failure with complete unwind.

## GH_NADT spectral peak-preparation pipeline

| Stock entry | Bytes | Local mapping | Recovered contract |
| --- | ---: | --- | --- |
| `0x000766AC` | 478 | `goodix_primitives_nadt_spectral_peak_prepare` | accumulate one 125-value channel, mask quartile outlier sign-runs, apply the private scale binding, generate a 53-bin FFT magnitude prefix, select five bounded peaks, and dispatch the three-output harmonic selector |

The stock input walked through a 0x104-byte channel record and then applied a
signed `-500` byte offset plus a UInt16 spectral offset. The reconstruction
accepts the already resolved 125-value span. Its private 125-value scale vector
and factor are explicit inputs, while the nine transient heap allocations are
replaced by `goodix_primitives_nadt_spectral_workspace`.

The recovered fixed geometry is explicit: outlier multiplier byte divided by
10, 125 inputs, `ceilf(52.2f) = 53` output bins, peak search from
`floorf(5.12f) = 5` through bin 52, factor-derived radius
`floorf(float((factor * 0.8 * 256) / 125))`, threshold 0.1, five retained
peaks, bin width 0.09765625, and three downstream outputs. The still-separate
`0x00035850` harmonic selector is a typed callback, so this body contains no
hidden code pointer or copied algorithm bytes.

Tests pin the outlier-run zeroing, zero-spectrum FFT path, 53-bin geometry,
begin bin five, radius three for factor two, stable five-peak indices
`{5,9,13,17,49}`, exact bin width, three callback outputs, provider failure,
and span validation.

## SpO2 five-channel normalized spectrum preparation

| Stock entry | Bytes | Local mapping | Recovered contract |
| --- | ---: | --- | --- |
| `0x000708F8` | 498 | `goodix_primitives_spo2_normalized_spectra_prepare` | transform and normalize four fixed 60-value Float32 channels, decimate and average four packed-6/9 channels into a fifth input, then transform and normalize that fifth channel |

The literal at `0x00070AEC` is exact Float64 `60.0`, so the stock count
conversion resolves to 60 input samples. Each channel is zero-padded to 256
values by the already reconstructed real-input FFT, the first 128 magnitude
bins are copied, and `goodix_primitives_normalize_by_max` applies the exact
stock reciprocal-maximum rule. The four Float32 inputs occupy consecutive
60-value slices of the typed transformed span.

The fifth input reads indices `0,3,...,177` from each of four private packed
channels, converts each value through the exact recovered sign/6-bit-exponent/
9-bit-fraction format, sums in channel order, and multiplies by exact Float32
`0.25f`. The stock `0x200377A4` root and `+0x94`, `+0x9C`, `+0xA4`, and
`+0xAC` pointer walks are explicit bindings. Its 240-byte heap temporary and
the two stock scratch regions are replaced by one caller-owned 257-float
workspace; no allocation or absolute firmware pointer remains.

Tests pin all four contiguous Float32 channel slices, ignored packed indices,
the terminal packed index 177, decimation by three, exact packed conversion
and four-channel average, DC zeroing, per-channel max normalization, identical
first/fifth spectra for identical inputs, and complete extent validation
before output mutation.

## NADT seven-stage generated-graph orchestrator

| Stock entry | Bytes | Local mapping | Recovered contract |
| --- | ---: | --- | --- |
| `0x00037890` | 500 | `goodix_primitives_nadt_generated_graph_execute` | execute two explicitly bound `0x34194` subgraphs and seven typed tensor nodes over the fixed NADT workspace topology, with optional recurrent-state clearing |

The stock 0x344-byte model owner exposed dimensions and raw Thumb callbacks at
`+0x2C4...+0x340`. The reconstruction replaces them with
`goodix_primitives_nadt_generated_graph`: two typed subgraph bindings, seven
typed node bindings, their contexts, five dynamic dimensions, and an explicit
recurrent-state span. Both `0x00034194` bindings can now point to the admitted
typed subgraph below; no model weight data or absolute code pointer is copied
into either source-admitted layer.

The fixed Float32 topology is preserved exactly. The first subgraph emits 120
values at workspace zero. Three nodes alternate through the bank at
`+0x3E0`; their final dynamic-width output is saved at `+0x8B8`. The 125-value
caller input then replaces workspace zero before the second subgraph. A
two-input node combines 120 values with the first three saved values into 123
values at `+0x3E0`. Those 123 values move to workspace zero, then three final
nodes use the `+0x7C0` state bank and `+0x3E0` output bank. The final dynamic
Float32 vector is copied to the bounded caller destination.

All callbacks, dimensions, recurrent storage, input/output spans, and every
derived workspace bank are validated before execution. Tests pin both
subgraph calls, all seven node descriptor shapes, the two-input 120+3 merge,
125-value input replacement, saved-branch values, recurrent reset and
preservation modes, final output copy, callback failure propagation, and
short-workspace/dimension rejection before output mutation.

## NADT generated-model subgraph

| Stock entry | Bytes | Local mapping | Recovered contract |
| --- | ---: | --- | --- |
| `0x00034194` | 630 | `goodix_primitives_nadt_generated_subgraph_execute` | run the fixed 19-operator in-place quantized/Float32 subgraph over a 0x7C0-byte workspace and leave 120 Float32 outputs at its base |

The copied 0x160-byte stock operator owner is now
`goodix_primitives_nadt_generated_subgraph`: nineteen typed operator bindings,
their contexts, and the two Float32 quantization-range words. The first
operator converts the `{1,1,125}` Float32 input in place and exposes its range
descriptor. Stock then overwrites the two range values from the owner, adds
the scalar descriptor containing UInt32 `2000`, and expands to
`{1,16,125}` UInt8 values.

The exact subsequent topology is preserved: reduction to `{16,62}`, a
three-operator `{4,62}->{4,62}->{16,62}` pipeline alternating between byte
offsets zero and `0x3E0`, a two-input skip merge, then the same sequence for
31 columns. A final reduction produces `{16,15}` UInt8 values and an explicit
operator converts them to Float32 at `+0x3E0`. The already-admitted
`0x0002F7DC` topology is reproduced as three explicit Float32 operators with
fixed shapes `{1,15}->{1,15}->{8,15}` and middle bank `+0x1F0`. A branch
operator writes a second `{8,15}` tensor at `+0x1E0`; its descriptor is passed
through the recovered auxiliary slot to the final merge. The 120 Float32
results remain at workspace zero, matching both in-place stock callers.

Every callback and the exact 496-Float32/0x7C0-byte extent is checked before
execution. Tests pin all nineteen calls in order, every element width, shape,
and bank address, scalar/range forwarding, both two-input merges, branch
descriptor handoff, final 120 values, and missing-operator/short-workspace
rejection before the first callback. The exact body SHA-256 is
`18b51a96c3f0c3d0c9c47727c5ec8f5a569e603ad2c882e74fef43f84588e285`.

## NADT channel-quality flags and weighted score

| Stock entry | Bytes | Local mapping | Recovered contract |
| --- | ---: | --- | --- |
| `0x00088E80` | 518 | `goodix_primitives_nadt_channel_quality_update` | update six masked diagnostic flags and a capped quality byte from two reciprocal-metric logistic scores plus one signed-quality logistic score |

The stock configuration fields at logical `+0x30`, `+0x34`, and
`+0x41...+0x43`, the summary bytes/halfword at `+3...+5`, and the first
44-byte output record are explicit typed structures. Flags retain the exact
bit assignments: summary thresholds `0x01/0x02`, positive activity `0x04`,
missing validity `0x08`, metric-limit or exact `-1.0f` sentinel `0x10`, and
signed quality below threshold `0x20`; the configured mask is applied after
all six tests. The recovered unsigned comparison of the sign-extended
secondary summary is preserved.

Both metrics use exact fallback bits `0x358637BD` when their raw Float32 word
is nonpositive. Their reciprocals share threshold `0x41855556` and logistic
scales `0x3F0F5C27` / `0x3BBA9C69`. The signed quality uses threshold 75 and
scales `0x3D98EAD6` / `0x3E656041`. The three already-local logistic results
are accumulated through exact Float64 weights 0.4, 0.4, and 0.2, converted
back to Float32 after each addition, capped at 100, and truncated to UInt8.
The exponential operation remains an explicit source-routed callback.

Tests pin every flag family, final masking, the stock negative-secondary
unsigned comparison, exact `-1.0f` sentinel handling, three provider calls,
and a deliberately asymmetric `{100,50,25}` component sequence yielding the
weighted score 65.

## NADT dual-window peak features and packed correlation

| Stock entry | Bytes | Local mapping | Recovered contract |
| --- | ---: | --- | --- |
| `0x00029144` | 520 | `goodix_primitives_nadt_dual_window_features_extract` | process two final-125 windows through normalized autocorrelation and peak features, retain the exact packed-5/10 primary representation, and report its normalized correlation with the secondary result |

The body reads the final 125 Float32 values from the stock pointer/count pairs
at logical `+0xD8/+0xDC` and `+0xE8/+0xEC`. These are explicit bounded spans.
Each lane runs the already-local centered autocorrelation, normalization,
62-row local-maximum mask, local-peak collection, terminal-phase append,
dispersion/quality calculation, and periodic-rate estimator. A lane with no
peaks writes exact `0.5f` dispersion while leaving its caller-provided rate and
quality unchanged, matching the stock early branch.

Before the secondary lane replaces the shared autocorrelation output, all 125
primary Float32 words are converted through the recovered shared packer with
five exponent bits and ten fraction bits. The correlation loop converts those
packed words back to Float32, accumulates their dot product with the secondary
autocorrelation, divides by the product of the two square roots of sum-of-
squares, and emits zero for either zero norm. The stock six heap allocations
are replaced by one fixed caller-owned workspace covering 125/249-value
correlation banks, the 969-byte peak mask, row/column scratch, 63 peak slots,
rate scratch, and the 125 packed primary values. No absolute state pointer,
hidden callback, allocator, or opaque table remains. The exact body SHA-256 is
`c981e359c84c06bd9782fd5a9230b1f446a78947b354b5d56fc23b4df0851661`.

Tests pin exact packed-5/10 zero, sign, subnormal, normal, maximum, infinity,
and NaN cases; fixed tail slicing with deliberately different ignored prefixes;
the no-peak `0.5f` and output-preservation path; the recovered 62-peak capacity
and appended terminal phase; exact impulse correlation; and complete input/
provider validation before result mutation.

## NADT auxiliary state classifier

| Stock entry | Bytes | Local mapping | Recovered contract |
| --- | ---: | --- | --- |
| `0x00037B80` | 554 | `goodix_primitives_nadt_auxiliary_state_classify` | classify the final 50 signed samples through range, rounded deviation, strict extrema, extrema clustering, and a consecutive-window transition latch |

The stock absolute context at `0x20007C88` is reduced to an explicit current
result, output mode, consecutive-match counter, and processing flag. The
configuration at `0x20037E10` becomes typed enable, signed range/deviation
thresholds, required extrema count, and required consecutive-window count.
The rolling source is a bounded mutable Int16 span, and only its final 50
values participate.

The function finds the signed extrema and preserves the recovered wrapping
Int16 range. It publishes that range to the optional diagnostics record, then
requires a strict threshold crossing before the full classifier runs. Sample
deviation uses the already-local centered integer formulation and the stock
nearest-even Float32-to-signed conversion. Adjacent duplicates are compacted
in place exactly as stock does. Strict local maxima and minima are collected
through the admitted `0x00098E4C` helper, retained only when they cross half
the full range, and summarized through the admitted wrapping trimmed-mean
helper at `0x0003623C`.

Each polarity counts extrema within ten units of the global endpoint. When
the two trimmed means differ by more than 100, values within ten units of the
matching trimmed mean count as clustered too. A window qualifies only when
its rounded deviation strictly exceeds the configured threshold, both extrema
counts reach the configured minimum, and at least `floor(count/2)` extrema of
each polarity are clustered. Qualifying windows increment the wrapping UInt8
latch; failures reset it. Once the latch reaches the configured consecutive
count and the caller enables transition, the function returns result two,
writes mode five, and clears the latch.

The stock 100-byte allocation is exactly two 25-entry Int16 index banks and is
now fixed caller workspace. Disabled and sub-50-sample calls return the prior
result without touching the latch. Instead of reproducing the stock unbounded
spin while its processing byte is one, the checked API rejects that state
without mutation. The exact body SHA-256 is
`52f12f8d61f54c675abefbdb349899fbbcdec3f843aaaa65f9274e5ba5af601e`.

Tests pin final-50 slicing, 24 maxima/minima, range 100, rounded deviation 51,
two-window transition, transition gating, low-range reset, short/disabled
preservation, adjacent-duplicate in-place compaction, optional diagnostics,
and processing-state rejection before output mutation.

## Packed-channel direct/width scaling closure

| Stock entry | Bytes | Local mapping | Recovered contract |
| --- | ---: | --- | --- |
| `0x000335B4` | 522 | `goodix_primitives_spo2_channel_scale_decode` | decode one direct or width-packed channel/group value and apply the selected scale-code/divisor formula through explicit table and binary64-power bindings |

The source fields previously walked at `+0x04`, `+0x0C`, `+0x10`, `+0x14`,
and `+0x31...+0x33` are a bounded typed scaling record. Direct encoding
converts the selected signed Int32 to Float32 and divides by exact `1000.0f`
and the parallel UInt16 divisor. Packed encoding applies the recovered low-bit
mask, reduces widths above 17 by one mask bit, and right-shifts by
`max(width - 17, 0)` before signed-to-Float32 conversion.

Scale mode zero preserves the stock Float32 multiplication order
`value * 2 * 800 * 1000`, then uses binary64 `/ pow(2,17) * pow(10,3) /
table_scale / divisor`. Modes one and two share binary64 `value * 1.8 /
pow(2,17) / table_scale / divisor * pow(10,9)`. The absolute RAM table root at
`0x20007D68` and its `-0x58` and `-0x24` bank offsets are three explicit
bounded Int32 spans, while `pow` is a typed toolchain provider. Zero table or
divisor values retain the stock zero result; malformed bindings are rejected
before destination mutation.

Tests pin both encodings, the packed mask/shift path, all three scaling modes,
exact constant and power-provider order, zero/unsupported fallbacks, and span
rejection. Together with the earlier source-admitted `0x00061DA4`, the entire
856-byte packed-channel decoder closure is now transparent.

### NADT output-state selector (`0x00036F88`)

The 744-byte body at `0x00036F88`, SHA-256
`1c454b3b53453c7d2e53dc9c04a6ed66c3d82d85b1e3dc7d389085d1cc59f3f3`,
now compiles as `goodix_primitives_nadt_output_state_select`. Its sole caller
is the GH_NADT preprocessing core at `0x0006EA7A`. The local API replaces the
private 0x44-byte lane record and configuration offsets with explicit rate
history, threshold, sample gates, feature flags, and five-state latch fields.

The reconstruction preserves the positive `+0.5` rate and phase rounding,
even-phase six-step retained-rate perturbation, 65..100 output clamp, exact
states `0/1/2/12/21`, output kinds `1/2/5`, threshold crossings, two
signal-present transition flags, retained-rate refresh after kind 5, and the
late sample/persistence override. Only the one lane executed by the stock loop
is represented. Empty history and unknown state values are rejected before
mutation instead of reading before a buffer or silently preserving an invalid
private state.

Tests traverse every legal transition family, the initial sample gate, exact
half-up rate conversion, retained-rate output and perturbation, threshold
clamp, late kind-1 override, retained-rate refresh, and no-mutation rejection
of an unknown state.

### Signal-confidence/state tracker (`0x00095828`)

The 674-byte root at `0x00095828` now compiles as
`goodix_primitives_nadt_signal_confidence_update`. Its stock body SHA-256 is
`509a3440ed4c47ba3c10db0911eb66bff2fbe1bf804e294ad5fe024dad5b98eb`, and its
sole callsite remains `0x0006EA88` in GH_NADT preprocessing root `0x0006E838`.
The local entry consumes the typed output of the already reconstructed
`0x00029144` dual-window feature extractor rather than retaining a private ABI.

The recovered behavior selects or blends the two periodic rates, carries the
corresponding maximum quality, forms 124 signed Float32 differences from the
exact 125-position interval window, and computes sample deviation in a fixed
caller-owned workspace. Strict quality/deviation gates maintain the two
five-window mode counters. The selected rate then passes the recovered
latest-rate, central-band, quality, hold-count, and mode-dependent deviation
gates before entering the 15-value rolling history. The entry publishes the
rolling mean and integrates the zero-centered Gaussian interval
`[-0.05 * mean, +0.05 * mean]` at step `0.1`, using explicit square-root and
exponential bindings. The stock 496-byte heap allocation is absent.

Tests pin disabled-state preservation, 0.8/0.2 rate blending, quality choice,
the exact 125-to-124 interval transform, low/high variation mode transitions,
rolling insertion and mean/probability updates, the ten-window central-rate
recovery gate, wrapping hold counter, invalid-rate preservation, and rejection
of malformed interval extents before history mutation.

### GH_NADT preprocessing orchestrator (`0x0006E838`)

The 682-byte GH_NADT preprocessing root now compiles as
`goodix_primitives_nadt_preprocess_execute`. Its stock body SHA-256 is
`d0e8d34ddfaf97ba47f66e94aa6a104b3efac71452ecb02f4f5a25379f04f656`.
The local plan exposes every direct algorithm stage as a typed enum callback while retaining the
recovered assembly, batch accumulation, readiness, spectral, peak, summary, quality, transition,
inference, output-quality, output-selection, confidence, and output-build order.

The reconstruction preserves the process/frame counters, failure encoding after either of the
first two stages, frame increment before the accumulation-readiness return, integer division by 25,
inference status across downstream output stages, quartic evaluation through the recovered
seven-word coefficient record, and the three exact unsigned bit-range adjustment predicates.
The five stock heap allocations become two lane-sized byte spans and three one-lane typed spans in
caller workspace. Tests cover the complete path, both fallback paths, readiness return, cadence
boundary, adjustment-enabled/threshold-disabled outputs, ignored intermediate status, retained
inference status, uninitialized state, and pre-mutation capacity rejection.

### NADT alternate-state classifier (`0x0007DD58`)

The 874-byte alternate-state classifier now compiles as
`goodix_primitives_nadt_alternate_state_classify`; its stock body SHA-256 is
`46240b4aebd8a3f9d4b26e2f109215ddb0793c7005de78f85826dc9ab7711775`.
The reconstruction preserves the fixed 200-sample min/max/range gate, signed mean, two
`0x00031624` autocorrelation passes with shared persistent tie state, strict local extrema,
peak-quality terminal insertion, signed 800-amplitude filters, count/order alternation rules,
wrapping Int16 interval sum, regularity thresholds, and consecutive-match transition to result 2
and mode 4. Five allocations are replaced by caller-owned signal, extrema, and interval banks.

Tests cover a regular equal-extrema periodic signal, the exact one-extra-maximum ordering branch,
two-window latching, diagnostics, disabled preservation, processing-state rejection, and the
non-200-sample counter reset.

### GH_HR extrema tracker (`0x00034CBC`)

The 956-byte compiler-scattered GH_HR body now compiles as
`goodix_primitives_hr_extrema_tracker_update`; its stock executable-segment SHA-256 is
`41bf9766adb1e05d96397c6e20463f9f7b51fc184319261670451cc4fa50dce0`.
The typed 48-byte record preserves the exact direction states `0/1/2`, full-buffer gate,
period-boundary position compensation, trough and peak positions/values, pair-ready flag,
rise/fall amplitudes and spans, completion flag, and sample index.

When signal mode one requires sub-sample refinement, four explicit curve coordinates bind the
last four history values into the already reconstructed cardinal-spline sampler. Modes `0/1/2/3`
retain 40/20/10/5 subdivisions; unknown modes retain the stock zero-subdivision path. Minimum or
maximum selection then adjusts the corresponding position and value. The stock 82-float local
area is represented as a bounded caller-owned 41-point workspace. Tests traverse unrefined rise
and fall transitions, period rollover, equality-state decisions, minimum/maximum spline paths,
derived amplitudes/spans, incomplete history, and invalid-input no-mutation behavior.

### GH_SPO2/dlCom input diagnostic emitter (`0x0006CCC0`)

The 984-byte diagnostic sibling now compiles as
`goodix_primitives_spo2_input_diagnostics_emit`; its stock body SHA-256 is
`bab60e2e6fdbd5958cac9cd00efc6f13ec921e6af437ea9af500a9a84cd95d7c`.
Its sole stock caller remains `0x0002C944` at `0x0002CA2C`, immediately after the
GH_SPO2/dlCom processing-root call.

The typed configuration makes the stock timestamp-zero initial-record gate explicit and exposes
the exact mode, frequency, channel, timing, scale, heart-rate, and timestamp words. A separately
bounded input exposes PPG values, enable bytes, and accelerometer/gyroscope triples. The local
implementation retains all seventeen format strings—including the recovered `c3Xm` and `groy`
spellings—the exact record order, the per-channel PPG loop, and the
`ceil(3 * channel_count / 8)` enable-byte count. The stock formatter route and direct route become
two typed sinks over an exact format plus at most three signed values. Heap availability is still
queried independently for each active sink, preserving the stock observable call order without a
variadic callback or 128-byte formatting scratch buffer.

Tests pin the nine initial records, timestamp gate, full dynamic order and values, both sink
routes, separate heap queries, three-channel/two-enable rounding, exact triple formats, pre-output
extent rejection, and the no-sink/no-query path.

### NADT window classifier (`0x000856EC`)

The 1,154-byte compiler-scattered body now compiles as
`goodix_primitives_nadt_window_classify`; its executable-segment SHA-256 is
`29e04962b88b0993700f603717f98229bd217e959192d045ee3cd3fbda7f82e1`.
The reconstruction replaces the absolute configuration, runtime state, diagnostic pointer, and
two history globals with bounded typed records. Its three algorithm dependencies are explicit
primary, auxiliary, and alternate classifier callbacks, and the double square root is a typed
toolchain-math binding.

The implementation retains four-lane max/min accumulation, rounded
`64 * sqrt(mean(metric) / 24)`, the exact unsigned Float32-bit interval test, the final-50 nonzero
gate at sample 100, high-variation reset, classifier precedence, elapsed-window result-three
transition, alternate result-two promotion, the cursor-relative 25-sample signed range, both
mode-specific evidence rules, near-zero-axis latch reset, ratio-streak result one, and
profile-specific result-two thresholds. Tests pin those paths, wrapping counters, diagnostics,
callback ordering, the no-mutation current-result contract, and malformed lane/history extents.

### NADT primary-signal classifier (`0x00047240`)

The 3,240-byte compiler-scattered body now compiles as
`goodix_primitives_nadt_primary_signal_classify`; its executable-segment SHA-256 is
`01e21104d3d962a09b4c9087eb0e3a49b56b70ee7ebc1eb4d7aa09236f3ab1ac`.
The reconstruction exposes paired Int32 sample windows, the four-lane activity extrema,
configuration thresholds, shared NADT state, boundary-filter coefficients, autocorrelation tie
state, and diagnostics as bounded types. Its stock heap temporaries are replaced by a fixed
100-sample caller workspace.

The implementation preserves adaptive transition counting, the exact reflected uniform 23-tap
filter path, signed residual construction, modular autocorrelation, strict local extrema and peak
quality, near-zero total/run tracking, four 25-sample ranges, residual turning-point amplitude and
phase analysis, 1500-unit periodic rate, mode-specific evidence counters, quality adjustment,
profile-dependent result-three thresholds, periodic result-one hold, and the strong-periodic bit
two signal. Tests cover disabled passthrough, near-zero classification, the 100-sample quarter
path, diagnostics, and rejection before state mutation.

### NADT harmonic-candidate selector (`0x00035850`)

The 1,162-byte compiler-scattered body now compiles as
`goodix_primitives_nadt_harmonic_candidates_select`; its executable-segment SHA-256 is
`c9fbb161215e9026649909ed8ef04b628221d7d51cbd4affb3c04f0a4c6a6c7a`.
The reconstruction converts six stock allocations into one fixed three-lane workspace and binds
square root explicitly. It retains nearest-peak matching, the 60-unit frequency-error scale,
harmonic-dependent 10/square-root/15 admission gates, amplitude tie breaking, weighted
fundamental fitting, normalized error rejection, and best-family selection. Tests pin a perfect
three-harmonic family, empty input, and rejection without output mutation.

### GH_HR processing root (`0x0006D51C`)

The 1,382-byte root now compiles as `goodix_primitives_hr_process`; its body SHA-256 is
`0f1b8fa8d247ca839a59cfffccb4f70e9cb1a689cd2f736c8514474c02358c9d`.
The stock global context becomes typed input, plan, state, and workspace records. The local path
retains invalid-input handling, motion and signal histories, weighted/extrema stage ordering,
periodic candidate selection, rate conversion, tag-derived quality, quality median, previous
result fallback, and reference-rate recovery. The former decision-stage binding now resolves to `goodix_primitives_hr_decision_update`.

### SpO2/dlCom stream accumulator (`0x0003113C`)

The 1,240-byte compiler-scattered body now compiles as
`goodix_primitives_spo2_stream_accumulate`; its executable-segment SHA-256 is
`96f4fe901ef2933d58e73b36d5532d8bc3623246beee03d37969cc472b695935`.
The stock runtime record becomes typed filter, scale, packed-history, motion-history, percentile,
and anchor state, and its temporary allocation becomes caller scratch. The implementation retains
four optical filter lanes, decimal-residual axis correction, RMS motion magnitude, exact-window
median cleanup and replay, subsequent rolling-percentile selection, and the every-third magnitude
lane. Tests cover the initial fill/replay, rolling continuation, and no-mutation rejection.

### Complete SpO2/dlCom processing root (`0x0006C6A8`)

The final 1,370-byte Goodix root now compiles as
`goodix_primitives_spo2_process`; its exact executable SHA-256 is
`400fd57d9c750bef559ccbc41301602007192f79f8cc13cebadd528795011d2c`.
The reconstruction exposes configuration, sample input, five-word output, persistent stream/report
state, packed-bank and spectral bindings, generated-model dispatch records, quantized runtime, and
math providers as bounded types. A fixed caller workspace replaces the stock 7,740-byte working
allocation, 16-byte report allocation, and 99-Float temporary.

The implementation preserves first-group transform validation and all-channel clearing, elapsed
quotient and cadence, MSB-first three-group assembly, valid-channel rejection, the fixed mode-zero
stream call, `stream_count > 50`, `sample_count > 150`, modulo-25 gating, seven packed banks,
four deviations, conditional triplicate expansion, seven-row range normalization, five normalized
spectra, report analysis, inclusive bins 15...113, four 99-value normalized model rows, configured
in-place Int8 quantization, filtered timed dispatch, transient-history logistic score, exact
half-away rounding, 70-point score flag, score scaling, and delayed publication. Tests pin cadence,
sanitation, the complete four-plus-four-plus-four sample layout, counter/error asymmetry, bounded
input rejection, and one full downstream pass.

### NADT streaming process (`0x0006E008`)

The 1,294-byte compiler-scattered root now compiles as
`goodix_primitives_nadt_stream_process`; its executable-segment SHA-256 is
`1b8a57e2d23467bbcd143115751d867207f56b1f12de3bada3efb8439795b5ea`.
The reconstruction exposes the runtime/configuration globals as typed records and uses fixed
caller storage for the 100-sample raw, filtered, and configuration-marker histories plus the
200-sample half-rate history. It retains the 25-Hz cadence, ratio triggers, sample preparation,
optical filter, rolling activity statistics, classifier dispatch, history compaction, and packed
result flag. Tests exercise cadence, a classified window, history extents, initialization, and
preflight rejection.

## GH_HR feature/event decision core (`0x00032808`)

The final 2,814-byte GH_HR child now compiles as
`goodix_primitives_hr_decision_update`; its four executable segments hash to
`d2723d09bfc22aef66fafa55623c2d86fb275a1a85b31b96759df0e0a8028a6f`.
The reconstruction exposes the complete 32-byte decision record, pending event
source, 20-record history, three 10-value diagnostic histories, sample-rate
interval limits, mode/latch/stale state, and capped three-value running
baseline. The stock mask and Float32 allocations become fixed caller workspace.
It retains periodic position shifts, pending-event clearing, primary/auxiliary
and interval geometry, MAD inlier selection, coefficient-of-variation
diagnostics, exact 0.05/0.8/0.6/0.3/0.2 thresholds, event tagging, six-float
merge semantics, baseline-qualified pair rebalancing, promotion to tracking
mode, latch recovery, stale-count handling, and fresh diagnostic baseline
replacement. Tests cover the periodic no-event path, first-event append,
mode promotion, all three histories, MAD diagnostics, source clearing, and
preflight no-mutation.

The complete Goodix reconstruction now has 339 compiled mappings: 320 formerly
opaque candidates, seventeen public-democode replacements, and two product
entries. No Goodix candidate function remains opaque; locally reconstructed
candidate bodies cover 66,048 declared stock bytes.
