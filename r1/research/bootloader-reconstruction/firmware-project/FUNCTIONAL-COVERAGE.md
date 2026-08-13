# Functional coverage and source ownership

The project follows the source-correlation result: the retail image is predominantly Nordic Secure
DFU plus identifiable bundled libraries. Upstream functionality is compiled from its upstream
implementation; R1-authored material is limited to recovered product data/configuration and build
verification.

| Recovered behavior | Project implementation | Origin | Validation |
| --- | --- | --- | --- |
| Cortex-M vectors, reset, system/errata setup | `modules/nrfx/mdk/gcc_startup_nrf52840.S`, `system_nrf52840.c` | Nordic/nrfx/CMSIS | SP `0x20040000`, Thumb reset vector in bootloader |
| boot decision, GPREGRET/buttonless entry, watchdog | `nrf_bootloader.c`, `nrf_bootloader_wdt.c` | Nordic | required symbols and recovered config macros |
| application handoff and ACL protection | `nrf_bootloader_app_start*.c` | Nordic | `nrf_bootloader_app_start_final` linked; recovered layout checked |
| app/SoftDevice/bootloader/combined activation | `nrf_bootloader_fw_activation.c`, `nrf_dfu_mbr.c` | Nordic | activation and MBR symbols linked |
| primary/backup settings reconciliation | `nrf_dfu_settings.c` | Nordic | source correlation plus functional-model tests |
| BLE Secure DFU service/transport | `nrf_dfu_ble.c`, SoftDevice handler sources | Nordic | `ble_dfu_transport_init` and observer sections linked |
| control-point request and DATA-object handling | `nrf_dfu_req_handler.c`, `nrf_dfu.c` | Nordic | request-handler symbols plus behavioral-model bounds tests |
| protobuf init-command parsing | `dfu-cc.pb.c`, nanopb `pb_common.c`/`pb_decode.c` | Nordic-generated + nanopb | parser symbols and source provenance |
| hardware/version/SoftDevice policy | `nrf_dfu_ver_validation.c` | Nordic | HW 52 and signed-update macros checked after preprocessing |
| ECDSA-P256/SHA-256 package authentication | `nrf_dfu_validation.c`, `nrf_crypto_*`, CC310 BL | Nordic/Arm | verifier requires signature-check and crypto symbols |
| independent image hash/postvalidation | `nrf_dfu_validation.c` | Nordic | validation symbols and behavioral-model hash tests |
| flash erase/write, SoftDevice/NVMC backends | `nrf_dfu_flash.c`, `nrf_fstorage*.c`, `nrf_nvmc.c` | Nordic/nrfx | linked source objects and symbols |
| CRC-32 `0xedb88320` implementation | `components/libraries/crc32/crc32.c` | Nordic | `crc32_compute` linked and clean-model vectors tested |
| scheduler, atomic FIFO, allocation, queues | Nordic library source units in `vendor/` | Nordic | all identified source families compiled |
| R1 public verification key | `src/r1_dfu_public_key.c` | recovered product data | compared to live flash and required exactly once in BIN |
| R1 36-page application-data reservation | `config/r1_recovered_config.h` | recovered product configuration | preprocessor/build configuration verification |
| captured debug-validation behavior | `captured` profile macro over Nordic behavior | recovered configuration | profile-specific macro and 64-byte code delta |
| repaired installed-app CRC behavior | `hardened` profile | reconstruction policy | absence of debug macro, valid signed-DFU path retained |

## Valid-input completeness

The target implements the complete valid-input behavior identified in the bootloader analysis:
startup, settings recovery, boot/DFU selection, BLE transport, control and DATA objects, nanopb init
commands, authenticated policy validation, bank management, image activation, and application
handoff. The build also retains vendor event scheduling, SoftDevice observers, flash backends, and
support libraries that are easy to omit from a host-only model.

The clean functional model remains the executable specification for audit-derived corner cases.
Its tests cover settings reconciliation, mandatory signature callbacks, version/hardware/SoftDevice
policy, signed-total and `0x1000` object bounds, postvalidation, activation selection, ACL ranges,
short control packets, bounded varints, and advertising-name bounds.

## Known fidelity boundary

Function count and byte placement differ because the captured binary appears to use a different
compiler/link pipeline and vendor product tree. The source-constructed captured profile uses 24,256
of 24,576 bootloader bytes versus 24,420 logical bytes in the live dump. Semantic source
correlation, matching layout, matching trust anchor/configuration, and complete subsystem linkage
support functional equivalence; they do not establish byte identity or hardware validation.

