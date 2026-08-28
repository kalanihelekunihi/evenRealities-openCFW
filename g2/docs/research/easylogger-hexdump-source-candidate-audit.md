# EasyLogger `elog_hexdump` source-candidate audit

Status: **candidate qualification complete; a reviewed production derivative
is source-integrated for G2 2.2.6.10. The candidate fixtures remain excluded,
and no firmware was flashed**.

This audit covers the Apollo-main Thumb body at
`[0x0043DACC, 0x0043DC88)` and its four bounded library/transport seams in the
authenticated G2 2.2.6.10 OTA. The candidate is a source adaptation of Armink
EasyLogger's `elog_hexdump`, compiled and tested outside every firmware
manifest. Its reviewed production derivative and dedicated leaf closure are
recorded in the promotion result below. No hardware was accessed.

## Authentication and provenance

The input package is
`blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin`. The application mapping
uses the 32-byte package preamble and base address `0x00438000`.

| Artifact | Size | SHA-256 |
| --- | ---: | --- |
| OTA package | 3,523,396 | `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863` |
| Application (`package[32:]`) | 3,523,364 | `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701` |
| Stock hexdump span | 444 | `782cb65686dde396075abdd4f7c6a168bbf64962498d97446ab35e0e1670536c` |

The stock span begins with
`2de9f04f85b004000f00984600201500` and ends with
`1bf1010bd0e7fff7dbfb05b0bde8f08f`.

The oracle is compiled directly from the authenticated EasyLogger
source-equivalent snapshot at commit
`a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24`. The snapshot verifier is run
offline by the qualification suite. Its relevant pins are:

| Upstream file | Size | SHA-256 |
| --- | ---: | --- |
| `src/elog.c` | 28,740 | `d4291ab1314a34cf940c8e0d7246e05570f8d32ae0704b498cf6fbacab76acb1` |
| `inc/elog.h` | 10,428 | `2890b272a01820a6336da544c056e7735b88330cd91a5092fb83a5538de11f48` |
| `inc/elog_cfg.h` | 3,995 | `bccd34ca41c36ce8201d78fd2b844b071bad25bfbac452d02764617ca4ed3073` |

This identification is source-level and semantic, not a byte-identical claim:
the released compiler and all of its code-generation settings remain unknown.

## Released ABI and recovered seams

The public argument registers are `r0=name`, `r1=width`, `r2=buffer`, and
`r3=size`. Released code truncates `width` to 8 bits and `size` to 16 bits.
The output sink takes exactly two arguments, `(buffer, length)`; it does not
receive a log level. The formatter calls use the following exact argument
order:

```text
snprintf(log_buffer, 1024, "D/HEX %s: %04X-%04X: ",
         name, offset, offset + width - 1)
snprintf(dump_string, 8, "%02X ", byte)
snprintf(dump_string, 8, "%c", printable_byte_or_dot)
```

Direct calls recovered from the authenticated body are:

| Call site | Target | Recovered role |
| --- | --- | --- |
| `0x0043DAE4` | `0x0043C0E4` | fill `dump_string` using `(destination, count, value)` |
| `0x0043DB02` | `0x0044B63A` | substring filter helper |
| `0x0043DB0C` | `0x0043D416` | output lock |
| `0x0043DB30` | `0x0044B668` | bounded append/copy helper |
| `0x0043DB3C` | `0x0044AA76` | raw two-argument sink |
| `0x0043DB72` | `0x0044B728` | IAR `snprintf`, header |
| `0x0043DB92` | `0x0044B5A0` | IAR `strncpy`, blank byte column |
| `0x0043DBB8` | `0x0044B728` | IAR `snprintf`, hexadecimal byte |
| `0x0043DBCA` | `0x0044B668` | append hexadecimal field |
| `0x0043DBEA` | `0x0044B668` | append eight-byte separator |
| `0x0043DC10` | `0x0044B668` | append ASCII separator |
| `0x0043DC60` | `0x0044B728` | IAR `snprintf`, ASCII character |
| `0x0043DC72` | `0x0044B668` | append character/newline path |
| `0x0043DC7E` | `0x0043D438` | output unlock |

The released literals resolve as follows:

| Address | Value |
| --- | --- |
| `0x0043DC88` | `"\n"` |
| `0x0043DC8C` | shared line buffer `0x2006BD30` |
| `0x0043DC90` | `"   "` |
| `0x0043DC98` | `" "` |
| `0x0043DC9C` | `"  "` |
| `0x0043DCA0` | `"%c"` |
| `0x0043DCB4` | EasyLogger object `0x20070BE8` |
| `0x0043DCB8` | `"D/HEX %s: %04X-%04X: "` at `0x007770FC` |
| `0x0043DCBC` | `"%02X "` at `0x0078D504` |

