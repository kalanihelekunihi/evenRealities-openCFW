# G2 bootloader tagged-handle acquire/release source closure

The complete acquire body `[0x004166AA,0x00416710)` is 102 bytes with SHA-256
`7e01992bf56a87f76d3d358be2ee1a493519767165cb5cfc739e9957a869e3f5`.
The release body `[0x00416710,0x00416762)` is 82 bytes with SHA-256
`73668052c9d6843302d6c1db4095d2c87ce56ab770499a25c4d55fb0912292d3`.
Nine direct callers of each entry are pinned.

The clean-room C strips the low-bit backend tag, rejects critical context and
null raw handles, selects the exact tagged/plain retained backend, preserves
timeout-to-error mapping for acquire, and supplies three zero arguments to the
plain release backend. Both profiles emit identical 68-byte acquire and
58-byte release leaves before relocation, with three strict relocations each.
Seven host tests and all offline build/package gates pass. Scheduler and object
lifetime validation is blocked by unavailable authorized responsive hardware.
