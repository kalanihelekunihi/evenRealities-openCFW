# nanopb private read-pair production-source audit

Status: bounded Apollo-main production source pair; no signing, flashing, or
on-device claim.

Scope: the private nanopb `buf_read()` and `pb_readbyte()` helpers in the
official G2 `2.2.6.10` Apollo-main image, authenticated nanopb 0.4.9 source,
the recovered stream ABI, callback identity, complete entry topology, retained
binary seams, host behavior, and an isolated Thumb target compile.

## Result

The stock helpers are compatible with the pristine nanopb 0.4.9 definitions
under the recovered G2 configuration. The definitions are also byte-identical
in pristine nanopb 0.4.7 and 0.4.8, but that compatibility range does **not**
prove the vendor's historical point release or checkout.

This evidence supports two bounded, uniquely named production functions in
separate translation units so each leaf has an independently closed relocation
set:

- `components/shared/nanopb/runtime_nanopb_buf_read.c` provides
  `open_cfw_nanopb_buf_read`; and
- `components/shared/nanopb/runtime_nanopb_readbyte.c` provides
  `open_cfw_nanopb_readbyte`.

Both are registered in the production overlay, firmware manifest, nanopb
provenance allowlist, and snapshot verifier. The overlay emits full-span entry
patches at the two authenticated stock bodies. At this read-pair milestone no
constructor patch was needed: the canonical callback identity remained the odd
Thumb entry `0x0048F3A5`. The later stream-constructor promotion is recorded in
`nanopb-istream-from-buffer-source-audit.md`.

## Content-addressed upstream authority

The selected offline baseline is nanopb 0.4.9 commit
`98bf4db69897b53434f3d0ba72e0a3ab1a902824`. Its `pb_decode.c` is 53,845
bytes with SHA-256
`e980f2a41d9abe37b7e6fb4c9ba1ebfd68507a6fd2653f8d755e1947a9c84b1a`.
The repository snapshot verifier authenticates the selected commit, tree,
files, and Zlib license.

Definitions are extracted from the first byte of the complete function
signature through the matching closing brace, without normalization.

| Definition | nanopb 0.4.9 byte span | Bytes | SHA-256 |
|---|---:|---:|---|
| private `buf_read` | `[3421,3743)` | 322 | `34b5a0a938c4cbfe431c24afc0a8f273879eef4ee4853282d4c44708f27f4867` |
| private `pb_readbyte` | `[4678,5112)` | 434 | `5a63231a2b3b2d79004219076ec6b6089c9d4ed2d9487cae9f0488e8c607c650` |
| `pb_istream_from_buffer` identity authority | `[5114,5692)` | 578 | `087c2b851d9ea55d5a81d70a37a88385ee7fe8db86daef34ea3d0584183b0b13` |

The 0.4.7 and 0.4.8 spans are `[3335,3657)`, `[4592,5026)`, and
`[5028,5606)` respectively and have the same three definition hashes.

## Authenticated stock boundaries

The official firmware package is 3,523,396 bytes and hashes to
`36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`.

| Provider | Runtime span | Bytes | SHA-256 |
|---|---:|---:|---|
| private `buf_read` | `[0x0048F3A4,0x0048F3BE)` | 26 | `9d6c6690294b82bbafba82ec0f63a6bb5b78e4146543db3a30fac92469ace723` |
| private `pb_readbyte` | `[0x0048F454,0x0048F49C)` | 72 | `15c8303c5c1dbf1b3f143142c6169026cb8bc56b37a6291dd0457b3664b67ae5` |
| `pb_istream_from_buffer` | `[0x0048F49C,0x0048F4B8)` | 28 | `852314bb8f86dcbd550deb0f51bc285b662e39c1b4fae66690c44a7bf4f7a674` |

The helpers exactly abut the already-reviewed `pb_read` entry and constructor;
there is no padding to infer as ownership.

## Complete ingress and identity topology

Exhaustive aligned Thumb-2 BL, B.W, wide-conditional, narrow-branch, and
byte-granular pointer scans produce this closure:

- `buf_read` has no direct branch caller and no interior ingress. The only
  stored pointer into its span is the canonical Thumb value `0x0048F3A5` at
  literal slot `0x0048FC78`.