The source candidate owns the small substring helper because that behavior is
fully described and differentially covered. Focused disassembly now also
closes the four formerly fixed code seams without importing a host libc:

| Released boundary | Authenticated result | Source treatment |
| --- | --- | --- |
| fill `[0x0043C0E4,0x0043C14A)` | 102-byte `memset` semantics with released nonstandard register order `(destination,count,value)`; low value byte is replicated and original destination is returned | local byte loop with the released argument order |
| `strncpy` `[0x0044B5A0,0x0044B610)` | standard copy/pad/return behavior; null padding branches to fill interior `0x0043C0EC` | exact eight-byte blank-column source helper |
| `snprintf` `[0x0044B728,0x0044B766)` | IAR variadic wrapper around formatter core `0x00481836` | bounded nonvariadic implementation of only the three authenticated hexdump formats |
| raw wrapper `[0x0044AA76,0x0044AA80)` | `(buffer,length)`, forces `metadata=0`, then calls level-less builder `0x00448CCC` | source raw wrapper plus source level-less G2 builder |

The raw path must not call the production three-argument formatted-output
wrapper: that sibling invokes the level-aware builder and writes record byte
`+0x0C`, whereas the level-less builder deliberately leaves that byte
untouched and starts payload at `+0x0D`.

## Ordering and arithmetic behavior

The first observable action is the eight-byte fill, before any logger gate.
The gates then run in this order: output enabled, global level at least debug
(`4`), and `strstr(name, filter.tag)` match. There is no released IPSR gate.
The output lock is acquired once after all gates and released once after the
line loop. The line buffer is not requested when the loop does not execute.

`offset`, `index`, and accumulated output length are 16-bit values. These
released behaviors are intentionally retained:

- `size == 0` locks and unlocks without calling the sink, including when
  `width == 0`.
- `width == 0 && size != 0` repeatedly emits offset `0000` forever. Tests use
  an artificial sink escape after three records; production code has no such
  escape. This compatibility path remains in the upstream-derived candidate,
  but the complete caller-width proof below makes it unreachable in this G2
  image.
- A nonterminating 16-bit offset sequence wraps. The qualification case
  `size=65535,width=2` reaches offset zero again on sink call 32,769.
- A negative header formatter result or one greater than 1,024 sets the
  16-bit accumulated length to 1,024. The newline path caps it to 1,023 before
  the final append.
- The end offset passed to the header formatter is the promoted unsigned
  expression `offset + width - 1`; at zero width it is `UINT_MAX`.

The printable test matches upstream unsigned-byte behavior: bytes in
`[0x20,0x7e]` are emitted directly and all others become `.`.

## Boundary census

An exhaustive halfword scan of the complete authenticated application found
41 direct `BL` callers and no `B.W` callers. The ordered caller-record SHA-256
is `eddd8dc16569623d78608b9f6b476c2279e51243d822f4732eed39d56a8c1ad3`;
the first caller is `0x004722BA` and the last is `0x005B210E`.

```text
004722BA 004788B2 00478DDC 00478DEC 00478E3E 00478F44 0047981E
0047B998 0047B9A8 0047BA50 0047BA5E 0047BB0C 0047BB1C 0048EF8C
0049FDFC 004A1334 004A2428 004BBEAE 004BC89C 004BCCAC 004BE2C4
004BE7E2 004C4890 005323E2 005326B0 005386DE 0057AF7C 0057C0CA
0057C156 0057C508 00588626 0058885A 00588948 00588A36 00588B20
00588BF6 00588CD2 0059F5AE 0059F940 005B1BBE 005B210E
```

The same census found no external wide or narrow branch to an interior
address, no external narrow branch to the entry, and no unaligned stored Thumb
pointer to the entry or interior. This establishes a replacement boundary for
this authenticated image only; it does not authorize a patch.

Each caller's final write to `r1` is also authenticated. Thirty-nine callers
use the exact Thumb instruction `0x2110` (`MOVS r1,#16`) and two callers,
`0x004BE7E2` and `0x0057AF7C`, use `0x2108` (`MOVS r1,#8`). There is no zero
width. The ordered `(caller,width-instruction,width,encoding)` record hashes to
`05d0d859ae08fa8b0f9b41a20335d62930e913432acd02e3f0d8e36ee5576908`.

