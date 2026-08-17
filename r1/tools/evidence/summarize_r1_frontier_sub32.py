#!/usr/bin/env python3
"""Pin and source-route the 268-function sub-32-byte R1 frontier.

Assignments were produced by function-local evidence review of the committed
decompilation corpus: exact instruction-range bytes, direct and registered
callers, shared RAM/literal structures, and pinned provider-source correlation.
Noncontiguous bodies pin their recovered window ranges exactly and record the
omitted remote bytes so the inventory size still matches.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
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
    inventory: str = "ghidra_functions_csv",
    pointer_refs: tuple[int, ...] = (),
) -> dict[str, Any]:
    return {
        "entry": entry,
        "size": size,
        "inventory": inventory,
        "ranges": ranges,
        "symbol": symbol,
        "role": role,
        "callers": callers,
        "provider_family": provider_family,
        "source_disposition": source_disposition,
        "pointer_refs": pointer_refs,
    }


R1_FRONTIER_LT32_FUNCTIONS = (
    _function(
        0x000628AE, 30, ((0x000628AE, 0x000628CC, "62bf3567bbf0f1267f7aeb9f42102e738fa4b9630d90f5a05ac13750ed352120"),),
        "r1_legacy_reply_nfc_field_seen", "legacy cmd 0x54 reply: gate byte +3, append st25dvxxkc field-seen byte, bounded reply len 5",
        ((0x0004E402, "BL"), (0x000627A6, "B.W"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x000934E4, 30, ((0x000934E4, 0x00093502, "b144fa74c6a4d74970f5bf654a8ed92ef2deb2f9ec672c2f5baa0401b934036b"),),
        "r1_nfc_charge_message_type5_send", "build 0x2c message (type 5) and call r1_nfc_charge_message_send",
        (),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0009754C, 30, ((0x0009754C, 0x0009756A, "6de5081a06961cc642e7f485ee1b3463f21cff45ca76bf629fcd440a6b926a31"),),
        "r1_iqs7211e_reg56_write", "write 2-byte big-endian value to IQS7211E register 0x56 via r1_iqs7211e_register_write_port; caller r1_iqs7211e_suspend",
        ((0x0002FE06, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0005084C, 30, ((0x0005084C, 0x0005086A, "4d0ae922e703d866844f76286e086c1a46cc755fe04e58e38f3d776019bf83e5"),),
        "r1_sensor_record_write_op", "fill 12-byte op record 0x200076dc, dispatch registry slot_10",
        ((0x0006F906, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0004E48C, 30, ((0x0004E48C, 0x0004E4AA, "10d4584b6f3e05bb2a3bf8724e4c66f50751a2bc9d61c053fb65391155c66695"),),
        "r1_gap_ppcp_set_checked", "SVC 0x7a (sd_ble_gap_ppcp_set) gated by cfg byte +0xe, fatal log on error; caller r1_nordic_gap_identity_configuration",
        ((0x00066CE4, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0004C3B8, 30, ((0x0004C3B8, 0x0004C3C2, "13d1b7caedb4f38283aa87c1dafa7b74c056bafe8753776e7d6ed9b7b49f5749"),),
        "r1_handler_triple_register", "load 3 handler ptrs, tail 0x815cc triple-register; caller module init 0x4a21c",
        ((0x0004A226, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00049E00, 30, ((0x00049E00, 0x00049E1E, "7e78d7c5b3fd449bb029969b11356840eaa33df654f08a8a6b65353f2a561609"),),
        "r1_hr_session_teardown", "sensor_stream_unregister + memclr 0xd0 of HR module block 0x20006d84",
        ((0x000498B8, "BL"), (0x00049D8C, "BL"), (0x00049E34, "BL"), (0x00049E98, "BL"), (0x0004A32A, "BL"), (0x0004A398, "B.W"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00062C74, 28, ((0x00062C74, 0x00062C90, "180b296b3ff1501ba7e81e14dac23110db17e08b22b5beb88e07a430ce87a64c"),),
        "r1_legacy_reply_temperature_reduce", "legacy reply: r1_temperature_pair_reduce then bounded reply len byte*2+5",
        (),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00091270, 28, ((0x00091270, 0x0009128C, "a72ad9407c167e0e69008f3c6ffa9c7c4d9b29586de5c902fa32a81df6465f72"),),
        "r1_charge_state_byte_get", "config-byte-0x70 gate, battery refresh if 0x55, return byte 0x20016b84+0x2c (default 1)",
        ((0x0003CD34, "BL"), (0x00046272, "BL"), (0x0004627C, "BL"), (0x000462DE, "BL"), (0x000462E8, "BL"), (0x0004C438, "BL"), (0x0004C442, "BL"), (0x0004EE20, "BL"), (0x0005069E, "B.W"), (0x0005E168, "BL"), (0x00062564, "BL"), (0x00062718, "BL"), (0x000838E2, "BL"), (0x00083DE8, "BL"), (0x000913DE, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x000913DC, 28, ((0x000913DC, 0x000913F8, "917cde190d419d4791889780f602e8c2e8fd54fc05370a852437ab6c022f7b4c"),),
        "r1_charge_state_cache_update", "cache charge-state byte, evaluate YHM predicates, forward to 0x913fc; caller r1_ble_connection_control_event_consumer",
        ((0x000453E6, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0004EB60, 28, ((0x0004EB60, 0x0004EB7C, "3967b21a269dda3a85b2d8e0129fb1a9322b2b78da26f2e8bf7860ea26cf45e5"),),
        "r1_touch_pending_flag_consume", "consume flag 0x200067f8 byte; run touch power-on tail 0x46f6c+0x4ebdc",
        ((0x000466F6, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x000933DC, 28, ((0x000933DC, 0x000933F8, "d07290f443cf9735b6d318bde9083dce81c1efe8bb6c60f44c76670d29cd0e21"),),
        "r1_touch_device_id_read", "dispatch slot_10 on touch record 0x200067f8+0xc, return byte; callers touch init/irq",
        ((0x000512D4, "BL"), (0x00051370, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00082F78, 28, ((0x00082F78, 0x00082F94, "e250f6e98e95286f1fc44a1b286f66cbcbb30ac0c4397f925cc083041ad0cc3d"),),
        "r1_proto_port_state_reset", "proto port state reset: memclr 0x280, reaper schedule, ack clear",
        ((0x0009271A, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00084130, 28, ((0x00084130, 0x0008414C, "52ea047bdfeccc353015e3618e131cad41ca59b3fefddd16aa55a143a1523f16"),),
        "r1_delayed_event_restart", "r1_delayed_event_cancel + r1_delayed_event_schedule(fn 0x4d2f0, arg, 0x7800)",
        (),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0005DCB0, 28, ((0x0005DCB0, 0x0005DCCC, "90515482d1ab401834fb39a0647c6d3adebabe299132540585adbfb7824d9b2b"),),
        "r1_event_bus_lock", "lazy osMutexNew + osMutexAcquire on event-bus mutex 0x20006794; callers r1_event_subscribe/multicast",
        ((0x0008AFA0, "BL"), (0x0008B03A, "BL"), (0x0008B10A, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00048234, 28, ((0x00048234, 0x00048250, "878fd9fd6f29ef9aaec171f5d46873b1106edc2f6c22ca16a1656780c6e017f0"),),
        "r1_ack_table_lock", "lazy osMutexNew + osMutexAcquire on ack-table mutex 0x20006b88+4; r1_ack_* callers",
        ((0x000824A4, "BL"), (0x000825CA, "BL"), (0x00083034, "BL"), (0x00083A0A, "BL"), (0x00083B40, "BL"), (0x00083B64, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0004AAD0, 28, ((0x0004AAD0, 0x0004AAEC, "66feab552755994d0d81a9b7c888ee7c1b0c71dd2c99268d5c7132e002f4e4bd"),),
        "r1_module_events_subscribe_a", "r1_event_subscribe(4, cb, ctx) + (1, cb, ctx); module-init caller 0x4a21c",
        ((0x0004A230, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x000497A4, 28, ((0x000497A4, 0x000497C0, "7b64e76424668a1a91706524b4833d6043fe5e863f6b7e9a21d5fb2076542529"),),
        "r1_module_events_subscribe_b", "r1_event_subscribe(4, cb, ctx) + (1, cb, ctx); module-init caller 0x4a21c",
        ((0x0004A234, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x000493C8, 28, ((0x000493C8, 0x000493E4, "060163a60c68a6010513afebeaee74e74bb617cbeab2ddd0e63cc86e8dd28484"),),
        "r1_s_detect_stream_register", "memclr 0x30 + find-or-register sensor stream 's_detect' via 0x897e8",
        ((0x0004A222, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00073778, 28, ((0x00073778, 0x00073794, "246cd71b2c7a7ea5206a8520435a52072fa7ad73f4f88198638acd39bc9f6c71"),),
        "r1_peer_record_flag_get", "record read 0x34 via 0x73930, return bit2 of byte 0x18; caller r1_peer_manager_event_policy",
        ((0x0004CB5E, "BL"), (0x0007F3A8, "BL"), (0x0007F3C2, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x000728B4, 26, ((0x000728B4, 0x000728CE, "76fafeaf1925cb2b9f19a56e0bca277906b954e3e60b21a792032ab7264c499d"),),
        "r1_touch_model_table_get", "table lookup (param-6)&0xff into 0x20007760, base offset by model-B210A flag",
        ((0x0002F88A, "BL"), (0x00062C0C, "BL"), (0x0008E75E, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x000723EC, 26, ((0x000723EC, 0x00072406, "bc7e9e848967b935a435306aae86c111b411a48282821536234a804f976b5d9b"),),
        "r1_touch_cfg_float_set", "store 0.01f/0.013f by flag at cfg+0x7c; via touch config dispatcher 0x8ec7c",
        ((0x0008ECA2, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00072650, 26, ((0x00072650, 0x0007266A, "2e4b6f86acf3c6ab083e1ee4458e9df1e40470fe3a5c714a0c1698565e16efd9"),),
        "r1_touch_cfg_range_check", "validate value in 4..99 or 100..105; caller 0x726fa",
        ((0x00072704, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0004E9EC, 26, ((0x0004E9EC, 0x0004EA06, "13e5e860ad85d5682d9234165b831caf9c117574c73d09f0a6f69c4c59149fca"),),
        "r1_rtc_open_enable", "dispatch slot_08 then slot_18 on sys_rtc record 0x20007690; caller r1_device_module_init",
        ((0x0005C4CE, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00077220, 26, ((0x00077220, 0x0007723A, "d70e06b1b0e59ac8ae49924df51c78fd1f348b690b78b448110f2ccfb0d23ce9"),),
        "r1_pmic_event_op_dispatch", "dispatch slot_08 then slot_20 on pmic record; callers r1_pmic_charge_event_plan/charged_notification_plan",
        ((0x00047F94, "BL"), (0x00096AA4, "BL"), (0x00096C06, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0004CB08, 26, ((0x0004CB08, 0x0004CB22, "98c4860f335cdba2be53d25e21e53612ef97adaf53bdc46e789496f4c56d7696"),),
        "r1_peer_channel_count", "count halfwords != -1 at 0x200064b2+8/+0xa; caller r1_status_record_ring_publish",
        ((0x0005E158, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0007BB5C, 26, ((0x0007BB5C, 0x0007BB76, "831757f8a47e03052c3eeff73a740c9b14fc029e612d25898d429c431cbc685f"),),
        "r1_batcfg_flag1_get", "record read 4 via 0x73930, return halfword +2 != 0; caller legacy battery cmd 0x62840",
        ((0x000628A0, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00045C20, 26, ((0x00045C20, 0x00045C3A, "f2adef76ae45b3177f0c0aa7557869666eb717046d8127c070445b515993c1d7"),),
        "r1_worker_park_epilogue", "mark registry record, set module event flag, osDelay forever",
        ((0x00092152, "BL"), (0x000922E2, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00046FB8, 24, ((0x00046FB8, 0x00046FD0, "90f62ddac8a10d42e1e88614a1148115f663c5da8c4565a226fa2f1ecbb77e41"),),
        "r1_touch_device_op_unlock", "dispatch slot_08 then slot_18 on touch record 0x200067f8+8",
        ((0x0004EB9C, "BL"), (0x0004EBE6, "B.W"), (0x000512A8, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00046F9C, 24, ((0x00046F9C, 0x00046FB4, "3f64d9f511ce0dd379e0ea47fec960b4ca01382231e7137355938ebb27a30432"),),
        "r1_touch_device_op_lock1", "dispatch slot_08 then slot_18(1) on touch record 0x200067f8+8",
        ((0x0004EB98, "BL"), (0x0004EBA6, "BL"), (0x000512A4, "BL"), (0x000512B2, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00046F6C, 24, ((0x00046F6C, 0x00046F84, "a46e3be99a22150573beaa97955e469c6c07a73aed34867d2edfabb0a0d14515"),),
        "r1_touch_device_op_stop", "dispatch slot_0c then slot_20(1) on touch record 0x200067f8+0xc",
        ((0x0004EB6E, "BL"), (0x0004EB94, "BL"), (0x000512A0, "BL"), (0x000512FA, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x000500D4, 24, ((0x000500D4, 0x000500EC, "72c4a4a580b75f4bd87f8807978005f172194172626e066cf48ad672d94998ab"),),
        "r1_watchdog_handle_init", "lazy find_by_name('watchdog') then open/enable ops via 0x5010c",
        ((0x000503AE, "B.W"), (0x0006626A, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0005010C, 24, ((0x0005010C, 0x00050124, "900ad0978055d601cce241647cdb23cae6b7e4347281965f9c644d9fb265bf06"),),
        "r1_watchdog_open_enable", "dispatch slot_00 then slot_18 on watchdog record 0x20007694",
        ((0x000500E8, "B.W"), (0x0006626E, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0003D7FC, 24, ((0x0003D7FC, 0x0003D814, "219862b9dd05a4c008e3dc89fafde4bf8d5fb1bacaefeda2485b8042007cc11f"),),
        "r1_tx_callback_register", "register callback in 3-slot table 0x20006xxx+0x18 with bitmask +0x10",
        ((0x0003D7B2, "BL"), (0x0003D7BE, "B.W"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00062C48, 22, ((0x00062C48, 0x00062C5E, "6488d09beed5bb9ec4d62d1e82b5ecb1ad4fb6b1395e2869d80c7b9ea22d53b1"),),
        "r1_legacy_reply_temperature_pair", "legacy reply: 0x50d2a fills two halfwords, bounded reply len 8",
        (),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00062C5E, 22, ((0x00062C5E, 0x00062C74, "9aa6df53e73cdc40ff52e91214e32a37838fe9168e21b21ea0ae51a6c85df1c4"),),
        "r1_legacy_reply_payload_10", "legacy reply: 0x510d8 fills payload, bounded reply len 10",
        (),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00062CD0, 22, ((0x00062CD0, 0x00062CE6, "fc629110109ab12efae18ed4fb0bbc6b8db0366c5996b2c0f1149382906cbd58"),),
        "r1_legacy_reply_motion_selection", "legacy reply: r1_motion_refresh_selection byte, bounded reply len 5",
        (),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00062CE6, 22, ((0x00062CE6, 0x00062CFC, "8f4ad4d60ffbbc30ed8ef1d03b6c91effce0783d3049971b66b69dea6f9ac6af"),),
        "r1_legacy_reply_byte_503b4", "legacy reply: 0x503b4 byte, bounded reply len 5",
        (),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00062CFC, 22, ((0x00062CFC, 0x00062D12, "a09122bc52311839b513a87808ff2a51730fd1a021c26b325b7cc07f0f8551bc"),),
        "r1_legacy_reply_yhm_status", "legacy reply: 0x50690 YHM status byte, bounded reply len 5",
        (),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00062D12, 22, ((0x00062D12, 0x00062D28, "fef998968fb28d43b1159ba71c5e0896c8af8e452cd127cbe20279dfdc8b6ee8"),),
        "r1_legacy_reply_goodix_identity", "legacy reply: r1_goodix_identity_probe byte, bounded reply len 5",
        (),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00062D28, 22, ((0x00062D28, 0x00062D3E, "fadebe006cedaf5f518dca9b342328c6044c4063f1491095c847ad60e23e972f"),),
        "r1_legacy_reply_word_50e1c", "legacy reply: 0x50e1c word, bounded reply len 8",
        (),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00062D3E, 22, ((0x00062D3E, 0x00062D54, "6ddc8fdd9f0868682d0ee428277454623693751cc7b598c6493a5a6232097349"),),
        "r1_legacy_reply_touch_status", "legacy reply: 0x5128c touch-query byte, bounded reply len 5",
        (),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00062D54, 22, ((0x00062D54, 0x00062D6A, "1cb0f82e303a444ab6ec2e395c0d89d62ee0058cbda5d460769e0c73381d9c44"),),
        "r1_legacy_reply_battery_voltage", "legacy reply: 0x913c8 battery halfword, bounded reply len 6",
        (),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00072898, 22, ((0x00072898, 0x000728AE, "77b0791e67635049e647d74aac38f47fa22b43fd55915b61ffc679fc6918bf80"),),
        "r1_touch_ati_data_get", "copy bytes 0x20007750+3/+4 to out params, return 1; caller r1_ati_calibration_command_plan",
        ((0x0006226C, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0004C92C, 22, ((0x0004C92C, 0x0004C942, "e36b5c9916ffe1309ab1433435022e05c599a18f2d0958a399752b0daa43c090"),),
        "r1_dfu_buttonless_init_checked", "ble_dfu_buttonless_init with static config, fatal log on error; caller r1_nordic_ble_bootstrap_configuration",
        ((0x0004DF5A, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00041800, 22, ((0x00041800, 0x00041816, "0eb16a2a3be10b91ad69895c6e3d588f1075f656a87442c58f9dca9ef8683ce8"),),
        "r1_gap_adv_addr_get", "SVC 0x93 (sd_ble_gap_adv_addr_get) into 8-byte buffer, bool return; adv/tx-power plans",
        ((0x0004C838, "BL"), (0x0004C900, "BL"), (0x0004D118, "BL"), (0x0004E1AE, "BL"), (0x00052F8C, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00084C82, 22, ((0x00084C82, 0x00084C98, "2cc23be2f6f8b36dfc04a99498fadfcf04b56ad38d42f63317a2b71e55064f9b"),),
        "r1_ble_send_byte_type8", "r1_phone_connection_handle_get + r1_ble_thread_message_encode(8,1,&byte)",
        (),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0003DFF8, 22, ((0x0003DFF8, 0x0003E00E, "fe7c4a81c348be7dadc17e62fe4196c9f8eba6f91e6f4a10b6e63492c44ae560"),),
        "r1_ble_tx_type2_send", "r1_glasses_connection_handle_get + r1_ble_tx_queue_dispatch_type2",
        (),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0003E00E, 10, ((0x0003E00E, 0x0003E018, "b582eaabcb0251b809c850fe8eeb29230ef19c077c46ab7f7e628941bcad384a"),),
        "r1_rtt_channel0_write_callback", "registered slot-1 adapter to SEGGER_RTT_Write(0, bytes, length)",
        (), "r1_product_specific", "clean_room_behavior_only",
        "manual_provenance_supplement", (0x0003D7C4,),
    ),
    _function(
        0x0003D7AC, 22, ((0x0003D7AC, 0x0003D7C2, "cb6aa598a11abf5e38053888027372832882d2bff3a4866d12bd376adb5854ea"),),
        "r1_tx_callback_register_defaults", "register fn 0x3e00e as slot1 and r1_ble_tx_type2_send (0x3dff8) as slot2",
        ((0x0004EF9C, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0004F8BC, 22, ((0x0004F8BC, 0x0004F8D2, "2c9df36298d72adb364f33a4ce591398d0798607f8fc682818029226efa9d192"),),
        "r1_module_stream_unregister_a", "sensor_stream_unregister + clear handle 0x2000673c+4; returns 1",
        (),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0004F328, 22, ((0x0004F328, 0x0004F33E, "c13d38df9ea0e8ca6f0b9bef24e5fb749303d10f1e378253e0fabd6ee7b979de"),),
        "r1_module_stream_unregister_b", "sensor_stream_unregister + clear handle 0x2000673c+0xc; returns 1",
        (),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0004ED14, 22, ((0x0004ED14, 0x0004ED2A, "91af1ccc63e938624e57d4dee4321b74ec51b621290472f3901efa3f2b1ac16f"),),
        "r1_module_stream_unregister_c", "sensor_stream_unregister + clear handle 0x2000673c+0x10; returns 1",
        (),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0007BB04, 22, ((0x0007BB04, 0x0007BB1A, "981ef6def730c211cdd44000f9b2d48e88893023bad05ec387ffb3d41ab7ff74"),),
        "r1_batcfg_word_4c_get", "record read 0x7c via 0x73930, return word at +0x4c; iqs7211e configure + legacy cmd",
        ((0x0002F89E, "BL"), (0x00062BFC, "BL"), (0x00062C28, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x000493F8, 22, ((0x000493F8, 0x0004940E, "61bd7df43afb5e3d879bf73d16eb8391e823a9a70b8eb394f82199254afb1142"),),
        "r1_cfg_byte_get_73798", "record read via 0x73798, return byte; callers 0x48d9c init + r1_hrv_timing_start_plan",
        ((0x00048DA6, "BL"), (0x00049AF2, "BL"), (0x00049F22, "BL"), (0x0004AF26, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0004BAB4, 22, ((0x0004BAB4, 0x0004BACA, "5e782069155feedb227bbf3108e81c161a7dc06196539fe9f3466a9c3abf94fa"),),
        "r1_temperature_mode_set", "r1_temperature_mode_plan_transition + store mode byte; caller r1_temp_sleep_status_plan",
        ((0x0004239A, "B.W"), (0x0004BB26, "BL"), (0x0004BB7C, "B.W"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0004B48C, 22, ((0x0004B48C, 0x0004B4A2, "712ab98cc60e50ef89673f38f620c1309350ae3821cc4b5f478641bce01066c5"),),
        "r1_stress_mode_set", "r1_stress_mode_timer_plan + store mode byte (<2)",
        ((0x00042312, "B.W"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00062C30, 20, ((0x00062C30, 0x00062C44, "959d2de157451a8e604c8416d86e3e728e4875346b91ed676a020afae883fa67"),),
        "r1_legacy_command_subdispatch", "legacy command sub-dispatch: byte+3 < 0x48 indexes jump table 0x20006c60",
        ((0x0004E348, "BL"), (0x000626AC, "B.W"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00091290, 20, ((0x00091290, 0x000912A4, "af1f05b702fdb875a7b1db7e7f80a19be8932f9dd17ddb790da9e0d69e555046"),),
        "r1_battery_voltage_get", "config-byte-0x70 gate, battery service if 0x55, return halfword 0x20016b84+0x2a",
        ((0x0003D8FE, "BL"), (0x0004EE1A, "BL"), (0x0004F4E6, "BL"), (0x0008443A, "BL"), (0x00096AFC, "BL"), (0x00096CEE, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0006F8FA, 20, ((0x0006F8FA, 0x0006F90E, "246148278bfc7e0acd389d3cb73d9803ac1dc0bfdefc608ecc19a19c2e59073f"),),
        "r1_sensor_reg_write16", "rev16 halfword then 0x5084c record write + dispatch; returns 1",
        (),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00050F08, 20, ((0x00050F08, 0x00050F1C, "adb53b2f56d9662e925298bb520867d9605d08df1891e7e39a33e35e0124d54c"),),
        "r1_i2c2_handle_cache", "lazy device_registry_find_by_name('i2c_2') into 0x200076f8",
        ((0x000503A2, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00050DC0, 20, ((0x00050DC0, 0x00050DD4, "d27dc40fa1142ecb68823181a6d30abe15f2ff704c3483bc67fbf37446f8a526"),),
        "r1_sys_rtc_handle_cache", "lazy device_registry_find_by_name('sys_rtc') into 0x20007690",
        ((0x0005038A, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0009143C, 20, ((0x0009143C, 0x00091450, "9a5902ed270d09f78142fa1517a913c34d99c5b76e02b08a68666494cd27e626"),),
        "r1_vbat_adc_handle_cache", "lazy device_registry_find_by_name('vbat_adc') into 0x20006890+0x10",
        ((0x0005038E, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0004E9BC, 20, ((0x0004E9BC, 0x0004E9D0, "874ea87ce4c3999ce5d3c4152cab61dd68f17c6bde09aaff8ff37565ef5f4b92"),),
        "r1_peers_delete_checked", "pm_peers_delete, fatal log on error; caller r1_system_control_command_37_plan",
        ((0x00046036, "BL"), (0x0006294C, "BL"), (0x00062966, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0003E924, 20, ((0x0003E924, 0x0003E938, "02fda4209a8d8247efc86332cfe7befa4731c8a18df49b78523e6c6ec431a511"),),
        "r1_hvx_sem_try_acquire", "non-null + osSemaphoreAcquire==ok -> 1; caller r1_bae8_hvx_serialized_send_adapter",
        ((0x0003E7BE, "BL"), (0x0003E846, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00049EF4, 20, ((0x00049EF4, 0x00049F08, "d38a9ee08dd9909a6bca2e11d86b9aa5549fc22d93ebb886e39d94138cc42672"),),
        "r1_hrv_stream_release", "free stream object 0x20006d84+0x10 via 0x8a3c0, clear handle",
        ((0x000498BC, "BL"), (0x00049D90, "BL"), (0x00049E38, "BL"), (0x0004A044, "B.W"), (0x0004A332, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00049D10, 20, ((0x00049D10, 0x00049D24, "e21491d49a31ff6915233fef46075e19e167e4cf7e6e2767a295d6e51e1385b4"),),
        "r1_hr_stream_release", "free stream object 0x20006d84+0xc via 0x8a3c0, clear handle",
        ((0x000498AE, "BL"), (0x00049BEA, "B.W"), (0x00049D94, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0004B2E4, 20, ((0x0004B2E4, 0x0004B2F8, "35c5e55c917000e8e7cc40685d9dce10996d4144a47e15f35dea6a6bb5405fbe"),),
        "r1_stress_stream_release", "free stream object 0x20006d98+4 via 0x8a3c0, clear handle",
        ((0x0004AB9C, "BL"), (0x0004AD52, "BL"), (0x0004AE86, "BL"), (0x0004B328, "B.W"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00046A2C, 20, ((0x00046A2C, 0x00046A40, "26db62ab6feefb9f0425c9d3d95a23e5f1e89d065d6f1f30e9c2ed132a14b705"),),
        "r1_task_stop_66d8", "osThreadTerminate task handle 0x200066d8+8 if set, clear handle",
        (),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0004690C, 20, ((0x0004690C, 0x00046920, "cc6584db2c93d83e56ecda35f129f5718340ac2fc8e7984e7188614169aa4529"),),
        "r1_task_stop_6608", "osThreadTerminate task handle 0x20006608+8 if set, clear handle",
        (),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00045E4C, 20, ((0x00045E4C, 0x00045E60, "6c932f4178946b1324513add8b884e4d6dbf59e467ad7196c4151d1bf9e27dd7"),),
        "r1_task_stop_6540", "osThreadTerminate task handle 0x20006540+8 if set, clear handle",
        (),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00045084, 20, ((0x00045084, 0x00045098, "34438ff662ed12d0ca78eb26a7835d72996b2b9bb9172c6fa0fbc3d5bd565437"),),
        "r1_task_stop_65bc", "osThreadTerminate task handle 0x200065bc+8 if set, clear handle",
        (),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0004503C, 20, ((0x0004503C, 0x00045050, "e5a3e603f1843064c0aa2766efd1d313794e4fff58781e06b07af722bdb11097"),),
        "r1_task_stop_6590", "osThreadTerminate task handle 0x20006590+8 if set, clear handle",
        (),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00044ED8, 20, ((0x00044ED8, 0x00044EEC, "a9d62f15e23a48c67b1ded18e2ef93406ed20725c2c50cfc3a7165fead9f8483"),),
        "r1_task_stop_65e0", "osThreadTerminate task handle 0x200065e0+8 if set, clear handle",
        (),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00044EC0, 20, ((0x00044EC0, 0x00044ED4, "018e657d5961954b353155f074bb3863053ddd17f4b6828fba51c0eaa2a9d599"),),
        "r1_task_stop_6568", "osThreadTerminate task handle 0x20006568+8 if set, clear handle",
        (),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00043B74, 20, ((0x00043B74, 0x00043B88, "491a85d99384c4c6aa235c4ea7d1600574b491f4a733d827b7ebe5bbd165b092"),),
        "r1_task_stop_668c", "osThreadTerminate task handle 0x2000668c+8 if set, clear handle",
        (),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0004CB40, 20, ((0x0004CB40, 0x0004CB54, "ab673eb20c4bbc3c3df96f939dd22a14c65cd1c29ee1fd196a46b8c56872eb07"),),
        "r1_peer_channel_b_valid", "return halfword 0x200064b2+0xa != -1; caller r1_protocol_send_response",
        ((0x000828D4, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0007BB44, 20, ((0x0007BB44, 0x0007BB58, "f216d21cfe1854166cdf370747c7c4a5deee5c03b677bfcf321c113b84d21e3f"),),
        "r1_batcfg_byte0_get", "record read 4 via 0x73930, return byte 0; R1 battery curve/cadence callers",
        ((0x0003DA04, "BL"), (0x0003DA28, "BL"), (0x0004EE26, "BL"), (0x0004FEC8, "BL"), (0x0004FF40, "BL"), (0x0005000A, "BL"), (0x0006285A, "BL"), (0x0007C53C, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0007BB7C, 20, ((0x0007BB7C, 0x0007BB90, "ef1518c258fdb39bc62af7a67d94e0f2b142ef30ea6f617dbb2bffe90b38c250"),),
        "r1_batcfg_word1_signed_get", "record read 4 via 0x73930, return signed halfword +2; r1_battery_* callers",
        ((0x0003205E, "BL"), (0x0003DA56, "BL"), (0x0003DA70, "BL"), (0x00062860, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0007BAC4, 20, ((0x0007BAC4, 0x0007BAD8, "009646934829f53bf461d199a9d0436789daf623c0434ef4917fd8e9369171e9"),),
        "r1_batcfg_byte_rec8_get", "record read 1 via 0x73930 on record 0x20007df8+8; legacy battery cmd callers",
        ((0x000628DC, "BL"), (0x0006A1D0, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00033350, 20, ((0x00033350, 0x00033364, "203130db7f0d1ab5a9b75dcd842ee0a263c88ae51be2bdad4d366f9b1aecd5ba"),),
        "r1_systick_guard", "if xTaskGetSchedulerState() != taskSCHEDULER_NOT_STARTED(1) tail-call xPortSysTickHandler; no exact match in pinned SDK 17.1.0 port",
        (),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00050D2A, 18, ((0x00050D2A, 0x00050D3C, "71a08b9d39573b1e85bccea116a8d174e62b6bcda2c5a87eb503a5056a2a36b9"),),
        "r1_temperature_pair_read", "fill two halfwords from 0x50c90/0x50d00 for legacy reply 0x62c48",
        ((0x00062C4E, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00091244, 18, ((0x00091244, 0x00091256, "45eafe6ee7e80d8011186d5c79c98ad509365567f64221c5cb21d41b195d2c37"),),
        "r1_charge_state_is_full", "YHM charge-state map == 2 predicate; caller r1_device_status_handler",
        ((0x000838EE, "BL"), (0x00083DF4, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0007271C, 18, ((0x0007271C, 0x0007272E, "b026b0fa73394897a00a0dc22dcc11bd9dc0f5f27347c0e6dd8741b1e1dfaef0"),),
        "r1_touch_cfg_field_set", "store value when *p < 3 else error 0x42; via touch config dispatcher 0x8ec7c",
        ((0x0008ECC6, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00082BD4, 18, ((0x00082BD4, 0x00082BE6, "1f0181948d602c0210ecae853b284d17e6b01d0e14a901c8b6548d03d81c9dac"),),
        "r1_packet_field12_get", "return p+0xc when record type halfword +8 != 0xc; packet/ack/settings handlers",
        ((0x00083D0C, "BL"), (0x00083FC6, "BL"), (0x00084154, "BL"), (0x000842D0, "BL"), (0x000842F4, "BL"), (0x000843D0, "BL"), (0x000844B8, "BL"), (0x000844F4, "BL"), (0x000845C2, "BL"), (0x000846EE, "BL"), (0x0008487A, "BL"), (0x00084A1A, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0005D1D8, 18, ((0x0005D1D8, 0x0005D1EA, "03bce9b6efd3baf928763cb2e1c77529a6c9ef66e865647c77cdf3cc1e595317"),),
        "r1_st25_subop_d_send", "one-call wrapper 0x5d1ea(0xd, arg, 1); exclusive caller r1_st25dvxxkc_initialize_configuration",
        ((0x00077800, "BL"), (0x000778B4, "BL"), (0x00077930, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0004C634, 18, ((0x0004C634, 0x0004C646, "b83f941b580bfb639bc74629bb8c2e3bd4997b67f0d9f88ee675e132dc1f4810"),),
        "r1_health_mode_is_2", "return byte 0x2001e454+0x24 == 2; activity/hr/hrv callers",
        ((0x00048D62, "BL"), (0x00048EF0, "BL"), (0x00049084, "BL"), (0x00049A4A, "BL"), (0x00049BBA, "BL"), (0x0004A302, "BL"), (0x0004A8D2, "BL"), (0x0004AC68, "BL"), (0x0004AE20, "BL"), (0x0004B536, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0007390C, 18, ((0x0007390C, 0x0007391E, "bf9f1444dd34016093ed3685a5fcc87b1e5ef5f668a1917d4c8dedaacc57f430"),),
        "r1_health_record_write", "record write 0x18 via 0x73968; r1_health storage/sync callers",
        ((0x0003C198, "BL"), (0x0003FDAA, "BL"), (0x00040C94, "BL"), (0x00043F70, "BL"), (0x0005E71E, "BL"), (0x0005E920, "BL"), (0x0008B298, "BL"), (0x0008BB74, "BL"), (0x0008BCBC, "BL"), (0x0008C1D8, "BL"), (0x0008C320, "BL"), (0x0008C7D8, "BL"), (0x0008C920, "BL"), (0x0008CDE8, "BL"), (0x0008CF30, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x000738F4, 18, ((0x000738F4, 0x00073906, "844a6140b564d457a8d13b75dc9ec0bbd84a7c38d2408b8b9e1ce395616283e9"),),
        "r1_health_record_read", "record read 0x18 via 0x73930; r1_health storage/sync callers",
        ((0x0003C142, "BL"), (0x0003FD54, "BL"), (0x00040C3E, "BL"), (0x00043F1A, "BL"), (0x0005E708, "BL"), (0x0005E8E4, "BL"), (0x0008BAFC, "BL"), (0x0008BB6C, "BL"), (0x0008BCB4, "BL"), (0x0008C160, "BL"), (0x0008C1D0, "BL"), (0x0008C318, "BL"), (0x0008C760, "BL"), (0x0008C7D0, "BL"), (0x0008C918, "BL"), (0x0008CD70, "BL"), (0x0008CDE0, "BL"), (0x0008CF28, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x000913C8, 16, ((0x000913C8, 0x000913D8, "8827c6825d79cd852723e08c93bdede226eb210af6a7a69b4f4f85edaad44325"),),
        "r1_battery_voltage_fresh_get", "refresh battery runtime then return halfword 0x20016b84+0x2a",
        ((0x00062D58, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0006A234, 16, ((0x0006A234, 0x0006A244, "81a6f4310898aaef3c7947a254ac014f9c3dc8c922bc84859d91601a88c36775"),),
        "r1_model_dependent_limit_get", "return 0x18 if model B210A else 0x15; caller r1_iqs7211e_ati_error_audit_policy",
        ((0x00041A68, "BL"), (0x0006A042, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00072410, 16, ((0x00072410, 0x00072420, "d7f7748c1cd3bc6677608f5377773e385a978b60e418bafdd23b7a183092b49d"),),
        "r1_touch_cfg_small_set", "store value < 3 else error 0x41; via touch config dispatcher 0x8ec7c",
        ((0x0008ECBA, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00042EC4, 16, ((0x00042EC4, 0x00042ED4, "d3371cc640874974b3e8557e02c9b3bc641d258d875281d02118b315d9fec97f"),),
        "r1_charge_event_i2c_op", "YHM record op 0x507a0 then 0x507ac(param); caller r1_pmic_charge_event_plan",
        ((0x00096A98, "BL"), (0x00096C14, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x000489D6, 16, ((0x000489D6, 0x000489E6, "5089d606da503fe66b31eb97fa135817048c894d7eed0c5e05b27b41a9763874"),),
        "r1_adv_param_by_mode", "return 0xee when mode byte +0x24==1 else 0x1f; referenced by ble_advertising_init edges",
        ((0x00051794, "BL"), (0x000517B6, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00083448, 16, ((0x00083448, 0x00083458, "9e136114095bb33b317fbf2bbd9e6d0378de0b515d7793b808b2b78275c99c9d"),),
        "r1_protocol_send_callback_set", "store callback at 0x20006c20+0, 0/-1; caller proto port init 0x830a8",
        ((0x000830B4, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00092390, 16, ((0x00092390, 0x000923A0, "06cc4e8fc30b16bb72e63ab08e28908f49d5f998b31e845d6ff20df38ac7fd2f"),),
        "r1_module_thread_flags_set", "osThreadFlagsSet(0x20006540+8, arg) guarded; caller sensor_algorithm_heap_fatal_candidate",
        ((0x0009269A, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00032730, 16, ((0x00032730, 0x00032740, "4bcb8570dc269597a4079d65ef7f6363dafc881087a2f92cb72caa35d7a0ef0f"),),
        "r1_task_flag_set_1", "guarded osThreadFlagsSet(0x20006568+8, 1)",
        (),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x000499E0, 16, ((0x000499E0, 0x000499F0, "efc1ab3539a0c26f27cfa8d8856082b4d4173ba818d7a6f3a09211bcbaf5099b"),),
        "r1_hr_value_plausible", "validate byte in 40..220 (bpm); caller r1_hr_once_result_plan",
        ((0x00049A42, "BL"), (0x00049BB2, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00050690, 14, ((0x00050690, 0x0005069E, "5a3f341fc5cef399633f9fdc9cccf2967c0505c54ad77db393f6b53537ccc77e"),),
        "r1_yhm_status_byte_get", "read YHM status byte via yhm 0x3530c for legacy reply 0x62cfc; returns 1",
        ((0x00062D02, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00091256, 14, ((0x00091256, 0x00091264, "a3c6a13dd117008f28ff60e09ab5cd167379f1c8b7e5cb141b48ededbaefcd41"),),
        "r1_charge_state_is_active", "YHM charge-state map == 1 predicate; callers r1_device_status_handler + 0x913dc",
        ((0x000838E8, "BL"), (0x00083DEE, "BL"), (0x000913E8, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0004EBDC, 14, ((0x0004EBDC, 0x0004EBEA, "584f8ee5f842242cece4d950dcd76664aa195526739656ba145a331dab7614d7"),),
        "r1_touch_power_on_step", "0x50378 bus-enable + 0x46fb8 device op; callers touch task dispatcher + registration",
        ((0x0004EB76, "B.W"), (0x000512FE, "BL"), (0x0008E7C2, "B.W"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00072B9C, 14, ((0x00072B9C, 0x00072BAA, "96a9b0a89b84e4e8d403f239a82360c0c06205887bc337e0507d07b4b4cd34b3"),),
        "r1_model_b210a_check", "return 0x6a244 device-model probe == 1; used by iqs7211e configure/irq and touch calibration",
        ((0x0002F898, "BL"), (0x00030FB2, "BL"), (0x0006A236, "BL"), (0x000728BA, "BL"), (0x00093016, "BL"), (0x0009328C, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00050D3C, 14, ((0x00050D3C, 0x00050D4A, "202b173525fbaf7c656014eb6ebfbe2763093be65686329aa5044b72ae52db48"),),
        "r1_vnfc_rect_adc_handle_cache", "device_registry_find_by_name('vnfc_rect_adc') into 0x20006854; caller r1_i2c5_nfc_resource_registration",
        ((0x00050474, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0004E65E, 14, ((0x0004E65E, 0x0004E66C, "49e584c61113a7970ff9dbd87943c1743c026c312fb71a6c0d1e284aa104de4f"),),
        "r1_hvx_send_flush_100", "r1_bae8_hvx_serialized_send_adapter with timeout 100, flag 0; caller r1_output_worker",
        ((0x00044F92, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0004E650, 14, ((0x0004E650, 0x0004E65E, "1a125d32eca665f8778a4730120ca5ff6817d93cb806e49e0eb2fd8d4a104463"),),
        "r1_hvx_send_flush_200", "r1_bae8_hvx_serialized_send_adapter with timeout 200, flag 1; caller r1_output_worker",
        ((0x00044FDC, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x000827F8, 14, ((0x000827F8, 0x00082806, "603d67ee0168a2a9e5b0ff6f985126c30da3fd5ef5172c59cba80de079eb5e91"),),
        "r1_protocol_send_hook_call", "tail-call **(0x20006c20) if registered else -1; caller r1_protocol_send_response",
        ((0x000829D4, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0005DCD4, 14, ((0x0005DCD4, 0x0005DCE2, "db6d8ef83d808f6310f95ef190f16e778b9b3f3c9c723ee9a5a42b4363f0831b"),),
        "r1_event_bus_unlock", "guarded osMutexRelease on event-bus mutex 0x20006794",
        ((0x0008AFDC, "BL"), (0x0008B012, "BL"), (0x0008B0E0, "BL"), (0x0008B130, "B.W"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00048258, 14, ((0x00048258, 0x00048266, "7e9768932470b24ff6832de37ecfe133860cabdd574b2c6d9f9bb8bee6c0b891"),),
        "r1_ack_table_unlock", "guarded osMutexRelease on ack-table mutex 0x20006b88+4",
        ((0x00082534, "B.W"), (0x00082662, "B.W"), (0x00083080, "BL"), (0x0008309C, "B.W"), (0x00083AB0, "B.W"), (0x00083B56, "BL"), (0x00083B7A, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0008FE14, 14, ((0x0008FE14, 0x0008FE22, "dfc92eca25147ff525029faf8048f378c84092f05a6ee454434649d2fc9d3d15"),),
        "r1_sleep_sector_count_get", "return (record 0x200067b4+4 -> +0x38) >> 12 as byte; r1_sleep_* callers",
        ((0x0005B2FC, "BL"), (0x0005B332, "BL"), (0x0005B3B8, "BL"), (0x0008FC70, "BL"), (0x0008FCC0, "BL"), (0x0008FE2C, "BL"), (0x0009020E, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0006ABE4, 14, ((0x0006ABE4, 0x0006ABF2, "3e76e3dea882bc1d6085c026358b0dfbba73cadc1d21831d1abc0ea77ed128e6"),),
        "r1_crash_record_marker_set", "store 0x2e0 halfword, return block 0x2001e054; caller r1_health_crash_record_initializer",
        ((0x0005A2E8, "BL"), (0x0006AD6E, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00095BEC, 14, ((0x00095BEC, 0x00095BFA, "4a64099cd667f8241842b4b1be9f1778761d35be07b915b6b2d14872918d2c9e"),),
        "r1_malloc_failed_hook", "basepri 0x40 + store to 0xffffffff fatal loop; sole caller pvPortMalloc failure path",
        ((0x00085664, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00062834, 12, ((0x00062834, 0x00062840, "e76f059e9db42145fdc8ebd7962b6fe5d17950532bca04efc51339af6d7e22c3"),),
        "r1_legacy_reply_status_ff", "legacy reply: payload byte 0xff, bounded reply len 5",
        ((0x0004E3E4, "BL"), (0x0006279A, "B.W"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00072888, 12, ((0x00072888, 0x00072894, "f7723f18d0f037fe33b60e4b468002c6537e79bde4bdb3454031467d3c19e907"),),
        "r1_touch_slider_flag_get", "return byte 0x2000772c+4 != 0; caller r1_iqs7211e_touch_task_dispatcher",
        ((0x000466FA, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x000500FC, 12, ((0x000500FC, 0x00050108, "86ba0ee3f1ae60776f348d0f1690c7c38398de1cda9040db7c38c3ddd2c17423"),),
        "r1_watchdog_op_18", "dispatch slot_18 on watchdog record 0x20007694",
        ((0x00045D86, "BL"), (0x00045DA4, "BL"), (0x00045DB4, "BL"), (0x00045DBC, "BL"), (0x0006624C, "BL"), (0x00092386, "BL"), (0x00095BE8, "B.W"), (0x00096A08, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00082EE8, 12, ((0x00082EE8, 0x00082EF4, "756426a63f4921c408c57acf5259e978e62206721616e22bd40f6fc90f1a1fd2"),),
        "r1_ack_record_remove_type2", "r1_ack_record_remove(2, hi, lo, arg); callers r1_event_post_module1/2/4/5/6",
        ((0x00083590, "BL"), (0x0008361E, "BL"), (0x000836AC, "BL"), (0x00083784, "BL"), (0x00083812, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00083CF4, 12, ((0x00083CF4, 0x00083D00, "100d4d8fd8ae69784a6c53fe83bdcd55130b5cb0b39eee1da461f888586ca568"),),
        "r1_ack_reaper_arm", "r1_delayed_event_schedule(fn 0x83cd0, 0, 0x384000)",
        ((0x00082F88, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x000923A4, 12, ((0x000923A4, 0x000923B0, "09eac463364de063225c7dce1278880dfb97c8ca1a2e54581fdbee4007cc5556"),),
        "r1_module_event_flag_set", "osEventFlagsSet(0x20006540+0x1c, 1<<arg); callers worker epilogue + touch task dispatcher",
        ((0x00045C2A, "BL"), (0x0004644E, "BL"), (0x00046674, "BL"), (0x00046A06, "BL"), (0x00092078, "BL"), (0x000921E2, "BL"), (0x00092368, "BL"), (0x0009264A, "BL"), (0x000927A6, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0006A2A0, 12, ((0x0006A2A0, 0x0006A2AC, "f01aebe66a11b2574afa66bbf813335209524b88361c4f1aba7a451638ed1d31"),),
        "r1_stream_cfg_set_14", "store non-null word at cfg block 0x20007b8c+0x14; r1_sensor_stream_registration_plan",
        ((0x00089F1A, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0006A2B0, 12, ((0x0006A2B0, 0x0006A2BC, "2c4a4590ce88f18e808679d296bfc3af714d6d5bc29e8fe47a1d8231693f709c"),),
        "r1_stream_cfg_set_10", "store non-null word at cfg block 0x20007b8c+0x10; r1_sensor_stream_registration_plan",
        ((0x00089F14, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0006A2C0, 12, ((0x0006A2C0, 0x0006A2CC, "fca087b2a0bf33e92c6b74c8084718240a959382b5e2d44fe1bcbed86106b364"),),
        "r1_stream_cfg_set_18", "store non-null word at cfg block 0x20007b8c+0x18; r1_sensor_stream_registration_plan",
        ((0x00089F26, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0006A2D0, 12, ((0x0006A2D0, 0x0006A2DC, "694ebfbf730445c2111da6754fc3c9aaa986b5d72bba2969be62b777dd485291"),),
        "r1_stream_cfg_set_04", "store non-null word at cfg block 0x20007b8c+4; r1_sensor_stream_registration_plan",
        ((0x00089F08, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0006A2E0, 12, ((0x0006A2E0, 0x0006A2EC, "1494ca0fc461a21bf2e657a78ad5387cce1e3f4c6950daf24a5230610ecb0d78"),),
        "r1_stream_cfg_set_00", "store non-null word at cfg block 0x20007b8c+0; r1_sensor_stream_registration_plan",
        ((0x00089EFC, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0006A2F0, 12, ((0x0006A2F0, 0x0006A2FC, "278550d643dba7068de7655ecd03137d59936f03f92cb807d18edad0025a5983"),),
        "r1_stream_cfg_set_1c", "store non-null word at cfg block 0x20007b8c+0x1c; r1_sensor_stream_registration_plan",
        ((0x00089F20, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0006A300, 12, ((0x0006A300, 0x0006A30C, "b06ad4bcbdbbf930fe88e226fde9343cde2d31d42ee43fd3e80d226b0050d9a6"),),
        "r1_stream_cfg_set_08", "store non-null word at cfg block 0x20007b8c+8; r1_sensor_stream_registration_plan",
        ((0x00089F02, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0006A310, 12, ((0x0006A310, 0x0006A31C, "9a9f47232f82b8566889ff6d3b3d1c36f7001dd1de60f483b2f1ce72fbcf37ef"),),
        "r1_stream_cfg_set_0c", "store non-null word at cfg block 0x20007b8c+0xc; r1_sensor_stream_registration_plan",
        ((0x00089F0E, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00073688, 12, ((0x00073688, 0x00073694, "af82bebef3e2e92402f1fafa0de3873ff9fb563810886e9cb8a81d835e6cb9fa"),),
        "r1_nv_modules_idle_check", "device_registry_module_enabled_scan() ^ 1; NV commit path + r1_nv_compiled_default_restore",
        ((0x00046C46, "BL"), (0x000736FE, "BL"), (0x00073828, "BL"), (0x0007385C, "BL"), (0x0007389C, "BL"), (0x000738E4, "BL"), (0x0007BBB2, "BL"), (0x0007BBDE, "BL"), (0x0007C694, "BL"), (0x0007C8D6, "BL"), (0x0007C904, "BL"), (0x0007C92E, "BL"), (0x0007C95C, "BL"), (0x0007C99A, "BL"), (0x0007C9DC, "BL"), (0x0007CA06, "BL"), (0x0007CA38, "BL"), (0x0007CA62, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00093414, 10, ((0x00093414, 0x0009341E, "cd4e7849617e97d4dcd9de6ae97b653923009ddfefbbfc8b4bddb4fe32bdd56d"),),
        "r1_touch_ati_mode_set", "store mode byte (max 3) at 0x2000772c+5; caller r1_ati_calibration_command_plan",
        ((0x00062172, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00077240, 10, ((0x00077240, 0x0007724A, "dc4d11fa61175507bbcde2c1716a64fb01679615c1182617d7e744c749557cc6"),),
        "r1_battery_task_flags_set", "osThreadFlagsSet(0x20006630+8, arg); R1 battery/pmic callers",
        ((0x00031FF2, "BL"), (0x00032178, "BL"), (0x0003D81C, "BL"), (0x00042D2A, "B.W"), (0x00042D3A, "B.W"), (0x00042E14, "B.W"), (0x00042EE4, "B.W"), (0x00096A76, "B.W"), (0x00096C1A, "BL"), (0x00096D5C, "B.W"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0004BD54, 10, ((0x0004BD54, 0x0004BD5E, "23aae7ee73541e2446866d80e50294d9fa7538cae8827f3204b7a95f2645c3b2"),),
        "r1_temp_sleep_status_report", "r1_temp_sleep_status_plan(&stack word); caller 0x4a4b4 sleep-force-awake",
        ((0x0004A4FA, "BL"), (0x0004A63A, "BL"), (0x0004AA7A, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00031FC0, 8, ((0x00031FC0, 0x00031FC8, "9c11506343aab8dad7a0a86e17d9f6824c973de5150972a17620aa5356213da5"),),
        "r1_battery_stats_clear", "memclr 0x33 of battery stats block; caller 0x913c8",
        ((0x000913CA, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00091264, 8, ((0x00091264, 0x0009126C, "7d654d2141405875c40911f8faf013d637f3cd23337c2af97f0138c31a1e8828"),),
        "r1_device_state_byte_2d_get", "return byte 0x20016b84+0x2d; caller r1_status_record_ring_publish",
        ((0x0005E14C, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00046F90, 8, ((0x00046F90, 0x00046F98, "c274c85c1161421ba6f48eb555acc3d4b4b6e95f0695f3c5ec463be7423e7887"),),
        "r1_touch_record_op_0c", "dispatch slot_0c on touch record 0x200067f8+8",
        ((0x0004EBB0, "BL"), (0x000512BC, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00046F60, 8, ((0x00046F60, 0x00046F68, "70436a6ca7bb66fe126e3f9a2e54df1a34054239d8110caa83f0e58718d98a9d"),),
        "r1_touch_record_op_08", "dispatch slot_08 on touch record 0x200067f8+4; heavy use by r1_iqs7211e_touch_task_dispatcher",
        ((0x0004FA94, "BL"), (0x0004FAB0, "BL"), (0x0004FACE, "BL"), (0x0004FAEE, "BL"), (0x0004FB0E, "BL"), (0x0004FB2E, "BL"), (0x000512E6, "BL"), (0x00051378, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00046F54, 8, ((0x00046F54, 0x00046F5C, "19d6ba4af861e978481e506cdd21a6e5d52f5d9025f6ea76d0b2c91891c149ab"),),
        "r1_touch_record_op_0c_b", "dispatch slot_0c on touch record 0x200067f8+4",
        ((0x0004FAA0, "B.W"), (0x0004FABC, "B.W"), (0x0004FAD6, "BL"), (0x0004FAF6, "BL"), (0x0004FB16, "BL"), (0x0004FB36, "BL"), (0x00051384, "B.W"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0007287C, 8, ((0x0007287C, 0x00072884, "8e9837530779a82c3684305f47053237e13123d5e7e247837ca2c3f2d9413b60"),),
        "r1_touch_slider_flag_clear", "clear byte 0x2000772c+4; pairs with r1_touch_slider_flag_get on same block",
        ((0x00046EAE, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00050F28, 8, ((0x00050F28, 0x00050F30, "034e81b868f4e0bfa210c45a8a48c061f018b5106811005a26ae3b70d7692034"),),
        "r1_i2c2_bus_lock", "dispatch slot_08 on i2c_2 record 0x200076f8; temp-reader bus acquire",
        ((0x00050E1E, "BL"), (0x00050E4E, "BL"), (0x00050ECE, "BL"), (0x000510DC, "BL"), (0x00051122, "BL"), (0x00051266, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00050EFC, 8, ((0x00050EFC, 0x00050F04, "6a1fbcf753d8112afbf3cfef51f3d94bac5174258e7496312f6b2781384470a0"),),
        "r1_i2c2_bus_unlock", "dispatch slot_0c on i2c_2 record 0x200076f8; temp-reader bus release",
        ((0x00050E3C, "BL"), (0x00050E74, "BL"), (0x00050EE6, "BL"), (0x00051102, "B.W"), (0x0005116C, "BL"), (0x00051288, "B.W"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x000500C8, 8, ((0x000500C8, 0x000500D0, "700aa73be52a29b79308687758ad2668a62dc0268d91a024bedaddff03e25324"),),
        "r1_watchdog_op_0c", "dispatch slot_0c on watchdog record 0x20007694",
        ((0x00066236, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0005083C, 8, ((0x0005083C, 0x00050844, "02796ba814e3d854412fd9ba83a3f4a9138355b88497bed956fbc8907370e510"),),
        "r1_yhm_block_word_set", "store word at YHM block 0x2000687c+0, return 1; caller r1_pmic_charge_event_plan",
        ((0x00096A9E, "BL"), (0x00096B14, "BL"), (0x00096BB2, "BL"), (0x00096C26, "B.W"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0004C5B8, 8, ((0x0004C5B8, 0x0004C5C0, "1067a0bdcf3149a9042ab3fe414cc4ad4c999b48a760b1847b20abfdb05a99fa"),),
        "r1_health_mode_get", "return byte 0x2001e454+0x24; activity/hrv callers",
        ((0x00048EEA, "BL"), (0x0004907E, "BL"), (0x00049AEA, "BL"), (0x00049F42, "BL"), (0x0004A99C, "BL"), (0x0004AF46, "BL"), (0x0004BBF2, "BL"), (0x0004FA62, "BL"), (0x0006ACEC, "BL"), (0x00084B2C, "BL"), (0x00084B32, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00050378, 6, ((0x00050378, 0x0005037E, "9a6c80e7430d2372665b4c8ef60b94c25d98cdcac6012fec680495eb8631c040"),),
        "r1_touch_bus_enable_on", "tail 0x50304 mode=1: dispatch slot_18 then slot_0c on record 0x20007688+4",
        ((0x0004EBDE, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0005037E, 6, ((0x0005037E, 0x00050384, "55324487a4f34514581a629ab36b6b0bd2a8f7be0672ff868bd91207b5a2685f"),),
        "r1_touch_bus_acquire_on", "tail 0x50338 mode=1: dispatch slot_08 then slot_18(1) on record 0x20007688+4",
        ((0x0004EB8A, "BL"), (0x00051296, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0006F812, 6, ((0x0006F812, 0x0006F818, "3f01b0974df2ddc0ecc7d672849bd70350f96ee66d05a4b7397a3d6712c00097"),),
        "r1_temp_reg90_read", "tail 0x6f53c RING-logged register read with addr 0x90",
        ((0x00050ED6, "BL"), (0x000510EE, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0006F82C, 6, ((0x0006F82C, 0x0006F832, "e1294c4430d5e48496a9c853ee712b3c5ff863527123fd263704f92747c4f2d5"),),
        "r1_temp_reg94_read", "tail 0x6f53c RING-logged register read with addr 0x94",
        ((0x00050EDC, "BL"), (0x000510F4, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0006F826, 6, ((0x0006F826, 0x0006F82C, "bae9bf0e761dc920d1de073345ce570ad185a82c34e9ad51840c4c86ac2447af"),),
        "r1_temp_channel_b_get", "tail 0x6f600: read reg 0x94, rev16, sxth, scale 0.0078125*1000 (mC)",
        ((0x00050E32, "BL"), (0x00050E6A, "BL"), (0x0005113A, "BL"), (0x0005127A, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00050998, 6, ((0x00050998, 0x0005099E, "5cb6a8729e95cc248a0c7ad68108c00e2564e96a9bea977932ae9018be8da215"),),
        "r1_health_module_field_set", "store word at 0x200076c4+4; caller r1_health_module_init",
        ((0x0004C5C8, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0004D584, 6, ((0x0004D584, 0x0004D58A, "97e279f9a3ade8c5ecfeff64897d7211922900f1df86b5ab1921609a6c0690e9"),),
        "r1_conn_field6_set", "store halfword at 0x200064b2+6; caller r1_message_pump_task",
        ((0x000450E6, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0004CB28, 6, ((0x0004CB28, 0x0004CB2E, "adef155190b82304e1ba90a2a25030357b49690bfb0c617f4be3480947c0c196"),),
        "r1_conn_field6_get", "return halfword 0x200064b2+6; caller r1_structured_log_cache_append",
        ((0x00041F0C, "BL"), (0x0004EE66, "BL"), (0x0004EE74, "BL"), (0x0004F9DE, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0004C6C0, 6, ((0x0004C6C0, 0x0004C6C6, "3c0a2c335e8fcf80c4100a66f61a44a70183c0c30be0a8749f802571f9a6902e"),),
        "r1_sleep_config_flag_get", "return byte 0x20006e94+2; caller sleep-drop logger 0x4a3e8",
        ((0x0004A3EC, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0004A8BC, 6, ((0x0004A8BC, 0x0004A8C2, "8f61f3207c802be9d89b3cfa1748adc458586b81abe646a9bf7b237057fa521b"),),
        "r1_activity_mode_byte_get", "return byte 0x20006ed4+0; callers activity accumulators + r1_hrv_rmssd",
        ((0x00048D5A, "BL"), (0x00048EDE, "BL"), (0x00049072, "BL"), (0x00057628, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0004E9D0, 6, ((0x0004E9D0, 0x0004E9D6, "8f61f3207c802be9d89b3cfa1748adc458586b81abe646a9bf7b237057fa521b"),),
        "r1_ble_control_flag_get", "return byte 0x200064f8+0; caller r1_ble_connection_control_event_consumer",
        ((0x00045284, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0008ACFC, 6, ((0x0008ACFC, 0x0008AD02, "0719e9572025682a72853d11d794ab4bf6ab4df0153470c259ebbf437cd6e011"),),
        "r1_sync_block_field_get", "return word 0x20006820+4; callers r1 activity/hr/hrv/spo2/sleep sync flush",
        ((0x0003C6DC, "BL"), (0x0004028E, "BL"), (0x000411A8, "BL"), (0x00044466, "BL"), (0x0008DB14, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0006F640, 4, ((0x0006F640, 0x0006F644, "f5c0c38d85ddf29a1b5db89d823b2a96137a77652922f8cb161f77f9925a2ede"),),
        "r1_temp_reg_read_thunk", "pure B.W thunk to 0x50f34 (register read 2 bytes via registry slot_14)",
        ((0x0006F54C, "BL"), (0x0006F60A, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0006F644, 4, ((0x0006F644, 0x0006F648, "e9bc7ab6405fe4cb4bd068c679cc8ee6720e9900bb43edad0abb2a009fa3c60e"),),
        "r1_temp_reg_write_thunk", "pure B.W thunk to 0x50f5c (register write via registry slot_14)",
        ((0x0006F668, "BL"), (0x0006F74A, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0004CB9C, 4, ((0x0004CB9C, 0x0004CBA0, "06936d0536d64e86c623270163a043c1b484bbc978af8fbf56cd1650cbfb6587"),),
        "r1_identity_data_ptr_get", "return RAM pointer 0x200064d6; callers version-string builder 0x4f160 + r1_system_control_command_37_plan",
        ((0x0004F16E, "BL"), (0x00062994, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00027208, 4, ((0x00027208, 0x0002720C, "6b6b0f7315d31682c7f8059490eb3df143139881118c2c78a5b82ce1834d895d"),),
        "r1_main_reset_trampoline", "reset-path B.W thunk to r1_main (0x75f64); caller __scatterload",
        ((0x000283B8, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00095BE8, 4, ((0x00095BE8, 0x00095BEC, "07983508cd241588ec24ee42f080e1abe7f59dfb06a3522f4fb2f0cf9f28213e"),),
        "r1_watchdog_op_18_thunk", "pure B.W thunk to 0x500fc (watchdog slot_18 dispatch)",
        ((0x00085034, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0008E7AC, 4, ((0x0008E7AC, 0x0008E7B0, "9c632ec6a3d17e3527a47ccda18cbfb19a86385ecc7aaec8565bf91aae90a43a"),),
        "r1_touch_button_irq_thunk", "pure B.W thunk to 0x51368 (RING-logged touch button irq process)",
        ((0x00046662, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0008DD8C, 4, ((0x0008DD8C, 0x0008DD90, "5c78a202af9bf7fd93bee114418537c8863916fb87775e46ad313a9eae35b2ce"),),
        "r1_sleep_db_init_thunk", "pure B.W thunk to 0x5b0f8 (RING-logged sleep_db FAL init)",
        ((0x00092712, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0005069E, 4, ((0x0005069E, 0x000506A2, "b445b5581f75edb494c8b24d469b073dd3508c28036437b2948f1725a113135f"),),
        "r1_charge_state_byte_thunk", "pure B.W thunk to 0x91270; caller r1_pmic_charge_event_plan",
        ((0x00096B3E, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00050754, 4, ((0x00050754, 0x00050758, "39350eb194d73c40fec05ef8f47fc189dd4befcc97f90f14b8cfc6b0f8e20657"),),
        "r1_sysctl_op_sequence_thunk", "pure B.W thunk to 0x80e74 (registry ops + 200x callback delay); caller r1_system_control_command_37_plan",
        ((0x000460DA, "BL"), (0x00062970, "BL"), (0x00062DC6, "BL"), (0x00062DE4, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0004B33C, 2, ((0x0004B33C, 0x0004B33E, "c7dfbb7d02759eacb64dbc916c1bb6f21eabaff1c1032ea5c9176abf7fd28df8"),),
        "r1_module_init_hook_nop", "empty init hook; caller module init 0x4a21c",
        ((0x0004A23C, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0004E1E0, 2, ((0x0004E1E0, 0x0004E1E2, "c7dfbb7d02759eacb64dbc916c1bb6f21eabaff1c1032ea5c9176abf7fd28df8"),),
        "r1_legacy_pair_hook_nop", "empty hook; caller r1_legacy_pair_command_plan",
        ((0x00092C14, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0007BBBC, 2, ((0x0007BBBC, 0x0007BBBE, "c7dfbb7d02759eacb64dbc916c1bb6f21eabaff1c1032ea5c9176abf7fd28df8"),),
        "r1_legacy_battery_hook_nop", "empty stub; caller legacy battery command switch 0x62840",
        ((0x00062890, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0002ADFC, 2, ((0x0002ADFC, 0x0002ADFE, "c7dfbb7d02759eacb64dbc916c1bb6f21eabaff1c1032ea5c9176abf7fd28df8"),),
        "r1_gsensor_sample_sink_nop", "empty per-sample sink; caller 0x6f920 gsensor record iterator",
        ((0x0006F94A, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0002ADFA, 2, ((0x0002ADFA, 0x0002ADFC, "c7dfbb7d02759eacb64dbc916c1bb6f21eabaff1c1032ea5c9176abf7fd28df8"),),
        "r1_gsensor_cache_hook_nop", "empty hook; caller 0x6f964 hal_gsensor LOG_D cache flush",
        ((0x0006F988, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
)

NORDIC_FRONTIER_LT32_FUNCTIONS = (
    _function(
        0x00030CA8, 8, ((0x00030CA8, 0x00030CB0, "e954cb072be3c92af3528634cb71438aa1d07a89dec0b07096ff7638a8261e69"),),
        "nrfx_pwm_0_irq_handler", "Nordic nrfx_pwm.c PWM0 instance vector stub over shared irq_handler",
        (),
        "nordic_nrf5_sdk_17_1_0", "use_nordic_sdk",
    ),
    _function(
        0x00030CB8, 8, ((0x00030CB8, 0x00030CC0, "dd963435c7870107d7d7f58f71a5329ddc336838dcc6fa62d94bafbdfbceeed6"),),
        "nrfx_pwm_1_irq_handler", "Nordic nrfx_pwm.c PWM1 instance vector stub over shared irq_handler",
        (),
        "nordic_nrf5_sdk_17_1_0", "use_nordic_sdk",
    ),
    _function(
        0x00030CC8, 8, ((0x00030CC8, 0x00030CD0, "75a2d10fe753e94a4ca292ea8b1448caa814946eafe0cc922dd20e7c340a6dbf"),),
        "nrfx_pwm_2_irq_handler", "Nordic nrfx_pwm.c PWM2 instance vector stub over shared irq_handler",
        (),
        "nordic_nrf5_sdk_17_1_0", "use_nordic_sdk",
    ),
)

TOOLCHAIN_FRONTIER_LT32_FUNCTIONS = (
    _function(
        0x000620F4, 24, ((0x000620F4, 0x0006210C, "6dd71d7dadaaab2a520855bda1f434c221a3be13566b281d292e05ad23695b58"),),
        "fabs", "double-precision absolute value (clears sign bit); called by atan/pow/tanh",
        ((0x00038272, "BL"), (0x00039C52, "BL"), (0x0003B26A, "BL"), (0x0003B2A4, "BL"),),
        "arm_toolchain_runtime", "use_toolchain_runtime",
    ),
    _function(
        0x00098ECA, 16, ((0x00098ECA, 0x00098EDA, "dd7681a368023a5ea89812d2f1c6aaf0bbeaefd1b292e829b3490cdb0b0b404b"),),
        "fabsf", "single-precision absolute value via vcmpe/vneg; called by YHM-region float code",
        ((0x00035522, "BL"), (0x00035540, "BL"),),
        "arm_toolchain_runtime", "use_toolchain_runtime",
    ),
)

GOMORE_FRONTIER_LT32_FUNCTIONS = (
    _function(
        0x0006AD04, 30, ((0x0006AD04, 0x0006AD22, "60b02a663e3bb8f5cf8ff6b6ef2ab9783225fdfcac9d2ffee1c6c1abb4ee9f60"),),
        "", "scan seven 0x10-stride records for clear bit0; exclusive GoMore caller 0x49410 (already GoMore-gated per stream boundary doc)",
        ((0x00049578, "BL"), (0x00049594, "BL"),),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x000715B8, 28, ((0x000715B8, 0x000715D4, "cb878382ff91f2a8ea0111a49077638214676a34fb2e35e45bda420c6da2c54a"),),
        "", "record field init (+4/+8/+0xc/+0x10 w/ 0x14 offset option); exclusive GoMore caller 0x88450 x7",
        ((0x000884C0, "BL"), (0x0008851E, "BL"), (0x00088576, "BL"), (0x000885CE, "BL"), (0x00088648, "BL"), (0x000886A0, "BL"), (0x000886F8, "BL"),),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x000883D4, 26, ((0x000883D4, 0x000883EE, "c663293b3bf8234e34a68923a02e9551836580e93d2a4d5c00465eaf6e2b9c7e"),),
        "", "memclr two adjacent 0x14 blocks; exclusive GoMore caller 0x60680",
        ((0x000607C0, "BL"),),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x00071B2A, 24, ((0x00071B2A, 0x00071B42, "e113c08156980270b0ab11ceb3ab5aca594d836e5c9d3c7416ef3a092eb782cf"),),
        "", "fill two floats with -1.0f; exclusive GoMore caller 0x5f3d8",
        ((0x0005F40E, "BL"), (0x0005F492, "BL"),),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x00068FBC, 24, ((0x00068FBC, 0x00068FD4, "8b61c14032db5d762408b8fbf7242739d686e9120d43540523b2a5ead875742f"),),
        "", "call GoMore pair 0x68f8c+0x6778c and store float result; exclusive GoMore callers 0x69644/0x81040",
        ((0x0006971E, "BL"), (0x000697A8, "BL"), (0x00081156, "BL"), (0x00081216, "BL"), (0x0008130E, "BL"), (0x00081366, "BL"),),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x00072AD4, 22, ((0x00072AD4, 0x00072AEA, "618c8bc341fa83b9f53579cd0d8302157ff624f0ecb132fcd837e34cd77b41da"),),
        "", "float bit-pattern bound check (bits+0xbde00000 <= 0x1500000); exclusive GoMore caller 0x5f56c",
        ((0x0005F5D0, "BL"), (0x0005F644, "BL"),),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x000928DA, 20, ((0x000928DA, 0x000928E0, "0d5d420fb05b64c7cb1ad2880b7d9bd544180c03d3abed40898f1202d68967b6"),),
        "", "float vector scalar-multiply tail at 0x928da with shared loop head 0x928cc (vldmia/vmul/vstmia)",
        (),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x00094A4C, 18, ((0x00094A4C, 0x00094A5E, "cccf4d472e4dc66599d2678b64e1be98f44961d09f64a8493c68bef7e0907139"),),
        "", "store callback record fields +0xb4/+0xb8/+0xbc; exclusive GoMore caller 0x60b80",
        ((0x00060DA6, "BL"),),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x00071A20, 18, ((0x00071A20, 0x00071A32, "d0a20affa037158d3b40bc8592eadfb2c0afa701a3da29b3c8be1b3751574836"),),
        "", "record field init (+0/+4 w/ 0x14 offset option); exclusive GoMore caller 0x88450 x4",
        ((0x00088780, "BL"), (0x0008879C, "BL"), (0x000887FE, "BL"), (0x00088836, "BL"),),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x00087600, 18, ((0x00087600, 0x00087612, "e39b613eea4a22ba36d7ff78051755d1842494e432db9fa5849b4b332160abe8"),),
        "", "qsort subrange wrapper with float comparator 0x58a40; exclusive GoMore callers 0x64380/0x68840/0x7ed30",
        ((0x00064432, "BL"), (0x000688F0, "BL"), (0x00068946, "BL"), (0x0007ED3E, "BL"),),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x00091A56, 8, ((0x00091A56, 0x00091A5E, "744a6da8eff470a16e1af07b9aa4828fe8319b8263bea7c1d7ad02fb07a5a0e4"),),
        "", "ldmia pair-unpack tail-thunk to GoMore max-index 0x4ece0; exclusive GoMore caller 0x88450",
        ((0x0008888A, "BL"),),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x00068720, 6, ((0x00068720, 0x00068726, "72ef1a57275a64f9fc84dd835dd28e7e0aafece2aceb853b3bf26e2b1dd5fb87"),),
        "", "return constant 0x2e0; exclusive GoMore callers 0x4bd98/0x6fea0",
        ((0x0004BDA0, "BL"), (0x0006FF46, "BL"),),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x0006841A, 6, ((0x0006841A, 0x00068420, "944d68547518c726a465ea491086a88fac31190904a1e4b15c718fbc74b12852"),),
        "", "return constant 0x39e0; exclusive GoMore caller 0x4bd98",
        ((0x0004BDA6, "BL"),),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x00071704, 6, ((0x00071704, 0x0007170A, "5b6782a5ed30d2414f7c3c02d135de1f6cf68ffccd406c398dd6aa74f6fea26f"),),
        "", "memclr 0x5a wrapper; GoMore caller 0x71cd8 (+0x94300)",
        ((0x00071D1E, "BL"), (0x00094352, "B.W"),),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x00064770, 4, ((0x00064770, 0x00064774, "35670bb79141dd43ff99efdf7b3389dba10de780c792cf02a685a59f85553750"),),
        "", "field setter *(p+4)=v; exclusive GoMore caller 0x60b80",
        ((0x00060CAE, "BL"),),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x0005A442, 4, ((0x0005A442, 0x0005A446, "a7ddd513d149ea16fdd4db3f82267f83087aeaddd06b5dde5468adb704205fc4"),),
        "", "return-0 provider stub; exclusive GoMore caller 0x6fea0",
        ((0x0006FFBC, "BL"),),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x00076500, 2, ((0x00076500, 0x00076502, "c7dfbb7d02759eacb64dbc916c1bb6f21eabaff1c1032ea5c9176abf7fd28df8"),),
        "", "empty callback stub; exclusive GoMore caller 0x94384",
        ((0x000944B6, "BL"),),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x000578C8, 2, ((0x000578C8, 0x000578CA, "c7dfbb7d02759eacb64dbc916c1bb6f21eabaff1c1032ea5c9176abf7fd28df8"),),
        "", "empty callback stub; exclusive GoMore caller 0x5ff94 x18",
        ((0x0005FFFA, "BL"), (0x0006004E, "BL"), (0x000600AA, "BL"), (0x0006010A, "BL"), (0x00060164, "BL"), (0x000601B4, "BL"), (0x0006020E, "BL"), (0x000602A6, "BL"), (0x00060314, "BL"), (0x0006036E, "BL"), (0x000603FC, "BL"), (0x0006044E, "BL"), (0x000604B0, "BL"), (0x0006050E, "BL"), (0x00060568, "BL"), (0x000605CA, "BL"),),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x00049E58, 2, ((0x00049E58, 0x00049E5A, "c7dfbb7d02759eacb64dbc916c1bb6f21eabaff1c1032ea5c9176abf7fd28df8"),),
        "", "empty callback stub; exclusive GoMore caller 0x6c294",
        ((0x0006C2EC, "BL"),),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
)

GOODIX_FRONTIER_LT32_FUNCTIONS = (
    _function(
        0x0006EB00, 30, ((0x0006EB00, 0x0006EB1E, "82e21044405ea1e2acb26b0c9aaa64bcedb74cfbf29a0bb6628f2ff431c67bcb"),),
        "", "bounded copy of version string 'pre_pv_v1_1_0' (max 0xe); exclusive Goodix-candidate caller 0x6ec28",
        ((0x0006EC7C, "BL"),),
        "goodix_gh3x2x_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x0006CC34, 30, ((0x0006CC34, 0x0006CC52, "aa82663a18dd17ffc44cacfde9a7e11d90bf349efb909ebd29096fe6661556ea"),),
        "", "bounded copy of version string 'pv_v1_1_0' (max 0xa); exclusive Goodix-candidate caller 0x6d3c0",
        ((0x0006D410, "BL"),),
        "goodix_gh3x2x_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x00029C74, 30, ((0x00029C74, 0x00029C92, "43fbd8e3bc97da80c1827c28455b88c761ecbc205cb61a96d5feb55d58c8a836"),),
        "", "copy 0x1c (7-entry) jump table to stack and call table[*param](param); Goodix-region state dispatcher",
        ((0x0006CC78, "BL"), (0x0006CC80, "BL"), (0x0006CC8A, "BL"),),
        "goodix_gh3x2x_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x0002ACF4, 28, ((0x0002ACF4, 0x0002AD10, "3978affe342cfb5b2f275676c9985d465b855b38882dc02cd51d187cd50b566d"),),
        "", "one-time init: flag-gated call 0x29f88 then byte defaults at +1/+0xb/+0x13; exclusive Goodix caller 0x6ec28",
        ((0x0006EC3E, "BL"),),
        "goodix_gh3x2x_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x0002D16C, 22, ((0x0002D16C, 0x0002D182, "7700bcdebc68cb3450f061c1479def157169d39b24def7d0d42097c773cbba1b"),),
        "", "call Goodix-candidate 0x6ec28(**(param+4)) and map to 0/-1 result",
        (),
        "goodix_gh3x2x_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x00029D34, 22, ((0x00029D34, 0x00029D4A, "cff4d8146e897ec486b19830f9c730e7565978d6daa7b77a022c44977e4c389f"),),
        "", "select fixed-point pair: flag 0 -> 0xeccccd/0xa66666, flag 1 -> 0xf33333/0xc00000; exclusive Goodix callers",
        ((0x00029DB2, "BL"), (0x0002B59E, "BL"), (0x0002C1DE, "BL"),),
        "goodix_gh3x2x_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x00029F88, 20, ((0x00029F88, 0x00029F9C, "cb689738042fc6105314455b4a3e3be8d58b6096759a1a927695674aa1d3e9d6"),),
        "", "record init: zero 2 bytes, fill 0x20 bytes with 0xff from +3; Goodix-region, callers 0x2aedc (goodix) + 0x2acf4",
        ((0x0002A63C, "BL"), (0x0002AD00, "BL"), (0x0002AEC8, "BL"), (0x0002B070, "BL"), (0x0002B132, "B.W"),),
        "goodix_gh3x2x_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x0002A474, 16, ((0x0002A474, 0x0002A484, "60556d6148277c82889dafacd0545465590003d839c0806844ba6c879d5452b7"),),
        "", "reset state record (0xff byte, zero +1/+0xe/+0x14); caller 0x29cc0 Goodix-region init",
        ((0x00029CC8, "BL"),),
        "goodix_gh3x2x_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x0006F9D4, 12, ((0x0006F9D4, 0x0006F9E0, "adba09bc5319492f55f0bb20a38e14e2bab536294fa54286c137d4ae00de2bb9"),),
        "", "indirect-call trampoline through RAM hook 0x2002fd28+4; exclusive Goodix-candidate caller 0x2e0d0",
        ((0x0002E1B8, "BL"),),
        "goodix_gh3x2x_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x0002ABEC, 12, ((0x0002ABEC, 0x0002ABF8, "9377983b147af3e7fcbb259dff45af55ad8fbd00d84c1fd982279a2787e388da"),),
        "", "clear bytes 5/6/7 of Goodix state struct 0x20006xxx; caller 0x29cc0 Goodix-region init",
        ((0x00029CCC, "BL"),),
        "goodix_gh3x2x_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x0006A140, 6, ((0x0006A140, 0x0006A146, "e63a4dcd56255eaa7da7028e69aae50c177f6658400356dff8b43d9c72444946"),),
        "", "return constant 0x12f9; exclusive Goodix-candidate caller 0x6d204",
        ((0x0006D2F4, "BL"),),
        "goodix_gh3x2x_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x0006A130, 4, ((0x0006A130, 0x0006A134, "06936d0536d64e86c623270163a043c1b484bbc978af8fbf56cd1650cbfb6587"),),
        "", "return library pointer 0x0009d640; exclusive Goodix-candidate caller 0x6d204",
        ((0x0006D302, "BL"),),
        "goodix_gh3x2x_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x0006A138, 4, ((0x0006A138, 0x0006A13C, "06936d0536d64e86c623270163a043c1b484bbc978af8fbf56cd1650cbfb6587"),),
        "", "return library pointer 0x000a04cc; exclusive Goodix-candidate caller 0x6d204",
        ((0x0006D2FC, "BL"),),
        "goodix_gh3x2x_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x0006A148, 4, ((0x0006A148, 0x0006A14C, "06936d0536d64e86c623270163a043c1b484bbc978af8fbf56cd1650cbfb6587"),),
        "", "return library pointer 0x000a50b0; exclusive Goodix-candidate caller 0x6d204",
        ((0x0006D308, "BL"),),
        "goodix_gh3x2x_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x0006A150, 4, ((0x0006A150, 0x0006A154, "06936d0536d64e86c623270163a043c1b484bbc978af8fbf56cd1650cbfb6587"),),
        "", "return library pointer 0x000a692c; exclusive Goodix-candidate caller 0x6d204",
        ((0x0006D2EE, "BL"),),
        "goodix_gh3x2x_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x0006A018, 4, ((0x0006A018, 0x0006A01C, "06936d0536d64e86c623270163a043c1b484bbc978af8fbf56cd1650cbfb6587"),),
        "", "return library pointer 0x000ad1ac; exclusive Goodix-candidate caller 0x2f624",
        ((0x0002F648, "BL"),),
        "goodix_gh3x2x_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x0006CC2C, 4, ((0x0006CC2C, 0x0006CC30, "06936d0536d64e86c623270163a043c1b484bbc978af8fbf56cd1650cbfb6587"),),
        "", "return library pointer 0x000ad13c; exclusive Goodix-candidate caller 0x6d3c0",
        ((0x0006D3EE, "BL"),),
        "goodix_gh3x2x_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x0006EAF8, 4, ((0x0006EAF8, 0x0006EAFC, "06936d0536d64e86c623270163a043c1b484bbc978af8fbf56cd1650cbfb6587"),),
        "", "return library pointer 0x000ad160; exclusive Goodix-candidate caller 0x6ec28",
        ((0x0006EC5A, "BL"),),
        "goodix_gh3x2x_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x0002E8C8, 4, ((0x0002E8C8, 0x0002E8CC, "64d23481cb6a254816fb9c4c9b22031f78ed0a6ece5a6b0f6849a3ee7f77a2bb"),),
        "", "constant-1 provider stub; exclusive Goodix-candidate caller 0x6ec28",
        ((0x0006EC48, "BL"),),
        "goodix_gh3x2x_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x0002E8C4, 4, ((0x0002E8C4, 0x0002E8C8, "eef50e6a1498dd61029a97dd496d75f59c4b2272f7ddc06bea7c6e697c6d50b0"),),
        "", "constant-4 provider stub; exclusive Goodix-candidate caller 0x6d3c0",
        ((0x0006D3DC, "BL"),),
        "goodix_gh3x2x_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x0002AE00, 4, ((0x0002AE00, 0x0002AE04, "64d23481cb6a254816fb9c4c9b22031f78ed0a6ece5a6b0f6849a3ee7f77a2bb"),),
        "", "constant-1 provider stub; exclusive Goodix-candidate caller 0x6a4d8",
        ((0x0006A4DC, "BL"),),
        "goodix_gh3x2x_candidate", "vendor_source_required_not_redistributable",
    ),
)

YHM_FRONTIER_LT32_FUNCTIONS = (
    _function(
        0x0003541C, 28, ((0x0003541C, 0x00035438, "8eb335948c8ef1db119364e80b4543a52cbb8141d0de1b04d81d9a7b300e8ac3"),),
        "", "YHM transport probe: invoke record ops +0x1c then +0x28 (block via DAT), return readback!=0; sole caller YHM status reader 0x3529a",
        ((0x0003529C, "BL"),),
        "yhmicros_yhm2710_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x00035272, 26, ((0x00035272, 0x00035280, "cc545f959282ef0a4fc2f1c448c5af86254e5627bc3954a8e446aa335cd8bbd9"), (0x0003528E, 0x0003529A, "d54c0a0c1de39eb699b9f3718876c88f64306951e5a1ceca4551d50d79d70466"),),
        "", "YHM status-nibble (0x3529a) to charge-state enum map (10-12->1, 13->2)",
        ((0x00050618, "B.W"),),
        "yhmicros_yhm2710_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x000507AC, 26, ((0x000507AC, 0x000507C6, "06432801ffd976c63c16c31ac7aaea5de21f3b6bb26c3fef4c68d4b9fef777a4"),),
        "", "dispatch registry slot_08 then slot_20 on YHM record 0x2000687c+0xc (transport lock + op)",
        ((0x00042ED0, "B.W"),),
        "yhmicros_yhm2710_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x00035684, 20, ((0x00035684, 0x00035698, "9ea11412388739d8bc24d284b9ebbf556b1badb5ef37d6e0e6eec323cb4caa86"),),
        "", "YHM single-wire command byte 0xf8 sender via transport write 0x35760",
        ((0x00050848, "B.W"),),
        "yhmicros_yhm2710_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x000355A8, 20, ((0x000355A8, 0x000355BC, "934a4f196b5dc923db4cb608dcc79d26418048fa452d42d1ad39720a258b1d68"),),
        "", "YHM single-wire command byte 0xa8 (register-2) sender via transport write 0x35760",
        ((0x0005078C, "BL"),),
        "yhmicros_yhm2710_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x0005C0FA, 20, ((0x0005C0FA, 0x0005C10E, "5847783ae5f4aff2d959dbac785f58d651b06c1a17558bd25d000a53cf169411"),),
        "", "0xd1-iteration nop delay loop; exclusive callers yhm2710_stacmd_bus_recovery/idle",
        ((0x0005CCA2, "BL"), (0x0005CCAC, "BL"), (0x0005CCB0, "BL"), (0x0005CCB4, "BL"), (0x0005CCB8, "BL"), (0x0005CCE8, "BL"),),
        "yhmicros_yhm2710_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x00035766, 12, ((0x00035766, 0x00035772, "622312fa1ca6e1e25f298f2e5537c11a8c42c91ee244132a5ad02a4f05e82168"),),
        "", "YHM transport write one-stack-byte wrapper over 0x35760",
        ((0x00050682, "BL"),),
        "yhmicros_yhm2710_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x00035412, 8, ((0x00035412, 0x0003541A, "4fe3ea9d2bf7ec94e85c69b533c47836894e8da18051ea75f4a082a004485e26"),),
        "", "YHM transport write wrapper (arg2->r2, len=1) tail-branching 0x3540c",
        ((0x00050630, "BL"), (0x00050638, "BL"), (0x00050640, "BL"), (0x0005066C, "BL"),),
        "yhmicros_yhm2710_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x000507A0, 8, ((0x000507A0, 0x000507A8, "d7ecb1cbaa34e5d6a75ec653c6631a7260e0a608c7f813ba76e8eb49423706b4"),),
        "", "dispatch registry slot_0c on YHM record field 0x2000687c+0xc; called by YHM transport 0x35760",
        ((0x00042EC6, "BL"), (0x00042EDA, "BL"), (0x000507D4, "BL"), (0x0005080C, "BL"), (0x00096B08, "BL"), (0x00096BA8, "BL"),),
        "yhmicros_yhm2710_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x00050608, 8, ((0x00050608, 0x00050610, "a86d3d01890cdb16820b6a56e429d56a013f73ee3b21a55878cef0417a3533f7"),),
        "", "dispatch registry slot_08 on YHM record field 0x2000687c+4; called by YHM transport 0x35760",
        ((0x000507D8, "BL"), (0x00050810, "BL"),),
        "yhmicros_yhm2710_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x0003540C, 6, ((0x0003540C, 0x00035412, "6ba60cc0148015a8c204c06e20d138f413cce8e7d75e3a2abb08d8a57bfc2c35"),),
        "", "YHM transport record write tail (uxtb + b.w 0x507cc, request block 0x20016b70 / YHM record 0x2000687c)",
        ((0x000350EE, "BL"), (0x0003526E, "B.W"), (0x000352A8, "BL"), (0x0003531A, "BL"), (0x00035416, "B.W"), (0x0003544A, "BL"), (0x00035562, "BL"), (0x000355CA, "BL"),),
        "yhmicros_yhm2710_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x00050618, 4, ((0x00050618, 0x0005061C, "9011d0939e811241075a55f8ebf69d4ebe99a0f5f8db71bbcedbd001ead7ae2b"),),
        "", "pure B.W thunk to 0x35272 (YHM charge-state map)",
        ((0x00031FD4, "BL"), (0x0003CD30, "BL"), (0x000463F6, "BL"), (0x0004640E, "BL"), (0x0004641C, "BL"), (0x00047F2E, "BL"), (0x0004C3D2, "BL"), (0x00062554, "BL"), (0x0006257E, "BL"), (0x00091246, "BL"), (0x00091258, "BL"), (0x000912B2, "BL"), (0x00096AD8, "BL"), (0x00096CE2, "BL"), (0x00096D08, "BL"),),
        "yhmicros_yhm2710_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x00050848, 4, ((0x00050848, 0x0005084C, "ccb12e110758e00d463f67ba662622dbfa9da9e573e9e977d28f9189ec635326"),),
        "", "pure B.W thunk to 0x35684 (YHM 0xf8 command sender)",
        ((0x00096BAC, "BL"),),
        "yhmicros_yhm2710_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x00050750, 4, ((0x00050750, 0x00050754, "1afc9fdea13e61b0a9571cee1ce39e20477840291e261b7ec4de737513e433a7"),),
        "", "pure B.W thunk to 0x35508 (classified yhmicros float charge-level search)",
        ((0x00096C5C, "BL"),),
        "yhmicros_yhm2710_candidate", "vendor_source_required_not_redistributable",
    ),
)

DEVICE_REGISTRY_FRONTIER_LT32_FUNCTIONS = (
    _function(
        0x0005DBEA, 28, ((0x0005DBEA, 0x0005DC06, "73a39fe8b4131faa0defda7f373c8f31517826306814f26d44f2c308c1475841"),),
        "", "set bit1 of registry record +0x10 under registry mutex; task-scope record activation",
        ((0x00045104, "BL"), (0x00045C24, "BL"), (0x00046448, "BL"), (0x0004666E, "BL"), (0x000469A2, "BL"), (0x00046A00, "BL"), (0x00091FAE, "BL"), (0x00092072, "BL"), (0x00092124, "BL"), (0x000921B2, "BL"), (0x000921DC, "BL"), (0x000922B4, "BL"), (0x00092538, "BL"), (0x000925E0, "BL"), (0x00092644, "BL"), (0x00092742, "BL"), (0x000927A0, "BL"), (0x00092804, "BL"),),
        "unknown_generic_device_registry_candidate", "clean_room_reimplementation_owner_authorized",
    ),
    _function(
        0x0005DA30, 22, ((0x0005DA30, 0x0005DA46, "202771b2d91286b388af3eea5175550d4113180b04b3d4fb50e2765f6ea3f4ff"),),
        "", "walk registry record chain at 0x20006730+4, return flagged record field; used by cmbacktrace adapters",
        ((0x00058618, "BL"), (0x0006A09A, "BL"), (0x0006A0BA, "BL"),),
        "unknown_generic_device_registry_candidate", "clean_room_reimplementation_owner_authorized",
    ),
    _function(
        0x00097730, 18, ((0x00097730, 0x00097742, "be57053145ecc75bb8701bedfe52ae7f9209df4fa0008599d48ed3daef101cda"),),
        "", "guarded osMutexAcquire on registry mutex 0x20006730+8; caller device_registry_name_task_insert",
        ((0x0005DA06, "BL"), (0x0005DA56, "BL"), (0x0005DB28, "BL"), (0x0005DBC2, "BL"), (0x0005DBF0, "BL"),),
        "unknown_generic_device_registry_candidate", "clean_room_reimplementation_owner_authorized",
    ),
    _function(
        0x00097748, 14, ((0x00097748, 0x00097756, "4f8bf51831aef1a72648b2b117af15b869adbb19f4ea16fd4a8c11b0d53825cf"),),
        "", "guarded osMutexRelease on registry mutex 0x20006730+8; caller device_registry_name_task_insert",
        ((0x0005DA26, "B.W"), (0x0005DAA4, "BL"), (0x0005DBA0, "BL"), (0x0005DBAC, "BL"), (0x0005DBE4, "B.W"), (0x0005DC00, "B.W"),),
        "unknown_generic_device_registry_candidate", "clean_room_reimplementation_owner_authorized",
    ),
)

SENSOR_STREAM_FRONTIER_LT32_FUNCTIONS = (
    _function(
        0x0008A584, 26, ((0x0008A584, 0x0008A59E, "3a3f22e296bf22ae85b36174c5c4634dc110b8de79dbf2883d8e456bf9875e7c"),),
        "", "set bit0 of stream object +0x14 (null-assert hang); caller 0x8a404 framework timer check",
        ((0x0008A450, "BL"),),
        "unknown_sensor_stream_framework_candidate", "clean_room_reimplementation_owner_authorized",
    ),
    _function(
        0x0008A5E4, 24, ((0x0008A5E4, 0x0008A5FC, "7d7cf5679612472cc449c6548f31c3a35f07e5f1b1e1b96aff3fd15c1a60528f"),),
        "", "saturating remaining-time = *p1 - elapsed(p1[1]); callers 0x8a404 + sensor_stream_timer_poll_candidate",
        ((0x0008A416, "BL"), (0x0008A4E0, "BL"),),
        "unknown_sensor_stream_framework_candidate", "clean_room_reimplementation_owner_authorized",
    ),
    _function(
        0x0008A5D0, 20, ((0x0008A5D0, 0x0008A5E4, "2a13d5d2bd800c574ff8e1401a0672925512a4c38610e848c3119c857fed6014"),),
        "", "guarded *p=v store (null-assert hang); callers sensor_stream_register/unregister_candidate",
        ((0x00089A0E, "BL"), (0x0008A0D6, "BL"),),
        "unknown_sensor_stream_framework_candidate", "clean_room_reimplementation_owner_authorized",
    ),
    _function(
        0x0008A540, 18, ((0x0008A540, 0x0008A552, "958d6ca092f7ff6895150039ef7f0258e958143b540f4d6482311f541399b46e"),),
        "", "clear framework timer +0x10 then invoke +0x28 hook with +0x2c arg (block 0x2001a2bc)",
        ((0x0008A34C, "BL"), (0x0008A3A4, "BL"), (0x0008A3F8, "B.W"), (0x0008A5AE, "B.W"),),
        "unknown_sensor_stream_framework_candidate", "clean_room_reimplementation_owner_authorized",
    ),
    _function(
        0x0005D986, 18, ((0x0005D986, 0x0005D998, "6406a46fcfa316eef9ecfc0f61f52672c9d8b8df0f246e5b413b93eaa57d206a"),),
        "", "stream-record idle check (+4/+8 both null); callers register/unregister/timer-dispatch candidates",
        ((0x000898B2, "BL"), (0x00089BF0, "BL"), (0x00089CD2, "BL"),),
        "unknown_sensor_stream_framework_candidate", "clean_room_reimplementation_owner_authorized",
    ),
    _function(
        0x0008A03C, 18, ((0x0008A03C, 0x0008A04E, "6b0d1845c3e23e0b11437313a71f96db28e8b4e02462b005e32f7357c6428860"),),
        "", "store 6-word descriptor (sxtb field) to framework static 0x2001a1e4",
        (),
        "unknown_sensor_stream_framework_candidate", "clean_room_reimplementation_owner_authorized",
    ),
    _function(
        0x0005D8FE, 16, ((0x0005D8FE, 0x0005D90E, "651788e4c2aeea04616cd676f0608e7414823b77bdc068d8c7f3eaec15db800a"),),
        "", "init buffer descriptor {align4(len),0,0}; callers sensor_stream_object_create + framework init 0x8a55c",
        ((0x0005DAD8, "BL"), (0x00089744, "BL"), (0x00089DAA, "BL"), (0x0008A562, "BL"),),
        "unknown_sensor_stream_framework_candidate", "clean_room_reimplementation_owner_authorized",
    ),
    _function(
        0x0008A5C0, 16, ((0x0008A5C0, 0x0008A5D0, "05a966bc816f07ac255032bb761b5f2502f1777eef7b2e8a264d5f5fba1e6deb"),),
        "", "bfi bit0 at stream object +0x28 (dispatch flag); exclusive caller r1_sensor_stream_registration_plan",
        ((0x00089F38, "BL"), (0x00089F4A, "BL"), (0x00089F5C, "BL"), (0x00089F6E, "BL"), (0x00089F80, "BL"), (0x00089F92, "BL"), (0x00089FA4, "BL"), (0x00089FBA, "B.W"),),
        "unknown_sensor_stream_framework_candidate", "clean_room_reimplementation_owner_authorized",
    ),
    _function(
        0x0008A3F0, 14, ((0x0008A3F0, 0x0008A3FE, "f5de64f8d83c73893f191a4dd6569cdf41735e510218d0cedcd4acd81844f305"),),
        "", "store byte at 0x2001a2bc+0xc, trigger 0x8a540 when nonzero; caller 0x8a55c framework init",
        ((0x0008A568, "BL"),),
        "unknown_sensor_stream_framework_candidate", "clean_room_reimplementation_owner_authorized",
    ),
    _function(
        0x00089ED8, 14, ((0x00089ED8, 0x00089EE6, "e830f7676e65c65d3257b920af4d45dc3ce3742888f2424f5a34cb8cafc1fd20"),),
        "", "store 6-word descriptor to framework static 0x2001a1cc",
        (),
        "unknown_sensor_stream_framework_candidate", "clean_room_reimplementation_owner_authorized",
    ),
    _function(
        0x0008A1D0, 12, ((0x0008A1D0, 0x0008A1DC, "7ac8dd812fdaa159fca9843eeb466207494679a3411caadc0ecf7c5817f613a8"),),
        "", "framework tick source: call RAM hook 0x2001a2ac+8 if set else osKernelGetTickCount; used by timer poll/dispatch",
        ((0x0006F530, "BL"), (0x0008174E, "BL"), (0x0008A1C8, "BL"), (0x0008A336, "BL"), (0x0008A38E, "BL"), (0x0008A426, "BL"), (0x0008A476, "BL"), (0x0008A52C, "BL"), (0x0008A5A4, "BL"),),
        "unknown_sensor_stream_framework_candidate", "clean_room_reimplementation_owner_authorized",
    ),
    _function(
        0x0008A1C4, 12, ((0x0008A1C4, 0x0008A1D0, "51ac6a37c4ae28d2b48dc63082cb836e99847d0f4ae2a84fe7dc82013265fea2"),),
        "", "elapsed ticks since param via 0x8a1d0; callers sensor_stream_timer_poll_candidate + 0x8a5e4",
        ((0x0008A4F8, "BL"), (0x0008A504, "BL"), (0x0008A5EA, "BL"),),
        "unknown_sensor_stream_framework_candidate", "clean_room_reimplementation_owner_authorized",
    ),
    _function(
        0x0008A1AC, 12, ((0x0008A1AC, 0x0008A1B8, "3b9701a55ac883697f973ff1d183ee322758e45ac95f3b7fcf18d9548ce2cec6"),),
        "", "sensor_stream_object_create singleton wrapper (size 2, fixed descriptor)",
        ((0x00092332, "BL"), (0x000925A8, "BL"),),
        "unknown_sensor_stream_framework_candidate", "clean_room_reimplementation_owner_authorized",
    ),
    _function(
        0x00089D88, 12, ((0x00089D88, 0x00089D94, "fcb22841a241a4e99d0da0f59b4540a514cc540a58443e933d2881e7ea4864bb"),),
        "", "sensor_stream_object_create singleton wrapper (size 0xbc, fixed descriptor)",
        ((0x0009232A, "BL"), (0x000925A0, "BL"),),
        "unknown_sensor_stream_framework_candidate", "clean_room_reimplementation_owner_authorized",
    ),
    _function(
        0x00089EC8, 10, ((0x00089EC8, 0x00089ED2, "f27828d15e45c68731df631c44d2e79b3e46ffc5a0173dc7015b4f8542bb175b"),),
        "", "store 4-word descriptor to framework static 0x2001a1bc",
        (),
        "unknown_sensor_stream_framework_candidate", "clean_room_reimplementation_owner_authorized",
    ),
)

QUANTIZED_RUNTIME_FRONTIER_LT32_FUNCTIONS = (
    _function(
        0x00074C98, 22, ((0x00074C98, 0x00074CAE, "f9ddb54f040d814978a95043cc04bdc95bef8b000b6e6761616758f1fd96837b"),),
        "", "init 16-byte operator descriptor {u8 tag, float s0, 0, fn=quantized_runtime_float_add_executor 0x98edc}",
        ((0x00028AAC, "BL"), (0x000299C4, "BL"), (0x00043B0E, "BL"),),
        "unknown_shared_quantized_neural_runtime_candidate", "clean_room_reimplementation_owner_authorized",
    ),
    _function(
        0x00074CDC, 4, ((0x00074CDC, 0x00074CE0, "06936d0536d64e86c623270163a043c1b484bbc978af8fbf56cd1650cbfb6587"),),
        "", "return fn ptr to classified quantized_runtime_float_softmax_executor (0x5d244); GoMore/Goodix callers",
        ((0x00034174, "BL"), (0x0009908E, "BL"),),
        "unknown_shared_quantized_neural_runtime_candidate", "clean_room_reimplementation_owner_authorized",
    ),
    _function(
        0x00074BD8, 4, ((0x00074BD8, 0x00074BDC, "06936d0536d64e86c623270163a043c1b484bbc978af8fbf56cd1650cbfb6587"),),
        "", "return fn ptr 0x36dcc (code: movs r3,#2; b.w 0x3f6b4); same getter shape/callers as 0x74cdc",
        ((0x000340E4, "BL"), (0x0009909C, "BL"),),
        "unknown_shared_quantized_neural_runtime_candidate", "clean_room_reimplementation_owner_authorized",
    ),
    _function(
        0x00074A9C, 4, ((0x00074A9C, 0x00074AA0, "06936d0536d64e86c623270163a043c1b484bbc978af8fbf56cd1650cbfb6587"),),
        "", "return fn ptr 0x95b20 (vector-op prologue); exclusive GoMore callers 0x2874c/0x2966c",
        ((0x000289EC, "BL"), (0x000298F2, "BL"),),
        "unknown_shared_quantized_neural_runtime_candidate", "clean_room_reimplementation_owner_authorized",
    ),
)

SENSOR_HEAP_FRONTIER_LT32_FUNCTIONS = (
    _function(
        0x0002963A, 28, ((0x0002963A, 0x00029656, "d44b27b4ccac027db46637516443cc2dbcecb5799fdbbce0e46299b5b5e9e0c5"),),
        "", "allocate 0x40 via heap zero-allocate, memclr, clear flag bytes; caller 0x96a20 buffer-pool init",
        ((0x00096A34, "BL"),),
        "unknown_sensor_algorithm_heap_provider_candidate", "investigate_before_implementing",
    ),
    _function(
        0x0006631E, 28, ((0x0006631E, 0x0006633A, "dc1a2c9d237039972994f782f58ef5237a02ea2a9e0153b5a58a4872b16ce894"),),
        "", "buffer descriptor init {ptr,len,cap}, heap zero-allocate n when caller ptr null; Goodix caller 0x6d204",
        ((0x0006D33A, "BL"), (0x0006D354, "BL"),),
        "unknown_sensor_algorithm_heap_provider_candidate", "investigate_before_implementing",
    ),
    _function(
        0x00034A3C, 28, ((0x00034A3C, 0x00034A58, "094026a648946b49998f77d280136bd2f1f8b831172eb321392fe195e05f5e59"),),
        "", "allocate 0x18*n and 0x18 arrays via heap zero-allocate into record +8/+0x18; Goodix caller 0x6eb94",
        ((0x0006EBD4, "BL"),),
        "unknown_sensor_algorithm_heap_provider_candidate", "investigate_before_implementing",
    ),
    _function(
        0x00036C60, 26, ((0x00036C60, 0x00036C7A, "ec125ca352337ecf4ac66be8dd62b9e1667d6bbf9f692265427f3704786a8270"),),
        "", "context destroy: free *(p+0x300) then p via heap free; caller 0x28ec0",
        ((0x0002D45C, "B.W"),),
        "unknown_sensor_algorithm_heap_provider_candidate", "investigate_before_implementing",
    ),
    _function(
        0x00066304, 26, ((0x00066304, 0x0006631E, "ab400f4cc536158004effcd5060cc440dfd2fd3aefef3c13dd0e631e8e90ca49"),),
        "", "buffer descriptor init {ptr,len,cap}, heap zero-allocate n<<1 when caller ptr null; Goodix caller 0x72c48",
        ((0x00031928, "BL"), (0x00031940, "B.W"), (0x00072D08, "BL"), (0x00072D1C, "BL"), (0x00072D28, "BL"), (0x00072D34, "BL"), (0x00072D40, "BL"), (0x00072D4C, "BL"),),
        "unknown_sensor_algorithm_heap_provider_candidate", "investigate_before_implementing",
    ),
    _function(
        0x000662EA, 26, ((0x000662EA, 0x00066304, "c11603d6d30fc47bfd1b334a2a27964d251df48fe92d1b7ca7aa25503f57e69e"),),
        "", "buffer descriptor init {ptr,len,cap}, heap zero-allocate n<<2 when caller ptr null; caller 0x3727c",
        ((0x0005A642, "BL"), (0x0005A650, "BL"),),
        "unknown_sensor_algorithm_heap_provider_candidate", "investigate_before_implementing",
    ),
    _function(
        0x00073154, 22, ((0x00073154, 0x0007316A, "9264879287d2eb9f686fc8132344415057a8493f89de9cb6226eca65bd0ca792"),),
        "", "free record fields +4 and +0x10 via heap free-and-null 0x6628a; caller 0x37e8a teardown chain",
        ((0x00037EA0, "BL"),),
        "unknown_sensor_algorithm_heap_provider_candidate", "investigate_before_implementing",
    ),
    _function(
        0x00098FFC, 20, ((0x00098FFC, 0x00099010, "3e809d220f247ee7d182b4bed97fb7cf091078638dbc221ec4153ec34bbea380"),),
        "", "free fields +8/+0x18 via sensor_algorithm_heap_free_candidate; teardown-step helper",
        ((0x0006EB40, "BL"),),
        "unknown_sensor_algorithm_heap_provider_candidate", "investigate_before_implementing",
    ),
    _function(
        0x00028EAC, 20, ((0x00028EAC, 0x00028EC0, "064adb73e651b343ee42dfa6483152992e166d71abc62fe28f6d3c8b04a094dd"),),
        "", "guarded free of *p then null (heap free wrapper); caller 0x7cba0 teardown",
        ((0x0007CBAC, "BL"),),
        "unknown_sensor_algorithm_heap_provider_candidate", "investigate_before_implementing",
    ),
    _function(
        0x00056860, 20, ((0x00056860, 0x00056874, "b0cb86f708edbd85a43712ba243985763fd186a40771e547cdf09b095ca24032"),),
        "", "guarded free of *p via classified heap free-thunk 0x6dfc8; exclusive Goodix-candidate caller 0x6dad0",
        ((0x0006DAD8, "BL"), (0x0006DAE0, "BL"), (0x0006DAE8, "BL"), (0x0006DAF0, "BL"), (0x0006DAF8, "BL"), (0x0006DB00, "BL"), (0x0006DB08, "BL"), (0x0006DB10, "BL"), (0x0006DB18, "BL"), (0x0006DB20, "BL"), (0x0006DB28, "BL"),),
        "unknown_sensor_algorithm_heap_provider_candidate", "investigate_before_implementing",
    ),
    _function(
        0x00066276, 20, ((0x00066276, 0x0006628A, "4db22b038aae2d4023e3b8ddb34249f8aae78049dec05a52bad029ae48d396f9"),),
        "", "guarded free-and-null helper wrapping heap free; caller 0x93e3a",
        ((0x00093E4A, "BL"), (0x00093E52, "BL"),),
        "unknown_sensor_algorithm_heap_provider_candidate", "investigate_before_implementing",
    ),
    _function(
        0x0006628A, 20, ((0x0006628A, 0x0006629E, "2dcd3968ded70e0d94725cf10b1029fdae651dcea5e47e0238c26353e7b5f0b6"),),
        "", "guarded free-and-null helper wrapping heap free; callers Goodix 0x29bbc + 0x73154",
        ((0x00029C04, "BL"), (0x00029C14, "BL"), (0x00029C1C, "BL"), (0x00029C24, "BL"), (0x00029C2C, "BL"), (0x00029C34, "BL"), (0x0007315A, "BL"), (0x00073166, "B.W"),),
        "unknown_sensor_algorithm_heap_provider_candidate", "investigate_before_implementing",
    ),
    _function(
        0x0006629E, 20, ((0x0006629E, 0x000662B2, "a01605c411ec145f2922083f9f4924c225f4708defc59315be561de01a4d32dc"),),
        "", "guarded free-and-null helper wrapping heap free; caller 0x6cc60 (Goodix teardown)",
        ((0x0006CC92, "BL"), (0x0006CCA2, "BL"),),
        "unknown_sensor_algorithm_heap_provider_candidate", "investigate_before_implementing",
    ),
    _function(
        0x000662B2, 20, ((0x000662B2, 0x000662C6, "e651df5f86970912d567a0c1569c8297c3dd1950160fd305bc90253908450dca"),),
        "", "guarded free-and-null helper wrapping heap free; caller 0x91890",
        ((0x000918D0, "BL"),),
        "unknown_sensor_algorithm_heap_provider_candidate", "investigate_before_implementing",
    ),
    _function(
        0x000662C6, 20, ((0x000662C6, 0x000662DA, "7f8741b168a137e3ea9d3333fe9e0919429bc54fdc01170fc2f023fbe22e61a8"),),
        "", "guarded free-and-null helper wrapping heap free; callers Goodix 0x29bbc + teardown chain",
        ((0x00029C3C, "BL"), (0x00029C44, "BL"), (0x00029C4C, "BL"), (0x00029C54, "BL"), (0x00029C5C, "BL"), (0x00029C64, "BL"), (0x00029C6C, "BL"), (0x000304A6, "BL"), (0x000304AE, "BL"), (0x000304B6, "BL"), (0x000304BE, "BL"), (0x000304C6, "BL"), (0x000304D2, "B.W"), (0x000305F2, "BL"), (0x00033812, "BL"), (0x0006CC9A, "BL"), (0x0006CCAA, "BL"), (0x000918B8, "BL"), (0x000918C0, "BL"), (0x000918C8, "BL"),),
        "unknown_sensor_algorithm_heap_provider_candidate", "investigate_before_implementing",
    ),
    _function(
        0x00092B60, 12, ((0x00092B60, 0x00092B66, "17d53cbefa791994ec7de0fd738c57b797dc097989e376bb3bcfb88f8a3263ca"),),
        "", "byte-fill loop; called by sensor_algorithm_heap_initialize_candidate via thunk 0x92b58 (pool clearing)",
        (),
        "unknown_sensor_algorithm_heap_provider_candidate", "investigate_before_implementing",
    ),
    _function(
        0x0003757C, 12, ((0x0003757C, 0x00037588, "1796c50a94ea091623472e619a54ae97cdababecac43d779f12855ed9fb7b947"),),
        "", "guarded free returning 0 (heap free wrapper)",
        (),
        "unknown_sensor_algorithm_heap_provider_candidate", "investigate_before_implementing",
    ),
    _function(
        0x00036230, 12, ((0x00036230, 0x0003623C, "3c5c3f7c7b6372907e8d4648607f2344e06a09bd8e06e97d27ad9bf777521b38"),),
        "", "guarded free returning 0 (heap free wrapper); caller 0x3e6b0 context destroy",
        ((0x0003E6B8, "BL"),),
        "unknown_sensor_algorithm_heap_provider_candidate", "investigate_before_implementing",
    ),
    _function(
        0x00028EC0, 10, ((0x00028EC0, 0x00028EC6, "89721658f01821b4970b17af8ab7b2584326a1d083911ac674e5dfc6c4a4b108"),),
        "", "teardown step: tail-branch field +0x1c to heap-free path (b.w 0x2d45c -> 0x36c60)",
        ((0x0006EB64, "BL"),),
        "unknown_sensor_algorithm_heap_provider_candidate", "investigate_before_implementing",
    ),
    _function(
        0x000667C0, 6, ((0x000667C0, 0x000667C6, "7a3199c1f927f019c9b78b2df32890ad4157c2b0d497313a6a6c597bfede37c0"),),
        "", "tail free of *(p+4) via heap free; exclusive Goodix-candidate caller 0x29bbc",
        ((0x00029BC8, "BL"), (0x00029BD8, "BL"), (0x00029BE0, "BL"), (0x00029BE8, "BL"), (0x00029BF0, "BL"), (0x00029BF8, "BL"),),
        "unknown_sensor_algorithm_heap_provider_candidate", "investigate_before_implementing",
    ),
    _function(
        0x00092B58, 2, ((0x00092B58, 0x00092B5A, "570c0f7fa07ebb3c7ad727d0a0f5b7ffacd31fc86459c7cf35cad2c463cd56f8"),),
        "", "2-byte B thunk to 0x92b60; sole caller sensor_algorithm_heap_initialize_candidate",
        ((0x0006DFF4, "BL"),),
        "unknown_sensor_algorithm_heap_provider_candidate", "investigate_before_implementing",
    ),
)

ALL_FUNCTIONS = (
    R1_FRONTIER_LT32_FUNCTIONS
    + NORDIC_FRONTIER_LT32_FUNCTIONS
    + TOOLCHAIN_FRONTIER_LT32_FUNCTIONS
    + GOMORE_FRONTIER_LT32_FUNCTIONS
    + GOODIX_FRONTIER_LT32_FUNCTIONS
    + YHM_FRONTIER_LT32_FUNCTIONS
    + DEVICE_REGISTRY_FRONTIER_LT32_FUNCTIONS
    + SENSOR_STREAM_FRONTIER_LT32_FUNCTIONS
    + QUANTIZED_RUNTIME_FRONTIER_LT32_FUNCTIONS
    + SENSOR_HEAP_FRONTIER_LT32_FUNCTIONS
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
        for pointer_address in function["pointer_refs"]:
            pointer = struct.unpack_from(
                "<I", image, pointer_address - LOAD_BASE
            )[0]
            if pointer != entry + 1:
                raise ValueError(
                    f"frontier callback pointer changed: 0x{pointer_address:08x}"
                )
        rows.append({
            **{k: v for k, v in function.items() if k != "ranges"},
            "entry": f"0x{entry:08x}",
            "pinned_bytes": pinned,
            "omitted_bytes": int(function["size"]) - pinned,
            "callers": [
                {"callsite": f"0x{callsite:08x}", "kind": kind}
                for callsite, kind in callers
            ],
            "pointer_refs": [
                f"0x{address:08x}" for address in function["pointer_refs"]
            ],
        })
    return {
        "analysis": "sub-32-byte ownership frontier",
        "image_sha256": EXPECTED_IMAGE_SHA256,
        "function_count": len(rows),
        "function_bytes": sum(int(row["size"]) for row in rows),
        "pinned_bytes": sum(int(row["pinned_bytes"]) for row in rows),
        "omitted_bytes": sum(int(row["omitted_bytes"]) for row in rows),
        "r1_function_count": len(R1_FRONTIER_LT32_FUNCTIONS),
        "manual_supplement_count": sum(
            row["inventory"] == "manual_provenance_supplement"
            for row in rows
        ),
        "nordic_function_count": len(NORDIC_FRONTIER_LT32_FUNCTIONS),
        "toolchain_function_count": len(TOOLCHAIN_FRONTIER_LT32_FUNCTIONS),
        "gomore_function_count": len(GOMORE_FRONTIER_LT32_FUNCTIONS),
        "goodix_function_count": len(GOODIX_FRONTIER_LT32_FUNCTIONS),
        "yhm_function_count": len(YHM_FRONTIER_LT32_FUNCTIONS),
        "device_registry_function_count": len(DEVICE_REGISTRY_FRONTIER_LT32_FUNCTIONS),
        "sensor_stream_function_count": len(SENSOR_STREAM_FRONTIER_LT32_FUNCTIONS),
        "quantized_runtime_function_count": len(QUANTIZED_RUNTIME_FRONTIER_LT32_FUNCTIONS),
        "sensor_heap_function_count": len(SENSOR_HEAP_FRONTIER_LT32_FUNCTIONS),

        "functions": rows,
        "safety": {
            "biometric_or_health_algorithm_reimplemented": False,
            "yhm_wire_or_register_body_recreated": False,
            "unidentified_framework_recreated": False,
            "time_calendar_provider_recreated": False,
            "withheld_dispatch_surface_enabled": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    print(json.dumps(summarize(parser.parse_args().image), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