- `pb_read` loads that literal at `0x0048F3D4` for its buffer-callback identity
  comparison. `pb_istream_from_buffer` loads the same literal at `0x0048F49E`
  and stores it in every constructed buffer stream.
- `pb_readbyte` has exactly three stock BL callers, all at its entry:
  `0x0048F4C4`, `0x0048F4FA`, and `0x0048F5CC`. It has no B.W, conditional,
  narrow, stored-pointer, or interior ingress.
- The current production source replacement for `pb_decode_varint` removes
  the executable stock call at `0x0048F5CC` and relocates its equivalent call
  to the stable `pb_readbyte` entry. The two `0x0048F4xx` callers remain.

The callback literal bytes are `a5f34800` with SHA-256
`4be42e91f7757f32aff0acddae22d357d34e83b8f10ef8e9c93339501ea69c3b`.
At this read-pair milestone the production trampoline at `0x0048F3A4`
preserved the odd callback identity `0x0048F3A5` without replacing the
constructor. The later constructor leaf preserves the same identity. The full
26-byte stock body is replaced by a four-byte B.W followed by eleven Thumb
NOPs. The full 72-byte `pb_readbyte` body is similarly replaced by a B.W and
thirty-four Thumb NOPs.

## ABI and retained closure

The recovered 32-bit stream is callback at `+0`, state at `+4`, `size_t
bytes_left` at `+8`, and error pointer at `+12`, total 16 bytes. Callback
streams and runtime errors are enabled: `PB_BUFFER_ONLY` and `PB_NO_ERRMSG`
remain undefined.

`buf_read` uses AAPCS arguments `r0` stream, `r1` nullable destination, and
`r2` count and returns Boolean success in `r0`. It captures the old state,
advances state by the exact count, copies only for a non-null destination, and
does not alter `bytes_left` or `errmsg`. Its one retained executable seam is
the ignored-return void-EABI `__aeabi_memcpy` entry `0x00439BE4`. The complete
166-byte provider `[0x00439BE4,0x00439C8A)` hashes to
`8e696e1fb54917a436f850e562f74e8cc8734c259fdaac9f767a3c264ff427cd`.

`pb_readbyte` accepts stream in `r0`, a required one-byte destination in `r1`,
and returns Boolean status in `r0`. Zero budget reports the first
`end-of-stream` error without calling the callback. Otherwise it invokes the
stream callback with count one; failure reports the first `io error` without
decrementing the budget, while success decrements the callback's current
`bytes_left` value exactly once.

The production source retains the existing strings as unresolved data seams:

| Seam | Runtime address | NUL bytes | SHA-256 |
|---|---:|---:|---|
| `end-of-stream` | `0x00787C70` | 14 | `e167d4f2ec31a2197c7bc32affd9865ac8609d7dae984d0916e01f044fcc67b4` |
| `io error` | `0x0078B690` | 9 | `3faaf40b4ee3e3b23823ed9851dc77bf6fc2d7c7c330240eeaed08bd9d084ec1` |

Retaining these addresses preserves error-pointer identity across the already
promoted `pb_read` and opaque nanopb providers.

## Host and target qualification

The host fixture differentially exercises the private buffer callback through
upstream `pb_istream_from_buffer().callback`, and exercises the private
read-byte contract through a one-byte upstream `pb_decode_varint` call. It
covers copying, null-destination skipping, state advancement, unchanged
budget/error fields, successful callback reads, zero budget, callback failure,
sticky preexisting errors, callback budget mutation, and the atomic
buffer-callback-to-read-byte path.

Apple clang 21.0.0 (`clang-2100.3.27.1`) produces deterministic, separate ELF
objects. The buffer object is 912 bytes with SHA-256
`fd491e856b03fcfb47646c0cd56e0ad2ebb017b2a64a67b52fcefb8b26a226b2`;
the read-byte object is 1,032 bytes with SHA-256
`354a05cf1decc66a7a12f31f08fe28dd5cec2744a3e75f22f83e957e38991e69`.
Together they contain exactly two executable production sections and no
allocated source-owned data:

| Section | Bytes | SHA-256 | Relocation closure |
|---|---:|---|---|
| `.text.open_cfw_nanopb_buf_read` | 30 | `db26e5bd51f3d313907af94bfe545cc9962b867ed18285f2025c401e8613700a` | one `R_ARM_THM_CALL` to the copy seam at offset 18 |
| `.text.open_cfw_nanopb_readbyte` | 64 | `eda66d0ae6274a2078b6eceaefc0e773169d5e15b26bce650a8d48b818e4f2b8` | MOVW/MOVT pairs to the two stock strings at offsets 32/36 and 50/54 |

