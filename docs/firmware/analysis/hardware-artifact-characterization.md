# Hardware Artifact Characterization

All conclusions are derived from local extracted firmware only (`captures/firmware/versions/*/extracted` and `captures/firmware/g2_extracted`). Method: static byte/ASCII/hash extraction; no API/CDN/network evidence.

---

## 1. BLE Artifact Extraction

### Method and Scope

- Inputs: `ota_s200_firmware_ota.bin` and `firmware_ble_em9305.bin` from all 5 extracted versions.
- Target artifacts: embedded BLE UUIDs, state/stack markers, transport framing clues, AT command surface.

### Version Inputs

| Version | Build Date | Build Time | Package | Extracted Dir |
|---|---|---|---|---|
| `2.0.1.14` | `2025-12-11` | `09:55:57` | `captures/firmware/versions/v2.0.1.14/09fe9c0df7b14385c023bc35a364b3a9.bin` | `captures/firmware/versions/v2.0.1.14/extracted` |
| `2.0.3.20` | `2025-12-31` | `16:36:51` | `captures/firmware/versions/v2.0.3.20/57201a6e7cd6dadeee1bdb8f6ed98606.bin` | `captures/firmware/versions/v2.0.3.20/extracted` |
| `2.0.5.12` | `2026-01-17` | `17:12:17` | `captures/firmware/versions/v2.0.5.12/53486f03b825cb22d13e769187b46656.bin` | `captures/firmware/versions/v2.0.5.12/extracted` |
| `2.0.6.14` | `2026-01-29` | `18:32:57` | `captures/firmware/versions/v2.0.6.14/0c9f9ca58785547278a5103bc6ae7a09.bin` | `captures/firmware/versions/v2.0.6.14/extracted` |
| `2.0.7.16` | `2026-02-13` | `18:47:47` | `captures/firmware/g2_2.0.7.16.bin` | `captures/firmware/g2_extracted` |

### BLE UUID Artifacts (Firmware Bytes)

Primary evidence target: `ota_s200_firmware_ota.bin`.

| UUID Alias | Canonical UUID | Latest Offset | Prefix4 | Stable Across Versions |
|---|---|---|---|---|
| `g2_service_discovery_0001` | `00002760-08c2-11e1-9073-0e8ac72e0001` | `0x2FB41B` | `00042208` | `True` |
| `g2_service_discovery_0002` | `00002760-08c2-11e1-9073-0e8ac72e0002` | `0x2FB42F` | `00102408` | `True` |
| `g2_control_5401` | `00002760-08c2-11e1-9073-0e8ac72e5401` | `0x2FB3CB` | `00044208` | `True` |
| `g2_control_5402` | `00002760-08c2-11e1-9073-0e8ac72e5402` | `0x2FB3DF` | `00104408` | `True` |
| `g2_control_parent_5450` | `00002760-08c2-11e1-9073-0e8ac72e5450` | `0x3006E0` | `60270000` | `True` |
| `g2_display_6401` | `00002760-08c2-11e1-9073-0e8ac72e6401` | `0x2FB3A3` | `00046208` | `True` |
| `g2_display_6402` | `00002760-08c2-11e1-9073-0e8ac72e6402` | `0x2FB3B7` | `00106408` | `True` |
| `g2_display_parent_6450` | `00002760-08c2-11e1-9073-0e8ac72e6450` | `0x3006B0` | `60270000` | `True` |
| `g2_file_7401` | `00002760-08c2-11e1-9073-0e8ac72e7401` | `0x2FB37B` | `00048208` | `True` |
| `g2_file_7402` | `00002760-08c2-11e1-9073-0e8ac72e7402` | `0x2FB38F` | `00108408` | `True` |
| `g2_file_parent_7450` | `00002760-08c2-11e1-9073-0e8ac72e7450` | `0x300680` | `60270000` | `True` |
| `nus_service_6e400001` | `6e400001-b5a3-f393-e0a9-e50e24dcca9e` | `0x300710` | `0300406e` | `True` |
| `ring_service_bae80001` | `bae80001-4f05-4503-8e65-3af1f7329d1f` | `0x2FF380` | `4e440000` | `True` |
| `ring_char_bae80010` | `bae80010-4f05-4503-8e65-3af1f7329d1f` | `0x2FF390` | `0100e8ba` | `True` |
| `ring_char_bae80011` | `bae80011-4f05-4503-8e65-3af1f7329d1f` | `0x2FF3A0` | `1000e8ba` | `True` |