The current source overlay replaces the stock functions containing 12 of the
41 call sites. The remaining 29 stock calls are 27 width-16 plus the same two
width-8 sites; their ordered width record hashes to
`1bf91062c55a70c5b00765e831ae15dc995902995e7b5ed44f0f559e9c78aec5`.
Every configured generated source was checked for either the candidate symbol
or the fixed entry address and none contains a hexdump call. Thus the current
generated image introduces no additional caller and the retained zero-width
compatibility behavior is unreachable.

## Raw transport closure

`0x0044AA76` has one caller, `0x0043DB3C`, and its sole dependency is
`0x00448CCC`. The level-less builder has one caller, `0x0044AA7A`. Its exact
130-byte span hashes to
`91ae986d5deaa816a662a842ecd71217c0deb0dff552ebbe04e382f16e8ebc55`
and calls allocator `0x00448A0C`, copy `0x00439BE4`, enqueue `0x00448AF0`,
recycler `0x00448A8E`, and diagnostic `0x004733EE` in that order.

The source builder preserves ready/null/zero-length rejection, low-byte
metadata defaulting, clamp-to-255, payload at `+0x0D`, terminator, 16-bit
length/metadata fields, and zero return. It deliberately does **not** preserve
stock's second-recycle defect. The openCFW ownership contract is allocation to
builder, followed by enqueue consuming the record on success or failure; the
builder never recycles after enqueue. This is an explicit safety correction,
not a claim that the source exactly reproduces the stock oracle. Its remaining
symbols are the ready/default bytes plus retained allocator, enqueue, and
diagnostic. It does not depend on or write a log level.

## Candidate and qualification artifacts

The production-excluded artifacts are:

- `components/shared/easylogger/runtime_easylogger_hexdump_candidate.[ch]`
- `components/shared/easylogger/runtime_easylogger_hexdump_seams.[ch]`
- `tests/fixtures/runtime_easylogger_hexdump_candidate_host.c`
- `tests/fixtures/runtime_easylogger_hexdump_upstream_oracle_host.c`
- `tests/fixtures/runtime_easylogger_hexdump_seams_host.c`
- `tests/test_easylogger_hexdump_candidate.py`

The focused suite now runs 19 methods. The original 14 qualifications remain:
upstream differential behavior, call ordering, formatter failure injection,
zero-width and 16-bit-wrap compatibility, whole-image hexdump topology, strict
ELF extraction, and Apple/exact-Linux determinism. Five added qualifications
authenticate the released seam spans and topology, exhaustively compare the
source fill and bounded formatters with standard oracles, exercise the
level-less record adapter's ownership and record-layout boundaries, pin all
nine per-leaf object/placement contracts, and fail closed under text, rodata,
symbol, relocation, and CANTUNWIND/PREL31 mutations.

## Deterministic target objects

Apple clang 21.0.0 (`clang-2100.3.27.1`) and exact-root Homebrew clang 22.1.8
each build two byte-identical candidate and seam objects with the reviewed
Thumb freestanding flags.

| Profile / item | Size | SHA-256 |
| --- | ---: | --- |
| Apple candidate object | 2,384 | `1daa36a1c4a3ee011cff337c74bfad06f7eb3bc36a9b75f2d67881ff9f6bb547` |
| Apple candidate text | 514 | `b590d72a5cea9fefcbab0a1b224ca032db38c853698ced7f2ee210b107a1cb87` |
| Apple candidate closure | 521 | `5e2c10b84757c891bca3dd226a2849bd1034db09f09d1ad87a7ae33334d142b9` |
| Linux candidate object | 2,352 | `4b1090c536705d393522b917b6cc1802a042670f9efb447b6cd43651ed9eb740` |
| Linux candidate text | 500 | `23b05264d4c99fa4e79ee0b5f422def9156cee4d53d88a96adb84c2db83aa051` |
| Linux candidate closure | 507 | `c0d7f4bc418cfc9a7d7a79f9e994d746c5817a70aa46855769da3f226857c420` |
| shared candidate rodata | 7 | `9f702654a35832eb92db88b74ff52483e0afacca06a1e79c14f86041105b762e` |
| Apple seam object | 5,072 | `60f1fd2587e56234f3959cb437648b4663697c98b34ad57a49bb5e65e10d1307` |
| Linux seam object | 5,048 | `3448cae3bf4e0398a5560f72a279fc025e9b417898196c343eb102a262a6669a` |

The candidate has 23 exact text relocations: 15 source-owned Thumb calls and
four local ROPI string pairs. The strict relocated candidate closures hash to
`c14b607ec21fd8ba87cc62cf666a87d59bd589d899047892a4d0fe1caebc441f`
on Apple and
`4471c11778e3ec2457766ce9d093a8473dc06ce4fd6abbe78b144a9761c4b96f`
on Linux. The exact candidate rodata is `20002020000a00` (`" "`, `"  "`,
and `"\n"`). An independent mini-linker reproduces both closures.

