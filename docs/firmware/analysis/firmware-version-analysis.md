# Firmware Version Analysis

Analysis performed 2026-03-03. All conclusions are derived from local firmware files only (`captures/firmware/**`, `docs/**`, `tools/**`). No API traces, CDN fetches, or web resources were used as evidence sources.

---

## 1. Corpus Overview

### Scope Lock

- Analysis boundary: local files only.
- Allowed evidence sources: `captures/firmware/**`, `docs/**`, `tools/**`.

### Traceability Template

| Claim ID | Conclusion | Evidence Path | Offset / String / Signature | Reproduction Command | Confidence |
|---|---|---|---|---|---|
| `CLM-###` | (What is true) | `captures/firmware/...` | `offset=0x...`, `"literal"`, checksum/hash match | `python3 ...` or `xxd ...` | `confirmed` / `likely` / `unknown` |

### Package Inventory

| Package Path | Size | SHA-256 | Magic (hex) | Inferred Format |
|---|---:|---|---|---|
| `captures/firmware/B210_ALWAY_BL_DFU_NO/bootloader.bin` | 24180 | `67cc2e9d3f70ea00e8246fe5715fd48067d6825a11425fa2a3c73bc9fc383714` | `a0cf0020d9830f00` | ARM image (vector-table start) |
| `captures/firmware/B210_BL_DFU_NO_v2.0.3.0004/bootloader.bin` | 24420 | `e049131a92c203e1c1f0abb067653e046c6955157e522914556004402f29ac60` | `a0cf0020d9830f00` | ARM image (vector-table start) |
| `captures/firmware/B210_SD_ONLY_NO_v2.0.3.0004/softdevice.bin` | 153140 | `192af010d0c5ca2111e14e644c02f79ac149f980c5ce7c729b006b1cf70eafd2` | `c0130020e15f0200` | ARM image (vector-table start) |
| `captures/firmware/g2_2.0.7.16.bin` | 3958551 | `47bdd17b9227d56566280fad42248dbecfe4fc70017ad9c74c3d949e27116b5e` | `4556454e4f544100` | EVENOTA container |
| `captures/firmware/g2_extracted/firmware_ble_em9305.bin` | 211948 | `91a38f7fc05555f86181ecb22b363e3239bfcaaa2ff6171e98524ae64821eca9` | `00020404703b0300` | Opaque binary blob |
| `captures/firmware/g2_extracted/firmware_box.bin` | 55296 | `d290f2b6899e69288b2b07b2d52471f193a4bf065f3eefe664c5a89aeadecb52` | `4556454e01023600` | EVEN wrapper |
| `captures/firmware/g2_extracted/firmware_codec.bin` | 319372 | `1c1462aff542d41429203e3a5d4cd53696f973133203cc44b9ae01523a551d03` | `4657504b00020000` | FWPK wrapper |
| `captures/firmware/g2_extracted/firmware_touch.bin` | 34080 | `35c49f3040fd75e251a2957d746f6ebc7c8a8401741f4d2ca8c33bffb3e0b823` | `4657504b00060002` | FWPK wrapper |
| `captures/firmware/g2_extracted/ota_s200_bootloader.bin` | 147727 | `5a5eb1d24160161e3fe5a020becd1c36ac68a59bdf27b491f47842555762d139` | `00fb0720cf244300` | ARM image (vector-table start) |
| `captures/firmware/g2_extracted/ota_s200_firmware_ota.bin` | 3189184 | `50f48eae3e031885086fa85d5e6f36d3d36582674adf5c6ec1d50da502f029eb` | `c0a930043f38a27b` | Opaque binary blob |
| `captures/firmware/g2_extracted/s200_firmware_raw.bin` | 3189152 | `3bd6e092fb5b3aa6dc35a15a9e380fd7663f97816c630f02fabab58994db1fb4` | `00fb072077975c00` | ARM image (vector-table start) |
| `captures/firmware/versions/g2_2.0.1.14.bin` | 3232068 | `d45005d5f75985339b234550b384899bb89fb37cfe4de4928abc9e882f0709e2` | `4556454e4f544100` | EVENOTA container |
| `captures/firmware/versions/g2_2.0.5.12.bin` | 3921853 | `83e3cc196df2d7bd74f735f2ffbfd9f01c204da2cb73a1fb6fee5119f1125e21` | `4556454e4f544100` | EVENOTA container |
| `captures/firmware/versions/v2.0.1.14/09fe9c0df7b14385c023bc35a364b3a9.bin` | 3232068 | `d45005d5f75985339b234550b384899bb89fb37cfe4de4928abc9e882f0709e2` | `4556454e4f544100` | EVENOTA container |
| `captures/firmware/versions/v2.0.3.20/57201a6e7cd6dadeee1bdb8f6ed98606.bin` | 3832044 | `84866f11895c34d15838736a373a50f06765232e2561fedd8ba1b62ba509c09c` | `4556454e4f544100` | EVENOTA container |
| `captures/firmware/versions/v2.0.5.12/53486f03b825cb22d13e769187b46656.bin` | 3921853 | `83e3cc196df2d7bd74f735f2ffbfd9f01c204da2cb73a1fb6fee5119f1125e21` | `4556454e4f544100` | EVENOTA container |
| `captures/firmware/versions/v2.0.6.14/0c9f9ca58785547278a5103bc6ae7a09.bin` | 3954281 | `f3c4c40aa122f61e859b82ee5eaa296ac8fa3a96e7b9905fd8d112ded732c5da` | `4556454e4f544100` | EVENOTA container |

### Version/Component Matrix

| Version | `firmware_ble_em9305.bin` | `firmware_box.bin` | `firmware_codec.bin` | `firmware_touch.bin` | `ota_s200_bootloader.bin` | `ota_s200_firmware_ota.bin` | `s200_firmware_raw.bin` |
|---|---|---|---|---|---|---|---|
| `2.0.1.14` | Y | Y | Y | Y | Y | Y |  |
| `2.0.3.20` | Y | Y | Y | Y | Y | Y |  |
| `2.0.5.12` | Y | Y | Y | Y | Y | Y |  |
| `2.0.6.14` | Y | Y | Y | Y | Y | Y |  |
| `2.0.7.16` | Y | Y | Y | Y | Y | Y | Y |

### Version Build Dates

| Version | Build Date | Build Time | Package | Extracted Dir |
|---|---|---|---|---|
| `2.0.1.14` | `2025-12-11` | `09:55:57` | `captures/firmware/versions/v2.0.1.14/09fe9c0df7b14385c023bc35a364b3a9.bin` | `captures/firmware/versions/v2.0.1.14/extracted` |
| `2.0.3.20` | `2025-12-31` | `16:36:51` | `captures/firmware/versions/v2.0.3.20/57201a6e7cd6dadeee1bdb8f6ed98606.bin` | `captures/firmware/versions/v2.0.3.20/extracted` |
| `2.0.5.12` | `2026-01-17` | `17:12:17` | `captures/firmware/versions/v2.0.5.12/53486f03b825cb22d13e769187b46656.bin` | `captures/firmware/versions/v2.0.5.12/extracted` |
| `2.0.6.14` | `2026-01-29` | `18:32:57` | `captures/firmware/versions/v2.0.6.14/0c9f9ca58785547278a5103bc6ae7a09.bin` | `captures/firmware/versions/v2.0.6.14/extracted` |
| `2.0.7.16` | `2026-02-13` | `18:47:47` | `captures/firmware/g2_2.0.7.16.bin` | `captures/firmware/g2_extracted` |

### CDN Artifact Retrieval

By varying the `common.versionName` header used for `GET /v2/g/check_latest_firmware`, the API returns older G2 packages:

| `common.versionName` | Returned firmware | CDN subPath |
|---|---|---|
| `2.0.7` | `2.0.7.16` | `/firmware/650176717d1f30ef684e5f812500903c.bin` |
| `2.0.5` | `2.0.5.12` | `/firmware/53486f03b825cb22d13e769187b46656.bin` |
| `1.8.0` | `2.0.1.14` | `/firmware/09fe9c0df7b14385c023bc35a364b3a9.bin` |

---

## 2. EVENOTA Container Format

### Field Semantics (Confirmed)

| Structure | Offset | Size | Meaning |
|---|---:|---:|---|
| Container header | `+0x00` | 8 | Magic `EVENOTA\0` |
| Container header | `+0x08` | 4 | Entry count (`LE32`) |
| Entry table row | `+0x00` | 4 | Entry ID (`LE32`) |
| Entry table row | `+0x04` | 4 | Entry absolute offset (`LE32`) |
| Entry table row | `+0x08` | 4 | Entry size (`LE32`) |
| Entry table row | `+0x0C` | 4 | Entry checksum in TOC (`LE32`) |
| Entry sub-header | `+0x08` | 4 | Payload size (`LE32`) |
| Entry sub-header | `+0x0C` | 4 | Entry checksum in sub-header (`LE32`) |
| Entry sub-header | `+0x24` | 4 | Type ID (`LE32`) |
| Entry sub-header | `+0x30` | 32 | Null-terminated entry filename |
| Entry payload | `+0x80` | variable | Payload coverage for checksum calculation |

Checksum rule (validated for all rows): `crc32c_msb(payload_bytes) == toc_checksum == sub_checksum`

### Package-Level Validation

