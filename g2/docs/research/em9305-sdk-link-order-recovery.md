# EM9305 SDK link-order and modified-function recovery

Status date: 2026-08-08

## Result

The authenticated `lib_emb_controller_iso.a` object order supplies a second,
independent provenance lane after exact byte matching. Case-sensitive symbol
order is monotonic at 99.596% of adjacent exact anchors (five inversions among
1,240 comparisons), consistent with final placement by sorted `.text.*`
section name. A fail-closed gap-tiling pass uses that order only when:

- both neighboring symbols are unique exact stock anchors in increasing
  address order;
- one to three unique archive symbols occur between those anchors;
- their complete archive sizes exactly tile the stock gap; and
- the proposed range does not overlap the existing exact-function map.

The strict pass finds 36 such ranges and identifies 46 functions / 2,116 bytes. Sixteen functions
/ 784 bytes are byte-exact archive bodies whose duplicate raw match locations
were disambiguated by link order. The other 30 functions / 1,332 bytes are
function-provenance identified but are deliberately excluded from exact-byte
coverage: 11 have fewer than eight compared bytes, ten are relocation-only
stubs, and nine are same-size vendor/configuration-modified functions.

| Evidence state | Functions | Bytes | What is proven |
|---|---:|---:|---|
| Exact body, placement resolved by link order | 16 | 784 | symbol, address, size, and complete normalized archive body |
| Link-order identified, low compared-byte count | 11 | 88 | symbol, address, and size; insufficient bytes for the exact-match floor |
| Link-order identified, relocation-only | 10 | 40 | symbol, address, and stub size; body bytes are link relocations |
| Same-size vendor/configuration-modified | 9 | 1,204 | symbol, address, size, and upstream role; stock body differs |
| **Total** | **46** | **2,116** | function provenance, with the tier-specific limits above |

A NOP-aware extension removes only boundary `nop_s` instructions before
tiling and accepts a bounded 2–32-byte delta only when exactly one unique SDK
symbol lies between the exact anchors and the archive body is at least half
the stock span. It adds 120 ranges / 156 functions / 9,818 stock bytes: 34
exact bodies / 774 bytes, 48 low-compared-byte functions
/ 480 bytes, 32 relocation-only stubs / 128 bytes, 29 same-size modified
functions / 4,496 bytes, and 13 singleton size-delta functions / 3,940 stock
bytes (3,820 archive bytes).

Across both passes, 156 ranges identify 202 functions / 11,934 bytes. The
authenticated vector ABI additionally resolves four duplicate interrupt
handlers / 760 bytes. Three / 574 bytes are exact SDK bodies; the 186-byte
radio-TX role is vector-proven but differs from the SDK's 380-byte TX body.
An authenticated `lib_em_system.a` prefix resolves six repeated four-byte
return leaves / 24 bytes at the exact end of the `EMSS_LeRand` left anchor.
Exact coverage is **1,494 functions / 157,122 bytes in 875 merged intervals**,
or **74.504950%** of the 210,888-byte application. Including every
tier-qualified placement identifies function provenance for **167,684 bytes
in 879 merged intervals**, or **79.513296%**. The remaining **43,204 bytes
(20.486704%)**
are not yet function-provenance identified; the residual census separately
classifies 9,546 of them as vectors, alignment, or post-text tables/data and
leaves 33,658 bytes as unresolved code or mixed content.

The archive-size ratio guard deliberately rejects
`lctrActPeerPhyReqWithCollision`: its four-byte archive relocation stub cannot
explain the 36-byte stock gap even though the neighboring symbols and absolute
size delta happen to fit. It remains in the unresolved queue. This negative
case prevents exact-neighbor order from turning a weak symbol-role inference
into a false function-boundary claim.

## Vector-resolved duplicate handlers

The authenticated SDK oracle commit
`e4412bc98d4e76d441d1226ca3696e53cfae5f54` / tree
`f5cb9ba00df71c2612d6d64cf39e05615a2feb64` supplies
`common/9305/includes/interrupts.h` blob
`8514b28756c0aeac44134404d1222c190ff4bcee` (SHA-256 `87505b42…d8f`)
assigns IRQ 0/1 to ARC timers 0/1 and IRQ 20/21 to radio TX/RX. ARC IRQ entries
begin at vector word 16. Stock and archive evidence therefore resolve:

| Vector word / IRQ | Stock address | Identity | Stock / SDK bytes | State |
|---:|---:|---|---:|---|
| 16 / 0 | `0x00305B1C` | `IRQHandler_ArcTimer0` | 194 / 194 | exact normalized SDK body |
| 17 / 1 | `0x00305BE0` | `IRQHandler_ArcTimer1` | 194 / 194 | exact normalized SDK body |
| 36 / 20 | `0x00306440` | `IRQHandler_RadioTx` | 186 / 380 | role/boundary identified; vendor-modified body, excluded from exact coverage |
| 37 / 21 | `0x00306384` | `IRQHandler_RadioRx` | 186 / 186 | exact normalized SDK body |

