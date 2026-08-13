# nanopb `pb_read` production-source audit

Status: bounded Apollo-main production source leaf with three retained stock
identity/data seams; no signing, flashing, or on-device claim.

Scope: official G2 `2.2.6.10` Apollo-main image, pristine nanopb 0.4.7–0.4.9,
the recovered `pb_istream_t` ABI, callback/error/accounting behavior, complete
entry and interior-ingress topology, Apple/Linux target profiles, and the
focused host/ARM qualification harness.

## Result

The 150-byte function at `[0x0048F3BE,0x0048F454)` implements the pristine
nanopb 0.4.7–0.4.9 `pb_read()` contract under the recovered G2 options:
callback streams are enabled, runtime error strings are enabled, and
`size_t`/pointers are 32 bits. The upstream definition is byte-identical in
all three surviving point releases. Its post-callback saturating accounting
is the already-authenticated discriminator that excludes pristine nanopb
0.4.6 and earlier.

This evidence supports the bounded, uniquely named production source leaf:

- `components/shared/nanopb/runtime_nanopb_read.c`; and
- `components/shared/nanopb/runtime_nanopb_read.h`.

The Apollo-main overlay redirects the complete 150-byte stock entry to
`open_cfw_nanopb_read`. The leaf retains nanopb's private buffer callback
identity as `open_cfw_nanopb_stock_buffer_read_identity`, bound to the reviewed
stock Thumb entry `0x0048F3A5`, plus the two reviewed stock error strings. This
preserves the upstream fast path for `pb_read(stream, NULL, count)` while
keeping all three binary-owned dependencies explicit and relocatable.

## Content-addressed upstream authority

The official nanopb repository is `https://github.com/nanopb/nanopb.git` and
the applicable code is Zlib licensed. The three annotated release tags are
unsigned, so this is content-addressed source authentication rather than a
cryptographic publisher-signature claim.

| Release | Annotated tag object | Commit | Tree | `pb_decode.c` bytes / SHA-256 |
|---|---|---|---|---|
| `nanopb-0.4.7` | `8b90300e154d7130c72ae6d4e74dd24ef6d45b5a` | `b97aa657a706d3ba4a9a6ccca7043c9d6fe41cba` | `2eb286236013d6d82f12383aa0e6fa316a78172e` | 53,759 / `9ed9e255e433324fc28557adb03bf494a3711c2a0480c97b3690a6871ce29c66` |
| `nanopb-0.4.8` | `9d6ee41c1edcab0f689430cbbde3bba0414d501c` | `6cfe48d6f1593f8fa5c0f90437f5e6522587745e` | `0197a003666f5fd44eb73d565aabe24ef8e11543` | 53,759 / `9ed9e255e433324fc28557adb03bf494a3711c2a0480c97b3690a6871ce29c66` |
| `nanopb-0.4.9` | `b3056c326da0e6cf702fd13ae2fe63225caa0801` | `98bf4db69897b53434f3d0ba72e0a3ab1a902824` | `2c4c260bcff3f9f7081238d377274dd385d76582` | 53,845 / `e980f2a41d9abe37b7e6fb4c9ba1ebfd68507a6fd2653f8d755e1947a9c84b1a` |

OpenCFW selects 0.4.9 as its compatibility baseline; this does not prove the
vendor's exact historical point release. The repository's offline snapshot
and verifier already pin the selected tag, commit, tree, file identities, and
license.

### Exact `pb_read()` definitions

Definitions were extracted from the first byte of
`bool checkreturn pb_read(...)` through the matching closing brace, without
normalizing whitespace or line endings.

| Release | Exact byte span in `pb_decode.c` | Length | Definition SHA-256 |
|---|---:|---:|---|
| 0.4.7 | `[3659,4473)` | 814 | `3b69f6f4eb56a87c3f8a7f9ac30ac7573328c560047cbc5b2295daceef18fb1c` |
| 0.4.8 | `[3659,4473)` | 814 | `3b69f6f4eb56a87c3f8a7f9ac30ac7573328c560047cbc5b2295daceef18fb1c` |
| 0.4.9 | `[3745,4559)` | 814 | `3b69f6f4eb56a87c3f8a7f9ac30ac7573328c560047cbc5b2295daceef18fb1c` |

The corresponding private `buf_read()` definitions are also byte-identical:
322 bytes with SHA-256
`34b5a0a938c4cbfe431c24afc0a8f273879eef4ee4853282d4c44708f27f4867`.
Their spans are `[3335,3657)` for 0.4.7/0.4.8 and `[3421,3743)` for 0.4.9.

## Recovered option and ABI contract

