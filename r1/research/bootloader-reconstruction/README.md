# Even Realities R1 bootloader reconstruction

Date: 2026-08-10

## Outcome

This directory is the reproducible reverse-engineering and clean functional-reconstruction package
for the live retail Even Realities R1 bootloader. The analyzed input is the read-only 24,576-byte
dump at `firmware/analysis/r1-live-2026-08-10/r1-bootloader-live.bin`, mapped at `0x000f8000` and
pinned to SHA-256:

```text
566cd2a50cd173680d314643e498202b364e4f8f8b6fd79b12ca71035e34ab8b
```

The logical linked image is 24,420 bytes (`0x5f64`), ending at `0x000fdf64`; the remaining 156
bytes through `0x000fe000` are erased padding.

The clean Ghidra 12.1.2 pass recovers 304 address-indexed functions and decompiles every one with
zero failures. Every function now has a useful name:

- 304 SDK/library, vector, compiler-runtime, or audit-derived names with an evidence/confidence record;
- zero residual synthetic names; and
- zero remaining `FUN_...` names.

Provider ownership is also complete for the bootloader: 218 Nordic SDK, 41 CryptoCell, 30 nanopb,
12 ArmCC/toolchain-runtime, and three R1-specific functions. Only those three product behaviors are
eligible for local clean-room implementation.

The package also contains a complete repository-contained
[`firmware-project`](firmware-project), a compile-tested C functional model, and the earlier nRF5
SDK overlay. The firmware project compiles the identified upstream implementation plus recovered R1
configuration and trust-anchor data into verified ELF/HEX/BIN outputs. These reproduce identified
behavior, not the vendor's unavailable original source text or compiler output. The separate
existing [`../r1-firmware-decompilation`](../r1-firmware-decompilation) corpus remains the
whole-firmware byte oracle for the application, bootloader, UICR, and runtime snapshots.

## Package map

| Path | Purpose |
| --- | --- |
| [`generated/r1_bootloader_ghidra.c`](generated/r1_bootloader_ghidra.c) | address-delimited C-like output for all 304 functions |
| [`generated/functions.csv`](generated/functions.csv) | exact function bodies, hashes, names, callers, and callees |
| [`generated/function-names.csv`](generated/function-names.csv) | previous/applied name, recovered-vs-synthetic class, confidence, and evidence |
| [`generated/source-correlations-raw.csv`](generated/source-correlations-raw.csv) | 12 ranked Ghidra BSim candidates per signature-bearing R1 function |
| [`generated/callgraph.csv`](generated/callgraph.csv) | direct call sites and resolved targets |
| [`generated/instructions.tsv`](generated/instructions.tsv) | decoded instruction address, bytes, operands, and owner |
| [`generated/vectors.csv`](generated/vectors.csv) | all 64 Cortex-M vector words and Thumb targets |
| [`generated/defined-data.csv`](generated/defined-data.csv) | Ghidra-defined data objects |
| [`generated/symbols.csv`](generated/symbols.csv) | all in-image symbols after naming |
| [`firmware-project`](firmware-project) | complete hash-pinned nRF52840/S140 C/assembly build producing ELF/HEX/BIN |
| [`functional-model`](functional-model) | compile-tested clean C model of security/update behavior |
| [`sdk-overlay`](sdk-overlay) | build-tested R1 public key, configuration deltas, and non-destructive GNU Make overlay |
| [`SOURCE-CORRELATION.md`](SOURCE-CORRELATION.md) | reference build and naming method/results |
| [`SECURITY-MODEL.md`](SECURITY-MODEL.md) | security-audit behavior incorporated into the reconstruction |
| [`MEMORY-MAP.md`](MEMORY-MAP.md) | linked flash/SRAM map |
| [`REBUILDABILITY.md`](REBUILDABILITY.md) | precise fidelity claims and remaining limits |

## Clean-pass metrics

| Metric | Value |
| --- | ---: |
| logical image bytes | 24,420 |
| recovered functions | 304 |
| decompiler failures | 0 |
| union of function-body bytes | 19,456 |
| decoded instruction bytes | 19,684 |
| Ghidra-defined data bytes | 2,619 |
| unclassified logical bytes | 2,117 |
| recovered names | 304 (268 high, 36 medium confidence) |
| synthetic descriptive names | 0 |
| BSim comparison rows | 3,576 across 298 signature-bearing R1 functions |

