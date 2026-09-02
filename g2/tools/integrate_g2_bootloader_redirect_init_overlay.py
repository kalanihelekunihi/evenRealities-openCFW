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
BUILD_REPORT = (
    ROOT / "components" / "bootloader" / "core_overlay" / "build"
    / "build-report.json"
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
            "bootloader_aeabi_memcpy_general_entry_source_replacement",
            "Generated redirect and NOP fill replacing the general Arm EABI "
            "forward-copy entry prelude while preserving its live ingress",
        ),
        "replace_bootloader_aeabi_memcpy_aligned_entry_source_redirect": (
            "bootloader_aeabi_memcpy_aligned_entry_source_replacement",
            "Generated redirect and NOP fill replacing the aligned Arm EABI "
            "forward-copy entry body while preserving its independent live ingress",
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
            "Generated entry redirect and leading NOP fill replacing the "
            "bootloader logging formatter core before the CLKGEN source cave",
        ),
        "open_cfw_bootloader_clkgen_config_426ccc_source_cave": (
            "bootloader_clkgen_config_426ccc_source_cave",
            "Compiled MIT CLKGEN control, mode, clock-select, and divider "
            "configuration service in authenticated generated-NOP space",
        ),
        "open_cfw_bootloader_clkgen_disable_426d1e_source_cave": (
            "bootloader_clkgen_disable_426d1e_source_cave",
            "Compiled MIT CLKGEN bit-preserving disable service in authenticated generated-NOP space",
        ),
        "open_cfw_bootloader_float_gcd_426d48_source_cave": (
            "bootloader_float_gcd_426d48_source_cave",
            "Compiled MIT bounded floating Euclidean common-divisor helper in authenticated generated-NOP space",
        ),
        "replace_bootloader_format_core_source_redirect_between_caves_3": (
            "bootloader_format_core_generated_fill_between_float_gcd_ratio_caves",
            "Generated NOP fill between the hard-float common-divisor and ratio source caves",
        ),
        "open_cfw_bootloader_float_ratio_426db4_source_cave": (
            "bootloader_float_ratio_426db4_source_cave",
            "Compiled MIT bounded floating ratio validation and encoding helper in authenticated generated-NOP space",
        ),
        "replace_bootloader_format_core_source_redirect_between_caves_4": (
            "bootloader_format_core_generated_fill_between_float_ratio_multiplier_caves",
            "Generated NOP fill between the hard-float ratio and multiplier source caves",
        ),
        "open_cfw_bootloader_float_multiplier_426eac_source_cave": (
            "bootloader_float_multiplier_426eac_source_cave",
            "Compiled MIT bounded floating multiplier validation and encoding helper in authenticated generated-NOP space",
        ),
        "open_cfw_bootloader_float_encoding_select_426f6c_source_cave": (
            "bootloader_float_encoding_select_426f6c_source_cave",
            "Compiled MIT floating encoding selection and result publication service in authenticated generated-NOP space",
        ),
        "replace_bootloader_format_core_source_redirect_after_caves": (
            "bootloader_format_core_generated_fill_after_clkgen_float_gcd_ratio_multiplier_select_caves",
            "Generated NOP fill after the CLKGEN configuration, disable, floating common-divisor, ratio, multiplier, and encoding-selector source caves "
            "within the bootloader formatter-core replacement span",
        ),
        "open_cfw_bootloader_syspll_min_fvco_427040_source_cave": (
            "bootloader_syspll_min_fvco_427040_source_cave",
            "Compiled BSD-3-Clause System PLL minimum-VCO configuration service in its reclaimed stock body",
        ),
        "replace_bootloader_syspll_min_fvco_427040_source_redirect_after_caves": (
            "bootloader_syspll_min_fvco_427040_generated_fill_after_cave",
            "Generated unreachable NOP fill after the bounded System PLL source cave",
        ),
        "open_cfw_bootloader_syspll_postdiv_427160_source_cave": (
            "bootloader_syspll_postdiv_427160_source_cave",
            "Compiled BSD-3-Clause System PLL postdivider configuration service in its reclaimed stock body",
        ),
        "replace_bootloader_syspll_postdiv_427160_source_redirect_after_caves": (
            "bootloader_syspll_postdiv_427160_generated_fill_after_cave",
            "Generated unreachable NOP fill after the bounded System PLL postdivider source cave",
        ),
        "open_cfw_bootloader_row6_create_4272ac_source_cave": (
            "bootloader_syspll_initialize_4272ac_source_cave",
            "Compiled BSD-3-Clause System PLL initialization service in its reclaimed stock body",
        ),
        "replace_bootloader_syspll_initialize_4272ac_source_redirect_after_caves": (
            "bootloader_syspll_initialize_4272ac_generated_fill_after_cave",
            "Generated unreachable NOP fill after the bounded System PLL initialization source cave",
        ),
        "open_cfw_bootloader_row6_start_427360_source_cave": (
            "bootloader_syspll_enable_427360_source_cave",
            "Compiled BSD-3-Clause System PLL enable service in its reclaimed stock body",
        ),
        "replace_bootloader_syspll_enable_427360_source_redirect_after_caves": (
            "bootloader_syspll_enable_427360_generated_fill_after_cave",
            "Generated unreachable NOP fill after the bounded System PLL enable source cave",
        ),
        "open_cfw_bootloader_row6_configure_42740c_source_cave": (
            "bootloader_syspll_configure_42740c_source_cave",
            "Compiled BSD-3-Clause System PLL configuration service in its reclaimed stock body",
        ),
        "replace_bootloader_syspll_configure_42740c_source_redirect_after_caves": (
            "bootloader_syspll_configure_42740c_generated_fill_after_cave",
            "Generated unreachable NOP fill after the bounded System PLL configuration source cave",
        ),
        "open_cfw_bootloader_row6_lock_wait_427522_source_cave": (
            "bootloader_syspll_lock_wait_427522_source_cave",
            "Compiled BSD-3-Clause System PLL lock-wait service in its reclaimed stock body",
        ),
        "replace_bootloader_syspll_lock_wait_427522_source_redirect_after_caves": (
            "bootloader_syspll_lock_wait_427522_generated_fill_after_cave",
            "Generated unreachable NOP fill after the bounded System PLL lock-wait source cave",
        ),
        "open_cfw_bootloader_queue_init_4275ea_source_cave": (
            "bootloader_queue_init_4275ea_source_cave",
            "Compiled BSD-3-Clause AmbiqSuite queue initializer in its reclaimed stock body",
        ),
        "open_cfw_bootloader_queue_item_add_427602_source_cave": (
            "bootloader_queue_item_add_427602_source_cave",
            "Compiled BSD-3-Clause AmbiqSuite queue item-add service in its reclaimed stock body",
        ),
        "open_cfw_bootloader_queue_item_get_427660_source_cave": (
            "bootloader_queue_item_get_427660_source_cave",
            "Compiled BSD-3-Clause AmbiqSuite queue item-get service in its reclaimed stock body",
        ),
        "open_cfw_bootloader_memmove_4276bc_source_cave": (
            "bootloader_memmove_4276bc_source_cave",
            "Compiled clean-room MIT overlap-safe byte move in its reclaimed stock body",
        ),
        "replace_bootloader_memmove_4276bc_source_redirect_after_caves": (
            "bootloader_memmove_4276bc_generated_fill_after_cave",
            "Generated unreachable NOP fill after the bounded overlap-safe byte-move source cave",
        ),
        "open_cfw_bootloader_cmdq_update_indices_427754_source_cave": (
            "bootloader_cmdq_update_indices_427754_source_cave",
            "Compiled BSD-3-Clause AmbiqSuite command-queue index updater in its reclaimed stock body",
        ),
        "replace_bootloader_cmdq_update_indices_427754_source_redirect_after_caves": (
            "bootloader_cmdq_update_indices_427754_generated_fill_after_cave",
            "Generated unreachable NOP fill after the bounded command-queue index-update source cave",
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
        "opaque_before_replace_bootloader_nvic_enable_irq_41fdc0": (
            "bootloader_allocator_literal_pool_0x0041fda8",
            "Authenticated allocator and diagnostic pointer literals retained before the IRQ-service cluster",
        ),
        "replace_bootloader_nvic_enable_irq_41fdc0_source_redirect": (
            "bootloader_nvic_enable_irq_41fdc0_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete NVIC interrupt-enable entry",
        ),
        "replace_bootloader_nvic_set_priority_41fdde_source_redirect": (
            "bootloader_nvic_set_priority_41fdde_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete NVIC/system-handler priority entry",
        ),
        "replace_bootloader_mspi_isr_41fe06_source_redirect": (
            "bootloader_mspi_isr_41fe06_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete MSPI status-clear-service interrupt wrapper",
        ),
        "replace_bootloader_mspi_enable_41fe28_source_redirect": (
            "bootloader_mspi_enable_41fe28_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete idempotent MSPI enable entry",
        ),
        "replace_bootloader_mspi_disable_41fe48_source_redirect": (
            "bootloader_mspi_disable_41fe48_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete MSPI disable entry",
        ),
        "replace_bootloader_event_flags_init_41fe62_source_redirect": (
            "bootloader_event_flags_init_41fe62_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete guarded event-flags service initializer",
        ),
        "replace_bootloader_event_flags_acquire_41fe9c_source_redirect": (
            "bootloader_event_flags_acquire_41fe9c_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete guarded event-flags acquire entry",
        ),
        "replace_bootloader_event_flags_release_41fed4_source_redirect": (
            "bootloader_event_flags_release_41fed4_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete guarded event-flags release entry",
        ),
        "replace_bootloader_mspi_guard_enter_41ff08_source_redirect": (
            "bootloader_mspi_guard_enter_41ff08_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete paired event-lock and conditional MSPI-disable guard entry",
        ),
        "replace_bootloader_mspi_guard_exit_41ff1e_source_redirect": (
            "bootloader_mspi_guard_exit_41ff1e_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete conditional MSPI-enable and paired event-unlock guard exit",
        ),
        "replace_bootloader_mspi_xip_config_41ff34_source_redirect": (
            "bootloader_mspi_xip_config_41ff34_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete MSPI XIP configuration-byte updater",
        ),
        "replace_bootloader_longest_ones_run_41ff60_source_redirect": (
            "bootloader_longest_ones_run_41ff60_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete longest consecutive-one run-length helper",
        ),
        "replace_bootloader_longest_ones_center_41ff74_source_redirect": (
            "bootloader_longest_ones_center_41ff74_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete longest consecutive-one run center-selection helper",
        ),
        "replace_bootloader_mspi_timing_scan_420002_source_redirect": (
            "bootloader_mspi_timing_scan_420002_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete exhaustive MSPI timing scan",
        ),
        "replace_bootloader_mspi_timing_auto_4201ba_source_redirect": (
            "bootloader_mspi_timing_auto_4201ba_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete automatic MSPI timing-selection wrapper",
        ),
        "replace_bootloader_mspi_low_level_init_420254_source_redirect": (
            "bootloader_mspi_low_level_init_420254_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete MX25U25643G low-level MSPI initializer",
        ),
        "replace_bootloader_mspi_driver_init_420476_source_redirect": (
            "bootloader_mspi_driver_init_420476_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete MX25U25643G public initialization wrapper",
        ),
        "replace_bootloader_mspi_soft_reset_42052a_source_redirect": (
            "bootloader_mspi_soft_reset_42052a_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete MX25U25643G soft-reset sequence",
        ),
        "replace_bootloader_mspi_read_id_42059e_source_redirect": (
            "bootloader_mspi_read_id_42059e_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete MX25U25643G JEDEC-ID reader",
        ),
        "replace_bootloader_mspi_read_transfer_4205f4_source_redirect": (
            "bootloader_mspi_read_transfer_4205f4_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete MX25U25643G read-transfer wrapper",
        ),
        "replace_bootloader_mspi_write_transfer_42069e_source_redirect": (
            "bootloader_mspi_write_transfer_42069e_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete MX25U25643G write-transfer wrapper",
        ),
        "replace_bootloader_mspi_busy_status_42074e_source_redirect": (
            "bootloader_mspi_busy_status_42074e_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete MX25U25643G status-register reader",
        ),
        "replace_bootloader_mspi_wait_ready_4207a2_source_redirect": (
            "bootloader_mspi_wait_ready_4207a2_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete MX25U25643G two-phase ready poll",
        ),
        "replace_bootloader_mspi_wait_ready_default_4207f4_source_redirect": (
            "bootloader_mspi_wait_ready_default_4207f4_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete MX25U25643G fixed ready-poll wrapper",
        ),
        "replace_bootloader_mspi_4byte_mode_420800_source_redirect": (
            "bootloader_mspi_4byte_mode_420800_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete MX25U25643G address-mode reader",
        ),
        "replace_bootloader_mspi_enter_4byte_mode_420890_source_redirect": (
            "bootloader_mspi_enter_4byte_mode_420890_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete MX25U25643G four-byte-mode entry sequence",
        ),
        "opaque_before_replace_bootloader_mspi_enter_4byte_mode_420890": (
            "bootloader_mspi_enter_4byte_mode_literal_gap",
            "Authenticated non-executable literal and alignment gap preceding the MX25U25643G four-byte-mode entry",
        ),
        "opaque_before_replace_bootloader_mspi_write_enable_420984": (
            "bootloader_mspi_write_enable_literal_gap",
            "Authenticated non-executable literal and alignment gap preceding the MX25U25643G write-enable wrapper",
        ),
        "replace_bootloader_mspi_write_enable_420984_source_redirect": (
            "bootloader_mspi_write_enable_420984_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete MX25U25643G write-enable wrapper",
        ),
        "opaque_before_replace_bootloader_mspi_write_disable_4209c4": (
            "bootloader_mspi_write_disable_literal_gap",
            "Authenticated non-executable literal and alignment gap preceding the MX25U25643G write-disable wrapper",
        ),
        "replace_bootloader_mspi_write_disable_4209c4_source_redirect": (
            "bootloader_mspi_write_disable_4209c4_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete MX25U25643G write-disable wrapper",
        ),
        "opaque_before_replace_bootloader_mspi_sector_erase_420a08": (
            "bootloader_mspi_sector_erase_literal_gap",
            "Authenticated non-executable literal and alignment gap preceding the MX25U25643G sector-erase service",
        ),
        "replace_bootloader_mspi_sector_erase_420a08_source_redirect": (
            "bootloader_mspi_sector_erase_420a08_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete MX25U25643G sector-erase service",
        ),
        "opaque_before_replace_bootloader_mspi_program_420b0c": (
            "bootloader_mspi_program_literal_gap",
            "Authenticated non-executable literal and alignment gap preceding the MX25U25643G page-program service",
        ),
        "replace_bootloader_mspi_program_420b0c_source_redirect": (
            "bootloader_mspi_program_420b0c_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete MX25U25643G page-program service",
        ),
        "opaque_before_replace_bootloader_mspi_quad_enable_420c5c": (
            "bootloader_mspi_quad_enable_literal_gap",
            "Authenticated non-executable literal and alignment gap preceding the MX25U25643G QE service",
        ),
        "replace_bootloader_mspi_quad_enable_420c5c_source_redirect": (
            "bootloader_mspi_quad_enable_420c5c_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete MX25U25643G status-register-2 QE service",
        ),
        "opaque_before_replace_bootloader_mspi_device_reconfigure_420e08": (
            "bootloader_mspi_device_reconfigure_literal_gap",
            "Authenticated non-executable literal pool preceding the MSPI device reconfiguration service",
        ),
        "replace_bootloader_mspi_device_reconfigure_420e08_source_redirect": (
            "bootloader_mspi_device_reconfigure_420e08_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete MSPI device reconfiguration service",
        ),
        "replace_bootloader_mspi_set_quad_mode_420e8c_source_redirect": (
            "bootloader_mspi_set_quad_mode_420e8c_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete MX25U25643G quad-mode selection service",
        ),
        "opaque_before_replace_bootloader_mspi_set_serial_mode_420f10": (
            "bootloader_mspi_set_serial_mode_literal_gap",
            "Authenticated non-executable literal pool preceding the MX25U25643G serial-mode service",
        ),
        "replace_bootloader_mspi_set_serial_mode_420f10_source_redirect": (
            "bootloader_mspi_set_serial_mode_420f10_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete MX25U25643G serial-mode selection service",
        ),
        "opaque_before_replace_bootloader_mspi_read_420f70": (
            "bootloader_mspi_read_literal_gap",
            "Authenticated non-executable literal and alignment gap preceding the MX25U25643G read service",
        ),
        "replace_bootloader_mspi_read_420f70_source_redirect": (
            "bootloader_mspi_read_420f70_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete MX25U25643G guarded read service",
        ),
        "opaque_before_replace_bootloader_check_and_create_directories_4210c8": (
            "bootloader_fs_directories_literal_pool",
            "Authenticated non-executable literal and alignment pool preceding the LittleFS directory bootstrap service",
        ),
        "replace_bootloader_check_and_create_directories_4210c8_source_redirect": (
            "bootloader_check_and_create_directories_4210c8_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete LittleFS directory bootstrap service",
        ),
        "replace_bootloader_littlefs_format_4211b0_source_redirect": (
            "bootloader_littlefs_format_4211b0_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete LittleFS format and mount orchestration service",
        ),
        "replace_bootloader_littlefs_init_421210_source_redirect": (
            "bootloader_littlefs_init_421210_source_replacement",
            "Generated entry redirect replacing the complete LittleFS mount, recovery, readiness, and boot-counter initialization service",
        ),
        "replace_bootloader_littlefs_init_421210_source_redirect_after_caves": (
            "bootloader_littlefs_init_421210_generated_tail",
            "Generated NOP tail after the authenticated reclaimed-body LittleFS program, erase, and sync leaves",
        ),
        "open_cfw_bootloader_littlefs_program_421310_source_cave": (
            "bootloader_littlefs_program_421310_source_cave",
            "Compiled clean-room G2 LittleFS block-program callback in authenticated reclaimed initializer body space",
        ),
        "open_cfw_bootloader_littlefs_erase_421348_source_cave": (
            "bootloader_littlefs_erase_421348_source_cave",
            "Compiled clean-room G2 LittleFS block-erase callback in authenticated reclaimed initializer body space",
        ),
        "open_cfw_bootloader_littlefs_sync_4213d4_source_cave": (
            "bootloader_littlefs_sync_4213d4_source_cave",
            "Compiled clean-room G2 LittleFS constant-success sync callback in authenticated reclaimed initializer body space",
        ),
        "replace_bootloader_littlefs_read_4212d8_source_redirect": (
            "bootloader_littlefs_read_4212d8_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete LittleFS block-read callback",
        ),
        "replace_bootloader_littlefs_program_421310_source_redirect": (
            "bootloader_littlefs_program_421310_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete LittleFS block-program callback",
        ),
        "replace_bootloader_littlefs_erase_421348_source_redirect": (
            "bootloader_littlefs_erase_421348_source_replacement",
            "Generated entry redirect and NOP fill replacing the complete LittleFS block-erase callback",
        ),
        "opaque_before_replace_bootloader_littlefs_sync_4213d4": (
            "bootloader_littlefs_erase_literal_gap",
            "Authenticated non-executable literal and alignment gap after the LittleFS block-erase callback",
        ),
        "replace_bootloader_littlefs_sync_4213d4_source_redirect": (
            "bootloader_littlefs_sync_4213d4_source_replacement",
            "Generated entry redirect replacing the complete constant-success LittleFS sync callback",
        ),
        "open_cfw_bootloader_address_identity_4213d8_source_in_place": (
            "bootloader_address_identity_4213d8_source_in_place",
            "Compiled clean-room G2 identity address-index helper at its authenticated stock address",
        ),
        "open_cfw_bootloader_address_map_4213da_source_in_place": (
            "bootloader_address_map_4213da_source_in_place",
            "Compiled clean-room G2 thresholded address-index helper at its authenticated stock address",
        ),
        "replace_bootloader_memory_select_copy_4213e6_source_redirect": (
            "bootloader_memory_select_copy_4213e6_source_replacement",
            "Generated entry redirect replacing the mapped-memory selector and copy service",
        ),
        "open_cfw_bootloader_memory_select_copy_4213e6_source_cave": (
            "bootloader_memory_select_copy_4213e6_source_cave",
            "Compiled clean-room G2 mapped-memory selector and copy service in authenticated reclaimed entry space",
        ),
        "open_cfw_bootloader_memory_select_odd_421548_source_cave": (
            "bootloader_memory_select_odd_421548_source_cave",
            "Compiled clean-room G2 odd-selector mapped-memory wrapper in authenticated reclaimed entry space",
        ),
        "replace_bootloader_memory_select_copy_4213e6_source_redirect_after_caves": (
            "bootloader_memory_select_copy_4213e6_generated_nop_tail",
            "Generated NOP tail after the mapped-memory selector and odd-selector wrapper caves",
        ),
        "replace_bootloader_memory_select_odd_421548_source_redirect": (
            "bootloader_memory_select_odd_421548_source_replacement",
            "Generated entry redirect and NOP fill replacing the odd-selector mapped-memory wrapper",
        ),
        "opaque_before_open_cfw_bootloader_popcount_421584_source_in_place": (
            "bootloader_memory_select_literal_pool",
            "Authenticated non-executable mapped-memory control, security, and window literal pool",
        ),
        "open_cfw_bootloader_popcount_421584_source_in_place": (
            "bootloader_popcount_421584_source_in_place",
            "Compiled clean-room G2 32-bit population-count helper at its authenticated stock address",
        ),
        "open_cfw_bootloader_bitmap_any_4215ae_source_in_place": (
            "bootloader_bitmap_any_4215ae_source_in_place",
            "Compiled clean-room G2 two-word bitmap nonempty helper at its authenticated stock address",
        ),
        "open_cfw_bootloader_bitmap_test_4215dc_source_in_place": (
            "bootloader_bitmap_test_4215dc_source_in_place",
            "Compiled clean-room G2 two-word bitmap membership helper at its authenticated stock address",
        ),
        "open_cfw_bootloader_bitmap_count_4215fe_source_in_place": (
            "bootloader_bitmap_count_4215fe_source_in_place",
            "Compiled clean-room G2 two-word bitmap population-count helper at its authenticated stock address",
        ),
        "open_cfw_bootloader_bitmap_update_421632_source_in_place": (
            "bootloader_bitmap_update_421632_source_in_place",
            "Compiled clean-room G2 validated two-word bitmap update helper at its authenticated stock address",
        ),
        "open_cfw_bootloader_poll_delay_4216b2_source_in_place": (
            "bootloader_poll_delay_4216b2_source_in_place",
            "Compiled clean-room G2 bounded poll-delay helper at its authenticated stock address",
        ),
        "open_cfw_bootloader_mode_service_4216d4_source_in_place": (
            "bootloader_mode_service_4216d4_source_in_place",
            "Compiled clean-room G2 mode/configuration transaction service at its authenticated stock address",
        ),
        "open_cfw_bootloader_dual_mode_service_4217d2_source_in_place": (
            "bootloader_dual_mode_service_4217d2_source_in_place",
            "Compiled clean-room G2 dual-controller mode transaction service at its authenticated stock address",
        ),
        "open_cfw_bootloader_bitmap_client_service_421978_source_in_place": (
            "bootloader_bitmap_client_service_421978_source_in_place",
            "Compiled clean-room G2 bitmap-client configuration service at its authenticated stock address",
        ),
        "open_cfw_bootloader_bitmap_row0_set_421a30_source_in_place": (
            "bootloader_bitmap_row0_set_421a30_source_in_place",
            "Compiled clean-room G2 bitmap row-zero set helper at its authenticated stock address",
        ),
        "open_cfw_bootloader_bitmap_row0_clear_421a62_source_in_place": (
            "bootloader_bitmap_row0_clear_421a62_source_in_place",
            "Compiled clean-room G2 bitmap row-zero clear helper at its authenticated stock address",
        ),
        "open_cfw_bootloader_bitmap_row1_set_421a94_source_in_place": (
            "bootloader_bitmap_row1_set_421a94_source_in_place",
            "Compiled clean-room G2 guarded bitmap row-one set helper at its authenticated stock address",
        ),
        "open_cfw_bootloader_bitmap_row1_clear_421ad6_source_in_place": (
            "bootloader_bitmap_row1_clear_421ad6_source_in_place",
            "Compiled clean-room G2 bitmap row-one clear helper at its authenticated stock address",
        ),
        "open_cfw_bootloader_mode1_enable_421b08_source_in_place": (
            "bootloader_mode1_enable_421b08_source_in_place",
            "Compiled clean-room G2 mode-one enable helper at its authenticated stock address",
        ),
        "open_cfw_bootloader_mode1_disable_421b5c_source_in_place": (
            "bootloader_mode1_disable_421b5c_source_in_place",
            "Compiled clean-room G2 mode-one last-client disable helper at its authenticated stock address",
        ),
        "open_cfw_bootloader_mode1_poll_cleanup_421ba4_source_in_place": (
            "bootloader_mode1_poll_cleanup_421ba4_source_in_place",
            "Compiled clean-room G2 mode-one poll and state cleanup helper at its authenticated stock address",
        ),
        "open_cfw_bootloader_mode0_enable_421bd2_source_in_place": (
            "bootloader_mode0_enable_421bd2_source_in_place",
            "Compiled clean-room G2 mode-zero enable transaction at its authenticated stock address",
        ),
        "open_cfw_bootloader_mode0_disable_421cce_source_in_place": (
            "bootloader_mode0_disable_421cce_source_in_place",
            "Compiled clean-room G2 mode-zero last-client disable helper at its authenticated stock address",
        ),
        "open_cfw_bootloader_mode0_poll_cleanup_421d28_source_in_place": (
            "bootloader_mode0_poll_cleanup_421d28_source_in_place",
            "Compiled clean-room G2 mode-zero poll and state cleanup helper at its authenticated stock address",
        ),
        "open_cfw_bootloader_row4_enable_421d5e_source_in_place": (
            "bootloader_row4_enable_421d5e_source_in_place",
            "Compiled clean-room G2 row-four enable transaction at its authenticated stock address",
        ),
        "open_cfw_bootloader_row4_disable_421e4a_source_in_place": (
            "bootloader_row4_disable_421e4a_source_in_place",
            "Compiled clean-room G2 row-four last-client disable helper at its authenticated stock address",
        ),
        "open_cfw_bootloader_row4_poll_cleanup_421e8c_source_in_place": (
            "bootloader_row4_poll_cleanup_421e8c_source_in_place",
            "Compiled clean-room G2 row-four poll and state cleanup helper at its authenticated stock address",
        ),
        "open_cfw_bootloader_row5_enable_421eba_source_in_place": (
            "bootloader_row5_enable_421eba_source_in_place",
            "Compiled clean-room G2 row-five enable transaction at its authenticated stock address",
        ),
        "open_cfw_bootloader_row5_disable_422040_source_in_place": (
            "bootloader_row5_disable_422040_source_in_place",
            "Compiled clean-room G2 row-five final-client disable helper at its authenticated stock address",
        ),
        "open_cfw_bootloader_row6_enable_4220b2_source_in_place": (
            "bootloader_row6_enable_4220b2_source_in_place",
            "Compiled clean-room G2 row-six enable transaction at its authenticated stock address",
        ),
        "opaque_before_open_cfw_bootloader_row6_disable_422220_source_in_place": (
            "bootloader_row6_enable_literal_seam",
            "Authenticated row-six enable literal seam retained between exact source bodies",
        ),
        "open_cfw_bootloader_row6_disable_422220_source_in_place": (
            "bootloader_row6_disable_422220_source_in_place",
            "Compiled clean-room G2 row-six final-client disable helper at its authenticated stock address",
        ),
        "opaque_before_open_cfw_bootloader_mode_dispatch_4222a0_source_in_place": (
            "bootloader_row6_disable_literal_seam",
            "Authenticated row-six disable literal seam retained between exact source bodies",
        ),
        "open_cfw_bootloader_mode_dispatch_4222a0_source_in_place": (
            "bootloader_mode_dispatch_4222a0_source_in_place",
            "Compiled clean-room G2 mode-family dispatcher at its authenticated stock address",
        ),
        "opaque_before_open_cfw_bootloader_mode_enable_route_4222f0_source_in_place": (
            "bootloader_mode_route_literal_seam",
            "Authenticated padding and literal seam retained before exact mode routing bodies",
        ),
        "open_cfw_bootloader_mode_enable_route_4222f0_source_in_place": (
            "bootloader_mode_enable_route_4222f0_source_in_place",
            "Compiled clean-room G2 seven-kind enable router at its authenticated stock address",
        ),
        "open_cfw_bootloader_mode_disable_route_422364_source_in_place": (
            "bootloader_mode_disable_route_422364_source_in_place",
            "Compiled clean-room G2 seven-kind disable router at its authenticated stock address",
        ),
        "open_cfw_bootloader_mode_clear_all_4223d8_source_in_place": (
            "bootloader_mode_clear_all_4223d8_source_in_place",
            "Compiled clean-room G2 seven-row client cleanup helper at its authenticated stock address",
        ),
        "open_cfw_bootloader_mode_configuration_copy_422416_source_in_place": (
            "bootloader_mode_configuration_copy_422416_source_in_place",
            "Compiled clean-room G2 fixed-size configuration copy helper at its authenticated stock address",
        ),
        "opaque_before_open_cfw_bootloader_debug_disable_422468_source_in_place": (
            "bootloader_debug_services_literal_pool",
            "Authenticated debug-service literal pool retained before exact source bodies",
        ),
        "open_cfw_bootloader_debug_disable_422468_source_in_place": (
            "bootloader_debug_disable_422468_source_in_place",
            "Compiled AmbiqSuite-compatible G2 debug shutdown service at its authenticated stock address",
        ),
        "open_cfw_bootloader_debug_power_4224b2_source_in_place": (
            "bootloader_debug_power_4224b2_source_in_place",
            "Compiled AmbiqSuite-compatible G2 debug power reference service at its authenticated stock address",
        ),
        "open_cfw_bootloader_debug_trace_disable_42252e_source_in_place": (
            "bootloader_debug_trace_disable_42252e_source_in_place",
            "Compiled AmbiqSuite-compatible G2 trace disable service at its authenticated stock address",
        ),
        "opaque_before_open_cfw_bootloader_constraint_dispatch_422590_source_in_place": (
            "bootloader_debug_trace_literal_pool",
            "Authenticated debug trace literal pool retained before the constraint dispatcher",
        ),
        "open_cfw_bootloader_constraint_dispatch_422590_source_in_place": (
            "bootloader_constraint_dispatch_422590_source_in_place",
            "Compiled clean-room G2 IAR-compatible constraint dispatcher at its authenticated stock address",
        ),
        "opaque_before_open_cfw_bootloader_memchr_4225d0_source_in_place": (
            "bootloader_constraint_pool_and_message",
            "Authenticated constraint-handler pointer and diagnostic string retained before memchr",
        ),
        "open_cfw_bootloader_memchr_4225d0_source_in_place": (
            "bootloader_memchr_4225d0_source_in_place",
            "Compiled clean-room G2 optimized memchr at its authenticated stock address",
        ),
        "open_cfw_bootloader_double_frexp_422628_source_in_place": (
            "bootloader_double_frexp_422628_source_in_place",
            "Compiled clean-room G2 IAR-compatible double frexp wrapper at its authenticated stock address",
        ),
        "open_cfw_bootloader_double_frexp_core_422634_source_in_place": (
            "bootloader_double_frexp_core_422634_source_in_place",
            "Compiled clean-room G2 IAR-compatible double normalization helper at its authenticated stock address",
        ),
        "open_cfw_bootloader_double_compare_422698_source_in_place": (
            "bootloader_double_compare_422698_source_in_place",
            "Compiled clean-room G2 IAR-compatible double comparator at its authenticated stock address",
        ),
        "open_cfw_bootloader_double_compare_reverse_4226cc_source_in_place": (
            "bootloader_double_compare_reverse_4226cc_source_in_place",
            "Compiled clean-room G2 IAR-compatible reverse double comparator at its authenticated stock address",
        ),
        "open_cfw_bootloader_double_ldexp_422700_source_in_place": (
            "bootloader_double_ldexp_422700_source_in_place",
            "Compiled clean-room G2 IAR-compatible double ldexp wrapper at its authenticated stock address",
        ),
        "opaque_before_open_cfw_bootloader_double_ldexp_core_422714_source_in_place": (
            "bootloader_double_ldexp_alignment",
            "Authenticated two-byte alignment between the double ldexp wrapper and core",
        ),
        "open_cfw_bootloader_double_ldexp_core_422714_source_in_place": (
            "bootloader_double_ldexp_core_422714_source_in_place",
            "Compiled clean-room G2 IAR-compatible double scaling core at its authenticated stock address",
        ),
        "open_cfw_bootloader_double_to_i32_422804_source_in_place": (
            "bootloader_double_to_i32_422804_source_in_place",
            "Compiled G2 VFP double-to-signed conversion leaf at its authenticated stock address",
        ),
        "open_cfw_bootloader_i32_to_double_422812_source_in_place": (
            "bootloader_i32_to_double_422812_source_in_place",
            "Compiled G2 VFP signed-to-double conversion leaf at its authenticated stock address",
        ),
        "open_cfw_bootloader_double_subtract_422820_source_in_place": (
            "bootloader_double_subtract_422820_source_in_place",
            "Compiled G2 VFP double subtraction leaf at its authenticated stock address",
        ),
        "open_cfw_bootloader_double_divide_422832_source_in_place": (
            "bootloader_double_divide_422832_source_in_place",
            "Compiled G2 VFP double division leaf at its authenticated stock address",
        ),
        "open_cfw_bootloader_double_to_u32_422844_source_in_place": (
            "bootloader_double_to_u32_422844_source_in_place",
            "Compiled G2 VFP double-to-unsigned conversion leaf at its authenticated stock address",
        ),
        "open_cfw_bootloader_u32_to_double_422852_source_in_place": (
            "bootloader_u32_to_double_422852_source_in_place",
            "Compiled G2 VFP unsigned-to-double conversion leaf at its authenticated stock address",
        ),
        "open_cfw_bootloader_double_multiply_422860_source_in_place": (
            "bootloader_double_multiply_422860_source_in_place",
            "Compiled G2 VFP double multiplication leaf at its authenticated stock address",
        ),
        "opaque_before_open_cfw_bootloader_thread_pointer_422874_source_in_place": (
            "bootloader_double_runtime_trailing_alignment",
            "Authenticated two-byte alignment before the IAR thread-pointer leaf",
        ),
        "open_cfw_bootloader_thread_pointer_422874_source_in_place": (
            "bootloader_thread_pointer_422874_source_in_place",
            "Compiled clean-room G2 IAR thread-pointer leaf and runtime anchor at their authenticated stock address",
        ),
        "open_cfw_bootloader_u64_divmod_42287c_source_in_place": (
            "bootloader_u64_divmod_42287c_source_in_place",
            "Compiled clean-room G2 IAR unsigned 64-bit divide/modulo runtime at its authenticated stock address",
        ),
        "open_cfw_bootloader_atomic_snapshot3_422aac_source_in_place": (
            "bootloader_atomic_snapshot3_422aac_source_in_place",
            "Compiled clean-room G2 interrupt-atomic three-word snapshot helper at its authenticated stock address",
        ),
        "open_cfw_bootloader_noop_422ac8_source_in_place": (
            "bootloader_noop_422ac8_source_in_place",
            "Compiled clean-room G2 no-operation runtime leaf at its authenticated stock address",
        ),
        "open_cfw_bootloader_retained_query_wrapper_422aca_source_in_place": (
            "bootloader_retained_query_wrapper_422aca_source_in_place",
            "Compiled clean-room G2 retained-query wrapper at its authenticated stock address",
        ),
        "opaque_before_open_cfw_bootloader_hw_instance_init_422ad4_source_in_place": (
            "bootloader_hw_instance_init_leading_alignment",
            "Authenticated two-byte alignment before the four-instance hardware-service initializer",
        ),
        "open_cfw_bootloader_hw_instance_init_422ad4_source_in_place": (
            "bootloader_hw_instance_init_422ad4_source_in_place",
            "Compiled clean-room G2 four-instance hardware-service initializer at its authenticated stock address",
        ),
        "open_cfw_bootloader_hw_instance_service_422ba8_source_in_place": (
            "bootloader_hw_instance_service_422ba8_source_in_place",
            "Compiled clean-room G2 instance register-transfer and lifecycle service at its authenticated stock address",
        ),
        "open_cfw_bootloader_hw_register_clear_422d20_source_in_place": (
            "bootloader_hw_register_clear_422d20_source_in_place",
            "Compiled clean-room G2 per-instance primary register-clear leaf at its authenticated stock address",
        ),
        "open_cfw_bootloader_hw_register_clear_422d4c_source_in_place": (
            "bootloader_hw_register_clear_422d4c_source_in_place",
            "Compiled clean-room G2 per-instance secondary register-clear leaf at its authenticated stock address",
        ),
        "opaque_before_open_cfw_bootloader_hw_status_map_422d7e_source_in_place": (
            "bootloader_hw_status_map_leading_datum",
            "Authenticated four-byte non-executable datum before the per-instance status mapper",
        ),
        "open_cfw_bootloader_hw_status_map_422d7e_source_in_place": (
            "bootloader_hw_status_map_422d7e_source_in_place",
            "Compiled clean-room G2 per-instance status mapper at its authenticated stock address",
        ),
        "open_cfw_bootloader_hw_descriptor_init_422dc6_source_in_place": (
            "bootloader_hw_descriptor_init_422dc6_source_in_place",
            "Compiled clean-room G2 per-instance dual-descriptor initializer at its authenticated stock address",
        ),
        "open_cfw_bootloader_hw_clock_divider_422e28_source_in_place": (
            "bootloader_hw_clock_divider_422e28_source_in_place",
            "Compiled clean-room G2 per-instance clock-divider service at its authenticated stock address",
        ),
        "open_cfw_bootloader_hw_config_latch_422ee2_source_in_place": (
            "bootloader_hw_config_latch_422ee2_source_in_place",
            "Compiled clean-room G2 interrupt-atomic per-instance configuration latch at its authenticated stock address",
        ),
        "open_cfw_bootloader_hw_config_latch_secondary_422f4c_source_in_place": (
            "bootloader_hw_config_latch_secondary_422f4c_source_in_place",
            "Compiled clean-room G2 interrupt-atomic secondary per-instance configuration latch at its authenticated stock address",
        ),
        "open_cfw_bootloader_hw_config_release_secondary_422fa2_source_in_place": (
            "bootloader_hw_config_release_secondary_422fa2_source_in_place",
            "Compiled clean-room G2 interrupt-atomic secondary per-instance configuration release at its authenticated stock address",
        ),
        "open_cfw_bootloader_hw_shutdown_422fde_source_in_place": (
            "bootloader_hw_shutdown_422fde_source_in_place",
            "Compiled clean-room G2 per-instance register-quiesce and hardware-shutdown service at its authenticated stock address",
        ),
        "open_cfw_bootloader_hw_initializer_42308e_source_in_place": (
            "bootloader_hw_initializer_42308e_source_in_place",
            "Compiled clean-room G2 per-instance hardware initializer at its authenticated stock address",
        ),
        "open_cfw_bootloader_hw_fifo_read_4232c8_source_in_place": (
            "bootloader_hw_fifo_read_4232c8_source_in_place",
            "Compiled clean-room G2 per-instance FIFO read service at its authenticated stock address",
        ),
        "open_cfw_bootloader_hw_fifo_write_42330e_source_in_place": (
            "bootloader_hw_fifo_write_42330e_source_in_place",
            "Compiled clean-room G2 per-instance FIFO write service at its authenticated stock address",
        ),
        "open_cfw_bootloader_hw_fifo_drain_423342_source_in_place": (
            "bootloader_hw_fifo_drain_423342_source_in_place",
            "Compiled clean-room G2 per-instance FIFO drain wrapper at its authenticated stock address",
        ),
        "open_cfw_bootloader_hw_fifo_snapshot_423350_source_in_place": (
            "bootloader_hw_fifo_snapshot_423350_source_in_place",
            "Compiled clean-room G2 critical-section FIFO snapshot adapter at its authenticated stock address",
        ),
        "open_cfw_bootloader_hw_fifo_pump_423390_source_in_place": (
            "bootloader_hw_fifo_pump_423390_source_in_place",
            "Compiled clean-room G2 critical-section FIFO pump adapter at its authenticated stock address",
        ),
        "opaque_before_open_cfw_bootloader_hw_mode_dispatch_4233e8_source_in_place": (
            "bootloader_hw_fifo_adapter_literal_words_4233e0_opaque",
            "Authenticated retained literal words between the FIFO adapters and mode dispatcher",
        ),
        "open_cfw_bootloader_hw_mode_dispatch_4233e8_source_in_place": (
            "bootloader_hw_mode_dispatch_4233e8_source_in_place",
            "Compiled clean-room G2 per-instance mode dispatcher at its authenticated stock address",
        ),
        "opaque_before_open_cfw_bootloader_hw_mode_zero_wait_423444_source_in_place": (
            "bootloader_hw_mode_dispatch_literal_words_423430_opaque",
            "Authenticated retained literal words between the mode dispatcher and source-owned wait wrappers",
        ),
        "open_cfw_bootloader_hw_mode_zero_wait_423444_source_in_place": (
            "bootloader_hw_mode_zero_wait_423444_source_in_place",
            "Compiled clean-room G2 mode-zero bounded wait wrapper at its authenticated stock address",
        ),
        "open_cfw_bootloader_hw_mode_one_wait_42348e_source_in_place": (
            "bootloader_hw_mode_one_wait_42348e_source_in_place",
            "Compiled clean-room G2 mode-one bounded wait wrapper at its authenticated stock address",
        ),
        "open_cfw_bootloader_hw_mode_two_start_4234d8_source_in_place": (
            "bootloader_hw_mode_two_start_4234d8_source_in_place",
            "Compiled clean-room G2 mode-two latch and progress start helper at its authenticated stock address",
        ),
        "open_cfw_bootloader_hw_mode_three_start_4234fa_source_in_place": (
            "bootloader_hw_mode_three_start_4234fa_source_in_place",
            "Compiled clean-room G2 mode-three latch and progress start helper at its authenticated stock address",
        ),
        "open_cfw_bootloader_hw_primary_progress_423524_source_in_place": (
            "bootloader_hw_primary_progress_423524_source_in_place",
            "Compiled clean-room G2 primary progress service at its authenticated stock address",
        ),
        "open_cfw_bootloader_hw_secondary_progress_423608_source_in_place": (
            "bootloader_hw_secondary_progress_423608_source_in_place",
            "Compiled clean-room G2 secondary progress service at its authenticated stock address",
        ),
        "open_cfw_bootloader_hw_register_or_4236ce_source_in_place": (
            "bootloader_hw_register_or_4236ce_source_in_place",
            "Compiled clean-room G2 per-instance register OR service at its authenticated stock address",
        ),
        "opaque_before_open_cfw_bootloader_hw_register_write_423700_source_in_place": (
            "bootloader_hw_register_or_literal_words_4236fa_opaque",
            "Authenticated retained alignment and literal word between register services",
        ),
        "open_cfw_bootloader_hw_register_write_423700_source_in_place": (
            "bootloader_hw_register_write_423700_source_in_place",
            "Compiled clean-room G2 per-instance register write service at its authenticated stock address",
        ),
        "open_cfw_bootloader_hw_register_query_42372a_source_in_place": (
            "bootloader_hw_register_query_42372a_source_in_place",
            "Compiled clean-room G2 per-instance register query service at its authenticated stock address",
        ),
        "opaque_before_open_cfw_bootloader_hw_service_dispatch_42377c_source_in_place": (
            "bootloader_hw_service_dispatch_literal_words_423764_opaque",
            "Authenticated retained register and identity words before the service dispatcher",
        ),
        "open_cfw_bootloader_hw_service_dispatch_42377c_source_in_place": (
            "bootloader_hw_service_dispatch_42377c_source_in_place",
            "Compiled clean-room G2 per-instance service dispatcher at its authenticated stock address",
        ),
        "opaque_before_open_cfw_bootloader_memory_swap_423864_source_in_place": (
            "bootloader_memory_exchange_literal_words_42382c_opaque",
            "Authenticated retained literal and status words before the bounded memory-exchange helpers",
        ),
        "open_cfw_bootloader_memory_swap_423864_source_in_place": (
            "bootloader_memory_swap_423864_source_in_place",
            "Compiled clean-room G2 bounded two-buffer memory exchange at its authenticated stock address",
        ),
        "open_cfw_bootloader_memory_rotate3_4238ba_source_in_place": (
            "bootloader_memory_rotate3_4238ba_source_in_place",
            "Compiled clean-room G2 bounded three-buffer memory rotation at its authenticated stock address",
        ),
        "open_cfw_bootloader_memory_rotate_front_423928_source_in_place": (
            "bootloader_memory_rotate_front_423928_source_in_place",
            "Compiled clean-room G2 bounded rotate-to-front helper at its authenticated stock address",
        ),
        "open_cfw_bootloader_memory_sort3_423972_source_in_place": (
            "bootloader_memory_sort3_423972_source_in_place",
            "Compiled clean-room G2 three-element comparator/exchange helper at its authenticated stock address",
        ),
        "open_cfw_bootloader_memory_heap_sift_4239c2_source_in_place": (
            "bootloader_memory_heap_sift_4239c2_source_in_place",
            "Compiled clean-room G2 Floyd max-heap sift helper at its authenticated stock address",
        ),
        "open_cfw_bootloader_memory_qsort_core_423a48_source_in_place": (
            "bootloader_memory_qsort_core_423a48_source_in_place",
            "Compiled clean-room G2 introspective qsort core at its authenticated stock address",
        ),
        "open_cfw_bootloader_memory_qsort_423d08_source_in_place": (
            "bootloader_memory_qsort_423d08_source_in_place",
            "Compiled clean-room G2 public qsort wrapper at its authenticated stock address",
        ),
        "open_cfw_bootloader_hw_global_service_423d20_source_in_place": (
            "bootloader_hw_global_service_423d20_source_in_place",
            "Compiled clean-room G2 global hardware-control service at its authenticated stock address",
        ),
        "open_cfw_bootloader_hw_control_initialize_423d58_source_in_place": (
            "bootloader_hw_control_initialize_423d58_source_in_place",
            "Compiled clean-room G2 hardware-control initializer at its authenticated stock address",
        ),
        "open_cfw_bootloader_hw_control_query_423d7a_source_in_place": (
            "bootloader_hw_control_query_423d7a_source_in_place",
            "Compiled clean-room G2 hardware-control register query at its authenticated stock address",
        ),
        "opaque_before_open_cfw_bootloader_hw_control_test_423da0_source_in_place": (
            "bootloader_hw_control_register_literal_423d9a_opaque",
            "Authenticated retained hardware-control register literal and alignment bytes",
        ),
        "open_cfw_bootloader_hw_control_test_423da0_source_in_place": (
            "bootloader_hw_control_test_423da0_source_in_place",
            "Compiled clean-room G2 indexed hardware-control register test at its authenticated stock address",
        ),
        "open_cfw_bootloader_hw_control_test_zero_423dc4_source_in_place": (
            "bootloader_hw_control_test_zero_423dc4_source_in_place",
            "Compiled clean-room G2 zero-index hardware-control test wrapper at its authenticated stock address",
        ),
        "opaque_before_open_cfw_bootloader_hw_control_critical_423dd0_source_in_place": (
            "bootloader_hw_control_critical_alignment_423dce_opaque",
            "Authenticated retained alignment before the interrupt-atomic hardware-control service",
        ),
        "open_cfw_bootloader_hw_control_critical_423dd0_source_in_place": (
            "bootloader_hw_control_critical_423dd0_source_in_place",
            "Compiled clean-room G2 interrupt-atomic hardware-control service at its authenticated stock address",
        ),
        "opaque_before_open_cfw_bootloader_hw_control_state_423e14_source_in_place": (
            "bootloader_hw_control_sram_literals_423e0c_opaque",
            "Authenticated retained SRAM literal words before the hardware-control state mapper",
        ),
        "open_cfw_bootloader_hw_control_state_423e14_source_in_place": (
            "bootloader_hw_control_state_423e14_source_in_place",
            "Compiled clean-room G2 hardware-control state mapper at its authenticated stock address",
        ),
        "open_cfw_bootloader_mspi_fifo_write_423e40_source_in_place": (
            "bootloader_mspi_fifo_write_423e40_source_in_place",
            "Compiled clean-room G2 global MSPI FIFO-write service at its authenticated stock address",
        ),
        "open_cfw_bootloader_mspi_fifo_read_423e8a_source_in_place": (
            "bootloader_mspi_fifo_read_423e8a_source_in_place",
            "Compiled clean-room G2 global MSPI FIFO-read service at its authenticated stock address",
        ),
        "open_cfw_bootloader_mspi_cq_init_423f28_source_in_place": (
            "bootloader_mspi_cq_init_423f28_source_in_place",
            "Compiled clean-room G2 MSPI command-queue initializer at its authenticated stock address",
        ),
        "open_cfw_bootloader_mspi_cq_term_423f54_source_in_place": (
            "bootloader_mspi_cq_term_423f54_source_in_place",
            "Compiled clean-room G2 MSPI command-queue terminator at its authenticated stock address",
        ),
        "open_cfw_bootloader_mspi_cq_enable_423f8e_source_in_place": (
            "bootloader_mspi_cq_enable_423f8e_source_in_place",
            "Compiled clean-room G2 MSPI command-queue enable service at its authenticated stock address",
        ),
        "open_cfw_bootloader_mspi_cq_disable_423fac_source_in_place": (
            "bootloader_mspi_cq_disable_423fac_source_in_place",
            "Compiled clean-room G2 MSPI command-queue disable service at its authenticated stock address",
        ),
        "open_cfw_bootloader_mspi_cq_pause_423fb8_source_in_place": (
            "bootloader_mspi_cq_pause_423fb8_source_in_place",
            "Compiled AmbiqSuite-compatible G2 MSPI command-queue pause service at its authenticated stock address",
        ),
        "open_cfw_bootloader_mspi_program_dma_42403e_source_in_place": (
            "bootloader_mspi_program_dma_42403e_source_in_place",
            "Compiled AmbiqSuite-compatible G2 MSPI high-priority DMA programming service at its authenticated stock address",
        ),
        "open_cfw_bootloader_mspi_sched_hiprio_4240aa_source_in_place": (
            "bootloader_mspi_sched_hiprio_4240aa_source_in_place",
            "Compiled AmbiqSuite-compatible G2 MSPI high-priority scheduler at its authenticated stock address",
        ),
        "opaque_before_open_cfw_bootloader_mspi_piomixed_configure_42488e_source_in_place": (
            "bootloader_mspi_device_configure_unreachable_tail_42423c_42488e_official",
            "Authenticated unreachable stock tail after the source-owned MSPI device-configuration return",
        ),
        "open_cfw_bootloader_mspi_device_configure_424120_source_in_place": (
            "bootloader_mspi_device_configure_424120_source_in_place",
            "Compiled AmbiqSuite-compatible G2 MSPI device-mode configuration service at its authenticated stock address",
        ),
        "open_cfw_bootloader_mspi_piomixed_configure_42488e_source_in_place": (
            "bootloader_mspi_piomixed_configure_42488e_source_in_place",
            "Compiled AmbiqSuite-compatible G2 MSPI PIO mixed-mode configuration service at its authenticated stock address",
        ),
        "open_cfw_bootloader_mspi_dummy_callback_424976_source_in_place": (
            "bootloader_mspi_dummy_callback_424976_source_in_place",
            "Compiled AmbiqSuite-compatible G2 MSPI no-op callback at its authenticated stock address",
        ),
        "open_cfw_bootloader_mspi_seq_loopback_424978_source_in_place": (
            "bootloader_mspi_seq_loopback_424978_source_in_place",
            "Compiled AmbiqSuite-compatible G2 MSPI sequence-loopback callback at its authenticated stock address",
        ),
        "opaque_before_open_cfw_bootloader_mspi_clkgen_ctrl_4249a0_source_in_place": (
            "bootloader_mspi0_base_literal_42499c_opaque",
            "Authenticated retained MSPI0 base literal before the clock-generator control service",
        ),
        "open_cfw_bootloader_mspi_clkgen_ctrl_4249a0_source_in_place": (
            "bootloader_mspi_clkgen_ctrl_4249a0_source_in_place",
            "Compiled AmbiqSuite-compatible G2 MSPI clock-generator control service at its authenticated stock address",
        ),
        "open_cfw_bootloader_mspi_xip_off_delay_424a18_source_in_place": (
            "bootloader_mspi_xip_off_delay_424a18_source_in_place",
            "Compiled AmbiqSuite-compatible G2 MSPI XIP-off minimum-delay selector at its authenticated stock address",
        ),
        "open_cfw_bootloader_mspi_initialize_424a5a_source_in_place": (
            "bootloader_mspi_initialize_424a5a_source_in_place",
            "Compiled AmbiqSuite-compatible G2 MSPI handle initializer at its authenticated stock address",
        ),
        "opaque_before_open_cfw_bootloader_mspi_configure_424af0_source_in_place": (
            "bootloader_mspi_initialize_literal_424aea_opaque",
            "Authenticated alignment and G2 MSPI state-base literal between initialize and configure",
        ),
        "open_cfw_bootloader_mspi_configure_424af0_source_in_place": (
            "bootloader_mspi_configure_424af0_source_in_place",
            "Compiled AmbiqSuite-compatible G2 MSPI configuration service at its authenticated stock address",
        ),
        "opaque_before_open_cfw_bootloader_mspi_device_configure_public_424be4_source_in_place": (
            "bootloader_mspi_device_config_literals_424bd4_opaque",
            "Authenticated handle, MSPI base, and pad-mask literals before public device configuration",
        ),
        "open_cfw_bootloader_mspi_device_configure_public_424be4_source_in_place": (
            "bootloader_mspi_device_configure_public_424be4_source_in_place",
            "Compiled AmbiqSuite-compatible G2 public MSPI device-configuration service at its authenticated stock address",
        ),
        "opaque_before_open_cfw_bootloader_mspi_enable_425066_source_in_place": (
            "bootloader_mspi_device_configure_public_unreachable_tail_424e84_425066_official",
            "Authenticated unreachable stock tail after the source-owned public MSPI device-configuration return",
        ),
        "open_cfw_bootloader_mspi_enable_425066_source_in_place": (
            "bootloader_mspi_enable_425066_source_in_place",
            "Compiled AmbiqSuite-compatible G2 MSPI enable service at its authenticated stock address",
        ),
        "opaque_before_open_cfw_bootloader_mspi_disable_4250f0_source_in_place": (
            "bootloader_mspi_enable_unreachable_tail_4250e6_4250f0_official",
            "Authenticated unreachable stock tail after the source-owned MSPI enable return",
        ),
        "open_cfw_bootloader_mspi_disable_4250f0_source_in_place": (
            "bootloader_mspi_disable_4250f0_source_in_place",
            "Compiled AmbiqSuite-compatible G2 MSPI disable service at its authenticated stock address",
        ),
        "opaque_before_open_cfw_bootloader_mspi_deinitialize_42516c_source_in_place": (
            "bootloader_mspi_disable_tail_and_lifecycle_alignment_425160_opaque",
            "Authenticated unreachable disable tail plus alignment and lifecycle literal bytes before MSPI deinitialize",
        ),
        "open_cfw_bootloader_mspi_deinitialize_42516c_source_in_place": (
            "bootloader_mspi_deinitialize_42516c_source_in_place",
            "Compiled AmbiqSuite-compatible G2 MSPI deinitialize service at its authenticated stock address",
        ),
        "opaque_before_open_cfw_bootloader_mspi_control_4251c0_source_in_place": (
            "bootloader_mspi_control_prefix_4251a4_opaque",
            "Authenticated alignment and literal pool between MSPI deinitialize and the control dispatcher",
        ),
        "open_cfw_bootloader_mspi_control_4251c0_source_in_place": (
            "bootloader_mspi_control_4251c0_source_in_place",
            "Compiled stock-ABI request adapter for the G2 MSPI control dispatcher at its authenticated stock address",
        ),
        "open_cfw_bootloader_mspi_control_upstream_4251c0_source_in_place": (
            "bootloader_mspi_control_upstream_42523c_source_in_place",
            "Compiled maintained AmbiqSuite Apollo510 MSPI control body behind the stock G2 request adapter",
        ),
        "opaque_before_open_cfw_bootloader_mspi_blocking_transfer_4262e0_source_in_place": (
            "bootloader_mspi_control_unreachable_tail_42612c_4262e0_official",
            "Authenticated unreachable stock tail after the source-owned MSPI control dispatcher",
        ),
        "open_cfw_bootloader_mspi_blocking_transfer_4262e0_source_in_place": (
            "bootloader_mspi_blocking_transfer_4262e0_source_in_place",
            "Compiled AmbiqSuite-compatible G2 MSPI blocking-transfer service at its authenticated stock address",
        ),
        "opaque_before_open_cfw_bootloader_mspi_interrupt_enable_426450_source_in_place": (
            "bootloader_mspi_blocking_transfer_unreachable_tail_and_alignment_4263e0_426450_official",
            "Authenticated unreachable stock tail after the source-owned blocking-transfer return plus the four-byte alignment boundary before interrupt services",
        ),
        "open_cfw_bootloader_mspi_interrupt_enable_426450_source_in_place": (
            "bootloader_mspi_interrupt_enable_426450_source_in_place",
            "Compiled AmbiqSuite-compatible G2 MSPI interrupt-enable service at its authenticated stock address",
        ),
        "opaque_before_open_cfw_bootloader_mspi_interrupt_disable_426484_source_in_place": (
            "bootloader_mspi_interrupt_enable_unreachable_tail_42647c_426484_official",
            "Authenticated unreachable stock tail after the source-owned MSPI interrupt-enable return",
        ),
        "open_cfw_bootloader_mspi_interrupt_disable_426484_source_in_place": (
            "bootloader_mspi_interrupt_disable_426484_source_in_place",
            "Compiled AmbiqSuite-compatible G2 MSPI interrupt-disable service at its authenticated stock address",
        ),
        "opaque_before_open_cfw_bootloader_mspi_interrupt_status_get_4264ba_source_in_place": (
            "bootloader_mspi_interrupt_disable_unreachable_tail_4264b0_4264ba_official",
            "Authenticated unreachable stock tail after the source-owned MSPI interrupt-disable return",
        ),
        "open_cfw_bootloader_mspi_interrupt_status_get_4264ba_source_in_place": (
            "bootloader_mspi_interrupt_status_get_4264ba_source_in_place",
            "Compiled AmbiqSuite-compatible G2 MSPI interrupt-status service at its authenticated stock address",
        ),
        "open_cfw_bootloader_mspi_interrupt_service_426536_source_in_place": (
            "bootloader_mspi_interrupt_service_426536_source_in_place",
            "Compiled AmbiqSuite 5.1.0-compatible MSPI interrupt-service dispatcher at its authenticated stock address",
        ),
        "opaque_before_open_cfw_bootloader_mspi_power_control_426808_source_in_place": (
            "bootloader_mspi_interrupt_service_literal_pool_4267fe_opaque",
            "Authenticated non-executable MSPI interrupt-service literal pool retained before power control",
        ),
        "open_cfw_bootloader_mspi_power_control_426808_source_in_place": (
            "bootloader_mspi_power_control_426808_source_in_place",
            "Compiled AmbiqSuite 5.1.0-compatible MSPI power-control service at its authenticated stock address",
        ),
        "opaque_after_source_redirects": (
            "bootloader_opaque_after_mspi_power_control_426bfe",
            "Authenticated retained bootloader bytes after the source-owned MSPI power-control body, beginning with its literal pool",
        ),
        "opaque_before_replace_ambiq_mspi_interrupt_clear": (
            "bootloader_mspi_interrupt_status_get_unreachable_tail_4264f6_426506_official",
            "Authenticated unreachable stock tail after the source-owned MSPI interrupt-status return and before the source-routed interrupt-clear entry",
        ),
        "opaque_before_open_cfw_bootloader_mspi_dummy_callback_424976_source_in_place": (
            "bootloader_mspi_piomixed_configure_unreachable_tail_4248e2_424976_official",
            "Authenticated unreachable stock tail after the source-owned MSPI PIO-mixed configuration return",
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
        "open_cfw_bootloader_nvic_enable_irq_41fdc0_source_leaf": (
            "bootloader_nvic_enable_irq_41fdc0_source_leaf",
            "Compiled clean-room G2 NVIC interrupt-enable entry",
        ),
        "open_cfw_bootloader_nvic_set_priority_41fdde_source_leaf": (
            "bootloader_nvic_set_priority_41fdde_source_leaf",
            "Compiled clean-room G2 NVIC/system-handler priority entry",
        ),
        "open_cfw_bootloader_mspi_isr_41fe06_source_leaf": (
            "bootloader_mspi_isr_41fe06_source_leaf",
            "Compiled clean-room G2 MSPI status-clear-service interrupt wrapper",
        ),
        "open_cfw_bootloader_mspi_enable_41fe28_source_leaf": (
            "bootloader_mspi_enable_41fe28_source_leaf",
            "Compiled clean-room idempotent G2 MSPI enable entry",
        ),
        "open_cfw_bootloader_mspi_disable_41fe48_source_leaf": (
            "bootloader_mspi_disable_41fe48_source_leaf",
            "Compiled clean-room G2 MSPI disable entry",
        ),
        "open_cfw_bootloader_event_flags_init_41fe62_source_leaf": (
            "bootloader_event_flags_init_41fe62_source_leaf",
            "Compiled clean-room guarded G2 event-flags service initializer",
        ),
        "open_cfw_bootloader_event_flags_acquire_41fe9c_source_leaf": (
            "bootloader_event_flags_acquire_41fe9c_source_leaf",
            "Compiled clean-room guarded G2 event-flags acquire entry",
        ),
        "open_cfw_bootloader_event_flags_release_41fed4_source_leaf": (
            "bootloader_event_flags_release_41fed4_source_leaf",
            "Compiled clean-room guarded G2 event-flags release entry",
        ),
        "open_cfw_bootloader_mspi_guard_enter_41ff08_source_leaf": (
            "bootloader_mspi_guard_enter_41ff08_source_leaf",
            "Compiled clean-room paired G2 event-lock and conditional MSPI-disable guard entry",
        ),
        "open_cfw_bootloader_mspi_guard_exit_41ff1e_source_leaf": (
            "bootloader_mspi_guard_exit_41ff1e_source_leaf",
            "Compiled clean-room conditional G2 MSPI-enable and paired event-unlock guard exit",
        ),
        "open_cfw_bootloader_mspi_xip_config_41ff34_source_leaf": (
            "bootloader_mspi_xip_config_41ff34_source_leaf",
            "Compiled clean-room G2 MSPI XIP configuration-byte updater",
        ),
        "open_cfw_bootloader_longest_ones_run_41ff60_source_leaf": (
            "bootloader_longest_ones_run_41ff60_source_leaf",
            "Compiled clean-room G2 longest consecutive-one run-length helper",
        ),
        "open_cfw_bootloader_longest_ones_center_41ff74_source_leaf": (
            "bootloader_longest_ones_center_41ff74_source_leaf",
            "Compiled clean-room G2 longest consecutive-one run center-selection helper",
        ),
        "open_cfw_bootloader_mspi_timing_scan_420002_alignment_padding": (
            "bootloader_mspi_timing_scan_420002_alignment_padding",
            "Generated two-byte alignment before the G2 MSPI timing scan",
        ),
        "open_cfw_bootloader_mspi_timing_scan_420002_source_leaf": (
            "bootloader_mspi_timing_scan_420002_source_leaf",
            "Compiled clean-room G2 exhaustive MSPI timing scan and center-selection entry",
        ),
        "open_cfw_bootloader_mspi_timing_auto_4201ba_source_leaf": (
            "bootloader_mspi_timing_auto_4201ba_source_leaf",
            "Compiled clean-room G2 automatic MSPI timing-selection and fallback wrapper",
        ),
        "open_cfw_bootloader_mspi_low_level_init_420254_source_leaf": (
            "bootloader_mspi_low_level_init_420254_source_leaf",
            "Compiled clean-room G2 MX25U25643G low-level MSPI initializer",
        ),
        "open_cfw_bootloader_mspi_driver_init_420476_source_leaf": (
            "bootloader_mspi_driver_init_420476_source_leaf",
            "Compiled clean-room G2 MX25U25643G public initialization wrapper",
        ),
        "open_cfw_bootloader_mspi_soft_reset_42052a_source_leaf": (
            "bootloader_mspi_soft_reset_42052a_source_leaf",
            "Compiled clean-room G2 MX25U25643G soft-reset sequence",
        ),
        "open_cfw_bootloader_mspi_read_id_42059e_source_leaf": (
            "bootloader_mspi_read_id_42059e_source_leaf",
            "Compiled clean-room G2 MX25U25643G JEDEC-ID reader",
        ),
        "open_cfw_bootloader_mspi_read_transfer_4205f4_source_leaf": (
            "bootloader_mspi_read_transfer_4205f4_source_leaf",
            "Compiled clean-room G2 MX25U25643G read-transfer wrapper",
        ),
        "open_cfw_bootloader_mspi_write_transfer_42069e_source_leaf": (
            "bootloader_mspi_write_transfer_42069e_source_leaf",
            "Compiled clean-room G2 MX25U25643G write-transfer wrapper",
        ),
        "open_cfw_bootloader_mspi_busy_status_42074e_source_leaf": (
            "bootloader_mspi_busy_status_42074e_source_leaf",
            "Compiled clean-room G2 MX25U25643G status-register reader",
        ),
        "open_cfw_bootloader_mspi_wait_ready_4207a2_source_leaf": (
            "bootloader_mspi_wait_ready_4207a2_source_leaf",
            "Compiled clean-room G2 MX25U25643G two-phase ready poll",
        ),
        "open_cfw_bootloader_mspi_wait_ready_default_4207f4_source_leaf": (
            "bootloader_mspi_wait_ready_default_4207f4_source_leaf",
            "Compiled clean-room G2 MX25U25643G fixed ready-poll wrapper",
        ),
        "open_cfw_bootloader_mspi_4byte_mode_420800_source_leaf": (
            "bootloader_mspi_4byte_mode_420800_source_leaf",
            "Compiled clean-room G2 MX25U25643G address-mode reader",
        ),
        "open_cfw_bootloader_mspi_enter_4byte_mode_420890_source_leaf": (
            "bootloader_mspi_enter_4byte_mode_420890_source_leaf",
            "Compiled clean-room G2 MX25U25643G four-byte-mode entry sequence",
        ),
        "open_cfw_bootloader_mspi_write_enable_420984_source_leaf": (
            "bootloader_mspi_write_enable_420984_source_leaf",
            "Compiled clean-room G2 MX25U25643G write-enable command wrapper",
        ),
        "open_cfw_bootloader_mspi_write_disable_4209c4_source_leaf": (
            "bootloader_mspi_write_disable_4209c4_source_leaf",
            "Compiled clean-room G2 MX25U25643G write-disable command wrapper",
        ),
        "open_cfw_bootloader_mspi_sector_erase_420a08_source_leaf": (
            "bootloader_mspi_sector_erase_420a08_source_leaf",
            "Compiled clean-room G2 MX25U25643G guarded sector-erase service",
        ),
        "open_cfw_bootloader_mspi_program_420b0c_source_leaf": (
            "bootloader_mspi_program_420b0c_source_leaf",
            "Compiled clean-room G2 MX25U25643G guarded page-splitting program service",
        ),
        "open_cfw_bootloader_mspi_quad_enable_420c5c_source_leaf": (
            "bootloader_mspi_quad_enable_420c5c_source_leaf",
            "Compiled clean-room G2 MX25U25643G status-register-2 QE service",
        ),
        "open_cfw_bootloader_mspi_device_reconfigure_420e08_source_leaf": (
            "bootloader_mspi_device_reconfigure_420e08_source_leaf",
            "Compiled clean-room G2 MSPI disable, device-configure, enable, and pin-group service",
        ),
        "open_cfw_bootloader_mspi_set_quad_mode_420e8c_source_leaf": (
            "bootloader_mspi_set_quad_mode_420e8c_source_leaf",
            "Compiled clean-room G2 MX25U25643G quad-mode template, reconfiguration, XIP, and control service",
        ),
        "open_cfw_bootloader_mspi_set_serial_mode_420f10_source_leaf": (
            "bootloader_mspi_set_serial_mode_420f10_source_leaf",
            "Compiled clean-room G2 MX25U25643G serial-mode reconfiguration, XIP, and control service",
        ),
        "open_cfw_bootloader_mspi_read_420f70_source_leaf": (
            "bootloader_mspi_read_420f70_source_leaf",
            "Compiled clean-room G2 MX25U25643G guarded blocking read service",
        ),
        "open_cfw_bootloader_check_and_create_directories_4210c8_source_leaf": (
            "bootloader_check_and_create_directories_4210c8_source_leaf",
            "Compiled clean-room G2 LittleFS directory bootstrap service",
        ),
        "open_cfw_littlefs_bootloader_format_4211b0_source_leaf": (
            "bootloader_littlefs_format_4211b0_source_leaf",
            "Compiled clean-room G2 LittleFS format, mount, and directory-bootstrap orchestration service",
        ),
        "open_cfw_littlefs_bootloader_init_421210_source_leaf": (
            "bootloader_littlefs_init_421210_source_leaf",
            "Compiled clean-room G2 LittleFS mount, recovery, readiness, and boot-counter initialization service",
        ),
        "open_cfw_bootloader_littlefs_read_4212d8_source_leaf": (
            "bootloader_littlefs_read_4212d8_source_leaf",
            "Compiled clean-room G2 LittleFS block-read callback",
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
    descriptions.update({
        "open_cfw_clkmgr_hfrc2_uq15_divider_source_cave": (
            "bootloader_clkmgr_hfrc2_uq15_divider_source_cave",
            "Compiled MIT Apollo510 HFRC2 UQ17.15 divider calculator in authenticated reclaimed NOP space",
        ),
        "open_cfw_clkmgr_hfrc_integer_divider_source_cave": (
            "bootloader_clkmgr_hfrc_integer_divider_source_cave",
            "Compiled MIT Apollo510 HFRC integer divider calculator in authenticated reclaimed NOP space",
        ),
        "replace_bootloader_easylogger_output_4176ce_source_redirect_after_caves": (
            "bootloader_easylogger_output_generated_fill_after_clkmgr_caves",
            "Generated NOP fill after the clock-manager source caves within the EasyLogger output replacement span",
        ),
        "opaque_before_open_cfw_bootloader_memset_wrapper_426c10_source_in_place": (
            "bootloader_mspi_power_control_literal_pool_426bfe_426c10_official",
            "Authenticated non-executable MSPI power-control literal pool and alignment",
        ),
        "open_cfw_bootloader_memset_wrapper_426c10_source_in_place": (
            "bootloader_memset_wrapper_426c10_source_in_place",
            "Compiled MIT conventional memset ABI wrapper over the source-owned Arm EABI byte-fill provider",
        ),
        "opaque_before_replace_bootloader_clkmgr_hfrc2_uq15_divider_426c24": (
            "bootloader_memset_wrapper_unreachable_tail_426c22_426c24_official",
            "Authenticated unreachable terminal return after the source-owned memset wrapper",
        ),
        "replace_bootloader_clkmgr_hfrc2_uq15_divider_426c24_source_redirect": (
            "bootloader_clkmgr_hfrc2_uq15_divider_source_redirect",
            "Generated entry redirect replacing the complete HFRC2 UQ17.15 divider body",
        ),
        "open_cfw_bootloader_clkgen_hfadj_config_426c72_source_cave": (
            "bootloader_clkgen_hfadj_config_426c72_source_cave",
            "Compiled MIT CLKGEN HFADJ configuration publisher in authenticated generated-NOP space",
        ),
        "open_cfw_bootloader_clkgen_hfadj_disable_426c7e_source_cave": (
            "bootloader_clkgen_hfadj_disable_426c7e_source_cave",
            "Compiled MIT CLKGEN HFADJ bit-preserving disable leaf in authenticated generated-NOP space",
        ),
        "replace_bootloader_clkmgr_hfrc2_uq15_divider_426c24_source_redirect_after_caves": (
            "bootloader_clkmgr_hfrc2_uq15_divider_generated_fill_after_hfadj_caves",
            "Generated NOP fill after the CLKGEN HFADJ configuration and disable source caves",
        ),
        "replace_bootloader_clkmgr_hfrc_integer_divider_426c4e_source_redirect": (
            "bootloader_clkmgr_hfrc_integer_divider_source_redirect",
            "Generated entry redirect and NOP fill replacing the complete HFRC integer divider body",
        ),
        "open_cfw_bootloader_clkgen_hfadj_enable_426c58_source_in_place": (
            "bootloader_clkgen_hfadj_enable_426c58_source_in_place",
            "Compiled MIT CLKGEN HFADJ bit-control leaf at its authenticated stock address",
        ),
        "opaque_before_replace_bootloader_clkgen_hfadj_config_426c72": (
            "bootloader_clkgen_hfadj_enable_unreachable_tail_426c70_426c72_official",
            "Authenticated unreachable terminal return after the source-owned CLKGEN HFADJ enable leaf",
        ),
        "replace_bootloader_clkgen_hfadj_config_426c72_source_redirect": (
            "bootloader_clkgen_hfadj_config_426c72_source_redirect",
            "Generated entry redirect and NOP fill routing the complete CLKGEN HFADJ configuration service to compiled MIT C",
        ),
        "replace_bootloader_clkgen_hfadj_disable_426c7e_source_redirect": (
            "bootloader_clkgen_hfadj_disable_426c7e_source_redirect",
            "Generated entry redirect and NOP fill routing the complete CLKGEN HFADJ disable service to compiled MIT C",
        ),
        "open_cfw_bootloader_dual_switch_426c8c_source_in_place": (
            "bootloader_dual_switch_426c8c_source_in_place",
            "Compiled MIT CLKGEN dual-clock switch with authenticated transition status check",
        ),
        "opaque_before_replace_bootloader_clkgen_config_426ccc": (
            "bootloader_dual_switch_unreachable_tail_426cc4_426ccc_official",
            "Authenticated unreachable terminal tail after the source-owned CLKGEN dual-clock switch",
        ),
        "replace_bootloader_clkgen_config_426ccc_source_redirect": (
            "bootloader_clkgen_config_426ccc_source_redirect",
            "Generated entry redirect and NOP fill routing the complete CLKGEN configuration service to compiled MIT C",
        ),
        "replace_bootloader_clkgen_disable_426d1e_source_redirect": (
            "bootloader_clkgen_disable_426d1e_source_redirect",
            "Generated entry redirect and NOP fill routing the complete CLKGEN disable service to compiled MIT C",
        ),
        "opaque_before_replace_bootloader_float_gcd_426d48": (
            "bootloader_clkgen_gap_426d2c_426d48_official",
            "Authenticated padding and literal-pool bytes between the CLKGEN disable and floating common-divisor entries",
        ),
        "replace_bootloader_float_gcd_426d48_source_redirect": (
            "bootloader_float_gcd_426d48_source_redirect",
            "Generated entry redirect and NOP fill routing the complete bounded floating common-divisor helper to compiled MIT C",
        ),
        "opaque_before_replace_bootloader_float_ratio_426db4": (
            "bootloader_float_gap_426db2_426db4_official",
            "Authenticated two-byte padding between the floating common-divisor and ratio helper entries",
        ),
        "replace_bootloader_float_ratio_426db4_source_redirect": (
            "bootloader_float_ratio_426db4_source_redirect",
            "Generated entry redirect and NOP fill routing the complete bounded floating ratio validation helper to compiled MIT C",
        ),
        "replace_bootloader_float_multiplier_426eac_source_redirect": (
            "bootloader_float_multiplier_426eac_source_redirect",
            "Generated entry redirect and NOP fill routing the complete bounded floating multiplier validation helper to compiled MIT C",
        ),
        "opaque_before_replace_bootloader_float_encoding_select_426f6c": (
            "bootloader_float_gap_426f6a_426f6c_official",
            "Authenticated two-byte padding between the floating multiplier and encoding-selector entries",
        ),
        "replace_bootloader_float_encoding_select_426f6c_source_redirect": (
            "bootloader_float_encoding_select_426f6c_source_redirect",
            "Generated entry redirect and NOP fill routing the complete floating encoding selection and result publication service to compiled MIT C",
        ),
        "opaque_before_replace_bootloader_syspll_min_fvco_427040": (
            "bootloader_float_select_syspll_gap_427032_427040_official",
            "Authenticated literals and alignment between the floating selector and System PLL minimum-VCO entry",
        ),
        "replace_bootloader_syspll_min_fvco_427040_source_redirect": (
            "bootloader_syspll_min_fvco_427040_source_redirect",
            "Generated entry redirect routing the complete System PLL minimum-VCO service to reviewed BSD-3-Clause C",
        ),
        "opaque_before_replace_bootloader_syspll_postdiv_427160": (
            "bootloader_syspll_gap_42714c_427160_official",
            "Authenticated literals and alignment between the System PLL minimum-VCO and postdivider entries",
        ),
        "replace_bootloader_syspll_postdiv_427160_source_redirect": (
            "bootloader_syspll_postdiv_427160_source_redirect",
            "Generated entry redirect routing the complete System PLL postdivider service to reviewed BSD-3-Clause C",
        ),
        "replace_bootloader_syspll_initialize_4272ac_source_redirect": (
            "bootloader_syspll_initialize_4272ac_source_redirect",
            "Generated entry redirect routing the complete System PLL initialization service to reviewed BSD-3-Clause C",
        ),
        "opaque_before_open_cfw_bootloader_row6_destroy_427310_source_in_place": (
            "bootloader_syspll_deinitialize_gap_427308_427310_official",
            "Authenticated literal/alignment gap between the System PLL initialization and deinitialization services",
        ),
        "open_cfw_bootloader_row6_destroy_427310_source_in_place": (
            "bootloader_syspll_deinitialize_427310_source_in_place",
            "Compiled BSD-3-Clause System PLL deinitialization service replacing its complete stock body in place",
        ),
        "replace_bootloader_syspll_enable_427360_source_redirect": (
            "bootloader_syspll_enable_427360_source_redirect",
            "Generated entry redirect routing the complete System PLL enable service to reviewed BSD-3-Clause C",
        ),
        "open_cfw_bootloader_row6_stop_4273dc_source_in_place": (
            "bootloader_syspll_disable_4273dc_source_in_place",
            "Compiled BSD-3-Clause System PLL disable service replacing its complete stock body in place",
        ),
        "replace_bootloader_syspll_configure_42740c_source_redirect": (
            "bootloader_syspll_configure_42740c_source_redirect",
            "Generated entry redirect routing the complete System PLL configuration service to reviewed BSD-3-Clause C",
        ),
        "replace_bootloader_syspll_lock_wait_427522_source_redirect": (
            "bootloader_syspll_lock_wait_427522_source_redirect",
            "Generated entry redirect routing the complete System PLL lock-wait service to reviewed BSD-3-Clause C",
        ),
        "opaque_before_replace_bootloader_queue_init_4275ea": (
            "bootloader_syspll_queue_gap_427588_4275ea_official",
            "Authenticated literals, alignment, and intervening code between System PLL lock-wait and the queue family",
        ),
        "replace_bootloader_queue_init_4275ea_source_redirect": (
            "bootloader_queue_init_4275ea_source_redirect",
            "Generated entry redirect routing the complete queue initializer to reviewed BSD-3-Clause C",
        ),
        "replace_bootloader_queue_item_add_427602_source_redirect": (
            "bootloader_queue_item_add_427602_source_redirect",
            "Generated entry redirect routing the complete queue item-add service to reviewed BSD-3-Clause C",
        ),
        "replace_bootloader_queue_item_get_427660_source_redirect": (
            "bootloader_queue_item_get_427660_source_redirect",
            "Generated entry redirect routing the complete queue item-get service to reviewed BSD-3-Clause C",
        ),
        "opaque_before_replace_bootloader_memmove_4276bc": (
            "bootloader_queue_memmove_alignment_4276ba_4276bc_official",
            "Authenticated zero alignment halfword between the queue family and memmove",
        ),
        "replace_bootloader_memmove_4276bc_source_redirect": (
            "bootloader_memmove_4276bc_source_redirect",
            "Generated entry redirect and NOP fill routing the complete overlap-safe byte move to reviewed MIT C",
        ),
        "opaque_before_replace_bootloader_cmdq_update_indices_427754": (
            "bootloader_memmove_cmdq_alignment_427752_427754_official",
            "Authenticated zero alignment halfword between memmove and the command-queue index updater",
        ),
        "replace_bootloader_cmdq_update_indices_427754_source_redirect": (
            "bootloader_cmdq_update_indices_427754_source_redirect",
            "Generated entry redirect routing the complete command-queue index updater to reviewed BSD-3-Clause C",
        ),
        "open_cfw_bootloader_cmdq_init_427794_source_in_place": (
            "bootloader_cmdq_init_427794_source_in_place",
            "Compiled BSD-3-Clause AmbiqSuite command-queue initializer at its authenticated stock entry",
        ),
        "opaque_before_open_cfw_bootloader_cmdq_enable_427878_source_in_place": (
            "bootloader_cmdq_init_427794_unreachable_tail",
            "Authenticated unreachable remainder after the source-owned command-queue initializer",
        ),
        "open_cfw_bootloader_cmdq_enable_427878_source_in_place": (
            "bootloader_cmdq_enable_427878_source_in_place",
            "Compiled BSD-3-Clause AmbiqSuite command-queue enable service at its authenticated stock entry",
        ),
        "opaque_before_open_cfw_bootloader_cmdq_disable_4278c8_source_in_place": (
            "bootloader_cmdq_enable_427878_unreachable_tail",
            "Authenticated unreachable remainder after the source-owned command-queue enable service",
        ),
        "open_cfw_bootloader_cmdq_disable_4278c8_source_in_place": (
            "bootloader_cmdq_disable_4278c8_source_in_place",
            "Compiled BSD-3-Clause AmbiqSuite command-queue disable service at its authenticated stock entry",
        ),
        "opaque_before_open_cfw_bootloader_cmdq_alloc_block_42790a_source_in_place": (
            "bootloader_cmdq_disable_4278c8_unreachable_tail",
            "Authenticated unreachable remainder after the source-owned command-queue disable service",
        ),
        "open_cfw_bootloader_cmdq_alloc_block_42790a_source_in_place": (
            "bootloader_cmdq_alloc_block_42790a_source_in_place",
            "Compiled BSD-3-Clause AmbiqSuite command-queue block allocator at its authenticated stock entry",
        ),
        "opaque_before_open_cfw_bootloader_cmdq_release_block_4279be_source_in_place": (
            "bootloader_cmdq_alloc_block_42790a_unreachable_tail",
            "Authenticated unreachable remainder after the source-owned command-queue block allocator",
        ),
        "open_cfw_bootloader_cmdq_release_block_4279be_source_in_place": (
            "bootloader_cmdq_release_block_4279be_source_in_place",
            "Compiled BSD-3-Clause AmbiqSuite command-queue block release service at its authenticated stock entry",
        ),
        "opaque_before_open_cfw_bootloader_cmdq_post_block_4279f0_source_in_place": (
            "bootloader_cmdq_release_block_4279be_unreachable_tail",
            "Authenticated unreachable remainder after the source-owned command-queue block release service",
        ),
        "open_cfw_bootloader_cmdq_post_block_4279f0_source_in_place": (
            "bootloader_cmdq_post_block_4279f0_source_in_place",
            "Compiled BSD-3-Clause AmbiqSuite command-queue block post service at its authenticated stock entry",
        ),
        "opaque_before_open_cfw_bootloader_cmdq_get_status_427a56_source_in_place": (
            "bootloader_cmdq_post_block_4279f0_unreachable_tail",
            "Authenticated unreachable remainder after the source-owned command-queue block post service",
        ),
        "open_cfw_bootloader_cmdq_get_status_427a56_source_in_place": (
            "bootloader_cmdq_get_status_427a56_source_in_place",
            "Compiled BSD-3-Clause AmbiqSuite command-queue status service at its authenticated stock entry",
        ),
        "opaque_before_open_cfw_bootloader_cmdq_term_427ad6_source_in_place": (
            "bootloader_cmdq_get_status_427a56_unreachable_tail",
            "Authenticated unreachable remainder after the source-owned command-queue status service",
        ),
        "open_cfw_bootloader_cmdq_term_427ad6_source_in_place": (
            "bootloader_cmdq_term_427ad6_source_in_place",
            "Compiled BSD-3-Clause AmbiqSuite command-queue termination service at its authenticated stock entry",
        ),
        "opaque_before_open_cfw_bootloader_cmdq_error_resume_427b38_source_in_place": (
            "bootloader_cmdq_term_427ad6_unreachable_tail",
            "Authenticated unreachable remainder after the source-owned command-queue termination service",
        ),
        "open_cfw_bootloader_cmdq_error_resume_427b38_source_in_place": (
            "bootloader_cmdq_error_resume_427b38_source_in_place",
            "Compiled BSD-3-Clause AmbiqSuite command-queue error-resume service at its authenticated stock entry",
        ),
        "opaque_before_open_cfw_bootloader_cmdq_reset_427baa_source_in_place": (
            "bootloader_cmdq_error_resume_427b38_unreachable_tail",
            "Authenticated unreachable remainder after the source-owned command-queue error-resume service",
        ),
        "open_cfw_bootloader_cmdq_reset_427baa_source_in_place": (
            "bootloader_cmdq_reset_427baa_source_in_place",
            "Compiled BSD-3-Clause AmbiqSuite command-queue reset service at its authenticated stock entry",
        ),
        "opaque_before_open_cfw_bootloader_cmdq_post_loop_block_427c12_source_in_place": (
            "bootloader_cmdq_reset_427baa_unreachable_tail",
            "Authenticated unreachable remainder after the source-owned command-queue reset service",
        ),
        "open_cfw_bootloader_cmdq_post_loop_block_427c12_source_in_place": (
            "bootloader_cmdq_post_loop_block_427c12_source_in_place",
            "Compiled BSD-3-Clause AmbiqSuite looping command-queue post service at its authenticated stock entry",
        ),
        "opaque_before_open_cfw_bootloader_floorf_427c90_source_in_place": (
            "bootloader_cmdq_tail_and_float_math_gap_427c72_427c90",
            "Authenticated unreachable command-queue suffix and typed gap before the source-owned binary32 math runtime",
        ),
        "open_cfw_bootloader_floorf_427c90_source_in_place": (
            "bootloader_floorf_427c90_source_in_place",
            "Compiled MIT hard-float floor veneer at its authenticated stock entry",
        ),
        "open_cfw_bootloader_floor_bits_427ca0_source_in_place": (
            "bootloader_floor_bits_427ca0_source_in_place",
            "Compiled MIT binary32 floor core at its authenticated internal entry",
        ),
        "open_cfw_bootloader_fmodf_427ccc_source_in_place": (
            "bootloader_fmodf_427ccc_source_in_place",
            "Compiled MIT hard-float remainder veneer at its authenticated stock entry",
        ),
        "open_cfw_bootloader_fmod_bits_427cdc_source_in_place": (
            "bootloader_fmod_bits_427cdc_source_in_place",
            "Compiled MIT freestanding binary32 remainder core at its authenticated internal entry",
        ),
        "opaque_before_open_cfw_bootloader_roundf_427d98_source_in_place": (
            "bootloader_fmod_bits_427cdc_unreachable_tail",
            "Authenticated unreachable remainder after the source-owned binary32 remainder core",
        ),
        "open_cfw_bootloader_roundf_427d98_source_in_place": (
            "bootloader_roundf_427d98_source_in_place",
            "Compiled MIT hard-float round veneer at its authenticated stock entry",
        ),
        "open_cfw_bootloader_round_bits_427da8_source_in_place": (
            "bootloader_round_bits_427da8_source_in_place",
            "Compiled MIT binary32 round core at its authenticated internal entry",
        ),
        "open_cfw_bootloader_ceilf_427dd0_source_in_place": (
            "bootloader_ceilf_427dd0_source_in_place",
            "Compiled MIT hard-float ceiling veneer at its authenticated stock entry",
        ),
        "open_cfw_bootloader_ceil_bits_427de0_source_in_place": (
            "bootloader_ceil_bits_427de0_source_in_place",
            "Compiled MIT binary32 ceiling core at its authenticated internal entry",
        ),
        "open_cfw_bootloader_float_range_classify_427e0c_source_in_place": (
            "bootloader_float_range_classify_427e0c_source_in_place",
            "Compiled MIT binary32 range classifier at its authenticated stock entry",
        ),
        "opaque_before_open_cfw_bootloader_spotmgr_transition_sequence_2b_428378_source_in_place": (
            "bootloader_opaque_between_float_math_and_spotmgr_427e54_428378",
            "Authenticated retained literal, table, and alignment bytes between the binary32 runtime and SPOT-manager transition",
        ),
        "open_cfw_bootloader_spotmgr_transition_sequence_2b_428378_source_in_place": (
            "bootloader_spotmgr_transition_sequence_2b_428378_source_in_place",
            "Compiled BSD-3-Clause Apollo510 SPOT-manager transition sequence at its authenticated stock entry",
        ),
        "opaque_before_open_cfw_bootloader_spotmgr_transition_sequence_7b_428a94_source_in_place": (
            "bootloader_opaque_between_spotmgr_transitions_4283e2_428a94",
            "Authenticated retained literal, table, and alignment bytes between the source-owned SPOT-manager transitions",
        ),
        "open_cfw_bootloader_spotmgr_transition_sequence_7b_428a94_source_in_place": (
            "bootloader_spotmgr_transition_sequence_7b_428a94_source_in_place",
            "Compiled BSD-3-Clause Apollo510 SPOT-manager transition sequence 7b at its authenticated stock entry",
        ),
        "opaque_before_open_cfw_bootloader_spotmgr_load_factory_trims_429da4_source_in_place": (
            "bootloader_opaque_between_spotmgr_transition_7b_and_factory_trims_428ba8_429da4",
            "Authenticated retained literal, table, and alignment bytes between SPOT-manager transition 7b and the factory-trim loader",
        ),
        "open_cfw_bootloader_spotmgr_load_factory_trims_429da4_source_in_place": (
            "bootloader_spotmgr_load_factory_trims_429da4_source_in_place",
            "Compiled MIT indexed SPOT-manager factory-trim loader at its authenticated stock entry",
        ),
        "opaque_before_open_cfw_bootloader_spotmgr_ensure_factory_trims_42a036_source_in_place": (
            "bootloader_opaque_between_factory_trims_and_ensure_429df6_42a036",
            "Authenticated retained literal, table, and alignment bytes between the factory-trim loader and readiness wrapper",
        ),
        "open_cfw_bootloader_spotmgr_ensure_factory_trims_42a036_source_in_place": (
            "bootloader_spotmgr_ensure_factory_trims_42a036_source_in_place",
            "Compiled MIT guarded SPOT-manager factory-trim readiness wrapper at its authenticated stock entry",
        ),
        "open_cfw_bootloader_spotmgr_timer_irq_service_42a04a_source_in_place": (
            "bootloader_spotmgr_timer_irq_service_42a04a_source_in_place",
            "Compiled BSD-3-Clause Apollo510 SPOT-manager timer interrupt service with exact critical-state restore",
        ),
        "opaque_before_open_cfw_bootloader_spotmgr_buck_deepsleep_state_42a08c_source_in_place": (
            "bootloader_opaque_between_spotmgr_timer_irq_and_buck_classifier_42a078_42a08c",
            "Authenticated retained literal and alignment bytes between the SPOT-manager timer interrupt service and SIMOBUCK classifier",
        ),
        "open_cfw_bootloader_spotmgr_buck_deepsleep_state_42a08c_source_in_place": (
            "bootloader_spotmgr_buck_deepsleep_state_42a08c_source_in_place",
            "Compiled BSD-3-Clause Apollo510 SPOT-manager SIMOBUCK deep-sleep state classifier at its authenticated stock entry",
        ),
        "open_cfw_bootloader_spotmgr_internal_power_domain_42a19c_source_in_place": (
            "bootloader_spotmgr_internal_power_domain_42a19c_source_in_place",
            "Compiled BSD-3-Clause Apollo510 SPOT-manager HP-to-deep-sleep transition marker at its authenticated stock entry",
        ),
        "opaque_before_open_cfw_bootloader_spotmgr_power_ton_adjust_42a1bc_source_in_place": (
            "bootloader_opaque_between_spotmgr_internal_domain_and_ton_adjust_42a1b2_42a1bc",
            "Authenticated retained literal and alignment bytes between the SPOT-manager internal-domain marker and Ton-trim selector",
        ),
        "open_cfw_bootloader_spotmgr_power_ton_adjust_42a1bc_source_in_place": (
            "bootloader_spotmgr_power_ton_adjust_42a1bc_source_in_place",
            "Compiled BSD-3-Clause Apollo510 SPOT-manager VDDC/VDDF Ton-trim selector at its authenticated stock entry",
        ),
        "opaque_before_open_cfw_bootloader_spotmgr_state_transition_sequence_42a2b4_source_in_place": (
            "bootloader_opaque_between_spotmgr_ton_adjust_and_state_sequence_42a2a4_42a2b4",
            "Authenticated retained literal and alignment bytes between the SPOT-manager Ton-trim selector and state-transition selector",
        ),
        "open_cfw_bootloader_spotmgr_state_transition_sequence_42a2b4_source_in_place": (
            "bootloader_spotmgr_state_transition_sequence_42a2b4_source_in_place",
            "Compiled BSD-3-Clause Apollo510 SPOT-manager power-state transition-sequence selector at its authenticated stock entry",
        ),
        "open_cfw_bootloader_spotmgr_temperature_transition_separate_42a43a_source_in_place": (
            "bootloader_spotmgr_temperature_transition_separate_42a43a_source_in_place",
            "Compiled BSD-3-Clause Apollo510 SPOT-manager stepwise temperature-transition dispatcher at its authenticated stock entry",
        ),
        "open_cfw_bootloader_spotmgr_power_trims_update_42a4bc_source_in_place": (
            "bootloader_spotmgr_power_trims_update_42a4bc_source_in_place",
            "Compiled BSD-3-Clause Apollo510 SPOT-manager power and Ton trim transition router at its authenticated stock entry",
        ),
        "opaque_before_open_cfw_bootloader_spotmgr_power_state_determine_42a550_source_in_place": (
            "bootloader_opaque_between_spotmgr_power_trims_and_power_state_42a546_42a550",
            "Authenticated retained literal and alignment bytes between the SPOT-manager trim router and power-state classifier",
        ),
        "open_cfw_bootloader_spotmgr_power_state_determine_42a550_source_in_place": (
            "bootloader_spotmgr_power_state_determine_42a550_source_in_place",
            "Compiled BSD-3-Clause Apollo510 SPOT-manager power and Ton state classifier at its authenticated stock entry",
        ),
        "opaque_before_open_cfw_bootloader_spotmgr_power_state_update_42a878_source_in_place": (
            "bootloader_opaque_between_spotmgr_power_state_classifier_and_update_42a85e_42a878",
            "Authenticated shared literal and alignment bytes before the SPOT-manager stimulus update entry",
        ),
        "open_cfw_bootloader_spotmgr_power_state_update_42a878_source_in_place": (
            "bootloader_spotmgr_power_state_update_42a878_source_in_place",
            "Compiled BSD-3-Clause Apollo510 SPOT-manager power-state stimulus update pipeline at its authenticated dispatch entry",
        ),
        "opaque_before_open_cfw_bootloader_spotmgr_profile_apply_42ab7c_source_in_place": (
            "bootloader_opaque_between_spotmgr_update_and_profile_apply_42ab6e_42ab7c",
            "Authenticated padding and shared literal words between the SPOT-manager update and profile entries",
        ),
        "open_cfw_bootloader_spotmgr_profile_apply_42ab7c_source_in_place": (
            "bootloader_spotmgr_profile_apply_42ab7c_source_in_place",
            "Compiled BSD-3-Clause Apollo510 SPOT-manager profile-to-register field application at its authenticated dispatch entry",
        ),
        "opaque_before_open_cfw_bootloader_spotmgr_init_42abbc_source_in_place": (
            "bootloader_opaque_between_spotmgr_profile_apply_and_init_42abb2_42abbc",
            "Authenticated shared literals and alignment between the SPOT-manager profile and initialization entries",
        ),
        "open_cfw_bootloader_spotmgr_init_42abbc_source_in_place": (
            "bootloader_spotmgr_init_42abbc_source_in_place",
            "Compiled BSD-3-Clause Apollo510 SPOT-manager initialization and trim-load pipeline at its authenticated dispatch entry",
        ),
        "opaque_before_open_cfw_bootloader_spotmgr_temperature_init_42ac54_source_in_place": (
            "bootloader_opaque_between_spotmgr_init_and_temperature_init_42ac4e_42ac54",
            "Authenticated alignment between the SPOT-manager initialization and temperature-monitor entries",
        ),
        "open_cfw_bootloader_spotmgr_temperature_init_42ac54_source_in_place": (
            "bootloader_spotmgr_temperature_init_42ac54_source_in_place",
            "Compiled BSD-3-Clause Apollo510 SPOT-manager temperature-monitor initialization at its authenticated dispatch entry",
        ),
        "opaque_before_open_cfw_bootloader_spotmgr_temperature_range_42ad40_source_in_place": (
            "bootloader_opaque_between_spotmgr_temperature_init_and_range_42aca4_42ad40",
            "Authenticated SPOT-manager shared literals and alignment before the temperature range classifier",
        ),
        "open_cfw_bootloader_spotmgr_temperature_range_42ad40_source_in_place": (
            "bootloader_spotmgr_temperature_range_42ad40_source_in_place",
            "Compiled BSD-3-Clause Apollo510 SPOT-manager hard-float temperature range classifier at its authenticated stock entry",
        ),
        "open_cfw_bootloader_spotmgr_trim_enable_42adb8_source_in_place": (
            "bootloader_spotmgr_trim_enable_42adb8_source_in_place",
            "Compiled BSD-3-Clause Apollo510 SPOT-manager trim enable and 10-bit headroom update at its authenticated stock entry",
        ),
        "open_cfw_bootloader_spotmgr_profile_trim_42ae24_source_in_place": (
            "bootloader_spotmgr_profile_trim_42ae24_source_in_place",
            "Compiled BSD-3-Clause Apollo510 SPOT-manager profile trim field update at its authenticated stock entry",
        ),
        "open_cfw_bootloader_spotmgr_trim_restore_42ae6c_source_in_place": (
            "bootloader_spotmgr_trim_restore_42ae6c_source_in_place",
            "Compiled BSD-3-Clause Apollo510 SPOT-manager gated trim restore at its authenticated stock entry",
        ),
        "open_cfw_bootloader_spotmgr_trim_commit_42ae9c_source_in_place": (
            "bootloader_spotmgr_trim_commit_42ae9c_source_in_place",
            "Compiled BSD-3-Clause Apollo510 SPOT-manager critical trim commit with complete PRIMASK restore at its authenticated stock entry",
        ),
        "opaque_before_open_cfw_bootloader_spotmgr_buck_deepsleep_scan_42aef0_source_in_place": (
            "bootloader_spotmgr_trim_commit_scan_gap_42aeec_42aef0",
            "Authenticated four-byte literal/alignment gap before the second SPOT-manager deep-sleep eligibility scan",
        ),
        "open_cfw_bootloader_spotmgr_buck_deepsleep_scan_42aef0_source_in_place": (
            "bootloader_spotmgr_buck_deepsleep_scan_42aef0_source_in_place",
            "Compiled BSD-3-Clause Apollo510 SPOT-manager deep-sleep eligibility scan at its authenticated stock entry",
        ),
        "opaque_before_open_cfw_bootloader_spotmgr_state_transition_effects_42b014_source_in_place": (
            "bootloader_spotmgr_buck_scan_transition_effects_gap_42b010_42b014",
            "Authenticated four-byte literal/alignment gap before the SPOT-manager state-transition side-effect leaf",
        ),
        "open_cfw_bootloader_spotmgr_state_transition_effects_42b014_source_in_place": (
            "bootloader_spotmgr_state_transition_effects_42b014_source_in_place",
            "Compiled BSD-3-Clause Apollo510 SPOT-manager state-transition side effects at the authenticated stock entry",
        ),
        "opaque_before_open_cfw_bootloader_spotmgr_power_transition_trims_42b06c_source_in_place": (
            "bootloader_spotmgr_transition_effects_power_trim_gap_42b068_42b06c",
            "Authenticated four-byte literal/alignment gap before the SPOT-manager power-transition trim transaction",
        ),
        "open_cfw_bootloader_spotmgr_power_transition_trims_42b06c_source_in_place": (
            "bootloader_spotmgr_power_transition_trims_42b06c_source_in_place",
            "Compiled BSD-3-Clause Apollo510 SPOT-manager power-transition trim transaction at the authenticated stock entry",
        ),
        "open_cfw_bootloader_spotmgr_state_transition_42b294_source_in_place": (
            "bootloader_spotmgr_state_transition_42b294_source_in_place",
            "Compiled MIT clean-room SPOT-manager state-transition, trim, and register orchestrator",
        ),
        "opaque_before_open_cfw_bootloader_hw_state_decode_42b6b8_source_in_place": (
            "bootloader_spotmgr_state_transition_decode_gap_42b69c_42b6b8",
            "Authenticated 28-byte literal and alignment gap before the hardware-state decoder",
        ),
        "open_cfw_bootloader_hw_state_decode_42b6b8_source_in_place": (
            "bootloader_hw_state_decode_42b6b8_source_in_place",
            "Compiled MIT clean-room hardware-state nibble composer and dual-output classifier",
        ),
        "opaque_before_open_cfw_bootloader_hw_state_compose_42bdf0_source_in_place": (
            "bootloader_opaque_between_hw_state_decode_and_compose_42b9ba_42bdf0",
            "Authenticated retained code and data between the hardware-state decoder and stored-entry composer",
        ),
        "open_cfw_bootloader_hw_state_compose_42bdf0_source_in_place": (
            "bootloader_hw_state_compose_42bdf0_source_in_place",
            "Compiled MIT clean-room hardware-state composer at its authenticated stored-pointer entry",
        ),
        "opaque_before_open_cfw_bootloader_hardware_readiness_gate_42bf54_source_in_place": (
            "bootloader_hw_state_compose_readiness_gap_42bf4e_42bf54",
            "Authenticated six-byte literal/alignment gap between the hardware-state composer and hardware-readiness gate",
        ),
        "open_cfw_bootloader_hardware_readiness_gate_42bf54_source_in_place": (
            "bootloader_hardware_readiness_gate_42bf54_source_in_place",
            "Compiled MIT clean-room hardware-readiness gate at its authenticated stored-pointer entry",
        ),
        "opaque_before_open_cfw_bootloader_hw_status_route_42c034_source_in_place": (
            "bootloader_opaque_between_readiness_gate_and_hw_status_route_42bfa4_42c034",
            "Authenticated retained code and data between the hardware-readiness gate and hardware-status route helper",
        ),
        "open_cfw_bootloader_hw_status_route_42c034_source_in_place": (
            "bootloader_hw_status_route_42c034_source_in_place",
            "Compiled MIT clean-room hardware status-route selector at its authenticated stock entry",
        ),
        "open_cfw_bootloader_hw_error_classify_42c076_source_in_place": (
            "bootloader_hw_error_classify_42c076_source_in_place",
            "Compiled MIT clean-room hardware error-precedence classifier at its authenticated stock entry",
        ),
        "open_cfw_bootloader_hw_event_apply_42c0b2_source_in_place": (
            "bootloader_hw_event_apply_42c0b2_source_in_place",
            "Compiled MIT clean-room retained hardware-event acknowledgement and timed-pulse service",
        ),
        "open_cfw_bootloader_rounded_divider_42c222_source_in_place": (
            "bootloader_rounded_divider_42c222_source_in_place",
            "Compiled MIT clean-room rounded integer divider at its authenticated stock entry",
        ),
        "open_cfw_bootloader_is_power_of_two_42c256_source_in_place": (
            "bootloader_is_power_of_two_42c256_source_in_place",
            "Compiled MIT clean-room nonzero power-of-two predicate at its authenticated stock entry",
        ),
        "open_cfw_bootloader_hw_clock_encode_42c26a_source_in_place": (
            "bootloader_hw_clock_encode_42c26a_source_in_place",
            "Compiled MIT clean-room hardware clock-divider search and register-field encoder",
        ),
        "open_cfw_bootloader_cmdq_adapter_init_42c3e2_source_in_place": (
            "bootloader_cmdq_adapter_init_42c3e2_source_in_place",
            "Compiled MIT clean-room command-queue adapter initialization at its authenticated stock entry",
        ),
        "open_cfw_bootloader_cmdq_adapter_enable_42c420_source_in_place": (
            "bootloader_cmdq_adapter_enable_42c420_source_in_place",
            "Compiled MIT clean-room command-queue adapter enable service at its authenticated stock entry",
        ),
        "open_cfw_bootloader_cmdq_adapter_disable_42c44e_source_in_place": (
            "bootloader_cmdq_adapter_disable_42c44e_source_in_place",
            "Compiled MIT clean-room command-queue adapter disable service at its authenticated stock entry",
        ),
        "open_cfw_bootloader_hw_descriptor_publish_42c45a_source_in_place": (
            "bootloader_hw_descriptor_publish_42c45a_source_in_place",
            "Compiled MIT clean-room ring-descriptor register publisher at its authenticated stock entry",
        ),
        "open_cfw_bootloader_hw_context_claim_42c4c6_source_in_place": (
            "bootloader_hw_context_claim_42c4c6_source_in_place",
            "Compiled MIT clean-room hardware-context ownership claim at its authenticated stock entry",
        ),
        "open_cfw_bootloader_hw_context_enable_42c538_source_in_place": (
            "bootloader_hw_context_enable_42c538_source_in_place",
            "Compiled MIT clean-room hardware-context activation and rollback service at its authenticated stock entry",
        ),
        "open_cfw_bootloader_hw_interrupt_enable_42c63a_source_in_place": (
            "bootloader_hw_interrupt_enable_42c63a_source_in_place",
            "Compiled MIT clean-room validated hardware interrupt-enable helper at its authenticated stock entry",
        ),
        "open_cfw_bootloader_hw_interrupt_status_get_42c672_source_in_place": (
            "bootloader_hw_interrupt_status_get_42c672_source_in_place",
            "Compiled MIT clean-room hardware interrupt-status query helper at its authenticated stock entry",
        ),
        "open_cfw_bootloader_hw_interrupt_clear_42c6b6_source_in_place": (
            "bootloader_hw_interrupt_clear_42c6b6_source_in_place",
            "Compiled MIT clean-room hardware interrupt-clear helper at its authenticated stock entry",
        ),
        "opaque_before_open_cfw_bootloader_hw_event_service_42c6f8_source_in_place": (
            "bootloader_opaque_between_interrupt_clear_and_event_service_42c6e4_42c6f8",
            "Authenticated retained alignment and data between the interrupt-clear helper and event service",
        ),
        "open_cfw_bootloader_hw_event_service_42c6f8_source_in_place": (
            "bootloader_hw_event_service_42c6f8_source_in_place",
            "Compiled MIT clean-room hardware event, descriptor, callback, and command-queue service",
        ),
        "opaque_before_open_cfw_bootloader_hw_config_transaction_42c988_source_in_place": (
            "bootloader_opaque_between_event_service_and_config_transaction_42c980_42c988",
            "Authenticated retained alignment and data between the event service and configuration transaction",
        ),
        "open_cfw_bootloader_hw_config_transaction_42c988_source_in_place": (
            "bootloader_hw_config_transaction_42c988_source_in_place",
            "Compiled MIT clean-room hardware configuration save, restore, and resource transaction",
        ),
        "open_cfw_bootloader_hw_instance_configure_42cc34_source_in_place": (
            "bootloader_hw_instance_configure_42cc34_source_in_place",
            "Compiled MIT clean-room hardware instance validation and mode-specific configuration service",
        ),
        "opaque_before_open_cfw_bootloader_state_adjust_42cdf8_source_in_place": (
            "bootloader_opaque_between_instance_configure_and_state_adjust_42cdb0_42cdf8",
            "Authenticated retained data between the instance configurator and state adjustment service",
        ),
        "open_cfw_bootloader_state_adjust_42cdf8_source_in_place": (
            "bootloader_state_adjust_42cdf8_source_in_place",
            "Compiled MIT clean-room bounded seven-bit state adjustment service at its authenticated stock entry",
        ),
        "open_cfw_bootloader_state_update_critical_42cea4_source_in_place": (
            "bootloader_state_update_critical_42cea4_source_in_place",
            "Compiled MIT clean-room critical state-update service at its authenticated stock entry",
        ),
        "open_cfw_bootloader_state_range_update_42ced8_source_in_place": (
            "bootloader_state_range_update_42ced8_source_in_place",
            "Compiled MIT clean-room floating-point range update service at its authenticated stock entry",
        ),
        "open_cfw_bootloader_state_event_zero_42cfe0_source_in_place": (
            "bootloader_state_event_zero_42cfe0_source_in_place",
            "Compiled MIT clean-room sixteen-channel state/event fault classifier",
        ),
        "opaque_before_open_cfw_bootloader_state_event_one_value_42d104_source_in_place": (
            "bootloader_state_event_zero_state_one_gap_42d0f2_42d104",
            "Authenticated retained state providers before the state-one tuning service",
        ),
        "open_cfw_bootloader_state_event_one_value_42d104_source_in_place": (
            "bootloader_state_event_one_value_42d104_source_in_place",
            "Compiled MIT clean-room state-one register tuning and restoration service",
        ),
        "open_cfw_bootloader_state_register_initialize_42d3bc_source_in_place": (
            "bootloader_state_register_initialize_42d3bc_source_in_place",
            "Compiled MIT clean-room state-transition register initialization and restoration service",
        ),
        "open_cfw_bootloader_state_event_dispatch_42d562_source_in_place": (
            "bootloader_state_event_dispatch_42d562_source_in_place",
            "Compiled MIT clean-room byte-event state dispatcher at its authenticated stock entry",
        ),
        "opaque_before_open_cfw_bootloader_stream_mode_42d84c_source_in_place": (
            "bootloader_opaque_between_state_dispatch_and_stream_mode_42d5c2_42d84c",
            "Authenticated retained code and data between the state dispatcher and stream-mode primitive",
        ),
        "open_cfw_bootloader_stream_mode_42d84c_source_in_place": (
            "bootloader_stream_mode_42d84c_source_in_place",
            "Compiled MIT clean-room stream-mode selection primitive at its authenticated stock entry",
        ),
        "open_cfw_bootloader_runtime_context_get_42d88a_source_in_place": (
            "bootloader_runtime_context_get_42d88a_source_in_place",
            "Compiled MIT clean-room runtime-context pointer getter at its authenticated stock entry",
        ),
        "open_cfw_bootloader_dfu_image_crc_check_42d890_source_in_place": (
            "bootloader_dfu_image_crc_check_42d890_source_in_place",
            "Compiled MIT clean-room DFU image open/read/CRC/close verifier at its authenticated stock entry",
        ),
        "open_cfw_bootloader_chunked_indirect_visit_42d9f0_source_in_place": (
            "bootloader_chunked_indirect_visit_42d9f0_source_in_place",
            "Compiled MIT clean-room chunked indirect traversal service at its authenticated stock entry",
        ),
        "open_cfw_bootloader_chunked_source_compare_42da1e_source_in_place": (
            "bootloader_chunked_source_compare_42da1e_source_in_place",
            "Compiled MIT clean-room bounded 4 KiB source-reader comparison service",
        ),
        "opaque_before_open_cfw_bootloader_dfu_payload_program_42dae8_source_in_place": (
            "bootloader_chunk_compare_payload_program_gap_42dad0_42dae8",
            "Authenticated twenty-four-byte literal/alignment gap before the DFU payload programmer",
        ),
        "open_cfw_bootloader_dfu_payload_program_42dae8_source_in_place": (
            "bootloader_dfu_payload_program_42dae8_source_in_place",
            "Compiled MIT clean-room chunked DFU payload programmer and verifier",
        ),
        "open_cfw_bootloader_vector_handoff_42dc90_source_in_place": (
            "bootloader_vector_handoff_42dc90_source_in_place",
            "Compiled MIT clean-room Cortex-M vector and stack handoff primitive at its authenticated stock entry",
        ),
        "open_cfw_bootloader_runtime_context_publish_42dca2_source_in_place": (
            "bootloader_runtime_context_publish_42dca2_source_in_place",
            "Compiled MIT clean-room queued runtime-context publisher at its authenticated stock entry",
        ),
        "open_cfw_bootloader_control_orchestrator_42dd14_source_in_place": (
            "bootloader_control_orchestrator_42dd14_source_in_place",
            "Compiled MIT clean-room non-returning event/control orchestrator at its authenticated stored-pointer entry",
        ),
        "open_cfw_bootloader_runtime_context_wrapper_42dd68_source_in_place": (
            "bootloader_runtime_context_wrapper_42dd68_source_in_place",
            "Compiled MIT clean-room runtime-context provider wrapper at its authenticated stock entry",
        ),
        "open_cfw_bootloader_runtime_queue_context_init_42dd70_source_in_place": (
            "bootloader_runtime_queue_context_init_42dd70_source_in_place",
            "Compiled MIT clean-room retained queue-context initializer at its authenticated stock entry",
        ),
        "open_cfw_bootloader_noop_callback_42dd98_source_in_place": (
            "bootloader_noop_callback_42dd98_source_in_place",
            "Compiled MIT clean-room no-op callback at the authenticated stock entry",
        ),
        "open_cfw_bootloader_control_one_wrapper_42dd9a_source_in_place": (
            "bootloader_control_one_wrapper_42dd9a_source_in_place",
            "Compiled MIT clean-room constant-one control wrapper at its authenticated stock entry",
        ),
        "open_cfw_bootloader_control_two_wrapper_42dda4_source_in_place": (
            "bootloader_control_two_wrapper_42dda4_source_in_place",
            "Compiled MIT clean-room second constant-one control wrapper at its authenticated stock entry",
        ),
        "open_cfw_bootloader_runtime_action_context_init_42ddae_source_in_place": (
            "bootloader_runtime_action_context_init_42ddae_source_in_place",
            "Compiled MIT clean-room retained action-context initializer at its authenticated stock entry",
        ),
        "open_cfw_bootloader_runtime_action_context_deinit_42ddda_source_in_place": (
            "bootloader_runtime_action_context_deinit_42ddda_source_in_place",
            "Compiled MIT clean-room guarded action-context teardown at its authenticated stock entry",
        ),
        "open_cfw_bootloader_runtime_enable_sequence_42ddf2_source_in_place": (
            "bootloader_runtime_enable_sequence_42ddf2_source_in_place",
            "Compiled MIT clean-room critical runtime enable sequence at its authenticated stock entry",
        ),
        "open_cfw_bootloader_critical_dispatch_transaction_42de0e_source_in_place": (
            "bootloader_critical_dispatch_transaction_42de0e_source_in_place",
            "Compiled MIT clean-room critical four-word dispatch transaction at its authenticated stock entry",
        ),
        "open_cfw_bootloader_dfu_service_task_42de58_source_in_place": (
            "bootloader_dfu_service_task_42de58_source_in_place",
            "Compiled MIT clean-room DFU queue service, image dispatch, and vector handoff task",
        ),
        "opaque_before_open_cfw_bootloader_control_bits_dispatch_42e1c4_source_in_place": (
            "bootloader_dfu_service_control_bits_gap_42e104_42e1c4",
            "Authenticated retained literal and alignment data after the DFU service task",
        ),
        "open_cfw_bootloader_control_bits_dispatch_42e1c4_source_in_place": (
            "bootloader_control_bits_dispatch_42e1c4_source_in_place",
            "Compiled MIT clean-room bit-22/bit-23 control dispatcher at its authenticated stock entry",
        ),
        "open_cfw_bootloader_control_terminal_loop_42e1da_source_in_place": (
            "bootloader_control_terminal_loop_42e1da_source_in_place",
            "Compiled MIT clean-room non-returning terminal notification loop at its authenticated stock entry",
        ),
        "open_cfw_bootloader_crc32_table_42e1ec_source_in_place": (
            "bootloader_crc32_table_42e1ec_source_in_place",
            "Compiled MIT clean-room table-driven CRC32 primitive at its authenticated stock entry",
        ),
        "opaque_before_open_cfw_bootloader_retained_state_probe_42e224_source_in_place": (
            "bootloader_crc32_state_probe_gap_42e220_42e224",
            "Authenticated retained alignment bytes between CRC32 and the source-owned state probe",
        ),
        "open_cfw_bootloader_retained_state_probe_42e224_source_in_place": (
            "bootloader_retained_state_probe_42e224_source_in_place",
            "Compiled MIT clean-room retained-state probe at its authenticated stock entry",
        ),
        "open_cfw_bootloader_event_flags_init_42e254_source_in_place": (
            "bootloader_event_flags_init_42e254_source_in_place",
            "Compiled MIT clean-room event-flags initializer at its authenticated stock entry",
        ),
        "open_cfw_bootloader_noop_callback_42e276_source_in_place": (
            "bootloader_noop_callback_42e276_source_in_place",
            "Compiled MIT clean-room no-op callback at the authenticated stock entry",
        ),
        "open_cfw_bootloader_event_runtime_setup_42e278_source_in_place": (
            "bootloader_event_runtime_setup_42e278_source_in_place",
            "Compiled MIT clean-room event-runtime setup wrapper at its authenticated stock entry",
        ),
        "open_cfw_bootloader_event_callback_dispatch_42e284_source_in_place": (
            "bootloader_event_callback_dispatch_42e284_source_in_place",
            "Compiled MIT clean-room retained callback dispatcher at its authenticated stock entry",
        ),
        "open_cfw_bootloader_event_wait_mask_42e2a2_source_in_place": (
            "bootloader_event_wait_mask_42e2a2_source_in_place",
            "Compiled MIT clean-room event wait-mask service at its authenticated stock entry",
        ),
        "open_cfw_bootloader_event_wait_one_wrapper_42e2ea_source_in_place": (
            "bootloader_event_wait_one_wrapper_42e2ea_source_in_place",
            "Compiled MIT clean-room event wait-one wrapper at its authenticated stock entry",
        ),
        "open_cfw_bootloader_event_service_loop_42e2f8_source_in_place": (
            "bootloader_event_service_loop_42e2f8_source_in_place",
            "Compiled MIT clean-room retained-event initialization and bounded-wait service loop at its authenticated stored-pointer entry",
        ),
        "open_cfw_bootloader_noop_callback_42e39a_source_in_place": (
            "bootloader_noop_callback_42e39a_source_in_place",
            "Compiled MIT clean-room no-op callback at the authenticated stock entry",
        ),
        "open_cfw_bootloader_guard_context_init_42e39c_source_in_place": (
            "bootloader_guard_context_init_42e39c_source_in_place",
            "Compiled MIT clean-room guarded-context initializer at its authenticated stock entry",
        ),
        "open_cfw_bootloader_guarded_context_teardown_42e3ca_source_in_place": (
            "bootloader_guarded_context_teardown_42e3ca_source_in_place",
            "Compiled MIT clean-room guarded context teardown at its authenticated stock entry",
        ),
        "open_cfw_bootloader_control_one_wait_42e3e0_source_in_place": (
            "bootloader_control_one_wait_42e3e0_source_in_place",
            "Compiled MIT clean-room event wait/log control at its authenticated stock entry",
        ),
        "open_cfw_bootloader_control_two_publish_42e412_source_in_place": (
            "bootloader_control_two_publish_42e412_source_in_place",
            "Compiled MIT clean-room event bit-publish control at its authenticated stock entry",
        ),
        "open_cfw_bootloader_event_bit_set_42e444_source_in_place": (
            "bootloader_event_bit_set_42e444_source_in_place",
            "Compiled MIT clean-room event-bit publisher at its authenticated stock entry",
        ),
        "opaque_before_open_cfw_bootloader_aligned_guarded_dispatch_42e4a0_source_in_place": (
            "bootloader_opaque_between_event_bit_and_guarded_dispatch_42e458_42e4a0",
            "Authenticated retained code and data between the event-bit publisher and guarded dispatcher",
        ),
        "open_cfw_bootloader_aligned_guarded_dispatch_42e4a0_source_in_place": (
            "bootloader_aligned_guarded_dispatch_42e4a0_source_in_place",
            "Compiled MIT clean-room aligned guarded dispatcher at its authenticated stock entry",
        ),
        "open_cfw_bootloader_alignment_dispatch_42e4f4_source_in_place": (
            "bootloader_alignment_dispatch_42e4f4_source_in_place",
            "Compiled MIT clean-room alignment-gated runtime dispatcher at its authenticated stock entry",
        ),
        "opaque_before_open_cfw_bootloader_terminal_mode_42e514_source_in_place": (
            "bootloader_alignment_dispatch_terminal_mode_gap_42e50e_42e514",
            "Authenticated six-byte literal/alignment gap before the terminal-mode primitive",
        ),
        "open_cfw_bootloader_terminal_mode_42e514_source_in_place": (
            "bootloader_terminal_mode_42e514_source_in_place",
            "Compiled MIT clean-room terminal-mode control primitive at its authenticated stock entry",
        ),
        "opaque_before_open_cfw_bootloader_event_runtime_init_42e53c_source_in_place": (
            "bootloader_terminal_mode_event_runtime_gap_42e534_42e53c",
            "Authenticated retained literal/alignment bytes before event-runtime initialization",
        ),
        "open_cfw_bootloader_event_runtime_init_42e53c_source_in_place": (
            "bootloader_event_runtime_init_42e53c_source_in_place",
            "Compiled MIT clean-room event-object and task initialization service at its authenticated stock entry",
        ),
        "opaque_before_open_cfw_bootloader_event_callback_loop_42e644_source_in_place": (
            "bootloader_event_runtime_callback_loop_gap_42e642_42e644",
            "Authenticated two-byte alignment between event-runtime initialization and callback dispatch",
        ),
        "open_cfw_bootloader_event_callback_loop_42e644_source_in_place": (
            "bootloader_event_callback_loop_42e644_source_in_place",
            "Compiled MIT clean-room queue-driven callback loop at its authenticated stock entry",
        ),
        "open_cfw_bootloader_event_callback_enqueue_42e686_source_in_place": (
            "bootloader_event_callback_enqueue_42e686_source_in_place",
            "Compiled MIT clean-room callback enqueue service at its authenticated stock entry",
        ),
        "opaque_before_open_cfw_bootloader_guarded_call_cleanup_42e8a4_source_in_place": (
            "bootloader_opaque_between_event_enqueue_and_guarded_call_42e6f2_42e8a4",
            "Authenticated retained code and data between callback enqueue and guarded indirect-call cleanup services",
        ),
        "open_cfw_bootloader_guarded_call_cleanup_42e8a4_source_in_place": (
            "bootloader_guarded_call_cleanup_42e8a4_source_in_place",
            "Compiled MIT clean-room guarded indirect-call and ordered cleanup service at its authenticated stock entry",
        ),
        "opaque_before_open_cfw_bootloader_hw_context_initialize_42e8d0_source_in_place": (
            "bootloader_guarded_call_context_initialize_gap_42e8c2_42e8d0",
            "Authenticated fourteen-byte literal/alignment gap before the hardware-context initializer",
        ),
        "open_cfw_bootloader_hw_context_initialize_42e8d0_source_in_place": (
            "bootloader_hw_context_initialize_42e8d0_source_in_place",
            "Compiled MIT clean-room hardware-context slot and calibration-profile initializer",
        ),
        "open_cfw_bootloader_hw_handle_reset_42ea32_source_in_place": (
            "bootloader_hw_handle_reset_42ea32_source_in_place",
            "Compiled MIT clean-room hardware-handle reset service at its authenticated stock entry",
        ),
        "open_cfw_bootloader_hw_profile_apply_42ea68_source_in_place": (
            "bootloader_hw_profile_apply_42ea68_source_in_place",
            "Compiled MIT clean-room validated seven-field hardware-profile publisher",
        ),
        "open_cfw_bootloader_hw_channel_config_42eaf6_source_in_place": (
            "bootloader_hw_channel_config_42eaf6_source_in_place",
            "Compiled MIT clean-room bounded channel configuration encoder at its authenticated stock entry",
        ),
        "opaque_before_open_cfw_bootloader_hw_handle_configure_42eb74_source_in_place": (
            "bootloader_opaque_between_hw_channel_config_and_handle_configure_42eb74",
            "Authenticated zero-length boundary marker between adjacent channel and handle configuration services",
        ),
        "open_cfw_bootloader_hw_handle_configure_42eb74_source_in_place": (
            "bootloader_hw_handle_configure_42eb74_source_in_place",
            "Compiled MIT clean-room hardware-handle configuration encoder at its authenticated stock entry",
        ),
        "open_cfw_bootloader_hw_handle_enable_42ebaa_source_in_place": (
            "bootloader_hw_handle_enable_42ebaa_source_in_place",
            "Compiled MIT clean-room hardware-handle ready-gated enable service at its authenticated stock entry",
        ),
        "open_cfw_bootloader_hw_handle_disable_42ebe2_source_in_place": (
            "bootloader_hw_handle_disable_42ebe2_source_in_place",
            "Compiled MIT clean-room hardware-handle disable service at its authenticated stock entry",
        ),
        "open_cfw_bootloader_hw_config_dispatch_42ec0c_source_in_place": (
            "bootloader_hw_config_dispatch_42ec0c_source_in_place",
            "Compiled MIT clean-room hardware configuration operation dispatcher at its authenticated stock entry",
        ),
        "opaque_before_open_cfw_bootloader_hw_handle_activate_42ed60_source_in_place": (
            "bootloader_zero_boundary_hw_config_dispatch_to_activate_42ed60",
            "Authenticated zero-length boundary marker between adjacent hardware configuration and activation services",
        ),
        "open_cfw_bootloader_hw_handle_activate_42ed60_source_in_place": (
            "bootloader_hw_handle_activate_42ed60_source_in_place",
            "Compiled MIT clean-room idempotent hardware-handle activation service at its authenticated stock entry",
        ),
        "open_cfw_bootloader_hardware_channel_normalize_42eda0_source_in_place": (
            "bootloader_hardware_channel_normalize_42eda0_source_in_place",
            "Compiled MIT clean-room hardware-channel control normalization at its authenticated stock entry",
        ),
        "opaque_before_open_cfw_bootloader_hw_channel_normalize_42ee00_source_in_place": (
            "bootloader_hardware_channel_normalize_gap_42edf6_42ee00",
            "Authenticated retained literal/alignment bytes between adjacent normalization services",
        ),
        "open_cfw_bootloader_hw_channel_normalize_42ee00_source_in_place": (
            "bootloader_hw_channel_normalize_42ee00_source_in_place",
            "Compiled MIT clean-room calibrated packed-channel normalization service at its authenticated stock entry",
        ),
        "opaque_before_open_cfw_bootloader_hw_channel_enumerate_42ee70_source_in_place": (
            "bootloader_channel_normalize_enumerate_gap_42ee6c_42ee70",
            "Authenticated four-byte literal/alignment gap between channel normalization and enumeration services",
        ),
        "open_cfw_bootloader_hw_channel_enumerate_42ee70_source_in_place": (
            "bootloader_hw_channel_enumerate_42ee70_source_in_place",
            "Compiled MIT clean-room bounded hardware/input channel enumeration service at its authenticated stock entry",
        ),
        "opaque_before_open_cfw_bootloader_hw_handle_command_42eff4_source_in_place": (
            "bootloader_zero_boundary_hw_channel_enumerate_to_command_42eff4",
            "Authenticated zero-length boundary marker between adjacent channel enumeration and command services",
        ),
        "open_cfw_bootloader_hw_handle_command_42eff4_source_in_place": (
            "bootloader_hw_handle_command_42eff4_source_in_place",
            "Compiled MIT clean-room validated hardware-handle command service at its authenticated stock entry",
        ),
        "opaque_before_open_cfw_bootloader_register_profile_transfer_42f020_source_in_place": (
            "bootloader_hw_command_profile_transfer_gap_42f014_42f020",
            "Authenticated retained literal/alignment bytes before register-profile transfer",
        ),
        "open_cfw_bootloader_register_profile_transfer_42f020_source_in_place": (
            "bootloader_register_profile_transfer_42f020_source_in_place",
            "Compiled MIT clean-room validated hardware register-profile capture/apply service",
        ),
        "opaque_before_open_cfw_bootloader_register_power_toggle_42f1c8_source_in_place": (
            "bootloader_profile_transfer_power_toggle_gap_42f14e_42f1c8",
            "Authenticated retained literal table and alignment before register power toggle",
        ),
        "open_cfw_bootloader_register_power_toggle_42f1c8_source_in_place": (
            "bootloader_register_power_toggle_42f1c8_source_in_place",
            "Compiled MIT clean-room register power toggle at its authenticated stock entry",
        ),
        "open_cfw_bootloader_event_value_provider_42f204_source_in_place": (
            "bootloader_event_value_profile_42f204_source_in_place",
            "Compiled MIT clean-room event-value hardware-profile publisher at its authenticated stock entry",
        ),
        "open_cfw_bootloader_hw_register_profile_restore_42f2fa_source_in_place": (
            "bootloader_hw_register_profile_restore_42f2fa_source_in_place",
            "Compiled MIT clean-room hardware register-profile restoration and mode finalization service",
        ),
        "open_cfw_bootloader_event_dispatch_42f38e_source_in_place": (
            "bootloader_event_dispatch_42f38e_source_in_place",
            "Compiled MIT clean-room stored-pointer event dispatcher at its authenticated stock entry",
        ),
        "opaque_before_open_cfw_bootloader_mode_apply_42ff00_source_in_place": (
            "bootloader_opaque_between_event_dispatch_and_mode_apply_42f3da_42ff00",
            "Authenticated retained code and data between the event dispatcher and mode router",
        ),
        "open_cfw_bootloader_mode_apply_42ff00_source_in_place": (
            "bootloader_mode_apply_42ff00_source_in_place",
            "Compiled MIT clean-room mode router and interrupt-safe aggregate bitset service",
        ),
        "open_cfw_bootloader_mode_one_apply_42fff2_source_in_place": (
            "bootloader_mode_one_apply_42fff2_source_in_place",
            "Compiled MIT clean-room constant mode-one adapter at its authenticated stock entry",
        ),
        "opaque_before_open_cfw_bootloader_platform_bringup_430000_source_in_place": (
            "bootloader_mode_one_platform_bringup_gap_42fffe_430000",
            "Authenticated two-byte alignment gap before platform bring-up",
        ),
        "open_cfw_bootloader_platform_bringup_430000_source_in_place": (
            "bootloader_platform_bringup_430000_source_in_place",
            "Compiled MIT clean-room platform bring-up, measurement, and teardown orchestrator",
        ),
        "open_cfw_bootloader_platform_boot_sequence_4301d6_source_in_place": (
            "bootloader_platform_boot_sequence_4301d6_source_in_place",
            "Compiled MIT clean-room platform boot sequence at its authenticated stock entry",
        ),
        "opaque_before_open_cfw_bootloader_nvic_enable_bit_430240_source_in_place": (
            "bootloader_platform_boot_nvic_gap_4301f4_430240",
            "Authenticated retained literal/alignment bytes before the first NVIC enable helper",
        ),
        "open_cfw_bootloader_nvic_enable_bit_430240_source_in_place": (
            "bootloader_nvic_enable_bit_430240_source_in_place",
            "Compiled MIT clean-room signed NVIC interrupt-enable bit publisher at its authenticated stock entry",
        ),
        "open_cfw_bootloader_scb_priority_nibble_43025c_source_in_place": (
            "bootloader_scb_priority_nibble_43025c_source_in_place",
            "Compiled MIT clean-room NVIC and SCB priority-nibble publisher at its authenticated stock entry",
        ),
        "open_cfw_bootloader_descriptor_register_430280_source_in_place": (
            "bootloader_descriptor_register_430280_source_in_place",
            "Compiled MIT clean-room bounded descriptor callback and interrupt registrar",
        ),
        "open_cfw_bootloader_boolean_route_status_4303bc_source_in_place": (
            "bootloader_boolean_route_status_4303bc_source_in_place",
            "Compiled MIT clean-room normalized boolean status route at its authenticated stock entry",
        ),
        "opaque_before_open_cfw_bootloader_nvic_enable_bit_430470_source_in_place": (
            "bootloader_opaque_between_boolean_route_and_nvic_enable_4303de_430470",
            "Authenticated retained code and data between the boolean status route and second NVIC enable helper",
        ),
        "open_cfw_bootloader_nvic_enable_bit_430470_source_in_place": (
            "bootloader_nvic_enable_bit_430470_source_in_place",
            "Compiled MIT clean-room signed NVIC interrupt-enable bit publisher at its second authenticated stock entry",
        ),
        "open_cfw_bootloader_hw_config_retry_43048e_source_in_place": (
            "bootloader_hw_config_retry_43048e_source_in_place",
            "Compiled MIT clean-room bounded hardware-configuration retry and callback setup service",
        ),
        "open_cfw_bootloader_platform_finish_430502_source_in_place": (
            "bootloader_platform_finish_430502_source_in_place",
            "Compiled MIT clean-room eight-slot hardware-context and event-service finalizer",
        ),
        "opaque_before_open_cfw_bootloader_address_validate_430a60_source_in_place": (
            "bootloader_opaque_between_platform_finish_and_address_validate_430610_430a60",
            "Authenticated retained code and data between the platform finalizer and address validator",
        ),
        "open_cfw_bootloader_address_validate_430a60_source_in_place": (
            "bootloader_address_validate_430a60_source_in_place",
            "Compiled MIT clean-room address and length validator at its authenticated stock entry",
        ),
        "open_cfw_bootloader_validated_byte_copy_430a9c_source_in_place": (
            "bootloader_validated_byte_copy_430a9c_source_in_place",
            "Compiled MIT clean-room validated byte-copy wrapper at its authenticated stock entry",
        ),
        "open_cfw_bootloader_validated_word_transfer_430ac4_source_in_place": (
            "bootloader_validated_word_transfer_430ac4_source_in_place",
            "Compiled MIT clean-room validated word-transfer wrapper at its authenticated stock entry",
        ),
        "open_cfw_bootloader_mode_four_wrapper_430aec_source_in_place": (
            "bootloader_mode_four_wrapper_430aec_source_in_place",
            "Compiled MIT clean-room mode-four provider wrapper without authenticated boot ingress",
        ),
        "opaque_before_open_cfw_bootloader_word_transfer_critical_430b10_source_in_place": (
            "bootloader_mode_wrapper_word_transfer_gap_430b0c_430b10",
            "Authenticated four-byte alignment gap before critical word transfer",
        ),
        "open_cfw_bootloader_word_transfer_critical_430b10_source_in_place": (
            "bootloader_word_transfer_critical_430b10_source_in_place",
            "Compiled MIT clean-room critical word-transfer dispatcher at its corrected authenticated extent",
        ),
        "opaque_before_open_cfw_bootloader_platform_services_init_43194c_source_in_place": (
            "bootloader_opaque_between_word_transfer_and_platform_init_430b3c_43194c",
            "Authenticated retained code and data between critical word transfer and platform service initialization",
        ),
        "open_cfw_bootloader_platform_services_init_43194c_source_in_place": (
            "bootloader_platform_services_init_43194c_source_in_place",
            "Compiled MIT clean-room platform-service initializer with authenticated stored ingress",
        ),
        "opaque_before_open_cfw_bootloader_zero_table_431e38_source_in_place": (
            "bootloader_opaque_between_platform_init_and_zero_table_43198a_431e38",
            "Authenticated retained code and data between platform initialization and zero-table service",
        ),
        "open_cfw_bootloader_zero_table_431e38_source_in_place": (
            "bootloader_zero_table_431e38_source_in_place",
            "Compiled MIT clean-room absolute/relative zero-table walker without authenticated boot ingress",
        ),
        "opaque_before_open_cfw_bootloader_vector_table_relocate_432910_source_in_place": (
            "bootloader_opaque_between_zero_table_and_startup_431e70_432910",
            "Authenticated retained code and data between the zero-table walker and Cortex-M startup services",
        ),
        "open_cfw_bootloader_vector_table_relocate_432910_source_in_place": (
            "bootloader_vector_table_relocate_432910_source_in_place",
            "Compiled MIT clean-room VTOR relocation service at its authenticated stock entry",
        ),
        "open_cfw_bootloader_stack_limits_init_43291a_source_in_place": (
            "bootloader_stack_limits_init_43291a_source_in_place",
            "Compiled MIT clean-room MSPLIM/PSPLIM initialization service at its authenticated stock entry",
        ),
        "opaque_before_open_cfw_bootloader_process_stack_init_43293c_source_in_place": (
            "bootloader_startup_literals_43292a_43293c",
            "Authenticated startup stack-limit literal and alignment bytes",
        ),
        "open_cfw_bootloader_process_stack_init_43293c_source_in_place": (
            "bootloader_process_stack_init_43293c_source_in_place",
            "Compiled MIT clean-room PSP and runtime-handoff initialization service at its authenticated stock entry",
        ),
        "opaque_before_open_cfw_bootloader_fpu_enable_432958_source_in_place": (
            "bootloader_process_stack_literal_432954_432958",
            "Authenticated process-stack initialization literal",
        ),
        "open_cfw_bootloader_fpu_enable_432958_source_in_place": (
            "bootloader_fpu_enable_432958_source_in_place",
            "Compiled MIT clean-room CP10/CP11 and FPSCR initialization service at its authenticated stock entry",
        ),
        "opaque_before_open_cfw_bootloader_runtime_start_43297c_source_in_place": (
            "bootloader_startup_runtime_alignment_43297a_43297c",
            "Authenticated alignment between the FPU initialization service and runtime startup dispatcher",
        ),
        "open_cfw_bootloader_runtime_start_43297c_source_in_place": (
            "bootloader_runtime_start_43297c_source_in_place",
            "Compiled MIT clean-room Cortex-M runtime startup dispatcher at its authenticated stock entry",
        ),
        "opaque_before_open_cfw_bootloader_init_array_run_43299c_source_in_place": (
            "bootloader_runtime_start_alignment_43299a_43299c",
            "Authenticated alignment between the runtime startup dispatcher and constructor-array walker",
        ),
        "open_cfw_bootloader_init_array_run_43299c_source_in_place": (
            "bootloader_init_array_run_43299c_source_in_place",
            "Compiled MIT clean-room constructor-array walker at its authenticated stock entry",
        ),
        "opaque_before_open_cfw_bootloader_terminal_loop_4329c4_source_in_place": (
            "bootloader_init_array_literals_4329bc_4329c4",
            "Authenticated constructor-array address literals before the terminal service loop",
        ),
        "open_cfw_bootloader_terminal_loop_4329c4_source_in_place": (
            "bootloader_terminal_loop_4329c4_source_in_place",
            "Compiled MIT clean-room non-returning terminal service loop at its authenticated stock entry",
        ),
        "opaque_after_open_cfw_bootloader_spotmgr_profile_apply_42ab7c_source_in_place": (
            "bootloader_opaque_between_spotmgr_profile_apply_and_init_42abb2_42abbc",
            "Authenticated shared literals and alignment between the SPOT-manager profile and initialization entries",
        ),
        "opaque_after_source_redirects": (
            "bootloader_opaque_after_terminal_loop_4329d2",
            "Authenticated retained bootloader bytes after the source-owned Cortex-M runtime startup tail",
        ),
    })
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
    build_report = json.loads(BUILD_REPORT.read_text(encoding="utf-8"))
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
    for key in (
        "source_owned_bytes",
        "opaque_base_bytes",
        "generated_patch_site_bytes",
        "generated_alignment_bytes",
        "source_owned_cave_bytes",
        "source_owned_in_place_bytes",
        "generated_isolated_alignment_bytes",
        "generated_relocated_alignment_bytes",
        "generated_stock_to_overlay_alignment_bytes",
    ):
        provider[key] = int(build_report["component"][key])
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
        "recovered NVIC enable/priority and MSPI interrupt-dispatch services through 0x0041FE28",
        "recovered idempotent MSPI enable and disable controls through 0x0041FE62",
        "recovered guarded event-flags initialization, acquire, and release services through 0x0041FF08",
        "recovered paired event-lock/MSPI guard enter and exit wrappers through 0x0041FF34",
        "recovered retained-configuration MSPI XIP request updater through 0x0041FF60",
        "recovered longest consecutive-one run-length and center-selection helpers through 0x00420002",
        "recovered exhaustive MSPI timing scan, pass-mask selection, and centered timing result through 0x004201BA",
        "recovered automatic MSPI timing-selection and fallback wrapper through 0x00420254",
        "recovered MX25U25643G low-level MSPI initialization through 0x00420476",
        "recovered MX25U25643G public initialization and service setup through 0x0042052A",
        "recovered MX25U25643G soft-reset sequence through 0x0042059E",
        "recovered MX25U25643G JEDEC-ID command and packing entry through 0x004205F4",
        "recovered MX25U25643G validated write-transfer wrapper through 0x0042074E",
        "recovered MX25U25643G status-register reader through 0x004207A2",
        "recovered MX25U25643G two-phase and fixed ready-poll wrappers through 0x00420800",
        "recovered MX25U25643G address-mode register reader through 0x0042086C",
        "recovered MX25U25643G guarded four-byte-mode entry sequence through 0x00420978",
        "recovered MX25U25643G guarded sector-erase service through 0x00420ADA",
        "recovered MX25U25643G page-splitting program service through 0x00420C14",
        "recovered MSPI device disable, reconfiguration, enable, and pin-group service through 0x00420E8C",
        "recovered MX25U25643G quad-mode template, reconfiguration, XIP, and control service through 0x00420F0C",
        "recovered MX25U25643G serial-mode reconfiguration, XIP, and control service through 0x00420F6A",
        "recovered MX25U25643G guarded blocking read service through 0x00420FF2",
        "recovered LittleFS directory bootstrap service through 0x004211B0",
        "recovered LittleFS format, mount, and directory-bootstrap orchestration service through 0x00421210",
        "recovered LittleFS mount, recovery, readiness, and boot-counter initialization service through 0x004212D8",
        "recovered LittleFS block-read callback through 0x00421310",
        "recovered LittleFS block-program callback through 0x00421348 using authenticated reclaimed initializer body space",
        "recovered LittleFS block-erase callback through 0x00421372 using authenticated reclaimed initializer body space",
        "recovered LittleFS constant-success sync callback through 0x004213D8 using authenticated reclaimed initializer body space",
        "recovered exact in-place address-index helpers through 0x004213E6",
        "recovered mapped-memory selector, copy service, and odd-selector wrapper through 0x0042156E using authenticated reclaimed entry space",
        "recovered exact in-place 32-bit population-count helper through 0x004215AE",
        "recovered exact in-place two-word bitmap query and count helpers through 0x00421632",
        "recovered exact in-place validated two-word bitmap update helper through 0x004216B2",
        "recovered exact in-place bounded poll-delay helper through 0x004216D4",
        "recovered exact in-place mode/configuration transaction service through 0x004217D2",
        "recovered exact in-place dual-controller mode transaction service through 0x00421978",
        "recovered exact in-place bitmap-client configuration and row mutation services through 0x00421B08",
        "recovered exact in-place mode-one enable, disable, and poll-cleanup services through 0x00421BD2",
        "recovered exact in-place mode-zero enable transaction through 0x00421CCE",
        "recovered exact in-place mode-zero disable and poll-cleanup services through 0x00421D5E",
        "recovered exact in-place row-four enable transaction through 0x00421E4A",
        "recovered exact in-place row-four disable and poll-cleanup services through 0x00421EBA",
        "recovered exact in-place row-five enable and disable services through 0x004220B2",
        "recovered exact in-place row-six enable/disable and mode-family dispatcher services through 0x004222D2",
        "recovered exact in-place mode enable/disable routing, all-row cleanup, and configuration copy services through 0x00422430",
        "recovered exact in-place AmbiqSuite-compatible debug shutdown, power-reference, and trace-disable services through 0x00422574",
        "recovered exact in-place constraint dispatch and optimized memchr services through 0x00422628",
        "recovered exact in-place IAR-compatible double runtime services through 0x00422872",
        "recovered exact in-place IAR thread-pointer leaf through 0x0042287C",
        "recovered exact in-place IAR unsigned 64-bit divide/modulo runtime through 0x00422AAC",
        "recovered exact in-place atomic snapshot, no-op, and retained-query wrappers through 0x00422AD2",
        "recovered exact in-place four-instance initialization, register-transfer/lifecycle, register-clear, and status-mapping services through 0x00422DC6",
        "recovered exact in-place guarded per-instance dual-descriptor initialization service through 0x00422E28",
        "recovered exact in-place per-instance clock-divider selection and programming service through 0x00422EE2",
        "recovered exact in-place interrupt-atomic per-instance configuration latch through 0x00422F4C",
        "recovered exact in-place interrupt-atomic secondary per-instance configuration latch through 0x00422FA2",
        "recovered exact in-place interrupt-atomic secondary per-instance configuration release through 0x00422FDE",
        "recovered exact in-place per-instance register-quiesce and hardware-shutdown service through 0x0042308E",
        "recovered exact in-place per-instance FIFO read/write and drain services at 0x004232C8 through 0x00423350",
        "recovered exact in-place critical-section FIFO snapshot and pump adapters through 0x004233E0",
        "recovered exact in-place type-checked mode dispatcher and mode-two/mode-three start helpers through 0x00423524",
        "recovered exact in-place mode-zero and mode-one bounded wait wrappers through 0x004234D8",
        "recovered exact in-place primary and secondary progress services through 0x004236CE",
        "recovered exact in-place per-instance register OR, write, and query services through 0x00423764",
        "recovered exact in-place per-instance interrupt and progress service dispatcher through 0x0042382C",
        "recovered exact in-place bounded memory exchange and three-buffer rotation through 0x00423928",
        "recovered exact in-place bounded rotate-to-front helper through 0x00423972",
        "recovered exact in-place three-element comparator/exchange helper through 0x004239C2",
        "recovered exact in-place Floyd max-heap sift helper through 0x00423A48",
        "recovered exact in-place introspective qsort core and public wrapper through 0x00423D20",
        "recovered exact in-place global hardware-control services through 0x00423E0C",
        "recovered exact in-place hardware-control state mapper through 0x00423E40",
        "recovered exact in-place global MSPI FIFO-write service through 0x00423E8A",
        "recovered exact in-place global MSPI FIFO-read service through 0x00423F28",
        "recovered exact in-place MSPI command-queue initializer through 0x00423F54",
        "recovered exact in-place MSPI command-queue terminator through 0x00423F8E",
        "recovered exact in-place MSPI command-queue enable/disable services through 0x00423FB8",
        "retained authenticated official MSPI configuration, lifecycle, control, and transfer bodies from 0x00424120 through 0x00426536",
        "recovered exact in-place AmbiqSuite 5.1.0 MSPI interrupt-service and power-control bodies through 0x00426BFE",
        "source-routed Apollo510 HFRC2 UQ17.15 and integer divider services through 0x00426C58 using authenticated reclaimed NOP space",
        "recovered exact in-place clean-room CLKGEN HFADJ bit-control leaf through 0x00426C70",
        "source-routed clean-room CLKGEN HFADJ configuration publisher through 0x00426C7E using authenticated generated NOP space",
        "source-routed clean-room CLKGEN HFADJ bit-preserving disable leaf through 0x00426C8C using authenticated generated NOP space",
        "recovered in-place clean-room CLKGEN dual-clock switch prefix through 0x00426CC4 with authenticated status-check binding",
        "source-routed clean-room CLKGEN control, mode, clock-select, and divider configuration service through 0x00426D1E using authenticated generated NOP space",
        "source-routed clean-room CLKGEN bit-preserving disable service through 0x00426D2C using authenticated generated NOP space",
        "source-routed AmbiqSuite 5.1.0 System PLL minimum-VCO, postdivider, and initialization services through 0x00427308 using authenticated reclaimed body space",
        "recovered exact in-place AmbiqSuite 5.1.0 System PLL deinitialization service through 0x00427360",
        "source-routed AmbiqSuite 5.1.0 System PLL enable service through 0x004273DC using authenticated reclaimed body space",
        "recovered exact in-place AmbiqSuite 5.1.0 System PLL disable service through 0x0042740C",
        "source-routed AmbiqSuite 5.1.0 System PLL configuration service through 0x00427522 using authenticated reclaimed body space",
        "source-routed AmbiqSuite 5.1.0 System PLL lock-wait service through 0x00427588 using authenticated reclaimed body space",
        "source-routed AmbiqSuite 5.1.0 queue initializer, item-add, and item-get services through 0x004276BA using authenticated reclaimed body space",
        "source-routed clean-room overlap-safe byte move through 0x00427752 using authenticated reclaimed body space",
        "source-routed AmbiqSuite 5.1.0 command-queue index updater through 0x00427794 using authenticated reclaimed body space",
        "recovered in-place AmbiqSuite 5.1.0 command-queue initialization, lifecycle, allocation, status, recovery, reset, and loop-post services through 0x00427C80; recovered in-place MIT hard-float veneers, binary32 rounding/remainder cores, and range classifier through 0x00427E84; recovered in-place BSD-3-Clause Apollo510 SPOT-manager transition sequences through 0x00428BA8; recovered in-place MIT indexed SPOT-manager factory-trim loader and readiness wrapper through 0x0042A04A; recovered in-place BSD-3-Clause SPOT-manager timer interrupt service through 0x0042A078",
    )
    parts = list(dict.fromkeys(
        part.strip() for part in override["function"].split(";") if part.strip()
    ))
    retired_suffixes = {
        "recovered exact in-place AmbiqSuite-compatible MSPI control dispatcher through 0x004262E0":
            "retained authenticated official MSPI configuration, lifecycle, control, and transfer bodies from 0x00424120 through 0x00426536",
    }
    parts = list(dict.fromkeys(retired_suffixes.get(part, part) for part in parts))
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