| Package | File Size | Entries | Table Start | Table End | Contiguous | Closes At EOF | Bounds OK | Payload Size OK | Checksum OK |
|---|---:|---:|---:|---:|---|---|---|---|---|
| `g2_2.0.7.16.bin` | 3958551 | 6 | `0x40` | `0xA0` | `True` | `True` | `True` | `True` | `True` |
| `g2_2.0.1.14.bin` | 3232068 | 6 | `0x40` | `0xA0` | `True` | `True` | `True` | `True` | `True` |
| `g2_2.0.5.12.bin` | 3921853 | 6 | `0x40` | `0xA0` | `True` | `True` | `True` | `True` | `True` |
| `v2.0.1.14/09fe9c0d...` | 3232068 | 6 | `0x40` | `0xA0` | `True` | `True` | `True` | `True` | `True` |
| `v2.0.3.20/57201a6e...` | 3832044 | 6 | `0x40` | `0xA0` | `True` | `True` | `True` | `True` | `True` |
| `v2.0.5.12/53486f03...` | 3921853 | 6 | `0x40` | `0xA0` | `True` | `True` | `True` | `True` | `True` |
| `v2.0.6.14/0c9f9ca5...` | 3954281 | 6 | `0x40` | `0xA0` | `True` | `True` | `True` | `True` | `True` |

### Confirmed Integrity Algorithms

- **EVENOTA**: `crc32c_msb(payload)` where `payload = package[entry_offset+0x80 : entry_offset+entry_size]`. CRC32C (Castagnoli, MSB-first, poly=0x1EDC6F41, init=0x00000000, xorout=0x00000000).
- **Touch FWPK**: reflected CRC32C over `touch[payload_offset : payload_offset+payload_size]` (payload reaches EOF in all sampled versions).
- **Codec FWPK**: CRC32 over each declared segment range (`segment0`, `segment1`).
- **Box EVEN**: additive sum of big-endian 32-bit words over `box[0x20 : 0x20+payload_length]` (zero-padded final partial word).
- **Main OTA preamble**: CRC32 over `ota_s200_firmware_ota.bin[0x08 : EOF]`.

### EVENOTA Coverage Proof (Cross-Version)

| Version | Entry | Type | Filename | Payload Range | TOC | Sub | Calc CRC32C-MSB | Bounds | Payload Size | Match |
|---|---:|---:|---|---|---|---|---|---|---|---|
| `2.0.1.14` | 1 | 4 | `firmware/codec.bin` | `[0x130, 0x4E0BC)` | `0xED6AD847` | `0xED6AD847` | `0xED6AD847` | `True` | `True` | `True` |
| `2.0.1.14` | 2 | 5 | `firmware/ble_em9305.bin` | `[0x4E13C, 0x81D28)` | `0xC074BAF7` | `0xC074BAF7` | `0xC074BAF7` | `True` | `True` | `True` |
| `2.0.1.14` | 3 | 3 | `firmware/touch.bin` | `[0x81DA8, 0x88A48)` | `0xB270E42D` | `0xB270E42D` | `0xB270E42D` | `True` | `True` | `True` |
| `2.0.1.14` | 4 | 6 | `firmware/box.bin` | `[0x88AC8, 0x95AF8)` | `0x980E79E5` | `0x980E79E5` | `0x980E79E5` | `True` | `True` | `True` |
| `2.0.1.14` | 5 | 1 | `ota/s200_bootloader.bin` | `[0x95B78, 0xB9B1C)` | `0x4F17170A` | `0x4F17170A` | `0x4F17170A` | `True` | `True` | `True` |
| `2.0.1.14` | 6 | 0 | `ota/s200_firmware_ota.bin` | `[0xB9B9C, 0x315144)` | `0x6445DC3F` | `0x6445DC3F` | `0x6445DC3F` | `True` | `True` | `True` |
| `2.0.3.20` | 1 | 4 | `firmware/codec.bin` | `[0x130, 0x4E0BC)` | `0xED6AD847` | `0xED6AD847` | `0xED6AD847` | `True` | `True` | `True` |
| `2.0.3.20` | 2 | 5 | `firmware/ble_em9305.bin` | `[0x4E13C, 0x81D28)` | `0xC074BAF7` | `0xC074BAF7` | `0xC074BAF7` | `True` | `True` | `True` |
| `2.0.3.20` | 3 | 3 | `firmware/touch.bin` | `[0x81DA8, 0x88BC8)` | `0xBD834F67` | `0xBD834F67` | `0xBD834F67` | `True` | `True` | `True` |
| `2.0.3.20` | 4 | 6 | `firmware/box.bin` | `[0x88C48, 0x96398)` | `0xB9D4D4A3` | `0xB9D4D4A3` | `0xB9D4D4A3` | `True` | `True` | `True` |
| `2.0.3.20` | 5 | 1 | `ota/s200_bootloader.bin` | `[0x96418, 0xBA3B8)` | `0xD31CE1EA` | `0xD31CE1EA` | `0xD31CE1EA` | `True` | `True` | `True` |
| `2.0.3.20` | 6 | 0 | `ota/s200_firmware_ota.bin` | `[0xBA438, 0x3A78EC)` | `0x4DD85AB3` | `0x4DD85AB3` | `0x4DD85AB3` | `True` | `True` | `True` |
| `2.0.5.12` | 1 | 4 | `firmware/codec.bin` | `[0x130, 0x4E0BC)` | `0xED6AD847` | `0xED6AD847` | `0xED6AD847` | `True` | `True` | `True` |
| `2.0.5.12` | 2 | 5 | `firmware/ble_em9305.bin` | `[0x4E13C, 0x81D28)` | `0xC074BAF7` | `0xC074BAF7` | `0xC074BAF7` | `True` | `True` | `True` |
| `2.0.5.12` | 3 | 3 | `firmware/touch.bin` | `[0x81DA8, 0x88C48)` | `0x7D5A89E9` | `0x7D5A89E9` | `0x7D5A89E9` | `True` | `True` | `True` |
| `2.0.5.12` | 4 | 6 | `firmware/box.bin` | `[0x88CC8, 0x96418)` | `0xB9D4D4A3` | `0xB9D4D4A3` | `0xB9D4D4A3` | `True` | `True` | `True` |
| `2.0.5.12` | 5 | 1 | `ota/s200_bootloader.bin` | `[0x96498, 0xBA561)` | `0x1DD577BA` | `0x1DD577BA` | `0x1DD577BA` | `True` | `True` | `True` |
| `2.0.5.12` | 6 | 0 | `ota/s200_firmware_ota.bin` | `[0xBA5E1, 0x3BD7BD)` | `0x3BB98935` | `0x3BB98935` | `0x3BB98935` | `True` | `True` | `True` |
| `2.0.6.14` | 1 | 4 | `firmware/codec.bin` | `[0x130, 0x4E0BC)` | `0xED6AD847` | `0xED6AD847` | `0xED6AD847` | `True` | `True` | `True` |
| `2.0.6.14` | 2 | 5 | `firmware/ble_em9305.bin` | `[0x4E13C, 0x81D28)` | `0xC074BAF7` | `0xC074BAF7` | `0xC074BAF7` | `True` | `True` | `True` |
| `2.0.6.14` | 3 | 3 | `firmware/touch.bin` | `[0x81DA8, 0x8A2C8)` | `0x419965B4` | `0x419965B4` | `0x419965B4` | `True` | `True` | `True` |
| `2.0.6.14` | 4 | 6 | `firmware/box.bin` | `[0x8A348, 0x97B48)` | `0xF0C5546F` | `0xF0C5546F` | `0xF0C5546F` | `True` | `True` | `True` |
| `2.0.6.14` | 5 | 1 | `ota/s200_bootloader.bin` | `[0x97BC8, 0xBBC91)` | `0x714713A7` | `0x714713A7` | `0x714713A7` | `True` | `True` | `True` |
| `2.0.6.14` | 6 | 0 | `ota/s200_firmware_ota.bin` | `[0xBBD11, 0x3C5669)` | `0x12588627` | `0x12588627` | `0x12588627` | `True` | `True` | `True` |
| `2.0.7.16` | 1 | 4 | `firmware/codec.bin` | `[0x130, 0x4E0BC)` | `0xED6AD847` | `0xED6AD847` | `0xED6AD847` | `True` | `True` | `True` |
| `2.0.7.16` | 2 | 5 | `firmware/ble_em9305.bin` | `[0x4E13C, 0x81D28)` | `0xC074BAF7` | `0xC074BAF7` | `0xC074BAF7` | `True` | `True` | `True` |
| `2.0.7.16` | 3 | 3 | `firmware/touch.bin` | `[0x81DA8, 0x8A2C8)` | `0x419965B4` | `0x419965B4` | `0x419965B4` | `True` | `True` | `True` |
| `2.0.7.16` | 4 | 6 | `firmware/box.bin` | `[0x8A348, 0x97B48)` | `0xF0C5546F` | `0xF0C5546F` | `0xF0C5546F` | `True` | `True` | `True` |
| `2.0.7.16` | 5 | 1 | `ota/s200_bootloader.bin` | `[0x97BC8, 0xBBCD7)` | `0xBB434910` | `0xBB434910` | `0xBB434910` | `True` | `True` | `True` |
| `2.0.7.16` | 6 | 0 | `ota/s200_firmware_ota.bin` | `[0xBBD57, 0x3C6717)` | `0xCC6CF1D8` | `0xCC6CF1D8` | `0xCC6CF1D8` | `True` | `True` | `True` |

### Entry-Level Validation (Full Detail)

