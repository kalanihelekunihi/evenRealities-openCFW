# DFU file services and synthetic NOR closure

## Provenance and boot mount path

Evidence is pinned to `g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin` (148,599 bytes; SHA-256 `f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5`; loaded at `0x00410000`). The Ghidra function catalogue authenticates each byte range against that image:

| Stock behavior | Address range | Bytes | Catalogue body SHA-256 |
|---|---:|---:|---|
| Boot filesystem init | `[0x00421210, 0x004212d8)` | 200 | `07d8267cfa9725c9ac0ee613334d09968b780b890c4680f612546239bff1adf8` |
| Read callback | `[0x004212d8, 0x00421310)` | 56 | `26e2b4b9fe7f3389d15261fe01621eb3b37bfc4b9923ebfac70609216ac92a90` |
| Program callback | `[0x00421310, 0x00421348)` | 56 | `6d46e88d2df85850b8ec35b4f55e5e0522884210c8bf5a3419e328599ffebf60` |
| Erase callback | `[0x00421348, 0x00421372)` | 42 | `df1788d1db60223b7af5050ab14307a3bf27f30fc6d61917adee77f679b3b872` |
| Mount wrapper | `[0x00415132, 0x0041513c)` | 10 | `b1ec5033634ac3d21aec8c912d993c6bb37ff44801657505658269b191090534` |
| Open wrapper | `[0x004153a4, 0x00415446)` | 162 | `800fce5063a3cf9eeea35d113fc4e009ed46453c80a71a2e9ea6d304b51f3588` |
| Close wrapper | `[0x00415446, 0x00415484)` | 62 | `86e71abbf3ac350622aae1d2d285499f9d7443a63939092bbf93c03ad4865d59` |
| Read wrapper | `[0x00415484, 0x004154d2)` | 78 | `0ed94f542c058e4a93e4bd04c9e6e98bc5262df242863162387612d2e8b0ff21` |
| Seek/prepare wrapper | `[0x004154d2, 0x0041552c)` | 90 | `e4d13d5b15990fa5dc083a4df5e6a4c428f9833206a6d1a61212b54a997892ea` |

The raw literal pool resolves the mount initializer’s filesystem object to `0x20026878`, configuration to `0x00431070`, and ready flag to `0x2002711c`. `0x421210` calls mount (`0x415132`). If mount fails, it formats (`0x415128`) and retries mount; a second failure logs and returns 9. It next ensures `/firmware`, `/ota`, `/user`, and `/log` exist, recovering through unmount/format/remount and retry if directory setup fails. On success it sets the ready flag and updates the `boot_count` file at `/boot_count`.

The DFU path reads `ota/s200_firmware_ota.bin` at `0x004336e4` using mode string `r+` at `0x0042dad8`. The file wrappers preserve the stock allocation size (`0x60`), mutex timeout argument (`1000`; units are not established here), mode-to-littlefs flags, element-count division on reads, seek validation, and close/free behavior.

## Storage geometry and callback contract

The littlefs configuration at `0x00431070` is the recovered 84-byte v2.10 configuration. It uses `read_size=16`, `prog_size=256`, `block_size=4096`, `block_count=3008`, `block_cycles=500`, `cache_size=4096`, and `lookahead_size=256`; the buffer pointers and optional maxima are zero. This maps littlefs blocks onto external NOR `[0x01400000,0x01fc0000)` (inclusive end `0x01fbffff`, 12,320,768 bytes).

The read/program/erase callbacks compute `0x01400000 + block*4096 + offset` (erase omits offset) and call `0x420f70`, `0x420b0c`, and `0x420a08`. Any nonzero provider status is logged and converted to littlefs `LFS_ERR_IO` (`-5`). The sync callback at `0x004213d4` returns zero. These contracts are independently represented in `filesystem.c`; the precise geometry bytes are checked by the existing `verify_arm.py` fixture against the locked image.

## Original/source evidence

`verify_file_services_differential.py` creates a valid littlefs image through ARM-compiled source on synthetic NOR, then remounts that same byte image in original firmware and compiled source. Both sides execute mount and the actual file open/prepare/read/close bodies on the exact DFU path and `r+` mode. They agree on successful mount/open, a 32-byte header read, a 9,001-byte payload read and SHA-256 (`ecfec1533dda6cf1ffe982e30c1bf9e0ab86a755c1ca989f93461a214a218c5c`), valid seek results, invalid-whence result `UINT32_MAX`, and close. The machine-readable comparison is in `file-services-comparison.json`.

During that comparison, the original mount wrapper executes stock littlefs and stock `0x4212d8` callbacks. NOR commands at `0x420f70/0x420b0c/0x420a08`, allocator, mutex and logging are explicit synthetic providers over mapped in-memory bytes. The source side executes ARM-compiled littlefs, file services and storage callbacks over the same bytes. It is not a test of an installed device filesystem.

`filesystem-source-arm.json` records the existing real-source verify/program run. `source-task-update-real-read.json` records a broader task run using source littlefs, filesystem wrappers, update core, DFU task, TLSF allocator, queue/runtime source, and the reconstructed NOR-read provider. It verifies and programs a 9,033-byte synthetic update image, then exercises modeled handoff after 122 synthetic PIO transfers through the read command. Lower MSPI/HAL is a provider cut; image-sector erase/program/readback remain synthetic. `source-task-update.json` is the earlier full-source task profile with direct synthetic NOR callbacks.

The existing host test also passed actual littlefs format, mount, write, seek, read, remount and wrapper failure cases under address/undefined sanitizers. The Cortex-M4 ARM library compiled cleanly; linker emitted the existing absolute-Thumb-provider warnings.

`g2/components/bootloader/filesystem/boot_mount.c/.h` provides the source initializer ABI `opencfw_provider_421210`. The original-instruction differential `verify_boot_mount_differential.py` passed four synthetic-NOR cases: blank-media format and repeated boot count; existing regular file at `/firmware` forcing stock `0x4211b0` recovery; and one failed mkdir program request exercising log-and-continue behavior. The stock and candidate executions matched return/ready state and the final NOR bytes in each case. Focused ASAN/UBSAN host coverage is available as `make -C g2/components/bootloader/filesystem host-boot-mount-test`; it uses a separate `/tmp` output directory. See `boot-mount.md` for exact entry identities and logging limits. This provider is not yet wired into the root combined linker/fixture.

## Remaining boundary

The repository and inspected backup inventory do not contain a physical, full-NOR filesystem image for the installed glasses. This limits claims about actual `/ota` contents and current on-device mount state, but does not block source development or synthetic comparisons. The boot initializer has a standalone source provider and passes direct original-instruction storage comparison for the exercised branches. Exact stock logger ABI, integration into the root combined linker/fixture, and full reset-to-update entry comparison remain open. No hardware access or writes were performed.