#### UUID Evidence References (latest version)

- `g2_service_discovery_0001` (`00002760-08c2-11e1-9073-0e8ac72e0001`) -> `ota_s200_firmware_ota.bin:0x2FB41B` (matched bytes `01002ec78a0e7390e111c20860270000`)
- `g2_service_discovery_0002` (`00002760-08c2-11e1-9073-0e8ac72e0002`) -> `ota_s200_firmware_ota.bin:0x2FB42F` (matched bytes `02002ec78a0e7390e111c20860270000`)
- `g2_control_5401` (`00002760-08c2-11e1-9073-0e8ac72e5401`) -> `ota_s200_firmware_ota.bin:0x2FB3CB` (matched bytes `01542ec78a0e7390e111c20860270000`)
- `g2_control_5402` (`00002760-08c2-11e1-9073-0e8ac72e5402`) -> `ota_s200_firmware_ota.bin:0x2FB3DF` (matched bytes `02542ec78a0e7390e111c20860270000`)
- `g2_control_parent_5450` (`00002760-08c2-11e1-9073-0e8ac72e5450`) -> `ota_s200_firmware_ota.bin:0x3006E0` (matched bytes `50542ec78a0e7390e111c20860270000`)
- `g2_display_6401` (`00002760-08c2-11e1-9073-0e8ac72e6401`) -> `ota_s200_firmware_ota.bin:0x2FB3A3` (matched bytes `01642ec78a0e7390e111c20860270000`)
- `g2_display_6402` (`00002760-08c2-11e1-9073-0e8ac72e6402`) -> `ota_s200_firmware_ota.bin:0x2FB3B7` (matched bytes `02642ec78a0e7390e111c20860270000`)
- `g2_display_parent_6450` (`00002760-08c2-11e1-9073-0e8ac72e6450`) -> `ota_s200_firmware_ota.bin:0x3006B0` (matched bytes `50642ec78a0e7390e111c20860270000`)
- `g2_file_7401` (`00002760-08c2-11e1-9073-0e8ac72e7401`) -> `ota_s200_firmware_ota.bin:0x2FB37B` (matched bytes `01742ec78a0e7390e111c20860270000`)
- `g2_file_7402` (`00002760-08c2-11e1-9073-0e8ac72e7402`) -> `ota_s200_firmware_ota.bin:0x2FB38F` (matched bytes `02742ec78a0e7390e111c20860270000`)
- `g2_file_parent_7450` (`00002760-08c2-11e1-9073-0e8ac72e7450`) -> `ota_s200_firmware_ota.bin:0x300680` (matched bytes `50742ec78a0e7390e111c20860270000`)
- `nus_service_6e400001` (`6e400001-b5a3-f393-e0a9-e50e24dcca9e`) -> `ota_s200_firmware_ota.bin:0x300710` (matched bytes `9ecadc240ee5a9e093f3a3b50100406e`)
- `ring_service_bae80001` (`bae80001-4f05-4503-8e65-3af1f7329d1f`) -> `ota_s200_firmware_ota.bin:0x2FF380` (matched bytes `1f9d32f7f13a658e0345054f0100e8ba`)
- `ring_char_bae80010` (`bae80010-4f05-4503-8e65-3af1f7329d1f`) -> `ota_s200_firmware_ota.bin:0x2FF390` (matched bytes `1f9d32f7f13a658e0345054f1000e8ba`)
- `ring_char_bae80011` (`bae80011-4f05-4503-8e65-3af1f7329d1f`) -> `ota_s200_firmware_ota.bin:0x2FF3A0` (matched bytes `1f9d32f7f13a658e0345054f1100e8ba`)

### BLE State/Stack Markers

| Marker Key | Latest Offset | Stable Across Versions | Matched Marker |
|---|---|---|---|
| `ble_fw_header_log` | `0x269D34` | `False` | `[srv.em9305]BLE firmware header: version=0x%08X, total_length=%d, record_count=%d, erase_pages_size=%d` |
| `service_discovery_state` | `0x268E94` | `False` | `[ble.disc][Service Discovery] SLAVE role: discState=%d, EVEN_BLE_DISC_SLAVE_ANCS_SVC=%d, phoneType=%d` |
| `ancs_handle_log` | `0x26EDE4` | `False` | `[ble.disc]ANCS Handles - NS: 0x%04x, NS_CCC: 0x%04x, CP: 0x%04x, DS: 0x%04x, DS_CCC: 0x%04x` |
| `pair_fail_state` | `0x266E9B` | `True` | `DM_SEC_PAIR_FAIL_IND: Connection %d has no valid pairing record to clear (valid=%d, keyMask=0x%02x)` |
| `encrypt_state` | `0x267A6A` | `True` | `DM_SEC_ENCRYPT_IND connId = %d encrypted PB_TxEncodeNotifySecAuth get sec auth flag will notify` |
| `master_connect_state` | `0x26A214` | `False` | `APP_MasterConnectEvent: event=0x%02X, fromRetry=%d, disconnectByLocal=%d, MConnId=%d` |
| `cordio_att_path` | `0x26F368` | `False` | `third_party\cordio\ble-host\sources\stack\att\att_main.c` |
| `cordio_dm_path` | `0x26D140` | `False` | `third_party\cordio\ble-host\sources\stack\dm\dm_conn_master.c` |

