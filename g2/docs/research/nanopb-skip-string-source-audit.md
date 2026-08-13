# Nanopb `pb_skip_string()` source audit

Status: current production source in the reviewed Apple-clang and exact-root
Linux-clang firmware profiles. This is an altered Zlib-licensed compatibility
implementation, not a pristine upstream checkout.

## Result

The authenticated application routine at `[0x0048F64C, 0x0048F66C)` is the
32-byte `pb_skip_string()` shape: decode a `uint32_t` length through
`pb_decode_varint32()`, then call `pb_read(stream, NULL, length)`. openCFW
replaces the complete span with a non-linking `B.W` and `NOP` fill and appends
`open_cfw_nanopb_skip_string()` as source-owned overlay text. Its two providers,
`open_cfw_nanopb_decode_varint32` and `open_cfw_nanopb_read`, are also
source-owned production leaves; neither dependency returns to an opaque stock
provider.

The selected compatibility baseline is nanopb 0.4.9. The pristine definition
is byte-identical across the authenticated 0.4.7, 0.4.8, and 0.4.9 definitions,
so this selection is compatibility evidence and is not proof of the Even
Realities vendor point release or historical checkout.

## Authenticated source and stock evidence

The exact pristine definition is 299 bytes with SHA-256
`8da14b4cc741fc15884b11d3447d0c2c529f65c31b3823170837229d36f81585`:

| Release | Commit | `pb_decode.c` byte span |
|---|---|---:|
| nanopb-0.4.7 | `b97aa657a706d3ba4a9a6ccca7043c9d6fe41cba` | `[8276, 8575)` |
| nanopb-0.4.8 | `6cfe48d6f1593f8fa5c0f90437f5e6522587745e` | `[8276, 8575)` |
| nanopb-0.4.9 | `98bf4db69897b53434f3d0ba72e0a3ab1a902824` | `[8362, 8661)` |

The official application body is 32 bytes with SHA-256
`03afe2d60436676fffba342c7b8c9504992fa903d7cba768396fd1de2c6c66cd`.
It has one direct external caller, `BL 0x0048F6C6 -> 0x0048F64C`, and two
outgoing calls:

- `BL 0x0048F654 -> 0x0048F5AE` (`pb_decode_varint32`)
- `BL 0x0048F666 -> 0x0048F3BE` (`pb_read`)

Halfword-aligned branch and stored-address scans found no alternate, interior,
conditional, narrow-branch, or stored-pointer ingress. The complete 32-byte
replacement is therefore the authenticated ownership boundary.

The caller instruction encoding is `fff7c1ff`. The containing caller span is
`[0x0048F6A0, 0x0048F6EA)`, SHA-256
`36089daffbbc82abad65d97ae0fd64b58b8ad227ed585aa704611bc30369912d`.

## Altered source and target contract

The production source removes only upstream's target-tautological
`(size_t)length != length` guard. Recovered target ABI evidence establishes
32-bit `size_t` and `uint32_t`, so the guard emits neither a branch nor the
`"size too large"` literal in the stock body. Static assertions retain that ABI
contract. The emitted leaf is 34 bytes, has no allocated writable or read-only
data closure, and carries exactly two `R_ARM_THM_CALL` relocations at offsets 8
and 20. Its 8-byte `.ARM.exidx` companion is authenticated `CANTUNWIND` metadata
with one same-function `R_ARM_PREL31` relocation and is deliberately discarded,
not promoted as executable closure data.

The altered production source is 1,688 bytes, SHA-256
`b1f492b0358e51ce89db622e4af13a7f1eef7ffce9fc81fd954609cdcd934876`;
its header is 1,732 bytes, SHA-256
`807fb52ae19de372024ebea64268aca011e573e9ad6d4247e911b2e037058303`.
Both compilers emit a 988-byte object, SHA-256
`d2bdca5570c8e7a0ee1adfc9decfb3ad54f6c77abe7c7e3f05e0e3dd9f1c5bbe`,
and identical unrelocated text SHA-256
`d3216f569354900680dae5d78350af7668be4d8fbdae64a47afc4f440b0df920`.
The discarded eight-byte exidx payload is `0000000001000000`, SHA-256
`01acecb507abfe1a354aa8064f4af5d3f1acd019e37db3c11c97523b71c76e9d`.

