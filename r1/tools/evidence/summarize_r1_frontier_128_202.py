#!/usr/bin/env python3
"""Pin and source-route the 63-function 128...202-byte R1 frontier.

Every remaining unclassified application function at 128 bytes or larger is
classified here from function-local evidence: exact body bytes, direct and
registered callers, shared RAM/literal structures, and pinned provider-source
correlation. Five functions have noncontiguous bodies; their recovered window
ranges are pinned exactly and the omitted remote bytes are recorded, matching
the inventory size.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from summarize_r1_gomore_call_graph import direct_thumb_branches_to


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_IMAGE = ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
LOAD_BASE = 0x00027000
EXPECTED_IMAGE_SHA256 = "0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a"


def _function(
    entry: int, size: int, ranges: tuple[tuple[int, int, str], ...],
    symbol: str, role: str, callers: tuple[tuple[int, str], ...],
    provider_family: str, source_disposition: str,
) -> dict[str, Any]:
    return {
        "entry": entry,
        "size": size,
        "inventory": "ghidra_functions_csv",
        "ranges": ranges,
        "symbol": symbol,
        "role": role,
        "callers": callers,
        "provider_family": provider_family,
        "source_disposition": source_disposition,
    }


R1_FRONTIER_128_202_PRODUCT_FUNCTIONS = (
    _function(
        0x0008B028, 202, ((0x0008B028, 0x0008B0F2, "4acb7d1b645f879364f0a622a2aa3887ec6d0223bd32dc2fce3d7435ff20d2d0"),),
        "r1_event_subscriber_multicast", "R1 per-module subscriber walk, listener invoke, and event republish",
        ((0x0003CDE6, "BL"), (0x00042906, "BL"), (0x00042918, "B.W"), (0x00042AAE, "B.W"), (0x0004A858, "BL"), (0x0004C434, "BL"), (0x0004C52A, "BL"), (0x0004C548, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0008D8FC, 202, ((0x0008D8FC, 0x0008D9C6, "dda68ce96d537f40a139557653a7c7c90c7ed366f37ec3f67deed27fa818a2e3"),),
        "r1_event_publish", "R1 private event publisher: three id windows, inline <=4-byte payload, bounded heap copy, queue handoff",
        ((0x0003D930, "B.W"), (0x00041F3E, "B.W"), (0x00046236, "BL"), (0x000462A8, "BL"), (0x00048FCC, "BL"), (0x00049156, "BL"), (0x00049A66, "BL"), (0x00049BD6, "BL"), (0x0004A326, "BL"), (0x0004A508, "BL"), (0x0004A588, "BL"), (0x0004A64C, "B.W"), (0x0004A77A, "BL"), (0x0004A84E, "BL"), (0x0004AA8C, "B.W"), (0x0004ACBE, "BL"), (0x0004AE76, "BL"), (0x0004B544, "BL"), (0x0005A9E4, "BL"), (0x0005B528, "BL"), (0x0005DFEE, "B.W"), (0x0005E1BE, "B.W"), (0x0007CA78, "B.W"), (0x00082C3E, "BL"), (0x00082C84, "BL"), (0x00082CC8, "BL"), (0x00082D0E, "BL"), (0x00082D54, "BL"), (0x00082D98, "BL"), (0x00082DB8, "B.W"), (0x00082DF2, "BL"), (0x00082E2E, "BL"), (0x00082E60, "BL"), (0x00082E94, "BL"), (0x00082EC8, "BL"), (0x00083CDE, "BL"), (0x0008404A, "BL"), (0x0008451C, "B.W"), (0x00084716, "BL"), (0x00084AD0, "BL"), (0x00084CD2, "B.W"), (0x0008A878, "BL"), (0x0008A890, "BL"), (0x0008A8A8, "BL"), (0x0008B0CA, "BL"), (0x0008BA6A, "B.W"), (0x0008DEFE, "BL"), (0x0008F7A8, "BL"), (0x000925CA, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0006C66C, 196, ((0x0006C66C, 0x0006C6A6, "680033f90b70146edc37650307ec930287bcff4aa9d316d371108ecbb232f203"),),
        "r1_user_profile_significance_check", "R1 GoMore-facing 12-byte user-profile significance thresholds and reinitialize trigger",
        ((0x00042708, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00092B98, 192, ((0x00092B98, 0x00092C58, "f14c8e1cc93651c5e8a4837cc604c524b201d6268831cd96464afc1f2c41c67f"),),
        "r1_legacy_pair_command_plan", "R1 legacy pair/connect sub-command acceptance and peer-comparison policy",
        ((0x0004E35C, "BL"), (0x00062706, "B.W"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0008D6D8, 184, ((0x0008D6D8, 0x0008D790, "5f8ccf9aba46b19945fa0295e9735b0935eef83d4a472da43564d22e1001631b"),),
        "r1_hrv_cache_future_record_guard", "R1 HRV RAM-cache future-timestamp record/day rejection policy",
        ((0x0007072C, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00083A00, 180, ((0x00083A00, 0x00083AB4, "a96960aba584e71b10d2f5f14eb2a48b5c05b2977221ca5c45fbb2c1271ab366"),),
        "r1_ack_record_remove", "R1 32-entry acknowledgement-record find and remove over table 0x20019EF4",
        ((0x00082EF0, "B.W"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x000450CC, 178, ((0x000450CC, 0x0004517E, "20d35ced5fe81e9967ec8a948a0ea8aa6ddf0f007bab039c53bab23b6a97e4f2"),),
        "r1_message_pump_task", "R1 message-pump task: queue drain, small-payload path, AT^-prefix routing",
        ((0x000921D2, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0008D538, 178, ((0x0008D538, 0x0008D5EA, "cfb71b7b2c0ee92371b61d23452b3618ebe62f26617043929e6a1f4f01e31fae"),),
        "r1_hr_cache_future_record_guard", "R1 HR RAM-cache future-timestamp record/day rejection policy",
        ((0x00070694, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0008E27C, 178, ((0x0008E27C, 0x0008E32E, "5ada8559cd5f877d362125d31c99b92948d37fa10f4348a341a35d7afafaa0d7"),),
        "r1_spo2_cache_future_record_guard", "R1 SpO2 RAM-cache future-timestamp record/day rejection policy",
        ((0x00090E3C, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0003D88C, 176, ((0x0003D88C, 0x0003D93C, "47da08214c49bac1655559c2f7f199b7ea4c0ef4a90e5cecf02ef719652478bf"),),
        "r1_battery_low_escalation", "R1 3350-mV battery-low counter, event-0x100C escalation, and wake policy",
        ((0x00032124, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0004BAD0, 176, ((0x0004BAD0, 0x0004BB80, "6dfdee0b3d81164daba3b3ca839282a41d13831b179441e082279f537ffb53ac"),),
        "r1_temp_sleep_status_plan", "R1 temperature/sleep status-change orchestration over stream register/unregister",
        ((0x0004BD58, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0005E118, 170, ((0x0005E118, 0x0005E1C2, "44f0bd5b85e647d66995f42a2e5821a6a181e1fb20d3ead9ce2b82f0c45d53f5"),),
        "r1_status_record_ring_publish", "R1 packed four-byte status record, 16-slot ring append, event-0x2003 publish",
        ((0x0005E1D8, "B.W"), (0x0005E1EA, "B.W"), (0x0005E1F6, "B.W"), (0x0009267C, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0004B348, 168, ((0x0004B348, 0x0004B3F0, "00f2e669b31ae40c4bba76d4a31721fa22fe15ceda30f1780df9fd70e964a64f"),),
        "r1_stress_mode_timer_plan", "R1 stress-mode same-check and 3600-second timing-mode timer lifecycle",
        ((0x0004B49A, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x000825C0, 166, ((0x000825C0, 0x00082666, "2cade807dac8711b9dfc5ab36c531506df0a13c88d00509faa9120e3f07d1f9e"),),
        "r1_ack_timeout_reaper", "R1 acknowledgement-table 10-second timeout sweep and record release",
        ((0x00083B60, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00083B20, 166, ((0x00083B20, 0x00083BC6, "816cdcb1a242b3294b73ed53b32ba5f5f6f2801aca351803851a1a710d5e2c9f"),),
        "r1_ack_record_register", "R1 acknowledgement-record registration with reap-and-retry on full table",
        ((0x00082F6E, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0004C5C4, 158, ((0x0004C5C4, 0x0004C60A, "288b3bddcc700da8a7927573fe463f5a8ec059bf8ca177a46042ec6696e16d6c"),),
        "r1_health_module_init", "R1 health/sensor module init: raw_hr/wearled object creation, event subscribe, 3000-ms timer",
        ((0x0004A21E, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0005C4C8, 158, ((0x0005C4C8, 0x0005C512, "bff0a2f687a0e94bd1cb09e20434e58a29fc553a1e795fdf11d3f7bdda11b9b7"),),
        "r1_device_module_init", "R1 device-module application init and temperature-hardware check bookkeeping",
        ((0x00075FA8, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00057D0C, 156, ((0x00057D0C, 0x00057DA8, "52562272d219407f75a6045e1a429c6c60787f24f2412d3277bd3ec9379fa58e"),),
        "r1_kv_flash_erase_scan", "R1 kv.bin per-page magic-word scan and erase-on-mismatch init policy",
        ((0x00094F34, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00030AC8, 154, ((0x00030AC8, 0x00030B62, "48ce5cf0dc8e7e6801c84e7290155845a1faad36eca1f904fd434e5dbb295ff6"),),
        "r1_power_clock_pof_handler", "R1 POWER_CLOCK vector POF one-shot alert: event clear, interrupt disable, single callback",
        (),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x000824A0, 152, ((0x000824A0, 0x00082538, "cf3bdfa248002d7d15d23307e44d712cce198828ec81815f23b734a36b8c2132"),),
        "r1_ack_table_clear", "R1 acknowledgement-table full clear with per-record payload release",
        ((0x00052F76, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00093514, 150, ((0x00093514, 0x000935AA, "0a1a4190cdf163c8276914157460d5809a32118a7b666cb51b4748c330915502"),),
        "r1_nfc_charge_message_send", "R1 NFC charge-task message queue send policy",
        ((0x000621EC, "BL"), (0x00062212, "BL"), (0x00062230, "BL"), (0x00062254, "BL"), (0x000934FA, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0004F3A0, 148, ((0x0004F3A0, 0x0004F434, "40ab36d63b31044ac95475509101b200019d9fa07973a8d0af950caa28a575d3"),),
        "r1_factory_read_command_plan", "R1 factory/debug formatted read command with bounded hex dump (withheld from dispatch)",
        (),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0005B0F8, 146, ((0x0005B0F8, 0x0005B18A, "b228d9b6bfa3574fe2430951f8a9cf8c4610af350ffb4ce03f3b095a46c77255"),),
        "r1_sleep_db_fal_bind", "R1 sleep.db FAL partition and flash-device binding",
        ((0x0008DD8C, "B.W"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0006BA68, 146, ((0x0006BA68, 0x0006BAFA, "d259be5b2364ced1011d094845448e6049e46742abb855d4c43b781212608f31"),),
        "r1_pkey_fal_bind", "R1 pKey.bin FAL partition and flash-device binding (payload access stays withheld)",
        ((0x0006AD8E, "BL"), (0x0006B772, "BL"), (0x0006BBBE, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00075F64, 146, ((0x00075F64, 0x00075FF6, "7e49fab8dc57d6ff08bbc624017708dd18d2b0c00e8e1e2cc45f8273b83d9700"),),
        "r1_main", "R1 application main entry: provider init chain and product startup sequencing",
        (),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0008AF8C, 146, ((0x0008AF8C, 0x0008B01E, "8a485b83574ad31fb809605f5be66fcc8abe3b2bc5984d65b3a8d2675cf325ec"),),
        "r1_event_subscribe", "R1 per-module event subscription over shared table 0x20015708",
        ((0x00048DF8, "B.W"), (0x000497AE, "BL"), (0x000497BC, "B.W"), (0x0004A5B0, "B.W"), (0x0004AADA, "BL"), (0x0004AAE8, "B.W"), (0x0004B6A2, "BL"), (0x0004B6B0, "B.W"), (0x0004C05C, "BL"), (0x0004C5F4, "BL"), (0x0004C5FE, "BL"), (0x0007010A, "BL"), (0x00070114, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x000659E8, 144, ((0x000659E8, 0x00065A78, "47846b4ebfa0561ce02ebc1af78cb4b5daee3e20e253d222369d017c1e71eea8"),),
        "r1_fw_event_loop_push", "R1 firmware event-loop queue push with drop diagnostics",
        ((0x00065BB6, "B.W"), (0x00066032, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0003ED34, 142, ((0x0003ED34, 0x0003EDC2, "6fe8dc98d1c1cd740e4589ee69a39b247230aa731556f741cc84de608dd6f3fc"),),
        "r1_ep_export_guard", "R1 ep.bin export 300-second guard timeout and deferred flush trigger",
        ((0x0005E0E0, "B.W"), (0x0005E0E6, "B.W"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00083510, 142, ((0x00083510, 0x0008359E, "8f8116e878deb163963867a43ec06aef5c17f8a49ca54bf300ef4c5975095f10"),),
        "r1_event_post_module5", "R1 typed event-0x501 post wrapper",
        ((0x0003C6F2, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0008359E, 142, ((0x0008359E, 0x0008362C, "6ccbcea6c65f7563f1118a739df4f8334f752e923c6bb1d1ffa3da458709cbc0"),),
        "r1_event_post_module1", "R1 typed event-0x101 post wrapper",
        ((0x000402A4, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0008362C, 142, ((0x0008362C, 0x000836BA, "cbfafb80efb75e0017369fd61da961ddebc332963359163c4e95ed1db58da7cb"),),
        "r1_event_post_module4", "R1 typed event-0x401 post wrapper",
        ((0x000411BE, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00083704, 142, ((0x00083704, 0x00083792, "777a56c47680536d88079b77d3c669d55a89648f48c1efc740429614a725395e"),),
        "r1_event_post_module6", "R1 typed event-0x601 post wrapper",
        ((0x0008DB80, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00083792, 142, ((0x00083792, 0x00083820, "4c987f4c826486b52520bfbc20263dfe0b7e046ac21939fef5d01532a4b49fc7"),),
        "r1_event_post_module2", "R1 typed event-0x201 post wrapper",
        ((0x0004447C, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0003EC78, 138, ((0x0003EC78, 0x0003ED02, "787987e27d5790b57579af92ecfc7e3dc441fe0af1851fbc833b8bc3f3566632"),),
        "r1_ep_export_ring_flush", "R1 ep.bin 16-slot index-ring drain to flash with dual-block toggle",
        ((0x0003EDAC, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x000499F0, 136, ((0x000499F0, 0x00049A78, "76591afd7faef04147f6d61252a59bd73225746e8286c9669df788261294144d"),),
        "r1_hr_once_result_plan", "R1 algo_hr_once result logging, event-6 publish, and stream unregister",
        (),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0004E150, 134, ((0x0004E150, 0x0004E1D6, "33647b7e811dd70f70f32d7f907e581eb530aed8427e6473965ca3b2f4e46d7e"),),
        "r1_tx_power_plan", "R1 per-link BLE TX-power policy over SD_BLE_GAP_TX_POWER_SET",
        ((0x0009205A, "BL"), (0x00092064, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0004C81C, 132, ((0x0004C81C, 0x0004C8A0, "7c4d876f9aeef3a520e560cb0834a9ec9fe6e6fe346e481560da6c73f060594f"),),
        "r1_advertising_restart", "R1 advertising stop/start wrapper over Nordic ble_advertising_start",
        ((0x000459FA, "BL"), (0x0007F5EE, "B.W"), (0x00092006, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00062388, 132, ((0x00062388, 0x000623A4, "86a27f612c87e8a96df0bac84c74f2332a867003de5d4c3f7b14411a89cd890d"), (0x000623AA, 0x00062412, "52c52124d8b41ee84299b7a4400491039b9dcafed116b241cb6894272734e7a2"),),
        "r1_legacy_subcommand_plan", "R1 legacy command sub-handler: four-way mode switch with typed responses",
        ((0x0004E3F8, "BL"), (0x00062646, "B.W"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x000826B4, 130, ((0x000826B4, 0x00082736, "167d42c6df7986cd37aca917b0a4790704c42e3a5165ee5da1bd43ae4e9fa950"),),
        "r1_proto_ble_recv_validate", "R1 channel-1 proto_ble_recv parameter and callback presence validation",
        ((0x00045128, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0008E880, 128, ((0x0008E880, 0x0008E900, "7c263841cd690826c4a737869247dcb77f7fb8661058e4c8b2b5d44c3fac8bc0"),),
        "r1_touch_long_press_clamp", "R1 touch long-press time clamp to the 100..1000-ms product range",
        ((0x00062B9C, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
)

NORDIC_FRONTIER_128_202_FUNCTIONS = (
    _function(
        0x00072A32, 156, ((0x00072A32, 0x00072ACE, "737a295c7841e11f91ca48f4bca0f9832ef384448171df7d354be98db01dc00c"),),
        "irq_handler", "Nordic nrfx_pwm.c irq_handler: SEQEND0/SEQEND1 flag-gated, LOOPSDONE default, STOPPED state/callback",
        ((0x00030CAC, "B.W"), (0x00030CBC, "B.W"), (0x00030CCC, "B.W"),),
        "nordic_nrf5_sdk_17_1_0", "use_nordic_sdk",
    ),
)

GOMORE_FRONTIER_128_202_FUNCTIONS = (
    _function(
        0x0007ED30, 190, ((0x0007ED30, 0x0007EDEE, "b1010b32a2891a0a8628844358cd2974fab4fe6d1c76baf00ba551f821b21e41"),),
        "", "GoMore sorted-sample percentile with linear interpolation",
        ((0x000688FC, "BL"), (0x00068952, "BL"),),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x00071B74, 186, ((0x00071B74, 0x00071C2E, "385e665635dd0389c6e17511326a1a0179e907ed4c0be34ba5ab3ba278983d45"),),
        "", "GoMore descriptor record initialization with float constants",
        ((0x00060CCC, "BL"),),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x000916C8, 178, ((0x000916C8, 0x0009177A, "c855da1867a64a7cab6eb9ecd32e01f47544e5f79365dbc4fa1ac39ba6fd779d"),),
        "", "GoMore mode/profile state setter over private state record",
        ((0x0004C046, "BL"), (0x0006FFB8, "BL"),),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x00059CB0, 176, ((0x00059CB0, 0x00059D60, "dd2378d04768f935ecf7a19b4eef96a54c72fdde5d255e748965d286bfac6183"),),
        "", "GoMore private seconds-to-civil-date conversion (1000/30601 month approximation)",
        ((0x00069418, "BL"), (0x0009409E, "BL"),),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x00057B38, 168, ((0x00057B38, 0x00057BE0, "79b221829340ac54cb8bc69f97c952e1dc2bf9c554c1f3f333afa749fa70b7de"),),
        "", "GoMore 16-digit model/algorithm identifier binding and compare",
        (),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x00091A60, 164, ((0x00091A60, 0x00091B04, "f91e8fbd926769fd2d75dfd24a8181dde3aec943e15f6a12fa79c2a4eca4bd17"),),
        "", "GoMore sliding-window mean over float matrix with edge clamping",
        ((0x000651B6, "BL"),),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x000949A8, 156, ((0x000949A8, 0x00094A44, "77954fec9b9d744084af97ab34cc71155677fef24796c38de9eb6137dcce48d3"),),
        "", "GoMore sample/quality statistics accumulator with running mean",
        ((0x00060D9C, "BL"),),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x0005C064, 150, ((0x0005C064, 0x0005C0FA, "c5c54653b54668da69ab4ff4748d2853ce66c22a8d595aa538d8b2ceff0b2bf5"),),
        "", "GoMore base64 block decoder for SDK authentication parsing",
        ((0x0008EB00, "BL"),),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x00056BA8, 130, ((0x00056BA8, 0x00056C2A, "5af53b02cd653ad84d450859737c53fbc7c659abc57eeadf2e18e43d14b743c7"),),
        "", "GoMore three-axis circular-buffer moving average",
        ((0x00067F90, "BL"),),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
)

GOODIX_FRONTIER_128_202_FUNCTIONS = (
    _function(
        0x000765E4, 192, ((0x000765E4, 0x000766A4, "e64443efa23f89901d2635099f4054fa87d83a495c261be5b35a5410d6ce598d"),),
        "", "Goodix half-to-float sample conversion, window scaling, and heap handoff",
        ((0x000767B4, "BL"),),
        "goodix_gh3x2x_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x00029E8C, 190, ((0x00029E8C, 0x00029F4A, "3efb27d0f55dc14a5a5e3218af44f057a8a8c06fc2dfc5ae8860a01a4d1c9b82"),),
        "", "Goodix 20-channel masked callback dispatch with per-channel state records",
        ((0x0006A328, "BL"),),
        "goodix_gh3x2x_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x00029BBC, 184, ((0x00029BBC, 0x00029C74, "375f17d6628a227612c3a54612aab85aaaede5e9bf8ae77baf163b707ce95f23"),),
        "", "Goodix 0x10-stride per-record teardown loop",
        ((0x0006CC68, "BL"),),
        "goodix_gh3x2x_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x0002AEDC, 178, ((0x0002AEDC, 0x0002AF14, "fb9465a58546b735b89354e8f05f5293426310edabefdeb6c33d56e3d34842e8"), (0x0002AF1C, 0x0002AF32, "045abe4a5127dd33668c11dcef3084d62f2b79fcb8f12e5fbecdd28ad23542e2"),),
        "", "Goodix 0x3000-windowed register write dispatcher",
        ((0x0002A8CE, "BL"), (0x0006A5A0, "B.W"),),
        "goodix_gh3x2x_candidate", "vendor_source_required_not_redistributable",
    ),
)

YHM_FRONTIER_128_202_FUNCTIONS = (
    _function(
        0x0003530C, 134, ((0x0003530C, 0x00035392, "332458ffe5ee0ca68d66a003f8252d5078c400f0b91e64f20bbc88fe55f51bd7"),),
        "", "YHM2710 chip-ID 0xA0 verification over the pinned single-wire transport",
        ((0x00035114, "BL"), (0x0004F12A, "BL"), (0x00050694, "BL"),),
        "yhmicros_yhm2710_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x00035508, 130, ((0x00035508, 0x0003558A, "63e320baf82628224a9f8170bf8fd2cde6ec222e874c203251f4d4f0fe0348a3"),),
        "", "YHM2710 8-step float ladder quantization and 3-bit register field update",
        ((0x00050750, "B.W"),),
        "yhmicros_yhm2710_candidate", "vendor_source_required_not_redistributable",
    ),
)

TIME_CALENDAR_FRONTIER_128_202_FUNCTIONS = (
    _function(
        0x0008AC28, 202, ((0x0008AC28, 0x0008ACF2, "2623a06ca72cdea62e4894bd6a6f8d9447eb5c4d51bfb92fd55385f587a68b9a"),),
        "", "time/calendar local broken-down time fill over provider thunks",
        ((0x00081898, "BL"),),
        "unknown_time_calendar_provider_candidate", "clean_room_reimplementation_owner_authorized",
    ),
)

DEVICE_REGISTRY_FRONTIER_128_202_FUNCTIONS = (
    _function(
        0x0005DB14, 158, ((0x0005DB14, 0x0005DBB2, "81a1b331bbdf6f1f38c1db1fa453025ce3bab0f17953f93f0652474b305bbb04"),),
        "", "name-keyed registry insert with 7-byte name cap and caller task handle",
        ((0x00045DC6, "BL"), (0x0004698A, "BL"), (0x00091F96, "BL"), (0x0009210E, "BL"), (0x0009219A, "BL"), (0x0009229E, "BL"), (0x00092522, "BL"), (0x000925BC, "BL"), (0x0009272A, "BL"), (0x000927EE, "BL"),),
        "unknown_generic_device_registry_candidate", "clean_room_reimplementation_owner_authorized",
    ),
    _function(
        0x000734E8, 144, ((0x000734E8, 0x00073578, "9121d4d29e7b656a978fae97935a8631cdf1a47763b744a1da2e49f70239fb3b"),),
        "", "registry module-enabled scan over seven named records (dev_info/ble_mult/health/hsync/power/nv_r1/r_size)",
        ((0x0007368A, "BL"),),
        "unknown_generic_device_registry_candidate", "clean_room_reimplementation_owner_authorized",
    ),
)

SENSOR_STREAM_FRONTIER_128_202_FUNCTIONS = (
    _function(
        0x000896F0, 200, ((0x000896F0, 0x000897B8, "51e4b5c9438f82c5d37956141643e4ff9a7188b1b4d52098adce6699fb33f152"),),
        "", "sensor-stream named 0x38-byte object create and registry insert",
        ((0x00089D90, "B.W"), (0x00089F32, "BL"), (0x00089F44, "BL"), (0x00089F56, "BL"), (0x00089F68, "BL"), (0x00089F7A, "BL"), (0x00089F8C, "BL"), (0x00089F9E, "BL"), (0x00089FB0, "BL"), (0x0008A1B4, "B.W"),),
        "unknown_sensor_stream_framework_candidate", "clean_room_reimplementation_owner_authorized",
    ),
)

QUANTIZED_RUNTIME_FRONTIER_128_202_FUNCTIONS = (
    _function(
        0x00098EDC, 164, ((0x00098EDC, 0x00098F80, "f8b319cde23a7e55fbad6f3578b24991ff36d586f4bbfb091023a589954d8ddb"),),
        "", "float elementwise tensor-add executor installed from descriptor installer 0x00074CB0",
        (),
        "unknown_shared_quantized_neural_runtime_candidate", "clean_room_reimplementation_owner_authorized",
    ),
    _function(
        0x0005D244, 152, ((0x0005D244, 0x0005D2DC, "d65d2cfefc35b9979b132595f3d4e290a17389059dd8bf9bd3d598d643055892"),),
        "", "float softmax executor (max-subtract, exp, normalize) installed from descriptor installer 0x00074CE0",
        (),
        "unknown_shared_quantized_neural_runtime_candidate", "clean_room_reimplementation_owner_authorized",
    ),
    _function(
        0x00074AAC, 146, ((0x00074AAC, 0x00074B3E, "87b0dd90844c2ed6d2df1dbe4a5aaba2de18a7d1a07ab8ab53420cb180b7d9bd"),),
        "", "0x18-byte neural-layer descriptor constructor with packed buffer-offset math",
        ((0x00028994, "BL"), (0x000289C0, "BL"), (0x00028A14, "BL"), (0x00028A40, "BL"), (0x00028A6C, "BL"), (0x00028A94, "BL"), (0x0002989A, "BL"), (0x000298C6, "BL"), (0x0002991E, "BL"), (0x00029948, "BL"), (0x0002997C, "BL"), (0x000299AC, "BL"), (0x00043A70, "BL"), (0x00043A9A, "BL"), (0x00043ACA, "BL"), (0x00043AF6, "BL"),),
        "unknown_shared_quantized_neural_runtime_candidate", "clean_room_reimplementation_owner_authorized",
    ),
)

ALL_FUNCTIONS = (
    R1_FRONTIER_128_202_PRODUCT_FUNCTIONS
    + NORDIC_FRONTIER_128_202_FUNCTIONS
    + GOMORE_FRONTIER_128_202_FUNCTIONS
    + GOODIX_FRONTIER_128_202_FUNCTIONS
    + YHM_FRONTIER_128_202_FUNCTIONS
    + TIME_CALENDAR_FRONTIER_128_202_FUNCTIONS
    + DEVICE_REGISTRY_FRONTIER_128_202_FUNCTIONS
    + SENSOR_STREAM_FRONTIER_128_202_FUNCTIONS
    + QUANTIZED_RUNTIME_FRONTIER_128_202_FUNCTIONS
)


def summarize(image_path: Path) -> dict[str, Any]:
    image = image_path.read_bytes()
    if hashlib.sha256(image).hexdigest() != EXPECTED_IMAGE_SHA256:
        raise ValueError("unexpected recovered application image")
    rows = []
    for function in ALL_FUNCTIONS:
        entry = int(function["entry"])
        pinned = 0
        for start, end, want in function["ranges"]:
            body = image[start - LOAD_BASE:end - LOAD_BASE]
            if hashlib.sha256(body).hexdigest() != want:
                raise ValueError(f"frontier range changed: 0x{start:08x}..<0x{end:08x}")
            pinned += end - start
        callers = tuple(direct_thumb_branches_to(image, LOAD_BASE, entry))
        if callers != function["callers"]:
            raise ValueError(f"frontier callers changed: 0x{entry:08x}")
        rows.append({
            **{k: v for k, v in function.items() if k != "ranges"},
            "entry": f"0x{entry:08x}",
            "pinned_bytes": pinned,
            "omitted_bytes": int(function["size"]) - pinned,
            "callers": [
                {"callsite": f"0x{callsite:08x}", "kind": kind}
                for callsite, kind in callers
            ],
        })
    return {
        "analysis": "128...202-byte ownership frontier",
        "image_sha256": EXPECTED_IMAGE_SHA256,
        "function_count": len(rows),
        "function_bytes": sum(int(row["size"]) for row in rows),
        "pinned_bytes": sum(int(row["pinned_bytes"]) for row in rows),
        "omitted_bytes": sum(int(row["omitted_bytes"]) for row in rows),
        "product_function_count": len(R1_FRONTIER_128_202_PRODUCT_FUNCTIONS),
        "nordic_function_count": len(NORDIC_FRONTIER_128_202_FUNCTIONS),
        "gomore_function_count": len(GOMORE_FRONTIER_128_202_FUNCTIONS),
        "goodix_function_count": len(GOODIX_FRONTIER_128_202_FUNCTIONS),
        "yhm_function_count": len(YHM_FRONTIER_128_202_FUNCTIONS),
        "time_calendar_function_count": len(TIME_CALENDAR_FRONTIER_128_202_FUNCTIONS),
        "device_registry_function_count": len(DEVICE_REGISTRY_FRONTIER_128_202_FUNCTIONS),
        "sensor_stream_function_count": len(SENSOR_STREAM_FRONTIER_128_202_FUNCTIONS),
        "quantized_runtime_function_count": len(QUANTIZED_RUNTIME_FRONTIER_128_202_FUNCTIONS),
        "functions": rows,
        "safety": {
            "biometric_or_health_algorithm_reimplemented": False,
            "yhm_wire_or_register_body_recreated": False,
            "unidentified_framework_recreated": False,
            "time_calendar_provider_recreated": True,
            "withheld_dispatch_surface_enabled": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    print(json.dumps(summarize(parser.parse_args().image), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
