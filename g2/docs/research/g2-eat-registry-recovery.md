# G2 complete eAT command-registry recovery

Status: complete stock registration-table census; all registered handlers have
independent fail-closed closures, while historical source remains incomplete.

## Result

The authenticated image contains exactly 21 structurally valid `AT...`
command records. They form one contiguous 336-byte table at
`[0x006C9260,0x006C93B0)` with SHA-256
`f47c2827a472adac781e19ae785e32c1eec101f5b7947d4be67a6dc07d7884ae`.
An exhaustive four-byte-aligned scan finds no other record matching the table
ABI: small command type, in-image NUL-terminated `AT...` name, odd in-image
Thumb handler, and zero auxiliary word.

All 21 records are assigned to closed analyses: two bond/connect commands,
one buzzer command, one audio command, one NUS command, three filesystem
commands, twelve core/sensor commands, and one touch-panel command. There are
no unassigned registered handlers. The map in
`tools/manifests/g2-eat-registry-map.tsv` pins every record address, type,
command string, handler pointer, and owning closure.

This proves completeness of the registered eAT runtime surface, not recovery
of every historical source file. Four retained eAT paths are known; pathless
objects still lack authenticated source inventories and licenses. None of the
21 handlers has a clean-room production candidate, so all remain stock-carried
and OpenCFW claims zero ownership bytes for the registry surface.

## Addendum: core/sensor production routing

After this census closed, the twelve core/sensor handlers gained a clean-room
production candidate: `at_core_sensor.c` is routed into the Apollo main
overlay under the reviewed apple-clang profile, and the twelve stored
registration pointers now reach the source leaves through entry redirects.
The registry census itself — twenty-one records, zero unassigned — is
unchanged. See `docs/research/g2-eat-core-sensor-recovery.md`.