### Transport Framing Clues

| Marker Key | Latest Offset | Stable Across Versions | Inference |
|---|---|---|---|
| `codec_pack_message` | `0x23B7BC` | `True` | Framing includes cmd(16), NR(8), TYPE(8), seq(8), flags(8), length, and CRC32 fields. |
| `codec_unpack_message` | `0x23C258` | `True` | RX path uses the same structured envelope as TX path. |
| `codec_response_message` | `0x271184` | `True` | Response handling keys on command and sequence metadata. |
| `ota_crc_guard` | `0x265E88` | `False` | File-transfer packets include payload-length-indexed CRC check and explicit mismatch handling. |
| `transport_timeout` | `0x26E62B` | `True` | Timeout state tracks serviceID/syncID/pipeID tuple for retransmission or error routing. |
| `transport_overflow` | `0x26FDBE` | `True` | Chunking uses packetLen/packetNum/packetTotalNum counters and guards against aggregate overflow. |
| `conn_param_retry` | `0x26C76B` | `True` | Connection-parameter update failures trigger deferred retry policy (30s backoff). |

### BLE/Radio AT Command Surface (latest)

| Command | Offset | Context Snippet |
|---|---|---|
| `AT^BLES` | `0x264D66` | `AT^BLES [Bondable/Disbondable/DISCONN/RESET9305/HOSTRESET]:` |
| `AT^BLEMC` | `0x266A66` | `AT^BLEMC [Conn/Disc] [addr[5]:addr[4]:addr[3]:addr[2]:addr[1]:addr[0]]:` |
| `AT^BLEM` | `0x269AC4` | `AT^BLEM [Scan/DisScan/RINGSTATE]: The parameter is incorrect. Please enter the correct command %s %s` |
| `AT^BLEADV` | `0x26BA40` | `AT^BLEADV [START/STOP/STATE]: The parameter is incorrect. Please enter the correct command %s %s` |
| `AT^BLERingSend` | `0x273CA4` | `AT^BLERingSend: The parameter is incorrect. Please enter the correct command %s %s` |
| `AT^BLE_KEEPCONNECT` | `0x2A6272` | `AT^BLE_KEEPCONNECT:` |
| `AT^BLECleanBond` | `0x2B7C6A` | `AT^BLECleanBond:` |
| `AT^EM9305` | `0x2B7C9A` | `AT^EM9305:` |
| `AT^BleGetMac` | `0x2D4052` | `AT^BleGetMac:` |
| `AT^CLEANBOND` | `0x2FC750` | `AT^CLEANBOND` |
| `AT^NUS` | `0x303824` | `AT^NUS` |

### Candidate Command Families (app-facing, firmware-only inference)

| Family | Evidence Count | Confidence | Earliest Evidence |
|---|---:|---|---|
| `settings_and_device_config` | 4 | `likely` | `0x2669ED` |
| `display_navigation_evenhub` | 4 | `likely` | `0x23900D` |
| `conversate_evenai_teleprompt` | 4 | `likely` | `0x264198` |
| `file_transfer_and_ota` | 4 | `likely` | `0x26577C` |
| `ring_and_peer_sync` | 4 | `likely` | `0x2678A1` |
| `quicklist_health_translate_onboarding` | 4 | `likely` | `0x26B8E3` |

#### Family Evidence References

