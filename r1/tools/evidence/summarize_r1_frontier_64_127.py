#!/usr/bin/env python3
"""Pin and source-route the 150-function 64...127-byte R1 frontier.

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


R1_FRONTIER_64_127_FUNCTIONS = (
    _function(
        0x0004F6F8, 126, ((0x0004F6F8, 0x0004F776, "f9f41351b8ca123b644a40811febabd342109b79981623fc11920d66838c8bca"),),
        "r1_eat_command_dispatch", "eAT command-table name match and handler dispatch (direct or deferred via queue post)",
        ((0x0004F2AC, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0004A8C8, 126, ((0x0004A8C8, 0x0004A946, "6dc57fd84eeb5251a6a8185d9c4b0f48d7076c8a5e3113108f26c5aceb4dca1f"),),
        "r1_algo_sleep_vivo_probe_start", "Sleep vivo-probe start: GoMore gate 5 on, 5000-ms timer create, [RING] algo_sleep_vivo_probe_start",
        ((0x0004A860, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x000832D4, 124, ((0x000832D4, 0x00083350, "001c859eea858ebca81f4f3180d7a30496dc1c341d98331430c951a6ed07a2a1"),),
        "r1_proto_register_ble_recv_callback", "BLE receive-callback registration with duplicate-registration diagnostic",
        ((0x000830BA, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0005128C, 124, ((0x0005128C, 0x000512D2, "b2bdf44ee7b999424b39138ffffa23ee028bb18956b02ad9f63a956e872f9864"), (0x000512D4, 0x0005130A, "3fde38cc770c4c6974c75cd9e4d7fbc7545aadb5ee4354b8e1844a7f37165515"),),
        "r1_touch_chip_id_probe", "Touch-controller board power sequence, polled ready loop, 2-byte identity read (reported by legacy command 0x62D3E)",
        ((0x0004F11E, "BL"), (0x00062D42, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00050F88, 124, ((0x00050F88, 0x00050F9A, "73d3d16326776e1fa84e05f9efb57839fb0decde9eecd55eaf1beb56eeca63f5"),),
        "r1_temperature_sensor_power_down", "Two-call GXT310 power/hold-off wrapper used only by R1 temperature paths",
        ((0x00050E38, "BL"), (0x00050E70, "BL"), (0x00050EE2, "BL"), (0x000510FA, "BL"), (0x00051168, "BL"), (0x00051280, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00050E4C, 124, ((0x00050E4C, 0x00050EC8, "d2167456de8a264e80873742889c7302c9f3637662f38c0a35c2a11b675df32b"),),
        "r1_temperature_pair_read_calibrated", "GXT310 power-on, raw pair read, product calibration-record apply, averaged 17-bit result",
        ((0x0009190E, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00091780, 118, ((0x00091780, 0x000917F6, "ec3e6261eb23bd02e9f4ba49401db527c527986c8399ba19141c103799eb18ea"),),
        "r1_store_class_record_write", "Store-class record CRC16 (r1_crc16_modbus), header pack, vtable write, [RING] store_class_fail diagnostic",
        ((0x00073510, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0004E070, 118, ((0x0004E070, 0x0004E0E6, "9345246d3cd3c253b16e4ec2967f22aa42baa82fb41ef55920eb2e221b9df487"),),
        "r1_touch_set_fast_mode", "Touch fast-mode connection policy: delayed-event cancel/schedule, [RING] touch_set_fast_mode log",
        ((0x0006A854, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0004A7F4, 118, ((0x0004A7F4, 0x0004A86A, "73278981f7cf2587e10d48ddbee36530656bbe8a767bd67938fa2e72dfa60fa0"),),
        "r1_algo_sleep_result_report", "Sleep-result status log, event-0xC publish, subscriber multicast, vivo-probe trigger",
        ((0x0006C32E, "BL"), (0x0006C36C, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0005061C, 116, ((0x0005061C, 0x00050690, "03caafb911c98a57f9166890cd052edaa8b6c1e488da82968312b0df4ed46454"),),
        "r1_pmic_charge_status_decode", "PMIC register 5/6/7 read, status-bit policy, register-3 bit-6 set (called from r1_pmic_charge_event_plan)",
        ((0x00096B0C, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00048BD0, 116, ((0x00048BD0, 0x00048C44, "e00c4ea099e0d80a5aaca080c487889e4d4c60273cf327375dd26878726b9eaa"),),
        "r1_factory_mode_start", "Factory/aging mode start: config word latch, 0xF000-tick timer, factory and aging stream registration",
        ((0x000623C0, "BL"), (0x000883F4, "B.W"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0005E4D8, 114, ((0x0005E4D8, 0x0005E54A, "d656e5a56f81232e9328f7dcaf5b852dafc55d40fc3f373908ac2a4b1f760e49"),),
        "r1_ep_record_write", "ep.bin bounded write adapter: 0x2000 range guard, [ep] write out of range, vtable op 0x2C",
        ((0x0003ECDE, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0005E404, 114, ((0x0005E404, 0x0005E476, "9c76d5c2b03ff4c501f9232e5984db8f599ba97bc73881dfd50e754d45ca75e2"),),
        "r1_ep_record_read", "ep.bin bounded read adapter: 0x2000 range guard, [ep] read out of range, vtable op 0x28",
        ((0x0003ED1C, "BL"), (0x0003EE64, "BL"), (0x0005E026, "BL"), (0x0005E080, "B.W"), (0x0005E0B2, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0004CA08, 114, ((0x0004CA08, 0x0004CA7A, "5a690530f149a349332571ac8e70acc714a06bd616ad0d39ac2fa28aa48b0eb5"),),
        "r1_app_ble_set_fast_mode", "BLE fast connection-interval policy via delayed-event reschedule, [RING] app_ble_set_fast_mode log",
        ((0x0004E7D6, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x000629D4, 110, ((0x000629D4, 0x00062A42, "e9a7bad36908e53d2d917a263daab7c841f674f276929178ab100b8ed224d650"),),
        "r1_factory_aging_stream_command", "Legacy command handler: aging/factory sensor-stream register/unregister sub-commands 0/4/10",
        ((0x0004E352, "BL"), (0x000626FA, "B.W"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0004A4B4, 110, ((0x0004A4B4, 0x0004A522, "aea7b68388d371072780cd1a7fab43201b5bf807761eea4e40a6ae99945d9fe6"),),
        "r1_algo_sleep_force_awake", "Sleep force-awake: [RING] log, GoMore 0x6B50C notify, event-0xC publish, 3000-ms timer",
        ((0x000423D4, "B.W"), (0x0004A9DC, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00088170, 108, ((0x00088170, 0x000881DC, "8d280bb91b9c6519b7e325fb1a165af07c20f6b06496dd1f1eee0bea54c6cb35"),),
        "r1_health_daily_record_replay", "FlashDB TSL blob read of daily record, local-hour bucket, six-handler fanout to HR/SpO2 daily caches",
        (),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0008345C, 108, ((0x0008345C, 0x000834C8, "96b3089d1fe38dac1372b163039c2d90db54e69c049f23032917bb76017bbb4a"),),
        "r1_proto_report_battery_status", "Battery percent/status pack and proto report send",
        ((0x0003213A, "BL"), (0x00046278, "BL"), (0x000462E4, "BL"), (0x0004C43E, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x000815E4, 108, ((0x000815E4, 0x00081650, "2efa4624d146a0523c78e225cc3449828534b8ad67ab3919ff0924b969ea2d2a"),),
        "r1_legacy_stream_sample_latch", "Five-sample latch emitting 0xF2/0x12 legacy reply then sensor-stream unregister",
        (),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0005B32C, 106, ((0x0005B32C, 0x0005B34A, "081ec05ef7696016b2b30c0e14f979b1336ec3ac132371b8f10ee22bdbb641ec"), (0x0005B34C, 0x0005B398, "1056fa41e40b329462d385e2313747ea3930f8f22d71050d88c43d6991f163cd"),),
        "r1_sleep_storage_valid_count", "Sleep-flash block scan counting valid 0x18-byte records via ops table",
        ((0x0005B23E, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00045EC8, 106, ((0x00045EC8, 0x00045EE8, "846ba2ab8495b8ffebcbc30fe22fd98652d4fcfa3de26f28cd729310cbb7a77e"), (0x00045EEE, 0x00045F38, "0fb1223ad590f11e02a0ed463c8837eb3a93e7e6a4023365e3b09b2ea30849cf"),),
        "r1_touch_config_queue_consume", "Touch-task queue consumer: five config-write cases plus pending-tap timeout",
        ((0x0004665A, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0006FC78, 104, ((0x0006FC78, 0x0006FCE0, "3f71257940745bf92a1a408f96b1961f2141fd26f0192872cba745c7159c4440"),),
        "r1_touch_irq_event_dispatch", "Touch IRQ event dispatch from iqs7211e worker: repeat/new-event select, tick stamp, handler call",
        ((0x00030FD4, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00062840, 104, ((0x00062840, 0x0006284E, "3f852d75f0884668b44aa00aab922e89a13f61150e7ac1d6b931d300f7b8f587"), (0x00062854, 0x000628AE, "4f27778f243b4cd6dfd6f1be95840ab8cc6c8ad2cb901b3500d3c1db72c8f80d"),),
        "r1_legacy_power_config_command", "Legacy command switch over config accessors 0x7BB44..0x7BBC0 with bounded reply",
        ((0x0004E416, "BL"), (0x000627BE, "B.W"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00050C90, 104, ((0x00050C90, 0x00050CF8, "2f865d225250cfb3b7d76eb6008f5dbf537d7c8363f645c7ec730c308c922774"),),
        "r1_adc_channel_read_averaged", "Device-registry ADC read: 10x64us settle, 3-sample signed average",
        ((0x00050D04, "BL"), (0x00050D2E, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0008D888, 102, ((0x0008D888, 0x0008D8EE, "2f3e64601f0b0cc9c0724c0ded69b869370d2c45e35f8b985046456580ca0f60"),),
        "r1_event_dispatch_by_id", "Event handler dispatch over three id-range tables (2..0xFFD, 0x1000.., 0x2000..), payload free above 4 bytes",
        ((0x000469E4, "BL"), (0x00092622, "BL"), (0x00092784, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0004C948, 102, ((0x0004C948, 0x0004C9AE, "3a1615ae905d13ed469c4dbebe4a296d5d64abbb14a5db15ad7369de02badd56"),),
        "r1_app_ble_disconnect", "BLE disconnect policy: conn-state CONNECTED gate, SVC 0x76, [RING] app_ble_disconnect log",
        ((0x00043014, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0008ED5C, 100, ((0x0008ED5C, 0x0008EDC0, "418101b748c927bc086d6e14f76a3227e1c4b60ad98baac5d6cd0b4816c9933b"),),
        "r1_dfu_ctrl_point_write_glue", "Buttonless-DFU control-point glue with bootloader settings-page write-protect diagnostic",
        ((0x0005225C, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0008E6A0, 100, ((0x0008E6A0, 0x0008E704, "6e28a5fac8de9270f349e09a1901d4294d6540696baf8eb021ca9e8e2b971abc"),),
        "r1_service_touch_close", "Touch lease source-bit clear; last close posts synthetic release and task event 4",
        ((0x000462F4, "BL"), (0x00047F3E, "BL"), (0x0004F9F0, "BL"), (0x00052F1A, "BL"), (0x0006229E, "BL"), (0x0006A9DA, "B.W"), (0x00084926, "BL"), (0x00092C46, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0004EF24, 100, ((0x0004EF24, 0x0004EF88, "97b0c0a7636db9cde69f70d384a73cb605c235330eb401c75309940f8774b619"),),
        "r1_eat_respond_format", "eAT vsnprintf into 0x200 buffer with three-slot subscriber fanout",
        ((0x0004ED94, "BL"), (0x0004EDAA, "B.W"), (0x0004EDF0, "BL"), (0x0004EE32, "BL"), (0x0004EE96, "BL"), (0x0004EECA, "BL"), (0x0004EEE2, "BL"), (0x0004F058, "BL"), (0x0004F066, "BL"), (0x0004F0BA, "BL"), (0x0004F0C8, "BL"), (0x0004F14E, "BL"), (0x0004F19E, "BL"), (0x0004F1EC, "BL"), (0x0004F20C, "BL"), (0x0004F314, "B.W"), (0x0004F386, "BL"), (0x0004F3D0, "BL"), (0x0004F3F0, "BL"), (0x0004F42C, "BL"), (0x0004F4AE, "BL"), (0x0004F4D8, "BL"), (0x0004F538, "BL"), (0x0004F572, "BL"), (0x0004F692, "BL"), (0x0004F6A0, "BL"), (0x0004F7A4, "BL"), (0x0004F7AE, "BL"), (0x0004F83E, "BL"), (0x0004F850, "BL"), (0x0004F918, "B.W"), (0x0004F99C, "B.W"), (0x0004F9CA, "BL"), (0x0004F9FA, "BL"), (0x0004FA70, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0004A998, 100, ((0x0004A998, 0x0004A9FC, "dfde79e1849c5018976339defeeff45af2703406bae098bde9664bf1a21accde"),),
        "r1_sleep_vivo_probe_stop", "Sleep vivo-probe stop: not-living diagnostic, GoMore gate 5 off, timer cancel",
        (),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0004EF8C, 98, ((0x0004EF8C, 0x0004EFEE, "af65174ff5a613886ea4382e835229feae4c12e000875efa6827261183a7768f"),),
        "r1_eat_core_init", "eAT core init: command-table bounds, two-channel setup, [RING] === eAT core init %d === log",
        ((0x00045D94, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0004DD78, 98, ((0x0004DD78, 0x0004DDDA, "c972202c101e2e5a23d347d01e3d4b5d2b412462711990f3de2b09b4ca81377d"),),
        "r1_app_ble_set_slow_mode", "BLE slow connection-interval policy, 0x2800-tick delayed schedule, [RING] log",
        ((0x000451F8, "BL"), (0x0004EE7A, "BL"), (0x0006A860, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0006F53C, 96, ((0x0006F53C, 0x0006F59C, "20032080d9034130d74333a01123c32c5b6ae6e04a8076ea9a958000ea4cc624"),),
        "r1_temperature_id_log", "Temperature-sensor register-3 read with [RING] temp addr/id diagnostic",
        ((0x0006F814, "B.W"), (0x0006F82E, "B.W"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00062B4C, 96, ((0x00062B4C, 0x00062BAC, "03ae0b50ce3a851840b3c69f515c9b8fc032c611acfc12326bfe9f95ed7b3c4f"),),
        "r1_touch_long_press_time_command", "Legacy command: byte-swapped long-press time, clamp via r1_touch_long_press_clamp",
        ((0x0004E372, "BL"), (0x00062712, "B.W"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x000506A4, 96, ((0x000506A4, 0x00050704, "31354bd530b12c212cee34c61ecf6524d6901414ca0efee18e2d97b43deaeacd"),),
        "r1_battery_voltage_read", "Device-registry ADC read, 3-sample average, x0x4B0>>12 millivolt scale",
        ((0x0004F4A6, "BL"), (0x00096CE8, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0004D9B0, 96, ((0x0004D9B0, 0x0004DA10, "b25b8d7adb24dc28f89701c9d66e5b176719c8972acb1c8398be7c6efaa6541a"),),
        "r1_peer_address_record_update", "Dual 6-byte peer-address record update with 0x14 flag stamp and nrf_log hexdump",
        ((0x00045970, "BL"), (0x00045ABE, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00049C64, 96, ((0x00049C64, 0x00049CC4, "3ba0080113a32ef7e8565cd3ac990ddebe715ed04b29ddb37ac87000051b24a7"),),
        "r1_algo_hr_timing_timeout", "HR timing timeout: stream unregister, GoMore gate 5 off, [RING] algo_hr_timing_timeout",
        (),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00048D9C, 96, ((0x00048D9C, 0x00048DFC, "610e7b2d98a33ae6c0f84e39a6213743aad1b4c11cee7d4589121da0da9d1190"),),
        "r1_health_activity_enable", "Health activity-mode enable: [RING] health_enabled log, GoMore gate 0 on, event-4 subscribe",
        ((0x0004A240, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0008E7D0, 94, ((0x0008E7D0, 0x0008E82E, "0fe40e1d121b57ebb30344db3ba088318aa80fb3bf222587f3ab10c5a806167d"),),
        "r1_service_touch_open", "Touch lease source-bit set; first open posts task event 2",
        ((0x0004621E, "BL"), (0x00046288, "BL"), (0x0004F9E8, "BL"), (0x00062296, "BL"), (0x0006A7A4, "BL"), (0x00084920, "BL"), (0x00092C40, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0006A1CC, 94, ((0x0006A1CC, 0x0006A22A, "152e27b7c075d7cdf0209695751e8f0c68d9615b7ddff0b3c6555e5f373dcfe5"),),
        "r1_product_sn_letter_decode", "Product-SN letter-to-digit decode (A-J/a-j) with 0xD fallback",
        ((0x0002F886, "BL"), (0x00041AFA, "BL"), (0x00041B3C, "BL"), (0x0004F200, "BL"), (0x000622A4, "BL"), (0x00062C08, "BL"), (0x0008E75A, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00054C58, 94, ((0x00054C58, 0x00054CB6, "7f05bd22c9775684f2dcfcbd48abd7d7cc5a60eb90e415e1006a80efd6327a04"),),
        "r1_named_gpio_output_set", "Named GPIO-output table dispatch (ppg_led_en/touch_ldo_en/ppg_reset_en/ship_mode_en/touch_rdy_out)",
        (),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00051368, 94, ((0x00051368, 0x000513C6, "231a97e5a112d8db77ba2fc88fc3dff925509229cb714d33c748909024a63326"),),
        "r1_touch_button_irq_process", "Touch/button IRQ top-half: ready poll, worker invoke, [RING] bc_touch_button diagnostic",
        ((0x0008E7AC, "B.W"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x000923B4, 92, ((0x000923B4, 0x00092410, "0458434e40289a408453b64141838f6caa655d821d6aa5c35e7e4eab09c3e707"),),
        "r1_thread_manager_sync_wait", "Thread-manager sync start: osThreadFlagsWait on bit 0x800000, [thread_manager] log",
        ((0x00046958, "BL"), (0x00091F56, "BL"), (0x000920EE, "BL"), (0x0009217A, "BL"), (0x0009227E, "BL"), (0x0009230E, "BL"), (0x000924F6, "BL"), (0x00092584, "BL"), (0x000926E0, "BL"), (0x000927CA, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0004D590, 92, ((0x0004D590, 0x0004D5EC, "f589a3c0a1ab9dc57a988b30475d1c60ff2fc1a19a89499b1d9cd79919fc3f42"),),
        "r1_app_ble_set_fast_mode_delayed", "BLE fast-mode variant scheduling conn*0x10000+1 delayed event",
        ((0x0004EE6A, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0004CC60, 92, ((0x0004CC60, 0x0004CCBC, "c09b407125ec5732152243231d0d39c7f0699a0390f7704d5d68ed7cd22338f4"),),
        "r1_glasses_tx_power_set", "Glasses link TX-power set over SVC 0x77 with [RING] glasses_tx_power_set success log",
        ((0x000453F4, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0004B234, 92, ((0x0004B234, 0x0004B290, "e8a07fb63d4ca3d302b2b1cd93922884d86e355edd2148bf2e4276bc20df3632"),),
        "r1_algo_spo2_timing_timeout", "SpO2 timing timeout: stream unregister, timer clear, [RING] algo_spo2_timing_timeout",
        (),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0004DE44, 90, ((0x0004DE44, 0x0004DE9E, "617a6c9957bef96c402c833ba60a4531786cee8c9685ac710457faa984736155"),),
        "r1_app_ble_set_slow_mode_again", "BLE slow-mode retry policy, 0x2C00-tick delayed schedule, [RING] log",
        ((0x0007F44A, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0004A3E8, 88, ((0x0004A3E8, 0x0004A440, "12a06e087ffac257a35968f3956c65a90abd2cb994965016ad948d3981a43d93"),),
        "r1_sleep_drop_guard", "Sleep-drop guard with [RING] no-living-confirm diagnostic",
        ((0x0004A76A, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0006A03C, 86, ((0x0006A03C, 0x0006A092, "07932107320bff91e7ae1dd99af3c65653d51ac458ec8b28fcfb08797607d591"),),
        "r1_touch_channel_average", "IQS7211E electrode byte-pair to u16 conversion and channel average (R1-owned ring-size/electrode data per provider boundary)",
        ((0x00030FD0, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x000503B4, 86, ((0x000503B4, 0x0005040A, "59cdd2d86abf7d040eab0cbb003319cb6a1971726f4c1b30287df206ae8d7b2b"),),
        "r1_nfc_chip_id_probe", "ST25DV NFC chip-id probe under I2C5 resource acquire with [RING] bc_nfc_st25dv log",
        ((0x0004F124, "BL"), (0x00062CEA, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0004EB80, 86, ((0x0004EB80, 0x0004EBD6, "921c60ee7f7353b5039b4e79c70d4e8d04e43df91d003d48228771c17b0e5c6a"),),
        "r1_touch_board_open", "Touch board-open rail/RDY sequence with 10/130/10/20 delays (matches recovered IQS7211E board-open order)",
        ((0x000466A8, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0003CD24, 86, ((0x0003CD24, 0x0003CD7A, "76e3e0708eb621a28c3e847344645ab29d3b4c6cabc9d8704890495880f4c727"),),
        "r1_temperature_sample_monitor", "Temperature pair-reduce consumer with counter persistence and config-byte 0x78 bit-0x10 escalation at 240",
        (),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x000830A8, 84, ((0x000830A8, 0x000830FC, "746d7a65dd823b34f644e8502b3dac79f4f01d34d1e5b0dc6575fc8f0742a898"),),
        "r1_proto_port_init", "Proto port init: callback registrations, [RING] proto_port_init initialized log",
        ((0x00082F7A, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0005C58C, 84, ((0x0005C58C, 0x0005C5E0, "9e252776bfeb423c3aa933de2f89cedd114e9f6d50430a93debfa36aed7c1c1c"),),
        "r1_ble_disconnect_attempt", "SVC 0x76 disconnect with [RING] Failed to disconnect connection diagnostic",
        (),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00043BD4, 84, ((0x00043BD4, 0x00043C28, "74d04e670cc066062c068f23c73c14512c44941bf78e4a7fd125739c814970d7"),),
        "r1_spo2_sync_clamp_future_ts", "SpO2 sync future-timestamp clamp with [RING] diagnostic",
        ((0x0004421A, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x000408B8, 84, ((0x000408B8, 0x0004090C, "2c557fb55ed6a11000cc473e766ba4fe6359133ceaa650df4e3fac832dd95e94"),),
        "r1_hrv_sync_clamp_future_ts", "HRV sync future-timestamp clamp with [RING] diagnostic",
        ((0x00040F46, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0003F9DC, 84, ((0x0003F9DC, 0x0003FA30, "14b7b183c463ce93e85741e04a2a46f7572db4362f0409fef03c076d9267c0e5"),),
        "r1_hr_sync_clamp_future_ts", "HR sync future-timestamp clamp with [RING] diagnostic",
        ((0x0004004A, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00084C0C, 82, ((0x00084C0C, 0x00084C5E, "f09c7a17ed32f9f2cd8f37bf87275e3cd847f0ee6db38f82ecd9185d5d20a97a"),),
        "r1_protocol_response_send_0x100", "Protocol response builder/sender for the 0x100 event window",
        ((0x0008388C, "BL"), (0x000838B0, "BL"), (0x000838D4, "BL"), (0x00083924, "BL"), (0x000839D0, "BL"), (0x000839F4, "BL"), (0x00083C7C, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00083820, 82, ((0x00083820, 0x00083872, "92099f382cf6c93ff29919c03dc81b9541713ae2ec50385de979ab9920d28257"),),
        "r1_protocol_payload_copy_send", "Heap-copy payload append and forward to the 0x200 response sender",
        ((0x00083556, "BL"), (0x000835E4, "BL"), (0x00083672, "BL"), (0x000836E2, "BL"), (0x0008374A, "BL"), (0x000837D8, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00082EF4, 82, ((0x00082EF4, 0x00082F46, "f596a1b561640e61b89ffcfb94c0751d69a6132fd630a60c8d7d60625ef86ad0"),),
        "r1_protocol_response_send_0x200", "Protocol response builder/sender for the 0x200 event window",
        ((0x0008385A, "BL"), (0x00083950, "BL"), (0x00083992, "BL"), (0x00083C40, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0006A244, 82, ((0x0006A244, 0x0006A296, "e34d48e2ccd0cf018c165ba066a78c0b312fb00e0eea88477abd9c925d356194"),),
        "r1_hardware_variant_bsn_detect", "One-shot BSN B210..A prefix detection latch",
        ((0x0004F1FA, "BL"), (0x00072B9E, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x000624F4, 82, ((0x000624F4, 0x00062546, "b9a0c33ad87c561ab5d1b3c8ed12cbc2694bf47901dbd418fc9ab235c0d882d0"),),
        "r1_legacy_sn_verify_command", "Legacy command: SN compare (sub 0) and SN read (sub 1) with bounded reply",
        ((0x0004E30C, "BL"), (0x000626D0, "B.W"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0004F260, 82, ((0x0004F260, 0x0004F286, "2e7dcef4554b19b0fc532c618367014d0d893909257e2ab3d9c52e198fd0184e"), (0x0004F288, 0x0004F2B4, "aa9df575ceb095b1c70d168eacc53665be0c41ad88f983619c7568178fe52bb5"),),
        "r1_eat_command_tokenize", "eAT frame tokenizer (strtok, two 0x80 slots) feeding the command dispatcher",
        ((0x00045178, "BL"), (0x00045FAA, "BL"), (0x00088444, "B.W"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00049E5C, 82, ((0x00049E5C, 0x00049EAE, "11d9ee10421a85667ce5008f89fab1253d2f0eb81e7b888061997b5c03e72b2c"),),
        "r1_algo_hrv_timing_timeout", "HRV timing timeout: [RING] algo_hrv_timing_timeout, state clear",
        (),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00048C68, 82, ((0x00048C68, 0x00048CBA, "c85444410ab7ca5108708a936114b640d21f44e1a56491cb218a8a1fb2e60947"),),
        "r1_factory_mode_stop", "Factory/aging mode stop: timer cancel, stream unregisters, counter persist",
        ((0x0003CD72, "BL"), (0x000623D8, "BL"), (0x000623FE, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0003D834, 82, ((0x0003D834, 0x0003D886, "193f4ac1e804e1639b680e3c8c4d4190e648edde0229df9ca13234ecc84490a8"),),
        "r1_battery_level_average", "8-slot battery-percent average with min/max rejection",
        ((0x000320F0, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00092440, 80, ((0x00092440, 0x00092490, "25872037723d0cad6e48924a971975aecbf199465bf62a88a401c8f490cb802e"),),
        "r1_thread_manager_sync_signal", "Thread-manager sync end: osEventFlagsSet 1<<id, [thread_manager] log",
        ((0x00046980, "BL"), (0x00091F74, "BL"), (0x00092104, "BL"), (0x00092190, "BL"), (0x00092294, "BL"), (0x00092338, "BL"), (0x00092518, "BL"), (0x000925B2, "BL"), (0x00092720, "BL"), (0x000927E4, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0005B23C, 80, ((0x0005B23C, 0x0005B28C, "285fac8e97bff70248473cf0f79f00c89566cab4d62dc4790c9f1a55ba21ba92"),),
        "r1_sleep_storage_delete_all", "Sleep storage delete-all with count diagnostic",
        ((0x0008B1D6, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0003DDA0, 80, ((0x0003DDA0, 0x0003DDF0, "4902b352c891bf1ac77ce23f3a555315a766e410710d845fc6614268f73a3235"),),
        "r1_battery_voltage_average", "8-slot 16-bit battery-voltage average with min/max rejection into slot 0x18",
        ((0x000320B8, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x000736B8, 78, ((0x000736B8, 0x00073706, "43c614544feaa2ebfc84fd8070d672bf05141c83c931ecee4fdf516d1b62802d"),),
        "r1_config_record_refresh", "0x34-byte config record read, magic-word compare, erase-and-rewrite on mismatch",
        ((0x0004CB5A, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0006244E, 78, ((0x0006244E, 0x0006249C, "ae31e7cd7cdb6b5f529d58718ed1a81dcf2f0730123786b42de594c64bf353a8"),),
        "r1_legacy_bsn_verify_command", "Legacy command: BSN compare (sub 0) and BSN read (sub 1) with bounded reply",
        ((0x0004E302, "BL"), (0x000626C4, "B.W"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0004F10C, 78, ((0x0004F10C, 0x0004F15A, "0ada74780ff50e3964b40236be53cdfba54d0503759f39f9ff71fbbf94eb7188"),),
        "r1_factory_device_info_query", "Factory device-info composition: motion, Goodix, touch, NFC, YHM identity probes in one reply",
        (),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00073634, 76, ((0x00073634, 0x00073680, "1e513aaceb5b40b6567ad160098361f3531a1724905f32b0cec841e740ebe46e"),),
        "r1_factory_read_lookup", "Factory read: name-keyed table search with bounds-checked record copy",
        ((0x0004F3E6, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00054B40, 76, ((0x00054B40, 0x00054B8C, "0efddded2558c8f5bca657409197f3e63f47395dcd9ada846723cb07e4428368"),),
        "r1_named_gpiote_irq_unregister", "Named GPIOTE input unregister: nrfx_gpiote_in_event_disable + in_uninit (acc_int_1/ppg_int/touch_rdy_in/mcu_reset_irq/pmic_irq/nfc_gpo_irq/device_stacmd_irq)",
        (),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0003BCA8, 76, ((0x0003BCA8, 0x0003BCF4, "ebf29c0b8bba45cdf7800b41e9ff3e82eb00c3f38db2269bb44ea25bec9be30b"),),
        "r1_ack_record_insert", "Acknowledgement-table insert into the pinned 32-entry 0x14-byte record table with tick stamp",
        ((0x00083B50, "BL"), (0x00083B74, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x000836BA, 74, ((0x000836BA, 0x00083704, "cc86c2058458ac3846fad7212d40e218711763c30447962edbb8a765654d5a63"),),
        "r1_event_post_0x601", "Event 0x601 poster: empty notify or payload path via the copy-send helper",
        ((0x0008DB54, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0008156C, 72, ((0x0008156C, 0x000815B4, "e769644cf7d08955933a6438c949635752e62dab2aef7f81ba6f528c3b475991"),),
        "r1_sensor_threshold_flag_latch", "Tri-axis threshold latch setting config byte bits 1/2/4 below reference",
        (),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0004F160, 72, ((0x0004F160, 0x0004F1A8, "e8de174a5cf7400078eb7831092c2b2c29d6981e6cbdd064476d30c35b34ce72"),),
        "r1_version_query_response", "Firmware/hardware version reply (2.2.6.0009 / 603MV1.9.3) via the eAT formatter",
        (),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0004A21C, 72, ((0x0004A21C, 0x0004A24C, "2dc387ca29b4868c471e50c1ba5ba1f774b8f34479c9a72fc3f7828bd07d612a"),),
        "r1_health_services_init", "Health service init orchestrator over module inits and event-4 subscribe",
        ((0x000925AC, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0008E154, 70, ((0x0008E154, 0x0008E19A, "f9d9335797355cc8ebb4ad70da287bd53d4857217cf60ade40688a7db80ee294"),),
        "r1_service_sleep_status_set", "Sleep-status setter with [RING] service_sleep_status log",
        ((0x00042966, "B.W"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0008B834, 70, ((0x0008B834, 0x0008B87A, "cd41222be7d3b6e70afdd9f0b3964ee96cf18f3c631d9bf5194f87fec9aac94c"),),
        "r1_service_health_report_set", "Health-proto report-enable setter with [RING] log",
        ((0x00082EE0, "B.W"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0008A5FC, 70, ((0x0008A5FC, 0x0008A642, "98cd5324cac6c20923c7dbd782122a7ace2483a01d464a53544e02452598a8e3"),),
        "r1_rtt_write_blocking", "SEGGER RTT channel-0 write with 3x64us retry and latch-off",
        (),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00050578, 70, ((0x00050578, 0x000505BE, "0e5ce23c9f5ea7a64b5a68a9f1fc6576f6b884f5faa90de61e203f516085a22f"),),
        "r1_pmic_device_handles_init", "Lazy device-handle resolution: device_stacmd, ship_mode_en, device_stacmd_irq, vpmic_isns_adc",
        ((0x00050392, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0004E5BC, 70, ((0x0004E5BC, 0x0004E602, "f687336eb7e1c19fb2e567c70c7c4c2d8dee1707f56c4a399382f3a2e8304b22"),),
        "r1_fatal_error_log", "R1 fatal-error logger ([RING] Fatal error, error code: 0x%08x) per briefing identity",
        ((0x0003E030, "BL"), (0x0003E194, "B.W"), (0x0003E814, "BL"), (0x0003E81C, "BL"), (0x0003E82A, "BL"), (0x0003E870, "BL"), (0x00048A56, "BL"), (0x00048AAA, "BL"), (0x0004C84A, "BL"), (0x0004C85A, "BL"), (0x0004C914, "BL"), (0x0004C93C, "BL"), (0x0004C9A8, "B.W"), (0x0004CC70, "BL"), (0x0004D134, "BL"), (0x0004D4E4, "BL"), (0x0004D512, "BL"), (0x0004D530, "B.W"), (0x0004D546, "BL"), (0x0004DF28, "BL"), (0x0004DF4C, "BL"), (0x0004E180, "BL"), (0x0004E1A4, "BL"), (0x0004E1CE, "B.W"), (0x0004E49C, "BL"), (0x0004E4BC, "BL"), (0x0004E508, "BL"), (0x0004E516, "BL"), (0x0004E67C, "BL"), (0x0004E6DE, "BL"), (0x0004E9CA, "B.W"), (0x0004F16A, "BL"), (0x00052DBA, "B.W"), (0x0005327C, "BL"), (0x0005389A, "B.W"), (0x000539C2, "BL"), (0x000539D4, "BL"), (0x000539F4, "BL"), (0x00053A3C, "BL"), (0x00053A52, "BL"), (0x000548B4, "BL"), (0x000548CA, "BL"), (0x00054A1C, "BL"), (0x00054F58, "BL"), (0x00054F68, "BL"), (0x000550A4, "BL"), (0x00055166, "BL"), (0x000552CC, "BL"), (0x00055316, "BL"), (0x00056376, "BL"), (0x00056672, "BL"), (0x0005667E, "BL"), (0x00066C6A, "BL"), (0x00066CD4, "BL"), (0x00066CE0, "BL"), (0x00075F7A, "BL"), (0x00075F92, "BL"), (0x00075F9C, "BL"), (0x00075FF0, "BL"), (0x00079DC8, "B.W"), (0x0007A3B8, "B.W"), (0x0007A512, "B.W"), (0x0007FB38, "BL"), (0x0007FB68, "B.W"), (0x0007FBBC, "BL"), (0x0007FBCE, "BL"), (0x0007FE44, "B.W"), (0x000882C6, "B.W"), (0x0009083A, "B.W"), (0x00090896, "B.W"), (0x00095E8E, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x000738A8, 68, ((0x000738A8, 0x000738EC, "6dc2ff34388aa88c5b8888d90905dd91cd23723bc39aac3543d4660b9fcabd97"),),
        "r1_peer_address_record_write", "0x34-byte peer-address record write with magic stamp and post-write hook",
        ((0x00046052, "BL"), (0x0004D9E2, "BL"), (0x000844E6, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0004C678, 68, ((0x0004C678, 0x0004C6BC, "6780bbe91d384a39de17dccd23840eb2145d7492a7c6d782a1f42e0ab4809541"),),
        "r1_touch_status_report", "Touch status 0x8C0900 packet to the glasses link via tx-queue dispatch type 0",
        ((0x000437EC, "BL"), (0x000453EA, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00083C20, 66, ((0x00083C20, 0x00083C62, "0b2273f7ac0c7af004c2ea3645de9588ad9022c87d21036339794e533154fd2f"),),
        "r1_event_0x202_response_send", "Event 0x202 response: empty ack or payload send on the phone connection",
        ((0x0008B9E8, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00082B54, 66, ((0x00082B54, 0x00082B96, "47d07efbb8f683ea9daf1f0effc47cc917dbf1c43416411f0355ea2f54912271"),),
        "r1_protocol_ack_header_send", "Protocol ack/header builder (xor-1 or-2 flags) over r1_protocol_send_response",
        ((0x0008473A, "BL"), (0x00084C74, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00062BEC, 66, ((0x00062BEC, 0x00062C2E, "d5fc9843211eed98b59850b3025560991e7a656fde0e6495b8a8e403667f40eb"),),
        "r1_legacy_sn_derived_command", "Legacy command using the SN letter decode with fallback read path",
        ((0x0004E420, "BL"), (0x000627CA, "B.W"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00054AFC, 64, ((0x00054AFC, 0x00054B3C, "dbef2eee52bcfe8250457b6b785c687425fde2dfdda3a1c9624553427c00713a"),),
        "r1_named_gpiote_irq_register", "Named GPIOTE input callback registration by name",
        (),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00050708, 64, ((0x00050708, 0x00050748, "f24cc674adecfdd302161eacdafcba00318705752f789cda33b77a7b41d27aec"),),
        "r1_ship_mode_pin_pulse", "GPIO P0.05 output-set, 200-ms hold, release (ship-mode/PMIC line control)",
        ((0x00096D9C, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0004CB58, 64, ((0x0004CB58, 0x0004CB98, "11951eef1487de360f37188bc1c1f0173defdfa6aaa18c77d76e236162a24ca0"),),
        "r1_peer_record_commit", "Peer record field pack, store, and address-flag update",
        ((0x00091F6A, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x000489E6, 64, ((0x000489E6, 0x00048A26, "68f49dfeb985b84fe71745240c840bbd455e79e0785e811ae9faab8f8685440f"),),
        "r1_advertising_params_init", "Advertising parameter init: interval 0xA0, timeout 0/6000 by config byte 0x70, duration 0x640",
        ((0x00048A96, "BL"), (0x000523A2, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00045D00, 64, ((0x00045D00, 0x00045D40, "92db1c361d95c960b36ad51cac10eb14c5006a7eff424e199441491842943e4f"),),
        "r1_thread_hardware_init_log_a", "Thread hardware-init trace hook ([RING] thread_hardware_init)",
        ((0x0004696E, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x00045C84, 64, ((0x00045C84, 0x00045CC4, "1edeb80f14582869d0857cdcd8a145162b83e27893b26fa18a7cc10d653418a3"),),
        "r1_thread_hardware_init_log_b", "Thread hardware-init trace hook, second instance",
        ((0x000926F6, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
    _function(
        0x0003D764, 64, ((0x0003D764, 0x0003D7A4, "db1870e67aa89d04b894922e1a8d730e0b0d73df2f14cd7479b5cb275141da3c"),),
        "r1_peer_address_flag_update", "6-byte address compare against stored constants and flag-byte 0x14 update",
        ((0x0004CB8A, "BL"), (0x0004CB92, "BL"),),
        "r1_product_specific", "clean_room_behavior_only",
    ),
)

NORDIC_FRONTIER_64_127_FUNCTIONS = (
    _function(
        0x00087ED0, 72, ((0x00087ED0, 0x00087F18, "8a6f4fe9d0b28bf0eb2fbb78cadb7b68b07c53f47930577e12b42431911cc035"),),
        "reattempt_previous_operations", "peer_database.c write-buffer store retry: exact match (m_pending_store, PM_FLASH_BUFFERS=4 records, store_busy/store_flash_full bits, write_buf_store_in_event)",
        ((0x0007E568, "B.W"),),
        "nordic_nrf5_sdk_17_1_0", "use_nordic_sdk",
    ),
)

TOOLCHAIN_FRONTIER_64_127_FUNCTIONS = (
    _function(
        0x00090E8C, 110, ((0x00090E8C, 0x00090EFA, "d4007c62206200d036f94827c3cc98bc58994922aba63e175e67e41295ea4fcc"),),
        "sqrt", "Double sqrt wrapper: binary64_sqrt plus EDOM via errno_set when result is NaN/Inf and input is finite",
        ((0x00039C2E, "BL"),),
        "arm_toolchain_runtime", "use_toolchain_runtime",
    ),
)

GOMORE_FRONTIER_64_127_FUNCTIONS = (
    _function(
        0x000655A8, 126, ((0x000655A8, 0x00065626, "012d6c85b36eebf4a5eee4ada8a8e72509653209be9100a282fbe270d198f039"),),
        "", "GoMore dense-layer composition with optional dual dequant-bias, scale multiply, and map activation",
        ((0x000654EA, "BL"),),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x00094300, 122, ((0x00094300, 0x0009437A, "b621598069e358cf71c6f3e9d894810f7acfa92a5f7b7ca018a617769fbd3f60"),),
        "", "GoMore 90-slot decimated byte-ring writer with float clamp at -0.109375/0.0",
        ((0x000940CE, "BL"),),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x00091EDC, 114, ((0x00091EDC, 0x00091F4E, "a0ec6501e82d36331646de40423df02a48730226a2953afc58e71cecaaac81d6"),),
        "", "GoMore descriptor softmax executor (expf sum/normalize), called only from gated GoMore 0x88450",
        ((0x0008884C, "BL"),),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x00065304, 114, ((0x00065304, 0x00065376, "546598df969857c3ee0ef3e80f92973bfa00f7c66cc6af7d68496b1fe290d714"),),
        "", "GoMore 2-D layer executor with per-row int16 dequant bias add",
        ((0x000884CE, "BL"), (0x0008852A, "BL"), (0x00088582, "BL"), (0x000885DA, "BL"), (0x00088654, "BL"), (0x000886AC, "BL"), (0x00088704, "BL"),),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x00065376, 112, ((0x00065376, 0x000653E6, "4e334616103c77d05d09c597e5b82d695c7641091d4f98407af84522056c1001"),),
        "", "GoMore sequential layer-chain runner with per-stage output handoff",
        ((0x000887EE, "BL"),),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x00094938, 110, ((0x00094938, 0x000949A6, "28cfecb79e2e648599812680a2bb9fc03427c839ea9338f20bb23b1f277fd65c"),),
        "", "GoMore 20-slot modulo-5 state recorder with 0xFF sentinel folding",
        ((0x000606B6, "BL"), (0x000606D6, "BL"),),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x0008EEBA, 110, ((0x0008EEBA, 0x0008EF28, "a68369c62867673bf3d39408f80a8a07801b1c39501d8a1668d3eb6a2cce7ac1"),),
        "", "GoMore 0x10-stride record window compaction (drop entries older than 25)",
        ((0x000485AE, "BL"), (0x00069892, "BL"), (0x000698E6, "BL"),),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x00065538, 108, ((0x00065538, 0x000655A4, "e943a2f94b3dd4b5273a05efb7b7ae0e2be4d63bd1b36d69631ad0c2303f5f68"),),
        "", "GoMore dense layer with optional dequant bias, no scale path, map activation",
        ((0x00065430, "BL"), (0x0006548C, "BL"),),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x0005D560, 108, ((0x0005D560, 0x0005D5CC, "2c3b7bb6bbffafd312012dc6df8b2b7a389fc492ffbaf9626ebd84017ff085cf"),),
        "", "GoMore 4-field comma-string parse and prefix compare (auth/version token match)",
        ((0x0008EB2E, "BL"), (0x0008EB3A, "BL"),),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x00091E02, 106, ((0x00091E02, 0x00091E6C, "937cfcbf6eb18a867597e5ef32c3b43a9245038e6cc10687a06664f3501dea12"),),
        "", "GoMore descriptor strided view/offset constructor (caller chain rooted at gated 0x653E6)",
        ((0x0005A3F6, "BL"), (0x0005A404, "BL"),),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x000728D4, 104, ((0x000728D4, 0x0007293C, "cd0c0e59f56abf96332d294be27d76631666185084c8ff76da57d0433df3f798"),),
        "", "GoMore float scoring helper with expf-based logistic term (constants 64.0/0.15/0.775)",
        ((0x0002F136, "BL"), (0x0002F14E, "BL"), (0x0002F16E, "BL"), (0x0002F18A, "BL"), (0x0002F1A2, "BL"),),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x00091D30, 102, ((0x00091D30, 0x00091D96, "6119ccdf030d1488ef994364eb51c4d198b5edead5aeff6c9239583a129f77d8"),),
        "", "GoMore quantized int8-by-float dot executor with float bias init (same caller island as gated 0x9196E)",
        ((0x0006554C, "BL"), (0x00065558, "BL"), (0x000655C0, "BL"), (0x000655CC, "BL"), (0x000656C6, "BL"),),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x00091CCC, 98, ((0x00091CCC, 0x00091D2E, "abb6bd5271ce26a0d8f6be8512606b8befe5abec9c0b44530abe93bb7019ee1e"),),
        "", "GoMore leaky-ReLU executor over float descriptor tensors",
        ((0x00065694, "BL"),),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x0006208C, 98, ((0x0006208C, 0x000620EE, "e65b24c39ebd2c1c83062782ff656423bb6f98ad3351bb5a2a534f0dfe264e6c"),),
        "", "GoMore float standard-deviation helper (powf/sqrtf over mean deviations)",
        ((0x00064408, "BL"), (0x00068866, "BL"), (0x00068BCA, "BL"),),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x000656AA, 96, ((0x000656AA, 0x0006570A, "b60512f00d43fcf059ed2838899c649fe7d25f7e09a1169ea2ebe1480c0bdd53"),),
        "", "GoMore dense executor with per-row int16 dequant bias add (1-D)",
        ((0x0008878C, "BL"), (0x000887A8, "BL"), (0x0008880A, "BL"), (0x00088842, "BL"),),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x00035D12, 92, ((0x00035D12, 0x00035D6E, "3d1432e7a8a93be6cbd3d5c32df6dcd4674853de31b011cd6364d6cb122843f3"),),
        "", "Pointer-installed 4-D tensor permute executor (Thumb ptr 0x35D13 stored by GoMore graph builders 0x2874C/0x2966C)",
        (),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x00057C84, 88, ((0x00057C84, 0x00057CDC, "47fc61f6e8f4358b9ec4c9f55f4ad74d48d815196b81dcd5d460be45ae701041"),),
        "", "GoMore binding/auth step: counter bump, window check, error record via 0x5D31E (sibling of gated model-ID binding 0x57B38)",
        (),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x0008EC7C, 86, ((0x0008EC7C, 0x0008ECD2, "4efed352e225ae769dc699bbb41c7a9684b6bbca5f7c3ab7c5d8438413fcfb47"),),
        "", "GoMore four-way sub-state dispatch over offsets 0xD14/0xD98/0x13F8/0x391C",
        ((0x0004C04E, "BL"),),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x000919BA, 84, ((0x000919BA, 0x00091A0E, "cf639b8e8387ef9d8df750681a629c7935897dbaa4c2744432fb6e7351b427b2"),),
        "", "GoMore int16 dequant bias-add executor over descriptors",
        ((0x0006556A, "BL"), (0x00065578, "BL"), (0x000655DE, "BL"), (0x000655EC, "BL"),),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x0006562C, 78, ((0x0006562C, 0x0006567A, "3885002ca9ab5b0281c99d694c08fd26ca65f024fd8fe292bf81f3813a04566c"),),
        "", "GoMore layer composition: map, scale, float add",
        ((0x00065518, "BL"),),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x00064774, 78, ((0x00064774, 0x000647C2, "30e87473ebd71029fdd6371274893212a12e71b47e2a04960eb20a50c8236970"),),
        "", "GoMore max first-difference index scan",
        ((0x000485FC, "BL"),),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x00062034, 78, ((0x00062034, 0x00062082, "5e8fde790b5040afb3540d000548e711f62cd00fdb8ddeedb5f25e34e0b80f7b"),),
        "", "GoMore float median via qsort",
        ((0x00064538, "BL"), (0x00064712, "BL"),),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x000967C8, 76, ((0x000967C8, 0x00096814, "2abc0d466d463cd9083db0fe25067acf2bebb7e6f4484c36532ed5190801a863"),),
        "", "GoMore binding-window/state validity check over shared 0x72ACE clock",
        ((0x0006FEE8, "BL"), (0x00094454, "BL"),),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x00091C80, 76, ((0x00091C80, 0x00091CCC, "3694f3c3ee4159952e40ed987b1ac770e99241b2952a547a27463b39c6a16fd5"),),
        "", "GoMore elementwise float multiply executor over descriptors",
        ((0x000655FA, "BL"), (0x0006563E, "BL"), (0x00065658, "BL"),),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x00091A0E, 72, ((0x00091A0E, 0x00091A56, "81f49b6782c223599f7ed9bbc3cc2efc3a66dfc5ff88a1649d408e530862f639"),),
        "", "GoMore elementwise function-map executor over descriptors",
        ((0x000655A0, "B.W"), (0x00065622, "B.W"), (0x0006564C, "BL"),),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x0005D31E, 66, ((0x0005D31E, 0x0005D360, "b19b0636327b566265890563f5d16bc6e9cac9543c7ce2dfb0efff2563a79e52"),),
        "", "GoMore auth error-scan and round-4 finalize (callers include gated model-ID binding 0x57B38)",
        ((0x00057B6E, "BL"), (0x00057BA8, "BL"), (0x00057BC2, "BL"), (0x00057BD2, "BL"), (0x00057C68, "BL"), (0x00057C7A, "BL"), (0x00057CBC, "BL"), (0x00057CD0, "BL"), (0x00074D3A, "BL"), (0x00074D4C, "BL"),),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x0004EC9C, 66, ((0x0004EC9C, 0x0004ECDE, "cb6c99c90b1a934e9cdcc14f03554b6857aef425b1fbfcab5b09fa494e8415cb"),),
        "", "GoMore float argmax scan over descriptor tensor range",
        ((0x0006465C, "BL"),),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x00057C44, 64, ((0x00057C44, 0x00057C84, "abd81a8414b37d3031d0da68ff4ac2eb465211f4fd5cf867c91336871538d9e3"),),
        "", "GoMore auth step with 0xFC13 error stamp (sibling of gated 0x57B38 path)",
        (),
        "gomore_health_algorithm_candidate", "vendor_source_required_not_redistributable",
    ),
)

GOODIX_FRONTIER_64_127_FUNCTIONS = (
    _function(
        0x000419C8, 120, ((0x000419C8, 0x00041A40, "5b035c9da9f946e3ae0b797139298c3474546cf9cbd57d6195a25674b7a3134f"),),
        "", "Goodix threshold-crossing peak accumulator over int32 sample arrays",
        ((0x00034456, "BL"), (0x00034480, "BL"),),
        "goodix_gh3x2x_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x0003DF18, 104, ((0x0003DF18, 0x0003DF80, "b028664143432659f1722c6eb266cc7885a2dad5ab54b05abc9a8abcd2402f02"),),
        "", "Goodix per-channel state zero-init helper (0x19/0x7D counts via 0x6635C)",
        ((0x0005CDA6, "BL"), (0x0005CDB0, "BL"),),
        "goodix_gh3x2x_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x0005CD90, 102, ((0x0005CD90, 0x0005CDF6, "6812dc278481be0a4585d9aab464cf0609e84a5ea536d7b3e35eed2172570b4f"),),
        "", "Goodix 0x104-stride session-buffer init driver",
        ((0x00037290, "BL"),),
        "goodix_gh3x2x_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x0003727C, 100, ((0x0003727C, 0x000372B0, "472f8543abd0b778d138d8c624515b8fbb2f24715b0e9af0873aaae85ddc0001"),),
        "", "Goodix session allocate-and-init (sensor-algorithm heap 0x104/0x18 blocks)",
        ((0x0006EBE0, "BL"),),
        "goodix_gh3x2x_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x00034AA0, 98, ((0x00034AA0, 0x00034B02, "4ca63a148e08c4df81ca12259c62ee45e5a16f1605eb0046eed454a494f1693b"),),
        "", "Goodix per-channel 0x28-record allocation and field init",
        ((0x0006EC0C, "BL"),),
        "goodix_gh3x2x_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x0006EB30, 94, ((0x0006EB30, 0x0006EB8E, "88eabc5d3a85dade93a9d18d458a795b6bffeae66370d2a9fb947c7cf7a3420a"),),
        "", "Goodix algorithm session teardown: six sub-frees plus sensor-algorithm heap free",
        ((0x0002CFDA, "BL"),),
        "goodix_gh3x2x_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x0006CC60, 88, ((0x0006CC60, 0x0006CCB8, "84dd1d7c5933cb50338bc0a98e4d4a75f67e103e4a745d0982f2e533c571849f"),),
        "", "Goodix driver teardown: gated 0x29BBC loop, 0x29C74 frees, sensor-algorithm heap free",
        ((0x0002C936, "BL"),),
        "goodix_gh3x2x_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x00032744, 86, ((0x00032744, 0x00032780, "05b5605288d198dcd001cfabd8098adaee2c41baa2d4f16c03a14f9086367950"),),
        "", "Goodix float channel-scale/copy helper (caller gated 0x766AC)",
        ((0x00076796, "BL"),),
        "goodix_gh3x2x_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x0002AF32, 80, ((0x0002AF32, 0x0002AF82, "a86126c03a080aabc1ffa1badabc829ec3b2ecd98734432e17d78b19ee3eae0e"),),
        "", "Goodix packed half-word lane update inside the 0x3000-windowed register-write path (caller gated 0x2AEDC)",
        ((0x0002B0AE, "BL"),),
        "goodix_gh3x2x_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x00091890, 78, ((0x00091890, 0x000918DE, "59bada2b6a0d19e08070ad038799414c9a08c77114ccd9d41d39a38ef9714063"),),
        "", "Goodix 0x104-stride session-buffer teardown/zero driver",
        ((0x00037EA8, "BL"),),
        "goodix_gh3x2x_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x0006F920, 64, ((0x0006F920, 0x0006F960, "d449353a4447899dc82337a09609f3beae17a4d80e700799c282a03055f3a3da"),),
        "", "Goodix 6-byte record iteration with callback and >100-count trap",
        ((0x0002DE30, "BL"),),
        "goodix_gh3x2x_candidate", "vendor_source_required_not_redistributable",
    ),
)

YHM_FRONTIER_64_127_FUNCTIONS = (
    _function(
        0x0003529A, 96, ((0x0003529A, 0x000352BA, "02e9c88c541f8e8f9727b9b286e6a38408e946a06726108e5722fd748a676f3b"), (0x000352CA, 0x0003530A, "097305c9b1213bc95b279a3ff916d085340cab92057e964724a42c597eae53ba"),),
        "", "YHM2710 register-6 nibble-to-enum decode over the single-wire transaction helpers (island shared with gated 0x3530C/0x35508/0x355BC)",
        ((0x00035274, "BL"),),
        "yhmicros_yhm2710_candidate", "vendor_source_required_not_redistributable",
    ),
    _function(
        0x00035760, 78, ((0x00035760, 0x00035766, "f34358d99aab6f335322dd6e2f8619f823a9f889b1e0fc4862e674f903f529c8"),),
        "", "YHM2710 single-wire write transaction: 3-byte frame, device-registry slot-0x14 dispatch, power release, completion callback",
        ((0x00035104, "BL"), (0x00035162, "BL"), (0x00035172, "BL"), (0x00035182, "BL"), (0x00035192, "BL"), (0x000351A2, "BL"), (0x000354A0, "BL"), (0x0003557C, "BL"), (0x000355A2, "BL"), (0x000355B6, "BL"), (0x00035620, "BL"), (0x00035692, "BL"), (0x0003576C, "BL"),),
        "yhmicros_yhm2710_candidate", "vendor_source_required_not_redistributable",
    ),
)

DEVICE_REGISTRY_FRONTIER_64_127_FUNCTIONS = (
    _function(
        0x0005D998, 104, ((0x0005D998, 0x0005DA00, "2e8cffcb32af1849cda9afd9fcc116913698d85b098921beb97d77405b21a9fa"),),
        "", "Intrusive offset-list remove shared by the named-registry and sensor-stream frameworks (0x5D8xx machinery)",
        ((0x00089BD2, "BL"), (0x00089CC6, "BL"), (0x0008A3CA, "BL"),),
        "unknown_generic_device_registry_candidate", "investigate_before_implementing",
    ),
    _function(
        0x0005D21E, 68, ((0x0005D21E, 0x0005D242, "039fad051b5fccab86cff3c9432cf50188e21a464a82ada00468a4b701320b4f"),),
        "", "0xAE request-record fill and registry slot-0x14 dispatch",
        ((0x0005D218, "BL"),),
        "unknown_generic_device_registry_candidate", "investigate_before_implementing",
    ),
)

SENSOR_STREAM_FRONTIER_64_127_FUNCTIONS = (
    _function(
        0x0007D0D8, 122, ((0x0007D0D8, 0x0007D12A, "c20bf5d3324457c8d20d3f43911a1c641f107bd7d040a2b7e1cad7ec09737865"), (0x0007D12C, 0x0007D154, "bfdbcb70a0462b64ed894acd2a8fe706ab32dec80c1fc321f8909548ea8494ca"),),
        "", "Sensor-stream sample-buffer rate resize/copy helper named in the framework boundary doc",
        ((0x000899F4, "BL"), (0x0008A0BA, "BL"), (0x0008A2A8, "BL"),),
        "unknown_sensor_stream_framework_candidate", "investigate_before_implementing",
    ),
    _function(
        0x000897E8, 100, ((0x000897E8, 0x0008984C, "b4680d6548180440c685f0a4f61b496aa5e95214f6ae12795c4d920cbc4a9f92"),),
        "", "Sensor-stream register-by-name front end; register_not_find_obj diagnostic matches the framework's unregister_not_find_obj family",
        ((0x0003D110, "BL"), (0x0003D17E, "BL"), (0x0003D49E, "BL"), (0x00048C26, "BL"), (0x00048C3C, "BL"), (0x000493DE, "BL"), (0x0004948C, "BL"), (0x000494AC, "BL"), (0x000494CC, "BL"), (0x000494EC, "BL"), (0x000497EA, "BL"), (0x000497FA, "BL"), (0x00049B0C, "BL"), (0x00049FD0, "BL"), (0x0004AB10, "BL"), (0x0004AFBA, "BL"), (0x0004B6E8, "BL"), (0x0004BB70, "BL"), (0x0004BC1E, "BL"), (0x0004C5DE, "BL"), (0x0004ED48, "BL"), (0x0004F2F0, "BL"), (0x0004F35C, "BL"), (0x0004F8F4, "BL"), (0x0004F960, "BL"), (0x00062A02, "BL"), (0x00062CAE, "BL"), (0x0006A630, "BL"), (0x00090FCA, "BL"),),
        "unknown_sensor_stream_framework_candidate", "investigate_before_implementing",
    ),
    _function(
        0x00089D9C, 92, ((0x00089D9C, 0x00089DF8, "9663abc8ebec524a3683abe2f7b3134822e7299698bb7004ca4fde95efe633be"),),
        "", "Sensor-stream object list insert with pool init; list_insert_fail diagnostic",
        ((0x00089752, "BL"),),
        "unknown_sensor_stream_framework_candidate", "investigate_before_implementing",
    ),
    _function(
        0x0008A404, 84, ((0x0008A404, 0x0008A458, "adf7fe540692e1131f7085fc9f0f056a61e26f72bb2518fd65a29976c63edc1b"),),
        "", "Sensor-stream timer expiry processing: tick stamp, callback, deferred cleanup routing",
        ((0x0008A4B2, "BL"),),
        "unknown_sensor_stream_framework_candidate", "investigate_before_implementing",
    ),
    _function(
        0x0008A368, 84, ((0x0008A368, 0x0008A3BC, "f755358f92315b2c7068bdf98877ec14f203a84917c28c3595d3c50b6f77115f"),),
        "", "Sensor-stream object allocation from pool 0x5D94A with field init and timer kick",
        ((0x000495A4, "BL"), (0x000899B4, "BL"),),
        "unknown_sensor_stream_framework_candidate", "investigate_before_implementing",
    ),
    _function(
        0x0008A310, 84, ((0x0008A310, 0x0008A364, "e827de79bcd3ff880e0245fd3dcd2399aa6eece7318db2485635424114d164f8"),),
        "", "Sensor-stream timer object allocation from pool 0x5D90E with field init and timer kick",
        ((0x0003D12A, "BL"), (0x0003D192, "BL"), (0x00048C12, "BL"), (0x000498DA, "BL"), (0x00049B20, "BL"), (0x00049FB4, "BL"), (0x0004A51A, "BL"), (0x0004A8EC, "BL"), (0x0004AFD0, "BL"), (0x0004B3B0, "BL"), (0x0004B7D4, "BL"), (0x0004C55A, "BL"), (0x000899C4, "BL"), (0x0008A578, "B.W"),),
        "unknown_sensor_stream_framework_candidate", "investigate_before_implementing",
    ),
)

QUANTIZED_RUNTIME_FRONTIER_64_127_FUNCTIONS = (
    _function(
        0x00074BE0, 98, ((0x00074BE0, 0x00074C42, "bc8763c1dd397b66d83d391525f2d765ecfc76c9117e095b92901763ce320537"),),
        "", "Shared 0x18-byte descriptor-record serializer with embedded executor pointer 0x85B9D; mixed GoMore (0x340A0) and Goodix (0x36C26) callers",
        ((0x0003413E, "BL"), (0x00034160, "BL"), (0x0009905A, "BL"), (0x0009907E, "BL"), (0x000990CE, "BL"), (0x000990EE, "BL"),),
        "unknown_shared_quantized_neural_runtime_candidate", "investigate_before_implementing",
    ),
    _function(
        0x00091E6C, 78, ((0x00091E6C, 0x00091EBA, "b87f45f4b27f518baeeb736ff0902540cf69f3a7c7e142572070ee0954dd8373"),),
        "", "Shared tensor-descriptor constructor (0x14-byte header, dims, element count) used by the pinned arena path 0x91D9C",
        ((0x00090F72, "BL"), (0x00091DA2, "BL"), (0x00091DCC, "BL"), (0x00091E3C, "BL"),),
        "unknown_shared_quantized_neural_runtime_candidate", "investigate_before_implementing",
    ),
    _function(
        0x00091DBE, 68, ((0x00091DBE, 0x00091E02, "5014b37fd01e3022d673fbe6c0e79b87f1bf4b6f1156625bd7d9ac0700191e8d"),),
        "", "Shared tensor create-and-fill via descriptor constructor plus pinned arena allocator 0x93628",
        ((0x00071664, "BL"),),
        "unknown_shared_quantized_neural_runtime_candidate", "investigate_before_implementing",
    ),
)

ALL_FUNCTIONS = (
    R1_FRONTIER_64_127_FUNCTIONS
    + NORDIC_FRONTIER_64_127_FUNCTIONS
    + TOOLCHAIN_FRONTIER_64_127_FUNCTIONS
    + GOMORE_FRONTIER_64_127_FUNCTIONS
    + GOODIX_FRONTIER_64_127_FUNCTIONS
    + YHM_FRONTIER_64_127_FUNCTIONS
    + DEVICE_REGISTRY_FRONTIER_64_127_FUNCTIONS
    + SENSOR_STREAM_FRONTIER_64_127_FUNCTIONS
    + QUANTIZED_RUNTIME_FRONTIER_64_127_FUNCTIONS
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
        "analysis": "64...127-byte ownership frontier",
        "image_sha256": EXPECTED_IMAGE_SHA256,
        "function_count": len(rows),
        "function_bytes": sum(int(row["size"]) for row in rows),
        "pinned_bytes": sum(int(row["pinned_bytes"]) for row in rows),
        "omitted_bytes": sum(int(row["omitted_bytes"]) for row in rows),
        "r1_function_count": len(R1_FRONTIER_64_127_FUNCTIONS),
        "nordic_function_count": len(NORDIC_FRONTIER_64_127_FUNCTIONS),
        "toolchain_function_count": len(TOOLCHAIN_FRONTIER_64_127_FUNCTIONS),
        "gomore_function_count": len(GOMORE_FRONTIER_64_127_FUNCTIONS),
        "goodix_function_count": len(GOODIX_FRONTIER_64_127_FUNCTIONS),
        "yhm_function_count": len(YHM_FRONTIER_64_127_FUNCTIONS),
        "device_registry_function_count": len(DEVICE_REGISTRY_FRONTIER_64_127_FUNCTIONS),
        "sensor_stream_function_count": len(SENSOR_STREAM_FRONTIER_64_127_FUNCTIONS),
        "quantized_runtime_function_count": len(QUANTIZED_RUNTIME_FRONTIER_64_127_FUNCTIONS),

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
