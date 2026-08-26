# Cordio `attc_main.c` source recovery

## Result

The stock interval `[0x00530D74,0x00531BD4)` is the complete linked Cordio
ATT client core. It contains 20 functions / 3,540 code bytes and 140 bytes of
owned alignment, trace categories, and literals. The 21st public definition,
`AttcSetAutoConfirm`, has no body, caller, or stored pointer and is
dead-stripped. `AttcInit` still initializes automatic confirmation to true.

The selected Apache-2.0 public core is Packetcraft r20.05c commit
`3656312d6b73e2a2c1c8b33ee0385bc199dd97e6`, Git blob
`10cb08f29cd37d0e6f86cdf1b35ad185ae052d11`, 26,980 bytes, SHA-256
`e5235e4929ee10a88c80fcf7a3fb4465a329efaa5d428a24796a1f3b26d729e8`.
The same blob spans r20.05 through r20.05c. The stock three-bearer control
block and 17-entry request table exclude the pre-EATT r19/AmbiqSuite 2.x
architecture.

Official AmbiqSuite R4.4.1 source later imported by AmbiqAI/neuralSPOT is a
more precise behavioral corroboration, SHA-256
`fba056a78c5bfa9157e05ccc1ede07e4c7ee297c4a975eec34a3e820c795b2a0`.
It adds the data-length check that stock implements: a zero-byte ATT packet is
rejected before parsing. Stock also expands connection validation and local
diagnostics, so neither public file is claimed as the exact historical vendor
text. R4 is a later oracle, not the generating commit.

## Boundary and ingress

The physical object hashes to
`3571bc76a244b81e8a605b4da8386fc1f3007b49eb3fae763ab077101422970d`;
the 20 concatenated bodies hash to
`4ad46a1239865f2b236a5a94d3b501a32efc7d208f4bb8826e85a9551a60212a`.
The retained path occupies `[0x006DC814,0x006DC874)` and is referenced from
the object tail. The next retained path is `attc_proc.c`, confirming the
translation-unit boundary.

Raw Thumb decoding closes 32 direct calls. The 17-entry `attcSendReqTbl` at
`0x00700920` stores 13 function entries, and `attcFcnIf` at `0x00785250`
stores the four data/control/message/connection callbacks. An exhaustive
unaligned scan finds exactly those 17 stored entries and no strict-interior
pointer.

## ABI and behavior

`attcCb` is at `0x2006F904`. Its first `0x18C` bytes hold nine 44-byte
`attcCcb_t` records: three connections times three bearers. Three 12-byte
on-deck API messages follow at `+0x18C`; `pSign` is at `+0x1B0` and
`autoCnf` at `+0x1B4`. This proves `DM_CONN_MAX=3`,
`EATT_CONN_CHAN_MAX=2`, and three total ATT bearers per connection.

The client core serializes requests per bearer, manages continuation and
response timers, handles signed and prepared writes, sends the one-shot MTU
request, and routes ATT responses, notifications, indications, control
confirmations, connection changes, cancellation, and timeout completion.
The zero-length receive guard agrees with the later official Ambiq source.
The product logger adds fail-closed validation around connection/bearer lookup.

## Reproducibility

`tools/analyze_g2_cordio_attc_main.py` pins the official image, every linked
body, all seven owned gaps, the physical object, retained path and control
block literals, both dispatch tables, all 32 direct calls, all 17 stored
entries, and zero strict-interior pointers. The complete source/body ledger is
`tools/manifests/packetcraft-cordio-attc-main-function-map.tsv`; release
identity is recorded in
`tools/manifests/packetcraft-cordio-attc-main-provenance.tsv`.

## Production replacement

`components/shared/cordio/runtime_cordio_attc_main.c` implements all 21 source
definitions. Twenty linked entries use guarded redirects to replace all 3,540
stock body bytes with 2,258 compiled Cortex-M55 bytes plus 12 alignment bytes
under 61 strict relocations. The dead-stripped `AttcSetAutoConfirm` definition
is retained and target-compiled without inventing stock coverage. `AttcInit`
binds the retained stock interface table at `0x00785250`.

The implementation preserves the authenticated G2 `0xA0` HCI-error base and
hardens connection/bearer bounds, one-based on-deck indexing, zero-length
packets, null/malformed messages, and send-table selection. Host tests cover
initialization, pending writes, simple/continuing/prepare/MTU requests, PDU and
control dispatch, sign hooks, connection lifecycle, cancellation, and timeout.

The canonical overlay is 353,336 bytes, SHA-256
`31eec27c1b67e8740a77144c24896a367239d0816fa48acee6b4926b14898106`;
the Apollo component is 3,876,732 bytes, SHA-256
`3aba35b870b09b678b1af07680b2db1ab61962baf0247a6e1b806954a6726444`;
and the deterministic package is 4,655,226 bytes, SHA-256
`b10166d4f1c1f91f348c3ee360afb2af1499df59715491a1256a1d0545f548bc`.
The 3,457,178-byte flash plan has 4,977 placed, two unresolved, five
container-only, and six protected regions. No image was signed, flashed, or
installed. Live ATT peer, controller, bearer scheduling, and timer validation
is blocked by unavailable authorized responsive G2/EM9305 physical evidence.
