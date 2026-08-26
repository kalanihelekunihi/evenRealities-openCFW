# G2 touch-controller DFU recovery

## Result

The retained first-party translation unit `platform\input\touchDFU\service_touch_dfu.c` is closed as a linked binary object in the official G2 2.2.6.10 OTA image. Its physical interval is `[0x0055FCB4,0x00561810)`: 7,004 bytes with SHA-256 `b53444478efe8eac988e311ee4a19f6ee07ab024779340847d77ba6845d5887b`.

The object contains 32 linked functions. Twelve are retained-path anchors and twenty adjacent pathless bodies were restored from source order, exact calls, literal ownership, and the enclosing IAR object boundary. Their 6,430 concatenated body bytes hash to `541a9a7deee567a6aa7b5a882a7daf4f86e65378bb1d10401cd612e69c1ba4ec`. Five owned alignment and literal-pool gaps total 574 bytes and hash to `1697430b30b5f4abe684049202b42ac41e749f6679b3f3e28d4058bc2216e228`.

This is binary inclusion and behavior closure, not historical source recovery. No authenticated historical source inventory or license was found. OpenCFW now supplies an independently authored 32-function GPL-3.0-only implementation in `components/apollo_main/core_overlay/service_touch_dfu.c`. Thirty-two guarded `B.W` redirects replace all 6,430 authenticated stock body bytes. The Apple-Clang Cortex-M55 build emits 3,134 Thumb text bytes plus 38 alignment bytes with 70 strict relocations; all 574 authenticated object-local gap/pool bytes remain official.

The canonical overlay is 251,578 bytes with SHA-256 `2def566dbf70594c89471066a7cd17f6d1fa94196f65ff48237385396e9cfd19`; the Apollo component is 3,774,974 bytes with SHA-256 `7228edb650fe39bda63480691fe94ed59d0807ca5e30846d35ec08e134e08350`; and the complete source package is 4,553,468 bytes with SHA-256 `c146ea7977a5521aa1df24a1a285768d7e2396fab96f117315a5baa2dcb65998`. Its flash plan hashes to `80d2f655555786d495d9df72b85013dee8e0076554b0d2deb82159a5c876e292` and accounts for 4,057 placed regions and two unresolved hardware payloads.

## Function inventory

The exact ledger is pinned in `tools/manifests/g2-service-touch-dfu-function-map.tsv`. Twelve names survive as exact strings:

- `TouchEnterDFU`, `TouchSetAppMeta`, `TouchSendOnePacket`, `TouchProgramData`, `TouchVerifyApp`, and `TouchExitDFU`;
- `TouchSendAppFile`, `free_touch_firmware_memory`, `get_touch_firmware_package_version`, and `load_touch_firmware_from_package`; and
- `isTouchNeedUpgrade` and `TouchUpdateFirmwareCheck`.

The twenty restored internal names use conservative `semantic_*` descriptions rather than unsupported historical symbols. They implement frame field accessors, frame construction and validation, the additive checksum, command retry, CRC-32, version formatting, and current-version logging.

## Package and memory contract

The package path is `/firmware/touch.bin`. Its 16-byte header begins with little-endian word `0x4B505746`, whose bytes spell `FWPK`, and carries the package version and firmware-record count. Each firmware record is 16 bytes. Type 3 selects the touch-controller firmware. The record supplies the stored size, file offset, and CRC. The loaded allocation includes a four-byte trailing checksum; the programmed application length is therefore the record size minus four.

The recovered persistent state is:

| Address | Meaning |
| --- | --- |
| `0x20074998` | package file handle |
| `0x2007499C` | firmware-buffer pointer |
| `0x200749A0` | firmware size |
| `0x200739BC` | current-version scratch |
| `0x20073E24` | touch transport/interface state |
| `0x0070F2A4` | CRC-32 nibble table |

Loading fails closed on malformed package metadata, absent type-3 data, allocation/read failure, or CRC mismatch. Cleanup releases the firmware buffer and clears its state.

