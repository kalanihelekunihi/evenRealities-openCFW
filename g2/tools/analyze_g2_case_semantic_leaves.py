#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Admit semantically closed charging-case leaves as isolated project C."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / "components/shared/case"
SOURCE = CASE / "runtime_case_semantic_leaves.c"
HEADER = CASE / "runtime_case_semantic_leaves.h"
BLOB = ROOT / "blobs/official/g2-2.2.6.10/firmware_box.bin"
FUNCTION_MAP = ROOT / "tools/manifests/g2-box-function-map.tsv"
CORPUS = ROOT / "research/corpus/case/ghidra/final-frontier/functions.jsonl"
PRIOR = ROOT / "tools/manifests/g2-case-register-transforms-admission-summary.json"
OUTPUT = ROOT / "tools/manifests/g2-case-semantic-leaves-admission.tsv"
SUMMARY = ROOT / "tools/manifests/g2-case-semantic-leaves-admission-summary.json"
APP_BASE = 0x08000000
WRAPPER_BYTES = 32
BLOB_SHA256 = "36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374"
CORPUS_SHA256 = "03474766c2bef410d520dbd71fe6a0b8565ef1b117168e1639cc8ab4700773ed"
PRIOR_CERTIFIED_FUNCTIONS = 29
PRIOR_CERTIFIED_INSTRUCTION_BYTES = 184

# These eleven wrappers have additional per-row decompilation pins beyond the
# authenticated whole-corpus identity below. They are a supplemental evidence
# subset, not the complete post-29-function / 184-byte admission delta.
SUPPLEMENTAL_DECOMPILATION_PINS = {
    0x08002B40: "3f455c93061bed570b2eba641e7c6587b29c188141c5a1749443a7f79e4b78da",
    0x08003656: "30c127ce78efc35da37d83d37af434a12763a2e89d22ea94dafb8f128835587c",
    0x08003A30: "1c2e6aec0934de67633867214418cf52d04dd623b94b456ed41b0fc5217eb1a4",
    0x08005024: "0936c43ca8bc10031ee3cd28c2a86f58da783c0ac8011e3d209eeb8b7349e10e",
    0x08005E18: "3fe1f585d4947860c772c48099db3a6fc4fe03a5adf7a316ba181a88d481655e",
    0x0800A124: "4008fb50ba7385ae11768ad686879b4282b09ddd218442fdd05ae245e0153fc3",
    0x0800A13A: "d9b83a4e8c64b4d4c07cca970fd67bfb094ec74dcef701e02e17f92f7e8aaaf2",
    0x0800C42C: "55be143a8cccf4e59e689dc727bd5b5dff84e8f260ffc266f730dc8e1c695337",
    0x0800C43C: "df4ce5d8e29b7cc463df44aab9d2c94be6b55da7d65cc7a1ab01886a653b0b4f",
    0x0800C478: "6311e1788b0cdf25a77db69425dcaf702daa0baad65debf4b7e972265f3847b7",
    0x0800C568: "14a9982adb739921b913d0a234011a01fd62d0f713d29e8455d3e30c96996e50",
}

SEQUENCE_DECOMPILATION_PINS = {
    0x0800A1AC: "e365cc38853ef8c3c1bc2f55ccdb2868da27d4ec97a69a518b52f40fc99cff4e",
    0x0800A1CA: "07acd8c8b7240d6b620126b9d496d5b9c5cc269e08744684dc38fffe859a6007",
    0x0800A1E8: "616a74c2138faa99f49f66f730d035f5216a40f14cbc9aaf5926cd2933054a9c",
    0x0800A206: "6f1384667d644c6012b09cafd0c27fa5894023b7b3effc432470f81cc2d1c91b",
    0x0800A224: "a2529ef3770a2f8303583e90bcd93236d4f2d27d3e0ffda8cdf7b29348064955",
    0x0800A24A: "cb745c5623db0649ffbc7b3ed21eed7203963adef4316dee7b005bab2ebd6544",
    0x0800A3D2: "310ef647ed8847e1ed14b0116bbbf8c704f3bc6f9546b0c4cd951da1048dba05",
    0x0800A414: "4cc87d18f3e0572e91b15fd7578a2c4d225bd0aca2c88e452df8a1cd94a4506b",
    0x0800A436: "1668c5d3704ceeed4415c892867b3ddf524e4653109a0444cbaea7f62d9698eb",
    0x0800A46C: "def15618aa34b152b5b3e4fcc00b8b30a9af7682b33b836bd61a26753988dc1e",
    0x0800A4B4: "8a31c8dcae7582c1ca11a3958844cd309f3cea28b92f480eb19fd6c5f67bcfd4",
    0x0800A4DC: "48bd1602704521066bf82157f5972ba08f7f5d53aca390c526fff6367fc50112",
    0x0800A270: "90e19a7030cb7f8083a9649ab18dc6965c37ebcb51f9ebd64384fe38ac2df6a5",
    0x0800A2E6: "e8f91cfffc2bfe5c8ec511113a9081d6e4ea4aa94a85442543fd56138aef7012",
    0x0800A310: "ced85f4f02b5df002cda0202016a59b57f7e2827ea87c61a242238e306963a54",
}