Apple clang 21.0.0 and Homebrew clang 22.1.8 independently produce the same
988-byte object and 34-byte unrelocated text. The reviewed placements are
offset `125224` / runtime `0x007B2C4C` on Apple and offset `127048` / runtime
`0x007B336C` on Linux. Relocated leaf SHA-256 is
`3b1a0dbe465d562770e02d5afe04357087a6bfee22342a0f6844986a0161f547`
for both profiles. The profile-specific full-span patch hashes are
`86ba480676461c25f262f93c3d1cc0e0e6080e6c44c367a261e1ac857ce81c3d`
and `738d3ad448d28a408c0aaa76f7c7188181966ac44bc22afe675bde4fd83a9f7d`.

## Current dual-profile firmware artifacts

| Artifact | Apple-clang | Linux-clang |
|---|---|---|
| Overlay | `125258` / `1f71240bd75af28798d93eba217b99464156ee40ae353333c2fd0f449b9a8c76` | `127082` / `f24cf0e060530429679df9389571ffee397819dfa2c3abc00d26deb75a3e47ad` |
| Main component | `3648654` / `36b7f32f9f5f1a4c2fbf800b8cda0f48aa521bfc87638d671932b80b49f7e991` | `3650478` / `5fe58e3af2a0b7fed55c6b7c33afbd1ac5c887860721b04859e2d49d81be828c` |
| Package | `4427148` / `532743c6a1b96f198f0991c320bf3318eac88bc538a90a9e0b0267aaacef07b3` | `4428972` / `22117e0cd7d0b827a8c31d22eb509edb30651fef6a6308838a8220ff80f6c702` |

Apple retains the per-function flash census `1032/2/5` and effective ownership
`126028/88659/4212461` (source/generated/opaque). Linux uses the reviewed coarse
appended-source mapping, census `848/2/5`, and effective ownership
`127963/88548/4212461`. Both profiles are current, deterministic, and
fail-closed; neither is pending, provisional, or deferred.

The canonical manifest has 960 regions. This increment contributes
`nanopb_skip_string_source_replacement`,
`opaque_application_between_nanopb_skip_string_and_nanopb_close_string_substream`,
`apollo_nanopb_skip_string_source_alignment`, and
`apollo_nanopb_skip_string_source_leaf`.

## Historical candidate qualification

Before promotion, the bounded candidate used
`open_cfw_nanopb_skip_string_source_candidate` with the deliberately stock
decode seam `open_cfw_nanopb_decode_varint32_stock_candidate`. Those names are
retained here only so the authenticated Git-object proof remains reviewable;
neither is a current production registration. The historical candidate object
was 1,044 bytes with SHA-256
`f059f1c161bb602413d0505e51f6253283bf589622159c0fe4ee4202153e2b72`;
its 34-byte text already had SHA-256
`d3216f569354900680dae5d78350af7668be4d8fbdae64a47afc4f440b0df920`.
The historical source blob `c9113221c6f392f48d11e4079876cb5ecb4f2311`
was 1,662 bytes with SHA-256
`28d3ec9e4e58f583ed19a0eee08247f5bc5df8c8c01dff418363eaa173b9ac24`;
the header blob `8d3f4901fbaf62c245b34e3bffc9b0564bfe45f9` was
2,023 bytes with SHA-256
`470e84bab1ba1d78630d198f023e28444f6d3ac658e041df23d85425918180e7`.

## Bootloader and hardware boundary

The authenticated 148,599-byte bootloader contains neither the complete stock
body nor its characteristic boundary probes, so no bootloader homolog exists.
This audit and its builds perform no signing, flashing, reset, boot, transport,
or hardware execution. They do not authorize any hardware operation.