| Package | ID | Type | Filename | Offset | Size | End | Payload Size Field | Derived Payload Size | TOC CKSUM | Sub CKSUM | Calc CKSUM | Bounds OK | Payload OK | CKSUM OK |
|---|---:|---:|---|---:|---:|---:|---:|---:|---|---|---|---|---|---|
| `g2_2.0.7.16.bin` | 1 | 4 | `firmware/codec.bin` | `0xB0` | `0x4E00C` | `0x4E0BC` | `0x4DF8C` | `0x4DF8C` | `0xED6AD847` | `0xED6AD847` | `0xED6AD847` | `True` | `True` | `True` |
| `g2_2.0.7.16.bin` | 2 | 5 | `firmware/ble_em9305.bin` | `0x4E0BC` | `0x33C6C` | `0x81D28` | `0x33BEC` | `0x33BEC` | `0xC074BAF7` | `0xC074BAF7` | `0xC074BAF7` | `True` | `True` | `True` |
| `g2_2.0.7.16.bin` | 3 | 3 | `firmware/touch.bin` | `0x81D28` | `0x85A0` | `0x8A2C8` | `0x8520` | `0x8520` | `0x419965B4` | `0x419965B4` | `0x419965B4` | `True` | `True` | `True` |
| `g2_2.0.7.16.bin` | 4 | 6 | `firmware/box.bin` | `0x8A2C8` | `0xD880` | `0x97B48` | `0xD800` | `0xD800` | `0xF0C5546F` | `0xF0C5546F` | `0xF0C5546F` | `True` | `True` | `True` |
| `g2_2.0.7.16.bin` | 5 | 1 | `ota/s200_bootloader.bin` | `0x97B48` | `0x2418F` | `0xBBCD7` | `0x2410F` | `0x2410F` | `0xBB434910` | `0xBB434910` | `0xBB434910` | `True` | `True` | `True` |
| `g2_2.0.7.16.bin` | 6 | 0 | `ota/s200_firmware_ota.bin` | `0xBBCD7` | `0x30AA40` | `0x3C6717` | `0x30A9C0` | `0x30A9C0` | `0xCC6CF1D8` | `0xCC6CF1D8` | `0xCC6CF1D8` | `True` | `True` | `True` |
| `g2_2.0.1.14.bin` | 1 | 4 | `firmware/codec.bin` | `0xB0` | `0x4E00C` | `0x4E0BC` | `0x4DF8C` | `0x4DF8C` | `0xED6AD847` | `0xED6AD847` | `0xED6AD847` | `True` | `True` | `True` |
| `g2_2.0.1.14.bin` | 2 | 5 | `firmware/ble_em9305.bin` | `0x4E0BC` | `0x33C6C` | `0x81D28` | `0x33BEC` | `0x33BEC` | `0xC074BAF7` | `0xC074BAF7` | `0xC074BAF7` | `True` | `True` | `True` |
| `g2_2.0.1.14.bin` | 3 | 3 | `firmware/touch.bin` | `0x81D28` | `0x6D20` | `0x88A48` | `0x6CA0` | `0x6CA0` | `0xB270E42D` | `0xB270E42D` | `0xB270E42D` | `True` | `True` | `True` |
| `g2_2.0.1.14.bin` | 4 | 6 | `firmware/box.bin` | `0x88A48` | `0xD0B0` | `0x95AF8` | `0xD030` | `0xD030` | `0x980E79E5` | `0x980E79E5` | `0x980E79E5` | `True` | `True` | `True` |
| `g2_2.0.1.14.bin` | 5 | 1 | `ota/s200_bootloader.bin` | `0x95AF8` | `0x24024` | `0xB9B1C` | `0x23FA4` | `0x23FA4` | `0x4F17170A` | `0x4F17170A` | `0x4F17170A` | `True` | `True` | `True` |
| `g2_2.0.1.14.bin` | 6 | 0 | `ota/s200_firmware_ota.bin` | `0xB9B1C` | `0x25B628` | `0x315144` | `0x25B5A8` | `0x25B5A8` | `0x6445DC3F` | `0x6445DC3F` | `0x6445DC3F` | `True` | `True` | `True` |
| `v2.0.3.20/57201a6e...` | 1 | 4 | `firmware/codec.bin` | `0xB0` | `0x4E00C` | `0x4E0BC` | `0x4DF8C` | `0x4DF8C` | `0xED6AD847` | `0xED6AD847` | `0xED6AD847` | `True` | `True` | `True` |
| `v2.0.3.20/57201a6e...` | 2 | 5 | `firmware/ble_em9305.bin` | `0x4E0BC` | `0x33C6C` | `0x81D28` | `0x33BEC` | `0x33BEC` | `0xC074BAF7` | `0xC074BAF7` | `0xC074BAF7` | `True` | `True` | `True` |
| `v2.0.3.20/57201a6e...` | 3 | 3 | `firmware/touch.bin` | `0x81D28` | `0x6EA0` | `0x88BC8` | `0x6E20` | `0x6E20` | `0xBD834F67` | `0xBD834F67` | `0xBD834F67` | `True` | `True` | `True` |
| `v2.0.3.20/57201a6e...` | 4 | 6 | `firmware/box.bin` | `0x88BC8` | `0xD7D0` | `0x96398` | `0xD750` | `0xD750` | `0xB9D4D4A3` | `0xB9D4D4A3` | `0xB9D4D4A3` | `True` | `True` | `True` |
| `v2.0.3.20/57201a6e...` | 5 | 1 | `ota/s200_bootloader.bin` | `0x96398` | `0x24020` | `0xBA3B8` | `0x23FA0` | `0x23FA0` | `0xD31CE1EA` | `0xD31CE1EA` | `0xD31CE1EA` | `True` | `True` | `True` |
| `v2.0.3.20/57201a6e...` | 6 | 0 | `ota/s200_firmware_ota.bin` | `0xBA3B8` | `0x2ED534` | `0x3A78EC` | `0x2ED4B4` | `0x2ED4B4` | `0x4DD85AB3` | `0x4DD85AB3` | `0x4DD85AB3` | `True` | `True` | `True` |
| `v2.0.5.12/53486f03...` | 1 | 4 | `firmware/codec.bin` | `0xB0` | `0x4E00C` | `0x4E0BC` | `0x4DF8C` | `0x4DF8C` | `0xED6AD847` | `0xED6AD847` | `0xED6AD847` | `True` | `True` | `True` |
| `v2.0.5.12/53486f03...` | 2 | 5 | `firmware/ble_em9305.bin` | `0x4E0BC` | `0x33C6C` | `0x81D28` | `0x33BEC` | `0x33BEC` | `0xC074BAF7` | `0xC074BAF7` | `0xC074BAF7` | `True` | `True` | `True` |
| `v2.0.5.12/53486f03...` | 3 | 3 | `firmware/touch.bin` | `0x81D28` | `0x6F20` | `0x88C48` | `0x6EA0` | `0x6EA0` | `0x7D5A89E9` | `0x7D5A89E9` | `0x7D5A89E9` | `True` | `True` | `True` |
| `v2.0.5.12/53486f03...` | 4 | 6 | `firmware/box.bin` | `0x88C48` | `0xD7D0` | `0x96418` | `0xD750` | `0xD750` | `0xB9D4D4A3` | `0xB9D4D4A3` | `0xB9D4D4A3` | `True` | `True` | `True` |
| `v2.0.5.12/53486f03...` | 5 | 1 | `ota/s200_bootloader.bin` | `0x96418` | `0x24149` | `0xBA561` | `0x240C9` | `0x240C9` | `0x1DD577BA` | `0x1DD577BA` | `0x1DD577BA` | `True` | `True` | `True` |
| `v2.0.5.12/53486f03...` | 6 | 0 | `ota/s200_firmware_ota.bin` | `0xBA561` | `0x30325C` | `0x3BD7BD` | `0x3031DC` | `0x3031DC` | `0x3BB98935` | `0x3BB98935` | `0x3BB98935` | `True` | `True` | `True` |
| `v2.0.6.14/0c9f9ca5...` | 1 | 4 | `firmware/codec.bin` | `0xB0` | `0x4E00C` | `0x4E0BC` | `0x4DF8C` | `0x4DF8C` | `0xED6AD847` | `0xED6AD847` | `0xED6AD847` | `True` | `True` | `True` |
| `v2.0.6.14/0c9f9ca5...` | 2 | 5 | `firmware/ble_em9305.bin` | `0x4E0BC` | `0x33C6C` | `0x81D28` | `0x33BEC` | `0x33BEC` | `0xC074BAF7` | `0xC074BAF7` | `0xC074BAF7` | `True` | `True` | `True` |
| `v2.0.6.14/0c9f9ca5...` | 3 | 3 | `firmware/touch.bin` | `0x81D28` | `0x85A0` | `0x8A2C8` | `0x8520` | `0x8520` | `0x419965B4` | `0x419965B4` | `0x419965B4` | `True` | `True` | `True` |
| `v2.0.6.14/0c9f9ca5...` | 4 | 6 | `firmware/box.bin` | `0x8A2C8` | `0xD880` | `0x97B48` | `0xD800` | `0xD800` | `0xF0C5546F` | `0xF0C5546F` | `0xF0C5546F` | `True` | `True` | `True` |
| `v2.0.6.14/0c9f9ca5...` | 5 | 1 | `ota/s200_bootloader.bin` | `0x97B48` | `0x24149` | `0xBBC91` | `0x240C9` | `0x240C9` | `0x714713A7` | `0x714713A7` | `0x714713A7` | `True` | `True` | `True` |
| `v2.0.6.14/0c9f9ca5...` | 6 | 0 | `ota/s200_firmware_ota.bin` | `0xBBC91` | `0x3099D8` | `0x3C5669` | `0x309958` | `0x309958` | `0x12588627` | `0x12588627` | `0x12588627` | `True` | `True` | `True` |

### Wrapper Coverage Proof (FWPK / EVEN)

#### Touch FWPK

| Version | Range | Field | Calc | Magic | firmware_count | In File | EOF-Aligned | Match |
|---|---|---|---|---|---:|---|---|---|
| `2.0.1.14` | `[0x20, 0x6CA0)` | `0x48674BC7` | `0x48674BC7` | `FWPK` | 3 | `True` | `True` | `True` |
| `2.0.3.20` | `[0x20, 0x6E20)` | `0x48674BC7` | `0x48674BC7` | `FWPK` | 3 | `True` | `True` | `True` |
| `2.0.5.12` | `[0x20, 0x6EA0)` | `0x48674BC7` | `0x48674BC7` | `FWPK` | 3 | `True` | `True` | `True` |
| `2.0.6.14` | `[0x20, 0x8520)` | `0x48674BC7` | `0x48674BC7` | `FWPK` | 3 | `True` | `True` | `True` |
| `2.0.7.16` | `[0x20, 0x8520)` | `0x48674BC7` | `0x48674BC7` | `FWPK` | 3 | `True` | `True` | `True` |

