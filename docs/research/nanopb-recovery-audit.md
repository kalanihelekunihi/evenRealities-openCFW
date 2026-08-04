# nanopb Recovery Audit — Even Realities G2 firmware `g2-2.2.6.10`

**Status: research-only recovery.** This document records a static reverse-engineering
analysis of the shipped firmware blob for interoperability / provenance purposes. No
firmware, build files, or blobs were modified. All findings are derived from read-only
disassembly with `python3` + `capstone` 5.0.7 (ARM Cortex-M55 Thumb-2, little-endian).

## Subject

| Item | Value |
|---|---|
| Blob | `blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin` |
| Size | 3,523,396 bytes (0x35C344) |
| Image type | Raw ARMv8.1-M / Cortex-M55 Thumb-2 XIP image |
| Load mapping | `run_addr = file_offset + 0x00437FE0` (confirmed; file 0x20 → run 0x438000) |
| nanopb runtime code region | file 0x57000–0x59400 → run **0x48F000–0x491400** |
| nanopb runtime string pool | file 0x31F688, 0x337474, 0x3497FC–0x3498EC, 0x34FC70–0x34FD00, 0x3536C8 |

The generator-emitted, application-level `.proto` messages (`ring.proto`,
`dashboard_ext.proto`, `sync_info`, `terminal`, `conversate`, `evenai`, etc.) are handled
by a single shared nanopb 0.4.x runtime linked once into the image at run 0x48F000.

---

## 1. Identity evidence

nanopb embeds **no version string** at runtime (`NANOPB_VERSION` is a compile-time macro
only), so identity rests on (a) the exact runtime error-string set and (b) the ABI/struct
layout observed in disassembly. Every string below was located by packing its run address
little-endian and finding the literal-pool word that references it; the referencing
function was then disassembled from its `push {…,lr}` entry.

### 1.1 Runtime error strings (nanopb-specific), with referencing function

| String | str run addr | referenced by (fn run addr) | nanopb source origin |
|---|---|---|---|
| `end-of-stream` | 0x787C70 | 0x48F3BE, 0x48F454 | `pb_decode.c` `buf_read`/`pb_readbyte` |
| `invalid wire_type` | 0x7817DC | 0x48F6A0, 0x48F6EA | `pb_decode.c` `pb_skip_field` |
| `wrong wire type` | 0x787CA0 | 0x48F7F4 | `pb_decode.c` `decode_basic_field` |
| `invalid field type` | 0x7817F0 / 0x781854 | 0x48F7F4, 0x48F968, 0x48FBE4, 0x490A46, 0x490D66 | decode/encode dispatch default case |
| `array overflow` | 0x787CB0 | 0x48F968 | `pb_decode.c` `decode_static_field` |
| `no malloc support` | 0x781804 | 0x48F968 (stub 0x48FB1C), 0x490358, 0x4903EA | pointer-field path, `PB_ENABLE_MALLOC` **off** |
| `callback failed` | 0x787CC0 | 0x48FB30 | `pb_decode.c` `decode_callback_field` |
| `invalid extension` | 0x781818 / 0x781868 | 0x48FC26, 0x490BC8 | extension decode/encode |
| `wrong size for fixed count field` | 0x757668 | 0x48FE98 | `pb_decode.c` fixed-count (`FT_STATIC` fixed array) |
| `integer too large` | 0x781840 | 0x4901D6 | `pb_decode.c` `pb_dec_varint` |
| `invalid data_size` | 0x78182C / 0x781890 | 0x4901D6, 0x490EAE, 0x490F72 | `pb_dec_varint` / `pb_enc_fixed` |
| `bytes overflow` | 0x787CD0 | 0x490358, 0x49053C | `pb_decode.c` `pb_dec_bytes` / fixed-length bytes |
| `string overflow` | 0x787CE0 | 0x4903EA | `pb_decode.c` `pb_dec_string` |
| `invalid field descriptor` | 0x76F454 / 0x76F470 | 0x49048C, 0x49104C | `pb_common.c`-derived iterator init |
| `submsg size changed` | 0x78187C | 0x490DDC | `pb_encode.c` `pb_encode_submessage` |
| `bytes size exceeded` | 0x7818A4 | 0x490FA2 | `pb_encode.c` `pb_enc_bytes` |
| `stream full` | 0x78B6A8 | 0x490616, 0x490DDC | `pb_encode.c` `buf_write` |

This is the complete and characteristic nanopb **0.4.x** runtime string set. The presence
of `wrong size for fixed count field` and the `invalid field descriptor` iterator error
require the **0.4.x compact-descriptor** runtime (these do not exist in the 0.3.x
`pb_field_t`-array ABI). No `invalid UTF-8 string`, no `pb_realloc`/`pb_free`, and no
`nanopb-0.4.x` path/version literal appear anywhere in the image.

