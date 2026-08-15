#!/usr/bin/env python3
"""Pin and source-route the 151-function 32...63-byte R1 frontier.

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


R1_FRONTIER_32_63_FUNCTIONS = (
    _function(
        0x000913FC, 62, ((0x000913FC, 0x0009143A, "2f8d0bb636bcf21f418de610c4e73d10f13ad83c06387fec58063beaf4f8072e"),),
        "r1_glasses_tag_frame_send", "Builds a 6-byte tagged frame and dispatches it to the glasses link via r1_ble_tx_queue_dispatch_type0",
        ((0x00032150, "BL"), (0x00046282, "BL"), (0x000462EE, "BL"), (0x0004C448, "BL"), (0x000913F4, "B.W"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00082B96, 62, ((0x00082B96, 0x00082BD4, "5ae822891068bdbd561241191d82f503441101070438fed90ae8a4185ef733c3"),),
        "r1_protocol_send_flag_inv", "Typed protocol send wrapper over r1_protocol_send_response with the ^1 flag word",
        ((0x00083C9A, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00062546, 62, ((0x00062546, 0x00062584, "82372506b04e81d1fc4e28404df38f9f8171a3a2455f9c971346b8e9ae3ebf90"),),
        "r1_legacy_cmd_battery_type_reply", "Legacy command handler: resolves battery/state byte and replies through the bounded reply sender",
        ((0x0004E32A, "BL"), (0x00062604, "B.W"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0004C8F8, 62, ((0x0004C8F8, 0x0004C926, "3fbc5eccace910d7e7c039763e9c1df6b9f8e0b716030121821ba0fe9fa38ee5"),),
        "r1_advertising_stop_guard", "Advertising-stop wrapper: SVC 0x74, state sanity check with fatal logger, status record publish",
        ((0x00045280, "BL"), (0x00045A24, "BL"), (0x0007F438, "BL"), (0x00091FDA, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0007C9A8, 60, ((0x0007C9A8, 0x0007C9E4, "2e33ef487faf80604b8fdb28c5f9ec40f4371c020284533b61a996e7e86b3b48"),),
        "r1_kv_nv_r1_string_set_b", "kv.bin nv_r1 class bounded string setter (30-byte cap) via the KV read/modify/write primitives",
        ((0x00062514, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00073968, 60, ((0x00073968, 0x000739A4, "9b8c40ba342144b326cb9af0905b442f78c445bb86eb7b9ec6c50b3267da5606"),),
        "r1_kv_class_write", "kv.bin class write primitive: length-checked record store under the class ops lock",
        ((0x00073628, "BL"), (0x000736FA, "BL"), (0x00073744, "BL"), (0x00073824, "BL"), (0x00073858, "BL"), (0x00073898, "BL"), (0x000738E0, "BL"), (0x00073918, "B.W"), (0x0007BBAE, "BL"), (0x0007BBDA, "BL"), (0x0007C118, "BL"), (0x0007C126, "BL"), (0x0007C13A, "BL"), (0x0007C682, "BL"), (0x0007C690, "BL"), (0x0007C8D2, "BL"), (0x0007C900, "BL"), (0x0007C92A, "BL"), (0x0007C958, "BL"), (0x0007C996, "BL"), (0x0007C9D8, "BL"), (0x0007CA02, "BL"), (0x0007CA34, "BL"), (0x0007CA5E, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00073868, 60, ((0x00073868, 0x000738A4, "c2cb55acf666e6e0efbfcb7e783385f40d54d06196ef8ca488817e3670f58d21"),),
        "r1_kv_dev_info_flag0_word_set", "kv.bin dev_info class bit-0 flag plus word read/modify/write",
        ((0x0008403E, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00073710, 60, ((0x00073710, 0x0007374C, "d6f1b90c70a386c34b5351e59786145c87aa2aaac91259bc733f58055c47320d"),),
        "r1_kv_dev_info_fields_set", "kv.bin dev_info class word plus packed bitfield read/modify/write",
        ((0x0003D912, "BL"), (0x0004F4FA, "BL"), (0x0008444E, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00062412, 60, ((0x00062412, 0x0006244E, "05acb98b277d6d756ef3ee74f721bcce404ce205f89e8c9f7c5f3a0a8f3069a9"),),
        "r1_legacy_cmd_mac_compare_reply", "Legacy command handler: 6-byte address compare against the device-info record, boolean reply",
        ((0x0004E334, "BL"), (0x000626EE, "B.W"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0007C968, 58, ((0x0007C968, 0x0007C9A2, "f916aca08ce7222027f5fec687c7f304c78ad6fbbae869156d87dbd9372da270"),),
        "r1_kv_nv_r1_string_set_a", "kv.bin nv_r1 class bounded string setter (30-byte cap), second field offset",
        ((0x0006246E, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0005CB6C, 58, ((0x0005CB6C, 0x0005CBA6, "ffacfcaa8ae84438bf99ba2712cd868a384b7f197cad833b9dc2f1d7c806d47f"),),
        "r1_module_init_table_run", "Boot init-table runner over three function-pointer ranges; the flash table contains R1 adapter/registrar entries",
        ((0x0004E1E8, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0004E21C, 58, ((0x0004E21C, 0x0004E256, "d434ca38982978e07aa39d70563c98837addbacbbd8913c855062d5372a8b2a0"),),
        "r1_ear_worn_state_notify", "Sends the fixed 4-byte {0,1,0x96,0} notification through r1_ble_tx_queue_dispatch_type2",
        ((0x00045450, "BL"), (0x000458FE, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0008287C, 56, ((0x0008287C, 0x000828B4, "23fb446f9c36374289a6252c09aff9af21dfd6ebddc3a18722e2fd252b330ec2"),),
        "r1_protocol_send_flag_set_c", "Typed protocol send wrapper over r1_protocol_send_response with the |3 flag word",
        ((0x00083D2C, "BL"), (0x00083D40, "BL"), (0x00083E3A, "BL"), (0x00083FDA, "BL"), (0x000843EE, "BL"), (0x00084402, "BL"), (0x000844CE, "BL"), (0x0008450A, "BL"), (0x000845BC, "BL"), (0x00084728, "BL"), (0x0008486E, "BL"), (0x00084A3A, "BL"), (0x00084A98, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00082844, 56, ((0x00082844, 0x0008287C, "ed8d8ced19ff37a636c4bac1cd4b640b73baf870d14d175365a6ef368b5de51a"),),
        "r1_protocol_send_flag_set_b", "Typed protocol send wrapper, identical body to 0x0008280C/0x0008287C (paired instantiation)",
        ((0x00082C68, "BL"), (0x00082CAE, "BL"), (0x00082CF2, "BL"), (0x00082D38, "BL"), (0x00082D7E, "BL"), (0x00082DE0, "BL"), (0x00082E1C, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0008280C, 56, ((0x0008280C, 0x00082844, "fcecb20f9282e2cbd77639a9c2582af95919440423a7ea4a311d2fccb914e263"),),
        "r1_protocol_send_flag_set_a", "Typed protocol send wrapper over r1_protocol_send_response used by five R1 event posters",
        ((0x0008356E, "BL"), (0x000835FC, "BL"), (0x0008368A, "BL"), (0x000836F8, "BL"), (0x00083762, "BL"), (0x000837F0, "BL"), (0x00083966, "BL"), (0x000839A8, "BL"), (0x00083C56, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00073930, 52, ((0x00073930, 0x00073964, "e403ecf7a8d7a54c94bc191402c8a31a1099063da2483442e2c5a71fb5483b09"),),
        "r1_kv_class_read", "kv.bin class read primitive: length-checked record load under the class ops lock",
        ((0x000735EE, "BL"), (0x00073612, "BL"), (0x000736A4, "BL"), (0x000736C4, "BL"), (0x00073720, "BL"), (0x0007375E, "BL"), (0x00073784, "BL"), (0x000737A8, "BL"), (0x000737D8, "BL"), (0x0007380E, "BL"), (0x00073842, "BL"), (0x00073878, "BL"), (0x000738B8, "BL"), (0x00073900, "B.W"), (0x0007B658, "BL"), (0x0007B6A2, "BL"), (0x0007B6B8, "BL"), (0x0007B9D6, "BL"), (0x0007B9F8, "BL"), (0x0007BA14, "BL"), (0x0007BA30, "BL"), (0x0007BA4E, "BL"), (0x0007BA88, "BL"), (0x0007BACE, "BL"), (0x0007BAEA, "BL"), (0x0007BB10, "BL"), (0x0007BB2A, "BL"), (0x0007BB4E, "BL"), (0x0007BB66, "BL"), (0x0007BB86, "BL"), (0x0007BBA0, "BL"), (0x0007BBCC, "BL"), (0x0007BE12, "BL"), (0x0007BE1C, "BL"), (0x0007BE26, "BL"), (0x0007C64E, "BL"), (0x0007C658, "BL"), (0x0007C8BE, "BL"), (0x0007C8F2, "BL"), (0x0007C91E, "BL"), (0x0007C94A, "BL"), (0x0007C97E, "BL"), (0x0007C9BE, "BL"), (0x0007C9F4, "BL"), (0x0007CA1E, "BL"), (0x0007CA52, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x000737C8, 52, ((0x000737C8, 0x000737FC, "097ef364d332ff61b41a9d36ed00d177ca75af5fdf16833f39014ec7c00e886e"),),
        "r1_kv_dev_info_pair_get", "kv.bin dev_info class two-word-plus-short pair getter",
        ((0x0004CB6A, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x000924C0, 50, ((0x000924C0, 0x000924F2, "cca20557110adcc080e287f2ab267b486e2f2dd5782de8e82e43bd269f48d23f"),),
        "r1_event_bus_enqueue", "Event-record queue put plus 0x400000 event-flag set; sole caller is the R1 private event publisher",
        ((0x0008D966, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0007CA10, 48, ((0x0007CA10, 0x0007CA40, "6b9f05ea09a387c295ed4d32e8b5208b991fca0ebe54a3bebd5c9513c62bc463"),),
        "r1_kv_nv_r1_addr_set", "kv.bin nv_r1 class 6-byte address field setter",
        ((0x00062426, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00073834, 48, ((0x00073834, 0x00073864, "18434d69194f14c10acb0fc9b74ca9e34cb39f59d4c4bfac41b002e5f5d007a6"),),
        "r1_kv_dev_info_bit2_set", "kv.bin dev_info class bit-2 flag read/modify/write",
        ((0x0004538E, "BL"), (0x00046040, "BL"), (0x000844D4, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00073800, 48, ((0x00073800, 0x00073830, "54d98394fa19b74ea1e986d8e79d6610ff07d5da41124849904a41e13477738e"),),
        "r1_kv_dev_info_bit1_set", "kv.bin dev_info class bit-1 flag read/modify/write",
        ((0x0008461A, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00050E1C, 48, ((0x00050E1C, 0x00050E4C, "7792537a1c203194c8c59fb0b188e9b50f795ab502373c4f80fe9ea6a6694556"),),
        "r1_gxt310_temp_average_read", "Dual GXT310 read orchestration with fixed delay and averaging; R1 glue around the gated vendor primitives",
        ((0x00062D2C, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00050944, 48, ((0x00050944, 0x00050974, "22b8a1396a5a7703fef878c01a6aed365eee13ab850a14ada78861e4babfdd6c"),),
        "r1_ppg_device_bind", "Board device binding for i2c_4, ppg_int, ppg_reset_en through the registry find-by-name",
        ((0x00050396, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0007C8B0, 46, ((0x0007C8B0, 0x0007C8DE, "5f634afb4d3ca5f37c4935f06b014d9defb771bd1f06db34f071c80ec2ca5f69"),),
        "r1_kv_nv_r1_field_set_a", "kv.bin nv_r1 class 6-byte field setter; called from the R1 motion adapter",
        ((0x0006F2AC, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x000510D8, 46, ((0x000510D8, 0x00051106, "6d7d51dae7516a12f1208598056bde8d3743d0471bb891d23ffd035a251f0dba"),),
        "r1_gxt310_id_pair_read", "Dual GXT310 identification-read orchestration into a caller buffer; R1 glue around the gated vendor primitives",
        ((0x000462FC, "BL"), (0x0004F132, "BL"), (0x00062C64, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00050ECC, 46, ((0x00050ECC, 0x00050EFA, "eba2786bceafb682f4b36f217bde772d9f6622660e1185f66a8210f6d034b1f1"),),
        "r1_gxt310_self_check", "Dual GXT310 fixed-pattern (0x50) self-check; sole caller is the pinned R1 temperature hardware check",
        ((0x0004E91C, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00050384, 46, ((0x00050384, 0x000503B2, "9d98f0ab7534b07a9d2d26da955eeea6623dbaec1e427642ac3d3f610bd43a53"),),
        "r1_peripheral_module_init", "Peripheral/board init orchestrator over ten subsystem initializers; called from the R1 main entry",
        ((0x00075FA4, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0008D858, 44, ((0x0008D858, 0x0008D884, "6c5aa5ea22f943cc7bcd4690b4da96735031c61d3012ea407e2cbb011966fb47"),),
        "r1_hrv_latest_sample_get", "HRV latest-sample fill composed from the pinned R1 HRV sample accessor",
        ((0x0008BA0C, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00082F48, 44, ((0x00082F48, 0x00082F74, "e1a1790215d26b83fe8085334dd0a13e3e4ed1022908c96881cbfd9d29c6470b"),),
        "r1_ack_record_register_typed", "Typed wrapper over r1_ack_record_register with the shared record constant",
        ((0x0008353E, "BL"), (0x000835CC, "BL"), (0x0008365A, "BL"), (0x00083732, "BL"), (0x000837C0, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00080E74, 44, ((0x00080E74, 0x00080EA0, "71cc1eb87b376f78acffc461051396d0e53864ac55066ead555974f4a7d980a3"),),
        "r1_analog_init_delay", "Registry device open plus 200x64,000-cycle Nordic delay pulse; the recovered analog init adapter",
        ((0x00050754, "B.W"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00073798, 44, ((0x00073798, 0x000737C4, "1a823323c138b84eaa9edcbc190c032239c8ec56a85f86657ae9b7c99ea6ab15"),),
        "r1_kv_dev_info_flag_word_get", "kv.bin dev_info class flag-bit plus word getter",
        ((0x00049404, "BL"), (0x00083F52, "BL"), (0x00083FE2, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00051310, 44, ((0x00051310, 0x0005133C, "7dfa924c5b251ae682ba6855b872f60250dc55355d4af6c717fe86422e0618ed"),),
        "r1_touch_device_bind", "Board device binding for i2c_0, touch_rdy_out, touch_rdy_in through the registry find-by-name",
        ((0x0005039E, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00051260, 44, ((0x00051260, 0x0005128C, "5e9b5b48604f922826e4647a02303d5e5cb678c33a24acf99ece5a973508bf2f"),),
        "r1_gxt310_temp_pair_read", "Dual GXT310 temperature read into out-parameters; R1 glue called from an R1 product path",
        ((0x00096B26, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0008E524, 42, ((0x0008E524, 0x0008E54E, "b01d4a25fa010876f2062d3510c439157844837373abfa971477ddd7ce4711a2"),),
        "r1_spo2_latest_sample_get", "SpO2 latest-sample fill composed from the pinned R1 SpO2 sample accessor",
        ((0x0008B9B2, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0008D6AC, 42, ((0x0008D6AC, 0x0008D6D6, "703740be283318e04598147a2b1a46c57ecf1ae4b6f752cc023ec7b6f9dc746c"),),
        "r1_hr_latest_sample_get", "HR latest-sample fill composed from the pinned R1 HR sample accessor",
        ((0x0008B962, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00073604, 42, ((0x00073604, 0x0007362E, "856a46f03318af50e9d97310e2a948c7c049779b93f0934b49dc42fd772d5eea"),),
        "r1_kv_health_set", "kv.bin health class 12-byte record read/modify/write",
        ((0x0006C694, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x000628CC, 42, ((0x000628CC, 0x000628F6, "c4dd3bcae2194f00834ed97a056c3afd7c29285866c3228528625568261b154f"),),
        "r1_legacy_cmd_ring_size_reply", "Legacy command handler: optional r_size write then state read and bounded reply",
        ((0x0004E37C, "BL"), (0x0006266A, "B.W"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00050D00, 42, ((0x00050D00, 0x00050D2A, "0c13aae02eb6d8bdd8b277cf0866afbef146d0180a5053d7247dfaa631d562c3"),),
        "r1_battery_raw_to_percent", "Fixed-constant battery raw-to-percentage conversion; recovered R1 conversion behavior",
        ((0x00050D34, "BL"), (0x00096B02, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0003E884, 42, ((0x0003E884, 0x0003E8AE, "d2a93d5f95f68fae264213aa76e0d7254e7d452726368616883bb81672a96f39"),),
        "r1_ble_error_is_benign", "Whitelist predicate over BLE/SD error codes; called only from the R1 Nordic SDK adapter",
        ((0x0003E7DA, "BL"), (0x0003E7F2, "BL"), (0x0003E85C, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0007C93C, 40, ((0x0007C93C, 0x0007C964, "2f52a1951c54c9900aed46699a2d73a690fe9e59f31938e678ac68be3ab36818"),),
        "r1_kv_nv_r1_byte_set_c", "kv.bin nv_r1 class byte field setter; called from R1 command paths",
        ((0x00062940, "BL"), (0x0006295A, "BL"), (0x000629B0, "BL"), (0x00062DC2, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0007C8E4, 40, ((0x0007C8E4, 0x0007C90C, "1e2d7d844232a2ee2ad739a45bfbc9743fda2ab391cbe510818ce59e657384b3"),),
        "r1_kv_nv_r1_byte_set_a", "kv.bin nv_r1 class byte field setter; called from R1 command paths",
        ((0x0003CD6E, "BL"), (0x00048BE6, "BL"), (0x00062404, "BL"), (0x000815AE, "B.W"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00062C90, 40, ((0x00062C90, 0x00062CB8, "15d0263c2da0ba558077c02938083adccbf36c649a18b96868ae0d77f4585e38"),),
        "r1_factory_stream_reregister", "Unregister-then-register of the 'factory' sensor stream against the stream framework",
        (),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0004E1E4, 40, ((0x0004E1E4, 0x0004E1F6, "934ee9aad46b6130a4fc6782f698176be05bc294c5d6f7f1213e8778c83a30db"),),
        "r1_boot_ctor_run", "IRQ-guarded init-table runner chained with 0x0005CB6C; called from the R1 main entry",
        ((0x00075FA0, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0003ED0C, 40, ((0x0003ED0C, 0x0003ED34, "0753d9f3301e0b2076e81e6665db815831e710c50ccf021f34257cf79ac45a7f"),),
        "r1_ep_sector_erase_if_dirty", "Reads a flash byte and erases the 0x1000 sector when not erased; called from the pinned R1 ep export flush",
        ((0x0003ECD0, "BL"), (0x0003ECFC, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0003E8B4, 40, ((0x0003E8B4, 0x0003E8DC, "9aee1c29657108809be1684aec20202fb879f9f6b4c381e7e2d3606990b290ef"),),
        "r1_queue_flush_bounded", "Bounded CMSIS message-queue drain used by the R1 log/ep flush path",
        ((0x0003E8F6, "B.W"), (0x00052B84, "BL"), (0x00052B90, "B.W"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0003D7CC, 40, ((0x0003D7CC, 0x0003D7F4, "f9f470653da689608b37b2f06da2cd44ed4211cd4c3c5d86a61e3b5b3376ed5a"),),
        "r1_deferred_call_post", "Heap-packs two words and defers to a fixed function through the FreeRTOS pend-function call",
        ((0x0004F760, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00090FAC, 38, ((0x00090FAC, 0x00090FD2, "7be912e0c9d7b9ac0385a6c209e9cd3a73de8a1b85f705b1cc72d556b3e58c8e"),),
        "r1_factory_acc_listener_register", "Registers the 'factory' listener on the 'acc' stream with the R1 motion-adapter callback",
        ((0x00062A3A, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0007CA44, 38, ((0x0007CA44, 0x0007CA6A, "c63130a1ac6516d3425fe664b80a139e00b37a79e31d7c15181e510ae4f213a2"),),
        "r1_kv_nv_r1_word_set_b", "kv.bin nv_r1 class word field setter",
        ((0x00062C24, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0007C910, 38, ((0x0007C910, 0x0007C936, "7e6fdcee0a3c77a857a568de7816bfd60ed3c8fa4584f65a06de08d29d0becbf"),),
        "r1_kv_nv_r1_word_set_a", "kv.bin nv_r1 class word field setter; called from R1 command paths",
        ((0x0003CD5C, "BL"), (0x00048BEE, "BL"), (0x00048C8A, "BL"), (0x0006240A, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00049E2C, 38, ((0x00049E2C, 0x00049E52, "33e63e4a7ec817181fdf48af623aa9bbf049dff6ee879e85c6485f3122c932df"),),
        "r1_hrv_timing_state_tick", "HRV timing state machine; invokes the pinned r1_hrv_timing_start_plan on the armed flag",
        (),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00048BA4, 38, ((0x00048BA4, 0x00048BCA, "5da5281b6504e8373b92acc295c3f0a9016fc9301836da09b8d67ad0822dbdce"),),
        "r1_wear_state_buffer_fill", "Composes pinned R1 state getters and conditionally fills a 0x7800-byte buffer",
        ((0x00092322, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00084C98, 36, ((0x00084C98, 0x00084CBC, "063c1224eaf715bf692cba2ebe1b04cf2ad7c51fc466798d0c4acd62e0f55911"),),
        "r1_ble_event_dispatch", "Indirect BLE event dispatch through the pinned R1 event-table lookup",
        ((0x00083216, "B.W"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00084C5E, 36, ((0x00084C5E, 0x00084C82, "b58b72cd8549277a98aad5ac3aee823454e11e4107efc733c4708f25407fab8b"),),
        "r1_protocol_send_checked", "Handle-validated protocol send wrapper returning a status pair",
        ((0x00083DDC, "BL"), (0x00083FBA, "BL"), (0x00084366, "BL"), (0x000845A8, "BL"), (0x00084896, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00083C62, 36, ((0x00083C62, 0x00083C86, "a2452f417276275f01e2f4ffe99487eaffec15e8f12a220bc23c02b4c9b673cc"),),
        "r1_phone_cmd_send_op3", "Phone-link typed command sender (opcode 3) over the R1 connection handle",
        ((0x000437E8, "BL"), (0x00084B96, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x000839DA, 36, ((0x000839DA, 0x000839FE, "e8c771d6d933ba0507c626641078983817ed432cbc1b5070fbe056a2b676a6b1"),),
        "r1_phone_cmd_send_op8", "Phone-link typed command sender (opcode 8) over the R1 connection handle",
        ((0x00045AF2, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x000838BA, 36, ((0x000838BA, 0x000838DE, "6b7e341052267787e0aeed00bc0cf8e267a736accc0e83e8a607f9788ceb3574"),),
        "r1_phone_cmd_send_op11", "Phone-link typed command sender (opcode 0xB) over the R1 connection handle",
        ((0x00083EE4, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00083896, 36, ((0x00083896, 0x000838BA, "8e5145b9482eadf36edf4a6a99ac4143462abba7ff70adce381878233c6e2898"),),
        "r1_phone_cmd_send_op1", "Phone-link typed command sender (opcode 1) over the R1 connection handle",
        ((0x000834C2, "BL"), (0x00083E20, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0007C9E8, 36, ((0x0007C9E8, 0x0007CA0C, "261cf8a7c98c769f6a23b4916121171d3a63c4125de33bf7ea1d6573069b9815"),),
        "r1_kv_r_size_set", "kv.bin r_size class 1-byte record read/modify/write",
        ((0x000628F0, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0007BBC0, 36, ((0x0007BBC0, 0x0007BBE4, "eee1d296709cc16ab3d3201fee4f24d737422815d0af1c27b1b5534a035b2fc1"),),
        "r1_kv_power_field_set", "kv.bin power class 2-byte field read/modify/write",
        ((0x0006288A, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0007BB94, 36, ((0x0007BB94, 0x0007BBB8, "b5a8512b986d4c406e278dff6cdb725a33bc65f6033623d3c0e7351373636998"),),
        "r1_kv_power_byte_set", "kv.bin power class 1-byte field read/modify/write",
        ((0x00062856, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00073750, 36, ((0x00073750, 0x00073774, "4b581bdfcd89ec9aa1cbc931b046527cd16b61befa0edb2fdc2cabbebceb7b54"),),
        "r1_kv_dev_info_bit_get", "kv.bin dev_info class single flag-bit getter",
        ((0x0006A78C, "BL"), (0x00084548, "BL"), (0x00084608, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00062584, 36, ((0x00062584, 0x000625A8, "156c4e80382a9139bef4e845937adcb2da87ada60250343822ea8554c071e7ce"),),
        "r1_legacy_cmd_version_reply", "Legacy command handler: replies with the compiled version strings through the bounded reply sender",
        ((0x0004E2F8, "BL"), (0x000626B8, "B.W"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00046A44, 36, ((0x00046A44, 0x00046A68, "fc0fde2b734b6b8892f7ea22d0df5f0447caffbba99ecb46367e4dc0c5129007"),),
        "r1_thread_create_g", "osThreadNew wrapper storing the handle and halting on failure; R1 startup thread creation",
        (),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00046924, 36, ((0x00046924, 0x00046948, "8bd351917c64b3396c2c15fffeef8fc80f029142ad884d992f92df1d05624e73"),),
        "r1_thread_create_f", "osThreadNew wrapper storing the handle and halting on failure; R1 startup thread creation",
        (),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0004509C, 36, ((0x0004509C, 0x000450C0, "2c96e0058530526b8ffac00e87b16b34fdd90fc46e8f50901cae538b52597a7e"),),
        "r1_thread_create_e", "osThreadNew wrapper storing the handle and halting on failure; R1 startup thread creation",
        (),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00045054, 36, ((0x00045054, 0x00045078, "3e876c194674d4853eada330d73b81d46c3c6bf9e4ff794b8303b3459f15cb01"),),
        "r1_thread_create_d", "osThreadNew wrapper storing the handle and halting on failure; R1 startup thread creation",
        (),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00044F20, 36, ((0x00044F20, 0x00044F44, "c471594bd62dd7d49d655f99ae1b4836a31dee93f58453efd8cfcfd87b6804bc"),),
        "r1_thread_create_c", "osThreadNew wrapper storing the handle and halting on failure; R1 startup thread creation",
        (),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00044EF0, 36, ((0x00044EF0, 0x00044F14, "ce158a021cb7a734fd680229c81cad5d5d9e78f22a58595e7f98da847bfb5788"),),
        "r1_thread_create_b", "osThreadNew wrapper storing the handle and halting on failure; R1 startup thread creation",
        (),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00043B8C, 36, ((0x00043B8C, 0x00043BB0, "bbfce44a4b823c0e07bd3d696f415527c110034c5f156ac98353cc7166f149ae"),),
        "r1_thread_create_a", "osThreadNew wrapper storing the handle and halting on failure; R1 startup thread creation",
        (),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0008967C, 34, ((0x0008967C, 0x0008969E, "95e39ea8a8f009fb4ce53a0eb2062d2bb3496c73413b09685b7d468707d07ba4"),),
        "r1_legacy_bounded_reply_send", "Legacy bounded reply sender over the R1 glasses connection handle (briefing-identified)",
        ((0x0004E214, "B.W"), (0x0006228A, "BL"), (0x000622B4, "B.W"), (0x000623FA, "B.W"), (0x00062442, "BL"), (0x0006248C, "BL"), (0x000624C4, "B.W"), (0x000624F0, "B.W"), (0x00062534, "BL"), (0x00062576, "B.W"), (0x000625A4, "B.W"), (0x0006272A, "B.W"), (0x0006283C, "B.W"), (0x0006289C, "B.W"), (0x000628C8, "B.W"), (0x000628EA, "B.W"), (0x00062948, "BL"), (0x00062962, "BL"), (0x0006297A, "BL"), (0x000629C6, "B.W"), (0x00062A36, "B.W"), (0x00062B32, "BL"), (0x00062BA8, "B.W"), (0x00062C1E, "B.W"), (0x00062C5A, "B.W"), (0x00062C70, "B.W"), (0x00062C8C, "B.W"), (0x00062CE2, "B.W"), (0x00062CF8, "B.W"), (0x00062D0E, "B.W"), (0x00062D24, "B.W"), (0x00062D3A, "B.W"), (0x00062D50, "B.W"), (0x00062D66, "B.W"), (0x00062D6E, "BL"), (0x00062DA0, "B.W"), (0x00062DB6, "BL"), (0x00062DDA, "BL"), (0x0006A86C, "B.W"), (0x0006F2D8, "BL"), (0x0006F374, "BL"), (0x0008164A, "BL"), (0x00092C54, "B.W"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0003E8FC, 34, ((0x0003E8FC, 0x0003E91E, "431ecbde57ff5efffa9d5b9050082d9cca2c83720ee21fff58e14a7bda82b827"),),
        "r1_per_link_value_select", "Selects a per-link stored value by glasses/phone connection handle",
        ((0x0003E7B6, "BL"), (0x00052B46, "BL"), (0x00052B5E, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00083C86, 32, ((0x00083C86, 0x00083CA6, "166e7c2d37d08393aa6297244c2420b9bb07da134fa55544fb6197e2878d3fa4"),),
        "r1_phone_link_ready_query", "Phone-link fixed-parameter protocol query returning a status pair",
        ((0x0008475E, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00073694, 32, ((0x00073694, 0x000736B4, "cecd7f3413612d182834754332fb5689c03123c4e0dc0ab39cc6260b0b3c3121"),),
        "r1_kv_dev_info_word_pair_get", "kv.bin dev_info class 8-byte word-pair getter",
        ((0x00091306, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x000735E0, 32, ((0x000735E0, 0x00073600, "110a8c89e27c9c139b86ba3d11b3fc54a54616f7e29531deea4c9f693d9c0d24"),),
        "r1_kv_health_get", "kv.bin health class 12-byte record getter",
        ((0x000425BC, "BL"), (0x0006AC00, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0005678C, 32, ((0x0005678C, 0x000567AC, "f85045c61e4ab18337b3422c07e592b0cc1092ce1361e89dfb89d0b411803108"),),
        "r1_constant_time_compare", "XOR-accumulate constant-time buffer compare used by the R1 legacy command handlers",
        ((0x0006247E, "BL"), (0x00062526, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x000502C4, 32, ((0x000502C4, 0x000502E4, "a7fba9d901b78695afdec7c36f540844791f228a6546937283d9cf8be52a66dd"),),
        "r1_led_ldo_device_bind", "Board device binding for ppg_led_en and touch_ldo_en through the registry find-by-name",
        ((0x00050386, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0004E1F8, 32, ((0x0004E1F8, 0x0004E218, "973761544e286a26b74ad2a6de4df420c5159d3efd3ef4ca8649ba44ee01e22e"),),
        "r1_legacy_cmd_cancel_event_reply", "Legacy command handler: cancels the delayed event and replies through the bounded reply sender",
        ((0x0004E386, "BL"), (0x00062740, "B.W"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0004C64C, 32, ((0x0004C64C, 0x0004C66C, "4e9607d4e249f9bb6f75efc2d9cc14410d7da83c9a7b5e323a576ee19ea2b7c5"),),
        "r1_raw_hr_stream_teardown", "Unregisters the 'raw_hr' sensor stream and frees its object; twin of the pinned R1 health/sensor init",
        (),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0003E8DC, 32, ((0x0003E8DC, 0x0003E8FC, "b9fb952c3b1cac66dd6c729fd8782a372271d1ddae94c9cc8363fd7f744bc570"),),
        "r1_queue_flush_wait", "CMSIS queue take-with-retry plus bounded drain used by the R1 log/ep flush path",
        ((0x00052B68, "B.W"), (0x00052B6E, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
)

GOMORE_FRONTIER_32_63_FUNCTIONS = (
    _function(
        0x00072B34, 58, ((0x00072B34, 0x00072B6E, "54c507a2fdac2057c5baf17d100a8522101906f1905ead2a12d9efa1ed1754b2"),),
        "", "Provider state predicate with a 300-tick window over offsets 0xA4/0xA8/0xA9; reached only from the gated GoMore statistics path",
        ((0x0005C23A, "BL"),),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x0006AB88, 58, ((0x0006AB88, 0x0006ABC2, "2ff97992dc73d02a97d5eb91e726c742915db7b3d57a8216009a5f751a0151e6"),),
        "", "Reads FICR device id, formats the 24-character %08x%08x%08x key string, or copies a cached provider blob; called from pinned GoMore pKey/auth scopes",
        ((0x0006B29E, "BL"), (0x00083E78, "BL"), (0x0008EA72, "BL"),),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x0008ECD8, 56, ((0x0008ECD8, 0x0008ED10, "9bc62d3e70012ebf52c4ea8faf751ca2d393223462ade011a88d0a4fd5ceb0af"),),
        "", "Per-slot state-byte transition logic at record offset 0x3845; all eight callsites are the pinned GoMore mode/profile setter",
        ((0x00091712, "BL"), (0x00091722, "BL"), (0x0009172E, "BL"), (0x0009173E, "BL"), (0x0009174A, "BL"), (0x0009175A, "BL"), (0x0009176A, "BL"), (0x00091774, "BL"),),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x0006AD28, 56, ((0x0006AD28, 0x0006AD60, "b82c7b08f1dc6fb87ebf19aa0249ae9909c0c6d7ec3a2b006267aa37afc3d04f"),),
        "", "Copies the 0x40-byte provider key blob from cache or the gated 0x0006AD80 flash path; callers are pinned GoMore pKey scopes",
        ((0x0006B2EC, "BL"), (0x0008EACA, "BL"),),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x000726C4, 54, ((0x000726C4, 0x000726FA, "bc491603f45ccd24f595a5f86058c5f7a29fd72b3a819ea8e065b1560d9f736f"),),
        "", "0x20-byte staged copy into the gated GoMore helper 0x00069644; sole caller is gated GoMore 0x00067BBC",
        ((0x00067C14, "BL"),),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x00062000, 48, ((0x00062000, 0x00062030, "99232721b603e900000b6e54705228163c5ff86570bd8b41a8539a6d31a12614"),),
        "", "Float-array mean; reached from gated GoMore scopes, matching the admitted sliding-window-mean precedent",
        ((0x0006209A, "BL"), (0x00064416, "BL"), (0x0006885A, "BL"), (0x00068BBE, "BL"),),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x000760EC, 46, ((0x000760EC, 0x0007611A, "f4ab2ecf7aa3f462eecf6dece16d74dfabe8264295d44d8f360456cf756ce49f"),),
        "", "Float-array argmax; sole caller is gated GoMore 0x00060680",
        ((0x000608BA, "BL"),),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x0004C37C, 46, ((0x0004C37C, 0x0004C3AA, "6a636e767ac2bced11dbcb1175620afb463ca43e5f652ea749b677abf3215835"),),
        "", "Clears the 0x2E0-byte provider state block and re-runs pinned GoMore init; called from gated GoMore index-update",
        ((0x0005DC58, "B.W"), (0x0006C224, "BL"), (0x0006C5C0, "B.W"),),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x0006C640, 44, ((0x0006C640, 0x0006C66C, "e8fb5c129824ccdda08fbd2993706f9668e421707ece60631c20e0e420948df6"),),
        "", "Four-byte provider sample plausibility bounds check; called from gated GoMore 0x0006ABF8 and the R1 GoMore-facing profile check",
        ((0x0006AC86, "BL"), (0x0006C67C, "BL"),),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x0006ACD8, 38, ((0x0006ACD8, 0x0006ACFE, "e9f08db33536ec5df52ca31e83a0324a5908a4ced6941a8a79ba083f82022935"),),
        "", "Stamps provider state with clock-backend timestamp, UTC offset, and sync flags; caller is pinned GoMore sensor-allocation",
        ((0x0006ACA8, "BL"), (0x0006C29C, "BL"),),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x00068570, 38, ((0x00068570, 0x00068596, "022723eb9499090e947524a0970ad01c61790f151bb863e2195365cb55dcda66"),),
        "", "Clamps a value against provider state at +0x39DC with +/-3 hysteresis; caller is gated GoMore 0x00094384",
        ((0x00094474, "BL"),),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x000726FA, 34, ((0x000726FA, 0x0007271C, "5c64556cb34a1d315ea93d2528ddba805b04e5a5e783ee1c8d1e0f81a96f65b7"),),
        "", "Provider parameter commit into offset 0x20F5; reached only from the pinned GoMore authorization init chain",
        ((0x0008ECB0, "BL"),),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x0006AB60, 34, ((0x0006AB60, 0x0006AB82, "719776dc190547df105be37970a8630691f7bcd6ba738b623f6ce6850fc4831f"),),
        "", "Seven-slot provider scan requiring enable bit 0 plus bit 2",
        ((0x00049498, "BL"), (0x0004951E, "BL"), (0x0006B0DC, "BL"),),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x0006AB38, 34, ((0x0006AB38, 0x0006AB5A, "490be24c3941b47214ce4028e5a93a598604867702dcee26028a2cc716568ac3"),),
        "", "Seven-slot provider scan requiring enable bit 0 plus bit 4",
        ((0x000494D8, "BL"), (0x00049558, "BL"),),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x0006AB10, 34, ((0x0006AB10, 0x0006AB32, "018b3cf04b0562d50285a3ac75077e01fb8ff42af28ec523e6ab144ebbee963c"),),
        "", "Seven-slot provider scan requiring enable bit 0 plus bit 3",
        ((0x000494B8, "BL"), (0x00049538, "BL"),),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x0006AAE8, 34, ((0x0006AAE8, 0x0006AB0A, "739332c40a93f26afce8f1f04854a36d6579286923d746b105a5b6cf0eb2adf0"),),
        "", "Seven-slot provider scan requiring enable bit 0 plus bit 1",
        ((0x00049478, "BL"), (0x00049506, "BL"), (0x0006B0D6, "BL"),),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
)

GOODIX_FRONTIER_32_63_FUNCTIONS = (
    _function(
        0x000362B6, 62, ((0x000362B6, 0x000362F4, "3d32384e89ad1e680c9003fdea14c8a015f53d6122015e6b189bfb7b8c3141df"),),
        "", "Allocates one 0x44-byte provider record and initializes its buffer descriptor; called only from the gated GH_SPO2/dlCom init bridge",
        ((0x0006EBEC, "BL"),),
        "goodix_gh3x2x_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x0006F964, 60, ((0x0006F964, 0x0006F9A0, "0d23d75d2303e7d6bdadc7dbaa89a5e9ea287bba9bc47f923d0345c6793fa946"),),
        "", "hal_gsensor_start_cache diagnostic and cached-buffer arm; sole caller is the gated Goodix gsensor path",
        ((0x0002E1AC, "BL"),),
        "goodix_gh3x2x_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x00029CC0, 58, ((0x00029CC0, 0x00029CD8, "1648f3be310fe8011357f2fec3af1869a8ca3ed00ed1e2d3be8f7e61190db71a"),),
        "", "Provider session-state reset over shared GH3X2X state at 0x20007A58; caller is the gated Goodix demo path",
        ((0x0002A75A, "BL"),),
        "goodix_gh3x2x_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x00056874, 56, ((0x00056874, 0x000568AC, "3cb142c6f1b7a1c0875074af40595da735f13d01e5afd4c2d5b36b096a77dac1"),),
        "", "Provider buffer-descriptor init with zeroing heap allocation; twelve callsites inside gated Goodix 0x0006DB5C",
        ((0x0006DD08, "BL"), (0x0006DD18, "BL"), (0x0006DD28, "BL"), (0x0006DD38, "BL"), (0x0006DD48, "BL"), (0x0006DD58, "BL"), (0x0006DD6E, "BL"), (0x0006DD80, "BL"), (0x0006DD90, "BL"), (0x0006DDA0, "BL"), (0x0006DDC4, "BL"),),
        "goodix_gh3x2x_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x000664F4, 54, ((0x000664F4, 0x0006652A, "db407ecc786251d0cdcdf575c074464c6e47e86928aa7a3bbd7ddea8609bca83"),),
        "", "Bounded word-window push with oldest-entry eviction; reached from gated Goodix 0x0003441C via 0x000419C8",
        ((0x00041A10, "BL"),),
        "goodix_gh3x2x_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x0003EFD8, 54, ((0x0003EFD8, 0x0003F00E, "e4381ae18ea5891e4b67e0f1c9a253c09c3ec38852cc49af8454e0b246c4a57a"),),
        "", "Scaled logistic 100/(1+exp(-k*(x-t))) scorer; three callsites inside gated Goodix 0x00088E80",
        ((0x00088F94, "BL"), (0x00088FDE, "BL"), (0x0008902A, "BL"),),
        "goodix_gh3x2x_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x000304A0, 54, ((0x000304A0, 0x000304D6, "e8e1d443136ce408b2cbe242d965c9b8c4bf76e3f5965ca3c6affaf202ce8b1f"),),
        "", "Six-slot pool teardown; part of the 0x0006EB30 provider model-context free chain",
        ((0x000918A6, "BL"), (0x000918B0, "BL"),),
        "goodix_gh3x2x_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x000667C6, 52, ((0x000667C6, 0x000667E4, "303eeca19ec00a28e3e1ea69bdcddf8e791a5a08f3a700fe61131bd108a1fd96"),),
        "", "Provider pair-buffer init with heap allocation; six callsites inside the pinned GH_HR private-context initializer",
        ((0x00072C72, "BL"), (0x00072C8E, "BL"), (0x00072CA2, "BL"), (0x00072CB6, "BL"), (0x00072CCA, "BL"), (0x00072CDE, "BL"),),
        "goodix_gh3x2x_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x0006635C, 50, ((0x0006635C, 0x0006638E, "0e0647dbe7e570930a4c47b2300462bb957b2986f19298a8cb4582c43c3a6ded"),),
        "", "Provider buffer-descriptor init (word elements) with heap allocation; gated Goodix callers including the GH_HR context initializer",
        ((0x00034AEE, "BL"), (0x000362E6, "BL"), (0x0003DF26, "BL"), (0x0003DF36, "BL"), (0x0003DF44, "BL"), (0x0003DF52, "BL"), (0x0003DF66, "BL"), (0x0003DF7C, "B.W"), (0x0005CDBE, "BL"), (0x0005CDCC, "BL"), (0x0005CDDA, "BL"), (0x0006D348, "BL"), (0x0006D362, "BL"), (0x00072D5A, "BL"), (0x00072D68, "BL"), (0x00072D76, "BL"), (0x00072D84, "BL"), (0x00072D92, "BL"), (0x00072DA0, "BL"), (0x00072DAE, "BL"),),
        "goodix_gh3x2x_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x000305D8, 50, ((0x000305D8, 0x0003060A, "d3eae9d26bb0029a9771c672edc4d01c412253237186ebfbe625844b9f01ac0f"),),
        "", "0x28-stride record teardown loop plus heap free; part of the 0x0006EB30 provider model-context free chain",
        ((0x0006EB70, "BL"),),
        "goodix_gh3x2x_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x000667E4, 48, ((0x000667E4, 0x00066814, "cb33111c174212cbd725ac38dac849a4e8873f2ae2f439696a4ac1b092119802"),),
        "", "Builds the dlCom_pre2exc_pv_v1.3.0 version string; callers are gated Goodix SpO2 paths",
        ((0x0006D4C6, "BL"), (0x0006ED34, "BL"),),
        "goodix_gh3x2x_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x00031914, 48, ((0x00031914, 0x00031944, "34d1c6e3be09ae22aefe2f71cc52c3e35a67c75897724e0d55f4cc87771cd8a6"),),
        "", "Descriptor fill-init with derived element count; reached from the pinned GH_SPO2/dlCom init bridge via 0x0003727C",
        ((0x00037298, "BL"),),
        "goodix_gh3x2x_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x00029CDC, 46, ((0x00029CDC, 0x00029D0A, "0da2d06e4ee504c07e24147926d321deb35aad32be665d690da2705280483605"),),
        "", "Provider mode toggle between two gated Goodix register paths; caller is gated Goodix 0x0002B218",
        ((0x0002B3CE, "BL"),),
        "goodix_gh3x2x_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x00037E8A, 44, ((0x00037E8A, 0x00037EB6, "f4810dd0ebbf63ac5c769cdf1a990881f31a62ca20a1ada36d68f5858a5ace3e"),),
        "", "Provider model-context teardown stage; part of the 0x0006EB30 free chain",
        ((0x0006EB4C, "BL"),),
        "goodix_gh3x2x_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x00029D0A, 42, ((0x00029D0A, 0x00029D34, "bfa84d1612fface2df5f02bcf4e43ec2ac9e8df9f7f0039700d7eb3b7612d9e1"),),
        "", "Provider min/max window tracker with saturation; callers are gated Goodix scopes",
        ((0x00029E1A, "BL"), (0x0002BADE, "BL"),),
        "goodix_gh3x2x_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x0003DDF4, 40, ((0x0003DDF4, 0x0003DE1C, "997fc21acd205e0b41d86dd9bbfab28da5092f2b6ecf18d8fe25691bea3acfd4"),),
        "", "Copies a seven-entry function table from flash and dispatches by index; three callsites inside gated Goodix 0x0006D204",
        ((0x0006D310, "BL"), (0x0006D31A, "BL"), (0x0006D324, "BL"),),
        "goodix_gh3x2x_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x00029C98, 40, ((0x00029C98, 0x00029CC0, "84620ef04f54d17c66096db4da7bcd3f7f3a9c0ced09c0852eb851f095fe474b"),),
        "", "Median-of-three selector; callers are gated Goodix scopes",
        ((0x00029DFE, "BL"), (0x0002BAC2, "BL"),),
        "goodix_gh3x2x_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x0007CBA0, 38, ((0x0007CBA0, 0x0007CBC6, "da29aadf6e7df58e22894b8d35b3fdb957d38ba2f1e591f7aedab4dfc79551e0"),),
        "", "Provider sub-record teardown plus heap free; part of the 0x0006EB30 free chain",
        ((0x0006EB7C, "BL"),),
        "goodix_gh3x2x_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x00036BD4, 38, ((0x00036BD4, 0x00036BFA, "9a189ec7bd731011a6389db12a9184c91d285e31ae4e4ac280d6a8898e813cf6"),),
        "", "0x4C-byte descriptor copy plus fixed field init (/25, 5, 25); caller is the pinned GH_SPO2/dlCom init bridge",
        ((0x0006EBC8, "BL"),),
        "goodix_gh3x2x_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x00033800, 38, ((0x00033800, 0x00033826, "1a1f06f53f1adc4507f23e7d0fc07dd16740e4c02355da8cd82fafd97492553c"),),
        "", "0x44-stride record teardown plus heap free, twin of the 0x000362B6 allocation; part of the 0x0006EB30 free chain",
        ((0x0006EB58, "BL"),),
        "goodix_gh3x2x_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x0002A65C, 38, ((0x0002A65C, 0x0002A682, "6f148cb2ec1bf03cab57be9b059caf0646101217157a2bed373aaf2669d9ee76"),),
        "", "Indirect provider op call with the 0xAAAA payload word over shared GH3X2X state RAM",
        (),
        "goodix_gh3x2x_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x00093E3A, 36, ((0x00093E3A, 0x00093E5E, "22be4a72d63088a72271b3f30d37361c5deb1d8ee2b33baa81cf592b06421230"),),
        "", "Paired pool-free loop over 0x18-stride records; part of the 0x0006EB30 free chain",
        ((0x00037E92, "BL"),),
        "goodix_gh3x2x_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x0005683C, 36, ((0x0005683C, 0x00056860, "493ebafe06f619243671f8a398a970cc7eef8a182ce6fbd5a0e9992485765a3d"),),
        "", "Six-field provider descriptor init plus paired buffer zeroing; callers are gated Goodix scopes",
        ((0x0006E5D0, "BL"), (0x0006E6E8, "BL"),),
        "goodix_gh3x2x_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x0002A630, 36, ((0x0002A630, 0x0002A654, "6bc0cc62488ed40a4c3a9e3681279ce905a09ba847e02b3c45e2212b8f85872c"),),
        "", "One-time provider lane-table init over 0x20030204; caller is gated Goodix 0x0006D3C0",
        ((0x0006D3D8, "BL"),),
        "goodix_gh3x2x_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x0006633A, 34, ((0x0006633A, 0x0006635C, "830c28a33687581667b07de4e53d1c4c9da91a237fcf158120661ba1e00638ad"),),
        "", "Provider buffer-descriptor init (halfword elements) with heap allocation; caller chain reaches the pinned GH_SPO2/dlCom bridge",
        ((0x0005CDE8, "BL"),),
        "goodix_gh3x2x_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x00096A20, 32, ((0x00096A20, 0x00096A40, "bb42b9a7b83f6b6f3434b9e74f92a07033c256785a209f3145dd3c838b30cf1d"),),
        "", "Provider 8-byte record allocation and init; caller is the pinned GH_SPO2/dlCom init bridge",
        ((0x0006EBF8, "BL"),),
        "goodix_gh3x2x_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x000929B6, 32, ((0x000929B6, 0x000929D6, "33d6a6d9106489339e092a2a242b28df0a7b417dfdff90b08113789198576dc3"),),
        "", "Max-plus-argmax scan over a provider sample vector; caller is gated Goodix 0x00066AB2",
        ((0x00066B1C, "BL"),),
        "goodix_gh3x2x_candidate", "vendor_source_required_not_redistributable",
    ),
)

TIME_CALENDAR_FRONTIER_32_63_FUNCTIONS = (
    _function(
        0x0008AD08, 52, ((0x0008AD08, 0x0008AD3C, "38227141313c91c72267c8bc5f1f0c2e19c2bc54982f6451a4cae5a47ce8da0a"),),
        "", "Clock-backend lookup plus registered-callback conversion composed exclusively from the pinned time provider snapshot/UTC-calendar adapters",
        ((0x00058844, "BL"),),
        "unknown_time_calendar_provider_candidate", "clean_room_reimplementation_owner_authorized",
    ),
)

DEVICE_REGISTRY_FRONTIER_32_63_FUNCTIONS = (
    _function(
        0x0005D94A, 60, ((0x0005D94A, 0x0005D986, "17c92b1ba32dda3b2f56234d6e340112f0a4888a91270e9e437c3cd5c749407b"),),
        "", "Named-registry list node allocate-plus-tail-link helper; consumed by the gated registry insert 0x0005DB14",
        ((0x0005DB60, "BL"), (0x00089DB0, "BL"), (0x0008A374, "BL"),),
        "unknown_generic_device_registry_candidate", "clean_room_reimplementation_owner_authorized",
    ),
    _function(
        0x0005D1EA, 52, ((0x0005D1EA, 0x0005D1F4, "1f9097d19d0e99a5c151dd3ec952c2f84273eaba7b486e0f3ed900c377aa2e95"),),
        "", "Static request-block fill (code 0xAE) and slot-0x10 dispatch through the registry operation table",
        ((0x0005D1E0, "B.W"), (0x0005D1FE, "BL"),),
        "unknown_generic_device_registry_candidate", "clean_room_reimplementation_owner_authorized",
    ),
    _function(
        0x0005B2F8, 48, ((0x0005B2F8, 0x0005B328, "2e8216f009494b6115d22deb8b0dc55e47fe15a342cd54a463750fd8b8c2e80b"),),
        "", "Sector erase loop through the registry device ops-table +0x30 slot over the queried sector count",
        ((0x0005B246, "BL"), (0x0005B94A, "BL"), (0x0008DD88, "B.W"),),
        "unknown_generic_device_registry_candidate", "clean_room_reimplementation_owner_authorized",
    ),
    _function(
        0x0005DBBC, 46, ((0x0005DBBC, 0x0005DBEA, "830f68f541d0bfba222452756ad329219a0462143c7a68248b8f5efc5c0a20cc"),),
        "", "Critical-section-guarded registry record flag clear plus ops-table +8 callback; shares the framework guard pair with the pinned registry insert",
        ((0x0004511A, "BL"), (0x000469B4, "BL"), (0x00091FC0, "BL"), (0x00092136, "BL"), (0x000921C4, "BL"), (0x000922C6, "BL"), (0x0009254A, "BL"), (0x000925F2, "BL"), (0x00092754, "BL"), (0x00092816, "BL"),),
        "unknown_generic_device_registry_candidate", "clean_room_reimplementation_owner_authorized",
    ),
    _function(
        0x0005DA00, 44, ((0x0005DA00, 0x0005DA2C, "86f88c0b4771227e98606eb14d98a06f8c4e2b1547419ad1647e930ada8c0508"),),
        "", "Critical-section-guarded registry ops-table +8 notification pair; called from the heap provider fatal path",
        ((0x00045DFE, "BL"), (0x00046A14, "BL"), (0x00092086, "BL"), (0x00092166, "BL"), (0x00092238, "BL"), (0x000922F6, "BL"), (0x0009255C, "BL"), (0x0009265C, "BL"), (0x00092692, "BL"), (0x000927B4, "BL"), (0x00092828, "BL"),),
        "unknown_generic_device_registry_candidate", "clean_room_reimplementation_owner_authorized",
    ),
    _function(
        0x0005D1F4, 42, ((0x0005D1F4, 0x0005D21E, "10b54c8aacdf82000405142bed448e79496840ee965df98a4f76f8bcaada15c6"),),
        "", "Registry request read-modify-write of one flag byte via the slot-0x10/0x14 submit wrappers",
        ((0x000778A8, "BL"), (0x00077924, "BL"),),
        "unknown_generic_device_registry_candidate", "clean_room_reimplementation_owner_authorized",
    ),
    _function(
        0x00050DF0, 40, ((0x00050DF0, 0x00050E18, "3c2e47cbaf2e1e3ab5f411afef283edacf666274aae82224329b97001ae8e65f"),),
        "", "Static request-block fill and slot-0x14 dispatch through the registry operation table",
        ((0x00050D9E, "BL"), (0x00050DB8, "BL"),),
        "unknown_generic_device_registry_candidate", "clean_room_reimplementation_owner_authorized",
    ),
    _function(
        0x00096FB0, 38, ((0x00096FB0, 0x00096FD6, "37fa10401aecec390816270b293f4efabecbd216a54c9091f051798878295197"),),
        "", "String-plus-length request-block fill (strlen when absent) and slot-0x14 dispatch",
        (),
        "unknown_generic_device_registry_candidate", "clean_room_reimplementation_owner_authorized",
    ),
    _function(
        0x0005E1FC, 38, ((0x0005E1FC, 0x0005E222, "3c7f1742f69ff01c9538eb242f5657868739069d6206f6202b6bc8b27a235130"),),
        "", "Single 0x1000-sector erase through the registry device ops-table +0x30 slot when flash is enabled",
        ((0x0003ED2E, "BL"),),
        "unknown_generic_device_registry_candidate", "clean_room_reimplementation_owner_authorized",
    ),
    _function(
        0x00050F5C, 38, ((0x00050F5C, 0x00050F82, "36d5fe09a66addc0b4283d62663f37f254cbffbf57589005db9581d693da940b"),),
        "", "Static request-block fill and slot-0x14 dispatch through the registry operation table",
        ((0x0006F644, "B.W"),),
        "unknown_generic_device_registry_candidate", "clean_room_reimplementation_owner_authorized",
    ),
    _function(
        0x0009338C, 36, ((0x0009338C, 0x000933B0, "d36856aca1028c9585f3ca0083938d84deb11137ced4eee1c2b8ee5107f0d310"),),
        "", "Static request-block fill and slot-0x10 dispatch; called from the R1 IQS7211E adapter and touch init",
        ((0x0002FEA8, "B.W"), (0x000512F0, "BL"),),
        "unknown_generic_device_registry_candidate", "clean_room_reimplementation_owner_authorized",
    ),
    _function(
        0x00050F34, 36, ((0x00050F34, 0x00050F58, "e31bc76652db2d545fda1abfb31060eed05836ebdcede2bc4cfac636d8016027"),),
        "", "Static request-block fill and slot-0x10 dispatch; thunked into the GXT310 register-read path",
        ((0x0006F640, "B.W"),),
        "unknown_generic_device_registry_candidate", "clean_room_reimplementation_owner_authorized",
    ),
    _function(
        0x000509BC, 32, ((0x000509BC, 0x000509DC, "704a804fd7a46799352215a72a54cc0598a7de54afe9f3c303f3c602d9cf8e29"),),
        "", "Static request-block fill and slot-0x14 dispatch through the registry operation table",
        ((0x0006F918, "BL"),),
        "unknown_generic_device_registry_candidate", "clean_room_reimplementation_owner_authorized",
    ),
)

SENSOR_STREAM_FRONTIER_32_63_FUNCTIONS = (
    _function(
        0x0005D90E, 60, ((0x0005D90E, 0x0005D94A, "b76f837b14c1dc92278d85b3cae151069928b27fc728497ed47f6d4ed92a4693"),),
        "", "Shared list node allocate-plus-head-link helper; consumed by the gated sensor-stream register 0x00089890",
        ((0x000898BA, "BL"), (0x0008A31C, "BL"),),
        "unknown_sensor_stream_framework_candidate", "clean_room_reimplementation_owner_authorized",
    ),
    _function(
        0x00089E8C, 56, ((0x00089E8C, 0x00089EC4, "e8368f115d5cb23110a97102e3f4172c91b040be1b4c2e8b741f61ba3364b985"),),
        "", "Clamped triple write into stream-object fields +0xC0/+0xC4/+0xC8 beside the framework object table",
        (),
        "unknown_sensor_stream_framework_candidate", "clean_room_reimplementation_owner_authorized",
    ),
    _function(
        0x00089E50, 56, ((0x00089E50, 0x00089E88, "33606d6ea16d0fbc1261d1e07420475180224b02d91457144e5c8d69c1f49cdc"),),
        "", "Clamped triple write into stream-object fields +0xCC/+0xD0/+0xD4, paired with 0x00089E8C",
        (),
        "unknown_sensor_stream_framework_candidate", "clean_room_reimplementation_owner_authorized",
    ),
    _function(
        0x00089D54, 48, ((0x00089D54, 0x00089D84, "c8a7e98e9b395be6e24adf0e6b6592d2e81afbd546c93a858a7260de761728a7"),),
        "", "Stream-object name lookup over the framework list; the pinned unregistration boundary resolves objects through this routine",
        ((0x000897F6, "BL"), (0x00089B0E, "BL"),),
        "unknown_sensor_stream_framework_candidate", "clean_room_reimplementation_owner_authorized",
    ),
    _function(
        0x0008A3C0, 44, ((0x0008A3C0, 0x0008A3EC, "527c07dd703a1bc06961f994429a950bde7e9287242b1e0ffd1002ec23112ef9"),),
        "", "Framework deferred-free: marks the object tombstone byte, unlinks through the list helper, and vPortFree; called by the pinned unregister",
        ((0x0003D0E4, "B.W"), (0x00048C06, "BL"), (0x00048C7A, "BL"), (0x000495D6, "BL"), (0x000498A6, "BL"), (0x00049CBA, "BL"), (0x00049D1A, "BL"), (0x00049E9E, "BL"), (0x00049EFE, "BL"), (0x0004A58E, "BL"), (0x0004A9F4, "BL"), (0x0004B282, "BL"), (0x0004B2EE, "BL"), (0x0004B398, "BL"), (0x0004B7BA, "BL"), (0x0004C45C, "BL"), (0x0004C510, "BL"), (0x0004C664, "BL"), (0x0008A18C, "BL"), (0x0008A44A, "BL"),),
        "unknown_sensor_stream_framework_candidate", "clean_room_reimplementation_owner_authorized",
    ),
    _function(
        0x0008A55C, 32, ((0x0008A55C, 0x0008A57C, "64998be5b4856e2127403c7ba086bfd043986402f886b38ac25524a86b1200f3"),),
        "", "Framework housekeeping init: list init, enable flag, and a 1000-ms timer creation",
        ((0x00092326, "BL"), (0x0009259C, "BL"),),
        "unknown_sensor_stream_framework_candidate", "clean_room_reimplementation_owner_authorized",
    ),
)

QUANTIZED_RUNTIME_FRONTIER_32_63_FUNCTIONS = (
    _function(
        0x0005A3D4, 58, ((0x0005A3D4, 0x0005A40E, "86d917fc6e76e5b29df99e011e92a52d59df9af35a9f126ae41c65ea0d246089"),),
        "", "Two-output thirds-slice compute over the 0x91xxx descriptor-runtime helper 0x00091E02; reached from gated GoMore graph scope",
        ((0x00065404, "BL"), (0x00065416, "BL"), (0x0006545E, "BL"), (0x00065472, "BL"), (0x000654BA, "BL"), (0x000654CE, "BL"),),
        "unknown_shared_quantized_neural_runtime_candidate", "clean_room_reimplementation_owner_authorized",
    ),
    _function(
        0x0006FE20, 54, ((0x0006FE20, 0x0006FE56, "88ac6554e24e424f83c3ca4863598ee025a8af2fd5237c0d2d17aac1189b7a48"),),
        "", "Requantization scale-ratio compute (x-min)*(255/(max-min)) into the runtime round helper; caller is the pinned int8-add executor",
        ((0x00036CC0, "BL"), (0x00036CDC, "BL"), (0x00036D00, "BL"),),
        "unknown_shared_quantized_neural_runtime_candidate", "clean_room_reimplementation_owner_authorized",
    ),
    _function(
        0x00091C48, 46, ((0x00091C48, 0x00091C56, "cfa2999425b7f6393942c5fd0492aeae71a5bf6046bff32a4d8cea3616674acb"),),
        "", "Twelve-slot 0x14-stride tensor-descriptor free; matches the pinned twelve-descriptor arena runtime",
        ((0x000651C2, "BL"), (0x000652F2, "BL"), (0x0006536C, "BL"), (0x000653B8, "BL"), (0x000653CE, "BL"), (0x0006550C, "BL"), (0x00065522, "BL"), (0x0006552A, "BL"), (0x00065590, "BL"), (0x00065612, "BL"), (0x00065670, "BL"), (0x000656A0, "BL"), (0x00065700, "BL"), (0x00088896, "BL"), (0x00091C36, "BL"), (0x00091C6E, "BL"),),
        "unknown_shared_quantized_neural_runtime_candidate", "clean_room_reimplementation_owner_authorized",
    ),
    _function(
        0x00091C56, 42, ((0x00091C56, 0x00091C80, "c671a07c516344d0142150e530df34a3d55e142fd00299ca323c0d96f63cc630"),),
        "", "Loop over descriptor pointers invoking the twelve-slot descriptor free",
        ((0x0006543C, "BL"), (0x0006544A, "BL"), (0x00065498, "BL"), (0x000654A6, "BL"), (0x000654F6, "BL"), (0x00065504, "BL"),),
        "unknown_shared_quantized_neural_runtime_candidate", "clean_room_reimplementation_owner_authorized",
    ),
    _function(
        0x00065680, 42, ((0x00065680, 0x000656AA, "8ff217df4d25f016ea26fc1923354451b69a307f46c673e1cb9f387f55595f5f"),),
        "", "Descriptor-runtime call plus conditional descriptor free; reached from gated GoMore 0x00088450",
        ((0x0008850C, "BL"), (0x00088564, "BL"), (0x000885BC, "BL"), (0x00088614, "BL"), (0x0008868E, "BL"), (0x000886E6, "BL"), (0x0008873E, "BL"), (0x000887C6, "BL"), (0x00088828, "BL"),),
        "unknown_shared_quantized_neural_runtime_candidate", "clean_room_reimplementation_owner_authorized",
    ),
    _function(
        0x0009371C, 40, ((0x0009371C, 0x00093744, "5806a13ecb796b4e1ad0f474cd62f15a5e93971e94c8eee39b61b651e1bc4e92"),),
        "", "Twelve-slot 0x14-stride tensor-descriptor allocation, mirror of the 0x00091C48 free",
        ((0x00091E76, "BL"),),
        "unknown_shared_quantized_neural_runtime_candidate", "clean_room_reimplementation_owner_authorized",
    ),
    _function(
        0x00091EBA, 34, ((0x00091EBA, 0x00091EDC, "b5e3ddca3a2c23ba60a3c1da873758a3bfad676b27a0f1fbcf8db8fd410b1d86"),),
        "", "Tensor-descriptor flag and u16 payload write matching the 0x14-stride descriptor layout",
        ((0x00088772, "BL"),),
        "unknown_shared_quantized_neural_runtime_candidate", "clean_room_reimplementation_owner_authorized",
    ),
    _function(
        0x00091D9C, 34, ((0x00091D9C, 0x00091DBE, "0d3b87b1a5048f89ca69d26fac1f8ad2eb5d10c5873b8ae9d990ef396c1a521c"),),
        "", "Descriptor allocation chained into the pinned tensor-arena compactor 0x00093628",
        ((0x000651E6, "BL"), (0x00091986, "BL"), (0x000919D4, "BL"), (0x00091A28, "BL"), (0x00091A94, "BL"), (0x00091B4A, "BL"), (0x00091B60, "BL"), (0x00091C98, "BL"), (0x00091CEA, "BL"), (0x00091D40, "BL"), (0x00091EF6, "BL"),),
        "unknown_shared_quantized_neural_runtime_candidate", "clean_room_reimplementation_owner_authorized",
    ),
    _function(
        0x000290FE, 34, ((0x000290FE, 0x00029120, "bdec0f3376563581f2578e7e253ebd0d44f950cb7cffaf4fe0eac54aafafdead"),),
        "", "Round-half-away-from-zero float-to-int used by the pinned int8-add executor's requantization path and by 0x0006FE20",
        ((0x00036D34, "BL"), (0x0006FE52, "B.W"),),
        "unknown_shared_quantized_neural_runtime_candidate", "clean_room_reimplementation_owner_authorized",
    ),
)

ALL_FUNCTIONS = (
    R1_FRONTIER_32_63_FUNCTIONS
    + GOMORE_FRONTIER_32_63_FUNCTIONS
    + GOODIX_FRONTIER_32_63_FUNCTIONS
    + TIME_CALENDAR_FRONTIER_32_63_FUNCTIONS
    + DEVICE_REGISTRY_FRONTIER_32_63_FUNCTIONS
    + SENSOR_STREAM_FRONTIER_32_63_FUNCTIONS
    + QUANTIZED_RUNTIME_FRONTIER_32_63_FUNCTIONS
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
        "analysis": "32...63-byte ownership frontier",
        "image_sha256": EXPECTED_IMAGE_SHA256,
        "function_count": len(rows),
        "function_bytes": sum(int(row["size"]) for row in rows),
        "pinned_bytes": sum(int(row["pinned_bytes"]) for row in rows),
        "omitted_bytes": sum(int(row["omitted_bytes"]) for row in rows),
        "r1_function_count": len(R1_FRONTIER_32_63_FUNCTIONS),
        "gomore_function_count": len(GOMORE_FRONTIER_32_63_FUNCTIONS),
        "goodix_function_count": len(GOODIX_FRONTIER_32_63_FUNCTIONS),
        "time_calendar_function_count": len(TIME_CALENDAR_FRONTIER_32_63_FUNCTIONS),
        "device_registry_function_count": len(DEVICE_REGISTRY_FRONTIER_32_63_FUNCTIONS),
        "sensor_stream_function_count": len(SENSOR_STREAM_FRONTIER_32_63_FUNCTIONS),
        "quantized_runtime_function_count": len(QUANTIZED_RUNTIME_FRONTIER_32_63_FUNCTIONS),

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
