# nanopb `pb_istream_from_buffer` production-source audit

Status: production source for the complete Apollo-main constructor; Apple and
Linux compiler outputs are pinned. No signing, flashing, or on-device behavior
is claimed.

Scope: official G2 `2.2.6.10` Apollo-main constructor
`[0x0048F49C,0x0048F4B8)`, authenticated nanopb source, the recovered stream
ABI, canonical buffer-callback identity, complete ingress topology, host
behavior, target compilation, flash ownership, and bootloader exclusion.

## Result and upstream authority

The 28-byte stock function is compatible with pristine nanopb
`pb_istream_from_buffer()` across authenticated releases 0.4.7 through 0.4.9.
openCFW selects tag `nanopb-0.4.9`, commit
`98bf4db69897b53434f3d0ba72e0a3ab1a902824`, as its compatibility baseline.
The exact 578-byte upstream definition at `pb_decode.c[5114:5692]` hashes to
`087c2b851d9ea55d5a81d70a37a88385ee7fe8db86daef34ea3d0584183b0b13`.
This compatibility result does not prove the vendor's historical nanopb point
release or checkout.

Production uses
`components/shared/nanopb/runtime_nanopb_istream_from_buffer.c` and its header.
Both retain the nanopb Zlib notice and altered-source attribution. The
constructor is the ninth bounded nanopb production function; pristine
`pb_common.c`, `pb_decode.c`, and `pb_encode.c` remain reference-only.

## Stock body, ABI, callback identity, and topology

The official application package is 3,523,396 bytes with SHA-256
`36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`.
The constructor occupies `[0x0048F49C,0x0048F4B8)`, 28 bytes, and hashes to
`852314bb8f86dcbd550deb0f51bc285b662e39c1b4fae66690c44a7bf4f7a674`.

The recovered 32-bit stream fields are callback `+0`, state `+4`, `size_t
bytes_left` `+8`, and error pointer `+12`, total 16 bytes. The stock constructor
loads literal slot `0x0048FC78`; the slot contains canonical Thumb callback
value `0x0048F3A5`. Production relocates exactly one MOVW/MOVT pair to that
identity. It does not bind the field directly to the appended private
`open_cfw_nanopb_buf_read` leaf, preserving pointer equality in the
source-owned `pb_read()` fast path and in preexisting streams.

Exhaustive whole-application scans find exactly 30 aligned `BL` callers, all
to entry `0x0048F49C`:

`0x0045934E`, `0x00459F12`, `0x004607AC`, `0x00471726`, `0x00472122`,
`0x0048FBD0`, `0x0048FE1C`, `0x00494D0A`, `0x004956C6`, `0x00496652`,
`0x0049B252`, `0x004A7988`, `0x004D6C58`, `0x004D84A2`, `0x004DA8F2`,
`0x004E3280`, `0x004FE392`, `0x00501AD6`, `0x00501FE8`, `0x00510AC4`,
`0x00558A06`, `0x0055A40A`, `0x0058736A`, `0x00588632`, `0x0059F5BA`,
`0x005B1BCA`, `0x005CE294`, `0x005CE9EC`, `0x005EE942`, and `0x005EEC0E`.

There is no alternate branch, stored-pointer, entry, or interior ingress.

## Production placement and ownership

The complete stock entry is replaced by a non-linking Thumb-2 `B.W` followed
by twelve Thumb NOPs. Canonical Apple clang 21 places the 20-byte leaf at
overlay offset 124,896 / runtime `0x007B2B04`; unrelocated SHA-256 is
`d106ce1009ddcbd4d39a7c56edbcd51f50d4cfa6768f78d224ea988aa9a416d7`
and relocated SHA-256 is
`af3357e8178ab650d5476d0ad0fbfee0b44cdb288d9251da909b3ba7a1de92c4`.
The Apple entry patch hashes to
`e2e120080f18fdd443e08a5def120575a2eae21139a5276f3f8fbb53e1aea6dd`.

Reviewed Linux clang 22.1.8 places the 22-byte leaf at overlay offset 126,720 /
runtime `0x007B3224`; unrelocated SHA-256 is
`6c23e37c9468d866db2e2cb6bf0ce8e103fb34df1078e740b4b8d5d799c257ff`
and relocated SHA-256 is
`59438f30232883560f65ad4e58ff97c05dcdffdb6287fffcb7c1b79487df436d`.
The Linux entry patch hashes to
`902daf1332ace8eae1d3f71e324ddbc03ec2542d93530fa876f24228d40c86ed`.

The canonical Apple overlay is 124,916 bytes with SHA-256
`bece5e1604f506af97c7025373d3910c4a22a8fb70104f4eafb17fe20d643144`;
the Apollo-main component is 3,648,312 bytes with SHA-256
`3176f78e3576591df05268e44c56e734cdee6a93b3ffae01f1ba85f6ab380bca`;
and the complete package is 4,426,806 bytes with SHA-256
`062eaf5a7f301022f97162f4517d15248276e80c11a27b7c9f9b0e4cda4fbef2`.

The Apollo-main manifest contains 949 regions. It tiles the constructor as a
28-byte `nanopb_istream_from_buffer_source_replacement` at component offset
357,564 / runtime `0x0048F49C`, followed by a 256-byte official region at
offset 357,592 / runtime `0x0048F4B8`. The source leaf is a 20-byte
`apollo_nanopb_istream_from_buffer_source_leaf` at component offset 3,648,292 /
runtime `0x007B2B04`. Apollo-main ownership is 184 official regions / 3,436,786
bytes, 595 generated entry-replacement regions / 86,220 bytes, and 110
source-compiled regions / 125,032 bytes.

## Validation boundary

Host differential tests cover construction, zero-length/null state, callback
copying, and state advancement. Target tests pin the exact two-relocation
closure, reject writable allocated data, authenticate the stock body and all
30 callers, and prove the complete 28-byte entry replacement. The
authenticated 148,599-byte bootloader contains neither the constructor body
nor its characteristic probes; no bootloader homolog is claimed.

This promotion removes 28 opaque Apollo-main bytes, adds a 28-byte generated
entry replacement and a 20-byte source leaf, and leaves unrelated opaque
regions untouched. Hardware execution remains a separately authorized step.
