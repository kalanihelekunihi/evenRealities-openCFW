# LZ4 stock reachability and memory-provider authentication audit

Status: **gate passed for the official-image reachability and stock memory-provider
questions covered here**. This does not by itself promote upstream LZ4: the
closure-aware relocation tooling, dual-profile production pins, integration
tests, and release gates in
`lz4-upstream-production-promotion-plan.md` remain separate requirements.

## Scope and authoritative image

This audit answers two production-promotion questions:

1. After retargeting the stock safe-wrapper entry, can any direct branch or
   stored code pointer still reach the stock safe wrapper, generic decoder,
   variable-length reader, or an interior instruction of those functions?
2. Can the selected upstream decoder object's `__aeabi_memcpy` and
   `__aeabi_memmove` calls safely bind to the two authenticated stock provider
   entry addresses, including every return and tail path used by those
   providers?

The authoritative input is
`blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin`:

| Image | Bytes | SHA-256 |
|---|---:|---|
| Complete package | 3,523,396 | `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863` |
| Apollo application after the 32-byte preamble | 3,523,364 | `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701` |

Application runtime addresses use base `0x00438000`. All spans below are
half-open; the parenthesized address is the equivalent inclusive last byte.

| Function | Authenticated runtime span | Bytes | SHA-256 |
|---|---:|---:|---|
| EvenHub mode-2 adapter | `[0x004E0C0C, 0x004E0C34)` (`0x004E0C33`) | 40 | `c97a5644f2451934f190a189006304f2a01f8b732fa5dd08711a2cc8272e5fc2` |
| LZ4 variable-length reader | `[0x0054EE90, 0x0054EF08)` (`0x0054EF07`) | 120 | `ac7afc67dfe6e35d5ccf23ba3e232439b75084fb80ae8b997674c0e473412a55` |
| Stock generic decoder | `[0x0054EF08, 0x0054F338)` (`0x0054F337`) | 1,072 | `8d8e6a9598ea565a6ca9b7fa1a41a67a2b1756b8fb43e84e684ed5b11de990ae` |
| Stock safe wrapper | `[0x0054F338, 0x0054F356)` (`0x0054F355`) | 30 | `d824bb067efb6bac662409f00f466631da69272c25c9bea6134c658e713eaef1` |
| Stock `__aeabi_memmove` provider | `[0x00439710, 0x004397A6)` (`0x004397A5`) | 150 | `31caf15ad676c4a99eace5673e1fe46b818b64d901707c461074e8acc5474b28` |
| Stock `__aeabi_memcpy` provider | `[0x00439BE4, 0x00439C8A)` (`0x00439C89`) | 166 | `8e696e1fb54917a436f850e562f74e8cc8734c259fdaac9f767a3c264ff427cd` |

Two short boundary byte strings provide an additional check on the patched
entries:

- mode-2 adapter: `10b51400002805d0002c03d0002901d0002b01d1002006e00a0021006ef086fb012800da002010bd`
- safe wrapper: `18b585b0002404940024039402910024019400240094fff7dbfd06b010bd`

## Full-image control-flow audit

The entire application was scanned at every halfword. The decoder covered
Thumb `BL`, `B.W`, wide conditional `B<c>.W`, narrow unconditional and
conditional `B`, and `CBZ`/`CBNZ`. Targets were checked against every audited
entry and every interior halfword. Candidate halfwords were then classified
against instruction ownership so that the second halfword of a 32-bit
instruction or aligned data could not be reported as executable control flow.

For the digests below, an address list is serialized as sorted little-endian
32-bit addresses. A call-record list is serialized as each little-endian
32-bit source address followed immediately by the four encoded instruction
bytes shown in the table.

### LZ4 direct entry routes

| Target | Source | Encoding | Decoded operation |
|---|---:|---|---|
| mode-2 adapter `0x004E0C0C` | `0x004968EA` | `4af08ff9` | `BL` |
| mode-2 adapter `0x004E0C0C` | `0x005498D2` | `97f79bf9` | `BL` |
| mode-2 adapter `0x004E0C0C` | `0x00549AD8` | `97f798f8` | `BL` |
| reader `0x0054EE90` | `0x0054F046` | `fff723ff` | `BL` |
| reader `0x0054EE90` | `0x0054F12E` | `fff7affe` | `BL` |
| generic decoder `0x0054EF08` | `0x0054F34E` | `fff7dbfd` | `BL` |
| safe wrapper `0x0054F338` | `0x004E0C28` | `6ef086fb` | `BL` |