The seam object contains nine pinned text sections. Its raw wrapper has one
local `R_ARM_THM_JUMP24` relocation to the level-less builder. The builder's
only undefined symbols are the five explicit retained transport dependencies;
there are no writable allocated sections. Each selected function has an exact
eight-byte CANTUNWIND companion with the authenticated `R_ARM_PREL31` contract.

## Strict production-excluded placement rehearsal

The rehearsal begins at the reviewed current production tail, aligns the
candidate to four bytes, and then places the nine seam leaves in source order.
The digit table is owned once by `put_hex` and referenced by `format_hex`; the
enqueue diagnostic string is owned once by the builder. No interval overlaps.
Promotion of the production single-owner builder reduced both reviewed
production overlays by 12 bytes. The rehearsal therefore moves every candidate
and seam address down by exactly `0xC`; object bytes and span sizes are
unchanged, while relocation-dependent closure digests are repinned.

| Profile | Production tail | Candidate | Final end | Added span from tail |
| --- | ---: | ---: | ---: | ---: |
| Apple | `0x007B1E8E` | `0x007B1E90` | `0x007B243E` | 1,456 |
| exact-root Linux | `0x007B25CA` | `0x007B25CC` | `0x007B2B5E` | 1,428 |

| Leaf | Apple address | Apple closure | Linux address | Linux closure |
| --- | ---: | ---: | ---: | ---: |
| fill | `0x007B209C` | 84 | `0x007B27C8` | 84 |
| header formatter | `0x007B20F0` | 232 | `0x007B281C` | 232 |
| bounded put | `0x007B21D8` | 22 | `0x007B2904` | 22 |
| hex put + shared digits | `0x007B21F0` | 251 | `0x007B291C` | 247 |
| byte formatter | `0x007B22EC` | 34 | `0x007B2A14` | 34 |
| character formatter | `0x007B2310` | 8 | `0x007B2A38` | 8 |
| blank column | `0x007B2318` | 22 | `0x007B2A40` | 22 |
| level-less builder + diagnostic | `0x007B2330` | 262 | `0x007B2A58` | 256 |
| raw submit | `0x007B2438` | 6 | `0x007B2B58` | 6 |

The relocated level-less builder closures now hash to
`5f81838fc52b3cb040e303ff635a60e2e1f470e21d2c0dd17fdf97b8a8f9c8e1`
on Apple and
`9782fd47c8147ed31323771afc08e9206e2f7f5af4c5a83c598aec0b28629227`
on Linux. These are the only seam-leaf closure digests changed by the uniform
placement shift because the builder alone branches to fixed retained targets.

The qualification records, per leaf and per compiler, exact text bytes,
selected-symbol metadata, zero or one owned rodata section, every relocation,
the relocated text/closure digest, and its selected-function
CANTUNWIND/PREL31 row. Independent mini-linking supports `R_ARM_THM_CALL`,
`R_ARM_THM_JUMP24`, absolute MOVW/MOVT, and PREL MOVW/MOVT. The exact-root
Linux production baseline was also reproduced at 123,558 bytes and SHA-256
`f2c33def6131981c1a283968bc02bd55cde32536f4f33a7fa3cbf905d42693fc`;
the compilation root is material and is part of that reviewed profile.

## Production promotion result

The separate production review is complete for G2 2.2.6.10. The production
overlay replaces three complete, authenticated, end-exclusive stock spans:

| Stock span | Bytes | SHA-256 | Production target |
| --- | ---: | --- | --- |
| `elog_hexdump` `[0x0043DACC,0x0043DC88)` | 444 | `782cb65686dde396075abdd4f7c6a168bbf64962498d97446ab35e0e1670536c` | `open_cfw_easylogger_hexdump` |
| level-less builder `[0x00448CCC,0x00448D4E)` | 130 | `91ae986d5deaa816a662a842ecd71217c0deb0dff552ebbe04e382f16e8ebc55` | `open_cfw_g2_easylogger_async_record_build_level_less_single_owner` |
| raw submit `[0x0044AA76,0x0044AA80)` | 10 | `a509174409c14871498cd505c5246e02d78cd9cf067100b83aff576842b3e123` | `open_cfw_easylogger_hexdump_raw_submit` |