## Frame and command protocol

An outgoing frame begins with byte `0x01`, followed by a one-byte command, a little-endian 16-bit payload length, the payload, a 16-bit checksum, and terminator byte `0x17`. The checksum is the 16-bit additive two's complement of the header and payload bytes (`payload_length + 4` bytes). Outgoing payloads are limited to 32 bytes.

Replies are capped at 15 bytes and must have a valid start byte, declared length, terminator, and checksum. Command transmission retries up to 100 times with a one-unit delay between attempts.

The recovered command map is:

| Command | Operation |
| --- | --- |
| `0x38` | enter DFU |
| `0x4C` | set application metadata |
| `0x37` | send one 32-byte packet |
| `0x49` | program the accumulated block |
| `0x31` | verify the application |
| `0x3B` | exit DFU |

`TouchSendAppFile` rounds the application length to 128 bytes. It emits four 32-byte packets for each block, then issues the program command. This preserves the device's 32-byte transport packet and 128-byte flash-programming granularities while padding only the final block.

## Upgrade orchestration

`TouchUpdateFirmwareCheck(force)` optionally compares the running touch-controller version with the version in `/firmware/touch.bin`; a forced update bypasses that equality check. When an update is needed it loads and validates the package, enters DFU, supplies application metadata, transfers and programs the image, verifies the result, exits DFU, and releases package memory on every terminal path.

The split between `get_touch_firmware_package_version`, `isTouchNeedUpgrade`, and `TouchUpdateFirmwareCheck` keeps the cheap version decision outside the destructive programming sequence. Errors from transport, package validation, programming, or verification prevent the remaining success path from being reported.

## Ingress and false-pointer closure

An exhaustive Thumb scan finds 60 calls to exact entries: 55 intra-object and five exterior calls. Their ordered little-endian pair digest is `40886bf36c1eeff76de7e2e94d3fd85c9a47bc44efa3f2e08b37001e41020e96`. The 32 bodies contain 394 direct calls with digest `51f1e146db48fafdbcc2b906a625b3926ec213e5cff7672ccda1c9eebc191fc4`. No direct call or `B.W` targets a strict interior.

The all-byte four-byte-window scan finds 23 numeric entry-or-interior collisions, with normalized digest `270bf0bfd92c344c42e117a20ac246103e9ef6962d4147b714edbd1779c510bc`. They are data windows rather than aligned stored entry pointers or branch targets. There are no aligned stored exact-entry pointers. Recording these collisions explicitly prevents unrelated packed bytes from becoming false ingress.

## Reproduction

Run the complete production gate:

```sh
make service-touch-dfu-closure
```

The analyzer authenticates the official image, all three manifests, every body and owned gap, both object boundaries, the retained path and three pointer cells, all twelve exact symbols, complete call topology, pointer-like windows, package/frame/state literals, production source and selector layout, all 70 relocations, 32 guarded redirects, source-manifest ownership, generated component, package, and flash plan. The host suite covers CRC-32C, exact framing, malformed replies, FWPK bounds/CRC/trailing-check exclusion, 32/128-byte programming granularity, same-version skip, forced update, cleanup, and the bounded transport-failure path.

## Limitations

- The historical source-only function count remains unknown because the source file is unavailable; the clean-room production inventory covers every one of the 32 linked entries.
- `semantic_*` labels are clean-room descriptions, not recovered symbols.
- Binary closure does not grant a license or justify copying vendor implementation text.
- The source routes through the authenticated CY8C transport/reset/version and filesystem seams, but timing and electrical behavior behind those seams require physical validation.
- Live destructive touch upgrade, controller reset, version readback, I2C timing, post-flash verification, and recovery remain explicitly blocked: the authorized right temple is nonresponsive, the authorized left temple must remain stock, and no responsive authorized pair, touch-controller fixture, or golden I2C/DFU capture is available. No image was signed or flashed, and wider firmware functional completeness is not claimed.