NOOPS = (
    0x080040F8, 0x080040FA, 0x080040FC, 0x080040FE,
    0x08004324, 0x08004326, 0x080046A0, 0x08004D00,
    0x08004D2C, 0x08005A50, 0x08005BD4, 0x08005BD6,
    0x08005BD8, 0x08005C26, 0x08005C8C, 0x08005E14,
    0x08005E16, 0x08005E2C, 0x08006776, 0x08006E18,
)
SYMBOLS = {
    **{address: f"open_cfw_case_hook_{address:08x}" for address in NOOPS},
    0x08002A5C: "open_cfw_case_read_byte3",
    0x08004EDC: "open_cfw_case_add_byte0_to_word8",
    0x08005F44: "open_cfw_case_or_words_88_8c",
    0x0800A408: "open_cfw_case_delay_10",
    0x0800A794: "open_cfw_case_busy_delay",
    0x0800A7A2: "open_cfw_case_busy_delay_alt",
    0x0800C3F8: "open_cfw_case_parity8",
    0x0800C412: "open_cfw_case_parity8_alt",
    0x0800D250: "open_cfw_case_copy_head8_to_tail8",
    0x08005024: "open_cfw_case_forward_action",
    0x08002B40: "open_cfw_case_command_a2_clear",
    0x08003656: "open_cfw_case_command_a2_set",
    0x08003A30: "open_cfw_case_run_pair",
    0x0800A124: "open_cfw_case_invoke_mode_one",
    0x0800A13A: "open_cfw_case_invoke_byte",
    0x0800C42C: "open_cfw_case_transform_word",
    0x0800C43C: "open_cfw_case_transform_word_alt",
    0x08005E18: "open_cfw_case_run_if_token",
    0x0800C478: "open_cfw_case_dispatch_resource",
    0x0800C568: "open_cfw_case_dispatch_resource4",
    0x0800A188: "open_cfw_case_route_boolean",
    0x0800A19A: "open_cfw_case_route_boolean_alt",
    0x0800A2A2: "open_cfw_case_emit_bits",
    0x0800A2C4: "open_cfw_case_emit_bits_alt",
    0x0800A148: "open_cfw_case_nested_delay",
    0x0800B064: "open_cfw_case_context_word38_is_zero",
    0x0800C4CC: "open_cfw_case_read_word_protected",
    0x080035B8: "open_cfw_case_run_guarded",
    0x0800BA44: "open_cfw_case_transition_word4",
    0x0800BA84: "open_cfw_case_transition_word4",
    0x0800BA64: "open_cfw_case_transition_word4_alt",
    0x0800BAA4: "open_cfw_case_transition_word4_alt",
    0x0800BB0C: "open_cfw_case_transition_word8",
    0x0800BB2C: "open_cfw_case_transition_word8_alt",
    0x0800BEBA: "open_cfw_case_write_profile_three",
    0x0800BF08: "open_cfw_case_write_profile_four",
    0x0800A528: "open_cfw_case_select_mask",
    0x0800A550: "open_cfw_case_write_selected_mask",
    0x0800A574: "open_cfw_case_write_selected_mask_alt",
    0x080006C4: "open_cfw_case_forward_resource",
    0x08006E08: "open_cfw_case_forward_resource",
    0x080084B0: "open_cfw_case_forward_resource",
    0x08008F98: "open_cfw_case_forward_resource",
    0x0800A130: "open_cfw_case_run_guarded_status",
    0x0800A39C: "open_cfw_case_read_mask4",
    0x0800A3AC: "open_cfw_case_read_mask8",
    0x0800BAC4: "open_cfw_case_write_mask4_set",
    0x0800BAE8: "open_cfw_case_write_mask4_clear",
    0x0800BAD8: "open_cfw_case_write_mask8_set",
    0x0800BAFC: "open_cfw_case_write_mask8_clear",
    0x08003BB0: "open_cfw_case_dispatch_tagged",
    0x0800A164: "open_cfw_case_route_parity",
    0x0800A176: "open_cfw_case_route_parity_alt",
    0x080086E0: "open_cfw_case_reset_timer_fields",
    0x080002D6: "open_cfw_case_expand_runs",
    0x08002F46: "open_cfw_case_classify_status",
    0x08005474: "open_cfw_case_shift_selected",
    0x08009EF8: "open_cfw_case_query_low_byte",
    0x0800AD24: "open_cfw_case_advance_cursor",
    0x0800A1AC: "open_cfw_case_pulse4_short",
    0x0800A1CA: "open_cfw_case_pulse8_short",
    0x0800A1E8: "open_cfw_case_pulse4_long",
    0x0800A206: "open_cfw_case_pulse8_long",
    0x0800A224: "open_cfw_case_pulse4_extended",
    0x0800A24A: "open_cfw_case_pulse8_extended",
    0x0800A3D2: "open_cfw_case_serial_preamble",
    0x0800A414: "open_cfw_case_serial_ack",
    0x0800A436: "open_cfw_case_serial_read_byte",
    0x0800A46C: "open_cfw_case_serial_write_byte",
    0x0800A4B4: "open_cfw_case_serial_start",
    0x0800A4DC: "open_cfw_case_serial_stop",
    0x0800A270: "open_cfw_case_pulse4_train_pre_delay",
    0x0800A2E6: "open_cfw_case_pulse4_train",
    0x0800A310: "open_cfw_case_pulse8_double_train",
    0x08002F28: "open_cfw_case_query_command_a2_is_one",
    0x08004FEC: "open_cfw_case_clear_irq",
    0x08004D04: "open_cfw_case_dispatch_pending",
    0x08005A52: "open_cfw_case_mark_controller_ready",
    0x08004958: "open_cfw_case_wait_elapsed",
    0x08005E2E: "open_cfw_case_guarded_controller_disable",
    0x0800AA00: "open_cfw_case_start_scheduler",
    0x0800A4FA: "open_cfw_case_serial_ack_sample",
    0x0800B5AC: "open_cfw_case_collect_bits",
    0x0800B5D6: "open_cfw_case_collect_bits",
    0x080099E8: "open_cfw_case_update_cached_byte",
    0x0800483C: "open_cfw_case_guarded_two_stage",
    0x080091AC: "open_cfw_case_configure_two_bit_field",
    0x0800A0EA: "open_cfw_case_retry_selector8",
    0x08005B8C: "open_cfw_case_wait_status_bit5",
    0x0800B4A4: "open_cfw_case_critical_read_word28",
    0x0800CDE4: "open_cfw_case_critical_read_flag40",
    0x0800C44C: "open_cfw_case_atomic_clear_word",
    0x08005EB6: "open_cfw_case_guarded_controller_field_high",
    0x08005E6E: "open_cfw_case_guarded_controller_field_mid",
    0x0800A046: "open_cfw_case_start_validated",
    0x080038A0: "open_cfw_case_toggle_lines_three",
    0x08002888: "open_cfw_case_configure_record_and_stop",
    0x0800C0E0: "open_cfw_case_normalize_context",
    0x08005F00: "open_cfw_case_reset_controller_context",
    0x08006D72: "open_cfw_case_wait_controller_ready",
    0x08006DB8: "open_cfw_case_prepare_controller_wait",
    0x08005048: "open_cfw_case_configure_mode_wait",
    0x080035F0: "open_cfw_case_configure_register_sequence",
    0x08005BDA: "open_cfw_case_initialize_peripheral_context",
    0x08005C28: "open_cfw_case_enable_peripheral_context",
    0x08003F6C: "open_cfw_case_wait_serial_idle",
    0x0800B4E0: "open_cfw_case_probe_low_signal",
    0x0800B53C: "open_cfw_case_probe_high_signal",
    0x08003E90: "open_cfw_case_fail_stop",
    0x08009190: "open_cfw_case_switch8_offset",
    0x08004EEC: "open_cfw_case_initialize_serial_block",
    0x080029A4: "open_cfw_case_serial_write_pair_200",
    0x08002A00: "open_cfw_case_serial_write_pair_70",
    0x080064EC: "open_cfw_case_start_context_transfer",
    0x080086F4: "open_cfw_case_reset_context_transfer",
    0x08009F80: "open_cfw_case_verify_selector_bank",
    0x0800A074: "open_cfw_case_read_stable_u16",
    0x08004A00: "open_cfw_case_build_register_descriptor",
    0x080062AC: "open_cfw_case_release_peripheral",
    0x08006BB0: "open_cfw_case_initialize_channel_profile",
    0x08006C00: "open_cfw_case_initialize_controller_profile",
    0x08006C80: "open_cfw_case_initialize_controller_profile",
    0x08006CF8: "open_cfw_case_initialize_controller_profile",
    0x080068F0: "open_cfw_case_initialize_transport_record",
    0x080006D4: "open_cfw_case_wait_controller_flag2",
    0x08000734: "open_cfw_case_start_controller_flag0",
    0x080046A4: "open_cfw_case_configure_irq_resource",
    0x08005B24: "open_cfw_case_configure_controller_irq",
    0x08008438: "open_cfw_case_initialize_application_profile",
    0x0800867C: "open_cfw_case_wait_controller_channels",
    0x080028B4: "open_cfw_case_serial_read_200",
    0x0800292C: "open_cfw_case_serial_read_70",
    0x08002EDC: "open_cfw_case_trimmed_average8",
    0x0800549C: "open_cfw_case_derive_clock",
    0x08005910: "open_cfw_case_start_controller",
    0x080084C0: "open_cfw_case_apply_controller_profile",
    0x08003F38: "open_cfw_case_copy64_protected",
    0x0800497C: "open_cfw_case_run_controller_range",
    0x08004B94: "open_cfw_case_copy_controller_words",
    0x08006240: "open_cfw_case_prepare_controller_context",
    0x08004FB0: "open_cfw_case_enable_interrupt_source",
    0x08004F14: "open_cfw_case_initialize_interrupt_path",
    0x08005A74: "open_cfw_case_activate_controller",
    0x08009E0C: "open_cfw_case_program_selector_bank",
    0x0800C4DE: "open_cfw_case_event_group_set_bits",
    0x08008758: "open_cfw_case_receive_u16",
    0x08008998: "open_cfw_case_receive_u8",
    0x080007A8: "open_cfw_case_start_peripheral",
    0x08004710: "open_cfw_case_wait_peripheral",
    0x08004C1C: "open_cfw_case_release_pins",
    0x08006308: "open_cfw_case_configure_resource_irq",
    0x080063EC: "open_cfw_case_read_controller_blocking",
    0x080066AC: "open_cfw_case_write_controller_blocking",
    0x080085B0: "open_cfw_case_apply_context_options",
    0x08008EC4: "open_cfw_case_wait_condition",
    0x08008D98: "open_cfw_case_begin_receive",
    0x08006A40: "open_cfw_case_configure_platform_routes",
    0x080052E4: "open_cfw_case_configure_clock_path",
    0x08003FD0: "open_cfw_case_calibrate_controller",
    0x08000270: "open_cfw_case_boot_initialize",
    0x080004C0: "open_cfw_case_wire_read_register",
    0x08000610: "open_cfw_case_wire_write_register",
    0x08000310: "open_cfw_case_wire_exchange_register",
    0x08006544: "open_cfw_case_process_frame_byte",
    0x0800B678: "open_cfw_case_emit_probe_train",
    0x08008808: "open_cfw_case_drain_receive_u16",
    0x08008A48: "open_cfw_case_drain_receive_u8",
    0x08004100: "open_cfw_case_configure_pin_policy",
    0x08005528: "open_cfw_case_configure_system_clock",
}