Set authentication:

| Target | Address-set SHA-256 | Address-plus-encoding SHA-256 |
|---|---|---|
| mode-2 adapter | `1fd7b5a21b3ea9fac3b5837f0cedcd4fc1be4404d57e4bf101a59d440761219d` | `27b6bbd1ade0f0c74b60719799b3fe85ea91aceed06785b3585bfc2ae08c11f0` |
| reader | `cce36c58ebe10e0819affb1c4c0c288c78e5ef965d6ddf8ed3ddc3919b84de81` | `713e4a162469d41b5242fa15a9e9a21216ac3b31263131f1d36b9f04f9fc03f9` |
| generic decoder | `21b846304d8e78fe37297dce99e28c630359d835b1082d1430e96cf47fa43798` | `477a63d27a3d5d6dbf002a9b566aa507de2157c754ed8405035718035ef137d9` |
| safe wrapper | `d79ff87f2439c0e33ae251679b71394f848a5d92db37c72adc2dd0aa0c7b7e71` | `7918475e843ec0b67e5c4fb492910a4a0076e0e9b1d554081b72f76bc2656ca3` |

There is no real external `B.W`, wide conditional branch, narrow branch, or
`CBZ`/`CBNZ` route to those entries. There is also no valid external branch
to an interior instruction in any of the four LZ4 spans. Interior targets that
remain after instruction classification are ordinary internal control flow
within their owning function; one example is the generic decoder's wide
conditional branch at `0x0054F262` to `0x0054F0C2`.

Two raw narrow-branch decoder matches initially appeared to target generic
decoder interiors, but neither source is an instruction boundary:

- At `0x0054EA74`, halfword `0xE364` would independently decode as a narrow
  branch to `0x0054F140`. It is the second halfword of the real 32-bit
  instruction at `0x0054EA72`, bytes `dff864e3`, an `ldr.w`.
- At `0x0054EE00`, halfword `0xD464` would independently decode as a
  conditional branch to `0x0054EECC`. It is the low halfword of aligned data
  word `0x0070D464` in the address table immediately before code beginning at
  `0x0054EE18`.

The resulting live chain is therefore complete and closed:

`three application callers -> mode-2 adapter -> safe wrapper -> generic decoder -> reader`

Retargeting the safe-wrapper entry removes the only external route into the
stock generic decoder, which in turn removes both routes into the reader.

## Stored-pointer audit

Every byte offset of the application was checked as a 32-bit window, rather
than checking only naturally aligned words. The scan searched both exact even
entry addresses and stored Thumb addresses (`entry | 1`), then canonicalized
the low bit and searched every interior address of all six authenticated
spans.

There are zero exact even or Thumb entry-pointer encodings for the mode-2
adapter, reader, generic decoder, safe wrapper, `memmove`, or `memcpy`. There
are also zero raw canonicalized interior collisions for every span except the
generic decoder. Its eight raw byte-pattern collisions are all instruction
bytes, not stored pointers:

| Window location | Raw value | Canonical target | Owning bytes / classification |
|---:|---:|---:|---|
| `0x0046AB9B` | `0x0054F0F8` | `0x0054F0F8` | Unaligned window crossing `dff8f054`, the `ldr.w` at `0x0046AB9A`, and the next byte |
| `0x004996C8` | `0x0054F115` | `0x0054F114` | `15f15400`, `adds.w r0,r5,#0x54` |
| `0x0049A0F8` | `0x0054F115` | `0x0054F114` | `15f15400`, `adds.w r0,r5,#0x54` |
| `0x005189C0` | `0x0054F10D` | `0x0054F10C` | `0df15400`, `add.w r0,sp,#0x54` |
| `0x005687F0` | `0x0054F117` | `0x0054F116` | `17f15400`, `adds.w r0,r7,#0x54` |
| `0x0056883A` | `0x0054F114` | `0x0054F114` | `14f15400`, `adds.w r0,r4,#0x54`, halfword-aligned |
| `0x00568858` | `0x0054F114` | `0x0054F114` | `14f15400`, `adds.w r0,r4,#0x54`, word-aligned |
| `0x005696C8` | `0x0054F115` | `0x0054F114` | `15f15400`, `adds.w r0,r5,#0x54` |