#### Codec FWPK Segments

| Version | Segment | Range | Field CRC32 | Calc CRC32 | In File | Match |
|---|---:|---|---|---|---|---|
| `2.0.1.14` | 0 | `[0x30, 0x958C)` | `0x307E8A10` | `0x307E8A10` | `True` | `True` |
| `2.0.1.14` | 1 | `[0x958C, 0x4DF8C)` | `0xB281D56C` | `0xB281D56C` | `True` | `True` |
| `2.0.3.20` | 0 | `[0x30, 0x958C)` | `0x307E8A10` | `0x307E8A10` | `True` | `True` |
| `2.0.3.20` | 1 | `[0x958C, 0x4DF8C)` | `0xB281D56C` | `0xB281D56C` | `True` | `True` |
| `2.0.5.12` | 0 | `[0x30, 0x958C)` | `0x307E8A10` | `0x307E8A10` | `True` | `True` |
| `2.0.5.12` | 1 | `[0x958C, 0x4DF8C)` | `0xB281D56C` | `0xB281D56C` | `True` | `True` |
| `2.0.6.14` | 0 | `[0x30, 0x958C)` | `0x307E8A10` | `0x307E8A10` | `True` | `True` |
| `2.0.6.14` | 1 | `[0x958C, 0x4DF8C)` | `0xB281D56C` | `0xB281D56C` | `True` | `True` |
| `2.0.7.16` | 0 | `[0x30, 0x958C)` | `0x307E8A10` | `0x307E8A10` | `True` | `True` |
| `2.0.7.16` | 1 | `[0x958C, 0x4DF8C)` | `0xB281D56C` | `0xB281D56C` | `True` | `True` |

#### Box EVEN

| Version | Range | Length Field | Field SUM | Calc SUM | In File | Tail Match | Match |
|---|---|---|---|---|---|---|---|
| `2.0.1.14` | `[0x20, 0xD030)` | `0xD010` | `0xA1D50BFE` | `0xA1D50BFE` | `True` | `True` | `True` |
| `2.0.3.20` | `[0x20, 0xD750)` | `0xD730` | `0x7054D5D8` | `0x7054D5D8` | `True` | `True` | `True` |
| `2.0.5.12` | `[0x20, 0xD750)` | `0xD730` | `0x7054D5D8` | `0x7054D5D8` | `True` | `True` | `True` |
| `2.0.6.14` | `[0x20, 0xD800)` | `0xD7E0` | `0x4C44DA98` | `0x4C44DA98` | `True` | `True` | `True` |
| `2.0.7.16` | `[0x20, 0xD800)` | `0xD7E0` | `0x4C44DA98` | `0x4C44DA98` | `True` | `True` | `True` |

#### Main OTA Preamble

| Version | Coverage | Field CRC32 | Calc CRC32 | Match |
|---|---|---|---|---|
| `2.0.1.14` | `[0x8, 0x25B5A8)` | `0xBDC6CEC9` | `0xBDC6CEC9` | `True` |
| `2.0.3.20` | `[0x8, 0x2ED4B4)` | `0x0D367398` | `0x0D367398` | `True` |
| `2.0.5.12` | `[0x8, 0x3031DC)` | `0xBDE9C048` | `0xBDE9C048` | `True` |
| `2.0.6.14` | `[0x8, 0x309958)` | `0x33A89446` | `0x33A89446` | `True` |
| `2.0.7.16` | `[0x8, 0x30A9C0)` | `0x7BA2383F` | `0x7BA2383F` | `True` |

### OTA Packaging Order and Dependency Clues

| Version | Type Order | Filename Order | Contiguous | Closes EOF | All Rows OK |
|---|---|---|---|---|---|
| `2.0.1.14` | `4, 5, 3, 6, 1, 0` | `firmware/codec.bin -> firmware/ble_em9305.bin -> firmware/touch.bin -> firmware/box.bin -> ota/s200_bootloader.bin -> ota/s200_firmware_ota.bin` | `True` | `True` | `True` |
| `2.0.3.20` | `4, 5, 3, 6, 1, 0` | `firmware/codec.bin -> firmware/ble_em9305.bin -> firmware/touch.bin -> firmware/box.bin -> ota/s200_bootloader.bin -> ota/s200_firmware_ota.bin` | `True` | `True` | `True` |
| `2.0.5.12` | `4, 5, 3, 6, 1, 0` | `firmware/codec.bin -> firmware/ble_em9305.bin -> firmware/touch.bin -> firmware/box.bin -> ota/s200_bootloader.bin -> ota/s200_firmware_ota.bin` | `True` | `True` | `True` |
| `2.0.6.14` | `4, 5, 3, 6, 1, 0` | `firmware/codec.bin -> firmware/ble_em9305.bin -> firmware/touch.bin -> firmware/box.bin -> ota/s200_bootloader.bin -> ota/s200_firmware_ota.bin` | `True` | `True` | `True` |
| `2.0.7.16` | `4, 5, 3, 6, 1, 0` | `firmware/codec.bin -> firmware/ble_em9305.bin -> firmware/touch.bin -> firmware/box.bin -> ota/s200_bootloader.bin -> ota/s200_firmware_ota.bin` | `True` | `True` | `True` |

#### Sequencing String Clues in `ota_s200_firmware_ota.bin`

| Version | Handler Order (by offset) | Path Order (by offset) |
|---|---|---|
| `2.0.1.14` | `box_ota_begin@0x203F1C -> ble_header@0x20513C -> touch_package_info@0x2117AC -> codec_package_info@0x21454C` | `path_box@0x21AECA -> path_ble@0x23F555 -> path_touch@0x24BC20 -> path_codec@0x24BC34` |
| `2.0.3.20` | `box_ota_begin@0x22CB10 -> ble_header@0x25B5DC -> touch_package_info@0x269D20 -> codec_package_info@0x277E0C` | `path_box@0x271F16 -> path_ble@0x2CD345 -> path_touch@0x2DBD30 -> path_codec@0x2DBD44` |
| `2.0.5.12` | `box_ota_begin@0x2379F0 -> ble_header@0x2669A4 -> touch_package_info@0x278400 -> codec_package_info@0x288F2C` | `path_box@0x28210E -> path_ble@0x2E28A1 -> path_touch@0x2F1928 -> path_codec@0x2F193C` |
| `2.0.6.14` | `box_ota_begin@0x23A4F8 -> ble_header@0x26949C -> touch_package_info@0x27C470 -> codec_package_info@0x28D998` | `path_box@0x2867F2 -> path_ble@0x2E8AB5 -> path_touch@0x2F802C -> path_codec@0x2F8040` |
| `2.0.7.16` | `box_ota_begin@0x23B3D8 -> ble_header@0x269D34 -> touch_package_info@0x27D768 -> codec_package_info@0x28EF88` | `path_box@0x287DA6 -> path_ble@0x2E9B11 -> path_touch@0x2F9078 -> path_codec@0x2F908C` |

#### Bootloader-to-Main Dependency Markers

| Version | targetRunAddr | app jump | DFU valid | path marker | All Present |
|---|---|---|---|---|---|
| `2.0.1.14` | `0x221EC` | `0x22DE4` | `0x22DC4` | `0x23124` | `True` |
| `2.0.3.20` | `0x222CC` | `0x22E9C` | `0x22E7C` | `0x231DC` | `True` |
| `2.0.5.12` | `0x223A4` | `0x22F98` | `0x22F78` | `0x232D8` | `True` |
| `2.0.6.14` | `0x223A4` | `0x22F98` | `0x22F78` | `0x232D8` | `True` |
| `2.0.7.16` | `0x223E8` | `0x22FDC` | `0x22FBC` | `0x2331C` | `True` |

---

## 3. Component Decomposition

### Cross-Version Component Fingerprints

| Component | Stable Across Versions | Size Trend (bytes by version) |
|---|---|---|
| `bootloader` | `False` | `2.0.1.14=147364, 2.0.3.20=147360, 2.0.5.12=147657, 2.0.6.14=147657, 2.0.7.16=147727` |
| `firmware_ota` | `False` | `2.0.1.14=2471336, 2.0.3.20=3069108, 2.0.5.12=3158492, 2.0.6.14=3184984, 2.0.7.16=3189184` |
| `ble` | `True` | `2.0.1.14=211948, 2.0.3.20=211948, 2.0.5.12=211948, 2.0.6.14=211948, 2.0.7.16=211948` |
| `touch` | `False` | `2.0.1.14=27808, 2.0.3.20=28192, 2.0.5.12=28320, 2.0.6.14=34080, 2.0.7.16=34080` |
| `codec` | `True` | `2.0.1.14=319372, 2.0.3.20=319372, 2.0.5.12=319372, 2.0.6.14=319372, 2.0.7.16=319372` |
| `box` | `False` | `2.0.1.14=53296, 2.0.3.20=55120, 2.0.5.12=55120, 2.0.6.14=55296, 2.0.7.16=55296` |

### Component Decomposition (Latest Version: 2.0.7.16)

