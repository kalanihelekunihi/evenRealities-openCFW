# G2 ring-battery service recovery

The retained `platform\service\ring_battery\service_ring_battery.c` anchor
expands from two path-anchored Ghidra bodies / 306 bytes to five functions /
352 body bytes plus a 44-byte pointer pool, for 396 physical bytes at
`[0x004FF8E4,0x004FFA70)`. Nine direct entries, 19 body calls, both adjacent
boundaries, three independent path-pointer references, and the absence of
stored, indirect, or strict-interior entries are pinned by the analyzer.

The object caches an 8-bit battery level (clamped at 100) and charging flag.
`SVC_RingBattery_Update` emits record type 5 with both values, while
`SVC_RingBattery_RequestFromPeer` emits type 6 through the service-record
transport under ID `0x105`. Those two names are retained diagnostic symbols;
the three pathless accessor names are deliberately semantic labels.

All 19 external calls terminate at 15 already admitted EasyLogger operations,
two bounded IAR `memset` calls, and two first-party service-record transport
calls. Exact public searches for both retained symbols and the source filename
found no public source. The object therefore has no unidentified third-party
definition, adds no dependency-version discriminator, and does not expose the
private generating commit.

## Production closure

All five linked functions now route to selector-isolated GPL-3.0-only
clean-room C in `components/apollo_main/core_overlay/service_ring_battery.c`.
Host contracts cover the cached state, 100-percent level clamp, Boolean charge
normalization, both getters, the 12-byte service-record ABI, local update type
5, peer request type 6, and service ID `0x105`. Five guarded redirects replace
all 352 stock body bytes with 134 compiled Thumb bytes plus four alignment
bytes. The only two strict relocations terminate at the recovered local and
peer service-record transports; the authenticated 44-byte diagnostic/path
pool remains retained data.

The canonical Apple overlay is 193,876 bytes with SHA-256
`a4c7927efe625a95e3bd928e5bb75b32c057837577dd9b9bf0cc3a5c19a42183`.
The 3,717,272-byte Apollo component hashes to
`026ba2cc0c5f4dd5ca052b630edd3bbbae8addd95b53f7bd0b16c0ebb40c316a`,
and the complete 4,495,766-byte package hashes to
`03d4b3f7813ce41814ae821ccbdaa3a1f2802fe4a459cf20351487a18332e783`.
The 1,985,178-byte flash plan hashes to
`ef7a204c200024422defd2cb9e0064a5aa4278bb14533e4007bd0daf2db1e67f`.

No hardware was accessed or flashed. Paired-G2 delivery, local/peer transport
ownership, callback timing, and live ring battery-state behavior remain
explicitly blocked by unavailable authorized physical evidence. There is no
remaining software functional gap in this five-function object; this does not
assert completeness of the wider ring stack or firmware.
