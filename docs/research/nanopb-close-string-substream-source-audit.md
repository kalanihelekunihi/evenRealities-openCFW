# nanopb `pb_close_string_substream` production source audit

Status: **production promoted; scoped GO for the audited Apollo-main source
replacement and its recorded Apple/Linux aggregate artifacts**.

The official G2 function at `[0x0048F7CA,0x0048F7F4)` is now replaced in
production by the Zlib-licensed
`open_cfw_nanopb_close_string_substream` source leaf. The 42-byte stock span
is authenticated before patching, then replaced by one profile-specific
`B.W` and nineteen Thumb NOPs. The relocated 36-byte leaf retains exactly one
reviewed ABI dependency: source-owned `pb_read` through its stable entry
trampoline at `0x0048F3BE`.

The focused production, nanopb snapshot, aggregate verification, historical
rollback, exact-root Linux replay, and full core-overlay gates all pass. This
is a GO for the bounded promotion and its recorded Apple/Linux artifacts. All
work described here was offline source review, compilation, binary analysis,
overlay assembly, and package construction. No image was signed or flashed
and no G2 hardware was operated.

## Decision and attribution boundary

Promotion is justified by a closed, fail-fast boundary:

- the exact upstream function definition is identical in authenticated
  nanopb 0.4.7, 0.4.8, and 0.4.9 source;
- the 42-byte G2 body, its two adjacent functions, all three direct callers,
  and its sole outgoing provider are independently pinned;
- whole-application scans find exactly the three expected direct calls to the
  stock entry and no tested alternate or interior ingress;
- the altered source preserves the recovered 16-byte callback-stream ABI and
  all success/failure state-transfer semantics;
- the target object has one code relocation and one undefined provider, with
  no local rodata or writable data;
- both reviewed compiler profiles have exact text, placement, patch, overlay,
  component, package, and flash-plan pins; and
- the canonical manifest exactly tiles the Apple Apollo-main component and
  records the resulting source/generated/opaque ownership change.

The selected source baseline is official nanopb 0.4.9. That is an openCFW
compatibility choice inside the authenticated pristine 0.4.7–0.4.9 range. It
is **not** proof that Even Realities used nanopb 0.4.9, any other exact point
release, or the selected Git checkout. The broader pristine `pb_common.c`,
`pb_decode.c`, and `pb_encode.c` translation units remain production-
unregistered.

## Authenticated inputs and upstream source

| Input | Bytes | SHA-256 |
|---|---:|---|
| official G2 2.2.6.10 OTA package | 3,523,396 | `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863` |
| installed Apollo application at `0x00438000` | 3,523,364 | `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701` |
| authenticated nanopb `pb_decode.c` | 53,845 | `e980f2a41d9abe37b7e6fb4c9ba1ebfd68507a6fd2653f8d755e1947a9c84b1a` |
| recovered G2 nanopb option contract | 1,551 | `ae758999d239e49e2d5c5bf6de3f4aef3aab5cd3c29d8de65c4db301c62899db` |

The OTA has a 32-byte package preamble. Therefore the stock function starts
at installed-application offset `0x577CA` and OTA file offset `0x577EA`.

The selected official `nanopb-0.4.9` record is the unsigned annotated tag
object `b3056c326da0e6cf702fd13ae2fe63225caa0801`, resolving to commit
`98bf4db69897b53434f3d0ba72e0a3ab1a902824` and tree
`2c4c260bcff3f9f7081238d377274dd385d76582`. The selected `pb_decode.c` Git
blob is `068306a05339af05b3b3fb80894746ed9a077bf8`. Git object integrity and path
membership are authenticated offline; neither the tag nor commit has a
verified signer identity. The complete upstream Zlib license is retained.

The authenticated point-release records are:

| Release | Commit | Tree | Exact definition span |
|---|---|---|---|
| 0.4.7 | `b97aa657a706d3ba4a9a6ccca7043c9d6fe41cba` | `2eb286236013d6d82f12383aa0e6fa316a78172e` | bytes `[11137,11482)`, lines 376–389 |
| 0.4.8 | `6cfe48d6f1593f8fa5c0f90437f5e6522587745e` | `0197a003666f5fd44eb73d565aabe24ef8e11543` | bytes `[11137,11482)`, lines 376–389 |
| 0.4.9 | `98bf4db69897b53434f3d0ba72e0a3ab1a902824` | `2c4c260bcff3f9f7081238d377274dd385d76582` | bytes `[11223,11568)`, lines 377–390 |