### 1.2 Core functions (run addresses)

Decode side — `pb_decode.c` (region run 0x48F000–0x490600):

| Function (best-fit name) | run addr |
|---|---|
| `buf_read` / `pb_read` | 0x48F3BE |
| `pb_readbyte` / raw read | 0x48F454 |
| `pb_decode_varint32` wrapper | 0x48F5AE |
| `pb_decode_varint` (64-bit) | 0x48F5B8 |
| `pb_decode_tag` | 0x48F66C |
| `pb_skip_field` | 0x48F6A0 / 0x48F6EA |
| `pb_field_iter_next` | 0x48F77E |
| `decode_basic_field` | 0x48F7F4 |
| `decode_static_field` | 0x48F968 |
| `decode_pointer_field` (no-malloc stub) | 0x48FB1C |
| `decode_callback_field` | 0x48FB30 |
| `decode_field` (dispatch) | 0x48FBE4 |
| `decode_extension` | 0x48FC26 |
| `pb_decode_inner` (main field loop) | 0x48FE98 |
| `pb_dec_varint` | 0x4901D6 |
| `pb_dec_bytes` | 0x490358 |
| `pb_dec_string` | 0x4903EA |
| `pb_decode` / top-level `decode_field` | 0x49048C |
| `pb_dec_fixed_length_bytes` | 0x49053C |

Encode side — `pb_encode.c` (region run 0x490600–0x491400):

| Function (best-fit name) | run addr |
|---|---|
| `buf_write` / `pb_write` | 0x490616 |
| encode dispatch (`pb_enc_*`) | 0x490A46, 0x490D66 |
| `encode_extension_field` | 0x490BC8 |
| `pb_encode_submessage` | 0x490DDC |
| `pb_enc_fixed` (32/64) | 0x490EAE, 0x490F72 |
| `pb_enc_bytes` | 0x490FA2 |
| `pb_encode` / `encode_field` | 0x49104C |

---

## 2. Recovered configuration macros (disassembly evidence)

### 2.1 `PB_ENABLE_MALLOC` — **OFF (disabled)**

`decode_static_field` (0x48F968) dispatches on the pointer/static ATYPE; the pointer
branch tail-calls a stub at run **0x48FB1C** that unconditionally sets the error string and
returns false:

```
0x0048fb26: ldr.w  r1, [pc, #0xa84]   ; -> "no malloc support"
0x0048fb2a: str    r1, [r0, #0xc]     ; stream->errmsg = "no malloc support"
0x0048fb2c: movs   r0, #0
0x0048fb2e: bx     lr
```

`pb_dec_string` (0x4903EA) and `pb_dec_bytes` (0x490358) contain the same guard: an ATYPE
test `(type & 0xC0) == 0x80` (pointer) routes to `"no malloc support"`:

```
0x00490438: ldrb   r1, [r6, #0x16]     ; iter->type
0x0049043a: ands   r1, r1, #0xc0       ; ATYPE mask
0x0049043e: cmp    r1, #0x80           ; PB_ATYPE_POINTER
0x00490440: bne    ...
0x0049044c: ldr    r0, [pc, #0x15c]    ; -> "no malloc support"
```

There is **no** `pb_realloc`/`pb_free`/`allocate_field` code — the pointer path is a pure
error stub. This is the exact shape emitted when nanopb is built without
`PB_ENABLE_MALLOC`. Consistent with the prior finding that dynamic allocation is disabled.

### 2.2 `PB_FIELD_32BIT` — **OFF (pb_size_t = 16-bit, the default)**

Every `pb_field_iter_t` size/count/tag member is accessed with a **16-bit** `ldrh`/`strh`,
never a 32-bit `ldr`. In `decode_static_field` (0x48F968) and `pb_dec_varint` (0x4901D6):

```
0x004901f8: ldrh   r0, [r5, #0x12]    ; iter->data_size  (pb_size_t)
...
0x00490572: ldrh   r1, [r5, #0x12]    ; data_size
0x0048fa46: ldrh   r3, [r5, #0x12]    ; data_size
0x0048fa58: ldrh   r1, [r5, #0x14]    ; iter->array_size (pb_size_t)
0x0048fa98: ldrh   r0, [r5, #0x10]    ; iter->tag        (pb_size_t)
```

Reconstructed `pb_field_iter_t` layout (total 0x28 bytes):

