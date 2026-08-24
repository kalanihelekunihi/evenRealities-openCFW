# G2 OTA service recovery

## Result

The retained first-party translation unit `platform\protocols\ota_service\ota_service.c` is closed as a linked binary object in the official G2 2.2.6.10 OTA image. Its physical interval is `[0x004448F4,0x004488EC)`: 16,376 bytes with SHA-256 `b58c8256ffee83bc9af1e920be4ba419f46e19695823a71dc8dc21c16be21acd`.

The object contains 25 linked functions. Twelve were retained-path anchors and thirteen adjacent pathless bodies were restored from source order, control flow, call topology, and the enclosing IAR object boundary. Their 15,394 concatenated body bytes hash to `2e6d2e90187fdd801af4f898a486524d2a03b64ba10a7cee6958c505ff76e3f1`. Seventeen owned alignment/literal-pool gaps total 982 bytes and hash to `60df545c40e9a17fbe5fae49b7942a9ae23b84f140731d1c05c74f9e2b8a9194`.

This binary inclusion and behavior closure is now paired with an independently authored, GPL-3.0-only production implementation at `components/apollo_main/core_overlay/ota_service.c`; no vendor implementation text was copied. The canonical Apple-clang build routes all 25 authenticated stock entries to 25 clean-room service leaves and uses four additional source-owned flash/status adapters. The 29 leaves compile to 3,130 text bytes plus 18 alignment bytes with 65 strict relocations. They replace all 15,394 stock function-body bytes while retaining the authenticated 982-byte alignment/literal/callback compatibility closure.

The resulting Apollo component is 3,746,344 bytes with SHA-256 `8e262f1ecea6bf0f3696d4216895e38bfc54f590a94fb628c0132e91e0bb118f`; the complete firmware package is 4,524,838 bytes with SHA-256 `61f5fc2763bbd2b17e6e28f09bb13bdfc38a21a9e072a51c88dbec171fcbdde3`.

## Function inventory

The exact ledger is pinned in `tools/manifests/g2-ota-service-function-map.tsv`. Retained names establish the main operations:

- `_evenOtaSetFwAddr`, `_verifyFlashContent`, and `_evenOtaBootloaderWriteFile2MRAM`
- `_otaFsHealthProbe` and `_otaFsHealthCheckAndHeal`
- `_fileCmdParse`, `_fileRawDataParse`, `_fileCaculateCRC`, and `_exportFileParse`
- `_evenOtaReplyToAPP`, `_RPC_SystemOtaStatusSync`, and `OTA_SetInterface`

The thirteen pathless functions are labeled `semantic_*` rather than assigned unevidenced historical names. They cover flash-operation selection, file sizing, range erase, buffered writes, descriptor commit, hexadecimal-address parsing, frame dispatch, export-state reset, three fixed status notifications, export cancellation, and the transfer-active query.

## Protocol contract

The frame dispatcher maps:

- `0xC0` to import/control parsing
- `0xC1` to raw import data and fixed two-byte status notifications
- `0xC2` and `0xC3` to export parsing

Observed control subcommands are 0 start, 1 continuation or activation, 2 result check, and 3 export cancellation. `_evenOtaReplyToAPP` emits a two-byte `{subcommand,status}` response unless the active interface is UART. `_RPC_SystemOtaStatusSync` reports OTA state to the system RPC. Three small helpers emit little-endian `0x0402`, `0x0302`, and `0x0502` payloads on frame `0xC1`.

The service recognizes product payloads including `ota/s200_firmware_ota.bin`, `ota/s200_bootloader.bin`, fonts, and touch, codec, EM9305 BLE, case, generic binary, and external-flash images. It routes writes across MRAM, filesystem, and external XIP flash backends. Flash operations use 4 KiB sectors, buffered 4 KiB chunks, CRC result checks, and read-after-write verification. The linked logic also includes filesystem health probing/healing and bootloader-to-MRAM installation.

The transfer state is 0x70 bytes; the export auxiliary state is 0x60 bytes; the shared chunk capacity is 0x1000 bytes. These sizes are behavioral ABI facts. They do not imply that historical C structure names or fields are known.

## Ingress and false-pointer closure

An exhaustive Thumb scan finds 107 direct calls to exact function entries: 68 intra-object and 39 exterior. Their ordered little-endian pair digest is `c1a4339a12650222a09af64f1b757f215bb9a52a7a526e461ca6c00630fadb90`. There are no direct calls or branches into a strict function interior.

Fourteen `B.W` targets are intentional intra-body jumps to shared epilogues inside `_fileCmdParse` and `_fileRawDataParse`; none is exterior or cross-function. An all-byte four-byte-window scan finds 81 numeric entry/interior collisions, but none is a legitimate aligned exact-entry function pointer. The one unaligned exact-entry window is data overlap, not stored ingress. This distinction prevents raw numeric coincidences from becoming false API claims.

## Reproduction

Run:

```sh
python3 openCFW/tools/analyze_g2_ota_service.py
python3 -m unittest openCFW.tests.test_analyze_g2_ota_service
```

The analyzer authenticates the official image, all three manifests, every function body, the complete physical interval, every owned gap, seven retained-path pointer cells, twelve retained symbols, direct calls, intra-body branches, raw pointer-like windows, all 29 source leaves, all 65 strict relocations, all 25 entry patches, appended-source ownership regions, and the component/package artifact pins. Host tests exercise backend selection, address/size rejection, import streaming, CRC and read-after-write failure handling, secure commit, status synchronization, filesystem healing, export, cancellation, and interface behavior; selector tests also compile every production leaf independently for Cortex-M55.

## Limitations

- The historical source-only function count remains unknown because no authenticated vendor source file is available; the clean-room production source contains 29 independently compiled leaves.
- Semantic names on pathless bodies are descriptive clean-room labels, not recovered symbols.
- Closure does not grant a license or justify copying vendor implementation text.
- Live OTA validation is explicitly blocked: no authorized responsive G2 peer and writable OTA target are physically available. The authorized right temple is nonresponsive and the left temple must remain stock, so MRAM/filesystem/XIP writes, bootloader installation, power-loss/rollback behavior, and peer-visible end-to-end status cannot be claimed as physically validated.