In all three releases, the exact 345-byte `pb_close_string_substream`
definition hashes to
`527e5ca208a04366c0911baf793af7dc7045fd73014eefc6e31ce3a8b6dc332f`.
Controlled whole-runtime reference builds also collide under the recovered G2
configuration, so this identity supports the range but cannot select one
historical vendor point release.

## Stock function and neighbor closure

The stock function is 42 bytes at `[0x0048F7CA,0x0048F7F4)`:

```text
38b504000d00a868002808d0aa6800212800fff7effd002801d1002004e068686060e868e060012032bd
```

Its SHA-256 is
`439bbeecb6a0b8266dc3dcd913e98793352b6b346a7a58cdd44322c734621818`.
The disassembly is structurally exact: test `substream->bytes_left`; when it is
nonzero call `pb_read(substream, NULL, bytes_left)` and return false on
failure; otherwise copy `state` and `errmsg` from child to parent and return
true.

The adjacent functions terminate exactly at the replacement boundaries:

| Boundary | Official span | Bytes | SHA-256 |
|---|---|---:|---|
| predecessor `pb_make_string_substream` | `[0x0048F77E,0x0048F7CA)` | 76 | `db925e0c532bac2f2e38f398c7b7d99669afe4d41e6690b08116e9f06ec7d88d` |
| replacement `pb_close_string_substream` | `[0x0048F7CA,0x0048F7F4)` | 42 | `439bbeecb6a0b8266dc3dcd913e98793352b6b346a7a58cdd44322c734621818` |
| successor `decode_basic_field` | `[0x0048F7F4,0x0048F968)` | 372 | `2b1bf389327c0f6ccde636bbb51e36cd0bab3eccc811db9aa0efd3dbfef9e445` |

There is no shared tail, fallthrough entry, or literal pool crossing either
boundary.

## Callers and ingress closure

Exactly three direct stock BL instructions target the original entry:

| Caller | Caller body | Bytes / SHA-256 | Call site / encoding |
|---|---|---|---|
| `decode_static_field` | `[0x0048F968,0x0048FB1C)` | 436 / `58eeda598e1b8e418e41323c1749fa1cd7270a38afb93f0e092bec2a8cfa19f1` | `0x0048FA30` / `fff7cbfe` |
| `decode_callback_field` | `[0x0048FB30,0x0048FBE4)` | 180 / `8e278f306b51ccd2cabc176f7674d17665ca0647facb310c2fe99cfd00a62379` | `0x0048FBA2` / `fff712fe` |
| `pb_dec_submessage` | `[0x0049048C,0x00490538)` | 172 / `3e28ac2fb953613cff7b8a7c30cfdc91aa6c585ea44769e7f64603be853f6f91` | `0x00490524` / `fff751f9` |

The four bytes at `[0x00490538,0x0049053C)` are a separate
`decode_static_field` literal (`0x00787CB0`), not part of the executable
`pb_dec_submessage` body.

For reproducibility, the ordered caller-address list hashes to
`e93c889b8e9d2c99c2283f7fb00a9c8110e38d28c81adae30d03d43964b7afe7`,
the ordered encodings hash to
`5650bceb4c832601ab1a8e63fc08925c6bd560132685920908b7a7afae06bf98`,
and the address-plus-encoding records hash to
`eba2f0d2a98c6983e456d0197a029024029ecc9e6c6df3f9dcf78958c3d740e8`.

The whole installed application contains exactly those three BL targets into
the stock span. Audited scans find no `B.W`, narrow `B`/`Bcc`,
`CBZ`/`CBNZ`, or byte-aligned stored even/Thumb address entering the function
or its interior. The focused gate rechecks those branch and stored-address
classes and requires all three callers to remain unchanged and enter the
generated patch at `0x0048F7CA`. This is a bounded ingress proof for the
decoded classes; it is not presented as a general whole-image data-flow proof
or a separate `MOVW`/`MOVT` materialization claim.

## Provider, ABI, configuration, and semantics

The stock body makes one outgoing call:

| Call site | Encoding | Provider |
|---|---|---|
| `0x0048F7DC` | `fff7effd` | `pb_read` at `0x0048F3BE` |