```
+0x00 descriptor  +0x04 message
+0x08 index(u16)  +0x0a field_info_index(u16)  +0x0c required_field_index(u16)  +0x0e submessage_index(u16)
+0x10 tag(u16)    +0x12 data_size(u16)         +0x14 array_size(u16)            +0x16 type(u8)+pad
+0x18 pField      +0x1c pData                  +0x20 pSize                      +0x24 submsg_desc
```

All `pb_size_t` members are 16 bits ⇒ `PB_FIELD_32BIT` is **not** defined (nanopb default).
This is the "16-bit field descriptors" configuration.

### 2.3 64-bit integers — **enabled (`PB_WITHOUT_64BIT` OFF)**

`pb_decode_varint` (0x48F5B8) decodes a full 64-bit value into an `r4:r5` register pair
(`strd r4, r5, [r7]`) with the 10-byte / 63-bit overflow guard. `pb_dec_varint` (0x4901D6)
stores size-8 fields with 64-bit `ldrd`/`strd`:

```
0x004901f8: ldrh   r0, [r5, #0x12]         ; data_size
0x004901fa: cmp    r0, #8
0x004901fe: ldrd   r0, r1, [sp, #8]        ; 64-bit value
0x00490204: strd   r0, r1, [r2]            ; store 8-byte field
0x0049020c: cmp    r1, r3 ; ... -> "integer too large" on truncation
```

The size dispatch handles 8/4/2/1-byte targets; size 8 uses `strd` (no 32-bit clamp).
64-bit varint/fixed support is compiled in.

### 2.4 `PB_CONVERT_DOUBLE_FLOAT` — **inactive / no conversion code**

A full disassembly sweep of the nanopb region (run 0x48F000–0x491400) contains **zero**
VFP instructions (`vcvt`, `vmov`, `vldr`, `vstr`, `vadd`, `vmul`) — see scan, 0 hits.
`pb_dec_fixed`/`pb_enc_fixed` move 8-byte doubles as raw memory (`ldrd`/`strd`), with no
float↔double conversion helper. On the Apollo510 Cortex-M55 (hardware FP64, `sizeof(double)
== 8`), `PB_CONVERT_DOUBLE_FLOAT` is a no-op even if defined; there is no evidence of the
conversion path being compiled or reachable. Doubles are handled natively as 8 bytes.

### 2.5 `PB_VALIDATE_UTF8` — **OFF**

No `invalid UTF-8 string` literal exists in the image, and `pb_dec_string` (0x4903EA)
writes the null terminator and copies bytes with **no** `pb_validate_utf8` call:

```
0x0049046c: movs   r0, #0
0x0049046e: ldr    r1, [sp]
0x00490470: strb   r0, [r5, r1]           ; NUL-terminate
0x00490472: ldr    r2, [sp]
0x00490478: bl     #0x48f3be              ; pb_read(bytes) — then return
```

UTF-8 validation is not compiled in.

### 2.6 `PB_MAX_REQUIRED_FIELDS` — **64 (default)**

`pb_decode_inner` (0x48FE98) tracks seen required fields in a stack bitmask
(`add r?, sp, #0xc`, indexed by `field_index >> 5`, bit `1 << (index & 0x1f)`), and clamps
the required-field range to 64:

```
0x00490024: cmp    r0, #0x40            ; index < 64
...
0x00490090: uxth   r1, r1
0x00490094: cmp    r1, #0x41            ; > 64 ?
0x00490098: movs   r0, #0x40            ; clamp to 64
```

The bitmask capacity and the `#0x40`/`#0x41` clamp correspond to the default
`PB_MAX_REQUIRED_FIELDS = 64`.

### 2.7 Packed/repeated + fixed-count + fixed-length-bytes — **enabled**

`decode_static_field` (0x48F968) implements the packed-repeated inner loop and static-array
bounds (`array overflow`); `pb_dec_fixed_length_bytes` (0x49053C) and the
`wrong size for fixed count field` path (referenced from `pb_decode_inner`, 0x48FE98) show
the `FT_STATIC` fixed-count and `FIXED_LENGTH_BYTES` features are present with size checks.

### Config summary

| Macro | State | Primary evidence (run addr) |
|---|---|---|
| `PB_ENABLE_MALLOC` | **off** | 0x48FB1C stub, 0x4903EA/0x490358 ATYPE guard |
| `PB_FIELD_32BIT` | **off** (16-bit `pb_size_t`) | `ldrh` field access, 0x48F968 / 0x4901D6 |
| `PB_WITHOUT_64BIT` | **off** (64-bit on) | `ldrd`/`strd` size-8, 0x48F5B8 / 0x4901D6 |
| `PB_CONVERT_DOUBLE_FLOAT` | inactive / no conv code | 0 VFP insns in 0x48F000–0x491400 |
| `PB_VALIDATE_UTF8` | **off** | no UTF-8 string; 0x4903EA has no validator |
| `PB_MAX_REQUIRED_FIELDS` | **64** (default) | clamp 0x490024 / 0x490094 |
| packed/fixed-count/fixed-length-bytes + size checks | **on** | 0x48F968, 0x49053C, 0x48FE98 |