Every site is a generated `B.W` followed by `0xBF00` NOP fill. The builder and
raw spans end exactly where the already-reviewed level-aware builder and
formatted submit patches begin, at `0x00448D4E` and `0x0044AA80`; the global
patch interval set is disjoint. The hexdump literal pool beginning at
`0x0043DC88` remains byte-identical.

The production sources are the MIT upstream-derived
`runtime_easylogger_hexdump.c/.h` pair and the MIT clean-room
`runtime_easylogger_hexdump_support.c/.h` pair. Their pins are:

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `runtime_easylogger_hexdump.c` | 6,542 | `7339a56f6e14ba5ffbbf506f1e1e80a9a19b19b0b455844a9e41a977801b8e6f` |
| `runtime_easylogger_hexdump.h` | 5,111 | `9e4d147b2441282cd49a54e1be4443a8a25498498b6e301ee69ca9407751f82c` |
| `runtime_easylogger_hexdump_support.c` | 9,910 | `1df9bbd35892888eee6412441958b2a2c6d60818caab2dbdf729f178d779446a` |
| `runtime_easylogger_hexdump_support.h` | 2,166 | `10fa9e61a9b87defd0c67eca4a5bf0d9ad1271f8a6806c6791809af0160d2ba6` |

Production places ten strict relocated leaves in dependency order. Unlike the
historical rehearsal, independently linked leaves cannot share an unowned
digit-table section. `put_hex` and `format_hex` therefore use equivalent
bounded uppercase arithmetic (`0`-`9`, `A`-`F`). Dedicated host tests execute
all 256 byte values, padding widths, and truncation/termination boundaries.

| Production leaf | Apple address / closure | Linux address / closure |
| --- | ---: | ---: |
| bounded put | `0x007B1E90` / 22 | `0x007B25CC` / 22 |
| arithmetic hex put | `0x007B1EA8` / 268 | `0x007B25E4` / 264 |
| fill | `0x007B1FB4` / 84 | `0x007B26EC` / 84 |
| header formatter | `0x007B2008` / 238 | `0x007B2740` / 238 |
| byte formatter | `0x007B20F8` / 48 | `0x007B2830` / 48 |
| character formatter | `0x007B2128` / 8 | `0x007B2860` / 8 |
| blank column | `0x007B2130` / 22 | `0x007B2868` / 22 |
| level-less builder + diagnostic | `0x007B2148` / 262 | `0x007B2880` / 256 |
| raw submit | `0x007B2250` / 6 | `0x007B2980` / 6 |
| `elog_hexdump` + rodata | `0x007B2258` / 521 | `0x007B2988` / 507 |

The main/builder/raw relocation contracts contain exactly 23/9/1 records on
both compilers. The raw wrapper routes only to the level-less builder. That
builder leaves record byte `+0x0C` untouched and has no recycler, event-set,
level-aware-builder, or formatted-submit route. Its only external transport
dependencies are ready/default-metadata, allocator, consuming enqueue, and
diagnostic; the local error string is its sole read-only closure.

Whole-image scanning authenticates exactly 41 `BL` callers of `elog_hexdump`,
one caller of raw submit (`0x0043DB3C`), and one caller of the level-less
builder (`0x0044AA7A`). There are no external `B.W`, wide conditional, narrow,
interior, or stored Thumb-pointer references into any of the three spans.

| Profile | Overlay | Apollo-main component | Core-source package |
| --- | --- | --- | --- |
| Apple Clang 21.0.0 | 123,197 / `bb870969ad9913e2cc4f012c0abec05b5a946bfbcaff4ab3cf7d7ac3b1e08966` | 3,646,593 / `24bb10715c6650429bcdbe0b2942f8b1a16ddd9b2f6aa2a65a69361df2611c7f` | 4,425,047 / `24d4b6527621c87622a5fdee96c63d266f10c3452e0a52322386ad717084b81c` |
| exact-root Linux Clang 22.1.8 | 125,023 / `47f588845f4bd202d1d184282996cf45dd2cb514b4795ac9cdd5a7835da90d02` | 3,648,419 / `df9a1b00038d07ea0137258cc879547ecc86a11a737d1954bd1f4babd259c8e3` | 4,426,873 / `2eef6375f1ac218701f438afd8f5b5752b789a20db1e73f6dfd71486acc94423` |

The historical placement rehearsal above remains frozen as independent
candidate/mini-link evidence; it is no longer asserted to equal the current
production tail. Candidate source and host fixtures remain absent from every
firmware input. Production applicability is limited to the authenticated G2
2.2.6.10 topology, and the authentic `width == 0 && size != 0` behavior remains
unchanged. No image was signed or flashed and no hardware was accessed.