The authenticated original `pb_read` body occupies
`[0x0048F3BE,0x0048F454)`, is 150 bytes, and hashes to
`69aecb900c749fd98bd2d05e2229e9a3d6829bd36f3e393f624e3579a9b4af7f`.
That complete entry now redirects to the qualified source-owned read leaf;
its remaining stock closure is private `buf_read` identity plus two error
strings.
Under AAPCS32, the close function receives parent in `r0`, substream in `r1`,
and returns its Boolean in `r0`. The provider receives substream in `r0`, NULL
buffer in `r1`, and the exact current `bytes_left` in `r2`, returning Boolean
status in `r0`.

The recovered stream ABI is:

| Offset | Field | G2 type/size |
|---:|---|---|
| `+0` | callback function pointer | 4-byte pointer |
| `+4` | state | 4-byte `void *` |
| `+8` | `bytes_left` | 4-byte `size_t` |
| `+12` | error string | 4-byte `const char *` |

The structure is 16 bytes. `bool` and `pb_byte_t` are one byte. The recovered
option contract has allocation off, 16-bit `pb_size_t`, 64-bit scalar support
on, native FP64, UTF-8 validation off, callback streams and error strings on,
packed structures and packed repeated-scalar encoding on, and
`PB_MAX_REQUIRED_FIELDS == 64`. In macro terms: `PB_ENABLE_MALLOC`,
`PB_FIELD_32BIT`, `PB_WITHOUT_64BIT`, `PB_CONVERT_DOUBLE_FLOAT`,
`PB_VALIDATE_UTF8`, `PB_BUFFER_ONLY`, `PB_NO_ERRMSG`,
`PB_NO_PACKED_STRUCTS`, and `PB_ENCODE_ARRAYS_UNPACKED` are all off/undefined.
Fixed-count and fixed-length are generated-schema choices, not runtime
preprocessor switches. Only the callback-stream and error-string portions are
directly exercised by this leaf; the complete list pins its surrounding
nanopb runtime contract.

The exact behavioral contract is:

- with zero child `bytes_left`, do not call `pb_read`; copy child `state` and
  `errmsg` to the parent and return true;
- with a nonzero remainder, call `pb_read(child, NULL, exact remainder)` once;
- on provider failure, return false immediately and leave the parent `state`
  and `errmsg` unchanged, even if the provider partially mutated the child;
- on provider success, copy only the resulting child `state` and `errmsg` to
  the parent and return true; and
- never change the parent callback or `bytes_left`.

`pb_make_string_substream` already debits the parent length when it creates the
child. Close therefore transfers stream state rather than re-debiting the
parent. Custom callbacks may implement a NULL-buffer skip in chunks; the
source-owned `pb_read` implementation preserves that behavior. The source
deliberately adds no null-pointer validation, allocator, global state, or
hardware access; normal C aliasing behavior is unchanged.

## Source, object, and relocation pins

| File | Bytes | SHA-256 |
|---|---:|---|
| `components/shared/nanopb/runtime_nanopb_close_string_substream.c` | 2,061 | `736e7ec228f9282ba5b093fd482441e6e2017fff860d989dc3aadb2bdeff0fcb` |
| `components/shared/nanopb/runtime_nanopb_close_string_substream.h` | 2,537 | `851af370162d79f4bd0be8b8bb9a5731d47cf02527078b9e278019340f2d65d4` |

These are altered production adaptations selected against the authenticated
0.4.9 compatibility baseline and licensed under Zlib. Apple Clang 21.0.0
(`clang-2100.3.27.1`) and Homebrew Clang 22.1.8 both produce the same
deterministic 968-byte target object with SHA-256
`864cf56e2148b53a0938de80a05e25a81951adbb8ca147a0ddf6297968c126fc`.
Compile-twice qualification reproduces the object.

The four-byte-aligned unrelocated text is 36 bytes:

```text
70b58a680c4605462ab1204600210026fff7feff20b16068e16801266860e960304670bd
```

Its SHA-256 is
`5e6ee5f441e5ba91e0e0147b8453a31186f3ce4bd0efc114edda60f00093a51e`.
The strict relocation contract permits exactly one `R_ARM_THM_CALL` at text
offset 16, through the sole undefined `STT_NOTYPE` symbol
`open_cfw_nanopb_read`, to fixed target `0x0048F3BE`. The only allocated
sections are the 36-byte function text and its eight-byte CANTUNWIND
`.ARM.exidx` metadata record; extraction discards that metadata. There is no
allocated rodata or writable data and no second runtime symbol.

