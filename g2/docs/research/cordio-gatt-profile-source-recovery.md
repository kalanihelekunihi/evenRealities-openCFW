# Cordio GATT-profile source recovery

Status: exact upstream source admitted; complete six-function stock object
closed; production routing remains off.

The retained path `platform\ble\profiles\gatt\profile_gatt.c` misleadingly
looks first-party. Its complete `[0x004B59C0,0x004B5B24)` object is Packetcraft
Cordio's standard `ble-profiles/sources/profiles/gatt/gatt_main.c`: all six
upstream functions occur in source order, including three bodies Ghidra missed.

| Function | Stock interval | Bytes | Qualification |
|---|---|---:|---|
| `GattDiscover` | `0x004B59C0..0x004B5A1E` | 94 | upstream terminal call plus inserted G2 logging |
| `GattValueUpdate` | `0x004B5A1E..0x004B5A3A` | 28 | upstream behavior |
| `GattSetSvcChangedIdx` | `0x004B5A3A..0x004B5A44` | 10 | upstream behavior |
| `GattSendServiceChangedInd` | `0x004B5A44..0x004B5ABA` | 118 | upstream behavior |
| `GattReadCback` | `0x004B5ADC..0x004B5B02` | 38 | upstream behavior |
| `GattWriteCback` | `0x004B5B02..0x004B5B24` | 34 | upstream behavior |

The 322 body bytes and 356 physical bytes are fully bounded. Eight exact-start
BL sites and two stored read/write callback pointers account for ingress; no
strict-interior or wide-branch ingress exists. Calls resolve to the expected
Cordio providers: `AppDiscFindService`, `AppDiscServiceChanged`,
`AttsCccEnabled`, `AttsHandleValueInd`, `AttsCsfGetFeatures`, and
`AttsCsfWriteFeatures`, plus `memcpy`.

The exact `gatt_main.c` blob `bba9a3041ce14284a0bf527934eabd01c01694d8`
and header blob `6b71dd3178cbf89bbe3751d0ba33fb4a1603d97b` are identical at all four
official Packetcraft releases r20.05 through r20.05c. The existing Cordio
selection therefore applies: r20.05c commit
`3656312d6b73e2a2c1c8b33ee0385bc199dd97e6`. That is the proper selected
source commit, not proof of the private historical G2 checkout, which remains
unobservable.

`third_party/packetcraft-gatt-profile` now vendors the exact Apache-2.0 source,
header, license, and offline verifier. Stock `GattDiscover` inserts EasyLogger
diagnostics but preserves the upstream `AppDiscFindService(connId, 2,
attGattSvcUuid, 3, gattDiscCharList, pHdlList)` operation. The other five
functions are direct semantic source matches. This removes the final opacity
from this copied profile object without claiming production ownership.