FUNCTIONS = {
    **{address: (
        2,
        "c7dfbb7d02759eacb64dbc916c1bb6f21eabaff1c1032ea5c9176abf7fd28df8",
        SYMBOLS[address],
        "behaviorally empty callback/reserved hook",
    ) for address in NOOPS},
    0x08002A5C: (
        6, "20b7429ad4a2738d10a7e021499fe6fbd4639a76beaaf5ed8b3606a713b8de36",
        SYMBOLS[0x08002A5C], "caller-owned record byte 3 read"),
    0x08004EDC: (
        12, "c8202e38b6bec0513269ceb7e7eb7852e3917486a78c89c8fea68d61c7c59c09",
        SYMBOLS[0x08004EDC], "record word 8 plus unsigned byte 0"),
    0x08005F44: (
        12, "061b4b9693ec66d6727125da2c02f3706cd18f8b96835484a7f34fa2e3d9803b",
        SYMBOLS[0x08005F44], "bitwise OR of context words at 0x88 and 0x8c"),
    0x0800A408: (
        12, "b661a011ab4aa7fb36e70bbb4ec3f02c8f6ad2dc84f9d9630b0822b9ccf348a7",
        SYMBOLS[0x0800A408], "ten-iteration busy loop"),
    0x0800A794: (
        14, "ba9af254a9ad99b2e1deb621bff84a9b5916a89a5dd9c7879f77d7284ea478fb",
        SYMBOLS[0x0800A794], "signed-count busy loop"),
    0x0800A7A2: (
        14, "ba9af254a9ad99b2e1deb621bff84a9b5916a89a5dd9c7879f77d7284ea478fb",
        SYMBOLS[0x0800A7A2], "signed-count busy-loop alias"),
    0x0800C3F8: (
        26, "3056e1af7e8eb01160dd4a701e52f4e012c92e62fe95f9669f76dce5637258e9",
        SYMBOLS[0x0800C3F8], "parity of the low eight bits"),
    0x0800C412: (
        26, "3056e1af7e8eb01160dd4a701e52f4e012c92e62fe95f9669f76dce5637258e9",
        SYMBOLS[0x0800C412], "low-eight-bit parity alias"),
    0x0800D250: (
        22, "b54ec861318bd467d1dfe3b4e6e16914aaf827c8705e33530e328f6756d9ffb0",
        SYMBOLS[0x0800D250], "copy bytes 0..7 to bytes 8..15"),
    0x08005024: (
        8, "6184af067579a437b117ef83ce6aa9ef83c11b2dc8568cb6de4d423b236db079",
        SYMBOLS[0x08005024], "forward a parameterless service action"),
    0x08002B40: (
        12, "69ef164f8c63b9c7793147e3673441b81c056c7f0ef08dd135e778d36e7c74dc",
        SYMBOLS[0x08002B40], "issue command 0xa2 with value zero"),
    0x08003656: (
        12, "6cde4422a92b5c3171d80caf68c2f0cbcbef1577a41ee3bd46d48d62275f074a",
        SYMBOLS[0x08003656], "issue command 0xa2 with value one"),
    0x08003A30: (
        12, "c575aaa734ee2b9d4e23e7b340fed3c61339547b8701ed7647e40e3f2b11590e",
        SYMBOLS[0x08003A30], "run two parameterless service actions in order"),
    0x0800A124: (
        12, "03f3e900f1697d04bdab04965e4af5c2f647ca5280830850c20d620c2cb8de8e",
        SYMBOLS[0x0800A124], "forward two values with fixed mode one"),
    0x0800A13A: (
        12, "5fca6606c54cc1b7dbaf735f023271ce7726920dafb915398d22748c4f9f08ae",
        SYMBOLS[0x0800A13A], "forward a selector and caller-owned byte"),
    0x0800C42C: (
        16, "0e59194910f794153846debc13b366fdce78e791a8cb3eae5217472eba3ead19",
        SYMBOLS[0x0800C42C], "transform a local word and publish the result"),
    0x0800C43C: (
        16, "d19946a5b66ccd600b29419e47236d3e89c8ebb6d4201a4650e95f8478e1ba4c",
        SYMBOLS[0x0800C43C], "alternate local-word transform wrapper"),
    0x08005E18: (
        16, "a979f66dd3d0f8094842e067fd139cb9e9a393badb763ce874cb57b6e5d31f90",
        SYMBOLS[0x08005E18], "run an action when a caller-owned token matches"),
    0x0800C478: (
        16, "b8ced8db9b9dbb3a4d495b57ba4393db7c1c1fdabd60d19e276875883f975d93",
        SYMBOLS[0x0800C478], "dispatch two values with a zero fourth argument"),
    0x0800C568: (
        16, "95683c30719f59412c67f611be6100bd11a71b699c5bbfbb91f49e8f04daf882",
        SYMBOLS[0x0800C568], "dispatch three values through a resource"),
    0x0800A188: (
        18, "c53e8ae884f8d2bfbc3322c7be826c64caeb4e9594df9492742442f5b9313d41",
        SYMBOLS[0x0800A188], "route a boolean to one of two actions"),
    0x0800A19A: (
        18, "c005f621a8e49f08f00b0ed83e852117e1687f997f02a0d42adc567cf68e82ea",
        SYMBOLS[0x0800A19A], "alternate boolean action router"),
    0x0800A2A2: (
        34, "637b227791b8df14c8c8ad6128163b7068e81fce8d62e7b216eabc9a36d5aa2d",
        SYMBOLS[0x0800A2A2], "emit seven or eight bits most-significant first"),
    0x0800A2C4: (
        34, "b082e39b937ce1787ca6890ee9342aec2ffd8ccd35163551967de6674f92ba5f",
        SYMBOLS[0x0800A2C4], "alternate MSB-first bit emitter"),
    0x0800A148: (
        24, "2dc05d0d2dc7caf019571f90eff1d33766fa77d1404b60cb0ba152449ac67b77",
        SYMBOLS[0x0800A148], "bounded nested busy loop"),
    0x0800B064: (
        28, "d7e73757e475238934b99fe20b474a38387f815c8005232171a17ad2d60ff7cf",
        SYMBOLS[0x0800B064], "test caller context word at offset 0x38"),
    0x0800C4CC: (
        18, "6b9a01edd096cfc827d6e66c3e8c5a37510a76c043f55aa6ccc6855ec2d2e620",
        SYMBOLS[0x0800C4CC], "read a word between caller-provided critical hooks"),
    0x080035B8: (
        24, "a997c6a1781cd6996c564fb08ad0ccc4414a319ae6625dcf7a6e8303e2534028",
        SYMBOLS[0x080035B8], "byte-one reentrancy guard around an action"),
    0x0800BA44: (
        24, "4aeba8dccfe9d9349f8ee1da2a642522573c6b898efc4ac3e79b920b27d372b0",
        SYMBOLS[0x0800BA44], "transition record word four to zero"),
    0x0800BA84: (
        24, "4acf4efe35c5619e244f37c486c8fc8a6c1e3f6e2f574cb851fcce1d0cb58023",
        SYMBOLS[0x0800BA84], "transition record word four to one"),
    0x0800BA64: (
        26, "2c113146a6c23cbbbb50b9e567a764d792bc8e4c86166249378d2a4264e2b153",
        SYMBOLS[0x0800BA64], "alternate word-four transition to zero"),
    0x0800BAA4: (
        26, "c4c830d88f9290b35d81151a25242b0bb0c79fe6410b70dbc59b39666f30bdd4",
        SYMBOLS[0x0800BAA4], "alternate word-four transition to one"),
    0x0800BB0C: (
        24, "56d7f411c0c978ec1021d44eab2e8d33cf5c8140f976fa6a60c16d7c9d6307f7",
        SYMBOLS[0x0800BB0C], "transition record word eight to one"),
    0x0800BB2C: (
        26, "dc2a5134b66e0d1ece68122a918b53ba25aa1cb95b0e610d9d0023a62997a163",
        SYMBOLS[0x0800BB2C], "alternate word-eight transition to one"),
    0x0800BEBA: (
        36, "ca9ef24cf7d1632fb69edf8caad261c83242378112a0eba25243af63cc32913b",
        SYMBOLS[0x0800BEBA], "write four indexed profile-three values"),
    0x0800BF08: (
        36, "ac8a3e2b8832c14160ac30e8596c4d59845d26abf6e4671af0e0ac010ba3f767",
        SYMBOLS[0x0800BF08], "write four indexed profile-four values"),
    0x0800A528: (
        30, "5c7d1a849c4eac162c4ca963adbb5e1b32bb81085beac309acc84c12c45ff0bc",
        SYMBOLS[0x0800A528], "select an eight- or sixteen-bit read mask"),
    0x0800A550: (
        28, "3610d639ce93caa6d84e1312a27de9a21266ea994d0ea6a1a513e6dc657a10d3",
        SYMBOLS[0x0800A550], "select and write the first mask polarity"),
    0x0800A574: (
        28, "678003548a8695de93e16f300c9f81cb027bc7e7404560db6df91efaa7105eac",
        SYMBOLS[0x0800A574], "select and write the inverse mask polarity"),
    0x080006C4: (
        10, "9e4bbf68eeea3e149e8cb97bda79dad3dbe5c7aa9d363be5bb536ad28074e4c1",
        SYMBOLS[0x080006C4], "forward the first fixed resource"),
    0x08006E08: (
        10, "fe2c3f42b428c1f36173c9315a7dcc126e523dc6bd2dd7b7d546bf465556673a",
        SYMBOLS[0x08006E08], "forward the second fixed resource"),
    0x080084B0: (
        10, "3c33d0083b2acc5371f48ca126cb8af845d02a82a0a3a1e81dc1ee1a7572044b",
        SYMBOLS[0x080084B0], "forward the third fixed resource"),
    0x08008F98: (
        10, "992ca4a166cc0d65ebb8c46c0bed755b3d585eb86c439402074462c7750e864c",
        SYMBOLS[0x08008F98], "forward the fourth fixed resource"),
    0x0800A130: (
        10, "687c4b62265fb24f22f85e358dd9891d73dc7cfca499ed98361090a192906a51",
        SYMBOLS[0x0800A130], "run the guarded service and return success"),
    0x0800A39C: (
        12, "36017903ed11cbdf9e013cbbb7f6d4efd7b687b10a7ea20efeb1a5eb9a4496b9",
        SYMBOLS[0x0800A39C], "read a fixed four-bit resource mask"),
    0x0800A3AC: (
        14, "fb47840018af492317e86c3fe0c72603df09d8dee8a9270d2efaa982c98aee8f",
        SYMBOLS[0x0800A3AC], "read a fixed eight-bit resource mask"),
    0x0800BAC4: (
        14, "8681cad6e7bfda76adb74a124014f132aa9594c887d6c0581ad17e880fecf684",
        SYMBOLS[0x0800BAC4], "set a fixed four-bit resource mask"),
    0x0800BAE8: (
        14, "5c7a7f7a1e210a3c8f10491628db1267e9e7129bc9be068957a6216a77ea3d80",
        SYMBOLS[0x0800BAE8], "clear a fixed four-bit resource mask"),
    0x0800BAD8: (
        16, "2bca89bc9fee4a2a3a879a89f5fe55b614e202270ad7be218023982133ba92e9",
        SYMBOLS[0x0800BAD8], "set a fixed eight-bit resource mask"),
    0x0800BAFC: (
        16, "6c4fa639faa322a143ce112f66db96715157b34061fa4b9d10d1ec91f1164ef3",
        SYMBOLS[0x0800BAFC], "clear a fixed eight-bit resource mask"),
    0x08003BB0: (
        16, "a2b3aa4c2ed523cf77ad992e67e9c60c3b6f8fdaa3e39ae41f6dad1e35f66238",
        SYMBOLS[0x08003BB0], "dispatch two values with a caller-supplied tag"),
    0x0800A164: (
        18, "d7443ede69ac6e42703e43047d6e8c013672549c81e978c9fdc6d54b4efcadcc",
        SYMBOLS[0x0800A164], "route low-byte parity through the first action pair"),
    0x0800A176: (
        18, "3fe00ddfffb93244b5c210cc7045d9adf53ab0e2626cbf4e7e17e5f69c3d4f15",
        SYMBOLS[0x0800A176], "route low-byte parity through the alternate action pair"),
    0x080086E0: (
        20, "7e1e2868861ef3df1a464e291757e1daa185e3ec2841b1207a0f2e381e2aa7c4",
        SYMBOLS[0x080086E0], "clear two timer halfwords then run a service action"),
    0x080002D6: (
        58, "69fe36d77bb8c738e666160d85769990680fe1f0522b7fda0e3f31bd81b02dca",
        SYMBOLS[0x080002D6], "expand alternating literal and zero runs"),
    0x08002F46: (
        26, "ccedbae4febe01e86cb64facb00636aa6c3c7d0b702c8811d640d826e13b67d7",
        SYMBOLS[0x08002F46], "classify status word bit twenty"),
    0x08005474: (
        26, "97cfc337346c93b13c6c261a3fb670099160dd5fcfd4ee1cc08562c6abb542e5",
        SYMBOLS[0x08005474], "select a table shift from control bits 12 through 14"),
    0x08009EF8: (
        32, "05da8cb680939c1332145ec0343c8d099270b4d2eba9b0d7c5b3880cc9fa53d8",
        SYMBOLS[0x08009EF8], "query a word and publish its low byte"),
    0x0800AD24: (
        36, "a5b486c47e5885ee9bd8d3d367325d125a6d93491df8ebd9bca1f099b68dd793",
        SYMBOLS[0x0800AD24], "advance and wrap a record cursor"),
    0x0800A1AC: (
        30, "60e1f8d022f750213cfc687f02be95348bc89da5552f7117efa2c975509bde2e",
        SYMBOLS[0x0800A1AC], "four-bit short pulse sequence"),
    0x0800A1CA: (
        30, "3476ce7b76727e4f86cfaea655bffd594e5b9768584953e8ced7d7597b1cec22",
        SYMBOLS[0x0800A1CA], "eight-bit short pulse sequence"),
    0x0800A1E8: (
        30, "48cafbdbfc041b0c58c3ac0f6e1ced400ae932765e4db219b2f15b675a300e3d",
        SYMBOLS[0x0800A1E8], "four-bit long pulse sequence"),
    0x0800A206: (
        30, "d77e147fdfca98d8255c2024aaa8e41cb87641786945bb5f8b10202d658474a5",
        SYMBOLS[0x0800A206], "eight-bit long pulse sequence"),
    0x0800A224: (
        38, "0a060acc777d3a4545473df0bde2742f76450c783d4037cd3894a0fcee8cffe2",
        SYMBOLS[0x0800A224], "four-bit extended pulse sequence"),
    0x0800A24A: (
        38, "7635a6838e1594418b00fbb978b103ceea76d6be49f77421de590633dffc891a",
        SYMBOLS[0x0800A24A], "eight-bit extended pulse sequence"),
    0x0800A3D2: (
        54, "cadee86db7d51e84b5df707d3348a1567c6c0b50cb2a42323d0f897a7af4f73e",
        SYMBOLS[0x0800A3D2], "serial-line five-transition preamble"),
    0x0800A414: (
        34, "16ba911ebea558840137d2c0bdbc4a4b432e33f2810f4bc285d4ab414c34d2e3",
        SYMBOLS[0x0800A414], "serial-line acknowledge transition"),
    0x0800A436: (
        54, "ca35f4869c1f1ead9279b61f3b770b8e2e5151eda674d5fd1933d514f2472239",
        SYMBOLS[0x0800A436], "sample one serial byte most-significant bit first"),
    0x0800A46C: (
        72, "34324d00a6d3f7a157796da105beb91fa0c868a25028a85c6eb81dc20a04a04f",
        SYMBOLS[0x0800A46C], "write one serial byte most-significant bit first"),
    0x0800A4B4: (
        40, "80524d030e4267a5eb85f500e6b151daba880c40b6ea618d043200c8cdadf2a3",
        SYMBOLS[0x0800A4B4], "serial-line start transition"),
    0x0800A4DC: (
        30, "ce6a10b2b68b08bf24e4b76e911d2a2041b587e85344d14ec7f4f4bfada87e5b",
        SYMBOLS[0x0800A4DC], "serial-line stop transition"),
    0x0800A270: (
        50, "87fa908d5ee529476006bdff2a44e7cf598e15f1eb048c2220c157a0eb4a234b",
        SYMBOLS[0x0800A270], "four-bit forty-delay pulse train with pre-delay"),
    0x0800A2E6: (
        42, "c6407b8af15ea0c2789d41ebe726ef6db688bc687da18bf520b63c55f69782e7",
        SYMBOLS[0x0800A2E6], "four-bit forty-delay pulse train"),
    0x0800A310: (
        70, "7d97c1c9a6dd34c94b330f25fc9b9b024ba061f9930e5cb8dbdb1bf3699a05a8",
        SYMBOLS[0x0800A310], "eight-bit paired ten-delay pulse trains"),
    0x08002F28: (
        30, "f30dbebb29b37d7916b5a609e6dfb80c0d182d970e54ee4dbdd36a082a9bd09b",
        SYMBOLS[0x08002F28], "query command 0xa2 and classify low byte one"),
    0x08004FEC: (
        26, "b2165405c4004a1a03af568aee6d740bee9510a301d1cd6c1c84d2175a7bef09",
        SYMBOLS[0x08004FEC], "clear indexed interrupt then issue both barriers"),
    0x08004D04: (
        36, "8daf57e9c9c177b56cb7dbab499dc0a739e12667e6fcf727716151e3fc764aad",
        SYMBOLS[0x08004D04], "acknowledge and dispatch two pending status banks"),
    0x08005A52: (
        34, "ead7b2b743ace0bbafc23d0e1df458940a3c9cad538af50359a65291eb974f51",
        SYMBOLS[0x08005A52], "mark controller context ready and notify bit-two state"),
    0x08004958: (
        32, "09bba7cab4e1920b6b9265f7cb57a9e716a53cc447e39b4ed558daea9620080e",
        SYMBOLS[0x08004958], "wait for unsigned tick delta with compensation"),
    0x08005E2E: (
        60, "05bf8c57b8cc3df322074d7c44bad89a7531092a16b12725573975f8e6a8f055",
        SYMBOLS[0x08005E2E], "guarded controller disable register sequence"),
    0x0800AA00: (
        36, "8b50fde64434922f62d18ca38978810ef4ce389a3d2bdffdcfd5a5a35115c723",
        SYMBOLS[0x0800AA00], "scheduler-start exception-context policy"),
    0x0800A4FA: (
        46, "98bf33c3c69d06a940d280a8ecd08c16f167a934e684da066fd658e2fe646984",
        SYMBOLS[0x0800A4FA], "serial-line acknowledge sample transition"),
    0x0800B5AC: (
        42, "4b3445ddcf078ecd0bbbb77e01f61c50e7b5fd56b84ffa44e8606ea73b768964",
        SYMBOLS[0x0800B5AC], "collect eight bits through the first reader"),
    0x0800B5D6: (
        42, "399da3559abc30265a89d5c340d3074215594767d8bc8bfba84b4cc135c367eb",
        SYMBOLS[0x0800B5D6], "collect eight bits through the alternate reader"),
    0x080099E8: (
        38, "066807352bd46b8efaabe9c847be6b09876aab8760ec30057bb5f381dfdd1a72",
        SYMBOLS[0x080099E8], "publish changed byte and update cache on success"),
    0x0800483C: (
        62, "aa5a5e8fc99d7f398bc93aedc8621955eaf48781ca2ae1fa674bdcaa3f5baca7",
        SYMBOLS[0x0800483C], "guarded two-stage context initialization"),
    0x080091AC: (
        60, "0ca16b2b29f5899aaf40a3e3435506b552d1cb526a15a1aaa029f4fbac3bab7d",
        SYMBOLS[0x080091AC], "configure indexed two-bit register field"),
    0x0800A0EA: (
        58, "304bfa9bba9551e1f8ebf939ff002d6b02d17714689e5dcfca47c97a6f69ca31",
        SYMBOLS[0x0800A0EA], "two selector-eight attempts with interposed delays"),
    0x08005B8C: (
        52, "d41432bfb95c3668c45dca72e4cacaddf09df05764246beac6a90d7fffb4178a",
        SYMBOLS[0x08005B8C], "clear status bits and wait for bit five"),
    0x0800B4A4: (
        26, "64980fd0019ddf7093477895e5efc620668c87cb64e93e0dea5b2bfd16b4ddcf",
        SYMBOLS[0x0800B4A4], "critical read of record word at offset 28"),
    0x0800CDE4: (
        38, "61bf76266be446eb56986da77e7a82f37f09f370a51d642f1cf6138ceca87f75",
        SYMBOLS[0x0800CDE4], "critical read of record flag at offset 40"),
    0x0800C44C: (
        42, "b079660180eb41a08b427510994eb367f582115937e82bc51c8e11f7191df7b7",
        SYMBOLS[0x0800C44C], "atomic low-24-bit mask clear returning prior word"),
    0x08005EB6: (
        70, "2f7a22523ec9ba1395bf0069a78c7f18fa99c091653edcb8bdbb73731f5837aa",
        SYMBOLS[0x08005EB6], "guarded high controller-field update"),
    0x08005E6E: (
        72, "ad5fcc66aac9df062d2b188ed15997276925b149715559938cc7578897d72026",
        SYMBOLS[0x08005E6E], "guarded middle controller-field update"),
    0x0800A046: (
        46, "fac523e14260d0494f5b5d6474a9ad5690e895fc2706440dd55b39bd5773d6ef",
        SYMBOLS[0x0800A046], "query marker 0xa0 then start and finalize"),
    0x080038A0: (
        62, "f23c4ff1e1dec4bb9828ff74c9c76289d08d38a09dad21a21fd33c7a0b465ed7",
        SYMBOLS[0x080038A0], "toggle two lines for three timed cycles"),
    0x08002888: (
        40, "60f7d3e9f357aa2bee966a24fa81b06502bfd2e28f14c7929084c1f074fc0c87",
        SYMBOLS[0x08002888], "configure the fixed five-word record then stop"),
    0x0800C0E0: (
        70, "cc1be3045b57e8d20b04955c8cd4a832d9848171b21d7fa369a71e3f08056cbc",
        SYMBOLS[0x0800C0E0], "normalize sentinel bytes and dispatch idle context"),
    0x08005F00: (
        66, "b0b1c1a2901d9b191cbce40958e141623a95b5b7fb037dde1254d7a8b615dda5",
        SYMBOLS[0x08005F00], "reset caller-owned controller context and release resources"),
    0x08006D72: (
        68, "16a6a5c45a1b68f186e9a8505659651f812b9a2cf1cd477e5edeb63441394d10",
        SYMBOLS[0x08006D72], "request controller ready and enforce a bounded tick timeout"),
    0x08006DB8: (
        74, "e1c5df16785d6731aa16c845705883d8379f1b900475d56b06c195fc4fef79ce",
        SYMBOLS[0x08006DB8], "temporarily suppress controller mode around a readiness wait"),
    0x08005048: (
        62, "6b55dd98ee196750c72b3a45c33dc4f0452e87a2d5a1fb18ff2262c5dda7efe1",
        SYMBOLS[0x08005048], "configure controller mode and enforce a computed wait budget"),
    0x080035F0: (
        102, "8904ce09c98b52543b32fd5eac102fcaccc560d1dfff456e25778aa435a0969c",
        SYMBOLS[0x080035F0], "write seven fixed register/value pairs with interposed delays"),
    0x08005BDA: (
        76, "9b1a4d0742e8a544fec67339c269e54db6e478efa672a3b66de0d1311afc02a2",
        SYMBOLS[0x08005BDA], "initialize and configure a caller-owned peripheral context"),
    0x08005C28: (
        80, "7197db954be995225d23781b86f44a8b8c639c1c1d9aa748b40abdcb4a2641a4",
        SYMBOLS[0x08005C28], "enable an initialized peripheral context with special-mode policy"),
    0x08003F6C: (
        82, "2cf1b7aa43c06cbf60de48cdfa02f471e7ec24ab40142b4e4242b3385f288fe9",
        SYMBOLS[0x08003F6C], "bounded serial-idle and completion wait with pending-error capture"),
    0x0800B4E0: (
        84, "bffe716eab12db89dd269918951268f4ae6a647df08704620bedb246bcf5e43c",
        SYMBOLS[0x0800B4E0], "sequence low-signal probe actions and bounded readiness sampling"),
    0x0800B53C: (
        104, "978232e95a79e56479f7ddaed79601a5dedfac71148a3c8bd430a86ec4de7f25",
        SYMBOLS[0x0800B53C], "sequence high-signal probe phases and return packed status"),
    0x08003E90: (
        4, "ba2d718b92d01eb1f8e40143481f113f9b1c1dcb94b78e076cbb2fd1f4096b82",
        SYMBOLS[0x08003E90], "disable interrupts and remain in the fail-stop idle loop"),
    0x08009190: (
        26, "52e0ea5004bcc3e4c72008eeb0c33f671d27bfcc5f848adb228107fb90119165",
        SYMBOLS[0x08009190], "resolve a bounded eight-bit compiler switch-table offset"),
    0x08004EEC: (
        36, "a44c624f5af6410f05b71d3f5eefb750e4a82dfe24e88485e2760f61072cb495",
        SYMBOLS[0x08004EEC], "enable and initialize a caller-owned serial block"),
    0x080029A4: (
        88, "30c299289eb7e16356a271e7c1c10e0b10dc6b91c660f57da10f32cd3dc98d56",
        SYMBOLS[0x080029A4], "write a two-byte payload after bounded address-200 acknowledgement"),
    0x08002A00: (
        88, "5a0ee6537e10cc82fc9919562d0c553081b6b974e2f8e2d1897b936cb6fd9e0c",
        SYMBOLS[0x08002A00], "write a two-byte payload after bounded address-0x70 acknowledgement"),
    0x080064EC: (
        88, "2302ddc0cc79d3abb0ef4f3aa42ecc79ac7750d36f5f747c4c006b62b56d90fa",
        SYMBOLS[0x080064EC], "validate context policy and start a protected transfer"),
    0x080086F4: (
        96, "ccad1afa4b7303b7ec82da169aa513a68c5650d44940fd12aba21acbc49dd6f5",
        SYMBOLS[0x080086F4], "clear protected controller fields and reset transfer state"),
    0x08009F80: (
        106, "b3fc1e4f07a94342a1257e65f585a12f5a1ba60becb33bc9cefb83c5a93138e9",
        SYMBOLS[0x08009F80], "validate mode selectors and compare an eighty-byte register bank"),
    0x0800A074: (
        118, "020d5c2e5f4f099830ca57aacac192ecdd062585dc2c386216d23578899640d3",
        SYMBOLS[0x0800A074], "read and byte-swap a stable two-byte resource value"),
    0x08004A00: (
        98, "dc8d2646d08e1aec4d91494069f1ddfbb9c48abece46b33021a4610357efa91b",
        SYMBOLS[0x08004A00], "build a seven-word descriptor from a selected register bank"),
    0x080062AC: (
        74, "f97e0e0117ec959de31742c525102cd70fb08c5d684845fab6cf8b31b96d5f55",
        SYMBOLS[0x080062AC], "release one of two caller-owned peripheral resources"),
    0x08006BB0: (
        72, "8e8f3848aa8ac1e9e2acd42dfc30417d7ddd1b774f55abf64f8d5372e7454546",
        SYMBOLS[0x08006BB0], "initialize and attach a fixed channel profile"),
    0x08006C00: (
        110, "8f0be46606da09dd8195d3354588b6917ab3eb848fc2067679909366229febe3",
        SYMBOLS[0x08006C00], "initialize mode-twelve controller context and start transfer"),
    0x08006C80: (
        106, "4fbcc4a55d407c0a94f80664c930880bfe58188fdeee808b112dc022812d9e0c",
        SYMBOLS[0x08006C80], "reset and initialize mode-four controller context"),
    0x08006CF8: (
        106, "521c710d64383c8df11511cac991c816b8d55334b36d290d421f9592e1206447",
        SYMBOLS[0x08006CF8], "reset and initialize mode-eight controller context"),
    0x080068F0: (
        108, "5b0936ba3ab04ff69515498ef3da358167ad5f4e2b0b577ff04532562d498945",
        SYMBOLS[0x080068F0], "initialize, attach, and finalize a transport record"),
    0x080006D4: (
        92, "0cece80f6b94f0348d7eeb80f5d3ad07ad1ccdbb52e53beed45718864b22b8bb",
        SYMBOLS[0x080006D4], "start and bound a controller flag-two wait"),
    0x08000734: (
        110, "486650b539c8d304e71cb705c085c38cfe87d527bee0edebde56785b9d26c762",
        SYMBOLS[0x08000734], "start and bound a controller flag-zero transition"),
    0x080046A4: (
        100, "f344eb2f21489c0d41cd9d455e7e25442112d10e3ea2b0831a64eb9770a5a508",
        SYMBOLS[0x080046A4], "configure a matched IRQ resource and clear its interrupt"),
    0x08005B24: (
        96, "54d76304a964ef80ce3323ff8c8ef0ec069652484d394e7adb078a0c3f40710c",
        SYMBOLS[0x08005B24], "initialize a matched controller IRQ profile"),
    0x08008438: (
        118, "fc2b7141fd09c6ec456cbb5eb52c11f88ca1b5c4733a80ecd3553a004a0d4335",
        SYMBOLS[0x08008438], "initialize and attach the fixed application profile"),
    0x0800867C: (
        96, "016eb53cd702ec5413e44d7d918394ac1a18c6a07171da21079daaf9e9da0dbb",
        SYMBOLS[0x0800867C], "wait for two active controller channels and reset context state"),
    0x080028B4: (
        114, "046ffd35165879c93662ccda04f0186970ba928fb87a2d7e635f9b04ffa47f26",
        SYMBOLS[0x080028B4], "read a selected address-200 serial register into a caller buffer"),
    0x0800292C: (
        114, "d83acd2a7f2e817ff14dd8b3c575054abbcb6e8d13aada6b485e05e0a2095815",
        SYMBOLS[0x0800292C], "read a selected address-0x70 serial register into a caller buffer"),
    0x08002EDC: (
        72, "19a5dfc24bb9c52a8381e8b4e9f19b3141a89def9da0f19b760e171b4e42992e",
        SYMBOLS[0x08002EDC], "average eight resource samples after discarding extrema"),
    0x0800549C: (
        130, "e44c45ecf3a52ed25713b3de93ad9cc470747cf5130828dcff66f92cfd1ce362",
        SYMBOLS[0x0800549C], "derive the active peripheral clock from four configuration words"),
    0x08005910: (
        122, "e45cbd74d3967a1df34927187eb94301f87fe63035795bb4fab27eb3b39fa6a9",
        SYMBOLS[0x08005910], "start a guarded controller and enforce its bounded ready wait"),
    0x080084C0: (
        122, "4cad39867e6e87cb292cf08e64d8a8d89ba5a5407fada8f19f2c1b7963d44c85",
        SYMBOLS[0x080084C0], "apply a six-word profile under controller-class field policy"),
    0x08003F38: (
        48, "3dd0b462c36cdad28ff4a39854f34a4181bad1f889aeb590e970b9b973458b5c",
        SYMBOLS[0x08003F38], "copy sixty-four words under protected interrupt state"),
    0x0800497C: (
        124, "5679f3ad487d5f58590cc6c19da1f6f1fa944847068c2e52745f9d13df7f6fe9",
        SYMBOLS[0x0800497C], "run a guarded single or ranged controller operation"),
    0x08004B94: (
        88, "ad977acf353e77f4e479ef6a71fe9fa9dec0c2b88b327c0565dea83a6095c14b",
        SYMBOLS[0x08004B94], "perform a guarded controller copy and clear its active mask"),
    0x08006240: (
        108, "7c904758b9e682be24b4ac3411a8fbf788204e8d03448c8cb590c4107df3962c",
        SYMBOLS[0x08006240], "prepare a controller context and wait for active channels"),
    0x08004FB0: (
        56, "f65f32b467c14ba4213ba37eaac1f2dbc783e73bd9bfab5ac2fd2bd9bcd5b41c",
        SYMBOLS[0x08004FB0], "enable, route, dispatch, and configure an interrupt source"),
    0x08004F14: (
        132, "bca22a8ea417589bad100c47034c672dedc6e750e3f179fd33e61c458eaf73b7",
        SYMBOLS[0x08004F14], "initialize and route a bounded interrupt timing profile"),
    0x08005A74: (
        172, "4cfc8970333b11f9ed8f58cb3bed4c73adc47b4d234d584e117484eb950c32fd",
        SYMBOLS[0x08005A74], "activate and configure a caller-owned controller context"),
    0x08009E0C: (
        170, "52fef6adeb1a43109ba1e139f3a5bbe2261daf05a630ca0eb85e25d53c0dd9fd",
        SYMBOLS[0x08009E0C], "program and poll an eighty-byte selector register bank"),
    0x0800C4DE: (
        138, "adec65cab22eae10b3f9c2d4f3bc58b2986b72c9137915d8e5e8d79fe969c496",
        SYMBOLS[0x0800C4DE], "set event-group bits and unblock matching waiters"),
    0x08008758: (
        174, "1d7db51983a0d5936fc8f6ed8164b6eef38a651bd04191453bfa9154c1c71504",
        SYMBOLS[0x08008758], "receive a masked sixteen-bit controller value"),
    0x08008998: (
        174, "cc083c2a860af273de4da501b4c33845c4455cfdd3a01a212a79a9be905068ea",
        SYMBOLS[0x08008998], "receive a masked eight-bit controller value"),
    0x080007A8: (
        162, "e80a57f4551a88af7841b023e2bb5f9ffee5c36ee4fefc860327bb999849dc31",
        SYMBOLS[0x080007A8], "start a peripheral and enforce its bounded ready transition"),
    0x08004710: (
        196, "3a5caa28158344c155da673f7d809fc8f8d440cbdaeb779e833adb509548aea1",
        SYMBOLS[0x08004710], "wait for a peripheral completion or record timeout state"),
    0x08004C1C: (
        206, "c62357aa9de403c382874f6f9d7fe95e510c0a3d96a8f4e6275a3baa8dcf1cc5",
        SYMBOLS[0x08004C1C], "release selected pin ownership and controller fields"),
    0x08006308: (
        212, "691d2eac1d6c524b0901e45290bb83ac5245b069926b6d1da3c399a35a806cbf",
        SYMBOLS[0x08006308], "initialize and route one of two controller resources"),
    0x080063EC: (
        252, "c32c4b071020034a62984a0c08a0ba774b7c444da16e5f8d062df02ab93c5d85",
        SYMBOLS[0x080063EC], "read a controller buffer under bounded wait policy"),
    0x080066AC: (
        202, "699a3dd41d29724d9da4692d36641a196020431358c6ac71bc0044d586bbe325",
        SYMBOLS[0x080066AC], "write a controller buffer under bounded wait policy"),
    0x080085B0: (
        202, "39e2203a10a00c8a3d99a7554752f9d1ba0217e58dbdb864e54b2319baecb984",
        SYMBOLS[0x080085B0], "apply enabled context option fields to controller registers"),
    0x08008EC4: (
        210, "38ac4eba5fad385117e78c5b44741aa71cd197e0fe45cf7e08666fe9088473bd",
        SYMBOLS[0x08008EC4], "wait on a controller condition and reset timed-out state"),
    0x08008D98: (
        280, "2e5ed912a84b7f41ce1c00525eccdbc79df3dedcdc5016305718873cc027331b",
        SYMBOLS[0x08008D98], "initialize direct or DMA-backed receive state"),
    0x08006A40: (
        298, "7aef064e38dc6e49b1725c221ae4244fc9b68d9c7ff7fbeac540fe1c2048fea6",
        SYMBOLS[0x08006A40], "configure the fixed platform route and interrupt sequence"),
    0x080052E4: (
        318, "ee30a871f376066fafc98b8f843c3963c9d975eff9e095998ec2d8cf809e5241",
        SYMBOLS[0x080052E4], "apply clock-path selection and derive the routed clock"),
    0x08003FD0: (
        282, "eb41a0c3c12cc61be81a39bfbec52ab51a75ec9f73e016bae6f10941f808dd61",
        SYMBOLS[0x08003FD0], "calibrate a controller from eight bounded samples"),
    0x08000270: (
        36, "9955b05104c79c9ded13dc2a3dc50e421d6f490ef736c15c954a874b8edfcc7b",
        SYMBOLS[0x08000270], "run initialization entries and expand packed startup data"),
    0x080004C0: (
        168, "afac8417e62c80722cf3f2b317b579f402c05e6e5ccc47110ae6ea08eda53484",
        SYMBOLS[0x080004C0], "read a checked framed wire-register transaction"),
    0x08000610: (
        174, "4edcb69facf78728167aafc9f3b6061061110a1c0c935f81d7c11b303eae1bc7",
        SYMBOLS[0x08000610], "write a checked framed wire-register transaction"),
    0x08000310: (
        268, "f32433fb67dcb5d830d633b3ba6795b91119d07458bae815270ea909cd596d8b",
        SYMBOLS[0x08000310], "exchange a checked framed wire-register transaction"),
    0x08006544: (
        338, "2a44a16ffc3fd241572e71b43c2e8e0e3c3911783bb660be7ae9596adafb7b98",
        SYMBOLS[0x08006544], "accumulate, validate, extend, and dispatch framed bytes"),
    0x0800B678: (
        362, "41979fa02fe29264f07a3efc30f1c37b8ecb231e9ca16e3bc29d508a92ea9501",
        SYMBOLS[0x0800B678], "emit the fixed three-phase probe pulse train"),
    0x08008808: (
        390, "ffb1cb338f7e77484eec8253c99e4a0a5f6a455aeaefd634b491eac1f9098338",
        SYMBOLS[0x08008808], "drain sixteen-bit receive FIFO state and service errors"),
    0x08008A48: (
        390, "20e584a13dd22d71a4a5a9c39b565c58c9b03381ce15208c665be02c164c9517",
        SYMBOLS[0x08008A48], "drain eight-bit receive FIFO state and service errors"),
    0x08004100: (
        522, "0682938a12722df01c45a136a35021b6fb5f82dbba3e3b72bdddf103fbb9feeb",
        SYMBOLS[0x08004100], "configure guarded pin and clock-routing policy"),
    0x08005528: (
        962, "050691a5e1ddeb35e98eecd2c46e744259131c8936ce45dca88495da0e0bc4dd",
        SYMBOLS[0x08005528], "configure and validate the complete system clock policy"),
}