## Apple and Linux placement and patch pins

| Profile | Overlay offset | Runtime span | Relocated bytes | Relocated SHA-256 |
|---|---:|---|---|---|
| Apple Clang 21.0.0 | 124,444 | `[0x007B2940,0x007B2964)` | `70b58a680c4605462ab1204600210026dcf435fd20b16068e16801266860e960304670bd` | `c838be0dfb478fe7fa03d9d71069a200a6477eb5783b631d7d977cd501475438` |
| exact-root Linux Clang 22.1.8 | 126,264 | `[0x007B305C,0x007B3080)` | `70b58a680c4605462ab1204600210026dcf4a7f920b16068e16801266860e960304670bd` | `a90a09f0f98c5b4cf7d885af34c914ae5d492ac7352b5e359ba68ad482cb3044` |

Both placements are four-byte aligned and require zero padding immediately
before this leaf. Profile-specific relocation changes only the encoded call to
the same stock provider.

| Profile | Exact 42-byte replacement | SHA-256 |
|---|---|---|
| Apple | `23f3b9b8` plus 19 x `00bf` | `1b395a30b511a1732cec3791c0c0e1306eac8b3a5c9fb2c1ce3f92e6eaca2255` |
| Linux | `23f347bc` plus 19 x `00bf` | `bcffd3e5e32492e5c32143eac31bec47f2fabb91c8411a274eebd29e99f203f3` |

Each first four-byte instruction branches from the authenticated original
entry to that profile's relocated leaf. The remaining 38 bytes are nineteen
Thumb NOPs, so no stale stock tail remains executable.

## Final aggregate package and plan pins

| Profile | Overlay | Apollo-main component | Core-source package | Flash plan |
|---|---|---|---|---|
| Apple Clang 21.0.0 | 124,480 / `8971dd8fdb8a5f7b703a16dea0c16f27b82739303f18b95fe0b80cf7885252a7` | 3,647,876 / `e416a5d9010c108370505c14b8115d7c9f179ea446fd6888e992c55d6a272ccc` | 4,426,330 / `c7ce9de85bceae301a60a9ef5d5d8d0d7beb62891c661980594de0ac4da22ecb` | 692,652 / `014379f55ad0ed067b0cae99565c4605972ce04c2d1c2cff571d4166010ad038` |
| exact-root Linux Clang 22.1.8 | 126,300 / `3a565aa2dd24d197e04a669bb11a1b12f39b4c8cc70344c55520c922df4964d9` | 3,649,696 / `1aa883832df0a09e0c540d4c31e93331053f05048baf149c3d5dba7725d19158` | 4,428,150 / `31a7850ca003235912a32e66a31397ccabcc3486b96e7acfde1086acfba3a1f1` | 583,414 / `b8654efdc30ec77fec4fff795d58782eb8fa853e5f1010989570388e2b02bdec` |

The Apple plan has 963 placed, two unresolved, and five container-only
records, 970 total. The Linux plan has 817 placed, two unresolved, and five
container-only records, 824 total. The two unresolved records are deliberate
existing package-plan entries, not new unresolved dependencies of this leaf.

The production overlay census is 646 functions, 595 patch sites, and 77
relocated leaves.

## Manifest, component accounting, and ownership

The canonical Apple Apollo-main manifest contains 907 consecutive,
nonoverlapping regions tiling all 3,647,876 component bytes:

| Address status | Regions | Bytes |
|---|---:|---:|
| container-only | 1 | 32 |
| generated alignment | 41 | 82 |
| generated source-entry replacement | 581 | 85,812 |
| generated exact load image | 1 | 6 |
| generated exact replacement | 7 | 134 |
| official blob | 180 | 3,437,194 |
| source compiled | 96 | 124,616 |

The exact split around the stock patch is:

| Region | Runtime span | Bytes | SHA-256 / ownership |
|---|---|---:|---|
| preceding opaque application | `[0x0048F64C,0x0048F7CA)` | 382 | `5450dcb9d4e9e0b080043932dd895b1e506a9500050f93778fb2e3dd6e1a50f8` / official blob |
| generated close replacement | `[0x0048F7CA,0x0048F7F4)` | 42 | `1b395a30b511a1732cec3791c0c0e1306eac8b3a5c9fb2c1ce3f92e6eaca2255` / generated entry replacement |
| following opaque application | `[0x0048F7F4,0x00490616)` | 3,618 | `669001623170616e71648753222e9ed9684086dff448d52804407059982a0019` / official blob |

