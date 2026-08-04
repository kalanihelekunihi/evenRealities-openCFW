# nanopb `pb_decode_fixed32` source-replacement audit

Status: **scoped GO for the authenticated 28-byte `pb_decode_fixed32` source
leaf closed over source-owned `pb_read`; NO-GO for hardware flashing or a
broader nanopb source-ownership claim**.

This audit qualifies the Zlib-licensed
`open_cfw_nanopb_decode_fixed32` adaptation against the official G2 2.2.6.10
Apollo image and the authenticated nanopb compatibility snapshot. The leaf is
small and closed: it has one direct caller, one outgoing provider call, no
observed alternate or interior ingress, no data closure, and one target-object
relocation.

The conclusion is deliberately narrow. Production redirects the original
entry to appended source-compiled text and calls source-owned `pb_read` through
its stable entry trampoline at `0x0048F3BE`. The succeeding read promotion
retains only private `buf_read` identity and two error strings as binary seams.
This audit does not identify the vendor's exact nanopb point release, qualify
the remainder of nanopb, sign an image, or authorize flashing a device.

## Decision boundary

The replacement is suitable for promotion because:

- the exact stock body, immediate boundary windows, sole caller, and sole
  provider are pinned against the official OTA;
- whole-application scans find the one expected direct BL to the entry and no
  tested branch or stored-pointer ingress to the interior;
- the selected upstream definition is authenticated at nanopb 0.4.9 and is
  byte-identical in the official 0.4.7 and 0.4.8 releases;
- the altered leaf preserves destination-on-failure behavior and produces the
  protobuf little-endian fixed32 value explicitly;
- 1,004 directed and randomized cases match the actual pristine upstream
  definition under the recovered G2 option contract; and
- the Thumb target object has one function text section, one undefined read
  seam, and exactly one `R_ARM_THM_CALL` relocation, with no allocated data or
  rodata.

Promotion remains conditional on the normal overlay, manifest, aggregate, and
historical-replay gates. This audit records the leaf and patch contract; it does
not claim an already-built production aggregate or hardware result.

## Authenticated inputs

| Input | Bytes | SHA-256 |
|---|---:|---|
| official G2 2.2.6.10 OTA package | 3,523,396 | `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863` |
| installed Apollo application at `0x00438000` | 3,523,364 | `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701` |
| authenticated nanopb 0.4.9 `pb_decode.c` | 53,845 | `e980f2a41d9abe37b7e6fb4c9ba1ebfd68507a6fd2653f8d755e1947a9c84b1a` |
| recovered G2 nanopb option contract | 1,551 | `ae758999d239e49e2d5c5bf6de3f4aef3aab5cd3c29d8de65c4db301c62899db` |

The OTA contains a 32-byte package preamble. Runtime address
`0x00490190` therefore maps to installed-application offset `0x58190` and OTA
file offset `0x581B0` (decimal 360,880).

The selected official `nanopb-0.4.9` annotated tag resolves to commit
`98bf4db69897b53434f3d0ba72e0a3ab1a902824` and tree
`2c4c260bcff3f9f7081238d377274dd385d76582`. The vendored snapshot verifies
the tag, commit, tree membership, exact file blobs, and complete Zlib license
offline. The tag and commit are unsigned, so Git object integrity is proven but
signer identity is not.

## Authenticated upstream compatibility

The exact pristine definition records are:

| Release | Commit | `pb_decode.c` definition bytes | Definition SHA-256 |
|---|---|---:|---|
| 0.4.7 | `b97aa657a706d3ba4a9a6ccca7043c9d6fe41cba` | `[43124,43742)`, 618 bytes | `1952ee1f743334c82f206c910392f63b2e7fdd702cbdd404dae04367aa8ae518` |
| 0.4.8 | `6cfe48d6f1593f8fa5c0f90437f5e6522587745e` | `[43124,43742)`, 618 bytes | `1952ee1f743334c82f206c910392f63b2e7fdd702cbdd404dae04367aa8ae518` |
| 0.4.9 | `98bf4db69897b53434f3d0ba72e0a3ab1a902824` | `[43210,43828)`, 618 bytes | `1952ee1f743334c82f206c910392f63b2e7fdd702cbdd404dae04367aa8ae518` |

The 0.4.7 and 0.4.8 `pb_decode.c` files are themselves byte-identical and hash
to `9ed9e255e433324fc28557adb03bf494a3711c2a0480c97b3690a6871ce29c66`.
The 0.4.9 file differs elsewhere, but its complete `pb_decode_fixed32`
definition is identical. The definition reads four bytes to a local union,
returns false before touching the destination if the read fails, and stores the
decoded value only after success.

This proves exact pristine-source compatibility across 0.4.7 through 0.4.9.
It does **not** prove which release, checkout, or vendor-modified derivative
Even Realities used.

## Stock boundary and semantics

The official stock body is `[0x00490190,0x004901AC)`, 28 bytes:

```text
1cb50c0004226946fff711f9002801d1002002e000982060012016bd
```

Its SHA-256 is
`1ee27599a8ac5b8d2a0cbaac59986fb49be7b24c348a960a216b8cbbecce5bf3`.
Its instruction-level behavior is:

1. preserve the destination pointer and allocate a four-byte stack temporary;
2. call `pb_read(stream, temporary, 4)`;
3. return false immediately when the provider returns false; and
4. otherwise load the temporary word, store it to the destination, and return
   true.

The direct word load and store establish the little-endian fast-path behavior
used by the G2 build. A failed provider can mutate stream state or partially
write the local temporary, but the destination remains unchanged.

The exact boundary witness windows are:

| Boundary witness | Span | Bytes | SHA-256 |
|---|---|---:|---|
| predecessor tail | `[0x00490180,0x00490190)` | 16 | `afa606ddde93a21b59394932fc95e7cb628978dc62bfa49c337b750c80cfa813` |
| fixed32 leaf | `[0x00490190,0x004901AC)` | 28 | `1ee27599a8ac5b8d2a0cbaac59986fb49be7b24c348a960a216b8cbbecce5bf3` |
| successor head | `[0x004901AC,0x004901C4)` | 24 | `8ec2f1b9165e3c501eb931ba6ee6180a6733ddf61760423a60fef54b260710f9` |

These windows independently pin the return boundary before the leaf and the
start of the following fixed64 decoder. They are boundary witnesses, not a
claim that the partial predecessor/successor windows are their complete
function bodies.

## Caller and whole-image ingress closure

Exactly one external direct call targets the stock entry:

| Caller owner | Owner span | Owner SHA-256 | Call site | Encoding |
|---|---|---|---|---|
| `decode_basic_field` | `[0x0048F7F4,0x0048F968)`, 372 bytes | `2b1bf389327c0f6ccde636bbb51e36cd0bab3eccc811db9aa0efd3dbfef9e445` | `0x0048F89C` | `00f078fc` |

The decoded target of that BL is exactly `0x00490190`. A complete installed-
application scan checks wide BL, wide `B.W`, wide conditional branches, narrow
`B`/`Bcc`, `CBZ`/`CBNZ`, and byte-aligned stored even or Thumb pointers. The
narrow scan includes the application's final halfword. Results are:

- one BL to the function entry, at `0x0048F89C`;
- no `B.W` target into the span;
- no external wide-conditional or narrow target into the span;
- no external entry at an interior halfword; and
- no stored even or Thumb pointer into the span.

This is a closed result for the decoded ingress classes. It is not a universal
data-flow proof and does not independently exclude an address synthesized by an
unrecognized multi-instruction sequence. The single known caller and lack of
interior ingress make an entry-only branch patch appropriate without editing
the caller.

## Retained provider closure

The stock leaf contains one outgoing call:

| Call site | Stock offset | Encoding | Provider |
|---|---:|---|---|
| `0x00490198` | `+8` | `fff711f9` | `pb_read` at `0x0048F3BE` |

The provider occupies `[0x0048F3BE,0x0048F454)`, is 150 bytes, and hashes to
`69aecb900c749fd98bd2d05e2229e9a3d6829bd36f3e393f624e3579a9b4af7f`.
That exact body was already reviewed as the callback-stream provider used by
other nanopb source leaves.

The replacement deliberately leaves `open_cfw_nanopb_read` undefined in its
object. Production relocation must bind only that symbol to the authenticated
stock entry `0x0048F3BE`. This retains provider behavior, including bounds
checks, callback errors, stream accounting, and first-error preservation. It
also means this promotion does not make the read path fully source-owned.

## Recovered ABI and configuration assumptions

The shared recovered `pb_istream_t` compatibility layout is:

| Offset | Field | G2 representation |
|---:|---|---|
| `+0` | callback | 4-byte function pointer |
| `+4` | state | 4-byte `void *` |
| `+8` | `bytes_left` | 4-byte `size_t` |
| `+12` | `errmsg` | 4-byte `const char *` |

The structure is 16 bytes. `bool` and `pb_byte_t` are one byte, pointers and
`size_t` are 32 bits, and the target is an 8-bit-byte little-endian ARM Thumb
environment. The leaf itself treats the stream as opaque; the layout matters
at the source-owned `pb_read` ABI boundary.

The surrounding recovered nanopb contract has:

- `PB_ENABLE_MALLOC`, `PB_FIELD_32BIT`, `PB_WITHOUT_64BIT`,
  `PB_CONVERT_DOUBLE_FLOAT`, `PB_VALIDATE_UTF8`, `PB_BUFFER_ONLY`,
  `PB_NO_ERRMSG`, `PB_NO_PACKED_STRUCTS`, and
  `PB_ENCODE_ARRAYS_UNPACKED` undefined;
- default 16-bit `pb_size_t`, 64-bit scalar support, and native 64-bit double;
- callback streams and runtime error strings enabled;
- packed structures and packed repeated-scalar encoding enabled; and
- `PB_MAX_REQUIRED_FIELDS == 64`.

Only the callback-stream, error, byte-width, word-width, and endian portions
are exercised directly by this leaf. The candidate explicitly assembles

```text
byte[0] | byte[1] << 8 | byte[2] << 16 | byte[3] << 24
```

