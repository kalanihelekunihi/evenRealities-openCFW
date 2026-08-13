# Cordio legacy SMP state-machine recovery

## Result

The legacy initiator and responder state-machine translation units are fully
identified. `smpi_sm.c` contributes `SmpiInit` at
`[0x00537EEC,0x00537F02)` plus 330 bytes of scattered interface, action, and
state-table data, for 370 identified owned bytes. `smpr_sm.c` contributes
`SmprInit` at `[0x005380DC,0x005380F2)` plus 375 bytes of corresponding data,
for 415 identified owned bytes. No source function is absent.

Packetcraft r20.05 through r20.05c and the official later AmbiqSuite R4.4.1
import share exact Apache-2.0 files: initiator blob
`b5bc5ba1a6a91d49d6523f6fbbfd3c07d2070670`, 11,739 bytes, SHA-256
`70cc74bfbbe000ceedff41645b5d01208f9b0a083c22adb913b215065f3c61fa`;
responder blob `a922f753e64b82bc92278671ded9f736b5a092e0`, 13,292 bytes,
SHA-256 `a60f0611344bf550b6bc6152139a660b3c0177835e537d20da6d131567e6a771`.
The selected public pin is r20.05c commit
`3656312d6b73e2a2c1c8b33ee0385bc199dd97e6`. R4.4.1 commit `4264b930`
is later corroboration, not the historical producing commit.

Initiator behavior is invariant back through r19/AmbiqSuite 2.x. Responder
behavior independently selects r20: its 27-entry action table contains
`smpActSecReqTimeout`, and its API-pair-request state includes both response
timeout `(event=0x0F,next=1,action=3)` and cleanup
`(event=0x1F,next=0,action=1)` before termination. The r19/AmbiqSuite 2.x
file has 26 actions and neither transition.

## Dispatch-data closure

Both initializer literal pools recover their `smpSmIf_t` roots, allowing the
otherwise scattered const objects to be traversed without address guessing:

| Role | Interface | Actions | State pointers | State-entry bytes | Identified ownership |
|---|---:|---:|---:|---:|---:|
| Initiator | `0x0078C344` | 25 / 100 B | 14 / 56 B | 15 tables / 162 B | 370 B |
| Responder | `0x0078C4AC` | 27 / 108 B | 15 / 60 B | 16 tables / 195 B | 415 B |

Each state entry is the packed three-byte `{event,nextState,action}` ABI and
each individual table ends in `{0,0,0}`. The interfaces identify the state
pointer arrays at `0x007235E8` and `0x00718E50`, action arrays at
`0x006DBAC4` and `0x006D7E7C`, and common tables at `0x007892D0` and
`0x00789480`. The ordered 785-byte ownership concatenation hashes to
`98a3708291e1ca0add3c7cc3e182b11e240680905fd74e336558d01f1e96fa79`.

The physical initializer objects are each 40 bytes including alignment and
their four-word literal pools. Initiator hashes to
`692ebaa593161de42e912411698481ce0ba40d0dd8e75b19cc5efeb6d15979b4`;
responder hashes to
`e8b27cfbbf917047a50437d2cf68b10640ae740cf9e92fe2bee79fff26316bd3`.
Both pools contain `smpCb=0x20070AEC`, the role interface, and the shared
legacy callbacks `smpProcPairing=0x0056E6E0` and
`smpAuthReq=0x0056E84C`.

## Runtime behavior and ingress

`SmpiInit` writes the initiator interface to `smpCb+0xE8`; `SmprInit` writes
the responder interface to `smpCb+0xE4`. Both install the shared legacy
pairing and authentication callbacks at `smpCb+0xF0` and `smpCb+0xF4`.
Their only direct callers are the stock stack initializer at `0x004B807C`
and `0x004B8084`. There is no stored pointer to either initializer and no
stored or branched strict-interior address.

The tables drive legacy pairing request/response, confirm/random verification,
STK encryption, key distribution, retry/attempt handling, response timeout,
connection close, and cancellation. Actions are implemented by the already
closed shared and role-specific action units.

## Reproducibility

`tools/analyze_g2_cordio_smp_legacy_sm.py` pins both initializer bodies and
pools, interfaces, action arrays, state-pointer arrays, every terminated state
table, the r20 responder discriminator, both callers, and the absence of
function-pointer or strict-interior ingress. Source identities and function
hashes are in `packetcraft-cordio-smp-legacy-sm-provenance.tsv` and
`packetcraft-cordio-smp-legacy-sm-function-map.tsv`; the scattered data ledger
is `packetcraft-cordio-smp-legacy-sm-table-map.tsv`.

Production ownership remains zero. All authenticated stock bytes continue to
be cut forward pending source compilation and exact placement.