The two timer definitions share one normalized archive hash and each match both
timer locations; the vector slots disambiguate their names. The SDK radio-RX
body matches both stock radio locations, but the TX vector slot—not body
similarity—establishes the TX role. It is consequently recorded as modified
rather than falsely promoted as a second radio-RX function. Each body ends at
an authenticated `nop_s` boundary. Round-four Ghidra decompilation independently
confirmed the interrupt save/callback/`rtie` shape at the two sampled entries.

## Authenticated EM-system short prefix

The authenticated `lib_em_system.a` artifact (Git blob
`47acd3c20c78d983b605267b18d4f8d6eb1e50d1`, SHA-256
`390b2d610c01b79a01b461dc5c88c7aa249e7bbd46d528455bce3dbce93f7b96`)
contains six lexically ordered `EMSRC_RfUtils.c.obj` definitions with the same
complete four-byte normalized body. Stock contains exactly six consecutive
copies at `[0x0030592C,0x00305944)`, beginning at the exact end of the unique
`EMSS_LeRand` anchor; the next four stock bytes differ, and the unique
`EMSystem_TransmitCM` right anchor begins at `0x00305AB4`. This complete-run
and stop-byte guard resolves the otherwise indistinguishable copies:

| Stock address | SDK symbol | Bytes |
|---:|---|---:|
| `0x0030592C` | `EMSystemStack_ReceiveStart` | 4 |
| `0x00305930` | `EMSystemStack_ReceiveStop` | 4 |
| `0x00305934` | `EMSystemStack_StartAdvertising` | 4 |
| `0x00305938` | `EMSystemStack_StartScan_15_4` | 4 |
| `0x0030593C` | `EMSystemStack_TransmitStart` | 4 |
| `0x00305940` | `EMSystemStack_TransmitStop` | 4 |

All six bodies hash to
`df76b0aba1f705436023e9ee970e8c37d8da26059a7798d11b602b9a118d51d8`.
The inference is bounded to this complete anchored run; it is not a general
promotion of repeated four-byte bodies.

All 210,888 application bytes remain stock-retained. These results improve
identity and semantics, not source ownership or redistribution status.

## Per-function placement ledger

### Exact body, duplicate location resolved

| Stock address | SDK symbol | Bytes |
|---:|---|---:|
| `0x00307970` | `LctrMstExtInitClearScanPhy` | 16 |
| `0x00307B60` | `LctrMstExtScanIsEnabled` | 16 |
| `0x00307B8C` | `LctrMstExtScanSetScanPhy` | 16 |
| `0x0030C72C` | `LlReadLocalResolvableAddr` | 60 |
| `0x0030E3FC` | `LmgrBuildRemapTable` | 48 |
| `0x003143F4` | `bbBleCancelOp` | 20 |
| `0x00314408` | `bbBleExecOp` | 20 |
| `0x00314558` | `bbBleStartBleDtm` | 16 |
| `0x00319958` | `lctrExtAdvActAdvTerm` | 24 |
| `0x003212F0` | `lctrMstLlcpExecuteSm` | 192 |
| `0x003217F0` | `lctrMstPerScanExecuteSm` | 48 |
| `0x00321820` | `lctrMstPerScanIsrInit` | 12 |
| `0x00323D1C` | `lctrPackConnIndPduAddr` | 28 |
| `0x00329034` | `lctrSlvBigExecuteSm` | 48 |
| `0x0032B210` | `lctrSlvLlcpExecuteSm` | 192 |
| `0x0032CA20` | `lctrStoreConnParamSpec` | 28 |

### Link-order identified, low compared-byte count

| Stock address | SDK symbol | Bytes | Compared bytes |
|---:|---|---:|---:|
| `0x00308198` | `LctrPrivSetResPrivAddrTimeout` | 12 | 4 |
| `0x0030BE3C` | `LlGetPeriodicChanMap` | 12 | 4 |
| `0x0030C40C` | `LlMathDivideUint32RoundUp` | 8 | 4 |
| `0x003100F8` | `PalFrcDeltaUs` | 4 | 4 |
| `0x003100FC` | `PalFrcHFTimerClear` | 8 | 4 |
| `0x00315C0C` | `lctrActNotifyHostColliding` | 12 | 4 |
| `0x00319204` | `lctrDecodeCtrlPduCaseDefault` | 4 | 4 |
| `0x00319950` | `lctrExtAdvActAdvCnf` | 8 | 4 |
| `0x00319970` | `lctrExtAdvActDisallowAdvCnf` | 8 | 4 |
| `0x00327A4C` | `lctrSlvAcadDisable` | 8 | 4 |
| `0x0032FC88` | `lhciIsoEncodeEvtPkt` | 4 | 4 |

### Link-order identified, relocation-only

| Stock address | SDK symbol | Bytes |
|---:|---|---:|
| `0x0030BB10` | `LlGenerateP256KeyPair` | 4 |
| `0x0030C724` | `LlReadIsoLinkQual` | 4 |
| `0x0030C728` | `LlReadIsoTxSync` | 4 |
| `0x0030E050` | `LlSetupIsoDataPath` | 4 |
| `0x00315DA0` | `lctrActPeerConnParamWithCollision` | 4 |
| `0x0031D438` | `lctrMstBisResetHandler` | 4 |
| `0x00320084` | `lctrMstExtInitResetHandler` | 4 |
| `0x0032182C` | `lctrMstPerScanResetHandler` | 4 |
| `0x00324FB0` | `lctrProcessTxAckCleanup` | 4 |
| `0x0032B2D0` | `lctrSlvPeriodicAdvAbortOp` | 4 |

