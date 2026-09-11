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
from verify_gx8002_model_set_task import verify as verify_setter
from verify_gx8002_app_resume import verify as verify_resume
from verify_gx8002_app_suspend import verify as verify_suspend
from verify_gx8002_watchdog_stop import verify as verify_watchdog
from verify_gx8002_queue_source import verify as verify_queue
from compare_gx8002_queue_get import verify_get
from compare_gx8002_queue_put import verify_put
from verify_gx8002_trigger_event import verify as verify_trigger
from compare_gx8002_crc import verify as verify_crc
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
    parse_main_image(output[main_record['offset']:])  # BINH structure and stage-1 CRCs unchanged.
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
        ('crc', verify_crc, 'crc.elf', 'gx8002-crc-target-comparison.json'),
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
        ('uart-flush', verify_uart_flush, 'flush.elf', 'gx8002-uart-flush-verification.json'),
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
        ('model', verify_model, 'runtime_gx8002_model_interface.o', 'gx8002-model-interface-verification.json'),
    ):
        directory = output / kind
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