- `settings_and_device_config`: `ota_s200_firmware_ota.bin:0x2669ED` (pb_service_setting), `:0x26B81B` (pb_service_dev_config), `:0x2A6272` (AT^BLE_KEEPCONNECT), `:0x2D4052` (AT^BleGetMac)
- `display_navigation_evenhub`: `ota_s200_firmware_ota.bin:0x23900D` (evenhub.data_parser), `:0x2633D5` (navigation.ui), `:0x2675A1` (page_state_sync_init), `:0x2684F7` (menu page recv data from BLE)
- `conversate_evenai_teleprompt`: `ota_s200_firmware_ota.bin:0x264198` ([service.evenAI]), `:0x26B7B7` (pb_service_conversate), `:0x26B9AB` (pb_service_teleprompt), `:0x270CFF` (pb_service_even_ai)
- `file_transfer_and_ota`: `ota_s200_firmware_ota.bin:0x26577C` (pt_ota_transmit_file), `:0x26DD21` (ota.service), `:0x26FDB5` (efs.tran), `:0x270BB9` (ota.tran)
- `ring_and_peer_sync`: `ota_s200_firmware_ota.bin:0x2678A1` (task.ring), `:0x273C27` (pb_service_ring), `:0x273CA4` (AT^BLERingSend), `:0x2780B5` (ring.proto)
- `quicklist_health_translate_onboarding`: `ota_s200_firmware_ota.bin:0x26B8E3` (pb_service_onboarding), `:0x26DF93` (pb_service_quicklist), `:0x26E053` (pb_service_translate), `:0x270D5B` (pb_service_health)

### EM9305 BLE Coprocessor Header Clues

| Version | Header Version Word | Total Length | Record Count | Erase Pages | Record0 (off/len/addr) |
|---|---|---:|---:|---:|---|
| `2.0.1.14` | `0x4040200` | 211824 | 4 | 29 | `0x7C/0xE0/0x300000` |
| `2.0.3.20` | `0x4040200` | 211824 | 4 | 29 | `0x7C/0xE0/0x300000` |
| `2.0.5.12` | `0x4040200` | 211824 | 4 | 29 | `0x7C/0xE0/0x300000` |
| `2.0.6.14` | `0x4040200` | 211824 | 4 | 29 | `0x7C/0xE0/0x300000` |
| `2.0.7.16` | `0x4040200` | 211824 | 4 | 29 | `0x7C/0xE0/0x300000` |

### Confirmed vs Likely vs Unknown

**Confirmed:**
- UUID tables for G2 control/display/file services and NUS/ring-related services are embedded in main OTA firmware bytes.
- Transport log formats encode explicit command envelope fields (`cmd`, `NR`, `TYPE`, `seq`, `flags`, `length`, `crc32`).
- OTA/file transfer transport maintains per-packet counters and CRC/timeout/overflow guards.
- EM9305 payload uses a structured record table (`offset`, `length`, `target_address`) with explicit erase-page count metadata.

**Likely:**
- Firmware command families cluster around settings/dev-config, display/evenhub, conversate/evenAI/teleprompt, OTA/file, ring, and quicklist/health/translate/onboarding modules.
- BLE link management uses Cordio ATT/DM state handling plus ANCS service-discovery branches in the same application image.

**Unknown:**
- Numeric opcode-to-feature mapping for all app commands is not fully recoverable from string evidence alone.
- Runtime ACK/retry thresholds beyond explicit `30s` backoff logs remain unresolved.
- `firmware_ble_em9305.bin` contains minimal printable symbols, so on-radio command semantics inside the coprocessor patch remain opaque.

---

## 2. Hardware Subsystem Ownership Map

### Handler-to-Subsystem Ownership

| Handler | Primary Marker Offset (latest) | Stable Across Versions | Subsystem | Confidence |
|---|---|---|---|---|
| `codec_update_handler` | `0x28EF88` | `True` | `audio_codec` | `confirmed` |
| `touch_update_handler` | `0x27D768` | `True` | `touch_input` | `confirmed` |
| `ble_coprocessor_update_handler` | `0x269D34` | `True` | `ble_coprocessor` | `confirmed` |
| `box_update_handler` | `0x23B3D8` | `True` | `box_controller` | `likely` |

#### Handler Evidence

