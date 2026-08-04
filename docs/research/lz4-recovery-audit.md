# LZ4 Recovery Audit — Even Realities G2 firmware `g2-2.2.6.10`

Status: research-only recovery, no artifact changed.

## Scope and method

- Blob: `blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin` (3,523,396 bytes),
  raw ARM Cortex-M55 Thumb-2 XIP image.
- Load mapping (confirmed): `run_addr = file_offset + 0x00437FE0`.
- Tools: `strings`, python3 + capstone 5.0.7 (`CS_ARCH_ARM`, `CS_MODE_THUMB`),
  bounded-window disassembly from known `push {..,lr}` entries. No linear sweep.
- Every address below is a **run address** unless labeled "file offset".

## Determination (summary)

- The codec identity is unequivocally LZ4, but its point release is
  **unresolved between authenticated upstream v1.9.4 and v1.10.0 source
  states**. Primary-upstream review corrected the earlier claim that three
  `read_variable_length` properties were v1.10.0-only: all three already exist
  in official v1.9.4 (see "Point-release correction").
- **Only the decompressor is present.** No LZ4 compressor is linked (no hash
  multiplier constant, no hash table, no compressor entry).
- Source lineage: **the LZ4 bundled with LVGL v9.3**, inferred (not proven) from
  build context — see "Source lineage".

## Identity evidence (strings)

The blob contains **no** LZ4 version string and **no** `third_party\lz4` (or
`libs/lz4`) source path. Every other third-party library in this build emits a
Windows `__FILE__` path (e.g. `...\third_party\lvgl_v9.3\LVGL\src\...`,
`...\third_party\littlefs\...`, `...\third_party\cordio\...`), but LZ4 emits
none — consistent with `lz4.c`, which does no `__FILE__`-based logging. The only
LZ4-related strings are application-level usage/log messages:

| String | File offset | Run address |
|---|---|---|
| `[navigation.ui]lz4 decompress mini map data len = %u` | `0x2e86c8` | `0x7206a8` |
| `[navigation.ui]lz4 decompress max map data len = %u`  | `0x2f31b4` | `0x72b194` |
| `lz4 decompress mini map data len = %u`                | `0x3138bc` | `0x74b89c` |
| `lz4 decompress max map data len = %u`                 | `0x313934` | `0x74b914` |
| `LZ4 decompress is not enabled`                        | `0x328810` | `0x7607f0` |

All five are used by application (navigation.ui) code, not by LVGL's image
decoder. The literal-pool word holding each string address was located by
searching the image for `struct.pack('<I', run_addr)`; the navigation strings
are referenced from the logging function at `~0x549ab4`, whose LZ4 call site is
`bl 0x4e0c0c` at `0x549ad8` (result logged as "…data len = %u").

## Recovered function / data addresses

| Symbol (inferred) | Run address | Notes |
|---|---|---|
| App LZ4 wrapper (null-checks args, reorders, calls safe) | `0x4e0c0c` | `push {r4,lr}`; validates dst/src/sizes != 0; `bl 0x54f338`; returns 0 on `result < 1` |
| `LZ4_decompress_safe` (thin wrapper) | `0x54f338` | zero-fills dict args on stack; `bl 0x54ef08` |
| `LZ4_decompress_generic` (core) | `0x54ef08` | full token/literal/match state machine |
| `read_variable_length` | `0x54ee90` | Authenticated LZ4 helper; not a point-release discriminator (below) |
| `LZ4_readLE16` | `0x54ee4e` | endian check then `p[0] | p[1]<<8` |
| `LZ4_isLittleEndian` (returns runtime byte) | `0x54ee18` | loads a global, reads low byte |
| `LZ4_wildCopy8` | `0x54ee6e` | 8-byte-chunk copy loop `while (d<e)` |
| 2-byte reader helper (memcpy 2) | `0x54ee2a` | used by big-endian `LZ4_readLE16` path |
| 4-byte reader helper (memcpy 4) | `0x54ee3e` | |
| `inc32table[8]` | `0x762110` | values `{0,1,2,1,0,4,4,4}` — canonical LZ4 |
| `dec64table[8]` | `0x762130` | values `{0,0,0,-1,-4,1,2,3}` — canonical LZ4 |
| `rvl_error` global (`(unsigned)-1`) | `0x78f2bc` | value `0xFFFFFFFF`; compared against `read_variable_length` result |

Shared runtime helpers used by the codec: `memcpy` at `0x439be4`,
`memmove` at `0x439710`.

The `inc32table`/`dec64table` values match upstream LZ4 exactly, independently
confirming this is genuine LZ4 (not a look-alike).

## Point-release correction — v1.9.4 remains possible

The original version conclusion was wrong. It compared the recovered helper
against a non-authoritative or older source shape instead of the official
`lz4/lz4` tag. The primary upstream references are:

| Release | Commit / tree | `lib/lz4.c` identity |
|---|---|---|
| `v1.9.4` | commit `5ff839680134437dbf4678f3d0c7b371d84f4964`; tree `939d919c3903b42ed637542a4799fb3f4fa8b5fc` | 113,390 B; SHA-256 `b6a85fd8f9be0fedb568abd1338719b23b999583ccda6f3404d5ae11e4ce7b8e`; Git blob `654bfdf32f96ac633a5d4bc4dde097dbdff46882` |
| `v1.10.0` | commit `ebb370ca83af193212df4dcbadcc5d87bc0de2f0`; tree `1ff35e0f086e3b431ea0efd001eb5c6254561953` | 118,145 B; SHA-256 `9396f7de527bc8435de9c7569fb7998e56545a84b4f3c2d808c0235c01774539`; Git blob `a2f7abee19fb9a5c768f2a6c266acf5b571f0855` |

