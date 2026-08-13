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
reveal the private generating commit. It is not yet production-routed.