The appended Apple leaf is the last region at component file offset
3,647,840, runtime `[0x007B2940,0x007B2964)`, and is 36 source-compiled bytes.

Canonical Apple builder accounting is:

- 124,662 total source-owned bytes, including 182 source-owned in-place
  bytes;
- 85,988 generated patch-site bytes and 32 generated wrapper bytes;
- 3,437,194 opaque base bytes; and
- 86,170 replaced stock bytes, equal to 85,988 generated patch bytes plus
  the 182 source-owned in-place bytes.

The additive component categories are 124,662 source, 85,988 generated patch,
32 generated wrapper, and 3,437,194 opaque bytes, totaling 3,647,876 bytes.

Exact canonical whole-package ownership for Apple is 125,251 source bytes
(2.829681%), 87,964 generated bytes (1.987290%), and 4,213,115 opaque bytes
(95.183030%), totaling 4,426,330. The coarser Apple flash-plan/envelope
classification is 125,236 source, 87,827 generated, and 4,213,267 opaque
bytes, also totaling 4,426,330. The Linux plan classifies 127,141 source,
87,742 generated, and 4,213,267 opaque bytes, totaling 4,428,150. Plan
classifications are profile-specific packaging views and do not replace the
exact canonical manifest ownership.

Relative to the immediately preceding production phase, this promotion adds
36 source bytes, changes 42 bytes from opaque to generated replacement, and
increases the package by 36 bytes. It requires no new alignment padding.

## Apollo-main-only and hardware boundary

The production registration, patch, relocated leaf, manifest split, and
aggregate pins in this audit apply only to Apollo-main. The bootloader has a
separate 84-byte homolog at `[0x00418A44,0x00418A98)`, SHA-256
`eaa3249e8ad25deec1e31aa5b03c3b0627448e9b821924f653764141c7d62571`,
with a distinct SRAM map. It contains no exact copy of the 42-byte Apollo-main
stock body and remains untouched. Boot manifest ownership remains 620 source,
817 generated, and 147,785 opaque bytes.

This leaf owns no allocator, transport, schema, generated message,
application callback, peripheral, register address, or other hardware seam.
The only live dependency is the reviewed Apollo-main `pb_read` entry.

## Validation

The final focused test artifact is
`tests/test_runtime_nanopb_close_string_substream.py`, 43,215 bytes, SHA-256
`131634eec3b6a8bae1e3e0c88735f890415d076b682fffb7b909a4da40f67ddb`.
Its six tests pass. They cover source/header/upstream/stock pins; an
authenticated build of the actual pristine upstream implementation; four
edge cases and 1,000 deterministic randomized upstream-vs-production
differential cases; 96 provider-stub zero-remainder, success, and failure
cases; callers, provider, stored addresses, and complete-halfword narrow,
wide unconditional, wide conditional, and linking branch ingress;
compile-twice object/text/relocation closure; and production overlay, patch,
manifest, package, and plan pins for the selected reviewed toolchain profile.

The final nanopb provenance record is 11,863 bytes, SHA-256
`a0d337cafab1537c22d71b7d8f535d5e935e88f9a7d14b73496b2733d23f3b99`.
The offline verifier is 38,752 bytes, SHA-256
`0c1078ea4016b062c621a631fdf99f0dc9fc42b29ed8711bee997e203c0fa785`.
Final gate results are:

- focused production suite: **6/6 PASS**;
- nanopb offline snapshot verifier: **PASS**; and
- nanopb snapshot suite: **11/11 PASS**;
- Apple `make verify`: **PASS**;
- exact-root Linux source replay: **PASS** with the recorded overlay,
  component, package, and flash-plan pins;
- scheduler-cluster historical rollback suite: **9/9 PASS**, including exact
  reconstruction of the 3,639,430-byte `4d564199` component at SHA-256
  `8a747653cc4d938e447197f2bec199933b68072318f0743e3cd85dcf656db8bc`;
  and
- full core-overlay suite: **251/251 PASS** in 588.184 seconds.

These results close the leaf-level source, provenance, ABI, semantic,
topology, relocation, production-registration, and recorded artifact gates.
They also close the aggregate, historical rollback, dual-profile replay, and
full core-overlay gates for this production tranche. The scoped GO does not
assert source provenance for retained opaque firmware and does not authorize
signing, flashing, reset, or hardware operation.