Official v1.9.4 `lib/lz4.c` lines 1901–1928 contain the same three
properties formerly described as decisive:

1. `Rvl_t` is `size_t`, failure is the `(Rvl_t)-1` `rvl_error` sentinel, and
   the signature is the same three-argument
   `read_variable_length(const BYTE** ip, const BYTE* ilimit,
   int initial_check)` form.
2. Its post-increment input bound is the same strict
   `if (unlikely((*ip) > ilimit))`, not `>=`.
3. Lines 1921–1923 contain the same 32-bit guard
   `length > ((Rvl_t)(-1)/2)`.

The recovered G2 helper does contain that guard:

   ```
   0x0054eec2: cmp.w  r0, #-0x80000000     ; length vs 0x80000000
   0x0054eec6: blo    0x54eed0             ; continue if length < 0x80000000
   0x0054eec8: ldr.w  r0, [pc, #0x48c]     ; else load rvl_error ...
   0x0054eecc: ldr    r0, [r0]             ; ... = 0xFFFFFFFF
   0x0054eece: b      0x54ef02             ; return rvl_error
   ```

This matches both official releases on a 32-bit target. The recovered strict
post-increment bound also matches both:

   ```
   0x0054eeb4: ldr    r4, [r3]             ; *ip (after increment)
   0x0054eeb6: cmp    r1, r4               ; ilimit vs *ip
   0x0054eeb8: bhs    0x54eec2             ; continue while ilimit >= *ip
   0x0054eeba: ...    return rvl_error     ; i.e. error only when *ip > ilimit
   ```

The two G2 call sites compare the return value against the `0xFFFFFFFF`
`rvl_error` global: the literal-length call at `0x54f046` followed by the
compare at `0x54f04a..0x54f052`, and the match-length call at `0x54f12e`
followed by the compare at `0x54f132..0x54f13a`. Again, this authenticates LZ4
but does not separate v1.9.4 from v1.10.0.

v1.10.0 refactors the first extension-byte iteration ahead of the `do` loop
and adds a fast return when that byte is not `255`; v1.9.4 keeps that first
iteration inside the loop. The observable bounds, sentinel, accumulator guard,
and decoded/error contract remain the same. An optimizing compiler can produce
the split control flow from either source form, so stripped optimized IAR code
is not a defensible source-tag discriminator without an instruction or literal
that cannot arise from both. No such marker has been established. The point
release therefore remains unresolved.

## Compressor presence — decompressor only

No LZ4 compressor is linked:
- The LZ4 hash multiplier `0x9E3779B1` (used by `LZ4_hash4`/`LZ4_hashPosition`
  in every LZ4 compressor) does **not** appear anywhere in the image; nor does
  `0x9E3779B9`. (xxHash seed `0x2545F491` is also absent.)
- No compressor hash table, `LZ4_compress_*` entry, or
  `LZ4_MEMORY_USAGE`-sized buffer was found.
- The only reachable LZ4 code is the decompression call chain
  `app wrapper 0x4e0c0c → LZ4_decompress_safe 0x54f338 → LZ4_decompress_generic
  0x54ef08` plus its leaf helpers.

Because no compressor is present, `LZ4_MEMORY_USAGE` / hash-table-size evidence
is not available. The decompressor markers fix the library identity but not the
point release.

## Source lineage — LVGL v9.3 bundle (inferred candidate)

The LVGL-bundled v1.10.0 source remains a plausible provenance candidate, not
a proven version or checkout:
- LVGL **v9.3** is unambiguously in this build (hundreds of
  `...\third_party\lvgl_v9.3\LVGL\src\...` path strings), and its vendored LZ4 is
  1.10.0 — consistent with the recovered decoder.
- There is **no** standalone `third_party\lz4` path among the many third-party
  path strings, even though every other third-party lib in this build does emit
  its paths. This is consistent with the codec coming in via LVGL's bundle rather
  than a separately vendored standalone `lz4.c`.
- Caveat: LVGL's bundled `lz4.c` is byte-identical to upstream standalone
  `lz4.c` of the same source state, so code shape cannot distinguish bundled
  from standalone provenance. The context also does not override the corrected
  v1.9.4/v1.10.0 ambiguity. The absence of a `__FILE__` path is expected and is
  not evidence either way.

## Remaining checks (would strengthen / settle open points)

- Compile authenticated v1.9.4 and v1.10.0 with the recovered IAR target profile
  and search the complete decoder closure for a reproducible instruction or
  data discriminator. Matching one optimized build is not sufficient if the
  other source state can generate the same bytes.
- Confirm `LZ4_decompress_safe` prototype/arg order at `0x54f338` by fully
  decoding the stacked dict arguments passed to the generic (`endCondition`,
  `dict`, `lowPrefix`, `dictStart`, `dictSize`) to verify it is the `safe`
  (noDict, full-block) instantiation rather than `safe_partial`.
- Verify no second LZ4 instantiation exists (e.g. a `_usingDict` variant) by
  enumerating all callers of `LZ4_decompress_generic 0x54ef08`.