| Component | Container/Format | Architecture/Runtime Hints | Evidence |
|---|---|---|---|
| `bootloader` | raw ARM image | SP=`0x2007FB00`, Reset=`0x4324CF`, stack in Cortex-M SRAM range; reset LSB=1 (Thumb entry); code address in Apollo-style execute region | `ota_s200_bootloader.bin:0x0`; `:0x223E8`; `:0x22FDC` |
| `firmware_ota` | preamble + ARM image | run_base=`0x438000`, vector@`0x20` SP=`0x2007FB00` Reset=`0x5C9777`, exec_span=`0x438000-0x74299F` | `ota_s200_firmware_ota.bin:0x14`; `:0x20`; `:0x23B3D8` |
| `BLE` (`firmware_ble_em9305.bin`) | record-based patch package | header words: version=`0x4040200`, records=`4`, erase_pages=`29`; record0 addr=`0x300000` len=`224` | `firmware_ble_em9305.bin:0x0`; `:0x10` |
| `touch` | FWPK wrapper + ARM vector | payload@`0x20` size=`34048`, vector SP=`0x20002000` Reset=`0x44D9`; stack in Cortex-M SRAM range; reset LSB=1 (Thumb entry); code address in zero-based flash map | `firmware_touch.bin:0x0`; `:0x20`; `:0x7955` |
| `codec` | FWPK dual-segment + BINH headers | seg0 off/len=`0x30`/`38236`, seg1 off/len=`0x958C`/`281088`; BINH0 stage1=`512` stage2=`12288` | `firmware_codec.bin:0x14`; `:0x24`; `:0x958C` |
| `box` | EVEN wrapper + ARM vector | payload_len_be=`0xD7E0`, checksum_be=`0x4C44DA98`, vector SP=`0x20002C88` Reset=`0x8000145`; stack in Cortex-M SRAM range; reset LSB=1 (Thumb entry); code address in STM32-style flash region | `firmware_box.bin:0x8`; `:0x20`; `:0x17A0` |

### Codec Segment-1 BINH Header Map (Stable Across All Versions)

| BINH # | Seg1 Off | Block End | +0x08 (LE) | +0x0C (LE) | +0x10 (LE) | +0x14 (LE) | +0x18 (LE) | +0x1C (LE) | Inferred Notes |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `0x0` | `0x2D970` | `0x200` | `0xADC0` | `0x3000` | `0x20000000` | `0x10000100` | `0x10000130` | `+0x0C` points to entropy jump (6.182->6.881); vector region dominated by `0x10000130` |
| 2 | `0x2D970` | `0x44A00` | `0x200` | `0x1408C` | `0x3000` | `0x20000000` | `0x10000100` | `0x10000130` | `+0x0C` points to entropy jump (6.656->7.432); vector region dominated by `0x10000130` |

BINH symbolic mapping (from v2.0.7.16 disassembly):
- `+0x08` => `stage1_size` (`0x00000200`)
- `+0x10` => `stage2_size` (`0x00003000`)

Source: `print_bootheader` (`0x0054404C`) reads `stage1_size` at `0x00544180: ldr r0, [r4, #0x8]`, `stage2_size` at `0x00544214: ldr r0, [r4, #0x10]`, `stage2_checksum` at `0x0054425E: ldr r0, [r4, #0x14]`. `download_bootimg_stage2` (`0x005449DC`) logs `"[codec.dfu]stage2_size = %u, checksum = %u"` at `0x00544A8A`.

### Boot/Update Relationships

| Relationship | Confidence | Evidence Anchors |
|---|---|---|
| `bootloader_handoff_to_main_firmware` | `confirmed` | `ota_s200_bootloader.bin:0x223E8`, `:0x22FDC`, `:0x2331C` |
| `main_firmware_orchestrates_subcomponent_updates` | `confirmed` | `ota_s200_firmware_ota.bin:0x28EF88`, `:0x27D768`, `:0x269D34`, `:0x23B3D8` |
| `subcomponents_use_distinct_update_formats` | `confirmed` | `firmware_touch.bin:0x0`, `firmware_codec.bin:0x0`, `firmware_box.bin:0x0`, `firmware_ble_em9305.bin:0x0` |
| `codec_update_uses_two_stage_boot_then_flash` | `confirmed` | `firmware_codec.bin:0x958C`, `ota_s200_firmware_ota.bin:0x2F908C` |
| `box_update_appears_bank_switched` | `likely` | `firmware_box.bin:0x17A0`, `firmware_box.bin:0x37E4` |

### Bootloader VTOR Write + App Jump (Instruction-Level Proof)

Assumption: bootloader runtime address = `0x00410000 + file_offset`.

- Handoff thunk at file offset `0x1DBDC` (`0x0042DBDC`):
  - `movw r1, #0xED08`
  - `movt r1, #0xE000`
  - `str r0, [r1]` (`SCB->VTOR = targetRunAddr`)
  - `ldr.w sp, [r0]` (`MSP = *(targetRunAddr + 0)`)
  - `ldr r1, [r0, #4]` (`entry = *(targetRunAddr + 4)`)
  - `bx r1`
- Upstream xrefs/logs proving `r0` is boot metadata run target:
  - `0x0042DF6E` references `"bootMetadataInfo.targetRunAddr = 0x%x(0x%x)"`
  - `0x0042DFBC` references `"APP jumpaddr app(0x%x) = 0x%x"`
  - `0x0042DF5E..0x0042DF88` normalizes run base to `0x00438000`.

---

## 4. Per-Version Analysis

### Component Fingerprints by Version

| Version | Component | Size | SHA-256 | Magic (hex) | Inferred Format |
|---|---|---:|---|---|---|
| `2.0.1.14` | `firmware_ble_em9305.bin` | 211948 | `91a38f7fc05555f86181ecb22b363e3239bfcaaa2ff6171e98524ae64821eca9` | `00020404703b0300` | Opaque binary blob |
| `2.0.1.14` | `firmware_box.bin` | 53296 | `7b3db020c80cd08fcdaaa2c21f7120dd56c5a74ab3704bd8b82db15aab73b188` | `4556454e01022800` | EVEN wrapper |
| `2.0.1.14` | `firmware_codec.bin` | 319372 | `1c1462aff542d41429203e3a5d4cd53696f973133203cc44b9ae01523a551d03` | `4657504b00020000` | FWPK wrapper |
| `2.0.1.14` | `firmware_touch.bin` | 27808 | `010ec2ef22742933c4539984170165777c95af9b8779305d8334c4fc9febb276` | `4657504b08000002` | FWPK wrapper |
| `2.0.1.14` | `ota_s200_bootloader.bin` | 147364 | `9379233bb7a9278da9dabfd9171ec1849554337d2bb9e81bcb72bc16422afaf6` | `00fb0720d3224300` | ARM image (vector-table start) |
| `2.0.1.14` | `ota_s200_firmware_ota.bin` | 2471336 | `ad951aec8e4140392c12715d2d1f8d575c8e288ab35331a635e2277cfb2b56fc` | `a8b52504c9cec6bd` | Opaque binary blob |
| `2.0.3.20` | `firmware_ble_em9305.bin` | 211948 | `91a38f7fc05555f86181ecb22b363e3239bfcaaa2ff6171e98524ae64821eca9` | `00020404703b0300` | Opaque binary blob |
| `2.0.3.20` | `firmware_box.bin` | 55120 | `fe0b3af4eb3c2b0a4981b9e1b09d622df3c6ad21944146e95dcef2bc598d5798` | `4556454e01023300` | EVEN wrapper |
| `2.0.3.20` | `firmware_codec.bin` | 319372 | `1c1462aff542d41429203e3a5d4cd53696f973133203cc44b9ae01523a551d03` | `4657504b00020000` | FWPK wrapper |
| `2.0.3.20` | `firmware_touch.bin` | 28192 | `e945a79dbb073a329dd16f3a0c4c052e4ec6a805acd6a4ecf7a1e02260978483` | `4657504b01030002` | FWPK wrapper |
| `2.0.3.20` | `ota_s200_bootloader.bin` | 147360 | `fd6cbe7045eaeb0e4a0ada33ccbc12ec6c7b6f006198ca93e1ee56645389d1b6` | `00fb0720b3234300` | ARM image (vector-table start) |
| `2.0.3.20` | `ota_s200_firmware_ota.bin` | 3069108 | `5cd7785bb232c298d66c0655c1236c8b8924419bdd61b9b35cf0ff04bd18ff4c` | `b4d42e049873360d` | Opaque binary blob |
| `2.0.5.12` | `firmware_ble_em9305.bin` | 211948 | `91a38f7fc05555f86181ecb22b363e3239bfcaaa2ff6171e98524ae64821eca9` | `00020404703b0300` | Opaque binary blob |
| `2.0.5.12` | `firmware_box.bin` | 55120 | `fe0b3af4eb3c2b0a4981b9e1b09d622df3c6ad21944146e95dcef2bc598d5798` | `4556454e01023300` | EVEN wrapper |
| `2.0.5.12` | `firmware_codec.bin` | 319372 | `1c1462aff542d41429203e3a5d4cd53696f973133203cc44b9ae01523a551d03` | `4657504b00020000` | FWPK wrapper |
| `2.0.5.12` | `firmware_touch.bin` | 28320 | `1587b63096a165be9a63b20e92680c705b050a797abb7d5a73d8ba28f902804d` | `4657504b07050002` | FWPK wrapper |
| `2.0.5.12` | `ota_s200_bootloader.bin` | 147657 | `c51dd99f5ff183afd32bfaab9cf04833b5b8f137a29f3706eb6b35649c7d29d4` | `00fb07208b244300` | ARM image (vector-table start) |
| `2.0.5.12` | `ota_s200_firmware_ota.bin` | 3158492 | `dfc0d525940547abb9645d60e1862c8b7e969af0794c851d0b6d1c69c3142c55` | `dc31300448c0e9bd` | Opaque binary blob |
| `2.0.6.14` | `firmware_ble_em9305.bin` | 211948 | `91a38f7fc05555f86181ecb22b363e3239bfcaaa2ff6171e98524ae64821eca9` | `00020404703b0300` | Opaque binary blob |
| `2.0.6.14` | `firmware_box.bin` | 55296 | `d290f2b6899e69288b2b07b2d52471f193a4bf065f3eefe664c5a89aeadecb52` | `4556454e01023600` | EVEN wrapper |
| `2.0.6.14` | `firmware_codec.bin` | 319372 | `1c1462aff542d41429203e3a5d4cd53696f973133203cc44b9ae01523a551d03` | `4657504b00020000` | FWPK wrapper |
| `2.0.6.14` | `firmware_touch.bin` | 34080 | `35c49f3040fd75e251a2957d746f6ebc7c8a8401741f4d2ca8c33bffb3e0b823` | `4657504b00060002` | FWPK wrapper |
| `2.0.6.14` | `ota_s200_bootloader.bin` | 147657 | `9c3c33b5632d0b3d074ae257ff5a31109d73e7330e833d9894b6598ebe2ba42f` | `00fb07208b244300` | ARM image (vector-table start) |
| `2.0.6.14` | `ota_s200_firmware_ota.bin` | 3184984 | `e295640f17a9a6c48734960f003ab663cf34b6835b212afa042db3c5703f5462` | `589930044694a833` | Opaque binary blob |
| `2.0.7.16` | `firmware_ble_em9305.bin` | 211948 | `91a38f7fc05555f86181ecb22b363e3239bfcaaa2ff6171e98524ae64821eca9` | `00020404703b0300` | Opaque binary blob |
| `2.0.7.16` | `firmware_box.bin` | 55296 | `d290f2b6899e69288b2b07b2d52471f193a4bf065f3eefe664c5a89aeadecb52` | `4556454e01023600` | EVEN wrapper |
| `2.0.7.16` | `firmware_codec.bin` | 319372 | `1c1462aff542d41429203e3a5d4cd53696f973133203cc44b9ae01523a551d03` | `4657504b00020000` | FWPK wrapper |
| `2.0.7.16` | `firmware_touch.bin` | 34080 | `35c49f3040fd75e251a2957d746f6ebc7c8a8401741f4d2ca8c33bffb3e0b823` | `4657504b00060002` | FWPK wrapper |
| `2.0.7.16` | `ota_s200_bootloader.bin` | 147727 | `5a5eb1d24160161e3fe5a020becd1c36ac68a59bdf27b491f47842555762d139` | `00fb0720cf244300` | ARM image (vector-table start) |
| `2.0.7.16` | `ota_s200_firmware_ota.bin` | 3189184 | `50f48eae3e031885086fa85d5e6f36d3d36582674adf5c6ec1d50da502f029eb` | `c0a930043f38a27b` | Opaque binary blob |
| `2.0.7.16` | `s200_firmware_raw.bin` | 3189152 | `3bd6e092fb5b3aa6dc35a15a9e380fd7663f97816c630f02fabab58994db1fb4` | `00fb072077975c00` | ARM image (vector-table start) |