## Modified upstream functions

Relocation masking compares 1,008 meaningful bytes across the nine same-size
placements: 942 match and 66 differ. The exact replay is pinned so any future
archive, compiler, address, or comparison drift fails closed.

| Stock address | SDK symbol | Size | Compared match | Interpretation |
|---:|---|---:|---:|---|
| `0x00306F44` | `LctrGetPeerMinUsedChan` | 44 | 39/40 (97.500%) | connection-context layout/configuration delta |
| `0x00318168` | `lctrCenSendPendingRspRptHandler` | 76 | 12/60 (20.000%) | locally optimized PAwR direct-table implementation |
| `0x00318F2C` | `lctrConnTxCompletedHandler` | 148 | 118/120 (98.333%) | connection-context layout/configuration delta |
| `0x00320274` | `lctrMstExtInitiateEndOp` | 108 | 87/88 (98.864%) | connection-context layout/configuration delta |
| `0x00324FB4` | `lctrReceivePeriodicSyncInd` | 320 | 271/272 (99.632%) | connection-context layout/configuration delta |
| `0x00325324` | `lctrRxConnEnq` | 44 | 35/36 (97.222%) | connection-context layout/configuration delta |
| `0x00325A68` | `lctrSendChanMapUpdateInd` | 172 | 127/136 (93.382%) | layout/field-offset delta |
| `0x0032698C` | `lctrSendRejectInd` | 96 | 78/80 (97.500%) | layout/field-offset delta |
| `0x003272D8` | `lctrSetCisTest` | 196 | 175/176 (99.432%) | connection-context layout/configuration delta |

GNU ARCv2 EM disassembly shows the dominant difference in the eight close
matches: the SDK indexes `lctrConnCtx_t` at a 900-byte stride, while stock
indexes it at 912 bytes. Related fields also move: the channel-map update
path shifts its observed field base by four bytes, and the reject-indication
field moves from SDK offset 830 to stock offset 834. These are strong evidence
for the same upstream C functions compiled against a different structure and
feature configuration, not independent stock algorithms.

The PAwR outlier preserves the same symbol role and 76-byte size but has a
substantive implementation change. The SDK calls `lctrFindPawrAdvSet` for each
index. Stock loads the configuration table once, walks 12-byte entries, checks
the entry pointer/state, calls the pending-response callback, and clears the
entry byte at offset 64. Every inspected Packetcraft SDK profile contains the
same archive body, so no alternate exact profile explains the stock version.
Its behavior is substantially recovered, but it remains stock-retained and is
not yet marked source-recreated.

## Reproduction and evidence identity

`tools/analyze_em9305_sdk_link_order.py` authenticates all prior archive-scan
inputs, enforces both the strict 36-range/46-function and NOP-aware
120-range/156-function censuses, rejects overlap, and emits the complete
dynamic anchor and placement map. Its current JSON report hashes to
`3551b7cfec594daaa627e2e2587dd276c956a241f1758b53b5c848d2d31fb4da`.

`tools/compare_em9305_modified_sdk_functions.py` authenticates the official
firmware (`91a38d…eca9`), controller ISO archive blob
`b9433012b264da2210f602395b144a6d21795f01` / SHA-256
`87af23b9…6cfa`, compiler-comment anchors, selected symbols, addresses, and
per-function mismatch counts. Lorelei reproduced the JSON byte-for-byte at
SHA-256 `6d095260360b8da8d4ed9782f1c6368be58bc435d2c3521ead01df133027175b`.
`tools/compare_em9305_nop_aware_modified_sdk_functions.py` independently pins
the 29 additional same-size modified functions: 3,815 of 3,868 meaningful
bytes match (98.630%), with 53 enforced mismatches. Its report hashes to
`320d5a03455fc7fac0e60c237834d3e475dd7491e959724633fc9fc7cf30063f`.
`tools/compare_em9305_size_delta_sdk_functions.py` independently decodes the
13 accepted size-delta pairs with GNU ARC binutils. Across 1,256 archive and
1,298 stock instructions, sequence alignment matches 1,225 instructions;
individual ratios range from 86.364% to 99.387%. Its pinned report hashes to
`252f5993438fec92c82f99945e9b5a5f5c0b54e9c6a6ea196c76623343a0c2d7`.
The extracted SDK-object disassembly and whole-stock GNU ARC disassembly hash
to `950e4998…b35` and `13d1e9c7…916f`, respectively. Temporary report paths
are working evidence only; the checked-in analyzers and pinned identities are
the durable reproduction mechanism.

The current interpretation is intentionally bounded: link-order constraints
identify symbols and ownership, normalized comparison identifies exact or
modified bodies, and GNU ARC disassembly supports semantics. None of those
steps grants source redistribution rights or converts retained stock bytes to
source-compiled coverage.