The authenticated G2 runtime evidence requires `PB_BUFFER_ONLY` and
`PB_NO_ERRMSG` to remain undefined. Consequently, the operative upstream
stream fields are:

| Offset | 32-bit field | Stock evidence |
|---:|---|---|
| `+0` | callback pointer | loaded for identity comparison at `0x0048F3D2` and indirect call at `0x0048F420` |
| `+4` | callback state | loaded, advanced, and stored by stock `buf_read()` at `0x0048F3A8–0x0048F3AE` |
| `+8` | `size_t bytes_left` | checked before the callback and reloaded after it |
| `+12` | `const char *errmsg` | loaded/preserved/stored by both error paths |

This yields the recovered 16-byte target layout:

```c
struct pb_istream_s {
    bool (*callback)(pb_istream_t *, uint8_t *, size_t);
    void *state;
    size_t bytes_left;
    const char *errmsg;
};
```

The production header pins all four offsets and the 16-byte total with target
static assertions. The 0.4.7 and 0.4.8 upstream struct definitions occupy
`pb_decode.h` bytes `[954,1464)`, 510 bytes, SHA-256
`7abc5f91bea7dfe8fb53754fac314a23904e8feaef96fdacf17349d354cb10a8`.
Nanopb 0.4.9 expands comments around the same operative fields; its exact
definition is `[954,1956)`, 1,002 bytes, SHA-256
`901e5ab799a9a0d5af3f82029dd399d5b2297d1d85e508f658af516eca03da99`.

## Stock implementation evidence

The official Apollo-main image is 3,523,396 bytes and hashes to
`36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`.

| Provider | Range | Bytes | SHA-256 |
|---|---|---:|---|
| private `buf_read()` | `[0x0048F3A4,0x0048F3BE)` | 26 | `9d6c6690294b82bbafba82ec0f63a6bb5b78e4146543db3a30fac92469ace723` |
| public `pb_read()` | `[0x0048F3BE,0x0048F454)` | 150 | `69aecb900c749fd98bd2d05e2229e9a3d6829bd36f3e393f624e3579a9b4af7f` |

The literal load at `0x0048F3D4` reads the Thumb pointer `0x0048F3A5` from
`0x0048FC78`, proving the private-buffer callback identity comparison. The
error literal pointers resolve to:

| Error | Address | NUL-terminated bytes | SHA-256 |
|---|---:|---:|---|
| `end-of-stream` | `0x00787C70` | 14 | `e167d4f2ec31a2197c7bc32affd9865ac8609d7dae984d0916e01f044fcc67b4` |
| `io error` | `0x0078B690` | 9 | `3faaf40b4ee3e3b23823ed9851dc77bf6fc2d7c7c330240eeaed08bd9d084ec1` |

Whole-image Thumb-2 direct-call decoding finds 15 calls to `0x0048F3BE`.
Two at `0x0048F3EA` and `0x0048F3FC` are the function's own skip recursion;
the 13 external direct callers are at `0x0048F632`, `0x0048F666`,
`0x0048F6C0`, `0x0048F6D0`, `0x0048F71A`, `0x0048F754`, `0x0048F764`,
`0x0048F7DC`, `0x00490198`, `0x004901B4`, `0x004903E4`, `0x00490478`, and
`0x004905A2`. Exhaustive aligned Thumb-2 BL/B.W/conditional and narrow-branch
scans find no external branch to the 146-byte interior. A bytewise 32-bit
pointer scan finds no stored pointer into the entry or interior. Redirecting
the entry therefore covers every authenticated ingress while preserving all
13 external call sites at their stable ABI address. The one raw narrow-decoder
hit at `0x0048F39C` is the low halfword of aligned literal-pool word
`0x0075B9E8`, not executable code or ingress.

## Behavioral equivalence boundary

The production source leaf preserves these upstream and stock behaviors:

1. A zero count succeeds before inspecting the callback, buffer, bounds, or
   error state.
2. A `NULL` destination with a non-buffer callback is consumed through a
   16-byte temporary in 16-byte recursive chunks plus one final chunk.
3. A `NULL` destination with the private buffer callback takes the direct
   callback path, so buffer-backed state advances without a temporary copy.
4. The pre-callback bounds check fails with `end-of-stream` and never calls
   the callback.
5. Callback failure preserves `bytes_left` and reports `io error`.
6. Error assignment is first-error-wins: an existing non-NULL `errmsg` is
   never overwritten.
7. Successful post-callback accounting reloads `bytes_left`, because a
   callback may have changed it; the result is clamped to zero when smaller
   than the requested count, otherwise the exact count is subtracted.