The undefined-symbol set is exactly the copy seam and two string seams. Each
function has only its normal relocation-free `.ARM.exidx` cant-unwind record.
The focused gate compiles every object twice and requires byte-for-byte
reproduction. The authoritative profile placements are:

| Profile/function | Overlay offset | Runtime address | Relocated SHA-256 |
|---|---:|---:|---|
| Apple `open_cfw_nanopb_buf_read` | 124800 | `0x007B2AA4` | `f312e087cf1fbecf19bd5fa0052d3a63ca91287c811de169aaf2a09322e0115e` |
| Apple `open_cfw_nanopb_readbyte` | 124832 | `0x007B2AC4` | `f3395a19a7406016e6b1f1daf14969dee91ccde4e9a98ba4eeaba0016e131871` |
| exact-root Linux `open_cfw_nanopb_buf_read` | 126624 | `0x007B31C4` | `a6b4d3a4e969f078683f1cde3a4043b70d8495d577f550ae35c6c2789ff470de` |
| exact-root Linux `open_cfw_nanopb_readbyte` | 126656 | `0x007B31E4` | `f3395a19a7406016e6b1f1daf14969dee91ccde4e9a98ba4eeaba0016e131871` |

The buffer patch hashes to
`7b95b1a632ce6362c74c2a3f3ae2e9ef15f5abb6800d1dd8ca1dd4586b4f73ac`;
the read-byte patch hashes to
`ed8460907148368a780a57a2abab8bb48cc80a78b980c38b0097e1b81ce1967e`.
At the read-pair milestone, the resulting Apple overlay was 124,896 bytes with
SHA-256
`341c1d641ae5ffa21ff2af55e1cbebae7353c3073595e9fe9170a647bcdcf543c`,
and the assembled Apollo-main component was 3,648,292 bytes with SHA-256
`355207d6be95cc718be02194ea432e779c6f23c7a448f080abba91aa85c01e8e`.

Exact-root Linux clang produces the same unrelocated section bytes and
relocation sets. Its buffer patch is `23f30ebf` plus eleven Thumb NOPs and
hashes to
`db7d0da006d031b33b6858a4b829d68403c9039f66d2ac4db576b00bdef94bec`;
its read-byte patch is `23f3c6be` plus thirty-four Thumb NOPs and hashes to
`b571a49431ddbdd7c71059acf67da1227af1eecba58b09fafea45177eda87fd0`.
The exact-root Linux aggregate pins are:

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| Apollo-main overlay | 126,720 | `0d0acba33cfd65e5b250e741b8e7d23f3af1e5959f8139bc7e614eb903f93cb9` |
| Apollo-main component | 3,650,116 | `99735e753f0b58c8db469bc15e92a87b446e7af917e13284e05f8c4538a2c25c` |
| core-source package | 4,428,610 | `ddf524c5c614be4ab627bfc17466df5bb99ae14efa98f38f0686192bb6a29ba0` |
| flash plan | 602,651 | `36e79b882a4637091ac922ee1a94f542a26425bb418273b495a0f2190c4647a8` |

Those Linux aggregate pins describe the read-pair milestone and are superseded
by the subsequent stream-constructor promotion; its Linux aggregate recording
is tracked separately. The read-pair plan closed 844 placed regions with two
unresolved regions.

## Bootloader exclusion

The authenticated 148,599-byte bootloader hashes to
`f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5`.
It contains neither complete stock helper, the constructor, their reviewed
characteristic instruction probes, nor any of the three nanopb error strings.
No authenticated bootloader homolog is claimed; the production scope is
Apollo-main only.

## Promotion boundary

At the read-pair milestone both reviewed profiles completed this bounded
production promotion: the source leaves were appended, relocated under strict
closure, and reached through full-span stock-entry patches. The constructor
was still binary-backed at that historical boundary; it is source-owned by the
subsequent promotion documented in
`nanopb-istream-from-buffer-source-audit.md`. The retained copy-library and
error-string seams remain binary-backed by design. No firmware was signed,
flashed, or executed on hardware.