### Per-Version Extracted Component Inventory

#### v2.0.1.14

| File | Size | MD5 | SHA-256 | Entropy | Magic (hex) | Magic (ascii) |
|---|---:|---|---|---:|---|---|
| `firmware_ble_em9305.bin` | 211948 | `af598d1e9a6dab7a3145d92a1f1bd2c5` | `91a38f7fc05555f86181ecb22b363e3239bfcaaa2ff6171e98524ae64821eca9` | 7.0698 | `00020404703b0300` | `....p;..` |
| `firmware_box.bin` | 53296 | `0fbef647d6e038ae7df8006e20dc4c72` | `7b3db020c80cd08fcdaaa2c21f7120dd56c5a74ab3704bd8b82db15aab73b188` | 6.8143 | `4556454e01022800` | `EVEN..(.` |
| `firmware_codec.bin` | 319372 | `3222dabe822aa388223171e2fb8802de` | `1c1462aff542d41429203e3a5d4cd53696f973133203cc44b9ae01523a551d03` | 7.0690 | `4657504b00020000` | `FWPK....` |
| `firmware_touch.bin` | 27808 | `5dd3e1ffe7f7d6bcccba6dadcb5fb760` | `010ec2ef22742933c4539984170165777c95af9b8779305d8334c4fc9febb276` | 6.7240 | `4657504b08000002` | `FWPK....` |
| `ota_s200_bootloader.bin` | 147364 | `27bf123ec85142df2cff9f1ad3f4304b` | `9379233bb7a9278da9dabfd9171ec1849554337d2bb9e81bcb72bc16422afaf6` | 6.7789 | `00fb0720d3224300` | `... ."C.` |
| `ota_s200_firmware_ota.bin` | 2471336 | `492b253103fc75c6924f1212907eb80b` | `ad951aec8e4140392c12715d2d1f8d575c8e288ab35331a635e2277cfb2b56fc` | 6.2257 | `a8b52504c9cec6bd` | `..%.....` |

- Package size: 3232068 bytes. EVENOTA: 6 entries, contiguous, exact EOF closure.
- Bootloader: SP=`0x2007FB00`, Reset=`0x004322D3`. Handlers span `0x0041676F-0x004322F1`. VTOR tuple at offset `0x222E4`.
- App: run_base=`0x438000`, Reset=`0x00573ABB`, exec_span=`0x00438000-0x00693587`.
- Box: payload_len=`0xD010`, checksum=`0xA1D50BFE`.
- OTA preamble CRC32: `0xBDC6CEC9`.

#### v2.0.3.20

| File | Size | MD5 | SHA-256 | Entropy | Magic (hex) | Magic (ascii) |
|---|---:|---|---|---:|---|---|
| `firmware_ble_em9305.bin` | 211948 | `af598d1e9a6dab7a3145d92a1f1bd2c5` | `91a38f7fc05555f86181ecb22b363e3239bfcaaa2ff6171e98524ae64821eca9` | 7.0698 | `00020404703b0300` | `....p;..` |
| `firmware_box.bin` | 55120 | `e0e603f6fdab0890c4f2927153d17de9` | `fe0b3af4eb3c2b0a4981b9e1b09d622df3c6ad21944146e95dcef2bc598d5798` | 6.8028 | `4556454e01023300` | `EVEN..3.` |
| `firmware_codec.bin` | 319372 | `3222dabe822aa388223171e2fb8802de` | `1c1462aff542d41429203e3a5d4cd53696f973133203cc44b9ae01523a551d03` | 7.0690 | `4657504b00020000` | `FWPK....` |
| `firmware_touch.bin` | 28192 | `db30bd024b53e9fde12b98f4c040d2c7` | `e945a79dbb073a329dd16f3a0c4c052e4ec6a805acd6a4ecf7a1e02260978483` | 6.7128 | `4657504b01030002` | `FWPK....` |
| `ota_s200_bootloader.bin` | 147360 | `5c27456156b48797e71b734cd3aab285` | `fd6cbe7045eaeb0e4a0ada33ccbc12ec6c7b6f006198ca93e1ee56645389d1b6` | 6.7775 | `00fb0720b3234300` | `... .#C.` |
| `ota_s200_firmware_ota.bin` | 3069108 | `037a5d03a23c9b896eddb5342cb8b073` | `5cd7785bb232c298d66c0655c1236c8b8924419bdd61b9b35cf0ff04bd18ff4c` | 6.3414 | `b4d42e049873360d` | `.....s6.` |

- Package size: 3832044 bytes. EVENOTA: 6 entries, contiguous, exact EOF closure.
- Bootloader: SP=`0x2007FB00`, Reset=`0x004323B3`. Handlers span `0x0041601F-0x004323D1`. VTOR tuple at offset `0x223C4`.
- App: run_base=`0x438000`, Reset=`0x005B6E5B`, exec_span=`0x00438000-0x00725493`.
- Box: payload_len=`0xD730`, checksum=`0x7054D5D8`.
- OTA preamble CRC32: `0x0D367398`.

#### v2.0.5.12

| File | Size | MD5 | SHA-256 | Entropy | Magic (hex) | Magic (ascii) |
|---|---:|---|---|---:|---|---|
| `firmware_ble_em9305.bin` | 211948 | `af598d1e9a6dab7a3145d92a1f1bd2c5` | `91a38f7fc05555f86181ecb22b363e3239bfcaaa2ff6171e98524ae64821eca9` | 7.0698 | `00020404703b0300` | `....p;..` |
| `firmware_box.bin` | 55120 | `e0e603f6fdab0890c4f2927153d17de9` | `fe0b3af4eb3c2b0a4981b9e1b09d622df3c6ad21944146e95dcef2bc598d5798` | 6.8028 | `4556454e01023300` | `EVEN..3.` |
| `firmware_codec.bin` | 319372 | `3222dabe822aa388223171e2fb8802de` | `1c1462aff542d41429203e3a5d4cd53696f973133203cc44b9ae01523a551d03` | 7.0690 | `4657504b00020000` | `FWPK....` |
| `firmware_touch.bin` | 28320 | `4201469bc765f0e095c4d14c4f84a4f3` | `1587b63096a165be9a63b20e92680c705b050a797abb7d5a73d8ba28f902804d` | 6.7180 | `4657504b07050002` | `FWPK....` |
| `ota_s200_bootloader.bin` | 147657 | `acf53a36afb6219a97b96701d2290d8e` | `c51dd99f5ff183afd32bfaab9cf04833b5b8f137a29f3706eb6b35649c7d29d4` | 6.7803 | `00fb07208b244300` | `... .$C.` |
| `ota_s200_firmware_ota.bin` | 3158492 | `13335651e5d77230df1594e4101cc637` | `dfc0d525940547abb9645d60e1862c8b7e969af0794c851d0b6d1c69c3142c55` | 6.3638 | `dc31300448c0e9bd` | `.10.H...` |

