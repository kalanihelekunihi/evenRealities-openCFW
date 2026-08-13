# nanopb `pb_decode_varint` source-candidate audit

## Result and scope

The official G2 Apollo-main function at
`[0x0048F5B8,0x0048F628)` is nanopb's 64-bit `pb_decode_varint()` under the
recovered callback-stream, error-enabled, 64-bit configuration. An isolated
source candidate now exists at
`components/shared/nanopb/runtime_nanopb_decode_varint_candidate.c` with its
ABI in the adjacent header. It is deliberately excluded from every production
overlay, manifest, and Makefile recipe.

The selected source baseline is the authenticated official nanopb 0.4.9
snapshot at commit `98bf4db69897b53434f3d0ba72e0a3ab1a902824`. This is an
openCFW compatibility choice. Existing authenticated source and reference-
build evidence proves only that the released runtime is compatible with
pristine nanopb 0.4.7, 0.4.8, and 0.4.9. It does **not** prove the vendor's
historical point release or exclude a vendor backport.

This tranche is offline qualification only. It does not change firmware,
aggregate pins, production configuration, or hardware.

## Authenticated inputs

| Item | Bytes | SHA-256 |
|---|---:|---|
| Official OTA component | 3,523,396 | `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863` |
| Installed payload | 3,523,364 | `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701` |
| Authenticated nanopb `pb_decode.c` | 53,845 | `e980f2a41d9abe37b7e6fb4c9ba1ebfd68507a6fd2653f8d755e1947a9c84b1a` |
| Authenticated nanopb `pb_decode.h` | 7,870 | `1747746e5961de5789bcf0795588da0790cd18b2e4e706ad9c7099a0fa1cc83f` |
| Recovered G2 options | 1,551 | `ae758999d239e49e2d5c5bf6de3f4aef3aab5cd3c29d8de65c4db301c62899db` |

The snapshot verifier authenticates the annotated 0.4.9 tag, commit, tree,
individual blobs, and unchanged Zlib license entirely offline. Its provenance
record explicitly marks 0.4.9 as a compatibility selection and
`exact_g2_point_release_proven` as false.

## Exact stock boundary

The OTA mapping is `runtime = file_offset + 0x00437FE0`. The selected stock
body is 112 bytes at file `[0x575D8,0x57648)`:

```text
2de9fc4106000f005ff000080024002569463000fff742ff002818d0b8f13f0f0
4d39df8000010f0fe0f12d19df8000010f07f00c117424649f0acfd04430d43
18f107089df800000006e1d40be000200ce0f068002801d0f06801e0dff8fc0a
f060002002e0c7e900450120bde8f681
```

Its SHA-256 is
`f93d678981f92603982c9afc6c6f9976ca14d1a7a7e0bfc949d3ff73f2791ff2`.
The immediately preceding 10-byte `pb_decode_varint32` wrapper occupies
`[0x0048F5AE,0x0048F5B8)` and hashes to
`48218a658cffd7aeddfb623c9d0e7bd038ceb2a6898e9f8d08b10d5779f4f79b`.
The following 68-byte pair of `pb_skip_varint` and `pb_skip_string` functions
occupies `[0x0048F628,0x0048F66C)` and hashes to
`5e6ebac0dfbc3643144fae98faa36f618e0394b3a95f0bbba491d3d08b256fb8`.
Those adjacent entry prologues, the selected epilogue at `0x0048F624`, and
the absence of external interior ingress close the function boundary.

## Callers and ingress closure

A halfword-aligned whole-image Thumb scan finds exactly three wide linked
branches into the selected span, all to its entry:

| Call site | Encoding | Owning caller |
|---|---|---|
| `0x00490156` | `fff72ffa` | `pb_decode_svarint` |
| `0x004901EC` | `fff7e4f9` | `pb_dec_varint`, unsigned path |
| `0x004902A0` | `fff78af9` | `pb_dec_varint`, signed-compatible path |

The ordered call-address SHA-256 is
`0e5dfe5425e46893f310d2ba87a0dd66693d64ef5872b5491bd08ac6aa1f4ba6`;
the address-plus-encoding record SHA-256 is
`75504b52a651ac12823cb66035f7c7063172354f3a33b692ace3275fe2094b4f`.
The two complete caller spans are:

| Caller | Span | Bytes | SHA-256 |
|---|---|---:|---|
| `pb_decode_svarint` | `[0x00490150,0x00490190)` | 64 | `80b24be422cf924f3ae1b79669312535dc0d5a56dd88be8a6b9e4ee5ff064048` |
| `pb_dec_varint` | `[0x004901D6,0x00490352)` | 380 | `ccae20aa7dff8515a5a2b6ad4a05248a865dfaa8c912fd38c8c5f77c3a6a8e0a` |

There is no exterior `B.W`, wide conditional branch, 16-bit unconditional or
conditional branch, `CBZ`/`CBNZ`, or aligned or byte-granular stored pointer to
the entry or an interior byte. Thus no alternate-entry ABI was found.

## ABI, configuration, and outgoing dependency closure

The function has the upstream AAPCS signature:

```c
bool pb_decode_varint(pb_istream_t *stream, uint64_t *destination);
```

`r0` is the stream, `r1` is the 64-bit destination, and the Boolean result is
returned in `r0`. Success stores the decoded pair through `r1`; all failures
leave the destination unchanged. The recovered 32-bit `pb_istream_t` layout
is callback `+0`, state `+4`, `bytes_left` `+8`, and `errmsg` `+12`, total 16
bytes. This proves callback streams and runtime error strings are enabled.
The body maintains a full 64-bit result and therefore also proves
`PB_WITHOUT_64BIT` is off. The surrounding runtime proves malloc off,
16-bit `pb_size_t`, native 64-bit doubles, UTF-8 checking off, packed support,
and the default 64 required-field limit; these states are enforced by
`third_party/nanopb/g2-config/pb_g2_options.h`.

The stock body has exactly these nonlocal dependencies:

| Site | Target / data | Contract |
|---|---|---|
| `0x0048F5CC` | `pb_readbyte` at `0x0048F454` | Reads one callback byte, decrements `bytes_left`, preserves the first error |
| `0x0048F5F0` | 64-bit left-shift helper at `0x004D914C` | IAR-emitted shift for `(byte & 0x7F) << bit_position` |
| `0x0048F614` | literal slot `0x00490114` -> `0x00787C80` | NUL-terminated `"varint overflow"` error |

The complete 72-byte `pb_readbyte` body hashes to
`15c8303c5c1dbf1b3f143142c6169026cb8bc56b37a6291dd0457b3664b67ae5`.
The 34-byte shift helper `[0x004D914C,0x004D916E)` hashes to
`b0eaecb9c4970d61ba662726c82e216b28ce4023456f6eb14df651c1def4dbb5`.
The four-byte literal slot hashes to
`932b450ffea27c45062b59f6e45c640d894e6eae043fd124b694358e87e00ab4`;
the 16-byte string including NUL hashes to
`e9b62825b028cfc32f718b48de14fcbc783a9009279d2c88cf4394d54767141d`.

The candidate deliberately exposes one unresolved read-byte seam. Its host
fixture supplies the exact upstream contract. Compiler-generated 64-bit shift
instructions and the candidate-owned error literal close the other two
dependencies; no heap, descriptor, schema, encoder, or global-state dependency
is introduced.

## Behavioral equivalence

The focused differential harness links the candidate against authenticated
nanopb 0.4.9 `pb_decode.c` and `pb_common.c`. It compares status, decoded or
unchanged destination, callback count, consumed bytes, remaining byte budget,
and classified error for:

- zero, one-byte, multibyte, and maximum 64-bit values;
- noncanonical but accepted encodings;
- the ninth/tenth-byte boundary and every tenth-byte overflow form;
- empty/truncated streams and independently shorter byte budgets;
- callback failures at every read position; and
- sticky preexisting errors on EOF, I/O failure, and overflow.

The candidate retains the upstream 0.4.6-and-later guard
`bit_position >= 63 && (byte & 0xFE) != 0`, first-error policy, and
destination-on-success-only rule.

## Reproducible candidate objects

Both reviewed compilers use the isolated freestanding Thumb target flags and
produce one executable candidate section, one 16-byte read-only error string,
no writable allocated section, and exactly four relocations: one
`R_ARM_THM_CALL` to `open_cfw_nanopb_readbyte_candidate`, paired
`R_ARM_THM_MOVW_PREL_NC` / `R_ARM_THM_MOVT_PREL` relocations to the local
error string, and the normal `R_ARM_PREL31` exidx relocation.

