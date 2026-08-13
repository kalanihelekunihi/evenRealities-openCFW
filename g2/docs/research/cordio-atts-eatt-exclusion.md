# Cordio enhanced ATT server exclusion audit

Status date: 2026-08-09  
Target: G2 `s200_v2.2.6.10` Apollo main

## Outcome

The optional `atts_eatt.c` translation unit is not linked into the stock G2
image. All twelve Packetcraft r20.05c definitions are source-only/dead-stripped
for this product configuration. No stock function span is assigned to them.

This is a positive initialization and provider-closure result. The closed
`AttHandlerInit` installs `eattFcnDefault=0x007851F0` at
`attCb.pEnServer` (`attCb=0x200610AC`, offset `+0x44`). A linked `EattsInit`
must replace that pointer with the TU-owned `attsFcnIf`. The entire image has
exactly five literal cells for `attCb`, all owned by the already-closed ATT,
ATTC, and ATTS objects; none implements that replacement. The default no-op
enhanced-server interface therefore remains installed.

The absence is independently closed through the function topology:

- `eattsGetFreeSlot`, enhanced data indication, and
  `EattsContinueWriteReq` must call `attCcbByConnId`; its complete stock caller
  list contains only the three legacy core calls at `0x004B4E10`,
  `0x004B4E58`, and `0x004B5208`.
- The four enhanced indication/notification wrappers must call
  `attsHandleValueIndNtf`; its only callers are the two linked legacy wrappers
  at `0x00533ED2` and `0x00533EEE`.
- Enhanced data-confirm and connection callbacks are rooted only by the
  absent `attsFcnIf` initializer. The local multi-notification length helper
  is rooted only by the absent public multi-value API.
- The separately audited `l2c_coc.c` TU has zero linked functions, so no
  enhanced credit-based bearer can deliver these callbacks.
- The image contains no `atts_eatt.c`, `eattsGetFreeSlot`,
  `EattsMultiValueNtf`, or `EattsContinueWriteReq` marker.

The public zero-copy allocator `AttMsgAlloc` is also source-only in the closed
ATT core, consistent with both enhanced zero-copy wrappers being absent.

## Source inventory

The excluded definitions are `eattsGetFreeSlot`, `eattsL2cCocDataInd`,
`eattsL2cCocDataCnf`, `eattsConnCback`, `eattMultiNtfLen`,
`EattsMultiValueNtf`, the four indication/notification wrappers,
`EattsContinueWriteReq`, and `EattsInit`. Their exact source-span hashes are
pinned in `packetcraft-cordio-atts-eatt-function-map.tsv`.

Packetcraft r20.05 through r20.05c and the later official AmbiqSuite R4.4.1
import share the exact Apache-2.0 file:

```text
blob    f1ca4879c8c32ef42127971399592329ca084680
bytes   16,713
sha256  99d169c7e0066186fb6d1ebfe718f36c84a45eddf54b4a99091747deedc51355
```

No stock body survives to distinguish releases. This file is the compatible
optional source beside the independently proven r20/R4 three-bearer ATT ABI,
not evidence that EATT is enabled in the product.

## Reproduction

```sh
python3 tools/analyze_g2_cordio_atts_eatt.py --json
python3 -m unittest tests.test_analyze_g2_cordio_atts_eatt
```

Production ownership and source replacement remain zero. The next optional
ATT server census is `atts_dyn.c`; it should be classified independently from
EATT because dynamic database APIs can exist on the legacy bearer.