- Package size: 3921853 bytes. EVENOTA: 6 entries, contiguous, exact EOF closure.
- Bootloader: SP=`0x2007FB00`, Reset=`0x0043248B`. Handlers span `0x00416027-0x004324A9`. VTOR tuple at offset `0x2249C`.
- App: run_base=`0x438000`, Reset=`0x005C219B`, exec_span=`0x00438000-0x0073B1BB`.
- Box: payload_len=`0xD730`, checksum=`0x7054D5D8`.
- OTA preamble CRC32: `0xBDE9C048`.

#### v2.0.6.14

| File | Size | MD5 | SHA-256 | Entropy | Magic (hex) | Magic (ascii) |
|---|---:|---|---|---:|---|---|
| `firmware_ble_em9305.bin` | 211948 | `af598d1e9a6dab7a3145d92a1f1bd2c5` | `91a38f7fc05555f86181ecb22b363e3239bfcaaa2ff6171e98524ae64821eca9` | 7.0698 | `00020404703b0300` | `....p;..` |
| `firmware_box.bin` | 55296 | `4bd641a15114943b35724a212a8408a9` | `d290f2b6899e69288b2b07b2d52471f193a4bf065f3eefe664c5a89aeadecb52` | 6.8091 | `4556454e01023600` | `EVEN..6.` |
| `firmware_codec.bin` | 319372 | `3222dabe822aa388223171e2fb8802de` | `1c1462aff542d41429203e3a5d4cd53696f973133203cc44b9ae01523a551d03` | 7.0690 | `4657504b00020000` | `FWPK....` |
| `firmware_touch.bin` | 34080 | `34a7ce2f99241b8e61db4e76b413a09f` | `35c49f3040fd75e251a2957d746f6ebc7c8a8401741f4d2ca8c33bffb3e0b823` | 6.7568 | `4657504b00060002` | `FWPK....` |
| `ota_s200_bootloader.bin` | 147657 | `f48d8ba8e28e25d2f1a1e6786cdfc444` | `9c3c33b5632d0b3d074ae257ff5a31109d73e7330e833d9894b6598ebe2ba42f` | 6.7803 | `00fb07208b244300` | `... .$C.` |
| `ota_s200_firmware_ota.bin` | 3184984 | `3e8fb39564d53a7ec50cdfb9d029a58c` | `e295640f17a9a6c48734960f003ab663cf34b6835b212afa042db3c5703f5462` | 6.3990 | `589930044694a833` | `X.0.F..3` |

- Package size: 3954281 bytes. EVENOTA: 6 entries, contiguous, exact EOF closure.
- Bootloader: SP=`0x2007FB00`, Reset=`0x0043248B`. Handlers span `0x00416027-0x004324A9`. VTOR tuple at offset `0x2249C`.
- App: run_base=`0x438000`, Reset=`0x005C903F`, exec_span=`0x00438000-0x00741937`.
- Box: payload_len=`0xD7E0`, checksum=`0x4C44DA98`.
- OTA preamble CRC32: `0x33A89446`.

#### v2.0.7.16

| File | Size | MD5 | SHA-256 | Entropy | Magic (hex) | Magic (ascii) |
|---|---:|---|---|---:|---|---|
| `firmware_ble_em9305.bin` | 211948 | `af598d1e9a6dab7a3145d92a1f1bd2c5` | `91a38f7fc05555f86181ecb22b363e3239bfcaaa2ff6171e98524ae64821eca9` | 7.0698 | `00020404703b0300` | `....p;..` |
| `firmware_box.bin` | 55296 | `4bd641a15114943b35724a212a8408a9` | `d290f2b6899e69288b2b07b2d52471f193a4bf065f3eefe664c5a89aeadecb52` | 6.8091 | `4556454e01023600` | `EVEN..6.` |
| `firmware_codec.bin` | 319372 | `3222dabe822aa388223171e2fb8802de` | `1c1462aff542d41429203e3a5d4cd53696f973133203cc44b9ae01523a551d03` | 7.0690 | `4657504b00020000` | `FWPK....` |
| `firmware_touch.bin` | 34080 | `34a7ce2f99241b8e61db4e76b413a09f` | `35c49f3040fd75e251a2957d746f6ebc7c8a8401741f4d2ca8c33bffb3e0b823` | 6.7568 | `4657504b00060002` | `FWPK....` |
| `ota_s200_bootloader.bin` | 147727 | `d45c5c3ca6d1d6bbfb7e4dfb28cde9c0` | `5a5eb1d24160161e3fe5a020becd1c36ac68a59bdf27b491f47842555762d139` | 6.7806 | `00fb0720cf244300` | `... .$C.` |
| `ota_s200_firmware_ota.bin` | 3189184 | `bea21ef8c130eaad9ab04497e56a0863` | `50f48eae3e031885086fa85d5e6f36d3d36582674adf5c6ec1d50da502f029eb` | 6.3995 | `c0a930043f38a27b` | `..0.?8.{` |
| `s200_firmware_raw.bin` | 3189152 | `03cb1675b3bcd43110344ad26fe66a7b` | `3bd6e092fb5b3aa6dc35a15a9e380fd7663f97816c630f02fabab58994db1fb4` | 6.3996 | `00fb072077975c00` | `... w.\.` |

- Package size: 3958551 bytes. EVENOTA: 6 entries, contiguous, exact EOF closure.
- Bootloader: SP=`0x2007FB00`, Reset=`0x004324CF`. Handlers span `0x00416027-0x004324ED`. VTOR tuple at offset `0x224E0`.
- App: run_base=`0x438000`, Reset=`0x005C9777`, exec_span=`0x00438000-0x0074299F`.
- Box: payload_len=`0xD7E0`, checksum=`0x4C44DA98`.
- OTA preamble CRC32: `0x7BA2383F`.

### Per-Version EVENOTA TOC/Sub-Header Checksum Proof

All versions validated with algorithm: CRC32C (Castagnoli), non-reflected/MSB-first, `poly=0x1EDC6F41`, `init=0x00000000`, `xorout=0x00000000`, coverage=`entry_payload = bytes[sub+0x80 : sub+size]`.

**v2.0.1.14**

| ID | Filename | TOC chk | Sub chk | crc32c_msb(payload) | Match |
|---:|---|---|---|---|---|
| 1 | `firmware/codec.bin` | `0xED6AD847` | `0xED6AD847` | `0xED6AD847` | `True` |
| 2 | `firmware/ble_em9305.bin` | `0xC074BAF7` | `0xC074BAF7` | `0xC074BAF7` | `True` |
| 3 | `firmware/touch.bin` | `0xB270E42D` | `0xB270E42D` | `0xB270E42D` | `True` |
| 4 | `firmware/box.bin` | `0x980E79E5` | `0x980E79E5` | `0x980E79E5` | `True` |
| 5 | `ota/s200_bootloader.bin` | `0x4F17170A` | `0x4F17170A` | `0x4F17170A` | `True` |
| 6 | `ota/s200_firmware_ota.bin` | `0x6445DC3F` | `0x6445DC3F` | `0x6445DC3F` | `True` |

**v2.0.3.20**

| ID | Filename | TOC chk | Sub chk | crc32c_msb(payload) | Match |
|---:|---|---|---|---|---|
| 1 | `firmware/codec.bin` | `0xED6AD847` | `0xED6AD847` | `0xED6AD847` | `True` |
| 2 | `firmware/ble_em9305.bin` | `0xC074BAF7` | `0xC074BAF7` | `0xC074BAF7` | `True` |
| 3 | `firmware/touch.bin` | `0xBD834F67` | `0xBD834F67` | `0xBD834F67` | `True` |
| 4 | `firmware/box.bin` | `0xB9D4D4A3` | `0xB9D4D4A3` | `0xB9D4D4A3` | `True` |
| 5 | `ota/s200_bootloader.bin` | `0xD31CE1EA` | `0xD31CE1EA` | `0xD31CE1EA` | `True` |
| 6 | `ota/s200_firmware_ota.bin` | `0x4DD85AB3` | `0x4DD85AB3` | `0x4DD85AB3` | `True` |

**v2.0.5.12**

| ID | Filename | TOC chk | Sub chk | crc32c_msb(payload) | Match |
|---:|---|---|---|---|---|
| 1 | `firmware/codec.bin` | `0xED6AD847` | `0xED6AD847` | `0xED6AD847` | `True` |
| 2 | `firmware/ble_em9305.bin` | `0xC074BAF7` | `0xC074BAF7` | `0xC074BAF7` | `True` |
| 3 | `firmware/touch.bin` | `0x7D5A89E9` | `0x7D5A89E9` | `0x7D5A89E9` | `True` |
| 4 | `firmware/box.bin` | `0xB9D4D4A3` | `0xB9D4D4A3` | `0xB9D4D4A3` | `True` |
| 5 | `ota/s200_bootloader.bin` | `0x1DD577BA` | `0x1DD577BA` | `0x1DD577BA` | `True` |
| 6 | `ota/s200_firmware_ota.bin` | `0x3BB98935` | `0x3BB98935` | `0x3BB98935` | `True` |

**v2.0.6.14**

| ID | Filename | TOC chk | Sub chk | crc32c_msb(payload) | Match |
|---:|---|---|---|---|---|
| 1 | `firmware/codec.bin` | `0xED6AD847` | `0xED6AD847` | `0xED6AD847` | `True` |
| 2 | `firmware/ble_em9305.bin` | `0xC074BAF7` | `0xC074BAF7` | `0xC074BAF7` | `True` |
| 3 | `firmware/touch.bin` | `0x419965B4` | `0x419965B4` | `0x419965B4` | `True` |
| 4 | `firmware/box.bin` | `0xF0C5546F` | `0xF0C5546F` | `0xF0C5546F` | `True` |
| 5 | `ota/s200_bootloader.bin` | `0x714713A7` | `0x714713A7` | `0x714713A7` | `True` |
| 6 | `ota/s200_firmware_ota.bin` | `0x12588627` | `0x12588627` | `0x12588627` | `True` |

