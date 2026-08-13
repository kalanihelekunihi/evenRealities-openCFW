# Nanopb `pb_skip_field()` source promotion audit

## Result

The complete stock dispatcher at `[0x0048F6A0,0x0048F6EA)` is now replaced by
a bounded production source leaf. Its 74 stock bytes hash to
`36089daffbbc82abad65d97ae0fd64b58b8ad227ed585aa704611bc30369912d`.
Rizin disassembly and the independent fail-closed analyzer recover the exact
upstream switch:

| Wire value | Stock call site | Target | Current ownership |
|---:|---:|---:|---|
| `0` / VARINT | `0x0048F6B6` | `pb_skip_varint` `0x0048F628` | Source-owned |
| `1` / 64-bit | `0x0048F6C0` | `pb_read` `0x0048F3BE`, count 8 | Source-owned |
| `2` / string | `0x0048F6C6` | `pb_skip_string` `0x0048F64C` | Source-owned |
| `5` / 32-bit | `0x0048F6D0` | `pb_read` `0x0048F3BE`, count 4 | Source-owned |
| other | local | preserve existing error or set `invalid wire_type` | Source-owned rodata |

Only two direct callers enter the function, at `0x0048FB44` and
`0x0048FFBE`. No bootloader homolog is claimed. The preceding complete
`pb_decode_tag` body and following `read_raw_value` prefix are independently
hash-pinned so the boundary cannot silently absorb a neighbor.

## Upstream authority

The maintained selection is the authenticated nanopb 0.4.9 annotated tag,
commit `98bf4db69897b53434f3d0ba72e0a3ab1a902824`, under Zlib. The exact
415-byte definition is `pb_decode.c[9043:9458]`, SHA-256
`4f447e98f77d58030aa39bf1d0e936b01253f828440f362336f96a8d7c679be1`.
The stock runtime remains compatible with pristine nanopb 0.4.7 through
0.4.9, so this pin is an openCFW compatibility choice, not proof of the
vendor's historical checkout.

The recovered G2 configuration retains callback streams and error messages,
uses the 16-byte `pb_istream_t` with `errmsg` at `+0x0C`, and compiles the wire
type as an eight-bit value at this ABI boundary. The official literal word at
`0x00490118` points to the 18-byte NUL-terminated string at `0x007817DC`,
SHA-256
`6e35ebc2e585a3ca08ee2d60871a7d16749421ae2b6c1a33bb20c50175e1048a`.

## Candidate, production leaf, and target closure

`components/shared/nanopb/runtime_nanopb_skip_field_candidate.c` is an altered,
production-excluded reference adaptation retained for audit and host tests.
The promoted `components/shared/nanopb/runtime_nanopb_skip_field.c` calls the
three existing source-owned providers by symbol and owns its diagnostic string
rather than adding a new stock-data dependency.

The candidate source is 2,477 bytes / SHA-256
`95bb1ab1dfda6c031613ef48939356cf2ee6c784015628718261a2716ed0bc21`;
its 2,029-byte header hashes to
`3ed7bb3bb6a998fba82e2a1bbdd9343e3d3c82f821ad4e2080a558622454976d`.
The production source is 2,417 bytes / SHA-256
`b0fbb6fc99f0a47a40e53662393a43c88b01d29d4b4457910b9f6be8063e7353`;
its 2,152-byte header hashes to
`9a76c3455119f814be099085c5fac2e2394c4a293e10c2e74d9bc33cf21866a4`.
The reviewed Apple target object is 1,212 bytes / SHA-256
`b33f904946842af2f5bd5e12429362b13f0b90943a635e1532bc3ee568699158`.

Apple Clang 21.0.0 emits:

| Allocated section | Bytes | Closure |
|---|---:|---|
| `.text.open_cfw_nanopb_skip_field` | 66 | four `R_ARM_THM_JUMP24` tail calls |
| `.rodata.open_cfw_nanopb_invalid_wire_type_error` | 18 | complete NUL-terminated diagnostic |
| `.ARM.exidx...` | 8 | CANTUNWIND companion, not a production payload candidate |

The unrelocated text hashes to
`893a37e8366996cbea7d54f63bcc81700e7feab62c4414d01b1f818aa9b77dd4`.
The relocated text is placed at `0x007B2C70`, hashes to
`31037e87e7a667852271b7fa3be6543232376b1ee6e10443517d75f1dc4126ca`,
and is followed at `0x007B2CB2` by the 18-byte diagnostic. The complete
84-byte source closure hashes to
`72fad2dba75d1fbbc06b3c0e3d250579b5116a1cb793b7886ff5c62b49f3004e`.
The text has two read-provider relocations and one each to skip-varint and
skip-string. Its only other relocations are the PREL `MOVW`/`MOVT` pair to the
leaf-owned read-only string. There is no allocated writable data.

Host tests cover all four valid wire types, provider failure propagation,
invalid values including `255`, and the upstream first-error-wins contract.
Mutation tests reject a changed stock body or caller. The audit candidate path
and symbol remain absent from production inputs, while the production source,
function, full-span redirect, and three manifest ownership regions are each
registered exactly once.

## Reproduction and remaining gate

```sh
rizin -q -n -a arm -b 16 -m 0x437fe0 \
  -c 'e asm.lines=false; pd 38 @ 0x48f6a0' \
  blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin
python3 tools/analyze_g2_nanopb_skip_field.py --json
python3 -m unittest -v tests.test_analyze_g2_nanopb_skip_field
```

The Apple-Clang profile now has exact object, text, rodata, alignment,
relocation, final-placement, overlay, component, package, and flash-layout
pins. The entry at `0x0048F6A0` uses a non-linking `B.W` and Thumb NOP fill over
the complete 74-byte stock span. Manifest ownership explicitly splits the
preceding opaque bytes, generated replacement, following opaque bytes, two-byte
alignment, 66-byte source text, and 18-byte source rodata.

Cross-profile reproduction remains pending because the reviewed Homebrew
Clang 22.1.8 executable is not present on this host and the local Docker daemon
is unavailable. No Linux object or aggregate value is inferred from the Apple
result. Signing, flashing, reset, boot, and device operation remain deferred.
