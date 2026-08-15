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
