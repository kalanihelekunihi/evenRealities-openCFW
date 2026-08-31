# G2 bootloader LittleFS initializer source closure

> **Superseded temple-status premise:** Treat temple nonresponse/unavailability
> claims below only as history. The case was bumped during lunch and caused the
> disconnect, not firmware or flashing; exclude it from feasibility conclusions.
> Hardware testing remains blocked by unavailable physical evidence.

## Disposition

The complete authenticated bootloader body `[0x00421210,0x004212D8)` is now
implemented as freestanding clean-room C in
`components/bootloader/core_overlay/runtime_littlefs_init_421210.c` and is
production-routed in both reviewed build profiles. This closes the software
gap for LittleFS mount recovery, readiness publication, and boot-counter
persistence. It does not establish on-device behavior or firmware-wide
functional completeness.

## Authenticated boundary

- Stock body: 200 bytes, SHA-256
  `07d8267cfa9725c9ac0ee613334d09968b780b890c4680f612546239bff1adf8`.
- Successor `[0x004212D8,0x00421310)`: 56 bytes, SHA-256
  `26e2b4b9fe7f3389d15261fe01621eb3b37bfc4b9923ebfac70609216ac92a90`.
- Sole authenticated caller: `0x0041B8A6`.
- Fixed LittleFS/configuration objects: `0x20026878` and `0x00431070`.
- Ready word and file object: `0x2002711C` and `0x20026C0C`.
- File path: `0x00433FC8` (`boot_count`); open flags: `0x103`.

The body calls retained littlefs wrappers for mount `0x00415132`, format
`0x00415128`, file open `0x00415146`, read `0x004151C0`, rewind `0x00415274`,
write `0x004151FC`, and close `0x00415180`. Calls to directory bootstrap
`0x004210C8`, recovery format `0x004211B0`, and EasyLogger output are routed to
source-owned leaves.

## Recovered behavior

The initializer first mounts the fixed filesystem. A first failure triggers a
format whose result is ignored, followed by one mount retry. A second mount
failure is diagnosed and mapped to status `9`. After a successful mount it
checks/creates the required directories. Directory failure is diagnosed and
invokes the source-owned format/bootstrap recovery service; that recovery
result is intentionally ignored and initialization continues.

The service then writes `1` to the readiness word. It initializes a local
four-byte boot count to zero, opens `boot_count` with flags `0x103`, reads four
bytes, increments the value, rewinds, writes four bytes, closes, and logs the
incremented value. All five file-operation results are deliberately ignored,
matching the authenticated body.

## Production evidence

Apple emits a 260-byte leaf at `0x00437EC0` (overlay offset 14,920), with
unrelocated SHA-256
`48cab28362a35f6ad1af9211d161c2eb69edfcf94d82a36d652879985091f356`
and relocated SHA-256
`443bb2e3be700dfaf4219c36c47a1f82ea7590fdd3a07b42a1a0a255c9e7d976`.
Linux emits a 260-byte leaf at `0x00437EB0` (offset 14,904), with unrelocated
SHA-256
`5c4899c2320c46bed7ef1fc006deedc9123b5bdfa6624b46baba246290fcb4db`
and relocated SHA-256
`c8ea2fb877b13d7e0871305f7462f328fb5929424fc7fceb8aae35f570d092ba`.
Five strict relocations bind the logger, directory-bootstrap, and
recovery-format calls.

The canonical overlay is 15,180 bytes with SHA-256
`18ce465a9a646bddad5cd7c663c0f4dfeb7b76fd93d1ad1cc48510f3d8dcd8e4`.
The 163,780-byte provider has SHA-256
`566895485d661ce696f4bcadd396f0f1f512fae92630f4f3c5315d67849bd5bd`
and CRC-32C/MSB `0xB0EBCCAD`. It closes at `0x00437FC4`, leaving 60 bytes
before the protected boundary. Exact accounting is 15,165 source-owned,
16,340 generated patch, 16 alignment, and 132,259 retained official bytes
across 197 functions, 178 relocated leaves, and 195 patch sites.

The Apple unsigned package is 4,745,358 bytes with SHA-256
`61a74ed44990d4fd5b2663b7fe0d68ffbef7a9f6afc3fb364854631ad6a0e15d`.
Its 4,561,240-byte flash plan has SHA-256
`c17a375878bb05229f8cfad7b7c3c105633289f9c4309b08b3c95f00c56e9f79`,
6,555 placed, two unresolved, five container-only, and six protected regions.
The Linux unsigned package is 4,521,352 bytes with SHA-256
`da9d13f90cbdd353104c81dfcba426eda994dff41aefb862bb9e5580322fd85f`.

Six focused tests cover the authenticated body and successor, caller and
literal topology, all control-flow paths, ignored-status policy, state
publication, counter behavior, and Cortex-M55 compilation. The aggregate
closure gate passes 343 tests plus snapshot, exact-routing, provider,
analyzer, package, and flash-plan checks.

## Physical-evidence block and next frontier

No signing, flashing, reset, boot, filesystem mutation, or hardware operation
was performed. There is no authorized responsive right G2 temple; the left
temple must remain stock. Live mount/format, directory mutation,
external-flash persistence, power-loss behavior, readiness observation,
boot-counter persistence, logging, and cold-boot evidence is therefore
explicitly blocked by unavailable physical evidence.

The next authenticated executable entry begins at `0x004212D8`. It remains a
software gap. Firmware-wide functional completeness is not claimed.