SOURCE_PINS = {
    SOURCE: (111011, "01bddc77e1d356e8538b80bc0e188138b8e291dfa3cd364c9d74dfaf6d0b4403"),
    HEADER: (37793, "544a0f148154f5e17a0f22b633c9b497b2ccc1045118c54a68f785851b193bc1"),
}

FORBIDDEN_SOURCE_TOKENS = (
    "__asm", "asm(", ".byte", ".hword", "expected_hex",
)
RAW_ARRAY_RE = re.compile(
    r"\b(?:u?int(?:8|16|32)_t|unsigned\s+char|char)\s+\w+\s*"
    r"\[[^]]+\]\s*=\s*\{")


class AuditError(RuntimeError):
    pass


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def function_rows() -> dict[int, dict[str, str]]:
    with FUNCTION_MAP.open(newline="", encoding="utf-8") as handle:
        rows = csv.DictReader(
            (line for line in handle if not line.startswith("#")), delimiter="\t")
        return {int(row["entry"], 0): row for row in rows}


def evidence_rows() -> dict[int, dict[str, object]]:
    rows = {}
    for line in CORPUS.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            rows[int(row["address"])] = row
    return rows


def _llvm_nm() -> str | None:
    found = shutil.which("llvm-nm")
    homebrew = Path("/opt/homebrew/opt/llvm/bin/llvm-nm")
    if found is None and homebrew.is_file():
        found = str(homebrew)
    return found