“Unclassified” includes vectors, alignment, literal/pointer tables, cryptographic constants, the
public key, scatter records, initialized-data bytes, and other non-instruction material. The byte
classes account for the complete logical image; they do not imply 2,117 bytes of missing code.

## Representative corrected names

The source-correlation pass did more than replace address labels. It corrected several earlier
semantic aliases:

| Address | Applied name | Evidence summary |
| ---: | --- | --- |
| `0x000f83c4` | `SVC_Handler` | vector slot 11 and SVC frame-dispatch semantics |
| `0x000fc3e4` | `nrf_svc_handler_c` | SVC tail target and BSim/source behavior |
| `0x000f8218...0x000f82ae` | `nrf_atfifo_*space_*` internal primitives | exact Nordic atomic-FIFO workspace/read-space source behavior; corrects former public-wrapper aliases |
| `0x000f82e0` | `nrf_atomic_internal_mov` | instruction-identical ArmCC SDK assembly helper |
| `0x000f9a10` / `0x000fadc8` | `SystemInit` / `main` | separates exact Nordic nRF52 startup/errata initialization from the secure-bootloader application entry |
| `0x000f8208` / `0x000f84c8` / `0x000f9c44...0x000f9c4c` | ArmCC runtime entry and scatterload/copy entries | startup literal, 16-byte scatter records, word-copy loop, and final branch to `main` |
| `0x000f852c...0x000f8cf4` | `PkaAddAff`, `PkaAddJcbAfn2Mdf`, point-doubling helpers, and `PkaEcdsaVerify` | exact CC310 archive symbols and scalar-multiply call topology; retained as Nordic-supplied CryptoCell provider code |
| `0x000f943c...0x000f948c` | CC310 HAL interrupt and PAL memory helpers | exact HOST register literals and provider wrapper slots |
| `0x000f9dc8...0x000f9ea8` | `app_sched_event_put`, `app_sched_execute`, `app_sched_init` | exact Nordic scheduler queue and critical-region behavior |
| `0x000f9f9c...0x000fa210` | BLE DFU service, response callback, transport lifecycle, and event handler | exact Nordic service/characteristic setup and event/request dispatch |
| `0x000fa65c` | `crc32_compute` | unique BSim candidate and `0xedb88320` literal |
| `0x000faf56` | `nrf_bootloader_app_start_final` | ACL, privilege reset, MSP load, vector jump, BSim significance 46.9 |
| `0x000fb0b8` | `nrf_bootloader_init` | Nordic initialization structure and BSim |
| `0x000fb994` | `nrf_dfu_settings_init` | flash-init → reinit → write/backup sequence |
| `0x000fb9d8` | `nrf_dfu_settings_reinit` | primary/backup validation and protected-range merge |
| `0x000fa54c` / `0x000fa594` / `0x000fa5a4` | `cc310_bl_backend_hash_sha256_finalize` / `init` / `update` | exact CC310_BL source semantics and immutable SHA-256 provider-table order |
| `0x000fa608` / `0x000fa640` | `cc310_bl_backend_init` / `uninit` | exact CC310_BL hardware-enable lifecycle and immutable backend-table order |
| `0x000fa4e4` / `0x000fa500` | `cc310_backend_mutex_trylock` / `unlock` | exact SDK mutex wrappers used by every recovered CC310_BL operation |
| `0x000fa510` / `0x000fa534` | `cc310_bl_backend_disable` / `enable` | exact interrupt-enabled hardware lifecycle paths |
| `0x000fabf4` | `hash_result_get` | exact CC310_BL SHA-256 error-to-NRF-result mapping |
| `0x000fae8c` / `0x000faea8` | `nrf_atomic_u32_fetch_or` / `fetch_store` | exact Nordic API wrappers over recovered internal atomic primitives |
| `0x000fadf8...0x000fae86` | public atomic-FIFO wrappers and `nrf_atomic_flag_clear` | exact SDK wrappers over the recovered internal FIFO/atomic primitives, including two non-contiguous compiler bodies |
| `0x000fa978` | `__NVIC_SystemReset` | exact CMSIS Cortex-M4 AIRCR reset sequence from the pinned Nordic SDK |
| `0x000fa118` | `ble_dfu_transport_close` | exact Nordic disconnect/advertising shutdown, 200 ms delay, and SDH-disable flow |
| `0x000fa178` | `ble_dfu_transport_init` | exact Nordic BLE DFU transport registration, advertising, and SoftDevice initialization flow |
| `0x000fa3f0...0x000fa400` | `boot_validate` / `boot_validation_crc` | exact Nordic CRC-skip validation gate and boot-validation settings CRC helper |
| `0x000fa40c` / `0x000fcff0` | `boot_validation_extract` / `postvalidate` | exact Nordic validation extraction and postvalidation state transitions |
| `0x000fa64c` / `0x000faaba...0x000faad8` | command response and extended-error helpers | exact Nordic request-handler state copies and extended-error normalization/read-clear/store behavior |
| `0x000fb198...0x000fb1c0` | `nrf_bootloader_wdt_feed`, feed-timer start, and watchdog init | exact Nordic watchdog lifecycle, including the recovered `3200`-tick reduction and `150`-tick floor |
| `0x000fb298` / `0x000fb3b8` | `nrf_crypto_ecc_public_key_from_raw` / `nrf_crypto_hash_update` | exact SDK validation and provider-dispatch paths |
| `0x000fb428` / `0x000fb4a0` | `nrf_crypto_internal_double_swap_endian` / `swap_endian` | exact SDK reverse-copy helpers |
| `0x000fc440` / `0x000fd78c` / `0x000fd7c8` | `nrf_wdt_started` / `wdt_feed` / timer handler | exact HAL status, seven-channel feed loop, and immutable callback thunk |
| `0x000fafdc` / `0x000fc114` / `0x000fd62c` / `0x000fd6bc` | inactivity restart / RTC event clear / timer init / timer stop | exact Nordic DFU timer-module and RTC HAL helpers |
| `0x000fb4d0...0x000fb52c` | bank-0/bank-1 address, invalidation, and cache preparation | exact Nordic DFU utility policies and page arithmetic |
| `0x000fb5c4...0x000fb7d8` | command/data request dispatch, `nrf_dfu_init`, MBR init, and request processing | exact Nordic object protocol and initialization state machine, including compiler-split bodies |
| `0x000fb8e4...0x000fbc28` | additional erase, progress reset, settings write, and validation init | exact Nordic settings/SVCI and stored-init-command lifecycle |
| `0x000fb6cc` / `0x000fb6f8` | `nrf_dfu_flash_erase` / `nrf_dfu_flash_store` | exact Nordic queued-flash API wrappers |
| `0x000fb73c` / `0x000fbb00` | `nrf_dfu_init_user` / `nrf_dfu_softdevice_start_address` | exact weak user-init slot and `MBR_SIZE` helper in their Nordic bootloader call sites |
| `0x000fb918` / `0x000fb988` / `0x000fd3fc` / `0x000fd410` | advertising-name copy and settings backup/CRC helpers | exact Nordic settings source ranges, callback wrappers, and fixed structure sizes |
| `0x000fbd5c` / `0x000fc134` / `0x000fc1d0` / `0x000fc330` | init-command state and SDH configuration/enable/state helpers | exact request and BLE stack call order; corrects the former `0xFC134` enable alias to `nrf_sdh_ble_default_cfg_set` |
| `0x000fbc4c...0x000fbcc8` | init-command append and execute | exact Nordic command-buffer bounds, decode, validation, and state flow |
| `0x000fbed4...0x000fc0d0` | fstorage and NVMC erase/write helpers | exact SDK public operations, event dispatch, ready polling, and word-write loops |
| `0x000fc1e4...0x000fc298` | SDH SOC poll, disable request, and enable request | exact Nordic SoftDevice lifecycle and observer control flow |
| `0x000fc394` | `nrf_section_iter_init` | exact empty-section skipping and iterator initialization |
| `0x000fd0f0...0x000fd1a0` | queue free/process/start | exact Nordic DFU flash-operation queue lifecycle |
| `0x000fd46c` / `0x000fd4ac` | SoftDevice-event IRQ disable/enable helpers | exact SDK NVIC wrappers and observer-state transitions |
| `0x000fd76c` | `verify_context` | exact static nrf_crypto hash context validator used by update and finalize |
| `0x000fc684` | `on_flash_write` | exact Nordic BLE DFU buffer-release callback, corroborated by its request callback-table slot |
| `0x000fd8b0` / `0x000fdaa0` | `nrfx_coredep_delay_machine_code_*` | duplicate compiler-emitted copies of Nordic's exact three-cycle delay-code array, distinguished by DFU-timer and BLE-DFU callers |
| `0x000fc718` | `pb_dec_bytes` | exact no-allocation nanopb bytes decoder in immutable decoder-table order |
| `0x000fad98` / `0x000fd1e0` | `iter_from_extension` / `read_raw_value` | exact nanopb extension iterator and callback wire-value reader |
| `0x000fc468` / `0x000fc690` | `on_ctrl_pt_write` / `on_rw_authorize_req` | exact Nordic BLE DFU control-point and write-authorization helpers |
| `0x000fd242...0x000fd6d0` | response encoding/sending, SoftDevice requirement checks, stored init decode, and `uint32_encode` | closes the residual Nordic DFU transport/version/validation helpers |
| `0x000fc75a` / `0x000fc760` | `pb_dec_fixed32` / `pb_dec_fixed64` | exact field-ignored nanopb wrappers to the bounded fixed-width decoders |
| `0x000fc766` | `pb_dec_string` | exact no-allocation nanopb string decoder in immutable decoder-table order |
| `0x000fc7e4` | `pb_dec_svarint` | seeded optimized function boundary and nanopb semantics |
| `0x000fc83c` | `pb_dec_uvarint` | bounded unsigned width/store behavior |
| `0x000fc894` | `pb_dec_varint` | signed-width/store behavior |
| `0x000fc8ec` | `pb_decode` | exact defaults-then-`pb_decode_noinit` wrapper with nanopb allocation support disabled |
| `0x000fce26` | `pb_message_set_to_defaults` | exact iterator-begin/default/iterator-next loop from SDK-bundled nanopb `pb_decode.c` |
| `0x000fcea4` | `pb_readbyte` | exact remaining-byte guard, one-byte callback read, and decrement helper |
| `0x000fcec4` | `pb_skip_field` | exact nanopb wire-type dispatch for varint, 64-bit, string, and 32-bit skips |
| `0x000fd1c4` | `nrf_fstorage_nvmc_read` | instruction-identical SDK NVMC-backend static `read`, qualified locally to keep names unique |
| `0x000fd1d2` | `nrf_fstorage_sd_read` | instruction-identical SDK SoftDevice-backend static `read`, qualified locally to keep names unique |

