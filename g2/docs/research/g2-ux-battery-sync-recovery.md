# G2 UX battery-sync recovery

The retained `app\ux\ux_battery_sync\ux_battery_sync.c` path resolves to one
complete callback body at `[0x005F958C,0x005F98D0)` and its 84-byte literal
pool, producing a 920-byte physical object at `[0x005F958C,0x005F9924)`.
The following halfword is the prologue of a different callback. Nine raw path
references, all 341 instructions, 57 direct calls, both adjacent boundaries,
and the sole stored Thumb entry at `0x006A46F4` are independently pinned.
The preceding table word binds that entry to service-record ID `0x105`.

`UX_BatterySyncHandler` rejects null or sub-12-byte input and accepts message
IDs 1 through 6. IDs 1/4 ask the charger service to send with roles 2/3;
IDs 2/3 import charger peer state. ID 5 clamps a signed ring level to 0..100,
normalizes charging, updates the ring-battery cache, and publishes callback
keys 0/1 only for changed values. ID 6 sends the cached ring state.

All 57 calls terminate at 45 already admitted EasyLogger operations, four
calls into the closed charger-common object, six into the closed ring-battery
object, and two calls into a 14-byte first-party callback-manager wrapper.
There are no direct CMSIS-FreeRTOS calls and no embedded third-party
definition. Exact public searches for `UX_BatterySyncHandler`,
`ux_battery_sync.c`, and `ux.battery_sync` returned no source candidate.
Consequently this object adds no dependency-version discriminator and cannot
reveal the private generating commit.

## Production routing

`components/apollo_main/core_overlay/ux_battery_sync.c` now supplies the
GPL-3.0-only clean-room service-record callback. One guarded redirect replaces
the complete 836-byte stock body with 158 compiled Thumb bytes plus two bytes
of alignment. Eleven strict relocations terminate at the bounded charger,
ring-battery, and source-owned callback providers; the authenticated 84-byte
diagnostic/path/literal pool remains stock data.

Host tests cover null/short rejection, unknown IDs, all six dispatch cases,
charger request/response roles, signed level clamping, charging normalization,
change-only callbacks, and cached ring-state export. The canonical Apple
overlay/component/package sizes are 193,738 / 3,717,134 / 4,495,628 bytes,
with SHA-256 values `a4c7927efe625a95e3bd928e5bb75b32c057837577dd9b9bf0cc3a5c19a42183`,
`026ba2cc0c5f4dd5ca052b630edd3bbbae8addd95b53f7bd0b16c0ebb40c316a`,
and `03d4b3f7813ce41814ae821ccbdaa3a1f2802fe4a459cf20351487a18332e783`.
The 1,975,706-byte deployment plan hashes to
`ef7a204c200024422defd2cb9e0064a5aa4278bb14533e4007bd0daf2db1e67f`.

The software gap is closed. Physical peer traffic, charger state, ring state,
and timing behavior remain explicitly blocked because no authorized G2 pair or
captured physical evidence is available.
