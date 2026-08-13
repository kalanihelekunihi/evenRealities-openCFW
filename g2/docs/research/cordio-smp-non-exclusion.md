# Cordio non-SMP alternative exclusion audit

Status date: 2026-08-09  
Target: G2 `s200_v2.2.6.10` Apollo main

## Outcome

The three-function `smp_non.c` translation unit is configuration-excluded from
stock G2. It is Cordio's alternative fixed-channel implementation for products
that do not support SMP; it cannot coexist as the active CID `0x0006` owner
with the complete `smp_main.c` implementation already recovered from stock.

The authenticated image contains exactly two direct calls to `L2cRegister`:

| Site | CID | Data callback | Control callback | Owner |
|---:|---:|---:|---:|---|
| `0x004B5138` | `0x0004` | `0x004B4DE1` | `0x004B4E09` | ATT |
| `0x00537CEA` | `0x0006` | `0x00537279` | `0x00537445` | full SMP |

The CID-6 call is inside linked `SmpHandlerInit`; its two callback pointer
values each occur exactly once in the image. The full SMP callback, handler,
allocation wrapper, role state machines, legacy actions, Secure Connections
actions, and database support are independently closed. There is no third
registration, alternate callback pointer, retained `smp_non.c` marker, or
`SmpNonInit` call.

The source-only data callback would necessarily add calls to
`DmConnIdByHandle`, `DmConnRole`, `smpMsgAlloc`, and `L2cDataReq`. Exhaustive
raw Thumb scans close all 7, 68, 13, and 8 respective stock call sites; none
forms the non-SMP pairing-failed response path. The two-byte no-op control
callback is not claimed absent from bytes by opcode identity alone—many empty
functions can fold to the same instruction—but it has no registration or
stored-pointer ingress. Thus all three definitions are fail-closed as
source-only/configuration-excluded, and no stock interval is assigned.

## Optional source lineage

Packetcraft r20.05 through r20.05c and the later official AmbiqSuite R4.4.1
import provide byte-identical optional source:

```text
blob    b024dc746c712284f2cb0b54669358b3f3cbd0fd
bytes   3,325
sha256  792892f2ca830fce8f1f0b280d098a9b188621fd5feb94a877a48b54779407b2
```

Packetcraft r19.02 and AmbiqSuite R2.5.1 are also definition-identical; their
3,298-byte file differs only in Apache-header formatting. No stock body exists
to discriminate releases. The surrounding linked SMP implementation already
selects the r20/R4 ABI, so r20.05c is the compatible public pin. The later R4
import is corroboration rather than G2's resolved historical producing commit.

Public source routes:

- [Packetcraft r20.05c `smp_non.c`](https://github.com/packetcraft-inc/cordio/blob/3656312d6b73e2a2c1c8b33ee0385bc199dd97e6/ble-host/sources/stack/smp/smp_non.c)
- [Official later AmbiqSuite R4.4.1 import](https://github.com/AmbiqAI/neuralSPOT/blob/4264b9309e03064ffad13a0468d5d0c1110c5288/extern/AmbiqSuite/R4.4.1/third_party/cordio/ble-host/sources/stack/smp/smp_non.c)

## Reproduction

```sh
python3 tools/analyze_g2_cordio_smp_non.py --json
python3 -m unittest tests.test_analyze_g2_cordio_smp_non
```

Production ownership and source replacement remain zero.