def target_compile() -> tuple[int, str, set[str]]:
    clang = shutil.which("clang")
    nm = _llvm_nm()
    if clang is None or nm is None:
        raise AuditError("clang/llvm-nm unavailable")
    with tempfile.TemporaryDirectory(prefix="g2-case-semantic-leaves-") as tmp:
        output = Path(tmp) / "semantic-leaves.o"
        proc = subprocess.run([
            clang, "--target=arm-none-eabi", "-mcpu=cortex-m0plus",
            "-mthumb", "-std=c11", "-Oz", "-ffreestanding", "-fno-builtin",
            "-ffunction-sections", "-fdata-sections", "-Wall", "-Wextra",
            "-Werror", "-I", str(CASE), "-c", str(SOURCE), "-o", str(output),
        ], capture_output=True, text=True)
        if proc.returncode != 0:
            raise AuditError(f"target compile failed: {proc.stderr}")
        nm_proc = subprocess.run([
            nm, "-g", "--defined-only", str(output),
        ], capture_output=True, text=True)
        if nm_proc.returncode != 0:
            raise AuditError(f"target symbol audit failed: {nm_proc.stderr}")
        symbols = set()
        for line in nm_proc.stdout.splitlines():
            parts = line.split()
            if len(parts) >= 3:
                symbols.add(parts[-1])
        data = output.read_bytes()
        return len(data), sha256(data), symbols


