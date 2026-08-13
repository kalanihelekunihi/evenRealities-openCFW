# Cordio SMP Secure Connections state-machine recovery

Status date: 2026-08-09  
Target: G2 `s200_v2.2.6.10` Apollo main

## Outcome

The apparent helpers at `0x00537F24` and `0x00538114` belong to
`smpi_sc_sm.c` and `smpr_sc_sm.c`; there are no corresponding
`smpi_main.c` or `smpr_main.c` source files in Packetcraft r20. The complete
initiator code/pool object is `[0x00537F14,0x005380DC)`, 456 bytes, SHA-256
`f3064c0be233c40088ecb5885ec0d7c89aa19c65f99ab1bcb18f927a692d8b98`.
The responder object is `[0x00538104,0x005382E4)`, 480 bytes, SHA-256
`9d2c76c594328e391b1befb588ccd45131a078f13ee8edcb55c217581c7eb663`.

All four source functions link: the two role initializers and two diagnostic
state-name switches contribute 598 code bytes. There are four exact direct
callers, no stored function pointer, and no entry or strict-interior value at
any byte alignment. The pools retain the interface and `smpCb` literals plus
the complete state-name pointer sets.

## Dispatch-data closure

The initializer literals recover both `smpSmIf_t` roots and make the otherwise
scattered const data fully traversable:

| Role | Interface | Actions | State pointers | State-entry bytes | Total identified ownership |
|---|---:|---:|---:|---:|---:|
| Initiator | `0x0078C320` (12 B) | 51 / 204 B | 38 / 152 B | 39 tables / 345 B | 1,169 B |
| Responder | `0x0078C470` (12 B) | 55 / 220 B | 40 / 160 B | 41 tables / 390 B | 1,262 B |

Each state entry is the exact three-byte `{event,nextState,action}` ABI and
each state table ends in `{0,0,0}`. The analyzer follows every state pointer,
pins the ordered entry concatenation, and verifies the interfaces and action
tables independently. Combined identified ownership is 2,431 bytes: 936
physical code/pool bytes plus 1,495 bytes of scattered dispatch data.

## Source and release result

Packetcraft r20.05 through r20.05c uses invariant blobs
`68d20bee606c584a0ecd66a5dd1dbd41faf73a85` (`smpi_sc_sm.c`) and
`09a208b4735cab37af65689bdf68288913f5e495` (`smpr_sc_sm.c`). The selected
pin is r20.05c commit
`3656312d6b73e2a2c1c8b33ee0385bc199dd97e6`; both files are Apache-2.0.

The initiator differs from r19/AmbiqSuite 2.x only in license formatting and
does not discriminate releases. The responder does: r20 adds action
`SMPR_SC_ACT_SEC_REQ_TO` and adds response-timeout plus cleanup transitions to
the API-pair-request state. Stock has the 55-entry action table and exact
state bytes ending in `(0x0F,0x01,0x03)` and `(0x1F,0x00,0x01)` before the
terminator. The r19/AmbiqSuite 2.x file has only 54 actions and lacks both
rows. This independently selects r20 behavior.

## Recovered runtime behavior

`SmpiScInit` writes the initiator interface to `smpCb.pMaster`; `SmprScInit`
writes the responder interface to `smpCb.pSlave`. Both then call `SmpScInit`,
which binds the three secure-connections control blocks and installs the
shared pairing/authentication callbacks. `smpiStateStr` covers states
`0x00`--`0x25`; `smprStateStr` covers `0x00`--`0x27`; unknown values return
the common unknown-state string.

```sh
python3 tools/analyze_g2_cordio_smp_sc_sm.py --json
```

Production ownership remains zero. The authenticated stock bytes remain cut
forward pending source compilation, exact IAR placement, and relocation
closure.
