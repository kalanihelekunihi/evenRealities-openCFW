#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Build an explicitly hybrid codec candidate from reviewed C replacements.

This is an integration step, not source-only completion. Every byte is assigned
to compiled C, generated container metadata, or an authenticated retained range.
"""
import argparse
import json
import struct
import zlib
from pathlib import Path
from analyze_gx8002_upstream_objects import IMAGE, IMAGE_SHA, sha
from analyze_g2_codec_fwpk_segments import parse_fwpk, parse_boot_image, parse_main_image
from open_cfw import validate_codec
from build_transparent_image import Elf32
from verify_gx8002_analog_source import verify as verify_analog
from verify_gx8002_csi_source import verify as verify_csi
from verify_gx8002_icache_source import verify as verify_icache
from verify_gx8002_i2s_source import verify as verify_i2s
from verify_gx8002_vad_curves import verify as verify_vad
from verify_gx8002_model_interface import verify as verify_model
from verify_gx8002_memcpy_source import verify as verify_memcpy
from verify_gx8002_uart_stage1_divmod import verify as verify_uart_stage1_divmod
from verify_gx8002_uart_stage1_reset import verify as verify_uart_stage1_reset
from verify_gx8002_uart_stage1_pmubits import verify as verify_uart_stage1_pmubits
from verify_gx8002_uart_stage1_serial import verify as verify_uart_stage1_serial
from verify_gx8002_uart_stage1_idbit import verify as verify_uart_stage1_idbit
from verify_gx8002_uart_stage1_xip import verify as verify_uart_stage1_xip
from verify_gx8002_uart_stage1_pmufill import verify as verify_uart_stage1_pmufill
from verify_gx8002_uart_stage1_mdelay import verify as verify_uart_stage1_mdelay
from verify_gx8002_uart_stage1_vectors import verify as verify_uart_stage1_vectors
from verify_gx8002_uart_stage1_railc import verify as verify_uart_stage1_railc
from verify_gx8002_uart_stage1_railb import verify as verify_uart_stage1_railb
from verify_gx8002_uart_stage1_raila import verify as verify_uart_stage1_raila
from verify_gx8002_uart_stage1_pmudisp import verify as verify_uart_stage1_pmudisp
from verify_gx8002_uart_stage1_pmusecond import verify as verify_uart_stage1_pmusecond
from verify_gx8002_uart_stage1_postamble import verify as verify_uart_stage1_postamble
from verify_gx8002_uart_stage1_uartcfg import verify as verify_uart_stage1_uartcfg
from verify_gx8002_uart_stage1_traptails import verify as verify_uart_stage1_traptails
from verify_gx8002_uart_stage1_beacon import verify as verify_uart_stage1_beacon
from verify_gx8002_uart_stage1_announce import verify as verify_uart_stage1_announce
from verify_gx8002_uart_stage1_handshake import verify as verify_uart_stage1_handshake
from verify_gx8002_model_set_task import verify as verify_setter
from verify_gx8002_app_resume import verify as verify_resume
from verify_gx8002_app_suspend import verify as verify_suspend
from verify_gx8002_watchdog_stop import verify as verify_watchdog
from verify_gx8002_queue_source import verify as verify_queue
from compare_gx8002_queue_get import verify_get
from compare_gx8002_queue_put import verify_put
from verify_gx8002_trigger_event import verify as verify_trigger
from verify_gx8002_crc32_source import verify as verify_crc
from verify_gx8002_uart_console import verify as verify_console
from verify_gx8002_logging import formatter as verify_formatter, printf as verify_printf
from verify_gx8002_fputc import verify as verify_fputc
from verify_gx8002_uart_tick import verify as verify_uart_tick
from verify_gx8002_app_tick import verify as verify_app_tick
from verify_gx8002_power_registration import verify as verify_power_registration
from verify_gx8002_irq import verify as verify_irq
from verify_gx8002_clock_source import verify as verify_clock
from verify_gx8002_platform_gate import verify as verify_gate
from verify_gx8002_watchdog_initialize import verify as verify_watchdog_initialize
from verify_gx8002_flash_transport import verify as verify_flash_transport
from verify_gx8002_flash_status import verify as verify_flash_status
from verify_gx8002_flash_device import verify as verify_flash_device
from verify_gx8002_flash_quad import verify as verify_flash_quad
from verify_gx8002_flash_xip import verify as verify_flash_xip
from verify_gx8002_platform_config import verify as verify_platform_config
from verify_gx8002_flash_discover import verify as verify_flash_discover
from verify_gx8002_flash_word_io import verify as verify_flash_word_io
from verify_gx8002_flash_info import verify as verify_flash_info
from verify_gx8002_flash_otp_region import verify as verify_flash_otp_region
from verify_gx8002_flash_address import verify as verify_flash_address
from verify_gx8002_flash_otp_descriptor import verify as verify_flash_otp_descriptor
from verify_gx8002_flash_state import verify as verify_flash_state
from verify_gx8002_flash_protection import verify as verify_flash_protection
from verify_gx8002_flash_protection_set import verify as verify_flash_protection_set
from verify_gx8002_flash_protection_tables import verify as verify_flash_protection_tables
from verify_gx8002_flash_protection_initialize import verify as verify_flash_protection_initialize
from verify_gx8002_flash_interrupt import verify as verify_flash_interrupt
from verify_gx8002_flash_interface_initialize import verify as verify_flash_interface_initialize
from verify_gx8002_flash_erase import verify as verify_flash_erase
from verify_gx8002_flash_read import verify as verify_flash_read
from verify_gx8002_flash_page_program import verify as verify_flash_page_program
from verify_gx8002_flash_block_range import verify as verify_flash_block_range
from verify_gx8002_flash_otp_status import verify as verify_flash_otp_status
from verify_gx8002_flash_otp_lock import verify as verify_flash_otp_lock
from verify_gx8002_flash_otp_erase import verify as verify_flash_otp_erase
from verify_gx8002_flash_otp_transmit import verify as verify_flash_otp_transmit
from verify_gx8002_flash_otp_write import verify as verify_flash_otp_write
from verify_gx8002_flash_otp_read import verify as verify_flash_otp_read
from verify_gx8002_flash_uid_read import verify as verify_flash_uid_read
from verify_gx8002_flash_interface_table import verify as verify_flash_interface_table
from verify_gx8002_flash_device_names import verify as verify_flash_device_names
from verify_gx8002_flash_initialize import verify as verify_flash_initialize
from verify_gx8002_board_initialize import verify as verify_board_initialize
from verify_gx8002_irq_compact_admission import verify as verify_irq_compact
from verify_gx8002_reset_entry import verify as verify_reset_entry
from verify_gx8002_main import verify as verify_main
from verify_gx8002_mode import verify as verify_mode
from verify_gx8002_idle import verify as verify_idle
from verify_gx8002_tws import verify as verify_tws
from verify_gx8002_kws_insert import verify as verify_kws_insert
from verify_gx8002_wakeword_parameters import verify as verify_wakeword_parameters
from verify_gx8002_memset import verify as verify_memset
from verify_gx8002_kws_reset import verify as verify_kws_reset
from verify_gx8002_max_initialize import verify as verify_max_initialize
from verify_gx8002_max_list import verify as verify_max_list
from verify_gx8002_max_score_source import verify as verify_max_score_source
from verify_gx8002_max_decoder_source import verify as verify_max_decoder_source
from verify_gx8002_kws_strategy_source import verify as verify_kws_strategy_source
from verify_gx8002_bionic_offsets import verify as verify_bionic_offsets
from verify_gx8002_bionic_run_source import verify as verify_bionic_run_source
from verify_gx8002_next_range_source import verify as verify_next_range_source
from verify_gx8002_app_gpio_power import verify as verify_app_gpio_power
from verify_gx8002_app_gpio_event_source import verify as verify_app_gpio_event_source
from verify_gx8002_sample_app_init_source import verify as verify_sample_app_init_source
from verify_gx8002_sample_event_source import verify as verify_sample_event_source
from verify_gx8002_start_i2s_source import verify as verify_start_i2s_source
from verify_gx8002_stop_i2s_source import verify as verify_stop_i2s_source
from verify_gx8002_i2s_request_tick_source import verify as verify_i2s_request_tick_source
from verify_gx8002_app_commands_source import verify as verify_app_commands_source
from verify_gx8002_app_reply_source import verify as verify_app_reply_source
from verify_gx8002_app_command_callback_persistent_source import verify as verify_app_callback_source
from verify_gx8002_notification_setup_source import verify as verify_notification_setup_source
from verify_gx8002_notification_stamp_source import verify as verify_notification_stamp_source
from verify_gx8002_event_notify_source import verify as verify_event_notify_source
from verify_gx8002_fpadd_parts_source import verify as verify_fpadd_parts_source
from verify_gx8002_adddf3_source import verify as verify_adddf3_source
from verify_gx8002_muldf3_fixed_source import verify as verify_muldf3_fixed_source
from verify_gx8002_divdf3_fixed_source import verify as verify_divdf3_fixed_source
from verify_gx8002_udivdi3_source import verify as verify_udivdi3_source
from verify_gx8002_application_vectors_source import verify as verify_application_vectors_source
from verify_gx8002_runtime_messages_source import verify as verify_runtime_messages_source
from verify_gx8002_board_gain_data_source import verify as verify_board_gain_data_source
from verify_gx8002_audio_board_control_source import verify as verify_audio_board_control_source
from verify_gx8002_audio_board_storage_source import verify as verify_audio_board_storage_source
from verify_gx8002_uart_descriptor_source import verify as verify_uart_descriptor_source
from verify_gx8002_distance_noise_source import verify as verify_distance_noise_source
from verify_gx8002_exception_source import verify as verify_exception_source
from verify_gx8002_keyword_list_get_source import verify as verify_keyword_list_get_source
from verify_gx8002_irq_save_disable_wrapper_source import verify as verify_irq_save_disable_wrapper_source
from verify_gx8002_audio_api_labels_source import verify as verify_audio_api_labels_source
from verify_gx8002_application_labels_source import verify as verify_application_labels_source
from verify_gx8002_audio_mapping_tables_source import verify as verify_audio_mapping_tables_source
from verify_gx8002_mode_descriptors_source import verify as verify_mode_descriptors_source
from verify_gx8002_event_defaults_source import verify as verify_event_defaults_source
from verify_gx8002_decoder_default_source import verify as verify_decoder_default_source
from verify_gx8002_application_descriptor_source import verify as verify_application_descriptor_source
from verify_gx8002_uart_header_defaults_source import verify as verify_uart_header_defaults_source
from verify_gx8002_reply_defaults_source import verify as verify_reply_defaults_source
from verify_gx8002_clock_module_dto_set_source import verify as verify_clock_module_dto_set_source
from verify_gx8002_clock_module_divider_set_source import verify as verify_clock_module_divider_set_source
from verify_gx8002_clock_module_query_source import verify as verify_clock_module_query_source
from verify_gx8002_clock_module_source_fixed_source import verify as verify_clock_module_source_fixed_source
from verify_gx8002_timer_dispatch_source import verify as verify_timer_dispatch_source
from verify_gx8002_delay_source import verify as verify_delay_source
from verify_gx8002_trim_state_source import verify as verify_trim_state_source
from verify_gx8002_trim_clock_enable_source import verify as verify_trim_clock_enable_source
from verify_gx8002_digital_voltage_source import verify as verify_digital_voltage_source
from verify_gx8002_analog_voltage_source import verify as verify_analog_voltage_source
from verify_gx8002_digital_control_source import verify as verify_digital_control_source
from verify_gx8002_flash_read_api_source import verify as verify_flash_read_api_source
from verify_gx8002_flash_type_api_source import verify as verify_flash_type_api_source
from verify_gx8002_flash_probe_source import verify as verify_flash_probe_source
from verify_gx8002_dcache_invalid_range_source import verify as verify_dcache_invalid_range_source
from verify_gx8002_dcache_clean_invalid_range_source import verify as verify_dcache_clean_invalid_range_source
from verify_gx8002_timer_initialize_source import verify as verify_timer_initialize_source
from verify_gx8002_timer_channel_initialize_source import verify as verify_timer_channel_initialize_source
from verify_gx8002_flash_info_api_source import verify as verify_flash_info_api_source
from verify_gx8002_flash_otp_configuration_source import verify as verify_flash_otp_configuration_source
from verify_gx8002_otp_lowpower_enter_source import verify as verify_otp_lowpower_enter_source
from verify_gx8002_platform_read_source import verify as verify_platform_read_source
from verify_gx8002_kws_pair_source import verify as verify_kws_pair_source
from verify_gx8002_audio_record_source import verify as verify_audio_record_source
from verify_gx8002_active_snpu_source import verify as verify_active_snpu_source
from verify_gx8002_tws_tick_source import verify as verify_tws_tick_source
from verify_gx8002_tws_standby_source import verify as verify_tws_standby_source
from verify_gx8002_tws_audio_source import verify as verify_tws_audio_source
from verify_gx8002_audio_irq_source import verify as verify_audio_irq_source
from verify_gx8002_flash_otp_read_api_source import verify as verify_flash_otp_read_api_source
from verify_gx8002_dcache_disable_upstream_source import verify as verify_dcache_disable_upstream_source
from verify_gx8002_clock_init_source import verify as verify_clock_init_source
from verify_gx8002_clock_switch_1m_source import verify as verify_clock_switch_1m_source
from verify_gx8002_clock_gate_query_source import verify as verify_clock_gate_query_source
from verify_gx8002_audio_lowpower_divider_source import verify as verify_audio_lowpower_divider_source
from verify_gx8002_clock_lowpower_init_source import verify as verify_clock_lowpower_init_source
from verify_gx8002_clock_time_ms_source import verify as verify_clock_time_ms_source
from verify_gx8002_clock_time_us_source import verify as verify_clock_time_us_source
from verify_gx8002_clock_pll_wait_source import verify as verify_clock_pll_wait_source
from verify_gx8002_clock_pll_source import verify as verify_clock_pll_source
from verify_gx8002_clock_source_select_source import verify as verify_clock_source_select_source
from verify_gx8002_uart_transmit_dma_placement_source import verify as verify_uart_transmit_dma_placement_source
from verify_gx8002_subdf3_source import verify as verify_subdf3_source
from verify_gx8002_muldi3_source import verify as verify_muldi3_source
from verify_gx8002_pack_double_source import verify as verify_pack_double_source
from verify_gx8002_floatunsidf_source import verify as verify_floatunsidf_source
from verify_gx8002_fixdfsi_source import verify as verify_fixdfsi_source
from verify_gx8002_unpack_double_source import verify as verify_unpack_double_source
from verify_gx8002_fpcmp_parts_source import verify as verify_fpcmp_parts_source
from verify_gx8002_gedf2_source import verify as verify_gedf2_source
from verify_gx8002_fixunsdfsi_source import verify as verify_fixunsdfsi_source
from verify_gx8002_div64_source import verify as verify_div64_source
from verify_gx8002_strtok_source import verify as verify_strtok_source
from verify_gx8002_i2s_ack_source import verify as verify_i2s_ack_source
from verify_gx8002_vad_notify_source import verify as verify_vad_notify_source
from verify_gx8002_notification_poll_source import verify as verify_notification_poll_source
from verify_gx8002_mic_buffer_source import verify as verify_mic_buffer_source
from verify_gx8002_tws_shutdown import verify as verify_tws_shutdown
from verify_gx8002_stream_shutdown import verify as verify_stream_shutdown
from verify_gx8002_driver_exit import verify as verify_driver_exit
from verify_gx8002_audio_reset import verify as verify_audio_reset
from verify_gx8002_snpu_suspend import verify as verify_snpu_suspend
from verify_gx8002_irq_mask import verify as verify_irq_mask
from verify_gx8002_snpu_clock import verify as verify_snpu_clock
from verify_gx8002_npu_registers import verify as verify_npu_registers
from verify_gx8002_npu_control import verify as verify_npu_control
from verify_gx8002_npu_accessors import verify as verify_npu_accessors
from verify_gx8002_npu_configuration import verify as verify_npu_configuration
from verify_gx8002_npu_interrupt_masks import verify as verify_npu_interrupt_masks
from verify_gx8002_npu_interrupt_status import verify as verify_npu_interrupt_status
from verify_gx8002_snpu_device import verify as verify_snpu_device
from verify_gx8002_npu_regs_init import verify as verify_npu_regs_init
from verify_gx8002_snpu_resume_internal import verify as verify_snpu_resume_internal
from verify_gx8002_snpu_initialize import verify as verify_snpu_initialize
from verify_gx8002_snpu_isr import verify as verify_snpu_isr
from verify_gx8002_snpu_process_status import verify as verify_snpu_process_status
from verify_gx8002_snpu_overtime import verify as verify_snpu_overtime
from verify_gx8002_snpu_tcb_init import verify as verify_snpu_tcb_init
from verify_gx8002_snpu_submit_task import verify as verify_snpu_submit_task
from verify_gx8002_snpu_run_task import verify as verify_snpu_run_task
from verify_gx8002_snpu_get_state import verify as verify_snpu_get_state
from verify_gx8002_gpio_isr import verify as verify_gpio_isr
from verify_gx8002_gpio_output import verify as verify_gpio_output
from verify_gx8002_gpio_trigger import verify as verify_gpio_trigger
from verify_gx8002_gpio_disable_trigger import verify as verify_gpio_disable_trigger
from verify_gx8002_gpio_initialize import verify as verify_gpio_initialize
from verify_gx8002_device_list_init import verify as verify_device_list_init
from verify_gx8002_spi_register_master import verify as verify_spi_register_master
from verify_gx8002_dw_spi_cleanup import verify as verify_dw_spi_cleanup
from verify_gx8002_dw_spi_setup import verify as verify_dw_spi_setup
from verify_gx8002_analog_config_update_enable import verify as verify_analog_config_update_enable
from verify_gx8002_irq_boot_stage2_enable import verify as verify_irq_boot_stage2_enable
from verify_gx8002_uart_boot_stage2_diagnostics import verify as verify_uart_boot_stage2_diagnostics
from verify_gx8002_stage2_libc import verify as verify_stage2_libc
from verify_gx8002_strncmp import verify as verify_strncmp
from verify_gx8002_main_strlen import verify as verify_main_strlen
from verify_gx8002_memmove_source import verify as verify_memmove_source
from verify_gx8002_kws_flash_load_source import verify as verify_kws_flash_load_source
from verify_gx8002_kws_initialize import verify as verify_kws_initialize
from verify_gx8002_audio_input_standby_source import verify as verify_audio_input_standby_source
from verify_gx8002_power_initialize_source import verify as verify_power_initialize_source
from verify_gx8002_power_locks_source import verify as verify_power_locks_source
from verify_gx8002_power_lock_control_source import verify as verify_power_lock_control_source
from verify_gx8002_multiboot_switch_source import verify as verify_multiboot_switch_source
from verify_gx8002_uart_message_start_source import verify as verify_uart_message_start_source
from verify_gx8002_uart_message_body_source import verify as verify_uart_message_body_source
from verify_gx8002_uart_body_done_source import verify as verify_uart_body_done_source
from verify_gx8002_uart_receive_body_done_source import verify as verify_uart_receive_body_done_source
from verify_gx8002_uart_message_done_source import verify as verify_uart_message_done_source
from verify_gx8002_uart_message_initialize_source import verify as verify_uart_message_initialize_source
from verify_gx8002_uart_message_enqueue_source import verify as verify_uart_message_enqueue_source
from verify_gx8002_uart_registration_source import verify as verify_uart_registration_source
from verify_gx8002_uart_receive_callback_source import verify as verify_uart_receive_callback_source
from verify_gx8002_uart_send_callback_source import verify as verify_uart_send_callback_source
from verify_gx8002_uart_receive_body_source import verify as verify_uart_receive_body_source
from verify_gx8002_uart_message_power_source import verify as verify_uart_message_power_source
from verify_gx8002_power_suspend_source import verify as verify_power_suspend_source
from verify_gx8002_lvp_system_initialize_source import verify as verify_lvp_system_initialize_source
from verify_gx8002_audio_input_env_noise_source import verify as verify_audio_input_env_noise_source
from verify_gx8002_audio_input_query_vad_source import verify as verify_audio_input_query_vad_source
from verify_gx8002_audio_input_init_source import verify as verify_audio_input_init_source
from verify_gx8002_audio_input_state import verify as verify_audio_input_state
from verify_gx8002_audio_input_config_source import verify as verify_audio_input_config_source
from verify_gx8002_audio_input_output_source import verify as verify_audio_input_output_source
from verify_gx8002_audio_input_buffers_source import verify as verify_audio_input_buffers_source
from verify_gx8002_buffer_metadata import verify as verify_buffer_metadata
from verify_gx8002_mic_frame import verify as verify_mic_frame
from verify_gx8002_context_acquire import verify as verify_context_acquire
from verify_gx8002_logfbank_index import verify as verify_logfbank_index
from verify_gx8002_buffer_accessors import verify as verify_buffer_accessors
from verify_gx8002_buffer_initialize_source import verify as verify_buffer_initialize_source
from verify_gx8002_dw_spi_irq import verify as verify_dw_spi_irq
from verify_gx8002_dw_spi_probe import verify as verify_dw_spi_probe
from verify_gx8002_dw_spi_quick_transfer import verify as verify_dw_spi_quick_transfer
from verify_gx8002_padmux_get import verify as verify_padmux_get
from verify_gx8002_padmux_check import verify as verify_padmux_check
from verify_gx8002_padmux_set import verify as verify_padmux_set
from verify_gx8002_padmux_init import verify as verify_padmux_init
from verify_gx8002_padmux_defaults import verify as verify_padmux_defaults
from verify_gx8002_rtc_isr import verify as verify_rtc_isr
from verify_gx8002_rtc_start_tick import verify as verify_rtc_start_tick
from verify_gx8002_rtc_set_tick import verify as verify_rtc_set_tick
from verify_gx8002_rtc_error import verify as verify_rtc_error
from verify_gx8002_rtc_init_source import verify as verify_rtc_init_source
from verify_gx8002_dma_clear_source import verify as verify_dma_clear_source
from verify_gx8002_uart_receive_dma_source import verify as verify_uart_receive_dma_source
from verify_gx8002_dma_transfer_source import verify as verify_dma_transfer_source
from verify_gx8002_uart_transmit_buffer_source import verify as verify_uart_transmit_buffer_source
from verify_gx8002_uart_receive_buffer_source import verify as verify_uart_receive_buffer_source
from verify_gx8002_uart_receive_control_source import verify as verify_uart_receive_control_source
from verify_gx8002_uart_transmit_control_source import verify as verify_uart_transmit_control_source
from verify_gx8002_uart_fifo_depth_source import verify as verify_uart_fifo_depth_source
from verify_gx8002_uart_read_source import verify as verify_uart_read_source
from verify_gx8002_uart_write_source import verify as verify_uart_write_source
from verify_gx8002_uart_receive_byte_source import verify as verify_uart_receive_byte_source
from verify_gx8002_uart_initialize_source import verify as verify_uart_initialize_source
from verify_gx8002_uart_configure_source import verify as verify_uart_configure_source
from verify_gx8002_uart_interrupt_source import verify as verify_uart_interrupt_source
from verify_gx8002_dma_abort_source import verify as verify_dma_abort_source
from verify_gx8002_uart_abort_source import verify as verify_uart_abort_source
from verify_gx8002_console_initialize_source import verify as verify_console_initialize_source
from verify_gx8002_cache_initialize_source import verify as verify_cache_initialize_source
from verify_gx8002_pcm_channel_setting_source import verify as verify_pcm_channel_setting_source
from verify_gx8002_audio_input_sadc_source import verify as verify_audio_input_sadc_source
from verify_gx8002_audio_input_pdm_source import verify as verify_audio_input_pdm_source
from verify_gx8002_audio_input_i2s_source import verify as verify_audio_input_i2s_source
from verify_gx8002_audio_input_channel_source import verify as verify_audio_input_channel_source
from verify_gx8002_audio_output_pcm_source import verify as verify_audio_output_pcm_source
from verify_gx8002_audio_output_logfbank_source import verify as verify_audio_output_logfbank_source
from verify_gx8002_audio_output_spectrum_source import verify as verify_audio_output_spectrum_source
from verify_gx8002_audio_output_i2s_source import verify as verify_audio_output_i2s_source
from verify_gx8002_audio_pga_gain_source import verify as verify_audio_pga_gain_source
from verify_gx8002_audio_dc_enable_source import verify as verify_audio_dc_enable_source
from verify_gx8002_audio_rough_gain_source import verify as verify_audio_rough_gain_source
from verify_gx8002_audio_evad_enable_source import verify as verify_audio_evad_enable_source
from verify_gx8002_audio_evad_threshold_source import verify as verify_audio_evad_threshold_source
from verify_gx8002_audio_logfbank_enable_source import verify as verify_audio_logfbank_enable_source
from verify_gx8002_audio_fftvad_enable_source import verify as verify_audio_fftvad_enable_source
from verify_gx8002_audio_fftvad_w_source import verify as verify_audio_fftvad_w_source
from verify_gx8002_audio_fftvad_chipping_source import verify as verify_audio_fftvad_chipping_source
from verify_gx8002_audio_fftvad_state_source import verify as verify_audio_fftvad_state_source
from verify_gx8002_audio_interrupt_enable_source import verify as verify_audio_interrupt_enable_source
from verify_gx8002_audio_initialize_source import verify as verify_audio_initialize_source
from verify_gx8002_audio_channel_field_source import verify as verify_audio_channel_field_source
from verify_gx8002_audio_output_bits_source import verify as verify_audio_output_bits_source
from verify_gx8002_audio_output_free_source import verify as verify_audio_output_free_source
from verify_gx8002_audio_output_push_frame_source import verify as verify_audio_output_push_frame_source
from verify_gx8002_audio_output_config_buffer_source import verify as verify_audio_output_config_buffer_source
from verify_gx8002_audio_output_config_pcm_source import verify as verify_audio_output_config_pcm_source
from verify_gx8002_audio_output_set_channel_source import verify as verify_audio_output_set_channel_source
from verify_gx8002_audio_output_alloc_playback_source import verify as verify_audio_output_alloc_playback_source
from verify_gx8002_audio_output_hw_config_source import verify as verify_audio_output_hw_config_source
from verify_gx8002_audio_output_handle_isr_source import verify as verify_audio_output_handle_isr_source
from verify_gx8002_audio_output_drain_frame_source import verify as verify_audio_output_drain_frame_source
from verify_gx8002_audio_output_init_source import verify as verify_audio_output_init_source
from verify_gx8002_audio_output_volume_source import verify as verify_audio_output_volume_source
from verify_gx8002_audio_output_route_source import verify as verify_audio_output_route_source
from verify_gx8002_audio_output_dispatch_source import verify as verify_audio_output_dispatch_source
from verify_gx8002_audio_output_public_init_source import verify as verify_audio_output_public_init_source
from verify_gx8002_audio_output_public_alloc_source import verify as verify_audio_output_public_alloc_source
from verify_gx8002_audio_output_public_free_source import verify as verify_audio_output_public_free_source
from verify_gx8002_audio_output_public_buffer_source import verify as verify_audio_output_public_buffer_source
from verify_gx8002_audio_output_public_pcm_source import verify as verify_audio_output_public_pcm_source
from verify_gx8002_audio_output_public_cb_source import verify as verify_audio_output_public_cb_source
from verify_gx8002_audio_output_public_frame_source import verify as verify_audio_output_public_frame_source
from verify_gx8002_audio_output_public_db_source import verify as verify_audio_output_public_db_source
from verify_gx8002_audio_output_public_channel_source import verify as verify_audio_output_public_channel_source
from verify_gx8002_audio_output_public_exit_source import verify as verify_audio_output_public_exit_source
from verify_gx8002_audio_output_suspend_source import verify as verify_audio_output_suspend_source
from verify_gx8002_audio_output_resume_source import verify as verify_audio_output_resume_source
from verify_gx8002_audio_output_exit_source import verify as verify_audio_output_exit_source
from verify_gx8002_audio_output_callbacks_source import verify as verify_audio_output_callbacks_source
from verify_gx8002_audio_output_mute_source import verify as verify_audio_output_mute_source
from verify_gx8002_audio_output_fixed_source import verify as verify_audio_output_fixed_source
from verify_gx8002_audio_output_config_i2s_source import verify as verify_audio_output_config_i2s_source
from verify_gx8002_audio_output_lodac_source import verify as verify_audio_output_lodac_source
from verify_gx8002_audio_output_i2s_config_source import verify as verify_audio_output_i2s_config_source
from verify_gx8002_audio_output_dac_source import verify as verify_audio_output_dac_source
from verify_gx8002_audio_output_config_dac_source import verify as verify_audio_output_config_dac_source
from verify_gx8002_uart_receive_complete_source import verify as verify_uart_receive_complete_source
from verify_gx8002_uart_dma_burst_source import verify as verify_uart_dma_burst_source
from verify_gx8002_dma_initialize_source import verify as verify_dma_initialize_source
from verify_gx8002_dma_irq_handler_source import verify as verify_dma_irq_handler_source
from verify_gx8002_dma_deallocate_source import verify as verify_dma_deallocate_source
from verify_gx8002_dma_select_source import verify as verify_dma_select_source
from verify_gx8002_dma_callback_source import verify as verify_dma_callback_source
from verify_gx8002_dma_configure_source import verify as verify_dma_configure_source
from verify_gx8002_dma_descriptors_source import verify as verify_dma_descriptors_source
from verify_gx8002_dma_bus_address_source import verify as verify_dma_bus_address_source
from verify_gx8002_board_pin_source import verify as verify_board_pin_source
from verify_gx8002_board_pin_setup_source import verify as verify_board_pin_setup_source
from verify_gx8002_board_pin_initialize_source import verify as verify_board_pin_initialize_source
from verify_gx8002_board_pin_initialize_error import verify as verify_board_pin_initialize_error
from verify_gx8002_board_pin_defaults import verify as verify_board_pin_defaults
from verify_gx8002_gsensor_workstate_source import verify as verify_gsensor_workstate
from verify_gx8002_channel_lookup_source import verify as verify_channel_lookup
from verify_gx8002_gsensor_workstate_message import verify as verify_gsensor_workstate_message
from verify_gx8002_board_pin_setup_error import verify as verify_board_pin_setup_error
from verify_gx8002_board_pin_error import verify as verify_board_pin_error
from verify_gx8002_clock_divider import verify as verify_clock_divider
from verify_gx8002_clock_frequency_source import verify as verify_clock_frequency
from verify_gx8002_uart_transmit_complete import verify as verify_uart_transmit_complete
from verify_gx8002_backup_uart_transmit_source import verify as verify_backup_uart_transmit
from verify_gx8002_backup_uart_receive_source import verify as verify_backup_uart_receive
from verify_gx8002_backup_dma_shared_source import verify as verify_backup_dma_shared
from verify_gx8002_backup_preserve_memory_source import verify as verify_backup_preserve_memory
from verify_gx8002_backup_status_source import verify as verify_backup_status
from verify_gx8002_backup_clear_bss_source import verify as verify_backup_clear_bss
from verify_gx8002_backup_irq_entry_source import verify as verify_backup_irq_entry
from verify_gx8002_backup_dma_configure_source import verify as verify_backup_dma_configure
from verify_gx8002_backup_dma_descriptors_source import verify as verify_backup_dma_descriptors
from verify_gx8002_backup_dma_bus_address_source import verify as verify_backup_dma_bus_address
from verify_gx8002_backup_dma_select_source import verify as verify_backup_dma_select
from verify_gx8002_backup_irq_state_source import verify as verify_backup_irq_state
from verify_gx8002_backup_clock_lookup_source import verify as verify_backup_clock_lookup
from verify_gx8002_backup_platform_gate_source import verify as verify_backup_platform_gate
from verify_gx8002_backup_clock_frequency_source import verify as verify_backup_clock_frequency
from verify_gx8002_backup_platform_read_source import verify as verify_backup_platform_read
from verify_gx8002_backup_rfft_source import verify as verify_backup_rfft
from verify_gx8002_backup_cfft_source import verify as verify_backup_cfft
from verify_gx8002_backup_request_irq_source import verify as verify_backup_request_irq
from verify_gx8002_backup_dma_initialize_source import verify as verify_backup_dma_initialize
from verify_gx8002_backup_dma_callback_source import verify as verify_backup_dma_callback
from verify_gx8002_backup_dma_abort_source import verify as verify_backup_dma_abort
from verify_gx8002_backup_dma_release_source import verify as verify_backup_dma_release
from verify_gx8002_backup_dma_transfer_source import verify as verify_backup_dma_transfer
from verify_gx8002_uart_flush import verify as verify_uart_flush
from verify_gx8002_dma_release import verify as verify_dma_release
from gx8002_source_tail_data import partition as partition_tail_data
from verify_gx8002_dcache_clean_range import verify as verify_dcache_clean_range
from verify_gx8002_snpu_task_cmd_cache_flush import verify as verify_snpu_task_cmd_cache_flush
from verify_gx8002_start_mode import verify as verify_start_mode
from verify_gx8002_system_initialize import verify as verify_system_initialize
from verify_gx8002_clear_bss import verify as verify_clear_bss
from verify_gx8002_startup import startup as verify_startup, reboot as verify_reboot

ROOT = Path(__file__).resolve().parents[1]


def reviewed_replacements(report, reviewed, obj, kind):
    if report != reviewed:
        raise ValueError(f'{kind}: qualification report differs from reviewed source admission baseline')
    elf = Elf32(obj.read_bytes(), str(obj))
    rows = report['functions'] if 'functions' in report else [report]
    replacements = []
    for row in rows:
        symbol = row['symbol'] if 'symbol' in row else ('gx_dcache_enable' if kind == 'csi' else 'gx_icache_enable')
        section_name = row.get('section_name', '.text.' + symbol)
        section = next(s for s in elf.sections if s['name'] == section_name)
        ownership_kind = row.get('ownership_kind', 'compiled_c')
        if ownership_kind not in ('compiled_c', 'compiled_assembly', 'generated_source_data'):
            raise ValueError('unsupported source ownership kind')
        if bool(section['flags'] & 4) != (ownership_kind in ('compiled_c', 'compiled_assembly')):
            raise ValueError('source ownership does not match executable section flag')
        payload = elf.contents(section)
        if sha(payload) != row['compiled_sha256'] or len(payload) != row['compiled_bytes']:
            raise ValueError('target object changed after verification')
        if elf.relocations(section['index']):
            raise ValueError('unresolved target relocation')
        matches = row['exact_stock_occurrences'] if kind == 'csi' else row['stock_occurrences']
        for match in matches:
            if len(payload) > match['bytes'] or match['package_offset'] % section['align']:
                raise ValueError('compiled function does not fit the aligned stock envelope')
            replacements.append({**match, 'payload': payload + bytes(match['bytes']-len(payload)),
                                 'compiled_bytes':len(payload), 'compiled_sha256': sha(payload),
                                 'ownership_kind': ownership_kind})
    return replacements


def compose(stock, replacements):
    if len(stock) != 326092 or sha(stock) != IMAGE_SHA:
        raise ValueError('codec baseline changed')
    parsed = parse_fwpk(stock)
    boot_record, main_record = parsed['records']
    boot_start = boot_record['offset']
    parse_boot_image(stock[boot_start:boot_start + boot_record['size']])
    parse_main_image(stock[main_record['offset']:])
    output = bytearray(stock)
    ownership = [{'offset': 0, 'size': 80, 'kind': 'generated_container_metadata'}]
    last = 80
    for replacement in sorted(replacements, key=lambda r: r['package_offset']):
        offset, size, payload = replacement['package_offset'], replacement['bytes'], replacement['payload']
        code_size = replacement.get('compiled_bytes', size)
        ownership_kind = replacement.get('ownership_kind', 'compiled_c')
        if ownership_kind not in ('compiled_c', 'compiled_assembly', 'generated_source_data'):
            raise ValueError('unsupported source ownership kind')
        if ownership_kind == 'generated_source_data' and code_size != size:
            raise ValueError('data replacement cannot claim unreachable code fill')
        if offset < last or offset + size > len(stock):
            raise ValueError('overlapping or out-of-bounds source replacement')
        if len(payload) != size or sha(stock[offset:offset+size]) != replacement['sha256']:
            raise ValueError('source replacement envelope or stock authentication changed')
        if not 0 < code_size <= size or sha(payload[:code_size]) != replacement['compiled_sha256']:
            raise ValueError('compiled source payload changed')
        if payload[code_size:] != bytes(size-code_size):
            raise ValueError('unreachable envelope fill changed')
        if offset > last:
            ownership.append({'offset': last, 'size': offset-last, 'kind': 'retained_stock'})
        output[offset:offset+size] = payload
        ownership.append({'offset': offset, 'size': code_size, 'kind': ownership_kind,
                          'symbol': replacement['symbol'], 'sha256': sha(payload[:code_size])})
        if code_size < size:
            ownership.append({'offset':offset+code_size, 'size':size-code_size,
                              'kind':'generated_unreachable_fill', 'symbol':replacement['symbol']})
        last = offset + size
    if last < len(stock):
        ownership.append({'offset': last, 'size': len(stock)-last, 'kind': 'retained_stock'})
    # Rebuild image-A padding and trailer after executable replacements.
    from generate_gx8002_image_a_tail import generate, PAD, CRC, XIP
    tail = generate(output)
    rebuilt_ownership = []
    for item in ownership:
        low, high = item['offset'], item['offset'] + item['size']
        if high <= PAD or low >= XIP:
            rebuilt_ownership.append(item)
            continue
        if item['kind'] != 'retained_stock':
            raise ValueError('Image-A generated tail overlaps another source owner')
        if low < PAD:
            rebuilt_ownership.append({**item, 'size': PAD-low})
        if high > XIP:
            rebuilt_ownership.append({**item, 'offset': XIP, 'size': high-XIP})
    output[PAD:XIP] = tail
    rebuilt_ownership.extend([
        {'offset': PAD, 'size': CRC-PAD, 'kind': 'generated_source_data',
         'symbol': 'image_a_stage1_zero_padding', 'sha256': sha(tail[:CRC-PAD])},
        {'offset': CRC, 'size': XIP-CRC, 'kind': 'generated_container_metadata',
         'symbol': 'image_a_stage1_crc_and_xip_extent', 'sha256': sha(tail[CRC-PAD:])}])
    ownership = sorted(rebuilt_ownership, key=lambda item: item['offset'])
    # Generate the complete UART header from reviewed fields, updating stage-2 sum.
    stage2 = output[0x2850:0x958c]
    uart = struct.pack('<HBBHBB', 0x8002, 1, 1, 0, 0, 0)
    uart += struct.pack('>IIII', 0x2800, 1500000, len(stage2), sum(stage2) & 0xffffffff)
    uart += bytes(8)
    output[48:80] = uart
    # Generate the complete FWPK header/table; both segment checksums cover new code.
    header = struct.pack('<4sIII', b'FWPK', 0x203, 2, 0)
    for record in parsed['records']:
        segment = output[record['offset']:record['offset']+record['size']]
        header += struct.pack('<IIII', record['type'], record['size'], record['offset'], zlib.crc32(segment) & 0xffffffff)
    output[:48] = header
    validate_codec(bytes(output))
    if struct.unpack_from('>I', output, 68)[0] != sum(output[0x2850:0x958c]) & 0xffffffff:
        raise ValueError('UART stage-2 checksum does not cover rebuilt code')
    parse_main_image(output[main_record['offset']:], verify_stock_identity=False)  # Validate regenerated BINH CRC/structure; application literals may be recompiled.
    for item in ownership:
        low, high = item['offset'], item['offset'] + item['size']
        if item['kind'] == 'retained_stock' and output[low:high] != stock[low:high]:
            raise ValueError('an unowned byte changed')
    totals = {kind: sum(r['size'] for r in ownership if r['kind'] == kind)
              for kind in ('compiled_c', 'compiled_assembly', 'generated_source_data', 'generated_container_metadata', 'generated_unreachable_fill', 'retained_stock')}
    if sum(totals.values()) != len(output):
        raise ValueError('ownership map does not close')
    return bytes(output), ownership, totals


def build(prefix, sdk, output):
    output.mkdir(parents=True, exist_ok=True)
    replacements = []
    tail_allocations = []
    for kind, verifier, artifact, baseline in (
        ('analog', verify_analog, 'runtime_gx8002_analog.o', 'gx8002-analog-source-verification.json'),
        ('csi', verify_csi, 'runtime_gx8002_dcache_enable.o', 'gx8002-csi-source-verification.json'),
        ('icache', verify_icache, 'runtime_gx8002_icache_enable.o', 'gx8002-icache-source-verification.json'),
        ('i2s', verify_i2s, 'runtime_gx8002_i2s.o', 'gx8002-i2s-source-verification.json'),
        ('vad', verify_vad, 'runtime_gx8002_vad_curves.o', 'gx8002-vad-source-verification.json'),
        ('crc', verify_crc, 'crc32.elf', 'gx8002-crc32-source-verification.json'),
        ('console', verify_console, 'console.elf', 'gx8002-uart-console-verification.json'),
        ('formatter', verify_formatter, 'formatter.elf', 'gx8002-formatter-verification.json'),
        ('printf', verify_printf, 'printf.elf', 'gx8002-printf-verification.json'),
        ('fputc', verify_fputc, 'fputc.elf', 'gx8002-fputc-verification.json'),
        ('uart_tick', verify_uart_tick, 'tick.elf', 'gx8002-uart-tick-verification.json'),
        ('app_tick', verify_app_tick, 'tick.elf', 'gx8002-app-tick-verification.json'),
        ('power_registration', verify_power_registration, 'registration.elf', 'gx8002-power-registration-verification.json'),
        ('irq', verify_irq, 'irq.elf', 'gx8002-irq-verification.json'),
        ('clock', verify_clock, 'tables.elf', 'gx8002-clock-source-verification.json'),
        ('gate', verify_gate, 'gate.elf', 'gx8002-platform-gate-verification.json'),
        ('watchdog_initialize', verify_watchdog_initialize, 'watchdog.elf', 'gx8002-watchdog-initialize-verification.json'),
        ('startup', verify_startup, 'startup.elf', 'gx8002-startup-verification.json'),
        ('reboot', verify_reboot, 'reboot.elf', 'gx8002-reboot-verification.json'),
        ('clear-bss', verify_clear_bss, 'clear-bss.elf', 'gx8002-clear-bss-verification.json'),
        ('system', verify_system_initialize, 'system.elf', 'gx8002-system-initialize-verification.json'),
        ('start-mode', verify_start_mode, 'mode.elf', 'gx8002-start-mode-verification.json'),
        ('transport', verify_flash_transport, 'transport.elf', 'gx8002-flash-transport-verification.json'),
        ('flash-status', verify_flash_status, 'status.elf', 'gx8002-flash-status-verification.json'),
        ('flash-device', verify_flash_device, 'device.elf', 'gx8002-flash-device-verification.json'),
        ('flash-quad', verify_flash_quad, 'quad.elf', 'gx8002-flash-quad-verification.json'),
        ('flash-xip', verify_flash_xip, 'xip.elf', 'gx8002-flash-xip-verification.json'),
        ('platform-config', verify_platform_config, 'config.elf', 'gx8002-platform-config-verification.json'),
        ('flash-discover', verify_flash_discover, 'discover.elf', 'gx8002-flash-discover-verification.json'),
        ('flash-word-io', verify_flash_word_io, 'word-io.elf', 'gx8002-flash-word-io-verification.json'),
        ('flash-info', verify_flash_info, 'info.elf', 'gx8002-flash-info-verification.json'),
        ('flash-otp-region', verify_flash_otp_region, 'otp-region.elf', 'gx8002-flash-otp-region-verification.json'),
        ('flash-address', verify_flash_address, 'address.elf', 'gx8002-flash-address-verification.json'),
        ('flash-otp-descriptor', verify_flash_otp_descriptor, 'otp-descriptor.o', 'gx8002-flash-otp-descriptor-verification.json'),
        ('flash-state', verify_flash_state, 'flash-state.o', 'gx8002-flash-state-verification.json'),
        ('flash-protection', verify_flash_protection, 'protection.elf', 'gx8002-flash-protection-verification.json'),
        ('flash-protection-set', verify_flash_protection_set, 'protection-set.elf', 'gx8002-flash-protection-set-verification.json'),
        ('flash-protection-tables', verify_flash_protection_tables, 'protection-tables.o', 'gx8002-flash-protection-tables-verification.json'),
        ('flash-protection-initialize', verify_flash_protection_initialize, 'protection-initialize.elf', 'gx8002-flash-protection-initialize-verification.json'),
        ('flash-interrupt', verify_flash_interrupt, 'flash-interrupt.elf', 'gx8002-flash-interrupt-verification.json'),
        ('flash-interface-initialize', verify_flash_interface_initialize, 'flash-interface.elf', 'gx8002-flash-interface-initialize-verification.json'),
        ('flash-erase', verify_flash_erase, 'erase.elf', 'gx8002-flash-erase-verification.json'),
        ('flash-read', verify_flash_read, 'read.elf', 'gx8002-flash-read-verification.json'),
        ('flash-page-program', verify_flash_page_program, 'page-program.elf', 'gx8002-flash-page-program-verification.json'),
        ('flash-block-range', verify_flash_block_range, 'block-range.elf', 'gx8002-flash-block-range-verification.json'),
        ('flash-otp-status', verify_flash_otp_status, 'otp-status.elf', 'gx8002-flash-otp-status-verification.json'),
        ('flash-otp-lock', verify_flash_otp_lock, 'otp-lock.elf', 'gx8002-flash-otp-lock-verification.json'),
        ('flash-otp-erase', verify_flash_otp_erase, 'otp-erase.elf', 'gx8002-flash-otp-erase-verification.json'),
        ('flash-otp-transmit', verify_flash_otp_transmit, 'otp-transmit.elf', 'gx8002-flash-otp-transmit-verification.json'),
        ('flash-otp-write', verify_flash_otp_write, 'otp-write.elf', 'gx8002-flash-otp-write-verification.json'),
        ('flash-otp-read', verify_flash_otp_read, 'otp-read.elf', 'gx8002-flash-otp-read-verification.json'),
        ('flash-uid-read', verify_flash_uid_read, 'uid-read.elf', 'gx8002-flash-uid-read-verification.json'),
        ('flash-interface-table', verify_flash_interface_table, 'flash-interface-table.elf', 'gx8002-flash-interface-table-verification.json'),
        ('flash-device-names', verify_flash_device_names, 'flash-device-names.o', 'gx8002-flash-device-names-verification.json'),
        ('flash-initialize', verify_flash_initialize, 'flash.elf', 'gx8002-flash-initialize-verification.json'),
        ('board-initialize', verify_board_initialize, 'board.elf', 'gx8002-board-initialize-verification.json'),
        ('irq-compact', verify_irq_compact, 'compact.elf', 'gx8002-irq-compact-admission.json'),
        ('reset-entry', verify_reset_entry, 'reset-entry.elf', 'gx8002-reset-entry-verification.json'),
        ('main', verify_main, 'main.elf', 'gx8002-main-verification.json'),
        ('mode', verify_mode, 'mode.elf', 'gx8002-mode-verification.json'),
        ('idle', verify_idle, 'idle.elf', 'gx8002-idle-verification.json'),
        ('tws', verify_tws, 'tws.elf', 'gx8002-tws-verification.json'),
        ('kws-insert', verify_kws_insert, 'kws-insert.elf', 'gx8002-kws-insert-verification.json'),
        ('wakeword-parameters', verify_wakeword_parameters, 'wakeword-parameters.o', 'gx8002-wakeword-parameters-verification.json'),
        ('memset', verify_memset, 'memset.elf', 'gx8002-memset-verification.json'),
        ('kws-reset', verify_kws_reset, 'kws-reset.elf', 'gx8002-kws-reset-verification.json'),
        ('max-initialize', verify_max_initialize, 'max-initialize.elf', 'gx8002-max-initialize-verification.json'),
        ('max-list', verify_max_list, 'max-list.elf', 'gx8002-max-list-verification.json'),
        ('max-score', verify_max_score_source, 'max-score.elf', 'gx8002-max-score-source-verification.json'),
        ('max-decoder', verify_max_decoder_source, 'max-decoder.elf', 'gx8002-max-decoder-source-verification.json'),
        ('kws-strategy', verify_kws_strategy_source, 'kws-strategy.elf', 'gx8002-kws-strategy-source-verification.json'),
        ('bionic-offsets', verify_bionic_offsets, 'offsets.elf', 'gx8002-bionic-offsets-verification.json'),
        ('bionic-run', verify_bionic_run_source, 'bionic-run.elf', 'gx8002-bionic-run-source-verification.json'),
        ('next-range', verify_next_range_source, 'next-range.elf', 'gx8002-next-range-source-verification.json'),
        ('app-gpio-power', verify_app_gpio_power, 'gpio-power.elf', 'gx8002-app-gpio-power-verification.json'),
        ('app-gpio-event', verify_app_gpio_event_source, 'app-gpio-event.elf', 'gx8002-app-gpio-event-source-verification.json'),
        ('sample-app-init', verify_sample_app_init_source, 'sample-app-init.elf', 'gx8002-sample-app-init-source-verification.json'),
        ('sample-event', verify_sample_event_source, 'sample-event.elf', 'gx8002-sample-event-source-verification.json'),
        ('start-i2s', verify_start_i2s_source, 'start-i2s.elf', 'gx8002-start-i2s-source-verification.json'),
        ('stop-i2s', verify_stop_i2s_source, 'stop-i2s.elf', 'gx8002-stop-i2s-source-verification.json'),
        ('i2s-request-tick', verify_i2s_request_tick_source, 'i2s-request-tick.elf', 'gx8002-i2s-request-tick-source-verification.json'),
        ('app-commands', verify_app_commands_source, 'app-commands.elf', 'gx8002-app-commands-source-verification.json'),
        ('app-reply', verify_app_reply_source, 'app-reply.elf', 'gx8002-app-reply-source-verification.json'),
        ('app-command-callback-persistent', verify_app_callback_source, 'app-command-callback-persistent.elf', 'gx8002-app-command-callback-persistent-source-verification.json'),
        ('notification-setup', verify_notification_setup_source, 'notification-setup.elf', 'gx8002-notification-setup-source-verification.json'),
        ('notification-stamp', verify_notification_stamp_source, 'notification-stamp.elf', 'gx8002-notification-stamp-source-verification.json'),
        ('event-notify', verify_event_notify_source, 'event-notify.elf', 'gx8002-event-notify-source-verification.json'),
        ('fpadd-parts', verify_fpadd_parts_source, 'fpadd-parts.elf', 'gx8002-fpadd-parts-source-verification.json'),
        ('adddf3', verify_adddf3_source, 'adddf3.elf', 'gx8002-adddf3-source-verification.json'),
        ('uart-transmit-dma-placement', verify_uart_transmit_dma_placement_source, 'uart-transmit-dma-placement.elf', 'gx8002-uart-transmit-dma-placement-source-verification.json'),
        ('clock-source-select', verify_clock_source_select_source, 'clock-source-select.elf', 'gx8002-clock-source-select-source-verification.json'),
        ('clock-module-dto-set', verify_clock_module_dto_set_source, 'clock-module-dto-set.elf', 'gx8002-clock-module-dto-set-source-verification.json'),
        ('clock-module-divider-set', verify_clock_module_divider_set_source, 'clock-module-divider-set.elf', 'gx8002-clock-module-divider-set-source-verification.json'),
        ('clock-module-query', verify_clock_module_query_source, 'clock-module-query.elf', 'gx8002-clock-module-query-source-verification.json'),
        ('clock-module-source-fixed', verify_clock_module_source_fixed_source, 'clock-module-source-fixed.elf', 'gx8002-clock-module-source-fixed-source-verification.json'),
        ('timer-dispatch', verify_timer_dispatch_source, 'timer-dispatch.elf', 'gx8002-timer-dispatch-source-verification.json'),
        ('delay', verify_delay_source, 'delay.elf', 'gx8002-delay-source-verification.json'),
        ('trim-state', verify_trim_state_source, 'trim-state.elf', 'gx8002-trim-state-source-verification.json'),
        ('trim-clock-enable', verify_trim_clock_enable_source, 'trim-clock-enable.elf', 'gx8002-trim-clock-enable-source-verification.json'),
        ('digital-voltage', verify_digital_voltage_source, 'digital-voltage.elf', 'gx8002-digital-voltage-source-verification.json'),
        ('analog-voltage', verify_analog_voltage_source, 'analog-voltage.elf', 'gx8002-analog-voltage-source-verification.json'),
        ('digital-control', verify_digital_control_source, 'digital-control.elf', 'gx8002-digital-control-source-verification.json'),
        ('flash-read-api', verify_flash_read_api_source, 'flash-read-api.elf', 'gx8002-flash-read-api-source-verification.json'),
        ('flash-type-api', verify_flash_type_api_source, 'flash-type-api.elf', 'gx8002-flash-type-api-source-verification.json'),
        ('flash-probe', verify_flash_probe_source, 'flash-probe.elf', 'gx8002-flash-probe-source-verification.json'),
        ('dcache-invalid-range', verify_dcache_invalid_range_source, 'dcache-invalid-range.elf', 'gx8002-dcache-invalid-range-source-verification.json'),
        ('dcache-clean-invalid-range', verify_dcache_clean_invalid_range_source, 'dcache-clean-invalid-range.elf', 'gx8002-dcache-clean-invalid-range-source-verification.json'),
        ('timer-initialize', verify_timer_initialize_source, 'timer-initialize.elf', 'gx8002-timer-initialize-source-verification.json'),
        ('timer-channel-initialize', verify_timer_channel_initialize_source, 'timer-channel-initialize.elf', 'gx8002-timer-channel-initialize-source-verification.json'),
        ('flash-info-api', verify_flash_info_api_source, 'flash-info-api.elf', 'gx8002-flash-info-api-source-verification.json'),
        ('flash-otp-configuration', verify_flash_otp_configuration_source, 'flash-otp-configuration.elf', 'gx8002-flash-otp-configuration-source-verification.json'),
        ('otp-lowpower-enter', verify_otp_lowpower_enter_source, 'otp-lowpower-enter.elf', 'gx8002-otp-lowpower-enter-source-verification.json'),
        ('tws-tick', verify_tws_tick_source, 'tws-tick.elf', 'gx8002-tws-tick-source-verification.json'),
        ('audio-irq', verify_audio_irq_source, 'irq.elf', 'gx8002-audio-irq-source-verification.json'),
        ('tws-audio', verify_tws_audio_source, 'audio.elf', 'gx8002-tws-audio-source-verification.json'),
        ('tws-standby', verify_tws_standby_source, 'standby.elf', 'gx8002-tws-standby-source-verification.json'),
        ('active-snpu', verify_active_snpu_source, 'active-snpu.elf', 'gx8002-active-snpu-source-verification.json'),
        ('audio-record', verify_audio_record_source, 'audio-record.elf', 'gx8002-audio-record-source-verification.json'),
        ('kws-pair', verify_kws_pair_source, 'kws-pair.elf', 'gx8002-kws-pair-source-verification.json'),
        ('platform-read', verify_platform_read_source, 'platform-read.elf', 'gx8002-platform-read-source-verification.json'),
        ('flash-otp-read-api', verify_flash_otp_read_api_source, 'flash-otp-read-api.elf', 'gx8002-flash-otp-read-api-source-verification.json'),
        ('dcache-disable-upstream', verify_dcache_disable_upstream_source, 'dcache-disable-upstream.elf', 'gx8002-dcache-disable-upstream-source-verification.json'),
        ('clock-init', verify_clock_init_source, 'clock-init.elf', 'gx8002-clock-init-source-verification.json'),
        ('clock-switch-1m', verify_clock_switch_1m_source, 'clock-switch-1m.elf', 'gx8002-clock-switch-1m-source-verification.json'),
        ('clock-gate-query-fixed', verify_clock_gate_query_source, 'clock-gate-query-fixed.elf', 'gx8002-clock-gate-query-fixed-source-verification.json'),
        ('audio-lowpower-divider', verify_audio_lowpower_divider_source, 'audio-lowpower-divider.elf', 'gx8002-audio-lowpower-divider-source-verification.json'),
        ('clock-lowpower-init-shared', verify_clock_lowpower_init_source, 'clock-lowpower-init-shared.elf', 'gx8002-clock-lowpower-init-shared-source-verification.json'),
        ('clock-time-ms', verify_clock_time_ms_source, 'clock-time-ms.elf', 'gx8002-clock-time-ms-source-verification.json'),
        ('clock-time-us', verify_clock_time_us_source, 'clock-time-us.elf', 'gx8002-clock-time-us-source-verification.json'),
        ('clock-pll-wait', verify_clock_pll_wait_source, 'clock-pll-wait.elf', 'gx8002-clock-pll-wait-source-verification.json'),
        ('clock-pll', verify_clock_pll_source, 'clock-pll.elf', 'gx8002-clock-pll-source-verification.json'),
        ('audio-board-control', verify_audio_board_control_source, 'audio-board-control.elf', 'gx8002-audio-board-control-source-verification.json'),
        ('audio-board-storage', verify_audio_board_storage_source, 'storage.elf', 'gx8002-audio-board-storage-source-verification.json'),
        ('uart-descriptors', verify_uart_descriptor_source, 'descriptors.elf', 'gx8002-uart-descriptor-source-verification.json'),
        ('distance-noise', verify_distance_noise_source, 'noise.elf', 'gx8002-distance-noise-source-verification.json'),
        ('exception', verify_exception_source, 'exception.elf', 'gx8002-exception-source-verification.json'),
        ('keyword-list-get', verify_keyword_list_get_source, 'get.elf', 'gx8002-keyword-list-get-source-verification.json'),
        ('irq-save-disable-wrapper', verify_irq_save_disable_wrapper_source, 'wrapper.elf', 'gx8002-irq-save-disable-wrapper-source-verification.json'),
        ('audio-api-labels', verify_audio_api_labels_source, 'labels.elf', 'gx8002-audio-api-labels-source-verification.json'),
        ('application-labels', verify_application_labels_source, 'labels.elf', 'gx8002-application-labels-source-verification.json'),
        ('audio-mapping-tables', verify_audio_mapping_tables_source, 'tables.elf', 'gx8002-audio-mapping-tables-source-verification.json'),
        ('mode-descriptors', verify_mode_descriptors_source, 'descriptors.elf', 'gx8002-mode-descriptors-source-verification.json'),
        ('event-defaults', verify_event_defaults_source, 'defaults.elf', 'gx8002-event-defaults-source-verification.json'),
        ('decoder-default', verify_decoder_default_source, 'defaults.elf', 'gx8002-decoder-default-source-verification.json'),
        ('application-descriptor', verify_application_descriptor_source, 'descriptor.elf', 'gx8002-application-descriptor-source-verification.json'),
        ('uart-header-defaults', verify_uart_header_defaults_source, 'defaults.elf', 'gx8002-uart-header-defaults-source-verification.json'),
        ('reply-defaults', verify_reply_defaults_source, 'defaults.elf', 'gx8002-reply-defaults-source-verification.json'),
        ('board-gain-data', verify_board_gain_data_source, 'board-gain-data.elf', 'gx8002-board-gain-data-source-verification.json'),
        ('runtime-messages', verify_runtime_messages_source, 'runtime-messages.elf', 'gx8002-runtime-messages-source-verification.json'),
        ('application-vectors', verify_application_vectors_source, 'application-vectors.elf', 'gx8002-application-vectors-source-verification.json'),
        ('udivdi3', verify_udivdi3_source, 'udivdi3.elf', 'gx8002-udivdi3-source-verification.json'),
        ('divdf3-fixed', verify_divdf3_fixed_source, 'divdf3-fixed.elf', 'gx8002-divdf3-fixed-source-verification.json'),
        ('muldf3-fixed', verify_muldf3_fixed_source, 'muldf3-fixed.elf', 'gx8002-muldf3-fixed-source-verification.json'),
        ('subdf3', verify_subdf3_source, 'subdf3.elf', 'gx8002-subdf3-source-verification.json'),
        ('muldi3', verify_muldi3_source, 'muldi3.elf', 'gx8002-muldi3-source-verification.json'),
        ('pack-double', verify_pack_double_source, 'pack-double.elf', 'gx8002-pack-double-source-verification.json'),
        ('floatunsidf', verify_floatunsidf_source, 'floatunsidf.elf', 'gx8002-floatunsidf-source-verification.json'),
        ('fixdfsi', verify_fixdfsi_source, 'fixdfsi.elf', 'gx8002-fixdfsi-source-verification.json'),
        ('unpack-double', verify_unpack_double_source, 'unpack-double.elf', 'gx8002-unpack-double-source-verification.json'),
        ('fpcmp-parts', verify_fpcmp_parts_source, 'fpcmp-parts.elf', 'gx8002-fpcmp-parts-source-verification.json'),
        ('gedf2', verify_gedf2_source, 'gedf2.elf', 'gx8002-gedf2-source-verification.json'),
        ('fixunsdfsi', verify_fixunsdfsi_source, 'fixunsdfsi.elf', 'gx8002-fixunsdfsi-source-verification.json'),
        ('div64', verify_div64_source, 'div64.elf', 'gx8002-div64-source-verification.json'),
        ('strtok', verify_strtok_source, 'strtok.elf', 'gx8002-strtok-source-verification.json'),
        ('i2s-ack', verify_i2s_ack_source, 'i2s-ack.elf', 'gx8002-i2s-ack-source-verification.json'),
        ('vad-notify', verify_vad_notify_source, 'vad-notify.elf', 'gx8002-vad-notify-source-verification.json'),
        ('notification-poll', verify_notification_poll_source, 'notification-poll.elf', 'gx8002-notification-poll-source-verification.json'),
        ('mic-buffer', verify_mic_buffer_source, 'mic-buffer.elf', 'gx8002-mic-buffer-source-verification.json'),
        ('tws-shutdown', verify_tws_shutdown, 'tws-shutdown.elf', 'gx8002-tws-shutdown-verification.json'),
        ('stream-shutdown', verify_stream_shutdown, 'stream-shutdown.elf', 'gx8002-stream-shutdown-verification.json'),
        ('driver-exit', verify_driver_exit, 'driver-exit.elf', 'gx8002-driver-exit-verification.json'),
        ('audio-reset', verify_audio_reset, 'audio-reset.elf', 'gx8002-audio-reset-verification.json'),
        ('snpu-suspend', verify_snpu_suspend, 'snpu-suspend.elf', 'gx8002-snpu-suspend-verification.json'),
        ('irq-mask', verify_irq_mask, 'irq-mask.elf', 'gx8002-irq-mask-verification.json'),
        ('snpu-clock', verify_snpu_clock, 'snpu-clock.elf', 'gx8002-snpu-clock-verification.json'),
        ('npu-register', verify_npu_registers, 'npu-register.elf', 'gx8002-npu-register-verification.json'),
        ('npu-control', verify_npu_control, 'npu-control.elf', 'gx8002-npu-control-verification.json'),
        ('npu-accessor', verify_npu_accessors, 'npu-accessor.elf', 'gx8002-npu-accessor-verification.json'),
        ('npu-configuration', verify_npu_configuration, 'npu-configuration.elf', 'gx8002-npu-configuration-verification.json'),
        ('npu-interrupt-mask', verify_npu_interrupt_masks, 'npu-interrupt-mask.elf', 'gx8002-npu-interrupt-mask-verification.json'),
        ('npu-interrupt-status', verify_npu_interrupt_status, 'npu-interrupt-status.elf', 'gx8002-npu-interrupt-status-verification.json'),
        ('snpu-device', verify_snpu_device, 'snpu-device.elf', 'gx8002-snpu-device-verification.json'),
        ('npu-regs-init', verify_npu_regs_init, 'npu-regs-init.elf', 'gx8002-npu-regs-init-verification.json'),
        ('snpu-resume-internal', verify_snpu_resume_internal, 'snpu-resume-internal.elf', 'gx8002-snpu-resume-internal-verification.json'),
        ('snpu-initialize', verify_snpu_initialize, 'snpu-initialize.elf', 'gx8002-snpu-initialize-verification.json'),
        ('snpu-isr', verify_snpu_isr, 'snpu-isr.elf', 'gx8002-snpu-isr-verification.json'),
        ('snpu-process-status', verify_snpu_process_status, 'snpu-process-status.elf', 'gx8002-snpu-process-status-verification.json'),
        ('snpu-overtime', verify_snpu_overtime, 'snpu-overtime.elf', 'gx8002-snpu-overtime-verification.json'),
        ('snpu-tcb-init', verify_snpu_tcb_init, 'snpu-tcb-init.elf', 'gx8002-snpu-tcb-init-verification.json'),
        ('dcache-clean-range', verify_dcache_clean_range, 'dcache-clean-range.elf', 'gx8002-dcache-clean-range-verification.json'),
        ('snpu-task-cmd-cache-flush', verify_snpu_task_cmd_cache_flush, 'snpu-task-cmd-cache-flush.elf', 'gx8002-snpu-task-cmd-cache-flush-verification.json'),
        ('snpu-submit-task', verify_snpu_submit_task, 'snpu-submit-task.elf', 'gx8002-snpu-submit-task-verification.json'),
        ('snpu-run-task', verify_snpu_run_task, 'snpu-run-task.elf', 'gx8002-snpu-run-task-verification.json'),
        ('snpu-get-state', verify_snpu_get_state, 'snpu-get-state.elf', 'gx8002-snpu-get-state-verification.json'),
        ('gpio-isr', verify_gpio_isr, 'gpio-isr.elf', 'gx8002-gpio-isr-verification.json'),
        ('gpio-output', verify_gpio_output, 'gpio-output.elf', 'gx8002-gpio-output-verification.json'),
        ('gpio-trigger', verify_gpio_trigger, 'gpio-trigger.elf', 'gx8002-gpio-trigger-verification.json'),
        ('gpio-disable-trigger', verify_gpio_disable_trigger, 'gpio-disable-trigger.elf', 'gx8002-gpio-disable-trigger-verification.json'),
        ('gpio-initialize', verify_gpio_initialize, 'gpio-initialize.elf', 'gx8002-gpio-initialize-verification.json'),
        ('device-list-init', verify_device_list_init, 'device-list-init.elf', 'gx8002-device-list-init-verification.json'),
        ('spi-register-master', verify_spi_register_master, 'spi-register-master.elf', 'gx8002-spi-register-master-verification.json'),
        ('dw-spi-cleanup', verify_dw_spi_cleanup, 'dw-spi-cleanup.elf', 'gx8002-dw-spi-cleanup-verification.json'),
        ('dw-spi-setup', verify_dw_spi_setup, 'dw-spi-setup.elf', 'gx8002-dw-spi-setup-verification.json'),
        ('analog-config-update-enable', verify_analog_config_update_enable, 'analog-config-update-enable.o', 'gx8002-analog-config-update-enable-verification.json'),
        ('irq-boot-stage2-enable', verify_irq_boot_stage2_enable, 'irq.o', 'gx8002-irq-boot-stage2-enable-verification.json'),
        ('uart-boot-stage2-diagnostics', verify_uart_boot_stage2_diagnostics, 'uart-boot-stage2-diagnostics.o', 'gx8002-uart-boot-stage2-diagnostics-verification.json'),
        ('stage2-libc', verify_stage2_libc, 'stage2_libc.o', 'gx8002-stage2-libc-verification.json'),
        ('strncmp', verify_strncmp, 'strncmp.o', 'gx8002-strncmp-verification.json'),
        ('main-strlen', verify_main_strlen, 'main-strlen.o', 'gx8002-main-strlen-verification.json'),
        ('memmove', verify_memmove_source, 'memmove.elf', 'gx8002-memmove-source-verification.json'),
        ('kws-flash-load', verify_kws_flash_load_source, 'loader.elf', 'gx8002-kws-flash-load-source-verification.json'),
        ('kws-initialize', verify_kws_initialize, 'init.elf', 'gx8002-kws-initialize-verification.json'),
        ('audio-input-standby', verify_audio_input_standby_source, 'buffers.elf', 'gx8002-audio-input-standby-source-verification.json'),
        ('power-initialize', verify_power_initialize_source, 'buffers.elf', 'gx8002-power-initialize-source-verification.json'),
        ('power-locks', verify_power_locks_source, 'buffers.elf', 'gx8002-power-locks-source-verification.json'),
        ('power-lock-control', verify_power_lock_control_source, 'buffers.elf', 'gx8002-power-lock-control-source-verification.json'),
        ('power-suspend', verify_power_suspend_source, 'buffers.elf', 'gx8002-power-suspend-source-verification.json'),
        ('uart-receive-body-done', verify_uart_receive_body_done_source, 'buffers.elf', 'gx8002-uart-receive-body-done-source-verification.json'),
        ('uart-message-done', verify_uart_message_done_source, 'callback.elf', 'gx8002-uart-message-done-source-verification.json'),
        ('uart-message-initialize', verify_uart_message_initialize_source, 'callback.elf', 'gx8002-uart-message-initialize-source-verification.json'),
        ('uart-message-enqueue', verify_uart_message_enqueue_source, 'callback.elf', 'gx8002-uart-message-enqueue-source-verification.json'),
        ('uart-registration', verify_uart_registration_source, 'callback.elf', 'gx8002-uart-registration-source-verification.json'),
        ('uart-receive-callback', verify_uart_receive_callback_source, 'callback.elf', 'gx8002-uart-receive-callback-source-verification.json'),
        ('uart-send-callback', verify_uart_send_callback_source, 'callback.elf', 'gx8002-uart-send-callback-source-verification.json'),
        ('uart-receive-body', verify_uart_receive_body_source, 'body.elf', 'gx8002-uart-receive-body-source-verification.json'),
        ('uart-message-power', verify_uart_message_power_source, 'buffers.elf', 'gx8002-uart-message-power-source-verification.json'),
        ('uart-body-done', verify_uart_body_done_source, 'buffers.elf', 'gx8002-uart-body-done-source-verification.json'),
        ('uart-message-body', verify_uart_message_body_source, 'buffers.elf', 'gx8002-uart-message-body-source-verification.json'),
        ('uart-message-start', verify_uart_message_start_source, 'buffers.elf', 'gx8002-uart-message-start-source-verification.json'),
        ('multiboot-switch', verify_multiboot_switch_source, 'buffers.elf', 'gx8002-multiboot-switch-source-verification.json'),
        ('lvp-system-initialize', verify_lvp_system_initialize_source, 'buffers.elf', 'gx8002-lvp-system-initialize-source-verification.json'),
        ('audio-input-env-noise', verify_audio_input_env_noise_source, 'noise.elf', 'gx8002-audio-input-env-noise-source-verification.json'),
        ('audio-input-query-vad', verify_audio_input_query_vad_source, 'query.elf', 'gx8002-audio-input-query-vad-source-verification.json'),
        ('audio-input-init', verify_audio_input_init_source, 'init.elf', 'gx8002-audio-input-init-source-verification.json'),
        ('audio-input-state', verify_audio_input_state, 'state.elf', 'gx8002-audio-input-state-verification.json'),
        ('audio-input-config', verify_audio_input_config_source, 'config.elf', 'gx8002-audio-input-config-source-verification.json'),
        ('audio-input-output', verify_audio_input_output_source, 'output.elf', 'gx8002-audio-input-output-source-verification.json'),
        ('audio-input-buffers', verify_audio_input_buffers_source, 'buffers.elf', 'gx8002-audio-input-buffers-source-verification.json'),
        ('buffer-metadata', verify_buffer_metadata, 'metadata.elf', 'gx8002-buffer-metadata-verification.json'),
        ('mic-frame', verify_mic_frame, 'index.elf', 'gx8002-mic-frame-verification.json'),
        ('context-acquire', verify_context_acquire, 'context.elf', 'gx8002-context-acquire-verification.json'),
        ('logfbank-index', verify_logfbank_index, 'index.elf', 'gx8002-logfbank-index-verification.json'),
        ('buffer-accessors', verify_buffer_accessors, 'accessors.elf', 'gx8002-buffer-accessors-verification.json'),
        ('buffer-initialize', verify_buffer_initialize_source, 'buffer.elf', 'gx8002-buffer-initialize-source-verification.json'),
        ('dw-spi-irq', verify_dw_spi_irq, 'dw-spi-irq.elf', 'gx8002-dw-spi-irq-verification.json'),
        ('dw-spi-probe', verify_dw_spi_probe, 'dw-spi-probe.elf', 'gx8002-dw-spi-probe-verification.json'),
        ('dw-spi-quick-transfer', verify_dw_spi_quick_transfer, 'dw-spi-quick-transfer.elf', 'gx8002-dw-spi-quick-transfer-verification.json'),
        ('padmux-get', verify_padmux_get, 'padmux-get.elf', 'gx8002-padmux-get-verification.json'),
        ('padmux-check', verify_padmux_check, 'padmux-check.elf', 'gx8002-padmux-check-verification.json'),
        ('padmux-set', verify_padmux_set, 'padmux-set.elf', 'gx8002-padmux-set-verification.json'),
        ('padmux-init', verify_padmux_init, 'padmux-init.elf', 'gx8002-padmux-init-verification.json'),
        ('padmux-defaults', verify_padmux_defaults, 'padmux-defaults.o', 'gx8002-padmux-defaults-verification.json'),
        ('rtc-isr', verify_rtc_isr, 'rtc-isr.elf', 'gx8002-rtc-isr-verification.json'),
        ('rtc-start-tick', verify_rtc_start_tick, 'rtc-start-tick.elf', 'gx8002-rtc-start-tick-verification.json'),
        ('rtc-set-tick', verify_rtc_set_tick, 'rtc-set-tick.elf', 'gx8002-rtc-set-tick-verification.json'),
        ('rtc-error', verify_rtc_error, 'rtc-error.o', 'gx8002-rtc-error-verification.json'),
        ('rtc-init', verify_rtc_init_source, 'rtc-init.elf', 'gx8002-rtc-init-source-verification.json'),
        ('board-pin', verify_board_pin_source, 'board-pin.elf', 'gx8002-board-pin-source-verification.json'),
        ('board-pin-error', verify_board_pin_error, 'board-pin-error.o', 'gx8002-board-pin-error-verification.json'),
        ('board-pin-setup', verify_board_pin_setup_source, 'board-pin-setup.elf', 'gx8002-board-pin-setup-source-verification.json'),
        ('board-pin-setup-error', verify_board_pin_setup_error, 'board-pin-setup-error.o', 'gx8002-board-pin-setup-error-verification.json'),
        ('board-pin-initialize', verify_board_pin_initialize_source, 'board-pin-initialize.elf', 'gx8002-board-pin-initialize-source-verification.json'),
        ('board-pin-initialize-error', verify_board_pin_initialize_error, 'board-pin-initialize-error.o', 'gx8002-board-pin-initialize-error-verification.json'),
        ('board-pin-defaults', verify_board_pin_defaults, 'board-pin-defaults.o', 'gx8002-board-pin-defaults-verification.json'),
        ('gsensor-workstate', verify_gsensor_workstate, 'gsensor-workstate.elf', 'gx8002-gsensor-workstate-source-verification.json'),
        ('channel-lookup', verify_channel_lookup, 'channel-lookup.elf', 'gx8002-channel-lookup-source-verification.json'),
        ('gsensor-workstate-message', verify_gsensor_workstate_message, 'gsensor-workstate-message.o', 'gx8002-gsensor-workstate-message-verification.json'),
        ('clock-divider', verify_clock_divider, 'clock-divider.elf', 'gx8002-clock-divider-verification.json'),
        ('clock-frequency', verify_clock_frequency, 'clock-frequency.elf', 'gx8002-clock-frequency-source-verification.json'),
        ('uart-transmit-complete', verify_uart_transmit_complete, 'complete.elf', 'gx8002-uart-transmit-complete-verification.json'),
        ('backup-uart-transmit', verify_backup_uart_transmit, 'transmit.elf', 'gx8002-backup-uart-transmit-source-verification.json'),
        ('backup-uart-receive', verify_backup_uart_receive, 'receive.elf', 'gx8002-backup-uart-receive-source-verification.json'),
        ('backup-dma-shared', verify_backup_dma_shared, 'pair.elf', 'gx8002-backup-dma-shared-source-verification.json'),
        ('backup-preserve-memory', verify_backup_preserve_memory, 'predicate.elf', 'gx8002-backup-preserve-memory-source-verification.json'),
        ('backup-status', verify_backup_status, 'status.elf', 'gx8002-backup-status-source-verification.json'),
        ('backup-clear-bss', verify_backup_clear_bss, 'clear.elf', 'gx8002-backup-clear-bss-source-verification.json'),
        ('backup-irq-entry', verify_backup_irq_entry, 'entry.elf', 'gx8002-backup-irq-entry-source-verification.json'),
        ('backup-dma-configure', verify_backup_dma_configure, 'configure.elf', 'gx8002-backup-dma-configure-source-verification.json'),
        ('backup-dma-descriptors', verify_backup_dma_descriptors, 'descriptors.elf', 'gx8002-backup-dma-descriptors-source-verification.json'),
        ('backup-dma-bus-address', verify_backup_dma_bus_address, 'bus_address.elf', 'gx8002-backup-dma-bus-address-source-verification.json'),
        ('backup-dma-select', verify_backup_dma_select, 'select.elf', 'gx8002-backup-dma-select-source-verification.json'),
        ('backup-irq-state', verify_backup_irq_state, 'state.elf', 'gx8002-backup-irq-state-source-verification.json'),
        ('backup-clock-lookup', verify_backup_clock_lookup, 'tables.elf', 'gx8002-backup-clock-lookup-source-verification.json'),
        ('backup-platform-gate', verify_backup_platform_gate, 'gate.elf', 'gx8002-backup-platform-gate-source-verification.json'),
        ('backup-clock-frequency', verify_backup_clock_frequency, 'frequency.elf', 'gx8002-backup-clock-frequency-source-verification.json'),
        ('backup-platform-read', verify_backup_platform_read, 'platform-read.elf', 'gx8002-backup-platform-read-source-verification.json'),
        ('backup-rfft', verify_backup_rfft, 'rfft.elf', 'gx8002-backup-rfft-source-verification.json'),
        ('backup-cfft', verify_backup_cfft, 'cfft.elf', 'gx8002-backup-cfft-source-verification.json'),
        ('backup-request-irq', verify_backup_request_irq, 'request.elf', 'gx8002-backup-request-irq-source-verification.json'),
        ('backup-dma-initialize', verify_backup_dma_initialize, 'initialize.elf', 'gx8002-backup-dma-initialize-source-verification.json'),
        ('backup-dma-callback', verify_backup_dma_callback, 'callback.elf', 'gx8002-backup-dma-callback-source-verification.json'),
        ('backup-dma-abort', verify_backup_dma_abort, 'abort.elf', 'gx8002-backup-dma-abort-source-verification.json'),
        ('backup-dma-release', verify_backup_dma_release, 'release.elf', 'gx8002-backup-dma-release-source-verification.json'),
        ('backup-dma-transfer', verify_backup_dma_transfer, 'transfer.elf', 'gx8002-backup-dma-transfer-source-verification.json'),
        ('uart-flush', verify_uart_flush, 'flush.elf', 'gx8002-uart-flush-verification.json'),
        ('dma-bus-address', verify_dma_bus_address_source, 'bus_address.elf', 'gx8002-dma-bus-address-source-verification.json'),
        ('dma-descriptors', verify_dma_descriptors_source, 'descriptors.elf', 'gx8002-dma-descriptors-source-verification.json'),
        ('dma-configure', verify_dma_configure_source, 'configure.elf', 'gx8002-dma-configure-source-verification.json'),
        ('dma-callback', verify_dma_callback_source, 'callback.elf', 'gx8002-dma-callback-source-verification.json'),
        ('dma-select', verify_dma_select_source, 'select.elf', 'gx8002-dma-select-source-verification.json'),
        ('dma-deallocate', verify_dma_deallocate_source, 'deallocate.elf', 'gx8002-dma-deallocate-source-verification.json'),
        ('dma-irq-handler', verify_dma_irq_handler_source, 'irq_handler.elf', 'gx8002-dma-irq-handler-source-verification.json'),
        ('dma-initialize', verify_dma_initialize_source, 'initialize.elf', 'gx8002-dma-initialize-source-verification.json'),
        ('uart-dma-burst', verify_uart_dma_burst_source, 'burst.elf', 'gx8002-uart-dma-burst-source-verification.json'),
        ('uart-receive-complete', verify_uart_receive_complete_source, 'complete.elf', 'gx8002-uart-receive-complete-source-verification.json'),
        ('uart-receive-control', verify_uart_receive_control_source, 'control.elf', 'gx8002-uart-receive-control-source-verification.json'),
        ('uart-transmit-control', verify_uart_transmit_control_source, 'control.elf', 'gx8002-uart-transmit-control-source-verification.json'),
        ('uart-fifo-depth', verify_uart_fifo_depth_source, 'fifo_depth.elf', 'gx8002-uart-fifo-depth-source-verification.json'),
        ('uart-read', verify_uart_read_source, 'read.elf', 'gx8002-uart-read-source-verification.json'),
        ('uart-write', verify_uart_write_source, 'write.elf', 'gx8002-uart-write-source-verification.json'),
        ('uart-receive-byte', verify_uart_receive_byte_source, 'receive_byte.elf', 'gx8002-uart-receive-byte-source-verification.json'),
        ('uart-initialize', verify_uart_initialize_source, 'initialize.elf', 'gx8002-uart-initialize-source-verification.json'),
        ('uart-configure', verify_uart_configure_source, 'configure.elf', 'gx8002-uart-configure-source-verification.json'),
        ('uart-interrupt', verify_uart_interrupt_source, 'interrupt.elf', 'gx8002-uart-interrupt-source-verification.json'),
        ('dma-abort', verify_dma_abort_source, 'abort.elf', 'gx8002-dma-abort-source-verification.json'),
        ('uart-abort', verify_uart_abort_source, 'control.elf', 'gx8002-uart-abort-source-verification.json'),
        ('console-initialize', verify_console_initialize_source, 'initialize.elf', 'gx8002-console-initialize-source-verification.json'),
        ('cache-initialize', verify_cache_initialize_source, 'initialize.elf', 'gx8002-cache-initialize-source-verification.json'),
        ('pcm-channel-setting', verify_pcm_channel_setting_source, 'setting.elf', 'gx8002-pcm-channel-setting-source-verification.json'),
        ('audio-input-sadc', verify_audio_input_sadc_source, 'sadc.elf', 'gx8002-audio-input-sadc-source-verification.json'),
        ('audio-input-pdm', verify_audio_input_pdm_source, 'pdm.elf', 'gx8002-audio-input-pdm-source-verification.json'),
        ('audio-input-i2s', verify_audio_input_i2s_source, 'i2s.elf', 'gx8002-audio-input-i2s-source-verification.json'),
        ('audio-input-channel', verify_audio_input_channel_source, 'channel.elf', 'gx8002-audio-input-channel-source-verification.json'),
        ('audio-output-pcm', verify_audio_output_pcm_source, 'pcm.elf', 'gx8002-audio-output-pcm-source-verification.json'),
        ('audio-output-logfbank', verify_audio_output_logfbank_source, 'logfbank.elf', 'gx8002-audio-output-logfbank-source-verification.json'),
        ('audio-output-spectrum', verify_audio_output_spectrum_source, 'spectrum.elf', 'gx8002-audio-output-spectrum-source-verification.json'),
        ('audio-output-i2s', verify_audio_output_i2s_source, 'i2s.elf', 'gx8002-audio-output-i2s-source-verification.json'),
        ('audio-pga-gain', verify_audio_pga_gain_source, 'gain.elf', 'gx8002-audio-pga-gain-source-verification.json'),
        ('audio-dc-enable', verify_audio_dc_enable_source, 'gain.elf', 'gx8002-audio-dc-enable-source-verification.json'),
        ('audio-rough-gain', verify_audio_rough_gain_source, 'gain.elf', 'gx8002-audio-rough-gain-source-verification.json'),
        ('audio-evad-enable', verify_audio_evad_enable_source, 'gain.elf', 'gx8002-audio-evad-enable-source-verification.json'),
        ('audio-evad-threshold', verify_audio_evad_threshold_source, 'gain.elf', 'gx8002-audio-evad-threshold-source-verification.json'),
        ('audio-logfbank-enable', verify_audio_logfbank_enable_source, 'gain.elf', 'gx8002-audio-logfbank-enable-source-verification.json'),
        ('audio-fftvad-enable', verify_audio_fftvad_enable_source, 'gain.elf', 'gx8002-audio-fftvad-enable-source-verification.json'),
        ('audio-fftvad-w', verify_audio_fftvad_w_source, 'gain.elf', 'gx8002-audio-fftvad-w-source-verification.json'),
        ('audio-fftvad-chipping', verify_audio_fftvad_chipping_source, 'gain.elf', 'gx8002-audio-fftvad-chipping-source-verification.json'),
        ('audio-fftvad-state', verify_audio_fftvad_state_source, 'gain.elf', 'gx8002-audio-fftvad-state-source-verification.json'),
        ('audio-interrupt-enable', verify_audio_interrupt_enable_source, 'gain.elf', 'gx8002-audio-interrupt-enable-source-verification.json'),
        ('audio-initialize', verify_audio_initialize_source, 'gain.elf', 'gx8002-audio-initialize-source-verification.json'),
        ('audio-channel-field', verify_audio_channel_field_source, 'field.elf', 'gx8002-audio-channel-field-source-verification.json'),
        ('audio-output-bits', verify_audio_output_bits_source, 'bits.elf', 'gx8002-audio-output-bits-source-verification.json'),
        ('audio-output-free', verify_audio_output_free_source, 'bits.elf', 'gx8002-audio-output-free-source-verification.json'),
        ('audio-output-push-frame', verify_audio_output_push_frame_source, 'bits.elf', 'gx8002-audio-output-push-frame-source-verification.json'),
        ('audio-output-config-buffer', verify_audio_output_config_buffer_source, 'bits.elf', 'gx8002-audio-output-config-buffer-source-verification.json'),
        ('audio-output-config-pcm', verify_audio_output_config_pcm_source, 'bits.elf', 'gx8002-audio-output-config-pcm-source-verification.json'),
        ('audio-output-set-channel', verify_audio_output_set_channel_source, 'bits.elf', 'gx8002-audio-output-set-channel-source-verification.json'),
        ('audio-output-alloc-playback', verify_audio_output_alloc_playback_source, 'bits.elf', 'gx8002-audio-output-alloc-playback-source-verification.json'),
        ('audio-output-hw-config', verify_audio_output_hw_config_source, 'bits.elf', 'gx8002-audio-output-hw-config-source-verification.json'),
        ('audio-output-handle-isr', verify_audio_output_handle_isr_source, 'bits.elf', 'gx8002-audio-output-handle-isr-source-verification.json'),
        ('audio-output-drain-frame', verify_audio_output_drain_frame_source, 'bits.elf', 'gx8002-audio-output-drain-frame-source-verification.json'),
        ('audio-output-init', verify_audio_output_init_source, 'bits.elf', 'gx8002-audio-output-init-source-verification.json'),
        ('audio-output-volume', verify_audio_output_volume_source, 'bits.elf', 'gx8002-audio-output-volume-source-verification.json'),
        ('audio-output-route', verify_audio_output_route_source, 'bits.elf', 'gx8002-audio-output-route-source-verification.json'),
        ('audio-output-dispatch', verify_audio_output_dispatch_source, 'bits.elf', 'gx8002-audio-output-dispatch-source-verification.json'),
        ('audio-output-public-init', verify_audio_output_public_init_source, 'bits.elf', 'gx8002-audio-output-public-init-source-verification.json'),
        ('audio-output-public-alloc', verify_audio_output_public_alloc_source, 'bits.elf', 'gx8002-audio-output-public-alloc-source-verification.json'),
        ('audio-output-public-free', verify_audio_output_public_free_source, 'bits.elf', 'gx8002-audio-output-public-free-source-verification.json'),
        ('audio-output-public-buffer', verify_audio_output_public_buffer_source, 'bits.elf', 'gx8002-audio-output-public-buffer-source-verification.json'),
        ('audio-output-public-pcm', verify_audio_output_public_pcm_source, 'bits.elf', 'gx8002-audio-output-public-pcm-source-verification.json'),
        ('audio-output-public-cb', verify_audio_output_public_cb_source, 'bits.elf', 'gx8002-audio-output-public-cb-source-verification.json'),
        ('audio-output-public-frame', verify_audio_output_public_frame_source, 'bits.elf', 'gx8002-audio-output-public-frame-source-verification.json'),
        ('audio-output-public-db', verify_audio_output_public_db_source, 'bits.elf', 'gx8002-audio-output-public-db-source-verification.json'),
        ('audio-output-public-channel', verify_audio_output_public_channel_source, 'bits.elf', 'gx8002-audio-output-public-channel-source-verification.json'),
        ('audio-output-public-exit', verify_audio_output_public_exit_source, 'bits.elf', 'gx8002-audio-output-public-exit-source-verification.json'),
        ('audio-output-suspend', verify_audio_output_suspend_source, 'bits.elf', 'gx8002-audio-output-suspend-source-verification.json'),
        ('audio-output-resume', verify_audio_output_resume_source, 'bits.elf', 'gx8002-audio-output-resume-source-verification.json'),
        ('audio-output-exit', verify_audio_output_exit_source, 'bits.elf', 'gx8002-audio-output-exit-source-verification.json'),
        ('audio-output-callbacks', verify_audio_output_callbacks_source, 'bits.elf', 'gx8002-audio-output-callbacks-source-verification.json'),
        ('audio-output-mute', verify_audio_output_mute_source, 'bits.elf', 'gx8002-audio-output-mute-source-verification.json'),
        ('audio-output-fixed', verify_audio_output_fixed_source, 'bits.elf', 'gx8002-audio-output-fixed-source-verification.json'),
        ('audio-output-config-i2s', verify_audio_output_config_i2s_source, 'bits.elf', 'gx8002-audio-output-config-i2s-source-verification.json'),
        ('audio-output-lodac', verify_audio_output_lodac_source, 'bits.elf', 'gx8002-audio-output-lodac-source-verification.json'),
        ('audio-output-i2s-config', verify_audio_output_i2s_config_source, 'bits.elf', 'gx8002-audio-output-i2s-config-source-verification.json'),
        ('audio-output-dac', verify_audio_output_dac_source, 'bits.elf', 'gx8002-audio-output-dac-source-verification.json'),
        ('audio-output-config-dac', verify_audio_output_config_dac_source, 'bits.elf', 'gx8002-audio-output-config-dac-source-verification.json'),
        ('uart-receive-buffer', verify_uart_receive_buffer_source, 'buffer.elf', 'gx8002-uart-receive-buffer-source-verification.json'),
        ('uart-transmit-buffer', verify_uart_transmit_buffer_source, 'buffer.elf', 'gx8002-uart-transmit-buffer-source-verification.json'),
        ('dma-transfer', verify_dma_transfer_source, 'transfer.elf', 'gx8002-dma-transfer-source-verification.json'),
        ('uart-receive-dma', verify_uart_receive_dma_source, 'dma.elf', 'gx8002-uart-receive-dma-source-verification.json'),
        ('dma-clear', verify_dma_clear_source, 'clear.elf', 'gx8002-dma-clear-source-verification.json'),
        ('dma-release', verify_dma_release, 'release.elf', 'gx8002-dma-release-verification.json'),
        ('trigger', verify_trigger, 'setter.elf', 'gx8002-trigger-event-verification.json'),
        ('queue_put', verify_put, 'queue-size.o', 'gx8002-queue-put-comparison.json'),
        ('queue_get', verify_get, 'queue-size.o', 'gx8002-queue-get-comparison.json'),
        ('queue', verify_queue, 'queue.o', 'gx8002-queue-source-verification.json'),
        ('watchdog', verify_watchdog, 'stop.o', 'gx8002-watchdog-stop-verification.json'),
        ('suspend', verify_suspend, 'setter.elf', 'gx8002-app-suspend-verification.json'),
        ('resume', verify_resume, 'setter.elf', 'gx8002-app-resume-verification.json'),
        ('setter', verify_setter, 'setter.elf', 'gx8002-model-set-task-verification.json'),
        ('memcpy', verify_memcpy, 'copy.o', 'gx8002-memcpy-source-verification.json'),
        ('uart-stage1-divmod', verify_uart_stage1_divmod, 'divmod.o', 'gx8002-uart-stage1-divmod-verification.json'),
        ('uart-stage1-reset', verify_uart_stage1_reset, 'reset.elf', 'gx8002-uart-stage1-reset-verification.json'),
        ('uart-stage1-pmubits', verify_uart_stage1_pmubits, 'pmubits.o', 'gx8002-uart-stage1-pmubits-verification.json'),
        ('uart-stage1-serial', verify_uart_stage1_serial, 'serial.elf', 'gx8002-uart-stage1-serial-verification.json'),
        ('uart-stage1-idbit', verify_uart_stage1_idbit, 'idbit.elf', 'gx8002-uart-stage1-idbit-verification.json'),
        ('uart-stage1-xip', verify_uart_stage1_xip, 'xip.elf', 'gx8002-uart-stage1-xip-verification.json'),
        ('uart-stage1-pmufill', verify_uart_stage1_pmufill, 'pmufill.elf', 'gx8002-uart-stage1-pmufill-verification.json'),
        ('uart-stage1-mdelay', verify_uart_stage1_mdelay, 'mdelay.elf', 'gx8002-uart-stage1-mdelay-verification.json'),
        ('uart-stage1-vectors', verify_uart_stage1_vectors, 'vectors.elf', 'gx8002-uart-stage1-vectors-verification.json'),
        ('uart-stage1-railc', verify_uart_stage1_railc, 'railc.elf', 'gx8002-uart-stage1-railc-verification.json'),
        ('uart-stage1-railb', verify_uart_stage1_railb, 'railb.elf', 'gx8002-uart-stage1-railb-verification.json'),
        ('uart-stage1-raila', verify_uart_stage1_raila, 'raila.elf', 'gx8002-uart-stage1-raila-verification.json'),
        ('uart-stage1-pmudisp', verify_uart_stage1_pmudisp, 'pmudisp.elf', 'gx8002-uart-stage1-pmudisp-verification.json'),
        ('uart-stage1-pmusecond', verify_uart_stage1_pmusecond, 'pmusecond.elf', 'gx8002-uart-stage1-pmusecond-verification.json'),
        ('uart-stage1-postamble', verify_uart_stage1_postamble, 'postamble.elf', 'gx8002-uart-stage1-postamble-verification.json'),
        ('uart-stage1-uartcfg', verify_uart_stage1_uartcfg, 'uartcfg.elf', 'gx8002-uart-stage1-uartcfg-verification.json'),
        ('uart-stage1-traptails', verify_uart_stage1_traptails, 'traptails.elf', 'gx8002-uart-stage1-traptails-verification.json'),
        ('uart-stage1-beacon', verify_uart_stage1_beacon, 'beacon.elf', 'gx8002-uart-stage1-beacon-verification.json'),
        ('uart-stage1-announce', verify_uart_stage1_announce, 'announce.elf', 'gx8002-uart-stage1-announce-verification.json'),
        ('uart-stage1-handshake', verify_uart_stage1_handshake, 'handshake.elf', 'gx8002-uart-stage1-handshake-verification.json'),
        ('model', verify_model, 'runtime_gx8002_model_interface.o', 'gx8002-model-interface-verification.json'),
    ):
        directory = output / kind
        print(f"Qualifying codec source: {kind}", flush=True)
        report = verifier(prefix, sdk, directory)
        reviewed = json.loads((ROOT / 'docs/research' / baseline).read_text())
        replacements += reviewed_replacements(report, reviewed, directory / artifact, kind)
        if 'tail_allocation' in report:
            tail_allocations.append(report['tail_allocation'])
    for allocation in tail_allocations:
        data_rows=[r for r in replacements if r['symbol']==allocation['data_symbol']]
        if len(data_rows)!=1:raise ValueError('Source tail allocation must identify one data section')
        data=data_rows[0]
        replacements=partition_tail_data(IMAGE.read_bytes(),[r for r in replacements if r is not data],data,
            allocation['host_symbol'],allocation['host_stock_sha256'])
    firmware, ownership, totals = compose(IMAGE.read_bytes(), replacements)
    path = output / 'firmware_codec.hybrid-candidate.bin'
    path.write_bytes(firmware)
    report = {'schema_version': 1, 'firmware_size': len(firmware), 'firmware_sha256': sha(firmware),
              'stock_sha256': IMAGE_SHA, 'source_only': False, 'hardware_qualified': False,
              'source_replacement_occurrences': len(replacements), 'byte_ownership': totals,
              'ownership': ownership,
              'limitations': ['Authenticated stock still supplies all retained ranges.',
                              'No whole-device or timing qualification; experimental candidate only.']}
    (output / 'build-report.json').write_text(json.dumps(report, indent=2) + '\n')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prefix', type=Path, default=ROOT / 'build/csky-macos/install/bin')
    parser.add_argument('--sdk', type=Path, default=ROOT / 'build/upstream-nationalchip-lvp-kws')
    parser.add_argument('--output', type=Path, default=ROOT / 'build/gx8002-source-candidate')
    parser.add_argument('--require-source-only', action='store_true')
    args = parser.parse_args()
    report = build(args.prefix.resolve(), args.sdk.resolve(), args.output.resolve())
    print(json.dumps({k:v for k,v in report.items() if k != 'ownership'}, indent=2))
    if args.require_source_only and report['byte_ownership']['retained_stock']:
        raise SystemExit('source-only gate failed: retained stock still supplies firmware bytes')


if __name__ == '__main__':
    main()