def analyze() -> dict[str, object]:
    blob = BLOB.read_bytes()
    if sha256(blob) != BLOB_SHA256:
        raise AuditError("case blob identity changed")
    app = blob[WRAPPER_BYTES:]
    mapped_functions = function_rows()
    if sha256(CORPUS.read_bytes()) != CORPUS_SHA256:
        raise AuditError("Case final-frontier corpus identity changed")
    evidence = evidence_rows()
    prior = json.loads(PRIOR.read_text(encoding="utf-8"))
    prior_remaining = int(prior["metrics"]["unclassified_bytes_after"])
    if prior_remaining != 16854:
        raise AuditError("prior Case admission tip changed")
    if len(FUNCTIONS) != 189 or set(FUNCTIONS) != set(SYMBOLS):
        raise AuditError("semantic-leaf address set changed")
    supplemental_bytes = sum(
        FUNCTIONS[address][0] for address in SUPPLEMENTAL_DECOMPILATION_PINS)
    if len(SUPPLEMENTAL_DECOMPILATION_PINS) != 11 or supplemental_bytes != 148:
        raise AuditError("supplemental semantic decompilation pins changed")
    sequence_bytes = sum(
        FUNCTIONS[address][0] for address in SEQUENCE_DECOMPILATION_PINS)
    if len(SEQUENCE_DECOMPILATION_PINS) != 15 or sequence_bytes != 642:
        raise AuditError("serial sequence semantic delta changed")

    combined_source = SOURCE.read_text(encoding="utf-8") + HEADER.read_text(
        encoding="utf-8")
    if combined_source.count("SPDX-License-Identifier: MIT") != 2:
        raise AuditError("source license declarations changed")
    for path, (expected_size, expected_sha) in SOURCE_PINS.items():
        data = path.read_bytes()
        if len(data) != expected_size or sha256(data) != expected_sha:
            raise AuditError(f"source identity changed: {path.relative_to(ROOT)}")
    if any(token in combined_source for token in FORBIDDEN_SOURCE_TOKENS):
        raise AuditError("source contains a forbidden raw-instruction construct")
    if RAW_ARRAY_RE.search(combined_source):
        raise AuditError("source contains an embedded byte/word array")

    object_size, object_sha, compiled_symbols = target_compile()
    expected_symbols = set(SYMBOLS.values())
    if compiled_symbols != expected_symbols:
        raise AuditError(
            f"target exports changed: {sorted(compiled_symbols)} != "
            f"{sorted(expected_symbols)}")

    admissions = []
    for address, (size, digest, symbol, contract) in sorted(FUNCTIONS.items()):
        row = mapped_functions.get(address)
        if row is None or row["ownership_category"] != "unresolved":
            raise AuditError(f"function-map boundary changed at {address:#x}")
        if int(row["size"], 0) != size:
            raise AuditError(f"function size changed at {address:#x}")
        body = app[address - APP_BASE:address - APP_BASE + size]
        if len(body) != size or sha256(body) != digest:
            raise AuditError(
                f"authenticated instruction identity changed at {address:#x}")
        evidence_row = evidence.get(address)
        if (evidence_row is None or int(evidence_row["address"]) != address or
                evidence_row["address_hex"] != f"0x{address:08X}" or
                int(evidence_row["size"]) != size or
                evidence_row["name"] != row["name"] or
                evidence_row["instruction_sha256"] != digest or
                evidence_row["prior_classification"] !=
                "project_source_candidate_not_routed"):
            raise AuditError(
                f"semantic decompilation evidence changed at {address:#x}")
        decompilation = evidence_row.get("decompilation")
        decompilation_digest = evidence_row.get("decompilation_sha256")
        if (not isinstance(decompilation, str) or not decompilation or
                not isinstance(decompilation_digest, str) or
                sha256(decompilation.encode("utf-8")) != decompilation_digest):
            raise AuditError(
                f"semantic decompilation content changed at {address:#x}")
        if (address in SUPPLEMENTAL_DECOMPILATION_PINS and
                decompilation_digest !=
                SUPPLEMENTAL_DECOMPILATION_PINS[address]):
            raise AuditError(
                f"supplemental semantic evidence changed at {address:#x}")
        if (address in SEQUENCE_DECOMPILATION_PINS and
                decompilation_digest !=
                SEQUENCE_DECOMPILATION_PINS[address]):
            raise AuditError(
                f"serial sequence semantic evidence changed at {address:#x}")
        admissions.append({
            "entry": address,
            "size": size,
            "name": row["name"],
            "instruction_sha256": digest,
            "source": str(SOURCE.relative_to(ROOT)),
            "symbol": symbol,
            "contract": contract,
            "license": "MIT",
            "status": "isolated_source_candidate_not_routed",
        })
    admitted_bytes = sum(int(row["size"]) for row in admissions)
    if admitted_bytes != 14208:
        raise AuditError(f"semantic-leaf byte total changed: {admitted_bytes}")
    post_baseline_functions = len(admissions) - PRIOR_CERTIFIED_FUNCTIONS
    post_baseline_bytes = (
        admitted_bytes - PRIOR_CERTIFIED_INSTRUCTION_BYTES)
    if post_baseline_functions != 160 or post_baseline_bytes != 14024:
        raise AuditError("post-baseline semantic admission delta changed")
    return {
        "schema_version": 1,
        "component": "G2 charging-case semantic leaves",
        "analysis_mode": (
            "offline authenticated instruction/source/build audit; caller-owned "
            "buffers only; no hardware, MMIO, flash, reset, signing, or "
            "deployment operation"),
        "integration": "isolated source candidate; production routing absent",
        "admissions": admissions,
        "metrics": {
            "admitted_functions": len(admissions),
            "admitted_instruction_bytes": admitted_bytes,
            "prior_certified_functions": PRIOR_CERTIFIED_FUNCTIONS,
            "prior_certified_instruction_bytes":
                PRIOR_CERTIFIED_INSTRUCTION_BYTES,
            "post_baseline_admitted_functions": post_baseline_functions,
            "post_baseline_admitted_instruction_bytes": post_baseline_bytes,
            "authenticated_decompilation_rows": len(admissions),
            "authenticated_decompilation_instruction_bytes": admitted_bytes,
            "supplemental_decompilation_pin_rows": len(
                SUPPLEMENTAL_DECOMPILATION_PINS),
            "supplemental_decompilation_pin_instruction_bytes":
                supplemental_bytes,
            "serial_sequence_functions": len(SEQUENCE_DECOMPILATION_PINS),
            "serial_sequence_instruction_bytes": sequence_bytes,
            "unclassified_bytes_before": prior_remaining,
            "unclassified_bytes_after": prior_remaining - admitted_bytes,
            "target_object_bytes": object_size,
            "target_object_sha256": object_sha,
            "target_missing_symbols": 0,
            "target_unexpected_symbols": 0,
            "embedded_instruction_byte_arrays": 0,
        },
        "software_source_complete": True,
        "software_source_complete_scope": "the 189 admitted semantic leaves only",
        "case_image_source_complete": False,
        "production_routed": False,
        "hardware_validation": "deferred by project direction",
        "hardware_operations": [],
    }


def write_outputs(report: dict[str, object]) -> None:
    with OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(["# SPDX-License-Identifier: MIT"])
        writer.writerow([
            "entry", "size", "name", "instruction_sha256", "source", "symbol",
            "contract", "license", "status",
        ])
        for row in report["admissions"]:
            writer.writerow([
                f"0x{int(row['entry']):08X}", row["size"], row["name"],
                row["instruction_sha256"], row["source"], row["symbol"],
                row["contract"], row["license"], row["status"],
            ])
    slim = {key: value for key, value in report.items() if key != "admissions"}
    SUMMARY.write_text(json.dumps(slim, indent=2, sort_keys=True) + "\n",
                       encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-manifests", action="store_true")
    args = parser.parse_args()
    report = analyze()
    if args.write_manifests:
        write_outputs(report)
    print(json.dumps(report["metrics"], sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AuditError as exc:
        raise SystemExit(f"Case semantic-leaf audit failed: {exc}") from exc