- `codec_update_handler`: OTA firmware parses codec FWPK metadata and dispatches codec update via transport/OTA services. Evidence: `ota_s200_firmware_ota.bin:0x28EF88` (codec_package_info), `:0x2F908C` (path_codec_bin), `:0x27177E` (path_transport_protocol), `:0x27CD07` (path_ota_service), `:0x273F65` (string_codec_dfu)
- `touch_update_handler`: OTA firmware validates touch package metadata and routes update through touch DFU service linked to input stack. Evidence: `ota_s200_firmware_ota.bin:0x27D768` (touch_package_info), `:0x2F9078` (path_touch_bin), `:0x282BA8` (path_service_touch_dfu), `:0x28293F` (path_service_gesture_processor)
- `ble_coprocessor_update_handler`: OTA firmware exposes explicit EM9305 header parsing and BLE profile bindings for radio coprocessor updates. Evidence: `ota_s200_firmware_ota.bin:0x269D34` (ble_firmware_header), `:0x2E9B11` (path_ble_bin), `:0x2828AD` (path_service_em9305_dfu), `:0x282147` (path_profile_gatt), `:0x282193` (path_profile_ring), `:0x2820AF` (path_profile_ancc)
- `box_update_handler`: OTA path toggles dedicated box OTA mode and bank-switch behavior for external box/glasses control firmware. Evidence: `ota_s200_firmware_ota.bin:0x23B3D8` (box_ota_begin), `:0x287DA6` (path_box_bin), `:0x2781EC` (path_service_box_detect), `firmware_box.bin:0x17A0` (box_running_bank), `firmware_box.bin:0x37E4` (box_swap_bank)

### Cross-Component Boundary Inference

| Boundary | Confidence | Evidence Anchors |
|---|---|---|
| `control_mcu -> ble_coprocessor` | `confirmed` | `ota_s200_firmware_ota.bin:0x269D34` (ble_firmware_header), `:0x2E9B11` (path_ble_bin), `:0x2828AD` (path_service_em9305_dfu), `:0x282147` (path_profile_gatt), `:0x282193` (path_profile_ring), `:0x2820AF` (path_profile_ancc), `:0x26F368` (path_cordio_att) |
| `control_mcu -> touch_input` | `confirmed` | `ota_s200_firmware_ota.bin:0x27D768` (touch_package_info), `:0x2F9078` (path_touch_bin), `:0x282BA8` (path_service_touch_dfu), `:0x28293F` (path_service_gesture_processor), `firmware_touch.bin:0x7841` (touch_fast_click_reset), `firmware_touch.bin:0x77C1` (touch_prox_baseline) |
| `control_mcu -> audio_codec` | `confirmed` | `ota_s200_firmware_ota.bin:0x28EF88` (codec_package_info), `:0x2F908C` (path_codec_bin), `:0x273F65` (string_codec_dfu), `firmware_codec.bin:0x1347B` (codec_i2s), `firmware_codec.bin:0x13450` (codec_dmic), `firmware_codec.bin:0x8110` (codec_flash_jedec) |
| `control_mcu -> display_optics` | `likely` | `ota_s200_firmware_ota.bin:0x23900D` (string_evenhub_data_parser), `:0x2633D5` (string_navigation_ui), `:0x27F6B8` (path_evenhub_common_image_container), `:0x27C608` (path_navigation_data_handler), `:0x280345` (path_displaydrv_manager), `:0x285A8C` (path_jbd_driver), `:0x2684F7` (string_menu_page) |
| `control_mcu -> box_controller` | `likely` | `ota_s200_firmware_ota.bin:0x23B3D8` (box_ota_begin), `:0x287DA6` (path_box_bin), `:0x2781EC` (path_service_box_detect), `firmware_box.bin:0x1208` (box_gls_ota_left), `firmware_box.bin:0x17A0` (box_running_bank) |

### Confidence-Tagged Hardware Behavior Map

