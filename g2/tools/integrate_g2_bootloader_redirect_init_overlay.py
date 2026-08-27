#!/usr/bin/env python3
"""Synchronize reviewed bootloader runtime production tranches.

This tool only reconciles local JSON ownership metadata with the already built
bootloader provider contract.  It never assembles a signed package and never
communicates with hardware.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
CONTRACT = (
    ROOT / "components" / "bootloader" / "core_overlay" / "build"
    / "provider-contract.json"
)
OVERLAY_CONFIG = (
    ROOT / "components" / "bootloader" / "core_overlay" / "overlay.json"
)
MANIFEST = ROOT / "manifests" / "g2-2.2.6.10-core-source.json"


def write_json(path: Path, value: Any) -> None:
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def ownership_key(region: dict[str, Any]) -> tuple[Any, ...]:
    return tuple(
        region[key]
        for key in ("file_offset", "size", "target_address", "address_status")
    )


def new_region(contract_region: dict[str, Any]) -> dict[str, Any]:
    name = contract_region["name"]
    address = int(contract_region["target_address"])
    descriptions = {
        "opaque_before_replace_bootloader_redirect_init": (
            "bootloader_opaque_before_redirect_init",
            "Official Apollo bootloader bytes before recovered redirect_init",
        ),
        "replace_bootloader_redirect_init_source_redirect": (
            "bootloader_redirect_init_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete "
            "S200 bootloader redirect_init mutex initializer",
        ),
        "opaque_before_replace_bootloader_aeabi_memset": (
            "bootloader_opaque_between_redirect_init_and_aeabi_memset",
            "Official Apollo bootloader bytes between redirect_init and the "
            "source-replaced Arm EABI byte-fill primitive",
        ),
        "replace_bootloader_aeabi_memset_source_redirect": (
            "bootloader_aeabi_memset_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete "
            "Arm EABI byte-fill primitive",
        ),
        "opaque_before_replace_bootloader_aeabi_memcpy": (
            "bootloader_opaque_between_aeabi_memset_and_aeabi_memcpy",
            "Official Apollo bootloader bytes between the Arm EABI byte-fill "
            "and forward-copy primitives",
        ),
        "replace_bootloader_aeabi_memcpy_source_redirect": (
            "bootloader_aeabi_memcpy_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete "
            "Arm EABI forward-copy primitive",
        ),
        "opaque_before_replace_bootloader_memcmp": (
            "bootloader_opaque_between_aeabi_memcpy_and_memcmp",
            "Official Apollo bootloader bytes between the Arm EABI forward-copy "
            "and bounded byte-comparison primitives",
        ),
        "replace_bootloader_memcmp_source_redirect": (
            "bootloader_memcmp_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete "
            "bounded byte-comparison primitive",
        ),
        "replace_bootloader_crc32_source_redirect": (
            "bootloader_crc32_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete "
            "reflected CRC-32 update primitive",
        ),
        "opaque_before_replace_bootloader_strcspn": (
            "bootloader_opaque_between_memcmp_and_strcspn",
            "Official Apollo bootloader bytes between the bounded byte "
            "comparison and reject-set span primitives",
        ),
        "replace_bootloader_strcspn_source_redirect": (
            "bootloader_strcspn_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete "
            "reject-set string-span primitive",
        ),
        "replace_bootloader_strspn_source_redirect": (
            "bootloader_strspn_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete "
            "accept-set string-span primitive",
        ),
        "replace_bootloader_store_200270cc_source_redirect": (
            "bootloader_store_200270cc_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete "
            "SRAM-word setter at 0x200270CC",
        ),
        "replace_bootloader_udiv10_source_redirect": (
            "bootloader_udiv10_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete "
            "unsigned 64-bit divide-by-ten helper",
        ),
        "replace_bootloader_udec_digits_source_redirect": (
            "bootloader_udec_digits_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete "
            "unsigned decimal digit-count helper",
        ),
        "replace_bootloader_sdec_digits_source_redirect": (
            "bootloader_sdec_digits_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete "
            "signed-magnitude decimal digit-count helper",
        ),
        "replace_bootloader_hex_digits_source_redirect": (
            "bootloader_hex_digits_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete "
            "hexadecimal digit-count helper",
        ),
        "replace_bootloader_parse_dec_source_redirect": (
            "bootloader_parse_dec_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete "
            "wrapping decimal parser",
        ),
        "replace_bootloader_u64_to_dec_source_redirect": (
            "bootloader_u64_to_dec_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete "
            "unsigned 64-bit decimal output helper",
        ),
        "replace_bootloader_u64_to_hex_source_redirect": (
            "bootloader_u64_to_hex_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete "
            "unsigned 64-bit hexadecimal output helper",
        ),
        "replace_bootloader_nullable_strlen_source_redirect": (
            "bootloader_nullable_strlen_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete "
            "nullable string-length helper",
        ),
        "replace_bootloader_repeat_char_source_redirect": (
            "bootloader_repeat_char_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete "
            "null-output-aware repeated-character helper",
        ),
        "replace_bootloader_float_to_fixed_source_redirect": (
            "bootloader_float_to_fixed_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete "
            "fixed-point float formatter",
        ),
        "replace_bootloader_format_core_source_redirect": (
            "bootloader_format_core_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete "
            "bootloader logging formatter core",
        ),
        "replace_bootloader_log_dispatch_source_redirect": (
            "bootloader_log_dispatch_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete "
            "bootloader variadic logging dispatch wrapper",
        ),
        "opaque_before_replace_bootloader_strstr": (
            "bootloader_logging_literal_pool",
            "Authenticated bootloader logging literal-pool data between the "
            "variadic dispatch wrapper and substring-search primitive",
        ),
        "replace_bootloader_strstr_source_redirect": (
            "bootloader_strstr_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete "
            "bootloader substring-search primitive",
        ),
        "opaque_before_replace_bootloader_critical_context": (
            "bootloader_two_byte_control_stubs",
            "Authenticated two-byte self-loop and no-op return stubs between "
            "substring search and the critical-context predicate",
        ),
        "replace_bootloader_critical_context_source_redirect": (
            "bootloader_critical_context_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete "
            "bootloader critical-context predicate",
        ),
        "replace_bootloader_gate_acquire_source_redirect": (
            "bootloader_gate_acquire_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete "
            "recovered runtime-state gate acquisition wrapper",
        ),
        "replace_bootloader_gate_state_source_redirect": (
            "bootloader_gate_state_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete "
            "recovered runtime-state and SRAM-gate mapper",
        ),
        "replace_bootloader_gate_release_source_redirect": (
            "bootloader_gate_release_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete "
            "recovered runtime-state gate release wrapper",
        ),
        "replace_bootloader_context_value_source_redirect": (
            "bootloader_context_value_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete "
            "recovered critical-context value-dispatch wrapper",
        ),
        "replace_bootloader_runtime_dispatch_4160fe_source_redirect": (
            "bootloader_runtime_dispatch_4160fe_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete "
            "recovered address-identified runtime dispatcher",
        ),
        "replace_bootloader_runtime_value_4161c6_source_redirect": (
            "bootloader_runtime_value_4161c6_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete "
            "recovered address-identified retained-value wrapper",
        ),
        "replace_bootloader_runtime_call_4161ce_source_redirect": (
            "bootloader_runtime_call_4161ce_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete "
            "recovered address-identified validated runtime call wrapper",
        ),
        "replace_bootloader_runtime_action_416200_source_redirect": (
            "bootloader_runtime_action_416200_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete "
            "recovered address-identified guarded runtime action wrapper",
        ),
        "replace_bootloader_runtime_transfer_41623a_source_redirect": (
            "bootloader_runtime_transfer_41623a_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete "
            "recovered address-identified two-phase runtime transfer wrapper",
        ),
        "replace_bootloader_runtime_wait_4162c4_source_redirect": (
            "bootloader_runtime_wait_4162c4_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete "
            "recovered address-identified masked runtime wait wrapper",
        ),
        "replace_bootloader_runtime_notify_416378_source_redirect": (
            "bootloader_runtime_notify_416378_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete "
            "recovered address-identified optional runtime notification wrapper",
        ),
        "replace_bootloader_runtime_callback_41639a_source_redirect": (
            "bootloader_runtime_callback_41639a_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete "
            "recovered address-identified registered runtime callback adapter",
        ),
        "replace_bootloader_runtime_register_4163b2_source_redirect": (
            "bootloader_runtime_register_4163b2_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete "
            "recovered address-identified registered runtime object constructor",
        ),
        "replace_bootloader_runtime_submit_41649a_source_redirect": (
            "bootloader_runtime_submit_41649a_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete "
            "recovered address-identified guarded runtime submission wrapper",
        ),
        "replace_bootloader_runtime_create_4164da_source_redirect": (
            "bootloader_runtime_create_4164da_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete "
            "recovered address-identified runtime object creation wrapper",
        ),
        "replace_bootloader_runtime_flags_set_41652e_source_redirect": (
            "bootloader_runtime_flags_set_41652e_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete "
            "recovered address-identified event-flags set wrapper",
        ),
        "opaque_before_replace_bootloader_runtime_flags_wait_416590": (
            "bootloader_event_flags_sram_literal",
            "Authenticated 0x200270D4 SRAM address literal retained between "
            "the event-flags set and wait wrappers",
        ),
        "replace_bootloader_runtime_flags_wait_416590_source_redirect": (
            "bootloader_runtime_flags_wait_416590_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete "
            "recovered address-identified event-flags wait wrapper",
        ),
        "replace_bootloader_runtime_flags_create_416610_source_redirect": (
            "bootloader_runtime_flags_create_416610_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete "
            "recovered address-identified event-flags creation wrapper",
        ),
        "replace_bootloader_runtime_handle_acquire_4166aa_source_redirect": (
            "bootloader_runtime_handle_acquire_4166aa_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete recovered tagged-handle acquire wrapper",
        ),
        "replace_bootloader_runtime_handle_release_416710_source_redirect": (
            "bootloader_runtime_handle_release_416710_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete recovered tagged-handle release wrapper",
        ),
        "replace_bootloader_runtime_semaphore_create_416762_source_redirect": (
            "bootloader_runtime_semaphore_create_416762_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete recovered semaphore creation wrapper",
        ),
        "replace_bootloader_runtime_queue_create_416816_source_redirect": (
            "bootloader_runtime_queue_create_416816_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete recovered message-queue creation wrapper",
        ),
        "replace_bootloader_runtime_queue_put_4168a2_source_redirect": (
            "bootloader_runtime_queue_put_4168a2_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete CMSIS message-queue put wrapper",
        ),
        "replace_bootloader_runtime_queue_get_416920_source_redirect": (
            "bootloader_runtime_queue_get_416920_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete CMSIS message-queue get wrapper",
        ),
        "replace_bootloader_runtime_bit_width_4169a4_source_redirect": (
            "bootloader_runtime_bit_width_4169a4_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete unsigned bit-width helper",
        ),
        "opaque_before_replace_bootloader_runtime_bit_width_4169a4": (
            "bootloader_runtime_queue_io_scb_literal_pool",
            "Authenticated ten-byte alignment and SCB ICSR literal pool retained after the message-queue wrappers",
        ),
        "replace_bootloader_runtime_ctz_4169e2_source_redirect": (
            "bootloader_runtime_ctz_4169e2_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete trailing-zero helper",
        ),
        "replace_bootloader_runtime_log2_4169f2_source_redirect": (
            "bootloader_runtime_log2_4169f2_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete unsigned floor-log2 helper",
        ),
        "opaque_before_replace_bootloader_runtime_queue_get_416920": (
            "bootloader_runtime_queue_io_scb_literal_pool",
            "Authenticated alignment and SCB ICSR literal bytes retained between the message-queue wrappers and the next executable body",
        ),
        "opaque_before_replace_easylogger_get_fmt_enabled": (
            "bootloader_easylogger_csi_start_literal_0x00417ad0",
            "Authenticated EasyLogger CSI-start literal and alignment bytes",
        ),
        "opaque_before_replace_bootloader_easylogger_mutex_create_41a648": (
            "bootloader_easylogger_port_transition_0x00417bb8",
            "Authenticated bootloader compatibility bytes retained after the EasyLogger output-lock enable entry and before the boot-port helpers",
        ),
        "opaque_before_replace_bootloader_easylogger_port_get_p_info_41a6f0": (
            "bootloader_easylogger_port_literals_0x0041a6da",
            "Authenticated EasyLogger percent-d format, mutex-handle, mutex-attribute, time-buffer, and unknown-name pointer literals",
        ),
        "opaque_before_replace_easylogger_strcpy": (
            "bootloader_easylogger_post_port_transition_0x0041a700",
            "Authenticated bootloader compatibility bytes retained after the EasyLogger boot-port helpers and before the bounded-copy helper",
        ),
        "opaque_before_replace_bootloader_easylogger_driver_output_41b854": (
            "bootloader_easylogger_pre_driver_transition_0x0041b1fa",
            "Authenticated bootloader compatibility bytes retained between the bounded-copy helper and EasyLogger channel-one output driver",
        ),
        "replace_bootloader_easylogger_driver_output_41b854_source_redirect": (
            "bootloader_easylogger_driver_output_41b854_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete G2 EasyLogger channel-one output driver",
        ),
        "opaque_before_replace_bootloader_easylogger_channel_write_41f918": (
            "bootloader_easylogger_pre_channel_transport_0x0041b862",
            "Authenticated bootloader compatibility bytes retained between the EasyLogger output driver and four-channel transfer routine",
        ),
        "replace_bootloader_easylogger_channel_write_41f918_source_redirect": (
            "bootloader_easylogger_channel_write_41f918_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete G2 four-channel transfer routine",
        ),
        "opaque_before_replace_bootloader_delay_milliseconds_41f9d8": (
            "bootloader_easylogger_transport_vector_literal_island_0x0041f9b6",
            "Authenticated vector and literal island retained after the EasyLogger channel transport",
        ),
        "replace_bootloader_delay_milliseconds_41f9d8_source_redirect": (
            "bootloader_delay_milliseconds_41f9d8_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete millisecond-to-microsecond delay wrapper",
        ),
        "replace_bootloader_delay_41f9e6_source_redirect": (
            "bootloader_delay_41f9e6_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete raw boot delay wrapper",
        ),
        "opaque_before_replace_bootloader_initializer_priority_compare_41f9f0": (
            "bootloader_initializer_comparator_alignment_0x0041f9ee",
            "Authenticated two-byte alignment retained before the initializer priority comparator",
        ),
        "replace_bootloader_initializer_priority_compare_41f9f0_source_redirect": (
            "bootloader_initializer_priority_compare_41f9f0_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete initializer-record priority comparator",
        ),
        "replace_bootloader_run_initializers_41f9f8_source_redirect": (
            "bootloader_run_initializers_41f9f8_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete capped initializer-table runner",
        ),
        "opaque_before_replace_bootloader_platform_setup_41fa50": (
            "bootloader_pre_platform_setup_literals_0x0041fa40",
            "Authenticated initializer-table pointers and alignment retained before the boot-platform setup entry",
        ),
        "replace_bootloader_platform_setup_41fa50_source_redirect": (
            "bootloader_platform_setup_41fa50_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete guarded teardown, configuration submission, and channel setup entry",
        ),
        "replace_bootloader_guarded_teardown_41fa98_source_redirect": (
            "bootloader_guarded_teardown_41fa98_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete guarded two-stage bootloader teardown entry",
        ),
        "opaque_before_replace_bootloader_pin_groups_41fadc": (
            "bootloader_guarded_teardown_literal_pool_0x0041fad0",
            "Authenticated guard, platform-configuration, and pin-configuration pointer literals retained after guarded teardown",
        ),
        "replace_bootloader_pin_groups_41fadc_source_redirect": (
            "bootloader_pin_groups_41fadc_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete two-bank pin-group configuration dispatcher",
        ),
        "opaque_before_replace_bootloader_allocator_init_41fd70": (
            "bootloader_pin_groups_post_dispatch_literal_pool_0x0041fcf6",
            "Authenticated pin-configuration and allocator literals retained between the pin-group dispatcher and TLSF pool initializer",
        ),
        "replace_bootloader_allocator_init_41fd70_source_redirect": (
            "bootloader_allocator_init_41fd70_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete TLSF pool initialization and handle-publication entry",
        ),
        "opaque_before_replace_ambiq_mspi_interrupt_clear": (
            "bootloader_opaque_after_easylogger_transport",
            "Authenticated bootloader compatibility bytes retained after the source-replaced allocator initializer and before the AmbiqSuite MSPI interrupt-clear leaf",
        ),
        "open_cfw_bootloader_easylogger_driver_output_41b854_source_leaf": (
            "bootloader_easylogger_driver_output_41b854_source_leaf",
            "Compiled clean-room G2 EasyLogger level-dropping channel-one output driver",
        ),
        "open_cfw_bootloader_easylogger_channel_write_41f918_source_leaf": (
            "bootloader_easylogger_channel_write_41f918_source_leaf",
            "Compiled clean-room G2 four-channel descriptor transfer and completion-polling routine",
        ),
        "open_cfw_bootloader_delay_milliseconds_41f9d8_source_leaf": (
            "bootloader_delay_milliseconds_41f9d8_source_leaf",
            "Compiled clean-room G2 millisecond-to-microsecond delay wrapper",
        ),
        "open_cfw_bootloader_delay_41f9e6_source_leaf": (
            "bootloader_delay_41f9e6_source_leaf",
            "Compiled clean-room G2 raw boot delay wrapper",
        ),
        "open_cfw_bootloader_initializer_priority_compare_41f9f0_source_leaf": (
            "bootloader_initializer_priority_compare_41f9f0_source_leaf",
            "Compiled clean-room G2 initializer-record priority comparator",
        ),
        "open_cfw_bootloader_run_initializers_41f9f8_source_leaf": (
            "bootloader_run_initializers_41f9f8_source_leaf",
            "Compiled clean-room G2 capped initializer-table runner",
        ),
        "open_cfw_bootloader_guarded_teardown_41fa98_source_leaf": (
            "bootloader_guarded_teardown_41fa98_source_leaf",
            "Compiled clean-room G2 guarded two-stage teardown and pin-state reconciliation entry",
        ),
        "open_cfw_bootloader_platform_setup_41fa50_source_leaf": (
            "bootloader_platform_setup_41fa50_source_leaf",
            "Compiled clean-room G2 platform reset, configuration submission, and channel setup entry",
        ),
        "open_cfw_bootloader_pin_groups_41fadc_source_leaf": (
            "bootloader_pin_groups_41fadc_source_leaf",
            "Compiled clean-room G2 two-bank pin-group configuration dispatcher",
        ),
        "open_cfw_bootloader_allocator_init_41fd70_source_leaf": (
            "bootloader_allocator_init_41fd70_source_leaf",
            "Compiled clean-room G2 TLSF pool initialization, handle-publication, and diagnostic entry",
        ),
        "open_cfw_bootloader_redirect_init_alignment_padding": (
            "bootloader_redirect_init_alignment_padding",
            "Generated two-byte alignment before the redirect_init closure",
        ),
        "open_cfw_bootloader_redirect_init_source_leaf": (
            "bootloader_redirect_init_source_leaf",
            "Compiled clean-room redirect_init function and authenticated "
            "diagnostic read-only-data closure",
        ),
        "open_cfw_bootloader_aeabi_memset_alignment_padding": (
            "bootloader_aeabi_memset_alignment_padding",
            "Generated one-byte alignment before the Arm EABI byte-fill leaf",
        ),
        "open_cfw_bootloader_aeabi_memset_source_leaf": (
            "bootloader_aeabi_memset_source_leaf",
            "Compiled clean-room Arm EABI byte-fill primitive",
        ),
        "open_cfw_bootloader_aeabi_memcpy_source_leaf": (
            "bootloader_aeabi_memcpy_source_leaf",
            "Compiled clean-room Arm EABI forward-copy primitive",
        ),
        "open_cfw_bootloader_memcmp_source_leaf": (
            "bootloader_memcmp_source_leaf",
            "Compiled clean-room bounded byte-comparison primitive",
        ),
        "open_cfw_bootloader_crc32_alignment_padding": (
            "bootloader_crc32_alignment_padding",
            "Generated two-byte alignment before the reflected CRC-32 leaf",
        ),
        "open_cfw_bootloader_crc32_source_leaf": (
            "bootloader_crc32_source_leaf",
            "Compiled clean-room reflected CRC-32 update primitive",
        ),
        "open_cfw_bootloader_strcspn_source_leaf": (
            "bootloader_strcspn_source_leaf",
            "Compiled clean-room reject-set string-span primitive",
        ),
        "open_cfw_bootloader_strspn_source_leaf": (
            "bootloader_strspn_source_leaf",
            "Compiled clean-room accept-set string-span primitive",
        ),
        "open_cfw_bootloader_store_200270cc_source_leaf": (
            "bootloader_store_200270cc_source_leaf",
            "Compiled clean-room SRAM-word setter for 0x200270CC",
        ),
        "open_cfw_bootloader_udiv10_source_leaf": (
            "bootloader_udiv10_source_leaf",
            "Compiled clean-room unsigned 64-bit divide-by-ten helper",
        ),
        "open_cfw_bootloader_udec_digits_source_leaf": (
            "bootloader_udec_digits_source_leaf",
            "Compiled clean-room unsigned decimal digit-count helper",
        ),
        "open_cfw_bootloader_sdec_digits_source_leaf": (
            "bootloader_sdec_digits_source_leaf",
            "Compiled clean-room signed-magnitude decimal digit-count helper",
        ),
        "open_cfw_bootloader_hex_digits_source_leaf": (
            "bootloader_hex_digits_source_leaf",
            "Compiled clean-room hexadecimal digit-count helper",
        ),
        "open_cfw_bootloader_parse_dec_source_leaf": (
            "bootloader_parse_dec_source_leaf",
            "Compiled clean-room wrapping decimal parser",
        ),
        "open_cfw_bootloader_u64_to_dec_source_leaf": (
            "bootloader_u64_to_dec_source_leaf",
            "Compiled clean-room unsigned 64-bit decimal output helper",
        ),
        "open_cfw_bootloader_u64_to_hex_source_leaf": (
            "bootloader_u64_to_hex_source_leaf",
            "Compiled clean-room unsigned 64-bit hexadecimal output helper",
        ),
        "open_cfw_bootloader_nullable_strlen_source_leaf": (
            "bootloader_nullable_strlen_source_leaf",
            "Compiled clean-room nullable string-length helper",
        ),
        "open_cfw_bootloader_repeat_char_source_leaf": (
            "bootloader_repeat_char_source_leaf",
            "Compiled clean-room null-output-aware repeated-character helper",
        ),
        "open_cfw_bootloader_float_to_fixed_source_leaf": (
            "bootloader_float_to_fixed_source_leaf",
            "Compiled clean-room fixed-point float formatter",
        ),
        "open_cfw_bootloader_format_core_source_leaf": (
            "bootloader_format_core_source_leaf",
            "Compiled clean-room bootloader logging formatter core",
        ),
        "open_cfw_bootloader_log_dispatch_source_leaf": (
            "bootloader_log_dispatch_source_leaf",
            "Compiled clean-room bootloader variadic logging dispatch wrapper",
        ),
        "open_cfw_bootloader_strstr_source_leaf": (
            "bootloader_strstr_source_leaf",
            "Compiled clean-room dependency-free substring-search primitive",
        ),
        "open_cfw_bootloader_critical_context_source_leaf": (
            "bootloader_critical_context_source_leaf",
            "Compiled clean-room IPSR and interrupt-mask context predicate",
        ),
        "open_cfw_bootloader_gate_acquire_source_leaf": (
            "bootloader_gate_acquire_source_leaf",
            "Compiled clean-room recovered runtime-state gate acquisition wrapper",
        ),
        "open_cfw_bootloader_gate_state_source_leaf": (
            "bootloader_gate_state_source_leaf",
            "Compiled clean-room recovered runtime-state and SRAM-gate mapper",
        ),
        "open_cfw_bootloader_gate_release_source_leaf": (
            "bootloader_gate_release_source_leaf",
            "Compiled clean-room recovered runtime-state gate release wrapper",
        ),
        "open_cfw_bootloader_context_value_source_leaf": (
            "bootloader_context_value_source_leaf",
            "Compiled clean-room recovered critical-context value dispatcher",
        ),
        "open_cfw_bootloader_runtime_dispatch_4160fe_source_leaf": (
            "bootloader_runtime_dispatch_4160fe_source_leaf",
            "Compiled clean-room recovered address-identified runtime dispatcher",
        ),
        "open_cfw_bootloader_runtime_value_4161c6_source_leaf": (
            "bootloader_runtime_value_4161c6_source_leaf",
            "Compiled clean-room recovered address-identified retained-value wrapper",
        ),
        "open_cfw_bootloader_runtime_call_4161ce_source_leaf": (
            "bootloader_runtime_call_4161ce_source_leaf",
            "Compiled clean-room recovered address-identified validated runtime call wrapper",
        ),
        "open_cfw_bootloader_runtime_action_416200_source_leaf": (
            "bootloader_runtime_action_416200_source_leaf",
            "Compiled clean-room recovered address-identified guarded runtime action wrapper",
        ),
        "open_cfw_bootloader_runtime_transfer_41623a_alignment_padding": (
            "bootloader_runtime_transfer_41623a_alignment_padding",
            "Generated two-byte alignment before the runtime transfer leaf",
        ),
        "open_cfw_bootloader_runtime_transfer_41623a_source_leaf": (
            "bootloader_runtime_transfer_41623a_source_leaf",
            "Compiled clean-room recovered address-identified two-phase runtime transfer wrapper",
        ),
        "open_cfw_bootloader_runtime_wait_4162c4_source_leaf": (
            "bootloader_runtime_wait_4162c4_source_leaf",
            "Compiled clean-room recovered address-identified masked runtime wait wrapper",
        ),
        "open_cfw_bootloader_runtime_notify_416378_source_leaf": (
            "bootloader_runtime_notify_416378_source_leaf",
            "Compiled clean-room recovered address-identified optional runtime notification wrapper",
        ),
        "open_cfw_bootloader_runtime_callback_41639a_source_leaf": (
            "bootloader_runtime_callback_41639a_source_leaf",
            "Compiled clean-room recovered address-identified registered runtime callback adapter",
        ),
        "open_cfw_bootloader_runtime_register_4163b2_alignment_padding": (
            "bootloader_runtime_register_4163b2_alignment_padding",
            "Generated two-byte alignment before the registered runtime object constructor",
        ),
        "open_cfw_bootloader_runtime_register_4163b2_source_leaf": (
            "bootloader_runtime_register_4163b2_source_leaf",
            "Compiled clean-room recovered address-identified registered runtime object constructor",
        ),
        "open_cfw_bootloader_runtime_submit_41649a_source_leaf": (
            "bootloader_runtime_submit_41649a_source_leaf",
            "Compiled clean-room recovered address-identified guarded runtime submission wrapper",
        ),
        "open_cfw_bootloader_runtime_create_4164da_source_leaf": (
            "bootloader_runtime_create_4164da_source_leaf",
            "Compiled clean-room recovered address-identified runtime object creation wrapper",
        ),
        "open_cfw_bootloader_runtime_flags_set_41652e_source_leaf": (
            "bootloader_runtime_flags_set_41652e_source_leaf",
            "Compiled clean-room recovered address-identified event-flags set wrapper",
        ),
        "open_cfw_bootloader_runtime_flags_wait_416590_source_leaf": (
            "bootloader_runtime_flags_wait_416590_source_leaf",
            "Compiled clean-room recovered address-identified event-flags wait wrapper",
        ),
        "open_cfw_bootloader_runtime_flags_create_416610_source_leaf": (
            "bootloader_runtime_flags_create_416610_source_leaf",
            "Compiled clean-room recovered address-identified event-flags creation wrapper",
        ),
        "open_cfw_bootloader_runtime_handle_acquire_4166aa_source_leaf": (
            "bootloader_runtime_handle_acquire_4166aa_source_leaf",
            "Compiled clean-room recovered address-identified tagged-handle acquire wrapper",
        ),
        "open_cfw_bootloader_runtime_handle_release_416710_source_leaf": (
            "bootloader_runtime_handle_release_416710_source_leaf",
            "Compiled clean-room recovered address-identified tagged-handle release wrapper",
        ),
        "open_cfw_bootloader_runtime_semaphore_create_416762_source_leaf": (
            "bootloader_runtime_semaphore_create_416762_source_leaf",
            "Compiled clean-room recovered address-identified semaphore creation wrapper",
        ),
        "open_cfw_bootloader_runtime_queue_create_416816_source_leaf": (
            "bootloader_runtime_queue_create_416816_source_leaf",
            "Compiled clean-room recovered address-identified message-queue creation wrapper",
        ),
        "open_cfw_bootloader_runtime_queue_put_4168a2_source_leaf": (
            "bootloader_runtime_queue_put_4168a2_source_leaf",
            "Compiled CMSIS-FreeRTOS message-queue put wrapper over retained queue providers",
        ),
        "open_cfw_bootloader_runtime_queue_get_416920_source_leaf": (
            "bootloader_runtime_queue_get_416920_source_leaf",
            "Compiled CMSIS-FreeRTOS message-queue get wrapper over retained queue providers",
        ),
        "open_cfw_bootloader_runtime_bit_width_4169a4_source_leaf": (
            "bootloader_runtime_bit_width_4169a4_source_leaf",
            "Compiled clean-room unsigned bit-width helper",
        ),
        "open_cfw_bootloader_runtime_ctz_4169e2_source_leaf": (
            "bootloader_runtime_ctz_4169e2_source_leaf",
            "Compiled clean-room trailing-zero helper",
        ),
        "open_cfw_bootloader_runtime_log2_4169f2_source_leaf": (
            "bootloader_runtime_log2_4169f2_source_leaf",
            "Compiled clean-room unsigned floor-log2 helper",
        ),
    }
    tlsf_block_primitives = (
        "block_size_4169fc",
        "block_set_size_416a10",
        "block_is_last_416a2c",
        "block_is_free_416a40",
        "block_set_free_416a4c",
        "block_set_used_416a5a",
        "block_is_previous_free_416a68",
        "block_set_previous_free_416a74",
        "block_set_previous_used_416a82",
        "block_from_pointer_416a90",
        "block_to_pointer_416a9c",
        "offset_to_block_416aa6",
    )
    for primitive in tlsf_block_primitives:
        descriptions[f"replace_bootloader_tlsf_{primitive}_source_redirect"] = (
            f"bootloader_tlsf_{primitive}_source_replacement",
            "Generated entry redirect and NOP fill replacing an authenticated "
            f"TLSF v3.1 block-header primitive ({primitive})",
        )
        descriptions[f"open_cfw_bootloader_tlsf_{primitive}_source_leaf"] = (
            f"bootloader_tlsf_{primitive}_source_leaf",
            "Compiled BSD-3-Clause TLSF v3.1 block-header primitive "
            f"({primitive})",
        )
    tlsf_block_topology = (
        "block_prev_416aaa",
        "block_next_416ad0",
        "block_link_next_416b14",
        "block_mark_as_free_416b22",
        "block_mark_as_used_416b38",
        "align_up_416b4e",
        "align_down_416b7a",
        "align_pointer_416ba4",
    )
    for primitive in tlsf_block_topology:
        descriptions[f"replace_bootloader_tlsf_{primitive}_source_redirect"] = (
            f"bootloader_tlsf_{primitive}_source_replacement",
            "Generated entry redirect and NOP fill replacing an authenticated "
            f"TLSF v3.1 physical-block/alignment helper ({primitive})",
        )
        descriptions[f"open_cfw_bootloader_tlsf_{primitive}_source_leaf"] = (
            f"bootloader_tlsf_{primitive}_source_leaf",
            "Compiled BSD-3-Clause TLSF v3.1 physical-block/alignment helper "
            f"({primitive})",
        )
    tlsf_mapping = (
        "adjust_request_size_416bce",
        "mapping_insert_416bf8",
        "mapping_search_416c26",
    )
    for primitive in tlsf_mapping:
        descriptions[f"replace_bootloader_tlsf_{primitive}_source_redirect"] = (
            f"bootloader_tlsf_{primitive}_source_replacement",
            "Generated entry redirect and NOP fill replacing an authenticated "
            f"TLSF v3.1 request-size/class-mapping helper ({primitive})",
        )
        descriptions[f"open_cfw_bootloader_tlsf_{primitive}_source_leaf"] = (
            f"bootloader_tlsf_{primitive}_source_leaf",
            "Compiled BSD-3-Clause TLSF v3.1 request-size/class-mapping helper "
            f"({primitive})",
        )
    descriptions[
        "open_cfw_bootloader_tlsf_search_suitable_block_416c4e_alignment_padding"
    ] = (
        "bootloader_tlsf_free_list_alignment_padding",
        "Generated alignment before the TLSF v3.1 free-list helper cluster",
    )
    tlsf_free_lists = (
        "search_suitable_block_416c4e",
        "remove_free_block_416cc6",
        "insert_free_block_416d5c",
    )
    for primitive in tlsf_free_lists:
        descriptions[f"replace_bootloader_tlsf_{primitive}_source_redirect"] = (
            f"bootloader_tlsf_{primitive}_source_replacement",
            "Generated entry redirect and NOP fill replacing an authenticated "
            f"TLSF v3.1 free-list helper ({primitive})",
        )
        descriptions[f"open_cfw_bootloader_tlsf_{primitive}_source_leaf"] = (
            f"bootloader_tlsf_{primitive}_source_leaf",
            "Compiled BSD-3-Clause TLSF v3.1 free-list helper "
            f"({primitive})",
        )
    tlsf_allocator = (
        "block_remove_416e04",
        "block_insert_416e26",
        "block_can_split_416e48",
        "block_split_416e60",
        "block_absorb_416f20",
        "block_merge_previous_416f62",
        "block_merge_next_416fc6",
        "block_trim_free_41702a",
        "block_locate_free_41707c",
        "block_prepare_used_4170de",
    )
    for primitive in tlsf_allocator:
        descriptions[f"replace_bootloader_tlsf_{primitive}_source_redirect"] = (
            f"bootloader_tlsf_{primitive}_source_replacement",
            "Generated entry redirect and NOP fill replacing an authenticated "
            f"TLSF v3.1 allocator helper ({primitive})",
        )
        descriptions[f"open_cfw_bootloader_tlsf_{primitive}_source_leaf"] = (
            f"bootloader_tlsf_{primitive}_source_leaf",
            "Compiled BSD-3-Clause TLSF v3.1 allocator helper "
            f"({primitive})",
        )
    tlsf_public = (
        "control_construct_41711c",
        "pool_overhead_41714c",
        "add_pool_41715c",
        "create_417208",
        "create_with_pool_417240",
        "malloc_41726a",
        "free_417290",
    )
    for primitive in tlsf_public:
        descriptions[f"replace_bootloader_tlsf_{primitive}_source_redirect"] = (
            f"bootloader_tlsf_{primitive}_source_replacement",
            "Generated entry redirect and NOP fill replacing an authenticated "
            f"TLSF v3.1 public/control entry ({primitive})",
        )
        descriptions[f"open_cfw_bootloader_tlsf_{primitive}_source_leaf"] = (
            f"bootloader_tlsf_{primitive}_source_leaf",
            "Compiled BSD-3-Clause TLSF v3.1 public/control entry "
            f"({primitive})",
        )
    descriptions[
        "opaque_before_replace_bootloader_easylogger_init_41733c"
    ] = (
        "bootloader_tlsf_easylogger_transition_data_0x004172da",
        "Authenticated TLSF/EasyLogger transition literals and alignment",
    )
    easylogger_control = (
        "init_41733c",
        "start_417392",
        "set_output_enabled_4173ca",
        "set_text_color_enabled_417438",
        "set_fmt_4174a6",
        "set_filter_lvl_417510",
        "output_lock_417570",
        "output_unlock_417592",
        "filter_tag_lvl_default_4175b4",
        "get_filter_tag_lvl_41760a",
        "output_4176ce",
        "output_lock_enabled_417b7c",
    )
    for entry in easylogger_control:
        role = (
            "output"
            if entry == "output_4176ce"
            else "output-lock control"
            if entry == "output_lock_enabled_417b7c"
            else "control"
        )
        descriptions[
            f"replace_bootloader_easylogger_{entry}_source_redirect"
        ] = (
            f"bootloader_easylogger_{entry}_source_replacement",
            "Generated entry redirect and NOP fill replacing an authenticated "
            f"EasyLogger {role} entry ({entry})",
        )
        descriptions[
            f"open_cfw_bootloader_easylogger_{entry}_source_leaf"
        ] = (
            f"bootloader_easylogger_{entry}_source_leaf",
            f"Compiled MIT EasyLogger {role} entry ({entry})",
        )
    easylogger_port = (
        "mutex_create_41a648",
        "mutex_acquire_41a65c",
        "mutex_release_41a672",
        "port_init_41a684",
        "port_output_41a692",
        "port_output_lock_41a69a",
        "port_output_unlock_41a6a2",
        "port_get_time_41a6aa",
        "task_name_41a6c2",
        "port_get_p_info_41a6f0",
        "port_get_t_info_41a6f8",
    )
    for entry in easylogger_port:
        descriptions[
            f"replace_bootloader_easylogger_{entry}_source_redirect"
        ] = (
            f"bootloader_easylogger_{entry}_source_replacement",
            "Generated entry redirect and NOP fill replacing an authenticated "
            f"EasyLogger boot-port entry ({entry})",
        )
        descriptions[
            f"open_cfw_bootloader_easylogger_{entry}_source_leaf"
        ] = (
            f"bootloader_easylogger_{entry}_source_leaf",
            f"Compiled MIT EasyLogger boot-port entry ({entry})",
        )
    if name not in descriptions:
        raise ValueError(f"no reviewed manifest identity for new region {name}")
    manifest_name, function = descriptions[name]
    return {
        "address_status": contract_region["address_status"],
        "file_offset": int(contract_region["file_offset"]),
        "function": function,
        "name": manifest_name,
        "output": (
            f"apollo510b/{manifest_name.replace('_', '-')}-"
            f"0x{address:08x}.bin"
        ),
        "size": int(contract_region["size"]),
        "target": "apollo510b_internal_mram",
        "target_address": address,
    }


def sync_manifest() -> None:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    overlay_config = json.loads(OVERLAY_CONFIG.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    override = manifest["component_overrides"]["apollo_bootloader"]
    old_regions = {
        ownership_key(region): region for region in override["regions"]
    }
    regions = []
    for contract_region in contract["regions"]:
        old = old_regions.get(ownership_key(contract_region))
        regions.append(dict(old) if old is not None else new_region(contract_region))

    provider = override["provider"]
    provider.update(contract["provider"])
    linux_expected = overlay_config["toolchain_profiles"]["linux-clang"][
        "expected"
    ]
    provider.setdefault("profiles", {})["linux-clang"] = {
        "size": linux_expected["component_size"],
        "sha256": linux_expected["component_sha256"],
    }
    for profile_name in (
        "apple-font-manager-record",
        "apple-product-rtos-record",
    ):
        if profile_name in provider.get("profiles", {}):
            provider["profiles"][profile_name] = {
                "size": provider["size"],
                "sha256": provider["sha256"],
            }
    suffixes = (
        "recovered S200 redirect_init two-mutex initialization entry",
        "recovered Arm EABI byte-fill primitive",
        "recovered Arm EABI forward-copy primitive",
        "recovered bounded byte-comparison primitive",
        "recovered reflected CRC-32 update primitive",
        "recovered reject-set string-span primitive",
        "recovered accept-set string-span primitive",
        "recovered SRAM-word setter at 0x200270CC",
        "recovered unsigned 64-bit divide-by-ten helper",
        "recovered unsigned decimal digit-count helper",
        "recovered signed-magnitude decimal digit-count helper",
        "recovered hexadecimal digit-count helper",
        "recovered wrapping decimal parser",
        "recovered unsigned 64-bit decimal output helper",
        "recovered unsigned 64-bit hexadecimal output helper",
        "recovered nullable string-length helper",
        "recovered null-output-aware repeated-character helper",
        "recovered fixed-point float formatter",
        "recovered bootloader logging formatter core",
        "recovered bootloader variadic logging dispatch wrapper",
        "recovered substring-search primitive",
        "recovered critical-context predicate",
        "recovered runtime-state gate acquisition wrapper",
        "recovered runtime-state and SRAM-gate mapper",
        "recovered runtime-state gate release wrapper",
        "recovered critical-context value-dispatch wrapper",
        "recovered address-identified runtime dispatcher at 0x004160FE",
        "recovered address-identified retained-value wrapper at 0x004161C6",
        "recovered address-identified validated runtime call wrapper at 0x004161CE",
        "recovered address-identified guarded runtime action wrapper at 0x00416200",
        "recovered address-identified two-phase runtime transfer wrapper at 0x0041623A",
        "recovered address-identified masked runtime wait wrapper at 0x004162C4",
        "recovered address-identified optional runtime notification wrapper at 0x00416378",
        "recovered address-identified registered runtime callback adapter at 0x0041639A",
        "recovered address-identified registered runtime object constructor at 0x004163B2",
        "recovered TLSF v3.1 block-header primitive cluster through 0x00416AAA",
        "recovered TLSF v3.1 physical-block and alignment helper cluster through 0x00416BCE",
        "recovered TLSF v3.1 request-size and class-mapping helper cluster through 0x00416C4E",
        "recovered TLSF v3.1 free-list selection and mutation helper cluster through 0x00416E04",
        "recovered TLSF v3.1 allocation, split, coalescing, lookup, and preparation helper cluster through 0x0041711C",
        "recovered TLSF v3.1 control, pool, allocation, and release entry cluster through 0x004172DA",
        "recovered EasyLogger initialization, start, output/color/format/filter control, lock/unlock, tag-level reset, and tag-level query entries through 0x004176CE",
        "recovered EasyLogger interrupt-gated filtered formatting and output entry through 0x00417AD0",
        "recovered EasyLogger mutex, output, time, process-name, and thread-name boot-port entries through 0x0041A700",
        "recovered EasyLogger channel-one driver and four-channel synchronous transfer transport through 0x0041F9B6",
        "recovered boot delay wrappers and capped initializer-table ordering and dispatch services through 0x0041FA40",
        "recovered guarded teardown, reset, hard-float derivation, configuration submission, and channel-four/five platform setup entry through 0x0041FA98",
        "recovered guarded two-stage teardown and pin-state reconciliation entry through 0x0041FAD0",
        "recovered two-bank pin-group configuration dispatcher through 0x0041FCF6",
        "recovered TLSF pool initialization, allocator-handle publication, and diagnostic entry through 0x0041FDA8",
    )
    parts = list(dict.fromkeys(
        part.strip() for part in override["function"].split(";") if part.strip()
    ))
    for suffix in suffixes:
        if suffix not in parts:
            parts.append(suffix)
    override["function"] = "; ".join(parts)
    override["regions"] = regions
    write_json(MANIFEST, manifest)


def verify() -> None:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    override = manifest["component_overrides"]["apollo_bootloader"]
    provider = override["provider"]
    for key in ("kind", "path", "size", "sha256"):
        if provider[key] != contract["provider"][key]:
            raise ValueError(f"bootloader provider {key} is stale")
    if [ownership_key(item) for item in override["regions"]] != [
        ownership_key(item) for item in contract["regions"]
    ]:
        raise ValueError("bootloader manifest ownership regions are stale")
    print(
        "Verified bootloader runtime manifest: "
        f"{provider['size']} bytes/{provider['sha256']}"
    )
    print("  hardware operations: none")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("sync-manifest", "verify"))
    args = parser.parse_args()
    if args.action == "sync-manifest":
        sync_manifest()
    verify()


if __name__ == "__main__":
    main()