8. A failure in a later recursive skip retains the bytes already consumed by
   earlier successful chunks.

No callback-null defensive behavior is added for a nonzero read; pristine
nanopb and the stock G2 provider both require a valid callback.

## Production source and target contracts

| File | Bytes | SHA-256 |
|---|---:|---|
| `runtime_nanopb_read.c` | 2,874 | `65f8f3cb92729e98f82f1254b18ba969cdd8a57c7ac74e8713137b5585102453` |
| `runtime_nanopb_read.h` | 2,059 | `aaa9847151722953498958687e91d55dc0b18cc9a60318b4f754110c66a443d6` |

Apple Clang 21.0.0 (`clang-2100.3.27.1`) produces a 1,192-byte ELF object
with SHA-256
`fafc2e4ec4081c523f87f1eda3ff87d9cc207119ec4f4ca77910bb08ccae0f0d`.
The selected `.text.open_cfw_nanopb_read` section is 158 bytes, aligned to
four bytes, and hashes before relocation to
`06def086733fd9801b712161943b0da64e3b2bdf82e6f5962ee9207c738c00b1`.
The reviewed Linux Clang 22.1.8 profile emits the same 158 unrelocated bytes.

The object has exactly six selected text relocations and three undefined
runtime symbols:

| Offset | Type | Symbol | Fixed target |
|---:|---|---|---:|
| `0x1C` | `R_ARM_THM_MOVW_ABS_NC` | `open_cfw_nanopb_end_of_stream_error` | `0x00787C70` |
| `0x20` | `R_ARM_THM_MOVT_ABS` | `open_cfw_nanopb_end_of_stream_error` | `0x00787C70` |
| `0x42` | `R_ARM_THM_MOVW_ABS_NC` | `open_cfw_nanopb_stock_buffer_read_identity` | `0x0048F3A5` |
| `0x46` | `R_ARM_THM_MOVT_ABS` | `open_cfw_nanopb_stock_buffer_read_identity` | `0x0048F3A5` |
| `0x86` | `R_ARM_THM_MOVW_ABS_NC` | `open_cfw_nanopb_io_error` | `0x0078B690` |
| `0x8A` | `R_ARM_THM_MOVT_ABS` | `open_cfw_nanopb_io_error` | `0x0078B690` |

The identity pair deliberately resolves to the odd Thumb function pointer
`0x0048F3A5`, not merely the even code address `0x0048F3A4`. No private error
string is compiled into the overlay; both strings remain authenticated stock
data seams. After applying all six relocations, both profiles produce the
same 158-byte leaf with SHA-256
`8b3de44a2cf7ca2e07715c913db0fa454ef65cbc453366190b12736e455aa7a8`.

| Profile | Overlay offset | Runtime address | Entry B.W | 150-byte entry patch SHA-256 |
|---|---:|---:|---|---|
| Apple Clang 21.0.0 | 124,640 | `0x007B2A04` | `23f321bb` | `c2c44419ee24c41c8d0e8bc7f04689bb7f1c18b1f7ec3d7304e04c37579938a1` |
| Linux Clang 22.1.8 | 126,464 | `0x007B3124` | `23f3b1be` | `4dc433588344c12d1a0abfab8c5f1673c24f6702d8f285f67fb0fd8b8e6e3eab` |

Each patch is its four-byte profile-specific B.W followed by 73 Thumb NOPs,
covering the complete reviewed stock span. Independent branch decoding
recovers the exact profile leaf address.

## Bootloader exclusion

No authenticated bootloader homolog was found. The official 148,599-byte
bootloader hashes to
`f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5`.
It contains neither the complete stock `pb_read` body nor the private
`buf_read` body, and contains neither NUL-terminated nanopb runtime error
string. The production replacement is therefore intentionally Apollo-main
only.

## Focused qualification

Run the fail-closed source/provenance gate and focused production tests with:

```sh
python3 third_party/nanopb/verify_snapshot.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v \
  tests.test_runtime_nanopb_read
```

The focused harness authenticates the local upstream definition, all three
retained stock seams, all 13 external callers, the absence of interior and
stored-pointer ingress, and the bootloader exclusion. It executes the eight
boundary/error/callback cases on the host, compiles the production target
object, verifies its six-relocation closure, regenerates both entry patches,
and checks the production overlay and provenance contracts.

The remaining binary-owned nanopb dependencies are explicit rather than
hidden: private `buf_read` identity and the two error strings. Promoting
`buf_read` later requires reviewing every buffer-stream constructor so pointer
identity remains coherent. The current evidence does not authorize signing or
flashing, and it does not claim on-device validation. No firmware was signed
or flashed during this audit.