The immutable fstorage API tables additionally recover and source-route both backends' complete
`init`/`uninit`/`read`/`write`/`erase`/`rmap`/`wmap`/`is_busy` sets. Qualified names keep the
otherwise-identical static SDK symbols unique without claiming those qualifiers were in the binary.

The complete provenance ledger is [`generated/function-names.csv`](generated/function-names.csv).
All 304 entries are now source- or behavior-recovered. Qualified names for duplicate static SDK
functions preserve uniqueness without claiming that the qualification was stored in the binary.

## Reproduction

Requirements used here are Ghidra 12.1.2, Java 21, Python 3, and the pinned input.

```sh
scripts/firmware/run_r1_bootloader_decompilation.sh
make -C docs/r1-bootloader-reconstruction/functional-model test
python3 scripts/firmware/verify_r1_bootloader_reconstruction.py
```

Build the source-constructed target with Arm GNU Toolchain 9.3.1:

```sh
make -C docs/r1-bootloader-reconstruction/firmware-project verify \
  PROFILE=captured GNU_INSTALL_ROOT=/absolute/toolchain/bin/
```

For SDK correlation, first build the official reference described in
[`SDK-SOURCE-MANIFEST.md`](SDK-SOURCE-MANIFEST.md), then run:

```sh
scripts/firmware/run_r1_bootloader_source_correlation.sh /absolute/reference.elf
```

## Signing boundary

The reconstruction retains signature verification. It contains the public P-256 verification key
because that non-secret trust anchor is in the captured executable, but contains no private key,
package-signing step, unsigned acceptance mode, or verification-gate patch. “Minus code signing”
means that an unsigned local build can be compiled and analyzed; it does not mean removing secure
DFU enforcement from the installed product.
