# Nanopb private `pb_decode_varint32_eof()` source-candidate audit

Status: bounded and qualified as a production-excluded source candidate. No
overlay, manifest, build, provenance, or snapshot-verifier registration is
made by this work.

## Boundary and source identification

The exact stock body occupies `[0x0048F4B8, 0x0048F5AE)`, ending immediately
before the public `pb_decode_varint32()` wrapper. Its 246 bytes have SHA-256
`8583fa17383d72bbdcab6c2a7a20369dc0598d3ac3061feaf8a7b29dfa520150`.
The body is source-compatible with private nanopb `pb_decode_varint32_eof()`.

The exact pristine 1,721-byte definition has SHA-256
`66833ae2defb892aa17162625ef107bda03be44e73f0b120d48e6d2b52770e2c`
in each authenticated release:

| Release | Commit | `pb_decode.c` byte span |
|---|---|---:|
| nanopb-0.4.7 | `b97aa657a706d3ba4a9a6ccca7043c9d6fe41cba` | `[5676, 7397)` |
| nanopb-0.4.8 | `6cfe48d6f1593f8fa5c0f90437f5e6522587745e` | `[5676, 7397)` |
| nanopb-0.4.9 | `98bf4db69897b53434f3d0ba72e0a3ab1a902824` | `[5762, 7483)` |

The vendored authenticated snapshot selects nanopb-0.4.9. Cross-release
identity proves compatibility, not the vendor's historical checkout.

## Ingress and outgoing closure

The official application contains exactly two direct callers:

- `BL 0x0048F5B2 → 0x0048F4B8` from `pb_decode_varint32()`
- `BL 0x0048F682 → 0x0048F4B8` from `pb_decode_tag()`

The complete outgoing code closure is two calls to the stable, reviewed
`pb_readbyte()` entry:

- `BL 0x0048F4C4 → 0x0048F454`
- `BL 0x0048F4FA → 0x0048F454`

A complete halfword-aligned application scan found no external `B.W`,
conditional-wide, narrow-branch, stored-function-pointer, or interior ingress
into the stock span. Full-span `B.W` plus NOP replacement is therefore the
future promotion shape; this candidate installs no replacement.

## Data seam

Both stock overflow paths load literal slot `0x0048FC84`, at instructions
`0x0048F54C` and `0x0048F588`. The slot contains `0x00787C80`, the unique
application copy of NUL-terminated `"varint overflow"`. The same literal slot
is also referenced by code outside this function, and a second pointer slot at
`0x00490114` targets the same shared string for public `pb_decode_varint()`.

Because the string is unequivocally part of the authenticated open-source
definition, the excluded candidate emits its own 16-byte source-owned constant
instead of depending on opaque data. Existing non-null `stream->errmsg` values
remain preserved exactly as required by `PB_RETURN_ERROR`.

## ABI and optional EOF contract

The private ABI is `bool (pb_istream_t *, uint32_t *, bool *)`, using `r0`,
`r1`, and `r2` for the three pointers and returning Boolean status in `r0`.
Recovered target widths are one-byte `bool`/byte and four-byte `uint32_t`; the
reviewed stream ABI has `bytes_left` at offset 8 and `errmsg` at offset 12.

The EOF pointer is optional and is written only when the *initial* read-byte
call fails with `bytes_left == 0`. A successful decode leaves it untouched, as
does failure after at least one byte or an I/O failure with bytes remaining.
Callers establish their own initial value: `pb_decode_tag()` clears it, while
the public varint32 wrapper passes null. The local `uint_fast8_t` bit position
never exceeds 70 in a path that reaches its increment, so its implementation
width creates no interface or wraparound ambiguity.

## Host and boot qualification

The host differential covers the authenticated upstream wrapper over quick,
multibyte, `UINT32_MAX`, sign-extension, truncation, 32-bit overflow, and
64-bit overflow paths. Separate checks cover initial EOF, null EOF, successful
decode, post-byte truncation, and forced I/O failure semantics.

Two pinned Apple clang 21 target builds produce the same 1,328-byte ELF object
with SHA-256
`1e83fc04ec39e95c96189dbca42b902dd3bfaead5f08068eb33edc4b6aad54a6`.
The sole executable section is 216 bytes with SHA-256
`557a878baea647ded461e093abe1d1a1c6f3d84820fae2d15f7513f27f122326`;
its only undefined symbol is `open_cfw_nanopb_readbyte`. Two
`R_ARM_THM_CALL` relocations at section offsets 16 and 106 target that seam.
The source-owned overflow string occupies a 16-byte read-only section with
SHA-256
`e9b62825b028cfc32f718b48de14fcbc783a9009279d2c88cf4394d54767141d`;
a local MOVW/MOVT relocation pair at offsets 204 and 208 reconstructs its
address. There is no writable data.

The authenticated bootloader contains neither the exact 246-byte body nor its
12-byte boundary probes. No bootloader homolog is claimed.

## Promotion gate

Source and target-object compatibility are bounded; no target ABI or
configuration blocker was found. Promotion still requires object placement,
relocation of the read-byte and source-owned data seams, and aggregate overlay
tests that authenticate complete stock-span replacement.