before the single successful destination store. It uses no `memcpy`, AEABI
helper, allocator, global state, or hardware interface. As in pristine
nanopb, `destination` must be a valid suitably aligned writable `uint32_t`
object; no new null or alignment check is introduced.

## Differential oracle

The host oracle compiles the actual authenticated pristine
`pb_decode_fixed32` definition from the vendored 0.4.9 `pb_decode.c`, with the
recovered G2 option header, alongside the altered candidate. Both executions
receive equivalent callback-stream state and provider outcomes.

The gate covers four directed cases and 1,000 deterministic randomized cases,
1,004 total. Inputs vary payload length and bytes, declared `bytes_left`, an
injected provider failure, preexisting error state, and the initial destination
word. It compares Boolean status, destination, remaining count, consumed input,
provider calls, and error classification. All 1,004 cases match. Every false
result additionally asserts that the initial destination is unchanged.

This is a source-level semantic differential against the real pristine
definition, not a handwritten model. The harness may use host-library helpers
to supply bytes; the target leaf itself has no such dependency.

## Source and target-object closure

| File | Bytes | SHA-256 |
|---|---:|---|
| `components/shared/nanopb/runtime_nanopb_decode_fixed32.c` | 1,975 | `fefd8a899174fb9332c366df691dc2c8ec6f4792f3fd464b65dbb573ace8ee19` |
| `components/shared/nanopb/runtime_nanopb_decode_fixed32.h` | 1,750 | `738e4c7d4ea983b0ba967fa42cdcc61cb2e20837531bc6176b7f95a5fe8e2460` |

The reviewed Thumbv7E-M build uses freestanding `-O2`, Thumb mode,
function/data sections, read-only position independence, no builtins, no
unaligned-access assumption, no unwind tables, and `-fno-ident`. Compile-twice
qualification produces the same 960-byte ELF object:

`499f6ec335b62a6af9a4f2370aaa5ef831a5ec2b3e8da99bcb6f7b8a4e83fedd`

The four-byte-aligned function text is 50 bytes:

```text
b0b582b00d4601a90422fff7feff70b19df804109df805209df806309df8074041ea022141ea034141ea0461296002b0b0bd
```

Its SHA-256 is
`798f8f7cbed57f6ba11dad46a6de9d25cb1f1710eb4fa904d79b6fe449952a04`.
The strict text relocation contract is exactly:

| Offset | ELF relocation | Symbol |
|---:|---|---|
| 10 | `R_ARM_THM_CALL` (type 10) | `open_cfw_nanopb_read` |

`open_cfw_nanopb_read` is the sole undefined runtime symbol. The only
nonempty allocated sections are the 50-byte function text and its eight-byte
CANTUNWIND `.ARM.exidx` metadata record; extraction discards the metadata.
There is no allocated data, BSS, rodata, literal string, `memcpy`, or AEABI
closure.

The exact object and text pins above were reproduced with the reviewed Apple
Clang 21 profile. A separate Linux compiler-profile object pin was not
available in this audit environment and remains an aggregate-integration
qualification rather than an inferred identity claim.

## Production patch strategy

Promotion should use the established relocated-leaf mechanism:

1. authenticate the original 28 bytes and their SHA-256 before mutation;
2. append the 50-byte, four-byte-aligned source leaf to the profile's Apollo
   overlay;
3. relocate its sole call seam to source-owned `pb_read` through the stable
   entry trampoline at `0x0048F3BE`;
4. replace the original entry with one profile-specific four-byte Thumb
   `B.W` to the appended leaf; and
5. overwrite the remaining 24 stock bytes with twelve Thumb NOPs (`00bf`), so
   no stale stock tail remains executable.

The resulting replacement span remains exactly 28 bytes: four branch bytes
plus 24 bytes of padding. The caller at `0x0048F89C` remains unchanged and
continues to enter `0x00490190`; there are no call-site rewrites. Each compiler
profile must independently pin its appended placement, relocated call bytes,
entry branch encoding, 28-byte patch hash, aggregate overlay, component,
manifest ownership, package, and flash-plan artifacts. Historical rollback
must restore all 28 authenticated stock bytes.

## Limitations and explicit GO/NO-GO

Scoped **GO**:

- promote only `pb_decode_fixed32` using the authenticated entry patch and
  source leaf described here;
- bind the single read seam to the authenticated source-owned `pb_read`
  trampoline at `0x0048F3BE`; and
- require the normal production and per-profile aggregate gates before
  accepting built artifacts.

Explicit **NO-GO**:

- no claim that private `buf_read`, the two retained error strings, or the
  broader nanopb decoder is source-owned;
- no claim that Even Realities used nanopb 0.4.9, rather than another member
  of the compatible 0.4.7–0.4.9 range or a vendor derivative;
- no extrapolation from the tested branch classes to a universal dynamic
  control-flow proof;
- no acceptance of an unpinned compiler profile, relocation, placement,
  patch, or aggregate artifact; and
- no signing, flashing, booting, or hardware-safety authorization.

All evidence in this audit is offline source authentication, disassembly,
whole-image scanning, host differential execution, and target-object
inspection. No G2 hardware was operated.