**v2.0.7.16**

| ID | Filename | TOC chk | Sub chk | crc32c_msb(payload) | Match |
|---:|---|---|---|---|---|
| 1 | `firmware/codec.bin` | `0xED6AD847` | `0xED6AD847` | `0xED6AD847` | `True` |
| 2 | `firmware/ble_em9305.bin` | `0xC074BAF7` | `0xC074BAF7` | `0xC074BAF7` | `True` |
| 3 | `firmware/touch.bin` | `0x419965B4` | `0x419965B4` | `0x419965B4` | `True` |
| 4 | `firmware/box.bin` | `0xF0C5546F` | `0xF0C5546F` | `0xF0C5546F` | `True` |
| 5 | `ota/s200_bootloader.bin` | `0xBB434910` | `0xBB434910` | `0xBB434910` | `True` |
| 6 | `ota/s200_firmware_ota.bin` | `0xCC6CF1D8` | `0xCC6CF1D8` | `0xCC6CF1D8` | `True` |

### Per-Version EVENOTA Layout Summary

| Version | ID | Type | Filename | Offset | Size | End | Payload Size | TOC chk | Sub chk |
|---|---:|---:|---|---:|---:|---:|---:|---|---|
| **2.0.1.14** | 1 | 4 | `firmware/codec.bin` | `0xB0` | `0x4E00C` | `0x4E0BC` | `0x4DF8C` | `0xED6AD847` | `0xED6AD847` |
| | 2 | 5 | `firmware/ble_em9305.bin` | `0x4E0BC` | `0x33C6C` | `0x81D28` | `0x33BEC` | `0xC074BAF7` | `0xC074BAF7` |
| | 3 | 3 | `firmware/touch.bin` | `0x81D28` | `0x6D20` | `0x88A48` | `0x6CA0` | `0xB270E42D` | `0xB270E42D` |
| | 4 | 6 | `firmware/box.bin` | `0x88A48` | `0xD0B0` | `0x95AF8` | `0xD030` | `0x980E79E5` | `0x980E79E5` |
| | 5 | 1 | `ota/s200_bootloader.bin` | `0x95AF8` | `0x24024` | `0xB9B1C` | `0x23FA4` | `0x4F17170A` | `0x4F17170A` |
| | 6 | 0 | `ota/s200_firmware_ota.bin` | `0xB9B1C` | `0x25B628` | `0x315144` | `0x25B5A8` | `0x6445DC3F` | `0x6445DC3F` |
| **2.0.3.20** | 1 | 4 | `firmware/codec.bin` | `0xB0` | `0x4E00C` | `0x4E0BC` | `0x4DF8C` | `0xED6AD847` | `0xED6AD847` |
| | 2 | 5 | `firmware/ble_em9305.bin` | `0x4E0BC` | `0x33C6C` | `0x81D28` | `0x33BEC` | `0xC074BAF7` | `0xC074BAF7` |
| | 3 | 3 | `firmware/touch.bin` | `0x81D28` | `0x6EA0` | `0x88BC8` | `0x6E20` | `0xBD834F67` | `0xBD834F67` |
| | 4 | 6 | `firmware/box.bin` | `0x88BC8` | `0xD7D0` | `0x96398` | `0xD750` | `0xB9D4D4A3` | `0xB9D4D4A3` |
| | 5 | 1 | `ota/s200_bootloader.bin` | `0x96398` | `0x24020` | `0xBA3B8` | `0x23FA0` | `0xD31CE1EA` | `0xD31CE1EA` |
| | 6 | 0 | `ota/s200_firmware_ota.bin` | `0xBA3B8` | `0x2ED534` | `0x3A78EC` | `0x2ED4B4` | `0x4DD85AB3` | `0x4DD85AB3` |
| **2.0.5.12** | 1 | 4 | `firmware/codec.bin` | `0xB0` | `0x4E00C` | `0x4E0BC` | `0x4DF8C` | `0xED6AD847` | `0xED6AD847` |
| | 2 | 5 | `firmware/ble_em9305.bin` | `0x4E0BC` | `0x33C6C` | `0x81D28` | `0x33BEC` | `0xC074BAF7` | `0xC074BAF7` |
| | 3 | 3 | `firmware/touch.bin` | `0x81D28` | `0x6F20` | `0x88C48` | `0x6EA0` | `0x7D5A89E9` | `0x7D5A89E9` |
| | 4 | 6 | `firmware/box.bin` | `0x88C48` | `0xD7D0` | `0x96418` | `0xD750` | `0xB9D4D4A3` | `0xB9D4D4A3` |
| | 5 | 1 | `ota/s200_bootloader.bin` | `0x96418` | `0x24149` | `0xBA561` | `0x240C9` | `0x1DD577BA` | `0x1DD577BA` |
| | 6 | 0 | `ota/s200_firmware_ota.bin` | `0xBA561` | `0x30325C` | `0x3BD7BD` | `0x3031DC` | `0x3BB98935` | `0x3BB98935` |
| **2.0.6.14** | 1 | 4 | `firmware/codec.bin` | `0xB0` | `0x4E00C` | `0x4E0BC` | `0x4DF8C` | `0xED6AD847` | `0xED6AD847` |
| | 2 | 5 | `firmware/ble_em9305.bin` | `0x4E0BC` | `0x33C6C` | `0x81D28` | `0x33BEC` | `0xC074BAF7` | `0xC074BAF7` |
| | 3 | 3 | `firmware/touch.bin` | `0x81D28` | `0x85A0` | `0x8A2C8` | `0x8520` | `0x419965B4` | `0x419965B4` |
| | 4 | 6 | `firmware/box.bin` | `0x8A2C8` | `0xD880` | `0x97B48` | `0xD800` | `0xF0C5546F` | `0xF0C5546F` |
| | 5 | 1 | `ota/s200_bootloader.bin` | `0x97B48` | `0x24149` | `0xBBC91` | `0x240C9` | `0x714713A7` | `0x714713A7` |
| | 6 | 0 | `ota/s200_firmware_ota.bin` | `0xBBC91` | `0x3099D8` | `0x3C5669` | `0x309958` | `0x12588627` | `0x12588627` |
| **2.0.7.16** | 1 | 4 | `firmware/codec.bin` | `0xB0` | `0x4E00C` | `0x4E0BC` | `0x4DF8C` | `0xED6AD847` | `0xED6AD847` |
| | 2 | 5 | `firmware/ble_em9305.bin` | `0x4E0BC` | `0x33C6C` | `0x81D28` | `0x33BEC` | `0xC074BAF7` | `0xC074BAF7` |
| | 3 | 3 | `firmware/touch.bin` | `0x81D28` | `0x85A0` | `0x8A2C8` | `0x8520` | `0x419965B4` | `0x419965B4` |
| | 4 | 6 | `firmware/box.bin` | `0x8A2C8` | `0xD880` | `0x97B48` | `0xD800` | `0xF0C5546F` | `0xF0C5546F` |
| | 5 | 1 | `ota/s200_bootloader.bin` | `0x97B48` | `0x2418F` | `0xBBCD7` | `0x2410F` | `0xBB434910` | `0xBB434910` |
| | 6 | 0 | `ota/s200_firmware_ota.bin` | `0xBBCD7` | `0x30AA40` | `0x3C6717` | `0x30A9C0` | `0xCC6CF1D8` | `0xCC6CF1D8` |

---

## 5. Key Cross-Version Findings

### Confirmed

- EVENOTA integrity is confirmed across all sampled versions: CRC32C (Castagnoli, MSB-first, poly=0x1EDC6F41) over entry payload range [entry+0x80, entry+size).
- Touch FWPK checksum is confirmed: reflected CRC32C over [payload_offset, payload_offset+payload_size).
- Codec FWPK segment checksums are confirmed: CRC32 over each segment range declared by offset/size fields.
- Box EVEN wrapper checksum is confirmed: big-endian additive 32-bit word sum over [0x20, 0x20+payload_length).
- Main OTA preamble checksum is confirmed: little-endian CRC32 over bytes [0x08, EOF).
- EVENOTA packaging order is stable across sampled versions: type order [4, 5, 3, 6, 1, 0] (codec, BLE, touch, box, bootloader, main OTA).
- Bootloader-to-main-firmware dependency is confirmed via boot markers referencing target run address, app jump, DFU-valid event, and ota/s200_firmware_ota.bin path.
- `firmware_ble_em9305.bin` and `firmware_codec.bin` are byte-identical across all 5 analyzed versions (hash/size stable).
- Codec BINH header structure is stable: two BINH blocks at same offsets with stable key fields (`+0x08=0x200`, `+0x10=0x3000`).
- Cross-version rule `crc32c_msb(payload) == toc_chk == sub_chk` holds for all 30 entries (6 per version x 5 versions).
- Box wrapper rule `sum_be32(payload) == box[0x0C:0x10]_be` holds for all 5 versions.

### Likely

- Handler string offset order suggests a likely internal update orchestration sequence: box -> BLE -> touch -> codec within main OTA code paths.

### Unknown / Hypotheses

- Runtime sequencing policy (including retries, rollback gating, and whether all components are always updated) is not statically proven from container metadata alone.
- FWPK non-checksum header semantics (for example word at +0x04 and firmware_count policy) remain unresolved.
- No unresolved checksum algorithm gaps remain for the target wrappers EVENOTA/FWPK/EVEN in this corpus; unresolved items are behavioral policy semantics.

---

## Reproduction Commands

- `python3 tools/build_firmware_corpus_baseline.py --output-md ... --output-json ...`
- `python3 tools/validate_evenota_headers.py --output-md ... --output-json ...`
- `python3 tools/analyze_integrity_packaging.py --output-md ... --output-json ...`
- `python3 tools/analyze_firmware_components.py --output-md ... --output-json ...`
- Per-version analysis scripts generated individual version reports.