| Subsystem | Confidence | Behavior | Evidence Anchors |
|---|---|---|---|
| `control_mcu` | `confirmed` | Apollo510b-class main firmware orchestrates OTA transport, protocol dispatch, and boot handoff to the app image. | `ota_s200_firmware_ota.bin:0x2683B8` (build_path_ap510), `ota_s200_bootloader.bin:0x223E8` (boot_target_runaddr), `:0x22FDC` (boot_app_jump), `:0x2331C` (boot_main_firmware_path), `ota_s200_firmware_ota.bin:0x27177E` (path_transport_protocol), `:0x27CD07` (path_ota_service), `:0x27CDA7` (path_ota_transport), `:0x14` (struct_run_base=0x438000), `:0x20` (struct_vector_sp=0x2007FB00), `:0x24` (struct_vector_reset=0x5C9777) |
| `ble_coprocessor` | `confirmed` | BLE subsystem combines Cordio/profile logic in main OTA with a separately packaged EM9305 record-based patch image. | `ota_s200_firmware_ota.bin:0x269D34` (ble_firmware_header), `:0x2E9B11` (path_ble_bin), `:0x2828AD` (path_service_em9305_dfu), `:0x282147` (path_profile_gatt), `:0x26F368` (path_cordio_att) |
| `touch_input` | `confirmed` | Touch firmware is isolated in its own FWPK payload and linked to gesture/reset/proximity handling paths. | `ota_s200_firmware_ota.bin:0x27D768` (touch_package_info), `:0x2F9078` (path_touch_bin), `:0x282BA8` (path_service_touch_dfu), `:0x28293F` (path_service_gesture_processor), `firmware_touch.bin:0x7955` (touch_version), `:0x7841` (touch_fast_click_reset), `:0x77C1` (touch_prox_baseline) |
| `audio_codec` | `confirmed` | Codec firmware uses a dedicated FWPK image and BINH payloads with explicit DMIC/I2S audio pipeline symbols. | `ota_s200_firmware_ota.bin:0x28EF88` (codec_package_info), `:0x2F908C` (path_codec_bin), `:0x273F65` (string_codec_dfu), `firmware_codec.bin:0x958C` (codec_binh), `:0x1347B` (codec_i2s), `:0x13450` (codec_dmic), `:0x8110` (codec_flash_jedec) |
| `display_optics` | `likely` | Display/UI rendering is mapped to EvenHub/navigation + LVGL/JBD driver paths, but optical engine specifics are not directly exposed in symbols. | `ota_s200_firmware_ota.bin:0x23900D` (string_evenhub_data_parser), `:0x2633D5` (string_navigation_ui), `:0x27F6B8` (path_evenhub_common_image_container), `:0x27C608` (path_navigation_data_handler), `:0x280345` (path_displaydrv_manager), `:0x285A8C` (path_jbd_driver) |
| `box_controller` | `likely` | Box firmware appears to manage GLS-side OTA and banked updates, indicating a separate external module boundary. | `ota_s200_firmware_ota.bin:0x23B3D8` (box_ota_begin), `:0x287DA6` (path_box_bin), `:0x2781EC` (path_service_box_detect), `firmware_box.bin:0x1208` (box_gls_ota_left), `:0x17A0` (box_running_bank), `:0x37E4` (box_swap_bank) |
| `inter_eye_or_box_link_protocol` | `unknown` | GLS_L/GLS_R coordination is visible, but physical link framing/transport semantics are not recoverable from current static strings. | `firmware_box.bin:0x1208` (box_gls_ota_left), `ota_s200_firmware_ota.bin:0x2781EC` (path_service_box_detect), `firmware_box.bin:0x17A0` (box_running_bank) |

### Structural Snapshot (latest)

| Field | Value | Evidence |
|---|---|---|
| `ota.run_base` | `0x438000` | `ota_s200_firmware_ota.bin:0x14` |
| `ota.vector_sp` | `0x2007FB00` | `ota_s200_firmware_ota.bin:0x20` |
| `ota.vector_reset` | `0x5C9777` | `ota_s200_firmware_ota.bin:0x24` |
| `em9305.record_count` | `4` | `firmware_ble_em9305.bin:0x08` |
| `em9305.erase_pages_count` | `29` | `firmware_ble_em9305.bin:0x0C` |

### Marker Stability Snapshot

| Marker Key | Stable Across Versions | Latest Offset |
|---|---|---|
| `codec_package_info` | `True` | `0x28EF88` |
| `touch_package_info` | `True` | `0x27D768` |
| `ble_firmware_header` | `True` | `0x269D34` |
| `box_ota_begin` | `True` | `0x23B3D8` |
| `path_codec_bin` | `True` | `0x2F908C` |
| `path_touch_bin` | `True` | `0x2F9078` |
| `path_ble_bin` | `True` | `0x2E9B11` |
| `path_box_bin` | `True` | `0x287DA6` |
| `path_service_em9305_dfu` | `True` | `0x2828AD` |
| `path_service_touch_dfu` | `True` | `0x282BA8` |
| `path_service_gesture_processor` | `True` | `0x28293F` |
| `path_displaydrv_manager` | `False` | `0x280345` |
| `path_jbd_driver` | `True` | `0x285A8C` |
| `path_transport_protocol` | `True` | `0x27177E` |
| `path_ota_service` | `True` | `0x27CD07` |
| `path_ota_transport` | `True` | `0x27CDA7` |

---

## 3. Cross-Version Behavior Evolution

### Marker Presence and Offset Evolution

