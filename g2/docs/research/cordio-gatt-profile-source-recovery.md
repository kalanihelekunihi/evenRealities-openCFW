# Cordio GATT-profile source recovery

Status: exact upstream source admitted; complete six-function stock object is
production-routed. Software behavior is closed; authorized physical G2/EM9305
interoperability evidence is unavailable.

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
functions are direct semantic source matches.

## Production closure

`components/apollo_main/core_overlay/cordio_gatt_profile.c` adapts all six
functions to the recovered G2 control-block, discovery-list, handle, and
provider ABI. Six selector-isolated Apple/Clang leaves contribute 254 compiled
Thumb bytes plus eight alignment bytes and carry ten strict relocations. Six
guarded entry redirects replace all 322 stock body bytes; the directly used
34-byte literal pool remains authenticated official data.

Host tests cover discovery arguments, service-changed routing and CCC gating,
all/specific-connection indication behavior, CSF read/write callbacks, and
single-function selector isolation. The fail-closed analyzer pins the source,
leaves, relocations, complete redirects, retained pool, component build,
manifest regions, and final package identity. Stock EasyLogger output is
omitted as non-controlling diagnostics while the terminal discovery operation
and all ATT/GATT state changes remain implemented.

Canonical Apple overlay/component/package identities are
`193488/3716884/4495378` bytes with SHA-256 values
`a4c7927efe625a95e3bd928e5bb75b32c057837577dd9b9bf0cc3a5c19a42183`,
`026ba2cc0c5f4dd5ca052b630edd3bbbae8addd95b53f7bd0b16c0ebb40c316a`,
and `03d4b3f7813ce41814ae821ccbdaa3a1f2802fe4a459cf20351487a18332e783`.
The 1,963,573-byte flash plan hashes to
`ef7a204c200024422defd2cb9e0064a5aa4278bb14533e4007bd0daf2db1e67f`.
No hardware was accessed or flashed. ATT discovery, CCCD state, indications,
controller timing, and peer interoperability remain explicitly blocked by the
absence of authorized G2/EM9305 hardware or captured physical evidence.
