# G2 bootloader LittleFS sync callback source closure

> **Superseded temple-status premise:** Treat temple nonresponse/unavailability
> claims below only as history. The case was bumped during lunch and caused the
> disconnect, not firmware or flashing; exclude it from feasibility conclusions.
> Hardware testing remains blocked by unavailable physical evidence.

The authenticated callback `[0x004213D4,0x004213D8)` is production-routed to
a four-byte freestanding C leaf at `[0x00421280,0x00421284)`. This is offline
software closure only; live persistence qualification is blocked by unavailable
authorized responsive right-temple hardware.

## Evidence and behavior

- Stock body: `00 20 70 47`, SHA-256
  `a7ddd513d149ea16fdd4db3f82267f83087aeaddd06b5dde5468adb704205fc4`.
- LittleFS configuration sync pointer at `0x00431080`: `0x004213D5`.
- The callback ignores `cfg`, performs no I/O, and returns zero.

`runtime_littlefs_sync_4213d4.c` is 353 bytes with SHA-256
`61cb60efd6396a2f5240eaf33786d0158f065c28cf1a14c02a0df72522ca90ae`.
Apple clang 21 and Homebrew clang 22.1.8 both emit the exact four stock
instruction bytes with no relocations. The authenticated four-byte generated
NOP cave pin is
`652e05ecd0fa115830117c1469510bb8b72641319fde694e129a020a012a7ebf`;
the stock entry redirects backward with displacement `-344`.

No signing, flashing, reset, boot, filesystem mutation, or device communication
occurred. Live persistence, concurrency, power-loss, and cold-boot behavior
remain hardware-validation blocked.