| Marker | Subsystem | Stable Presence | Added | Removed | Shifted | First Offset | Last Offset | Net Delta |
|---|---|---|---|---|---|---|---|---|
| `ble_firmware_header` | `ble` | `True` | `0` | `0` | `4` | `0x20513C` | `0x269D34` | `0x64BF8` |
| `ble_path_service_em9305_dfu` | `ble` | `True` | `0` | `0` | `4` | `0x20CB6C` | `0x2828AD` | `0x75D41` |
| `ble_path_profile_gatt` | `ble` | `True` | `0` | `0` | `4` | `0x20C6F2` | `0x282147` | `0x75A55` |
| `ble_path_profile_ring` | `ble` | `True` | `0` | `0` | `4` | `0x20C73A` | `0x282193` | `0x75A59` |
| `ble_path_profile_ancc` | `ble` | `True` | `0` | `0` | `4` | `0x20C662` | `0x2820AF` | `0x75A4D` |
| `ble_path_transport_protocol` | `ble` | `True` | `0` | `0` | `4` | `0x2061C1` | `0x27177E` | `0x6B5BD` |
| `ble_path_ota_transport` | `ble` | `True` | `0` | `0` | `4` | `0x20A9A6` | `0x27CDA7` | `0x72401` |
| `ble_service_discovery_state` | `ble` | `False` | `1` | `0` | `3` | `-` | `0x268E94` | `-` |
| `ble_ancs_handle_log` | `ble` | `False` | `1` | `0` | `3` | `-` | `0x26EDE4` | `-` |
| `ble_master_connect_state` | `ble` | `False` | `1` | `0` | `2` | `-` | `0x26A214` | `-` |
| `ble_conn_param_retry` | `ble` | `True` | `0` | `0` | `4` | `0x206430` | `0x26C76B` | `0x6633B` |
| `ble_ota_crc_guard` | `ble` | `False` | `1` | `0` | `3` | `-` | `0x265E88` | `-` |
| `ble_path_cordio_att` | `ble` | `False` | `1` | `0` | `1` | `-` | `0x26F368` | `-` |
| `ble_path_cordio_dm` | `ble` | `False` | `1` | `0` | `2` | `-` | `0x26D140` | `-` |
| `ble_at_keepconnect` | `ble` | `True` | `0` | `0` | `4` | `0x21764E` | `0x2A6272` | `0x8EC24` |
| `ble_at_ringsend` | `ble` | `True` | `0` | `0` | `4` | `0x205D60` | `0x273CA4` | `0x6DF44` |
| `touch_package_info` | `touch` | `True` | `0` | `0` | `4` | `0x2117AC` | `0x27D768` | `0x6BFBC` |
| `touch_path_service_touch_dfu` | `touch` | `True` | `0` | `0` | `4` | `0x20CDAF` | `0x282BA8` | `0x75DF9` |
| `touch_path_service_gesture_processor` | `touch` | `True` | `0` | `0` | `4` | `0x20CBF6` | `0x28293F` | `0x75D49` |
| `touch_component_version` | `touch` | `True` | `0` | `0` | `3` | `0x6065` | `0x7955` | `0x18F0` |
| `touch_component_fast_click_reset` | `touch` | `True` | `0` | `0` | `3` | `0x5FFD` | `0x7841` | `0x1844` |
| `touch_component_prox_baseline` | `touch` | `False` | `1` | `0` | `0` | `-` | `0x77C1` | `-` |
| `codec_package_info` | `codec` | `True` | `0` | `0` | `4` | `0x21454C` | `0x28EF88` | `0x7AA3C` |
| `codec_path_codec_bin` | `codec` | `True` | `0` | `0` | `4` | `0x24BC34` | `0x2F908C` | `0xAD458` |
| `codec_string_dfu` | `codec` | `True` | `0` | `0` | `4` | `0x254634` | `0x273F65` | `0x1F931` |
| `codec_component_i2s` | `codec` | `True` | `0` | `0` | `0` | `0x49B84` | `0x49B84` | `0x0` |
| `codec_component_dmic` | `codec` | `True` | `0` | `0` | `0` | `0x13450` | `0x13450` | `0x0` |
| `codec_component_binh` | `codec` | `True` | `0` | `0` | `0` | `0x958C` | `0x958C` | `0x0` |
| `box_ota_begin` | `box` | `True` | `0` | `0` | `4` | `0x203F1C` | `0x23B3D8` | `0x374BC` |
| `box_path_box_bin` | `box` | `True` | `0` | `0` | `4` | `0x21AECA` | `0x287DA6` | `0x6CEDC` |
| `box_service_box_detect` | `box` | `True` | `0` | `0` | `4` | `0x20AE63` | `0x2781EC` | `0x6D389` |
| `box_component_gls_ota` | `box` | `True` | `0` | `0` | `2` | `0x119C` | `0x1208` | `0x6C` |
| `box_component_running_bank` | `box` | `True` | `0` | `0` | `2` | `0x171C` | `0x17A0` | `0x84` |
| `box_component_swap_bank` | `box` | `True` | `0` | `0` | `2` | `0x377C` | `0x37E4` | `0x68` |
| `display_path_displaydrv_manager` | `display` | `False` | `1` | `0` | `3` | `-` | `0x280345` | `-` |
| `display_path_jbd_driver` | `display` | `True` | `0` | `0` | `4` | `0x2132B3` | `0x285A8C` | `0x727D9` |
| `display_path_evenhub_common_image_container` | `display` | `False` | `1` | `0` | `2` | `-` | `0x27F6B8` | `-` |
| `display_path_navigation_data_handler` | `display` | `True` | `0` | `0` | `4` | `0x20C2E7` | `0x27C608` | `0x70321` |
| `display_navigation_ui` | `display` | `True` | `0` | `0` | `4` | `0x250DC4` | `0x2633D5` | `0x12611` |
| `display_evenhub_parser` | `display` | `False` | `1` | `0` | `2` | `-` | `0x23900D` | `-` |
| `display_menu_page_ble` | `display` | `False` | `1` | `0` | `1` | `-` | `0x2684F7` | `-` |