| Profile | Object | Candidate text | Text SHA-256 |
|---|---|---:|---|
| Apple clang 21.0.0 | 1,284 / `c5c95e69e834ab88c21b060813181598e9ec3696e7f3c76b814357f70f772a97` | 128 | `b3f040de87b4fd22ba1e66c81121194ddaa03f56253b5d9e0a322a9671247e94` |
| exact-root Linux clang 22.1.8 | 1,260 / `cfb795065b13944582e127b4cd6154f632d9dada423854db2f19697de4c876b0` | 124 | `e820aa1b54f20ec1454462d356562177f8d03d98f21dff4bba77fa39fe282fa5` |

The local string SHA-256 is
`e9b62825b028cfc32f718b48de14fcbc783a9009279d2c88cf4394d54767141d`
in both profiles. Two independent objects per active profile must reproduce
byte-for-byte.

## Production promotion

The placements and aggregate artifact pins in this section are the frozen
nanopb-only promotion phase, before the later CmBacktrace and FreeRTOS+CLI
source additions compacted the overlay tail.  The current aggregate repins the
nanopb text/rodata to `0x007B2560` / `0x007B25E0` on Apple and
`0x007B2C80` / `0x007B2CFC` on exact-root Linux; current artifact pins are
maintained in `docs/source-coverage.md` and the canonical build reports.

The candidate remains independently named and production-excluded. A separate
altered source, `components/shared/nanopb/runtime_nanopb_decode_varint.c`, is
now the reviewed production leaf. Its complete Zlib notice and comments state
that nanopb 0.4.9 is a compatibility baseline, not proof of the vendor's
historical point release. The offline snapshot verifier now permits only this
pinned local leaf while continuing to reject direct registration of pristine
`pb_common.c`, `pb_decode.c`, or `pb_encode.c`.

The production source is 2,219 bytes with SHA-256
`ae728feddd4456f7e846596dcd40b4a8be3540f52086811d5290866a3bdd1fb1`.
Its Apple/Linux raw objects are respectively 1,244 bytes /
`29cebc44eddfd9c79aceccf6da2bec1dd577c555619f3a2b9b0c74500daea7a7`
and 1,220 bytes /
`0f19f9419ddc74d50e58f5e63737fe7224de35fdf7a0395267e987748e5064ed`.
Both retain one undefined `open_cfw_nanopb_readbyte` seam and the same
16-byte local overflow string; there is no candidate symbol in the production
object or registration.

Apple places the 128-byte text at `0x007B2564` and rodata at `0x007B25E4`;
exact-root Linux places 124-byte text at `0x007B2C84` and rodata at
`0x007B2D00`. The sole external relocation is explicitly bound to reviewed
stock `pb_readbyte` at `0x0048F454`; a paired local PREL MOVW/MOVT closes the
diagnostic string. The complete stock span is authenticated before being
replaced by one B.W and 54 Thumb NOPs.

The production differential suite compares production, candidate, and
authenticated upstream behavior. Its whole-component ingress gate exercises
live decoders for BL/B.W, wide conditional, narrow B/Bcond/CBZ/CBNZ, and scans
byte-granular canonical and Thumb-form stored pointers. Only the three known
stock-entry BL callers remain; no exterior edge or pointer enters the old
interior. The ten preceding and 68 following stock bytes are unchanged.

Final Apple overlay/component/package pins are 123,600 /
`ea8a43a1c6e674cb3f2b1df4adc75887b39e92da7ff9c22fc400a634b09ae1e2`,
3,646,996 /
`a897f9ae6215d4669b540f0142c356dc8e6610543884694e856308e303826b68`,
and 4,425,450 /
`cdbc1c41607d4623625ce25d0757457c72c550915c60d4b5ab7077c5760d0812`.
Exact-root Linux pins are 125,420 /
`dfc052f153f99c1fb153dd06cfcbd5380733d47d6e376ce902dbc2dc63413692`,
3,648,816 /
`24a02cdaf64fb9d761fb896a4d09d72cfbe48f08b799cb49a95e0a61ad69892f`,
and 4,427,270 /
`81729530e02fc666dfdef831933b44ec74e45bc3412c81d7c1161e03a5055152`.

No firmware was signed, flashed, reset, booted, or executed on G2 hardware.
