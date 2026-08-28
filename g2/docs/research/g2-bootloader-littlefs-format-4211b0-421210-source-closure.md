# G2 bootloader LittleFS format/bootstrap source closure

## Scope and authenticated boundary

This increment replaces the complete Apollo510B bootloader body
`[0x004211B0,0x00421210)` with clean-room compilable C. The 96-byte stock
body has SHA-256
`9c3d0c94a411e7e0a666d918d23a0c8f4eefecd2d5a32761767786bf1f47bc08`.
The 200-byte successor initializer `[0x00421210,0x004212D8)` remains retained
with SHA-256
`07d8267cfa9725c9ac0ee613334d09968b780b890c4680f612546239bff1adf8`.
Its direct call to this service is at `0x0042126E`.

## Recovered behavior

The service uses the fixed LittleFS object at `0x20026878` and configuration
at `0x00431070`. It calls the retained public wrappers at `0x0041513C`
(unmount), `0x00415128` (format), and `0x00415132` (mount), in that order.
Unmount and format statuses are deliberately ignored. A nonzero mount status
is diagnosed and mapped to `9`. Successful mount calls the source-owned
directory bootstrap; a nonzero result is diagnosed and also mapped to `9`.
Only successful mount and directory bootstrap return `0`.

The fixed filesystem/configuration objects, retained public LittleFS wrappers,
and authenticated logging literals are compatibility seams. The directory
bootstrap and EasyLogger output edges resolve to source-owned leaves. No stock
implementation bytes are carried in the clean-room source.

## Production routing and reproducibility

The stock body is replaced by one wide Thumb branch plus NOP fill. Apple clang
emits a 108-byte leaf at overlay offset 14,812 / address `0x00437E54`; its
unrelocated SHA-256 is
`173e8b905d12452d033fef79fe4729df236a647d92f4ed23f07f901e0bda55bc`
and relocated SHA-256 is
`dde3d1adb0ab07eb997820b6b6f6c505b965be976585252b893daff999585fdc`.
Homebrew clang emits a 112-byte leaf at offset 14,792 / address `0x00437E40`;
its unrelocated SHA-256 is
`fdaa46af99eafc00fe47ec1fc36dc5369073273746a98a9765df3ad6359e65b8`
and relocated SHA-256 is
`12fd66d55998567771ffdd1fa725ceaddcda6e2046aa0f5f14e28c6f50387260`.
Both profiles pin exactly two source-to-source call relocations.

Apple/Linux overlays are 14,920 / 14,904 bytes with SHA-256
`360c37433d555f50a9bf117e9d7c029708e2a3ef1c996892fb846b657aaaa257`
and `9576b3c3024ceda0269d2a947cc9fc7f460e0730af80f4a50d122fccfbd0602f`.
Providers are 163,520 / 163,504 bytes with SHA-256
`52d2d2e27cbfff363d18010650dd7751bbdbfbc0acffef731e416df47835c270`
and `59f841fe1197395dcebbc0c550d4080106da2984fdd477d2fd28dc09431210b8`.
Canonical provider accounting is 14,905 source-owned, 16,140 generated
redirect, 16 generated alignment, and 132,459 retained official bytes across
196 functions, 177 relocated leaves, and 194 patch sites.

Unsigned Apple/Linux packages are 4,745,098 / 4,521,092 bytes with SHA-256
`d91b1a7aa58deb5e10499569fe12754b37bc589e9ab4df768c956cd1fc766d19`
and `c0e06590e74ec97dc5b7474df610d0e557013e5a0d95ef5c1f0cc972eadb2a42`.
The Apple flash plan is 4,559,746 bytes with SHA-256
`e6c01bac8cc86b4cb3f71c5a09eb3ff64b0e7563c8e7bef39903112e5f8723ad`;
it records 6,553 placed, two unresolved, five container-only, and six
protected regions.

Five focused tests authenticate the body, successor, calls, literals, and
caller; exercise successful sequencing, ignored unmount/format results,
mount failure, directory failure, status mapping, diagnostics, and early
stop; and compile the source for Cortex-M55.

## Physical-evidence block

No signing, flashing, format, erase, reset, boot, filesystem mutation, MSPI
command, or other hardware operation occurred. There is no authorized
responsive right G2 temple, and the left temple must remain stock. Live
unmount/format/mount behavior, block erase/program activity, persistence,
power-loss recovery, diagnostics, and cold-boot qualification are explicitly
blocked by unavailable physical evidence. This closes one software gap only.
The next authenticated executable frontier is `0x00421210`.