### Component Change Matrix (size/hash/marker shifts)

| Component | `2.0.1.14` | `2.0.3.20` | `2.0.5.12` | `2.0.6.14` | `2.0.7.16` | Hash Changes | Size Changes |
|---|---|---|---|---|---|---|---|
| `firmware_ble_em9305.bin` | `211948/91a38f7f` | `211948/91a38f7f` | `211948/91a38f7f` | `211948/91a38f7f` | `211948/91a38f7f` | `0` | `0` |
| `firmware_touch.bin` | `27808/010ec2ef` | `28192/e945a79d` | `28320/1587b630` | `34080/35c49f30` | `34080/35c49f30` | `3` | `3` |
| `firmware_codec.bin` | `319372/1c1462af` | `319372/1c1462af` | `319372/1c1462af` | `319372/1c1462af` | `319372/1c1462af` | `0` | `0` |
| `firmware_box.bin` | `53296/7b3db020` | `55120/fe0b3af4` | `55120/fe0b3af4` | `55296/d290f2b6` | `55296/d290f2b6` | `2` | `2` |
| `ota_s200_firmware_ota.bin` | `2471336/ad951aec` | `3069108/5cd7785b` | `3158492/dfc0d525` | `3184984/e295640f` | `3189184/50f48eae` | `4` | `4` |

| Subsystem | Component | Stable Hash | Stable Size | Marker Stable Presence | Marker Shifted | Marker Added/Removed |
|---|---|---|---|---|---|---|
| `ble` | `firmware_ble_em9305.bin` | `True` | `True` | `10/16` | `54` | `6` |
| `touch` | `firmware_touch.bin` | `False` | `False` | `5/6` | `18` | `1` |
| `codec` | `firmware_codec.bin` | `True` | `True` | `6/6` | `12` | `0` |
| `box` | `firmware_box.bin` | `False` | `False` | `6/6` | `18` | `0` |
| `display` | `ota_s200_firmware_ota.bin` | `False` | `False` | `3/7` | `20` | `4` |

### Bluetooth Compatibility / Regression Risk Notes

- **LOW** `EM9305 payload is byte-stable across analyzed versions`: `firmware_ble_em9305.bin` hash/size did not change from `2.0.1.14` to `2.0.7.16`; BLE coprocessor patch compatibility risk is low.
- **LOW** `Core BLE host/profile paths remain present in all versions`: Service/profile/transport path markers stay present across all analyzed versions; controller app command families likely remain on a stable BLE host surface.
- **MEDIUM** `BLE diagnostics/retry/guard markers appear progressively across releases`: Several BLE-facing markers are absent in early builds and present in later builds, suggesting evolving telemetry or guard paths; mixed-fleet app handling should tolerate version-specific behavior.

---

## Reproduction Commands

- `python3 tools/analyze_ble_artifacts.py --output-md ... --output-json ...`
- `python3 tools/analyze_hardware_mapping.py --output-md ... --output-json ...`
- `python3 tools/analyze_cross_version_evolution.py --output-md ... --output-json ...`
