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
private generating commit. It is not yet production-routed.