---

## 3. Point-release determination

**Firm lower bound: nanopb ≥ 0.4.2.** In `decode_callback_field` (0x48FB30) the code loads
the message descriptor from the field iterator and calls the message-level
`field_callback` at descriptor offset **+0x0C**:

```
0x0048fb38: ldr    r0, [r5]           ; iter->descriptor  (pb_msgdesc_t*)
0x0048fb3a: ldr    r0, [r0, #0xc]     ; descriptor->field_callback
0x0048fb3c: cmp    r0, #0
...
0x0048fb76: ldr    r3, [r5]
0x0048fb78: ldr    r3, [r3, #0xc]     ; descriptor->field_callback
0x0048fb7a: blx    r3                 ; call it (istream, 0, iter)
```

The per-message `field_callback` member of `pb_msgdesc_t` (and `pb_default_field_callback`)
was **introduced in nanopb 0.4.2**; the compact-descriptor iterator, `field_info` /
`submsg_info` / `default_value` / `field_callback` layout observed here is the 0.4.2+ ABI.
The 0.4.0/0.4.1 descriptor had no `field_callback` slot, so those are excluded, as is all of
0.3.x (incompatible `pb_field_t`-array ABI).

**Stronger lower bound: pristine upstream ≥ 0.4.7.** `pb_decode_varint`
(`0x0048F5B8`) uses the 63-bit-limit plus tenth-byte `& 0xFE` overflow guard
introduced in 0.4.6, correcting this audit's earlier 0.4.4 attribution. More
decisively, `pb_read()` at `0x0048F43C` contains the saturating post-callback
`bytes_left` clamp introduced in 0.4.7. Authenticated reference sources and
builds therefore exclude unmodified 0.4.4, 0.4.5, and 0.4.6.

**Cannot pin a single point release in 0.4.7–0.4.9.** Authenticated Cortex-M55
reference builds of `pb_common.c`, `pb_decode.c`, and `pb_encode.c` produce
byte-identical object triplets for all three surviving releases under the
recovered G2 configuration. Runtime C and effective header changes provide no
additional discriminator in this target build.

**Determination:** the runtime is compatible with pristine upstream nanopb
**0.4.7–0.4.9**. A vendor backport could reproduce either discriminator, so
this remains a compatibility range rather than an unequivocal vendor-version
claim. The complete Git-object, source-hash, instruction, and reference-build
proof is in `nanopb-point-release-recovery-audit.md`.

### What would settle it

1. **Dependency provenance.** Recover a retained build manifest, SBOM, package
   lock, submodule SHA, or compiler log that names the vendor source revision.
2. **Generator stamp.** Any retained build manifest / SBOM / lockfile referencing the
   `nanopb` package version, or a generated `*.pb.h` carrying the generator version comment
   (comments are not in the stripped blob but are in the source tree if available).
3. **Descriptor-format micro-changes.** A byte-level study of the `field_info` word encoding
   emitted by `PB_BIND` for a known message, compared against generator output per release —
   the generator's descriptor packing has minor version-dependent edges.

---

## 4. Remaining checks / open items

- Recover a manifest, generator stamp, or known schema/descriptor pair to
  separate the reference-build-equivalent 0.4.7–0.4.9 releases (Section 3.1).
- Confirm `pb_encode.c` mirror config (encode side already shows `stream full`,
  `submsg size changed`, `bytes size exceeded`, `invalid data_size` at 0x490616–0x49104C;
  no encode-side malloc/UTF-8 paths observed) with a full encode-path walk if needed.
- Enumerate which application `.proto` message descriptors use callbacks vs. static fields
  (the shared runtime supports both; `decode_callback_field` at 0x48FB30 is live).
- No action on build/source files is implied by this document — recovery only.

### Method notes (reproducibility)

- `run_addr = file_offset + 0x437FE0`; string refs found by
  `data.find(struct.pack('<I', run_addr))` (literal-pool words); functions disassembled
  from `push {…,lr}` entries with capstone `CS_ARCH_ARM, CS_MODE_THUMB|CS_MODE_LITTLE_ENDIAN`
  over bounded windows (no whole-image linear sweep).
- VFP scan disassembled the entire 0x57000–0x59400 file window and filtered for
  `vcvt/vmov/vldr/vstr/vadd/vmul`: 0 hits.
