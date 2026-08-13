# Cordio WSF EFS/math exclusion audit

## Outcome

The Ambiq Cordio FreeRTOS `wsf_efs.c` and `wsf_math.c` translation units are
not linked into the G2 stock image with high confidence. This is an exclusion
result: no code bytes, candidate functions, or replacement coverage are
assigned to either file.

The conclusion combines the authenticated 7,370-function Lorelei corpus with
raw image constants/strings, retained-path inventory, expected upstream call
topology, and distinctive data-layout fingerprints. It is materially stronger
than merely failing to find a retained `__FILE__` string. It also avoids an
unnecessary 20-function decompilation effort for EFS.

## EFS structural exclusion

Official AmbiqSuite R2.5.1 `wsf_efs.c` is 19,876 bytes, SHA-256
`878125a6bb701d0875d58c05bfcb4ad770c9f95f8c09f69706959795bee7741a`,
Git blob `2b3bd045380968aa8bc7f54166434baee386f237`. Its header is 16,408
bytes, SHA-256 `b077c6e8…59ac`, blob
`e02c283ebde1498793003a480db4c0b847333df1`. R2.4.2 has byte-identical
files under the older `third_party/exactle` ancestor.

If linked with the archived defaults, the module would leave a highly
specific constellation:

- 20 functions, including three private helpers and 17 public APIs;
- six 52-byte file records (312 bytes total), with `maxSize +0`, address `+4`,
  media `+8`, size `+0x0C`, attributes `+0x10`, permissions `+0x30`, and type
  `+0x32`;
- four media pointers and 32-byte media objects with callbacks at offsets
  `+0x0C`, `+0x10`, `+0x14`, `+0x18`, and `+0x1C`;
- one shared 12-caller validator implementing unsigned handle `<6`,
  `table + handle*0x34`, and `maxSize != UINT32_MAX`;
- three internal callers of the media validator and helper fan-in through
  `WsfEfsAddFile`; and
- permission masks `0x0101`, `0x0202`, and `0x0404` in erase/get/put paths.

The complete corpus contains no such table, validator, media registration
function, callback-offset family, or coherent helper/accessor fan-in. Every
normalized `*0x34` lookalike belongs to a different first-party record system.
The canonical rejected body is `[0x00460450,0x004604C2)`, SHA-256
`7f4646808be287728ab8ed26f984b7c0d270870193427260dbf15a34a4b8ba93`:
it scans eight records, keys on field `+0x30`, returns unrelated fields, and
is called by application menu/configuration code.

Upstream EFS consumers are confined to the WDXS profile family. The stock
image and 357-path census contain no `wsf_efs`, `WsfEfs`, WDXS, or WDXC
marker, and no WDXS topology. Six generic `Unknown` strings all have unrelated
UI/state/log owners. The structure, topology, paths, and strings therefore
agree that EFS/WDXS was removed by configuration or link-time garbage
collection.

## Public implementation route if future evidence changes

Although the Ambiq file carries an ARM confidential/proprietary header, all 20
of its function bodies are byte-identical to official Apache-2.0 Packetcraft
r19.02 commit `86372d84ef0386d8834ed036e613c8f2ded1ff16`, path
`wsf/sources/port/baremetal/wsf_efs.c`, blob
`b193e8482e34223677d7936df1c9fab63cf6581a`, source SHA-256
`fd6846095df9a8a7b189f4b72679225a0244baf27c8048543d246348f9a21163`.
This supplies a clean exact public implementation route if a later stock
image proves EFS inclusion. Packetcraft r20.05 changes only the three media
callback address types/casts from integer addresses to pointers; the G2-era
Ambiq ABI uses 32-bit integer addresses.

## Math exclusion

AmbiqSuite R2.5.1 `wsf_math.c` is 3,269 bytes, SHA-256
`c914080c3e7f24de8941c5628ecb1ca962f731221baa1f6eeef4d83922250bb4`,
blob `6830b3b99bf88f446dee6cf21cf29ab5a8c790e4`. Its fallback random
generator resets four Marsaglia xorshift128 seeds and combines shifts
`<<11`, `>>19`, and `>>8`; its AES entry is only a 16-byte copy stub. Three
unique seeds are absent from both raw flash and decoded initialized SRAM, and
no corpus function has the combined shift signature. There is no retained
path, prototype consumer, or Packetcraft public implementation source.
`wsf_math.c` is therefore classified as unlinked rather than opaque.

`wsf_cs.h`, `wsf_intrinsic.h`, and `wsf_types.h` are header-only inventory.
The CS macros are proven linked through the already recovered
`WsfCsEnter`/`WsfCsExit` bodies; the intrinsic macros have no attributable
call site; the types header has no standalone code.

## Next linked target

The exclusion census found the next defensible linked WSF utility in
`wsf/sources/util/wstr.c`: `WStrReverseCpy` begins at `0x0056D8C4` and
`WStrReverse` at `0x0056D8F0`. Their exact public-source provenance and full
caller/ingress closure are the next bounded tranche. This replaces speculative
EFS work with a small source-bearing target and keeps absent modules out of
the reconstructed memory map.
