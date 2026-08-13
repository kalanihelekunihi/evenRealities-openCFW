# Nanopb private `pb_dec_submessage` source audit

Status: production-integrated for the reviewed Apple toolchain. The larger
private `pb_decode_inner` dependency is deliberately retained as an explicit
stock seam rather than being described as source-owned. Exact-root Linux
aggregate reproduction remains pending.

## Identity and boundary

The official Apollo-main image supplies `pb_dec_submessage` at
`[0x0049048C,0x00490538)`: 172 bytes with SHA-256
`3e28ac2fb953613cff7b8a7c30cfdc91aa6c585ea44769e7f64603be853f6f91`.
The end is `0x00490538`, including the two-byte return at `0x00490536`.
The four-byte words at `[0x00490488,0x0049048C)` and
`[0x00490538,0x0049053C)` are separately pinned literal islands, not function
bytes. The successor `pb_dec_fixed_length_bytes` begins at `0x0049053C`.

The sole direct caller is the `BL` at `0x0048F92C` (`00f0aefd`). Its address
digest is `9cf45d77d33e2071d3a218f916571e367cf613ffc3d8349d615e1aed9b6511d3`;
the address-plus-opcode digest is
`e495ed6e8d76d6ffacaf2829a7aafe8a02fa9626a4ba9661f9d61d863e8504e7`.
There is no wide, narrow, conditional, or call ingress into the interior.

One raw stored-value scan collision occurs at unaligned address `0x004B29DF`
for interior value `0x004904FC`. Rizin disassembly closes it as the final byte
of `77f0d5fc` (`BL 0x0052A38A`) followed by `0449` (`LDR r1, [pc, #0x10]`),
not a pointer. Context `[0x004B29D0,0x004B29F2)` hashes to
`5fd8bf531f028807afc495f5b09e3d3cc4ac6c6eb438c522e2ad43cbc480c078`.

## Upstream attribution

Authenticated nanopb commit
`98bf4db69897b53434f3d0ba72e0a3ab1a902824` is the selected 0.4.9
compatibility baseline. `pb_decode.c[49908:51557]` is 1,649 bytes and hashes
to `94000cbd5547153805c6b687cb80650a6f57cf9a030434cbf179cfde94ae3f4e`.
The source remains compatible with the previously authenticated pristine
0.4.7--0.4.9 range; this does not prove the vendor's historical checkout.

## Closure and remaining seams

The stock body calls:

| Site | Target | Ownership |
|---|---:|---|
| `0x0049049C` | `pb_make_string_substream` `0x0048F77E` | source-owned |
| `0x0049051A` | `pb_decode_inner` `0x0048FE98` | retained stock executable seam |
| `0x00490524` | `pb_close_string_substream` `0x0048F7CA` | source-owned |

The `BLX r3` at `0x004904E4` is the nanopb application message-callback ABI.
It is a dynamic schema/application seam, not a fixed hidden firmware target.
The callback structure is two target pointers (decode function and argument),
stored immediately before `field->pSize`. The only diagnostic pointer is
`0x004905D8 -> 0x0076F454`, the 25-byte NUL-terminated string
`invalid field descriptor`; the replacement owns this string locally.

The replacement preserves `PB_LTYPE_SUBMSG_W_CB == 9`, static/non-repeated
`PB_DECODE_NOINIT == 1`, callback-consumed substreams, early descriptor
failure, unconditional close after callback/inner decoding, and close-failure
precedence. It intentionally declares `open_cfw_nanopb_decode_inner` as a
fixed-address stock provider. Therefore this leaf can improve ownership while
remaining accurately classified as partially closed; the next dependency
frontier is private `pb_decode_inner` beginning at `0x0048FE98`.

Apple Clang 21.0.0 emits a 1,320-byte object. The 138-byte text leaf is placed
at `0x007B307C` with relocated SHA-256
`6164e7106258de3ee838ef6847afa63cf509c8cd7696d99dddf2c2f56cfa84ea`;
its unrelocated hash is
`ae1d41d5b11734d754d8511f0e782434d757d4fa097b0431ef46c64e1344018c`.
The 25-byte diagnostic follows at `0x007B3106`; the complete 163-byte closure
hashes to `85d3f4025b36602f47fb0ddb9145a40bbe54226de4ea044a6a2db5671245d82b`.
One generated alignment byte precedes the leaf. The complete entry replacement
hash is `24ead852701a33f497a850ca4f52cdb744297ef6a360779e3d54adaff0183ba8`.

## Reproduction

```sh
python3 tools/analyze_g2_nanopb_dec_submessage.py --json
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v \
  tests.test_runtime_nanopb_dec_submessage
```

No hardware execution claim is made. Linux/Clang aggregate reproduction and
full firmware testing remain deferred under the current iterative policy.