The sorted `(window location, raw value, canonical target)` records, each
serialized as three little-endian 32-bit words, have SHA-256
`60d76d5caf1a830a3202c1c8c9c47929eec4ab376741b7507a4f9519a79d84b4`.
Five values happen to be odd/Thumb-looking and three are even; six windows are
word-aligned, one is only halfword-aligned, and one is byte-unaligned.
Alignment alone is therefore insufficient, but instruction ownership proves
all eight false as pointer references.

## Selected upstream object's memory calls

The Apple-clang candidate was independently rebuilt using the plan's pinned
Cortex-M55 Thumb, freestanding, `-O2`, sectioning, ROPI, and hardening flags.
The object is 90,780 bytes with SHA-256
`5df6949c8e67061fe59a27e0c0a427bf31a7e9a8235e8cc643234b036c721b0b`.
Its selected `.text.unlikely.LZ4_decompress_safe` section is 1,660 bytes,
alignment 4, SHA-256
`3bb106d1a943c19f0c3f6e2252ae1fbb2bbb78a8a69772e4729a15596bc9da49`.

The selected section has exactly these external memory-call relocations:

| Section offset | Relocation | Target | Argument/return observation |
|---:|---|---|---|
| `+0xF4` | `R_ARM_THM_CALL` | `__aeabi_memcpy` | At `+0xEE/+0xF0/+0xF2`, `r0 = r10` (destination), `r1 = r5` (source), `r2 = 0x10` (count). Following code does not consume the returned `r0`. |
| `+0x636` | `R_ARM_THM_CALL` | `__aeabi_memmove` | At `+0x632/+0x634`, `r0 = r10` (destination), `r1` retains the source, and `r2 = r4` (count). At `+0x63A`, code loads a new `r0`, so no return value is consumed. |

These are AAPCS EABI void-provider calls with `(r0 destination, r1 source,
r2 count)`. They are not calls that rely on ISO C `memcpy`/`memmove` returning
the original destination.

## Stock provider reachability and complete path analysis

### `__aeabi_memcpy` at `0x00439BE4`

The provider performs a forward copy from `r1` to `r0` for `r2` bytes. A zero
count takes the `CBZ` return at `0x00439C40`; other paths return at either
`0x00439C40` or `0x00439C88`. The wide-copy path preserves `r4` and `r5` with
paired push/pop operations. No callee-saved register is left clobbered.

The routine advances `r0` while copying instead of restoring the original
destination. It is therefore valid as the void EABI provider used by the
candidate, but must not be declared or exposed as an ISO C `memcpy` whose
caller consumes a returned destination pointer.

The canonical start has 790 external `BL` callers. In addition, the stock
`memmove` non-overlap path makes one non-linking `B.W` tail transfer from
`0x00439718`, for 791 direct routes total. The sorted little-endian address set
has SHA-256
`84686c724f478f6543364c6ae5677839118aadbabd783111127c887f8ec78b09`;
the address-plus-encoding record set has SHA-256
`47755a50a71bd6c444810944e4b2b0c6e485e9ecb2077b4f5e152fb54564cd11`.
The first sorted source is the `memmove` tail at `0x00439718`; the last `BL`
source is `0x005F3C3E`.

There is also a genuine alternate entry at `0x00439C04`, used by 597 external
`BL` callers. Its sorted address set has SHA-256
`150840e78264efb86706a5f10f436ecce01a2226bcf3b15d48b03b443e0058ad`
and its address-plus-encoding records have SHA-256
`b8e9b863994373fc7f7f04a751c077af9b89d8deab95679edef365528282911a`;
the first and last sources are `0x00440776` and `0x005F8F58`.
This alternate aligned-copy entry is not the candidate relocation target, but
it is why the complete 166-byte provider span must remain authenticated and
pinned. The candidate binds only to canonical start `0x00439BE4`.

The stock generic decoder's ten calls all target that canonical start:

`0x0054EF9C`, `0x0054EFAC`, `0x0054EFBC`, `0x0054EFF8`, `0x0054F1DA`,
`0x0054F208`, `0x0054F25A`, `0x0054F2AE`, `0x0054F2CA`, and `0x0054F31E`.

Their encodings, in the same order, are `eaf622fe`, `eaf61afe`, `eaf612fe`,
`eaf6f4fd`, `eaf603fd`, `eaf6ecfc`, `eaf6c3fc`, `eaf699fc`, `eaf68bfc`, and
`eaf661fc`. There is no generic-decoder call to the alternate entry.

### `__aeabi_memmove` at `0x00439710`

The provider compares source and destination and computes the source end.
For `destination <= source` or `destination >= source + count`, including a
zero count, it makes a non-linking tail `B.W` from `0x00439718` (bytes
`00f064ba`) to canonical `__aeabi_memcpy` at `0x00439BE4`. Because the branch
does not replace `lr`, the `memcpy` return goes directly to the original
`memmove` caller.

For the overlapping case `source < destination < source + count`, the
provider computes the source and destination ends and copies backward through
its alignment, word, halfword, and byte loops. Every backward path returns at
one of two sites:

- `BX LR` at `0x00439730` from the initial byte-alignment loop; or
- `BX LR` at `0x0043976C` after the shared word/halfword/byte tail. Branches
  from `0x00439788` and `0x004397A4` converge at `0x0043975A` and then reach
  this return.

Any use of `r4` and `r5` is protected by paired push/pop operations. The
overlap path advances `r0` to the destination end, so this provider likewise
satisfies the EABI void contract but must not be presented as a C-return-value
implementation.

There are 12 external `BL` callers to the canonical entry:

`0x00438FE0`, `0x0043902A`, `0x00454760`, `0x00524D90`, `0x0054F0E6`,
`0x0054F1BA`, `0x0056789E`, `0x00591474`, `0x00599594`, `0x005D8EAE`,
`0x005EABA0`, and `0x005F520C`.

Their sorted little-endian address set has SHA-256
`a3650e0944f51e2216357bcf8aceaee7ce3308f63a7e0bc8377d03d39839196b`;
their address-plus-encoding records have SHA-256
`e05f4eabbbbda1db0bae3f1552595e9bb0515bbe760c8969026e3d7b9393ffa8`.
There is no external branch into a `memmove` interior. The stock generic
decoder calls it at `0x0054F0E6` (`eaf613fb`) and `0x0054F1BA`
(`eaf6a9fa`).

The `memmove` tail makes `memcpy` a transitive dependency even in a candidate
that did not call `memcpy` directly. This candidate has both relocations, so
both dependencies are explicit.

## Gate conclusion

The official-image reachability gate passes:

- retargeting the safe-wrapper entry cuts the only external path to the stock
  generic decoder and reader;
- no valid direct branch enters an LZ4 interior;
- no stored even or Thumb code pointer retains an indirect route; and
- the eight raw generic-interior byte matches are proven instruction bytes,
  not pointers.

The memory-provider authentication gate also passes with an explicit opaque
dependency policy:

- bind only `__aeabi_memcpy` to `0x00439BE4` and `__aeabi_memmove` to
  `0x00439710`;
- preserve and authenticate the complete provider spans listed above,
  including the `memcpy` alternate entry and the `memmove -> memcpy` tail;
- type and name the providers as EABI void routines, never as ISO C functions
  whose return values are usable; and
- retain these two stock spans as named binary dependencies until reviewed
  source-owned EABI shims replace them.

No newly observed LZ4 caller, interior target, stored pointer, ABI mismatch,
unhandled return path, or provider-tail blocker was found.

## Validation note

`python3 third_party/lz4/verify_snapshot.py` passed against the authenticated
upstream snapshot. The selected Apple object, section, relocations, call-site
register use, and official provider disassembly were independently checked as
part of this audit.

The full candidate unittest could not be used as an integration result in the
shared worktree during this audit: concurrent promotion work had already
renamed the production decoder symbol to its `_legacy` name while the existing
test setup still requested the former production symbol, so setup failed
before any test case ran. That transient integration mismatch does not affect
the read-only official-image or independently rebuilt-object findings above,
but a clean candidate and full-suite run remains required by the production
promotion plan.
