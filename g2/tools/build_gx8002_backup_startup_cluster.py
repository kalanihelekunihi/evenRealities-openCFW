# SPDX-License-Identifier: MIT
"""Link source backup reset, vectors, BSS clear and system initialization."""
import json,subprocess,struct,re
from compose_gx8002_backup_printf_startup import prepare as prepare_formatter,verify as verify_formatter
from build_gx8002_backup_reset import build as reset_build,ROOT,Elf32,sha
from build_gx8002_backup_system_initialize import build as system_build
from build_gx8002_backup_preserve_memory import build as predicate_build
from build_gx8002_backup_board_initialize import build as board_build
from build_gx8002_backup_clock_initialize import build as clock_build
from build_gx8002_backup_trim_state import build as trim_build
from build_gx8002_backup_queue_put import build as queue_put_build
from build_gx8002_backup_denoise_record_callback import build as record_callback_build
from build_gx8002_placed_rfft_cluster import build as placed_rfft_build
from build_gx8002_backup_maxabs_q15 import build as beam_peak_build
from build_gx8002_drc_stage4_set_gain import build as drc_stage4_set_gain_build
from build_gx8002_drc_initialize import build as drc_initialize_build
from build_gx8002_drc_stage4_initialize import build as drc_stage4_build
from build_gx8002_drc_stage3_initialize import build as drc_stage3_build
from build_gx8002_drc_stage2_initialize import build as drc_stage2_build
from build_gx8002_drc_stage1_cluster import build as drc_stage1_build
from build_gx8002_beam_spectrums_entry import build as beam_entry_build
from build_gx8002_beam_spectrums import build as beam_spectrums_build
from build_gx8002_beam_shift_q15 import build as beam_shift_build
from build_gx8002_beam_fill_q15 import build as beam_fill_build
from build_gx8002_imcra_process_placed import build as imcra_process_build
from build_gx8002_imcra_sample_shift import build as imcra_shift_build
from build_gx8002_backup_memmove import build as backup_memmove_build
from build_gx8002_imcra_peak_shift import build as imcra_peak_build
from build_gx8002_backup_imcra_state import build as imcra_state_build
from build_gx8002_powf_placed import build as power_build
from build_gx8002_backup_power_wrapper import build as power_wrapper_build
from build_gx8002_backup_cosine import build as cosine_build
from build_gx8002_backup_imcra_workspace import build as imcra_workspace_build
from build_gx8002_backup_imcra_initialize import build as imcra_initialize_build
from build_gx8002_backup_trigger_app_event import build as trigger_event_build
from build_gx8002_backup_audio_interrupt_enable import build as audio_irq_enable_build
from build_gx8002_backup_audio_suspend_resume import build as audio_suspend_resume_build
from build_gx8002_backup_audio_read_index import build as audio_read_index_build
from build_gx8002_backup_get_out_buffer import build as get_out_buffer_build
from build_gx8002_backup_copy_q15 import build as copy_q15_build
from build_gx8002_backup_dcache_clean_range import build as dcache_clean_build
from build_gx8002_backup_dcache_invalid_range import build as dcache_invalid_build
from build_gx8002_backup_get_context import build as get_context_build
from build_gx8002_backup_mic_frame import build as mic_frame_build
from build_gx8002_backup_dma_deallocate import build as dma_deallocate_build
from build_gx8002_backup_lvp_system_initialize import build as lvp_system_build
from build_gx8002_backup_platform_read import build as platform_read_build
from build_gx8002_backup_padmux import build as padmux_build
from build_gx8002_backup_gpio_output import build as gpio_output_build
from build_gx8002_backup_dw_spi_cleanup import build as spi_cleanup_build
from build_gx8002_backup_dw_spi_setup import build as spi_setup_build
from build_gx8002_backup_spi_register_master import build as spi_register_build
from build_gx8002_backup_dw_spi_transfer import build as spi_transfer_build
from build_gx8002_backup_dw_spi_probe import build as spi_probe_build
from build_gx8002_backup_spi_master import build as spi_master_build
from build_gx8002_backup_dw_spi_irq import build as spi_irq_build
from build_gx8002_backup_board_pin_initialize import build as board_pin_initialize_build
from build_gx8002_backup_board_pin_setup import build as board_pin_setup_build
from build_gx8002_backup_board_pin_data import build as board_pin_data_build
from build_gx8002_backup_padmux_init import build as padmux_init_build
from build_gx8002_backup_ldo_control import build as ldo_build
from build_gx8002_backup_clock_tables import build as tables_build
from build_gx8002_backup_clock_source_select import build as source_select_build
from build_gx8002_backup_clock_module_source import build as module_source_build
from build_gx8002_backup_clock_rate_setters import build as rates_build
from build_gx8002_backup_clock_pll import build as pll_build
from build_gx8002_backup_clock_time_us import build as timer_build
from build_gx8002_backup_irq_entry import build as irq_build
from build_gx8002_backup_exception import build as exception_build
from build_gx8002_backup_main import build as main_build
from build_gx8002_backup_mode import build as mode_build
from build_gx8002_backup_idle_mode import build as idle_build
from build_gx8002_backup_denoise_record import build as denoise_build
from build_gx8002_backup_context_initialize import build as context_build
from build_gx8002_backup_memset import build as memset_build
from build_gx8002_backup_context_storage import build as storage_build
from build_gx8002_backup_denoise_initialize import build as denoise_init_build
from build_gx8002_backup_denoise_messages import build as messages_build
from build_gx8002_backup_context_accessors import build as accessors_build
from build_gx8002_backup_heap_wrappers import build as heap_build
from build_gx8002_backup_heap_initialize import build as heap_init_build
from build_gx8002_backup_heap_data import build as heap_data_build
from build_gx8002_backup_calloc import build as calloc_build
from build_gx8002_backup_heap_merge import build as heap_merge_build
from build_gx8002_backup_heap_free import build as heap_free_build
from build_gx8002_backup_heap_malloc import build as heap_malloc_build
from build_gx8002_backup_heap_realloc import build as heap_realloc_build
from verify_gx8002_backup_memcpy import verify as memcpy_build
from build_gx8002_backup_console_wrappers import build as console_build
from build_gx8002_backup_printf_output import build as printf_output_build
from build_gx8002_backup_printf_wrapper import build as printf_wrapper_build
from build_gx8002_backup_printf_reverse import build as printf_reverse_build
from build_gx8002_backup_printf_integer import build as printf_integer_build
from build_gx8002_backup_printf_long_long import build as printf_long_long_build
from build_gx8002_backup_unsigned_division import build as division_build
from build_gx8002_backup_uart_putc import build as uart_putc_build
from build_gx8002_backup_uart_descriptors import build as uart_descriptors_build
from build_gx8002_backup_console import build as console_state_build
from build_gx8002_backup_uart_initialize import build as uart_initialize_build
from build_gx8002_backup_clock_frequency import build as frequency_build
from build_gx8002_backup_uart_configure import build as uart_configure_build
from build_gx8002_backup_uart_fifo import build as uart_fifo_build
from build_gx8002_backup_uart_interrupt import build as uart_interrupt_build
from build_gx8002_backup_request_irq import build as request_irq_build
from build_gx8002_backup_irq_storage import build as irq_storage_build
from build_gx8002_backup_queue_initialize import build as queue_initialize_build
from build_gx8002_backup_app_event_tick import build as event_tick_build
from build_gx8002_backup_app_event_storage import build as event_storage_build
from build_gx8002_backup_crc32 import build as crc_build
from build_gx8002_backup_uart_async_tick import build as async_tick_build
from build_gx8002_backup_uart_async_storage import build as async_storage_build
from build_gx8002_backup_uart_registration import build as uart_registration_build
from build_gx8002_backup_app_power_callbacks import build as app_power_build
from build_gx8002_backup_app_event_initialize import build as event_initialize_build
from build_gx8002_backup_pmu_registration import build as pmu_registration_build
from build_gx8002_backup_pmu_initialize import build as pmu_initialize_build
from build_gx8002_backup_system_done import build as system_done_build
from build_gx8002_backup_device_list import build as device_list_build
from build_gx8002_backup_gpio_initialize import build as gpio_initialize_build
from build_gx8002_backup_rtc_ticks import build as rtc_ticks_build
from build_gx8002_backup_rtc_isr import build as rtc_isr_build
from build_gx8002_backup_rtc_initialize import build as rtc_initialize_build
from build_gx8002_backup_irq_initialize import build as irq_initialize_build
from build_gx8002_backup_dma_initialize import build as dma_initialize_build
from build_gx8002_backup_dma_storage import build as dma_storage_build
from build_gx8002_backup_dma_irq import build as dma_irq_build
from build_gx8002_backup_irq_state import build as irq_state_build
from build_gx8002_backup_cache_initialize import build as cache_initialize_build
from build_gx8002_backup_dcache_control import build as dcache_control_build
from build_gx8002_backup_flash_otp_read_api import build as flash_otp_read_api_build
from build_gx8002_backup_strings import build as strings_build
from build_gx8002_backup_flash_otp_configuration import build as otp_configuration_build, BINDINGS as OTP_BINDINGS
from build_gx8002_backup_flash_otp_read import build as otp_read_build
from build_gx8002_backup_otp_region import build as otp_region_build, ROWS as OTP_REGION_ROWS
from build_gx8002_backup_otp_status import build as otp_status_build
from build_gx8002_backup_otp_lock import build as otp_lock_build
from build_gx8002_backup_otp_erase import build as otp_erase_build
from build_gx8002_backup_otp_transmit import build as otp_transmit_build
from build_gx8002_backup_otp_write import build as otp_write_build
from build_gx8002_backup_flash_read import build as flash_read_build
from build_gx8002_backup_page_program import build as page_program_build
from build_gx8002_backup_block_range import build as block_range_build
from build_gx8002_backup_flash_sync import build as sync_build
from build_gx8002_backup_flash_erase import build as range_erase_build
from build_gx8002_backup_chip_erase import build as chip_erase_build
from build_gx8002_backup_protection_callbacks import build as protection_callbacks_build
from build_gx8002_backup_protection_query import build as protection_query_build
from build_gx8002_backup_protection_set import build as protection_set_build
from build_gx8002_backup_platform_literals import build as platform_literals_build
from build_gx8002_backup_platform_config_cluster import build as platform_config_build
from build_gx8002_backup_flash_word_read import build as flash_word_read_build
from build_gx8002_backup_flash_word_program import build as flash_word_program_build
from build_gx8002_backup_flash_interrupt import build as flash_interrupt_build
from build_gx8002_backup_flash_protection_initialize import build as flash_protection_init_build
from build_gx8002_backup_flash_protection_data import build as flash_protection_data_build
from build_gx8002_backup_flash_names import build as flash_names_build
from build_gx8002_backup_flash_discover import build as flash_discover_build
from build_gx8002_backup_flash_quad import build as flash_quad_build
from build_gx8002_backup_flash_status_write import build as flash_status_write_build
from build_gx8002_backup_flash_transport import build as flash_transport_build
from build_gx8002_backup_flash_getinfo import build as flash_getinfo_build
from build_gx8002_backup_flash_gettype import build as flash_gettype_build
from build_gx8002_backup_flash_storage import build as flash_storage_build
from build_gx8002_backup_flash_interface import build as flash_interface_build
from build_gx8002_backup_flash_probe import build as flash_probe_build
from build_gx8002_backup_flash_info_api import build as flash_info_api_build
from build_gx8002_backup_flash_type import build as flash_type_build
from build_gx8002_backup_digital_control import build as digital_control_build
from build_gx8002_backup_icache_enable import build as icache_enable_build
from build_gx8002_backup_timer_initialize import build as timer_initialize_build
from build_gx8002_backup_timer_channel_initialize import build as timer_channel_build
from build_gx8002_backup_timer_storage import build as timer_storage_build
from build_gx8002_backup_timer_dispatch import build as timer_dispatch_build


def build():
    evidence={'drc_stage4_set_gain':drc_stage4_set_gain_build(),'drc_stage4':drc_stage4_build(),'drc_stage3':drc_stage3_build(),'drc_stage2':drc_stage2_build(),'drc_stage1':drc_stage1_build(),'beam_entry':beam_entry_build(),'beam_peak':beam_peak_build(),'beam_spectrums':beam_spectrums_build(),'beam_shift':beam_shift_build(),'beam_fill':beam_fill_build(),'imcra_process':imcra_process_build(),'placed_rfft':placed_rfft_build(),'imcra_shift':imcra_shift_build(),'backup_memmove':backup_memmove_build(),'imcra_peak':imcra_peak_build(),'imcra_state':imcra_state_build(),'power':power_build(),'power_wrapper':power_wrapper_build(),'cosine':cosine_build(),'imcra_workspace':imcra_workspace_build(),'imcra_initialize':imcra_initialize_build(),'trigger_event':trigger_event_build(),'audio_irq_enable':audio_irq_enable_build(),'audio_suspend_resume':audio_suspend_resume_build(),'audio_read_index':audio_read_index_build(),'get_out_buffer':get_out_buffer_build(),'copy_q15':copy_q15_build(),'dcache_clean':dcache_clean_build(),'queue_put':queue_put_build(),'record_callback':record_callback_build(),'dcache_invalid':dcache_invalid_build(),'get_context':get_context_build(),'mic_frame':mic_frame_build(),'dma_deallocate':dma_deallocate_build(),'lvp_system':lvp_system_build(),'reset':reset_build(),'system':system_build(),'predicate':predicate_build(),'board':board_build(),'clock':clock_build(),'trim':trim_build(),'platform_read':platform_read_build(),'padmux':padmux_build(),'gpio_output':gpio_output_build(),'spi_cleanup':spi_cleanup_build(),'spi_setup':spi_setup_build(),'spi_register':spi_register_build(),'spi_transfer':spi_transfer_build(),'spi_probe':spi_probe_build(),'spi_master':spi_master_build(),'spi_irq':spi_irq_build(),'board_pin_initialize':board_pin_initialize_build(),'board_pin_setup':board_pin_setup_build(),'board_pin_data':board_pin_data_build(),'padmux_init':padmux_init_build(),'ldo':ldo_build(),'tables':tables_build(),'source_select':source_select_build(),'module_source':module_source_build(),'rates':rates_build(),'pll':pll_build(),'timer':timer_build(),'irq':irq_build(),'exception':exception_build(),'main':main_build(),'mode':mode_build(),'idle':idle_build(),'denoise':denoise_build(),'context':context_build(),'memset':memset_build(),'storage':storage_build(),'denoise_init':denoise_init_build(),'messages':messages_build(),'accessors':accessors_build(),'heap':heap_build(),'heap_init':heap_init_build(),'heap_data':heap_data_build(),'calloc':calloc_build(),'heap_merge':heap_merge_build(),'heap_free':heap_free_build(),'heap_malloc':heap_malloc_build(),'heap_realloc':heap_realloc_build(),'memcpy':memcpy_build(),'console':console_build(),'console_state':console_state_build(),'uart_putc':uart_putc_build(),'uart_descriptors':uart_descriptors_build(),'uart_initialize':uart_initialize_build(),'frequency':frequency_build(),'uart_configure':uart_configure_build(),'uart_fifo':uart_fifo_build(),'uart_interrupt':uart_interrupt_build(),'request_irq':request_irq_build(),'irq_storage':irq_storage_build(),'queue_initialize':queue_initialize_build(),'event_tick':event_tick_build(),'event_storage':event_storage_build(),'crc':crc_build(),'async_tick':async_tick_build(),'async_storage':async_storage_build(),'uart_registration':uart_registration_build(),'app_power':app_power_build(),'event_initialize':event_initialize_build(),'pmu_registration':pmu_registration_build(),'pmu_initialize':pmu_initialize_build(),'system_done':system_done_build(),'device_list':device_list_build(),'gpio_initialize':gpio_initialize_build(),'rtc_ticks':rtc_ticks_build(),'rtc_isr':rtc_isr_build(),'rtc_initialize':rtc_initialize_build(),'irq_initialize':irq_initialize_build(),'dma_initialize':dma_initialize_build(),'dma_storage':dma_storage_build(),'dma_irq':dma_irq_build(),'irq_state':irq_state_build(),'cache_initialize':cache_initialize_build(),'dcache_control':dcache_control_build(),'flash_otp_read_api':flash_otp_read_api_build(),'strings':strings_build(),'otp_configuration':otp_configuration_build(),'otp_read':otp_read_build(),'otp_region':otp_region_build(),'otp_status':otp_status_build(),'otp_lock':otp_lock_build(),'otp_erase':otp_erase_build(),'otp_transmit':otp_transmit_build(),'otp_write':otp_write_build(),'flash_read':flash_read_build(),'page_program':page_program_build(),'block_range':block_range_build(),'sync':sync_build(),'range_erase':range_erase_build(),'chip_erase':chip_erase_build(),'protection_callbacks':protection_callbacks_build(),'protection_query':protection_query_build(),'protection_set':protection_set_build(),'platform_literals':platform_literals_build(),'platform_config':platform_config_build(),'flash_word_read':flash_word_read_build(),'flash_word_program':flash_word_program_build(),'flash_interrupt':flash_interrupt_build(),'flash_protection_init':flash_protection_init_build(),'flash_protection_data':flash_protection_data_build(),'flash_names':flash_names_build(),'flash_discover':flash_discover_build(),'flash_quad':flash_quad_build(),'flash_status_write':flash_status_write_build(),'flash_transport':flash_transport_build(),'flash_getinfo':flash_getinfo_build(),'flash_gettype':flash_gettype_build(),'flash_storage':flash_storage_build(),'flash_interface':flash_interface_build(),'flash_probe':flash_probe_build(),'flash_info_api':flash_info_api_build(),'flash_type':flash_type_build(),'digital_control':digital_control_build(),'icache_enable':icache_enable_build(),'timer_initialize':timer_initialize_build(),'timer_channel':timer_channel_build(),'timer_storage':timer_storage_build(),'timer_dispatch':timer_dispatch_build(),'printf_output':printf_output_build(),'printf_wrapper':printf_wrapper_build(),'printf_reverse':printf_reverse_build(),'printf_integer':printf_integer_build(),'printf_long_long':printf_long_long_build(),'division':division_build()}
    evidence['drc_initialize']=drc_initialize_build()
    out=ROOT/'build/gx8002-backup-startup-cluster';out.mkdir(exist_ok=True)
    reset=ROOT/'build/gx8002-backup-reset';system=ROOT/'build/gx8002-backup-system-initialize'
    predicate=ROOT/'build/gx8002-backup-preserve-memory';board=ROOT/'build/gx8002-backup-board-initialize'
    ld=(reset/'reset.ld').read_text().replace('system_init = 0x1000314c;\n','')
    ld=ld.replace('SECTIONS {','SECTIONS {\n.system 0x1000314c : { *system.o(.text*) }',1)
    ld+='clk_init = 0x10003294;\nopen_cfw_gx8002_backup_preserve_memory = 0x10003ffc;\nboard_init = 0x100034d4;\n'
    ld=ld.replace('open_cfw_gx8002_backup_preserve_memory = 0x10003ffc;\n','').replace('board_init = 0x100034d4;','board_init = open_cfw_gx8002_backup_board_initialize;')
    extra='\n'.join(line for line in (board/'board.ld').read_text().splitlines() if line.startswith('.'))
    ld=ld.replace('SECTIONS {','SECTIONS {\n'+extra+'\n.predicate 0x10003ffc : { *predicate.o(.text*) }',1)
    clock=ROOT/'build/gx8002-backup-clock-initialize';data=ROOT/'build/gx8002-backup-clock-source-data'
    padmux_init=ROOT/'build/gx8002-backup-padmux-init'
    init_ld=(padmux_init/'erase.ld').read_text().replace('*(.rodata.open_cfw_gx8002_padmux_defaults)',str(padmux_init/'defaults.o')+'(.rodata.open_cfw_gx8002_padmux_defaults)').replace('*(',str(padmux_init/'erase.o')+'(').replace('open_cfw_gx8002_padmux_set = 0x10008720;','')
    ld=init_ld+ld
    board_pin_initialize=ROOT/'build/gx8002-backup-board-pin-initialize'
    board_pin_setup=ROOT/'build/gx8002-backup-board-pin-setup'
    board_pin_data=ROOT/'build/gx8002-backup-board-pin-data'
    for component in (board_pin_initialize,board_pin_setup):
        component_ld=(component/'erase.ld').read_text().replace('*(',str(component/'erase.o')+'(')
        for symbol in ('padmux_init','padmux_check','gpio_set_direction','printf','board_pin_setup','padmux_set'):
            component_ld=re.sub(r'open_cfw_gx8002_'+symbol+r' = 0x[0-9a-f]+;', '', component_ld)
        ld=component_ld+ld
    ld+='open_cfw_gx8002_printf = printf;\n'
    ld=(board_pin_data/'data.ld').read_text().replace('*(',str(board_pin_data/'data.o')+'(')+ld
    spi_master=ROOT/'build/gx8002-backup-spi-master'
    ld=(spi_master/'master.ld').read_text().replace('*(',str(spi_master/'master.o')+'(')+ld
    spi_probe=ROOT/'build/gx8002-backup-dw-spi-probe'
    probe_ld=(spi_probe/'dw-spi-probe-candidate.ld').read_text().replace('.text 0x','.spi_probe 0x').replace('*(',str(spi_probe/'dw-spi-probe-candidate.o')+'(')
    probe_ld=re.sub(r'open_cfw_gx8002_[a-z_]+ = 0x[0-9a-f]+;', '', probe_ld)
    ld=probe_ld+ld
    spi_transfer=ROOT/'build/gx8002-backup-dw-spi-transfer'
    ld=(spi_transfer/'dw-spi-quick-transfer-candidate.ld').read_text().replace('.text 0x','.spi_transfer 0x').replace('*(',str(spi_transfer/'dw-spi-quick-transfer-candidate.o')+'(').replace('open_cfw_gx8002_clock_gate = 0x10003be8;', 'open_cfw_gx8002_clock_gate = gx_clock_set_module_enable;')+ld
    spi_register=ROOT/'build/gx8002-backup-spi-register-master'
    ld=(spi_register/'spi-register-master-candidate.ld').read_text().replace('.text 0x','.spi_register 0x').replace('*(',str(spi_register/'spi-register-master-candidate.o')+'(').replace('open_cfw_gx8002_device_heads = 0x20017660;','')+ld
    spi_setup=ROOT/'build/gx8002-backup-dw-spi-setup'
    ld=(spi_setup/'dw-spi-setup-candidate.ld').read_text().replace('.text 0x','.spi_setup 0x').replace('*(',str(spi_setup/'dw-spi-setup-candidate.o')+'(').replace('open_cfw_gx8002_clock_frequency = 0x10003cf0;', 'open_cfw_gx8002_clock_frequency = gx_clock_get_module_frequence;')+ld
    spi_cleanup=ROOT/'build/gx8002-backup-dw-spi-cleanup'
    ld=(spi_cleanup/'dw-spi-cleanup-candidate.ld').read_text().replace('.text 0x','.spi_cleanup 0x').replace('*(',str(spi_cleanup/'dw-spi-cleanup-candidate.o')+'(')+ld
    spi_irq=ROOT/'build/gx8002-backup-dw-spi-irq'
    ld=(spi_irq/'dw-spi-irq-candidate.ld').read_text().replace('.text 0x','.spi_irq 0x').replace('*(',str(spi_irq/'dw-spi-irq-candidate.o')+'(')+ld
    gpio_output=ROOT/'build/gx8002-backup-gpio-output'
    ld=(gpio_output/'erase.ld').read_text().replace('*(',str(gpio_output/'erase.o')+'(')+ld
    padmux=ROOT/'build/gx8002-backup-padmux'
    ld=(padmux/'erase.ld').read_text().replace('*(',str(padmux/'erase.o')+'(')+ld
    platform_read=ROOT/'build/gx8002-backup-platform-read'
    ld=(platform_read/'platform-read.ld').read_text().replace('*(',str(platform_read/'platform-read.o')+'(')+ld
    trim=ROOT/'build/gx8002-backup-trim-state';ldo=ROOT/'build/gx8002-backup-ldo-control'
    extra='\n'.join(line for line in (data/'data.ld').read_text().splitlines() if line.startswith('.'))
    extra+='\n.clock 0x10003294 : { *clock.o(.text* .rodata*) }\n.trim 0x1000401c : { *trim.o(.text*) }\n.ldo 0x100080f4 : { *ldo.o(.text* .rodata*) }\n'
    ld=ld.replace('SECTIONS {','SECTIONS {\n'+extra,1).replace('clk_init = 0x10003294;','clk_init = open_cfw_gx8002_backup_clock_initialize;')
    ld+='open_cfw_gx8002_backup_trim_state = open_cfw_gx8002_trim_state;\n'
    ld+='\n'.join(line for line in (clock/'clock.ld').read_text().splitlines() if ' = ' in line and not line.startswith(('open_cfw_gx8002_backup_preserve_memory','open_cfw_gx8002_backup_trim_state','open_cfw_gx8002_backup_ldo_control','gx_clock_set_module_enable','__module_get_info')))+'\n'
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    tables=ROOT/'build/gx8002-backup-clock-tables';gate=ROOT/'build/gx8002-backup-platform-gate'
    lookup_obj=out/'lookup-global.o';gate_obj=out/'gate-input.o'
    subprocess.run([pre+'objcopy','--globalize-symbol=__module_get_info','--globalize-symbol=gx_clock_param_table','--redefine-sym=open_cfw_gx8002_platform_gate=unused_lookup_gate','--localize-symbol=open_cfw_gx8002_clock_lookup',str(tables/'lookup.o'),str(lookup_obj)],check=True)
    subprocess.run([pre+'objcopy','--weaken-symbol=__module_get_info','--localize-symbol=open_cfw_gx8002_clock_lookup',str(gate/'global.o'),str(gate_obj)],check=True)
    extra='\n'.join(line.replace('*(.data.', '*lookup-global.o(.data.') for line in (tables/'tables.ld').read_text().splitlines() if line.startswith('.data.'))
    extra+='\n.lookup 0x100034e0 : { *lookup-global.o(.text.__module_get_info) }\n.gate 0x10003be8 : { *gate-input.o(.text.open_cfw_gx8002_platform_gate) }\n.gate_switch 0x1001295c : { *gate-input.o(.rodata.open_cfw_gx8002_platform_gate) }\n'
    ld=ld.replace('SECTIONS {','SECTIONS {\n'+extra,1)
    ld+='gx_clock_set_module_enable = open_cfw_gx8002_platform_gate;\n'
    ld+='SECTIONS { /DISCARD/ : { *lookup-global.o(.text* .rodata*) *gate-input.o(.text* .rodata* .data*) } }\n'
    source_select=ROOT/'build/gx8002-backup-clock-source-select'
    ld=ld.replace('SECTIONS {','SECTIONS {\n.source_select 0x100035a0 : { *source.o(.text.open_cfw_gx8002_clock_source_select) }',1)
    ld=ld.replace('gx_clock_set_source = 0x100035a0;','gx_clock_set_source = open_cfw_gx8002_clock_source_select;')
    module_source=ROOT/'build/gx8002-backup-clock-module-source'
    ld=ld.replace('SECTIONS {','SECTIONS {\n.module_source 0x100035c0 : { *source.o(.text.open_cfw_gx8002_clock_module_source_fixed) }',1)
    ld=ld.replace('gx_clock_set_module_source = 0x100035c0;','gx_clock_set_module_source = open_cfw_gx8002_clock_module_source_fixed;')
    rates=ROOT/'build/gx8002-backup-clock-rate-setters'
    ld=ld.replace('SECTIONS {','SECTIONS {\n.divider 0x10003788 : { *divider.o(.text* .rodata*) }\n.dto 0x100038e8 : { *dto.o(.text* .rodata*) }',1)
    ld=ld.replace('gx_clock_set_div = 0x10003788;','gx_clock_set_div = open_cfw_gx8002_clock_module_divider_set;')
    ld=ld.replace('gx_clock_set_dto = 0x100038e8;','gx_clock_set_dto = open_cfw_gx8002_clock_module_dto_set;')
    pll=ROOT/'build/gx8002-backup-clock-pll'
    extra='\n'.join(line for line in (pll/'pll.ld').read_text().splitlines() if line.startswith('.'))
    ld=ld.replace('SECTIONS {','SECTIONS {\n'+extra,1)
    ld=ld.replace('gx_clock_set_pll_no_block = 0x100039f4;','gx_clock_set_pll_no_block = open_cfw_gx8002_clock_pll_wait_timeout;')
    ld=ld.replace('gx_clock_set_pll = 0x10003b08;','gx_clock_set_pll = open_cfw_gx8002_clock_pll_wait;')
    timer=ROOT/'build/gx8002-backup-clock-time-us'
    ld=ld.replace('SECTIONS {','SECTIONS {\n.timer 0x10005070 : { *timer.o(.text*) }',1)
    irq=ROOT/'build/gx8002-backup-irq-entry'
    ld=ld.replace('SECTIONS {','SECTIONS {\n.irq 0x10004880 : { *entry.o(.text.open_cfw_gx8002_irq_compact_entry) }',1)
    ld=ld.replace('gx_irq_handler = 0x10004880;','gx_irq_handler = open_cfw_gx8002_irq_compact_entry;')
    ld+='open_cfw_gx8002_irq_table = 0x200173a8;\n'
    exception=ROOT/'build/gx8002-backup-exception'
    extra='\n'.join(line for line in (exception/'exception.ld').read_text().splitlines() if line.startswith('.'))
    ld=ld.replace('SECTIONS {','SECTIONS {\n'+extra,1)
    ld=ld.replace('Default_Handler = 0x10003240;\n','')
    main=ROOT/'build/gx8002-backup-main'
    ld=ld.replace('main = 0x10015cfc;\n','')
    ld=ld.replace('SECTIONS {','SECTIONS {\n.main 0x10015cfc : { *main.o(.sram_text) }',1)
    ld+='\n'.join(line for line in (main/'main.ld').read_text().splitlines() if ' = ' in line)+'\n'
    mode=ROOT/'build/gx8002-backup-mode'
    extra='\n'.join(line.replace('*(.', '*mode.o(.') for line in (mode/'mode.ld').read_text().splitlines() if line.startswith('.'))
    ld=ld.replace('SECTIONS {','SECTIONS {\n'+extra,1)
    ld+='SECTIONS { /DISCARD/ : { *mode.o(.text*) } }\n'
    ld+='\n'.join(line for line in (mode/'mode.ld').read_text().splitlines() if ' = ' in line)+'\n'
    ld=ld.replace('LvpInitMode = 0x1000b748;\n','').replace('LvpModeTick = 0x1000b7a0;\n','')
    idle=ROOT/'build/gx8002-backup-idle-mode'
    extra='\n'.join(line.replace('*(.', '*idle.o(.') for line in (idle/'idle.ld').read_text().splitlines() if line.startswith('.'))
    ld=ld.replace('SECTIONS {','SECTIONS {\n'+extra,1)
    ld=ld.replace('lvp_idle_mode_info = 0x1001366c;\n','')
    ld+='printf = 0x10009934;\n'
    denoise=ROOT/'build/gx8002-backup-denoise-record'
    extra='\n'.join(line.replace('*(.', '*denoise.o(.') for line in (denoise/'denoise.ld').read_text().splitlines() if line.startswith('.'))
    ld=ld.replace('SECTIONS {','SECTIONS {\n'+extra,1)
    ld=ld.replace('lvp_denoise_mode_info = 0x100136b0;\n','')
    ld+='\n'.join(line for line in (denoise/'denoise.ld').read_text().splitlines() if ' = ' in line and not line.startswith('printf'))+'\n'
    context=ROOT/'build/gx8002-backup-context-initialize'
    ld=ld.replace('SECTIONS {','SECTIONS {\n.context_init 0x10009d7c : { *context.o(.text*) }',1)
    ld=ld.replace('open_cfw_gx8002_backup_context_initialize = 0x10009d7c;\n','')
    ld+='memset = 0x100113c4;\n'
    memset=ROOT/'build/gx8002-backup-memset'
    ld=ld.replace('SECTIONS {','SECTIONS {\n.memset 0x100113c4 : { *memset-candidate.o(.text.open_cfw_gx8002_memset) }',1)
    ld=ld.replace('memset = 0x100113c4;','memset = open_cfw_gx8002_memset;')
    storage=ROOT/'build/gx8002-backup-context-storage'
    extra='\n'.join(line.replace('*(.', '*storage.o(.') for line in (storage/'storage.ld').read_text().splitlines() if line.startswith('.'))
    ld=ld.replace('SECTIONS {','SECTIONS {\n'+extra,1)
    denoise_init=ROOT/'build/gx8002-backup-denoise-initialize'
    ld=ld.replace('SECTIONS {','SECTIONS {\n.denoise_init 0x1000bc44 : { *denoise-initialize/initialize.o(.text*) }',1)
    ld=ld.replace('open_cfw_gx8002_backup_denoise_init = 0x1000bc44;\n','')
    ld+='\n'.join(line for line in (denoise_init/'initialize.ld').read_text().splitlines() if ' = ' in line and not line.startswith(('printf','denoise_status_3c8f8')))+'\n'
    ld+='denoise_status_3c8f8 = open_cfw_gx8002_backup_status;\n'
    messages=ROOT/'build/gx8002-backup-denoise-messages'
    extra='\n'.join(line.replace('*(.', '*messages.o(.') for line in (messages/'messages.ld').read_text().splitlines() if line.startswith('.'))
    ld=ld.replace('SECTIONS {','SECTIONS {\n'+extra,1)
    ld='\n'.join(line for line in ld.splitlines() if not line.startswith('denoise_msg_'))+'\n'
    accessors=ROOT/'build/gx8002-backup-context-accessors'
    extra='\n'.join(line.replace('*(.', '*accessors.o(.') for line in (accessors/'accessors.ld').read_text().splitlines() if line.startswith('.'))
    ld=ld.replace('SECTIONS {','SECTIONS {\n'+extra,1)
    ld=ld.replace('denoise_rate_428c0 = 0x10009f80;','denoise_rate_428c0 = backup_pcm_sample_rate;')
    heap=ROOT/'build/gx8002-backup-heap-wrappers'
    extra='\n'.join(line.replace('*(.', '*wrappers.o(.') for line in (heap/'wrappers.ld').read_text().splitlines() if line.startswith('.'))
    ld=ld.replace('SECTIONS {','SECTIONS {\n'+extra,1)
    ld+='\n'.join(line for line in (heap/'wrappers.ld').read_text().splitlines() if ' = ' in line)+'\n'
    ld=ld.replace('denoise_prepare_42850 = 0x10009f10;','denoise_prepare_42850 = backup_heap_initialize;').replace('denoise_allocate_4286c = 0x10009f2c;','denoise_allocate_4286c = backup_allocate;')
    heap_init=ROOT/'build/gx8002-backup-heap-initialize'
    ld=ld.replace('SECTIONS {','SECTIONS {\n.heap_init 0x10009a44 : { *heap.o(.text*) }',1)
    ld=ld.replace('rt_system_heap_init = 0x10009a44;','rt_system_heap_init = backup_rt_heap_initialize;')
    ld+='\n'.join(line for line in (heap_init/'heap.ld').read_text().splitlines() if ' = ' in line and not line.startswith('printf'))+'\n'
    heap_data=ROOT/'build/gx8002-backup-heap-data'
    extra='\n'.join(line.replace('*(.', '*heap-data.o(.') for line in (heap_data/'data.ld').read_text().splitlines() if line.startswith('.'))
    ld=ld.replace('SECTIONS {','SECTIONS {\n'+extra,1)
    ld='\n'.join(line for line in ld.splitlines() if not line.startswith(('backup_heap_state =','backup_heap_invalid_message =','backup_heap_initialize_message =')))+'\n'
    calloc=ROOT/'build/gx8002-backup-calloc'
    ld=ld.replace('SECTIONS {','SECTIONS {\n.calloc 0x10009c0c : { *calloc.o(.text*) }',1)
    ld=ld.replace('rt_calloc = 0x10009c0c;','rt_calloc = backup_rt_calloc;')
    heap_merge=ROOT/'build/gx8002-backup-heap-merge'
    ld=ld.replace('SECTIONS {','SECTIONS {\n.merge 0x100099d4 : { *merge.o(.text*) }',1)
    assert evidence['heap_merge']['fits']
    heap_free=ROOT/'build/gx8002-backup-heap-free'
    ld=ld.replace('SECTIONS {','SECTIONS {\n.free 0x10009c2c : { *free.o(.text*) }',1)
    ld=ld.replace('rt_free = 0x10009c2c;','rt_free = backup_rt_free;')
    assert evidence['heap_free']['fits']
    heap_malloc=ROOT/'build/gx8002-backup-heap-malloc'
    ld=ld.replace('SECTIONS {','SECTIONS {\n.malloc 0x10009ab8 : { *malloc.o(.text*) }',1)
    ld=ld.replace('rt_malloc = 0x10009ab8;','rt_malloc = backup_rt_malloc;')
    assert evidence['heap_malloc']['fits']
    heap_realloc=ROOT/'build/gx8002-backup-heap-realloc'
    ld=ld.replace('SECTIONS {','SECTIONS {\n.realloc 0x10009ca4 : { *realloc.o(.text*) }',1)
    ld=ld.replace('rt_realloc = 0x10009ca4;','rt_realloc = backup_rt_realloc;')
    memcpy=ROOT/'build/gx8002-backup-memcpy'
    ld=ld.replace('SECTIONS {','SECTIONS {\n.memcpy 0x10011344 : { *copy.o(.text.open_cfw_gx8002_memcpy) }',1)
    ld+='memcpy = open_cfw_gx8002_memcpy;\n'
    assert evidence['heap_realloc']['fits']
    console=ROOT/'build/gx8002-backup-console-wrappers'
    uart_putc=ROOT/'build/gx8002-backup-uart-putc'
    ld=ld.replace('SECTIONS {','SECTIONS {\n.console 0x10004818 : { *gx8002-backup-console-wrappers/wrappers.o(.text.backup_console_putc) }\n.putchar 0x10009990 : { *gx8002-backup-console-wrappers/wrappers.o(.text.backup_putchar) }\n.uart_putc 0x100045a0 : { *putc.o(.text*) }',1)
    ld+='backup_console_port = 0x2001739c;\nbackup_uart_descriptors = 0x20016b84;\n'
    uart_descriptors=ROOT/'build/gx8002-backup-uart-descriptors'
    ld=ld.replace('backup_uart_descriptors = 0x20016b84;','backup_uart_descriptors = open_cfw_gx8002_uart_descriptors;')
    ld=ld.replace('SECTIONS {','SECTIONS {\n.descriptors 0x20016b84 : { *descriptors.o(.data.open_cfw_gx8002_uart_descriptors) }',1)
    console_state=ROOT/'build/gx8002-backup-console'
    ld=ld.replace('backup_console_port = 0x2001739c;','backup_console_port = open_cfw_gx8002_backup_console_port;')
    ld=ld.replace('SECTIONS {','SECTIONS {\n.console_init 0x10004808 : { *gx8002-backup-console/console.o(.text.gx_console_init) }\n.console_port 0x2001739c (NOLOAD) : { *gx8002-backup-console/console.o(.bss.backup_console_port) }',1)
    ld+='gx_uart_init = 0x1000451c;\nSECTIONS { /DISCARD/ : { *gx8002-backup-console/console.o(.text.gx_console_putc) } }\n'
    uart_initialize=ROOT/'build/gx8002-backup-uart-initialize'
    ld=ld.replace('gx_uart_init = 0x1000451c;','gx_uart_init = open_cfw_gx8002_uart_initialize;')
    ld=ld.replace('SECTIONS {','SECTIONS {\n.uart_init 0x1000451c : { *gx8002-backup-uart-initialize/initialize.o(.text.open_cfw_gx8002_uart_initialize) }',1)
    ld+='open_cfw_gx8002_platform_gate = gx_clock_set_module_enable;\nopen_cfw_gx8002_clock_frequency = 0x10003cf0;\nopen_cfw_gx8002_uart_configure = 0x100043a4;\n'
    frequency=ROOT/'build/gx8002-backup-clock-frequency'
    subprocess.run([pre+'objcopy','--weaken-symbol=__module_get_info',str(frequency/'global.o'),str(out/'frequency.o')],check=True)
    ld=ld.replace('open_cfw_gx8002_clock_frequency = 0x10003cf0;','')
    ld=ld.replace('SECTIONS {','SECTIONS {\n.frequency 0x10003cf0 : { *gx8002-backup-startup-cluster/frequency.o(.text.open_cfw_gx8002_clock_frequency) }\n.frequency_switch 0x100129f0 : { *gx8002-backup-startup-cluster/frequency.o(.rodata.open_cfw_gx8002_clock_frequency) }',1)
    ld+='SECTIONS { /DISCARD/ : { *gx8002-backup-startup-cluster/frequency.o(.text* .data* .rodata*) } }\n'
    assert all(r['fits'] for r in evidence['frequency']['sections'])
    uart_configure=ROOT/'build/gx8002-backup-uart-configure';uart_fifo=ROOT/'build/gx8002-backup-uart-fifo'
    ld=ld.replace('open_cfw_gx8002_uart_configure = 0x100043a4;','')
    ld=ld.replace('SECTIONS {','SECTIONS {\n.uart_configure 0x100043a4 : { *gx8002-backup-uart-configure/configure.o(.text*) }\n.uart_fifo 0x1000433c : { *gx8002-backup-uart-fifo/fifo.o(.text*) }',1)
    ld+='open_cfw_gx8002_uart_interrupt = 0x10004250;\nopen_cfw_gx8002_request_irq = 0x10004844;\n'
    uart_interrupt=ROOT/'build/gx8002-backup-uart-interrupt';request_irq=ROOT/'build/gx8002-backup-request-irq'
    ld=ld.replace('open_cfw_gx8002_uart_interrupt = 0x10004250;','').replace('open_cfw_gx8002_request_irq = 0x10004844;','open_cfw_gx8002_request_irq = open_cfw_gx8002_backup_request_irq;')
    ld=ld.replace('SECTIONS {','SECTIONS {\n.uart_interrupt 0x10004250 : { *gx8002-backup-uart-interrupt/interrupt.o(.text.open_cfw_gx8002_uart_interrupt) }\n.uart_tx 0x1000435c : { *gx8002-backup-uart-interrupt/interrupt.o(.text.uart_write_bytes*) }\n.request_irq 0x10004844 : { *gx8002-backup-request-irq/request.o(.text*) }',1)
    ld+='open_cfw_gx8002_backup_irq_table = 0x200173a8;\n'
    assert evidence['request_irq']['fits'] and not evidence['uart_interrupt']['dispatch_differences']
    irq_storage=ROOT/'build/gx8002-backup-irq-storage'
    ld=ld.replace('open_cfw_gx8002_irq_table = 0x200173a8;','').replace('open_cfw_gx8002_backup_irq_table = 0x200173a8;','open_cfw_gx8002_backup_irq_table = open_cfw_gx8002_irq_table;')
    ld=(irq_storage/'storage.ld').read_text()+ld
    queue_initialize=ROOT/'build/gx8002-backup-queue-initialize'
    ld=ld.replace('denoise_prepare_428e8 = 0x10009fa8;','denoise_prepare_428e8 = LvpQueueInit;')
    event_tick=ROOT/'build/gx8002-backup-app-event-tick';queue_get=ROOT/'build/gx8002-backup-queue-get'
    for folder,keep,dest in ((queue_initialize,'LvpQueueInit','queue-init.o'),(queue_get,'LvpQueueGet','queue-get.o')):
        original=Elf32((folder/'queue.o').read_bytes(),'queue source')
        unused=[s['name'] for s in original.symbols() if s['name'].startswith('LvpQueue') and s['name']!=keep]
        subprocess.run([pre+'objcopy',*['--localize-symbol='+name for name in unused],str(folder/'queue.o'),str(out/dest)],check=True)
    ld=(queue_initialize/'queue.ld').read_text().replace('*(',str(out/'queue-init.o')+'(')+ld
    event_script=(event_tick/'tick.ld').read_text().replace(str(queue_get/'queue.o'),str(out/'queue-get.o'))
    event_storage=ROOT/'build/gx8002-backup-app-event-storage'
    event_script=event_script.replace('s_app_misc_event_queue = 0x2002d784;','')
    ld=(event_storage/'storage.ld').read_text()+event_script+ld
    ld=ld.replace('LvpAppEventTick = 0x1000be5c;','')
    crc=ROOT/'build/gx8002-backup-crc32'
    ld=(crc/'candidate.ld').read_text()+ld
    assert all(row['fits'] for row in evidence['crc']['sections'])
    async_tick=ROOT/'build/gx8002-backup-uart-async-tick'
    async_script=(async_tick/'tick.ld').read_text().replace('*(',str(async_tick/'tick.o')+'(')
    for assignment in ('LvpQueueGet = 0x10009fbc;','crc32 = 0x1000c5c4;','printf = 0x10009934;'):
        async_script=async_script.replace(assignment,'')
    async_storage=ROOT/'build/gx8002-backup-uart-async-storage'
    async_script=async_script.replace('s_uart_recv_pack_queue = 0x2002d770;','').replace('s_uart_msg_regist_array = 0x2002cf30;','')
    async_script=(async_storage/'storage.ld').read_text()+async_script
    ld=async_script+ld.replace('UartMessageAsyncTick = 0x1000b4c8;','')
    uart_registration=ROOT/'build/gx8002-backup-uart-registration'
    registration_script=(uart_registration/'callback.ld').read_text().replace('*(.text*)',str(uart_registration/'callback.o')+'(.text*)').replace('.text 0x1000b430','.uart_registration 0x1000b430').replace('s_uart_msg_regist_array = 0x2002cf30;','')
    ld=registration_script+ld
    app_power=ROOT/'build/gx8002-backup-app-power-callbacks'
    power_script=(app_power/'callbacks.ld').read_text().replace('*(',str(app_power/'callbacks.o')+'(')
    ld=power_script+ld
    event_initialize=ROOT/'build/gx8002-backup-app-event-initialize'
    init_script=(event_initialize/'callbacks.ld').read_text().replace('*(',str(event_initialize/'callbacks.o')+'(')
    for assignment in ('app_core_ops = 0x20016f74;','s_app_misc_event_queue = 0x2002d784;','s_app_misc_event_queue_buffer = 0x2002d31c;','LvpQueueInit = 0x10009fa8;','_LvpAppSuspend = 0x1000bdb0;','_LvpAppResume = 0x1000bdcc;'):
        init_script=init_script.replace(assignment,'')
    ld=init_script+ld.replace('LvpInitializeAppEvent = 0x1000bdfc;','')
    assert all(row['stock_byte_exact'] for row in evidence['event_initialize']['sections'])
    pmu_registration=ROOT/'build/gx8002-backup-pmu-registration'
    pmu_script=(pmu_registration/'callbacks.ld').read_text().replace('*(',str(pmu_registration/'callbacks.o')+'(').replace('memcpy = 0x10011344;','')
    ld=pmu_script+ld.replace('LvpSuspendInfoRegist = 0x1000a784;','').replace('LvpResumeInfoRegist = 0x1000a7f0;','')
    pmu_initialize=ROOT/'build/gx8002-backup-pmu-initialize'
    pmu_init_script=(pmu_initialize/'callbacks.ld').read_text().replace('*(',str(pmu_initialize/'callbacks.o')+'(').replace('s_handle = 0x2002cb88;','').replace('memset = 0x100113c4;','').replace('gx_pmu_get_wakeup_source = 0x10003fb8;','gx_pmu_get_wakeup_source = denoise_status_3c8f8;')
    ld=pmu_init_script+ld
    system_done=ROOT/'build/gx8002-backup-system-done'
    done_script=(system_done/'callbacks.ld').read_text().replace('*(',str(system_done/'callbacks.o')+'(')
    ld=done_script+ld.replace('LvpSystemDone = 0x1000aacc;','')
    timer_storage=ROOT/'build/gx8002-backup-timer-storage'
    timer_dispatch=ROOT/'build/gx8002-backup-timer-dispatch'
    ld=(timer_dispatch/'timer-dispatch-candidate.ld').read_text().replace('*(',str(timer_dispatch/'timer-dispatch-candidate.o')+'(').replace('.text 0x100050cc','.timer_dispatch 0x100050cc').replace('.timer_state ','.timer_slots ').replace('open_cfw_gx8002_clock_time_us = 0x10005070;','')+ld
    timer_channel=ROOT/'build/gx8002-backup-timer-channel-initialize'
    ld=(timer_channel/'timer-channel-initialize-candidate.ld').read_text().replace('*(',str(timer_channel/'timer-channel-initialize-candidate.o')+'(').replace('.text 0x10004fcc','.timer_channel 0x10004fcc').replace('open_cfw_gx8002_clock_frequency = 0x10003cf0;','')+ld
    timer_initialize=ROOT/'build/gx8002-backup-timer-initialize'
    timer_init_script=(timer_initialize/'timer-initialize-candidate.ld').read_text().replace('*(',str(timer_initialize/'timer-initialize-candidate.o')+'(').replace('.text 0x10004ffc','.timer_initialize 0x10004ffc')
    for assignment in ('open_cfw_gx8002_clock_frequency = 0x10003cf0;','gx_clock_set_module_enable = 0x10003be8;','memset = 0x100113c4;','gx_request_irq = 0x10004844;'):
        timer_init_script=timer_init_script.replace(assignment,'')
    ld=timer_init_script.replace('open_cfw_gx8002_timer_channel_initialize = 0x10004fcc;','').replace('open_cfw_timer_slots = 0x200174bc;','').replace('open_cfw_gx8002_timer_dispatch = 0x100050cc;','')+'\ngx_timer_init = open_cfw_gx8002_timer_initialize;\n'+ld
    assert evidence['timer_initialize']['fits']
    flash_otp_read_api=ROOT/'build/gx8002-backup-flash-otp-read-api'
    ld=(flash_otp_read_api/'flash-otp-read-api-candidate.ld').read_text().replace('*(',str(flash_otp_read_api/'flash-otp-read-api-candidate.o')+'(').replace('.text 0x1000802c','.flash_otp_read_api 0x1000802c')+ld
    strings=ROOT/'build/gx8002-backup-strings'
    strings_ld=(strings/'strings.ld').read_text()
    for name,symbol in (('strlen','open_cfw_gx8002_stage2_strlen'),('strncmp','open_cfw_gx8002_strncmp')):
        strings_ld=strings_ld.replace('*(.text.'+symbol+')',str(strings/(name+'.o'))+'(.text.'+symbol+')')
    ld=strings_ld+ld
    otp_configuration=ROOT/'build/gx8002-backup-flash-otp-configuration'
    # The reviewed candidate uses the two-byte alignment before the setter.
    assert evidence['otp_configuration']['compiled_bytes']==120
    assert (ROOT/'blobs/official/g2-2.2.6.10/firmware_codec.bin').read_bytes()[0x4e08a:0x4e08c]==bytes(2)
    otp_ld=(otp_configuration/'configuration.ld').read_text()
    for symbol,address in OTP_BINDINGS.items():
        assignment=f'{symbol} = {address:#x};'
        assert assignment in otp_ld
        otp_ld=otp_ld.replace(assignment,'')
    otp_ld+='\nopen_cfw_gx8002_flash_otp_probe = open_cfw_gx8002_flash_interface;\nopen_cfw_gx8002_flash_otp_error = open_cfw_gx8002_backup_otp_error;\nopen_cfw_gx8002_flash_otp_signature = open_cfw_gx8002_backup_otp_model;\n'
    ld=otp_ld.replace('*(',str(otp_configuration/'configuration.o')+'(').replace('.text 0x100156d4','.otp_configuration 0x100156d4')+ld
    otp_read=ROOT/'build/gx8002-backup-flash-otp-read'
    ld=(otp_read/'otp-read.ld').read_text().replace('*(',str(otp_read/'otp-read.o')+'(').replace('open_cfw_gx8002_flash_state = 0x20016d60;','').replace('open_cfw_gx8002_flash_wait_ready = 0x10007350;','')+ld
    otp_region=ROOT/'build/gx8002-backup-otp-region'
    region_ld=(otp_region/'otp-region.ld').read_text().replace('*(.text.',str(otp_region/'otp-region.o')+'(.text.').replace('*(.data.',str(otp_region/'otp-descriptor.o')+'(.data.').replace('open_cfw_gx8002_flash_state = 0x20016d60;','')
    ld=region_ld+ld
    otp_status=ROOT/'build/gx8002-backup-otp-status'
    ld=(otp_status/'otp-status.ld').read_text().replace('*(',str(otp_status/'otp-status.o')+'(').replace('open_cfw_gx8002_flash_state = 0x20016d60;','').replace('open_cfw_gx8002_flash_wait_ready = 0x10007350;','').replace('open_cfw_gx8002_flash_command_read = 0x10006c30;','')+ld
    otp_lock=ROOT/'build/gx8002-backup-otp-lock'
    lock_ld=(otp_lock/'otp-lock.ld').read_text().replace('*(',str(otp_lock/'otp-lock.o')+'(')
    for assignment in ('open_cfw_gx8002_flash_state = 0x20016d60;','open_cfw_gx8002_flash_wait_ready = 0x10007350;','open_cfw_gx8002_flash_command_read = 0x10006c30;','backup_flash_status_write = 0x10006d34;'):
        assert assignment in lock_ld
        lock_ld=lock_ld.replace(assignment,'')
    ld=lock_ld+ld
    otp_erase=ROOT/'build/gx8002-backup-otp-erase'
    erase_ld=(otp_erase/'otp-erase.ld').read_text().replace('*(',str(otp_erase/'otp-erase.o')+'(')
    for assignment in ('open_cfw_gx8002_flash_state = 0x20016d60;','open_cfw_gx8002_flash_wait_ready = 0x10007350;','open_cfw_gx8002_flash_command_write = 0x10006cb0;'):
        assert assignment in erase_ld
        erase_ld=erase_ld.replace(assignment,'')
    ld=erase_ld+ld
    otp_transmit=ROOT/'build/gx8002-backup-otp-transmit'
    ld=(otp_transmit/'otp-transmit.ld').read_text().replace('*(',str(otp_transmit/'otp-transmit.o')+'(').replace('open_cfw_gx8002_flash_state = 0x20016d60;','').replace('open_cfw_gx8002_flash_wait_ready = 0x10007350;','')+ld
    otp_write=ROOT/'build/gx8002-backup-otp-write'
    write_ld=(otp_write/'otp-write.ld').read_text().replace('*(',str(otp_write/'otp-write.o')+'(')
    for assignment in ('open_cfw_gx8002_flash_state = 0x20016d60;','open_cfw_gx8002_flash_wait_ready = 0x10007350;','open_cfw_gx8002_flash_command_write = 0x10006cb0;','open_cfw_gx8002_flash_otp_transmit = 0x10007790;'):
        assert assignment in write_ld
        write_ld=write_ld.replace(assignment,'')
    ld=write_ld+ld
    flash_read=ROOT/'build/gx8002-backup-read'
    ld=(flash_read/'read.ld').read_text().replace('*(',str(flash_read/'read.o')+'(').replace('open_cfw_gx8002_flash_state = 0x20016d60;','').replace('open_cfw_gx8002_flash_wait_ready = 0x10007350;','')+ld
    page_program=ROOT/'build/gx8002-backup-page-program'
    page_ld=(page_program/'page-program.ld').read_text().replace('*(',str(page_program/'page-program.o')+'(')
    for assignment in ('open_cfw_gx8002_flash_state = 0x20016d60;','open_cfw_gx8002_flash_wait_ready = 0x10007350;','open_cfw_gx8002_flash_command_write = 0x10006cb0;'):
        assert assignment in page_ld
        page_ld=page_ld.replace(assignment,'')
    ld=page_ld+ld
    block_range=ROOT/'build/gx8002-backup-block-range'
    ld=(block_range/'block-range.ld').read_text().replace('*(',str(block_range/'block-range.o')+'(').replace('open_cfw_gx8002_flash_state = 0x20016d60;','')+ld
    sync=ROOT/'build/gx8002-backup-sync'
    ld=(sync/'sync.ld').read_text().replace('*(',str(sync/'sync.o')+'(').replace('open_cfw_gx8002_flash_command_read = 0x10006c30;','')+ld
    range_erase=ROOT/'build/gx8002-backup-erase'
    chip_erase=ROOT/'build/gx8002-backup-chip-erase'
    protection_callbacks=ROOT/'build/gx8002-backup-protection-callbacks'
    protection_query=ROOT/'build/gx8002-backup-protection-query'
    protection_set=ROOT/'build/gx8002-backup-protection-set'
    for component in (range_erase,chip_erase,protection_callbacks,protection_query,protection_set):
        component_ld=(component/'erase.ld').read_text().replace('*(',str(component/'erase.o')+'(')
        for assignment in ('open_cfw_gx8002_flash_state = 0x20016d60;','open_cfw_gx8002_flash_wait_ready = 0x10007350;','open_cfw_gx8002_flash_command_write = 0x10006cb0;','open_cfw_gx8002_flash_erase = 0x1000764c;','open_cfw_gx8002_flash_command_read = 0x10006c30;','backup_flash_status_write = 0x10006d34;','open_cfw_gx8002_backup_flash_protection_query = 0x10006f04;','open_cfw_gx8002_backup_flash_protection_set = 0x10006fec;'):
            component_ld=component_ld.replace(assignment,'')
        ld=component_ld+ld
    platform_literals=ROOT/'build/gx8002-backup-platform-literals'
    ld=(platform_literals/'literals.ld').read_text().replace('*(',str(platform_literals/'literals.o')+'(').replace('open_cfw_gx8002_backup_flash_probe_slot = 0x20016d80;','open_cfw_gx8002_backup_flash_probe_slot = open_cfw_gx8002_flash_interface;').replace('open_cfw_gx8002_backup_platform_dispatch = 0x10012a3c;','')+ld
    platform_config=ROOT/'build/gx8002-backup-platform-config-cluster'
    platform_ld=(platform_config/'config.ld').read_text().replace('*(.text.entry)',str(platform_config/'entry.o')+'(.text.entry)').replace('*(.text.open_cfw_gx8002_platform_config)',str(platform_config/'config.o')+'(.text.open_cfw_gx8002_platform_config)').replace('*(.rodata.open_cfw_gx8002_platform_config)',str(platform_config/'config.o')+'(.rodata.open_cfw_gx8002_platform_config)')
    platform_ld=platform_ld.replace('.rodata.platform_config 0x10012a3c : {','.rodata.platform_config 0x10012a3c : { open_cfw_gx8002_backup_platform_dispatch = .;')
    ld=platform_ld+ld
    flash_word_read=ROOT/'build/gx8002-backup-flash-word-read'
    ld=(flash_word_read/'transport.ld').read_text().replace('*(',str(flash_word_read/'transport.o')+'(').replace('open_cfw_gx8002_flash_state = 0x20016d60;','')+ld
    flash_word_program=ROOT/'build/gx8002-backup-flash-word-program'
    ld=(flash_word_program/'transport.ld').read_text().replace('*(',str(flash_word_program/'transport.o')+'(').replace('open_cfw_gx8002_flash_wait_ready = 0x10007350;','')+ld
    flash_interrupt=ROOT/'build/gx8002-backup-flash-interrupt'
    ld=(flash_interrupt/'flash-interrupt.ld').read_text().replace('*(',str(flash_interrupt/'flash-interrupt.o')+'(')+ld
    flash_protection_data=ROOT/'build/gx8002-backup-flash-protection-data'
    protection_ld=(flash_protection_data/'data.ld').read_text().replace('*(.rodata.',str(flash_protection_data/'tables.o')+'(.rodata.').replace('*(.bss.',str(flash_protection_data/'profiles.o')+'(.bss.')
    flash_protection_init=ROOT/'build/gx8002-backup-flash-protection-initialize'
    protection_init_ld=(flash_protection_init/'protection-initialize.ld').read_text().replace('*(',str(flash_protection_init/'protection-initialize.o')+'(')
    for name,address in [('256k',0x20016dfc),('512k',0x20016e24),('1024k',0x20016e5c),('profiles',0x20017644)]:
        protection_init_ld=protection_init_ld.replace(f'open_cfw_gx8002_flash_protection_{name} = {address:#x};','')
    ld=protection_ld+protection_init_ld+ld
    flash_names=ROOT/'build/gx8002-backup-flash-names'
    ld=(flash_names/'names.ld').read_text().replace('*(',str(flash_names/'names.o')+'(')+ld
    flash_discover=ROOT/'build/gx8002-backup-flash-discover'
    ld=(flash_discover/'discover.ld').read_text().replace('*(',str(flash_discover/'discover.o')+'(').replace('open_cfw_gx8002_flash_state = 0x20016d60;','').replace('open_cfw_gx8002_flash_command_read = 0x10006c30;','')+ld
    flash_quad=ROOT/'build/gx8002-backup-flash-quad'
    ld=(flash_quad/'transport.ld').read_text().replace('*(',str(flash_quad/'transport.o')+'(').replace('open_cfw_gx8002_flash_command_read = 0x10006c30;','').replace('backup_flash_status_write = 0x10006d34;','')+ld
    flash_status_write=ROOT/'build/gx8002-backup-flash-status-write'
    ld=(flash_status_write/'initialize.ld').read_text().replace('*(',str(flash_status_write/'initialize.o')+'(').replace('.text 0x10006d34','.flash_status_write 0x10006d34').replace('open_cfw_gx8002_flash_command_read = 0x10006c30;','').replace('open_cfw_gx8002_flash_command_write = 0x10006cb0;','')+ld
    flash_transport=ROOT/'build/gx8002-backup-flash-transport'
    ld=(flash_transport/'transport.ld').read_text().replace('*(',str(flash_transport/'transport.o')+'(')+ld
    flash_getinfo=ROOT/'build/gx8002-backup-flash-getinfo'
    ld=(flash_getinfo/'info.ld').read_text().replace('*(',str(flash_getinfo/'info.o')+'(').replace('open_cfw_gx8002_flash_state = 0x20016d60;','')+ld
    flash_gettype=ROOT/'build/gx8002-backup-flash-gettype'
    ld=(flash_gettype/'info.ld').read_text().replace('*(',str(flash_gettype/'info.o')+'(').replace('open_cfw_gx8002_flash_state = 0x20016d60;','')+ld
    flash_storage=ROOT/'build/gx8002-backup-flash-storage'
    flash_storage_ld=(flash_storage/'storage.ld').read_text().replace('*(.data.open_cfw_gx8002_flash_state)',str(flash_storage/'state.o')+'(.data.open_cfw_gx8002_flash_state)').replace('*(.data.open_cfw_gx8002_flash_interface)',str(flash_storage/'table.o')+'(.data.open_cfw_gx8002_flash_interface)').replace('open_cfw_gx8002_flash_interface_initialize = 0x10007d78;','').replace('open_cfw_gx8002_flash_gettype = 0x10007f58;','').replace('open_cfw_gx8002_flash_getinfo = 0x10006eb8;','')
    flash_storage_ld=flash_storage_ld.replace('open_cfw_gx8002_flash_otp_read = 0x100079e8;','')
    for name,offset,size in OTP_REGION_ROWS:
        assignment=f'open_cfw_gx8002_{name} = {offset-0x38940+0x10000000:#x};'
        assert assignment in flash_storage_ld
        flash_storage_ld=flash_storage_ld.replace(assignment,'')
    flash_storage_ld=flash_storage_ld.replace('open_cfw_gx8002_flash_otp_status = 0x100071d4;','')
    flash_storage_ld=flash_storage_ld.replace('open_cfw_gx8002_flash_otp_lock = 0x1000715c;','')
    flash_storage_ld=flash_storage_ld.replace('open_cfw_gx8002_flash_otp_erase = 0x1000723c;','')
    flash_storage_ld=flash_storage_ld.replace('open_cfw_gx8002_flash_otp_write = 0x10007884;','')
    flash_storage_ld=flash_storage_ld.replace('open_cfw_gx8002_flash_read = 0x10006e64;','')
    flash_storage_ld=flash_storage_ld.replace('open_cfw_gx8002_flash_page_program = 0x100074c0;','')
    flash_storage_ld=flash_storage_ld.replace('open_cfw_gx8002_flash_block_range = 0x100075d0;','')
    flash_storage_ld=flash_storage_ld.replace('open_cfw_gx8002_flash_sync = 0x10007118;','')
    flash_storage_ld=flash_storage_ld.replace('open_cfw_gx8002_flash_erase = 0x1000764c;','').replace('open_cfw_gx8002_flash_chip_erase = 0x10007f78;','')
    for suffix,address in (('mode',0x10006fc8),('status',0x10006fac),('lock',0x100070f8),('unlock',0x10007108)):
        flash_storage_ld=flash_storage_ld.replace(f'open_cfw_gx8002_flash_write_protect_{suffix} = {address:#x};','')
    ld=flash_storage_ld+ld
    flash_interface=ROOT/'build/gx8002-backup-flash-interface'
    ld=(flash_interface/'initialize.ld').read_text().replace('*(',str(flash_interface/'initialize.o')+'(').replace('.text 0x10007d78','.flash_interface 0x10007d78').replace('open_cfw_gx8002_platform_gate = 0x10003be8;','').replace('open_cfw_gx8002_request_irq = 0x10004844;','').replace('open_cfw_gx8002_flash_state = 0x20016d60;','').replace('open_cfw_gx8002_flash_interface = 0x20016d80;','').replace('open_cfw_gx8002_platform_config = 0x1001574c;','').replace('open_cfw_gx8002_flash_word_read = 0x100074ec;','').replace('open_cfw_gx8002_flash_word_program = 0x10006d90;','').replace('open_cfw_gx8002_flash_interrupt = 0x10007138;','').replace('open_cfw_gx8002_flash_protection_initialize = 0x10007f80;','').replace('open_cfw_gx8002_flash_discover = 0x10007c90;','').replace('open_cfw_gx8002_flash_quad_enable = 0x100073b4;','').replace('open_cfw_gx8002_flash_quad_enable_pair = 0x10007370;','').replace('open_cfw_gx8002_flash_device_config = 0x100073f0;','').replace('backup_flash_status_write = 0x10006d34;','').replace('backup_flash_command_read = 0x10006c30;','backup_flash_command_read = open_cfw_gx8002_flash_command_read;')+ld
    flash_info_api=ROOT/'build/gx8002-backup-flash-info-api'
    ld=(flash_info_api/'flash-info-api-candidate.ld').read_text().replace('*(',str(flash_info_api/'flash-info-api-candidate.o')+'(').replace('.text 0x10008018','.flash_info_api 0x10008018')+'\ngx_spi_flash_getinfo = open_cfw_gx8002_flash_info_api;\n'+ld
    flash_probe=ROOT/'build/gx8002-backup-flash-probe'
    ld=(flash_probe/'flash-probe-candidate.ld').read_text().replace('*(',str(flash_probe/'flash-probe-candidate.o')+'(').replace('.text 0x10007fac','.flash_probe 0x10007fac').replace('open_cfw_gx8002_flash_probe_callback = 0x20016d80;','open_cfw_gx8002_flash_probe_callback = open_cfw_gx8002_flash_interface;').replace('gx_clock_get_time_us = 0x10005070;','gx_clock_get_time_us = open_cfw_gx8002_clock_time_us;')+'\ngx_spi_flash_probe = open_cfw_gx8002_flash_probe;\n'+ld
    flash_type=ROOT/'build/gx8002-backup-flash-type'
    ld=(flash_type/'flash-type-api-candidate.ld').read_text().replace('*(',str(flash_type/'flash-type-api-candidate.o')+'(').replace('.text 0x1000800c','.flash_type 0x1000800c')+'\ngx_spi_flash_gettype = open_cfw_gx8002_flash_type_api;\n'+ld
    digital_control=ROOT/'build/gx8002-backup-digital-control'
    ld=(digital_control/'digital-control-candidate.ld').read_text().replace('*(',str(digital_control/'digital-control-candidate.o')+'(').replace('.text 0x10008134','.digital_control 0x10008134')+'\ngx_analog_get_ldo_dig_ctrl = open_cfw_gx8002_digital_control;\n'+ld
    icache_enable=ROOT/'build/gx8002-backup-icache-enable'
    ld=(icache_enable/'device.ld').read_text().replace('*(',str(icache_enable/'device.o')+'(')+ld
    dcache_control=ROOT/'build/gx8002-backup-dcache-control'
    ld=(dcache_control/'control.ld').read_text()+ld
    cache_initialize=ROOT/'build/gx8002-backup-cache-initialize'
    ld=(cache_initialize/'initialize.ld').read_text().replace('*(',str(cache_initialize/'control.o')+'(').replace('.text 0x100051a4','.cache_initialize 0x100051a4').replace('gx_dcache_enable = 0x10004d94;','').replace('gx_dcache_disable = 0x10004db4;','').replace('gx_icache_enable = 0x10004fac;','')+'\ngx_cache_init = open_cfw_gx8002_cache_initialize;\n'+ld
    irq_state=ROOT/'build/gx8002-backup-irq-state'
    state_obj=out/'irq-state.o'
    state_elf=Elf32((irq_state/'state.o').read_bytes(),'IRQ state object')
    localize=[s['name'] for s in state_elf.symbols() if s['name'] and s['section'] not in (0,0xfff1) and s['name'] not in ('open_cfw_gx8002_irq_save','open_cfw_gx8002_irq_restore') and s['type']==2]
    # Localize the unused shared IRQ definitions before linking this subset.
    subprocess.run([pre+'objcopy',*[arg for name in localize for arg in ('--localize-symbol',name)],str(irq_state/'state.o'),str(state_obj)],check=True)
    ld=(irq_state/'state.ld').read_text().replace('*(',str(state_obj)+'(')+ld
    dma_deallocate=ROOT/'build/gx8002-backup-dma-deallocate'
    dma_irq=ROOT/'build/gx8002-backup-dma-irq'
    dma_helpers=''
    for folder,stem,section,address in ((dma_irq,'irq','.dma_irq','0x10004c04'),(dma_deallocate,'deallocate','.dma_deallocate','0x10004bc0')):
        part=(folder/(stem+'.ld')).read_text().replace('*(.text*)',str(folder/(stem+'.o'))+'(.text*)').replace('.text '+address,section+' '+address)
        part=part.replace('open_cfw_gx8002_backup_dma_state = 0x2002d3e8;','').replace('open_cfw_gx8002_backup_dma_callbacks = 0x200174a8;','').replace('open_cfw_gx8002_backup_dma_resource = 0x10003be8;','')
        part=part.replace('open_cfw_gx8002_backup_dma_deallocate = 0x10004bc0;','').replace('open_cfw_gx8002_backup_irq_save = 0x1000486c;', 'open_cfw_gx8002_backup_irq_save = open_cfw_gx8002_irq_save;').replace('open_cfw_gx8002_backup_irq_restore = 0x10004878;', 'open_cfw_gx8002_backup_irq_restore = open_cfw_gx8002_irq_restore;')
        dma_helpers+=part
    dma_helpers+='\nopen_cfw_gx8002_backup_dma_state = open_cfw_gx8002_dma_state;\nopen_cfw_gx8002_backup_dma_callbacks = open_cfw_gx8002_dma_callbacks;\nopen_cfw_gx8002_backup_dma_resource = gx_clock_set_module_enable;\nopen_cfw_gx8002_dma_irq_handler = open_cfw_gx8002_backup_dma_irq_handler;\n'
    ld=dma_helpers+ld
    assert evidence['dma_irq']['fits'] and evidence['dma_deallocate']['fits']
    dma_initialize=ROOT/'build/gx8002-backup-dma-initialize'
    dma_script=(dma_initialize/'initialize.ld').read_text().replace('*(.text*)',str(dma_initialize/'initialize.o')+'(.text*)').replace('.text 0x10004d14','.dma_initialize 0x10004d14').replace('open_cfw_gx8002_request_irq = 0x10004844;','').replace('open_cfw_gx8002_dma_resource = 0x10003be8;','open_cfw_gx8002_dma_resource = gx_clock_set_module_enable;')
    dma_storage=ROOT/'build/gx8002-backup-dma-storage'
    dma_script=(dma_storage/'storage.ld').read_text()+dma_script.replace('open_cfw_gx8002_dma_state = 0x2002d3e8;','').replace('open_cfw_gx8002_dma_irq_handler = 0x10004c04;','')
    ld=dma_script+'\ngx_dma_init = open_cfw_gx8002_dma_initialize;\n'+ld
    assert evidence['dma_initialize']['fits']
    irq_initialize=ROOT/'build/gx8002-backup-irq-initialize'
    ld=(irq_initialize/'device.ld').read_text().replace('*(',str(irq_initialize/'device.o')+'(').replace('open_cfw_gx8002_irq_saved_enable = 0x200173a0;','')+ld
    rtc_initialize=ROOT/'build/gx8002-backup-rtc-initialize'
    rtc_init_script=(rtc_initialize/'device.ld').read_text().replace('*(',str(rtc_initialize/'device.o')+'(')
    for assignment in ('gx_clock_set_module_enable = 0x10003be8;','printf_ = 0x10009934;','open_cfw_gx8002_rtc_isr = 0x100087dc;','open_cfw_gx8002_rtc_start_tick = 0x10008800;'):
        rtc_init_script=rtc_init_script.replace(assignment,'')
    rtc_init_script=rtc_init_script.replace('gx_clock_get_module_frequence = 0x10003cf0;','gx_clock_get_module_frequence = open_cfw_gx8002_clock_frequency;').replace('gx_request_irq = 0x10004844;','gx_request_irq = open_cfw_gx8002_backup_request_irq;')
    ld=rtc_init_script+ld
    rtc_isr=ROOT/'build/gx8002-backup-rtc-isr'
    ld=(rtc_isr/'device.ld').read_text().replace('*(',str(rtc_isr/'device.o')+'(')+ld
    rtc_ticks=ROOT/'build/gx8002-backup-rtc-ticks'
    ld=(rtc_ticks/'ticks.ld').read_text()+ld
    gpio_initialize=ROOT/'build/gx8002-backup-gpio-initialize'
    ld=(gpio_initialize/'device.ld').read_text().replace('*(',str(gpio_initialize/'device.o')+'(').replace('open_cfw_gx8002_platform_gate = 0x10003be8;','')+ld
    device_list=ROOT/'build/gx8002-backup-device-list'
    ld=(device_list/'device.ld').read_text().replace('*(',str(device_list/'device.o')+'(')+ld
    assert all(row['stock_byte_exact'] for row in evidence['app_power']['sections'])
    assert evidence['uart_registration']['fits']
    assert evidence['queue_initialize']['stock_byte_exact']
    assert evidence['uart_putc']['fits']
    printf_output=ROOT/'build/gx8002-backup-printf'
    # Compile the authenticated upstream wrapper/callback as a separate unit,
    # leaving the formatter as an ordinary unresolved source dependency.
    sdk_text=(ROOT/'build/upstream-nationalchip-lvp-kws/utility/libc/printf.c').read_text()
    def source_function(signature):
        start=sdk_text.index(signature);brace=sdk_text.index('{',start);depth=1;end=brace+1
        while depth:
            depth+=(sdk_text[end]=='{')-(sdk_text[end]=='}');end+=1
        return sdk_text[start:end]
    wrapper_source=out/'printf-output.c'
    wrapper_source.write_text('#include <stddef.h>\n#include <stdarg.h>\nextern void _putchar(char);\nextern int _vsnprintf(void (*)(char,void*,size_t,size_t),char*,size_t,const char*,va_list);\n'+source_function('static void _out_char(')+'\n'+source_function('int printf_(')+'\n')
    subprocess.run([pre+'gcc','-Os','-fno-shrink-wrap','-mcpu=ck804ef','-mhard-float','-ffreestanding','-fno-builtin','-ffunction-sections','-fdata-sections','-c',str(wrapper_source),'-o',str(out/'printf-output-local.o')],check=True)
    subprocess.run([pre+'objcopy','--globalize-symbol=_out_char',str(out/'printf-output-local.o'),str(out/'printf-output.o')],check=True)
    ld=ld.replace('SECTIONS {','SECTIONS {\n.printf_output 0x10009924 : { *printf-output.o(.text._out_char) }',1)
    ld=ld.replace('SECTIONS {','SECTIONS {\n.printf_wrapper 0x10009934 : { *printf-output.o(.text.printf_) }',1)
    ld=ld.replace('printf = 0x10009934;','printf = printf_;')
    ld+='_putchar = backup_putchar;\n'
    (out/'printf-reverse.ld').write_text('SECTIONS { .text._out_rev : { *(.text._out_rev) } /DISCARD/ : { *(.text*) *(.rodata*) } }\n')
    subprocess.run([pre+'objcopy','--globalize-symbol=_out_rev',str(printf_output/'reverse.o'),str(out/'printf-reverse-source.o')],check=True)
    subprocess.run([pre+'ld','-r','-T',str(out/'printf-reverse.ld'),str(out/'printf-reverse-source.o'),'-o',str(out/'printf-reverse.o')],check=True)
    ld=ld.replace('SECTIONS {','SECTIONS {\n.printf_reverse 0x10008a04 : { *printf-reverse.o(.text._out_rev) }',1)
    subprocess.run([pre+'objcopy','--globalize-symbol=_ntoa_format','--globalize-symbol=_ntoa_long','--globalize-symbol=_ntoa_long_long','--weaken-symbol=_out_rev','--weaken-symbol=printf_',str(printf_output/'integer.o'),str(out/'printf-integer.o')],check=True)
    ld=ld.replace('SECTIONS {','SECTIONS {\n.printf_long 0x10008c88 : { *printf-integer.o(.text._ntoa_long) }\n.printf_format 0x10008aa0 : { *printf-integer.o(.text._ntoa_format) }',1)
    ld=ld.replace('SECTIONS {','SECTIONS {\n.printf_long_long 0x10008d48 : { *printf-integer.o(.text._ntoa_long_long) }',1)
    division=ROOT/'build/gx8002-backup-unsigned-division'
    ld=(division/'division.ld').read_text()+ld
    # Select these compiled helpers; the strong reverse helper supplies the call.
    ld+='SECTIONS { /DISCARD/ : { *printf-integer.o(.text* .rodata*) } }\n'
    evidence['printf_source'],formatter_script,formatter_inputs=prepare_formatter(out,pre)
    gate_query=ROOT/'build/gx8002-board'
    gate_query_ld=(gate_query/'clock-gate-query-fixed-candidate.ld').read_text().replace('*(',str(gate_query/'clock-gate-query-fixed-candidate.o')+'(')
    gate_query_ld=re.sub(r'__module_get_info = 0x[0-9a-f]+;','',gate_query_ld)
    gate_query_ld=re.sub(r'gx_clock_param_table = 0x[0-9a-f]+;','',gate_query_ld)
    gate_query_ld+='open_cfw_gx8002_clock_gate_query = open_cfw_gx8002_clock_gate_query_fixed;\n'
    ld=gate_query_ld+ld
    formatter_inputs.append(str(gate_query/'clock-gate-query-fixed-candidate.o'))
    ld=formatter_script+ld
    lvp_system=ROOT/'build/gx8002-backup-lvp-system-initialize'
    lvp_ld=(lvp_system/'buffers.ld').read_text().split('\n}\n',1)[0]+'\n}\n'
    lvp_ld=lvp_ld.replace('*(.rodata.',str(lvp_system/'data.o')+'(.rodata.').replace('*(.text.',str(lvp_system/'buffers.o')+'(.text.').replace('.text.initialize ','.lvp_system ')
    lvp_ld=re.sub(r'\.rodata.sys_version 0x[0-9a-f]+ : \{[^}]+\}', '', lvp_ld)
    lvp_ld+='SECTIONS { /DISCARD/ : { '+str(lvp_system/'data.o')+'(.rodata.sys_version) } }\nsys_version = denoise_msg_single_fail + 40;\n'
    ld=lvp_ld+ld.replace('LvpSystemInit = 0x1000a8ec;', 'LvpSystemInit = open_cfw_gx8002_backup_lvp_system_initialize;')
    ld+='BoardInit = open_cfw_gx8002_backup_board_pin_initialize;\nspi_master_v3_probe = open_cfw_gx8002_dw_spi_probe;\nopen_cfw_gx8002_power_initialize = LvpPmuInit;\ngx_pmu_ctrl_get = open_cfw_gx8002_platform_read;\n'
    mic_frame=ROOT/'build/gx8002-backup-mic-frame'
    assert evidence['mic_frame']['fits']
    ld=(mic_frame/'index.ld').read_text().replace('.text 0x','.mic_frame 0x').replace('*(',str(mic_frame/'index.o')+'(')+ld
    get_context=ROOT/'build/gx8002-backup-get-context'
    assert evidence['get_context']['fits']
    ld=(get_context/'index.ld').read_text().replace('.text 0x','.get_context 0x').replace('*(',str(get_context/'index.o')+'(').replace('backup_context_frames = 0x20017780;','').replace('backup_context_header = 0x20017700;','')+ld
    dcache_invalid=ROOT/'build/gx8002-backup-dcache-invalid-range'
    assert evidence['dcache_invalid']['fits']
    ld=(dcache_invalid/'dcache-invalid-range-candidate.ld').read_text().replace('.text 0x','.dcache_invalid 0x').replace('*(',str(dcache_invalid/'dcache-invalid-range-candidate.o')+'(')+ld
    queue_put=ROOT/'build/gx8002-backup-queue-put'
    record_callback=ROOT/'build/gx8002-backup-denoise-record-callback'
    assert evidence['queue_put']['fits'] and evidence['record_callback']['fits']
    ld=(queue_put/'queue.ld').read_text().replace('*(',str(queue_put/'queue.o')+'(')+ld
    callback_ld=(record_callback/'callback.ld').read_text().replace('*(',str(record_callback/'callback.o')+'(').replace('.callback ','.denoise_record_callback ')
    for name,target in {'backup_get_context':'open_cfw_gx8002_backup_get_context','backup_get_mic_frame':'open_cfw_gx8002_mic_frame','backup_dcache_invalid_range':'open_cfw_gx8002_dcache_invalid_range','backup_queue_put':'LvpQueuePut'}.items():
        callback_ld=re.sub(name+r' = 0x[0-9a-f]+;',name+' = '+target+';',callback_ld)
    callback_ld=callback_ld.replace('backup_denoise_state = 0x2002d2bc;','')
    ld=callback_ld+ld.replace('denoise_callback_44694 = 0x1000bd54;', 'denoise_callback_44694 = open_cfw_gx8002_backup_denoise_record_callback;')
    dcache_clean=ROOT/'build/gx8002-backup-dcache-clean-range'
    assert evidence['dcache_clean']['fits']
    ld=(dcache_clean/'dcache-clean-range-candidate.ld').read_text().replace('.text 0x','.dcache_clean 0x').replace('*(',str(dcache_clean/'dcache-clean-range-candidate.o')+'(')+ld
    copy_q15=ROOT/'build/gx8002-backup-copy-q15'
    assert evidence['copy_q15']['fits']
    ld=(copy_q15/'copy.ld').read_text().replace('.text 0x','.copy_q15 0x').replace('*(',str(copy_q15/'copy.o')+'(')+ld
    get_out_buffer=ROOT/'build/gx8002-backup-get-out-buffer'
    assert evidence['get_out_buffer']['fits']
    ld=(get_out_buffer/'index.ld').read_text().replace('.text 0x','.get_out_buffer 0x').replace('*(',str(get_out_buffer/'index.o')+'(').replace('backup_context_frames = 0x20017780;','').replace('backup_context_header = 0x20017700;','')+ld
    ld+='ASSERT(backup_context_frames == backup_context_header + 128, "output context layout changed")\n'
    audio_read_index=ROOT/'build/gx8002-backup-audio-read-index'
    assert evidence['audio_read_index']['fits']
    ld=(audio_read_index/'index.ld').read_text().replace('*(',str(audio_read_index/'index.o')+'(')+ld
    audio_irq_enable=ROOT/'build/gx8002-backup-audio-interrupt-enable'
    audio_suspend_resume=ROOT/'build/gx8002-backup-audio-suspend-resume'
    assert evidence['audio_irq_enable']['fits']
    ld=(audio_irq_enable/'gain.ld').read_text().replace('.text 0x','.audio_irq_enable 0x').replace('*(',str(audio_irq_enable/'gain.o')+'(')+ld
    ld=(audio_suspend_resume/'wrappers.ld').read_text().replace('*(',str(audio_suspend_resume/'wrappers.o')+'(').replace('open_cfw_gx8002_audio_interrupt_enable = 0x10005cbc;','')+ld
    trigger_event=ROOT/'build/gx8002-backup-trigger-app-event'
    ld=(trigger_event/'trigger.ld').read_text().replace('*(',str(trigger_event/'trigger.o')+'(').replace('LvpQueuePut = 0x10015b64;','').replace('open_cfw_gx8002_app_event_queue = 0x2002d784;', 'open_cfw_gx8002_app_event_queue = s_app_misc_event_queue;')+ld
    imcra_initialize=ROOT/'build/gx8002-backup-imcra-initialize'
    assert evidence['imcra_initialize']['fits']
    imcra_ld=(imcra_initialize/'index.ld').read_text().replace('*(',str(imcra_initialize/'index.o')+'(')
    for binding in ('backup_denoise_state = 0x2002d2bc;', 'backup_allocate = 0x10009f2c;', 'backup_pcm_sample_rate = 0x10009f80;', 'printf = 0x10009934;'):
        imcra_ld=imcra_ld.replace(binding,'')
    ld=imcra_ld+ld.replace('denoise_imcra_4425c = 0x1000b91c;', 'denoise_imcra_4425c = open_cfw_gx8002_backup_imcra_initialize;')
    imcra_workspace=ROOT/'build/gx8002-backup-imcra-workspace'
    assert evidence['imcra_workspace']['fits']
    ld=(imcra_workspace/'index.ld').read_text().replace('*(',str(imcra_workspace/'index.o')+'(')+ld
    cosine=ROOT/'build/gx8002-backup-cosine'
    assert evidence['cosine']['fits'] and evidence['cosine']['exact_table']
    ld='SECTIONS { .cosine 0x1000ee64 : { '+str(cosine/'cosine.o')+'(.text*) } .sine_table 0x100148d4 : { '+str(cosine/'table.o')+'(.rodata*) } }\n'+ld
    power=ROOT/'build/gx8002-powf-placed'
    power_objects=[ROOT/'build/gx8002-powf-source-closure'/n for n in ('ef_pow.c.o','ef_sqrt.c.o')]+[ROOT/'build/gx8002-scalbnf-corrected'/('source%d.o'%i) for i in (0,1)]
    power_ld=(power/'power.ld').read_text()
    for symbol,obj in zip(('open_cfw_gx8002_backup_rfft','source_cfft_256','source_rfft_forward','source_rfft_inverse','open_cfw_gx8002_imcra_sample_shift','open_cfw_gx8002_memmove','open_cfw_gx8002_imcra_peak_shift','open_cfw_gx8002_backup_imcra_state_initialize','imcra_error_header','imcra_error_required','imcra_error_space','imcra_memory_temp','imcra_memory_static','imcra_memory_total','__ieee754_powf','__ieee754_sqrtf','open_cfw_gx8002_scale_float','open_cfw_gx8002_copy_float_sign','open_cfw_gx8002_float_absolute'),(power_objects[0],power_objects[1],power_objects[2],power_objects[3],power_objects[3])):
        power_ld=power_ld.replace('*(.text.'+symbol+')',str(obj)+'(.text.'+symbol+')')
    for section in ('power','sqrt','scale','sign','absolute'):
        power_ld=power_ld.replace('.'+section+' ','.math_'+section+' ').replace('SIZEOF(.'+section+')','SIZEOF(.math_'+section+')')
    power_wrapper=ROOT/'build/gx8002-backup-power-wrapper'
    wrapper_ld=(power_wrapper/'wrapper.ld').read_text().replace('*(',str(power_wrapper/'wrapper.o')+'(').replace('__ieee754_powf = 0x100100bc;','')
    ld=power_ld+wrapper_ld+ld
    imcra_state=ROOT/'build/gx8002-backup-imcra-state'
    assert evidence['imcra_state']['fits']
    state_ld=(imcra_state/'state.ld').read_text().replace('*(.text*)',str(imcra_state/'state.o')+'(.text*)').replace('*(.rodata.',str(imcra_state/'messages.o')+'(.rodata.')
    for symbol in ('open_cfw_gx8002_backup_imcra_workspace','open_cfw_gx8002_powf','csky_cos_f32','memset','printf','__extendsfdf2'):
        state_ld=re.sub(symbol+r' = 0x[0-9a-f]+;', '',state_ld)
    ld=state_ld+ld.replace('backup_imcra_state_initialize = 0x1000e384;', 'backup_imcra_state_initialize = open_cfw_gx8002_backup_imcra_state_initialize;')
    imcra_peak=ROOT/'build/gx8002-imcra-peak-shift'
    assert evidence['imcra_peak']['fits']
    ld=(imcra_peak/'index.ld').read_text().replace('*(',str(imcra_peak/'index.o')+'(')+ld
    backup_memmove=ROOT/'build/gx8002-backup-memmove'
    assert evidence['backup_memmove']['fits']
    ld=(backup_memmove/'memmove.ld').read_text().replace('.text 0x','.backup_memmove 0x').replace('*(',str(backup_memmove/'memmove.o')+'(').replace('open_cfw_gx8002_memcpy = 0x10011344;','')+ld
    imcra_shift=ROOT/'build/gx8002-imcra-sample-shift'
    assert evidence['imcra_shift']['fits']
    ld=(imcra_shift/'index.ld').read_text().replace('*(',str(imcra_shift/'index.o')+'(')+ld
    placed_rfft=ROOT/'build/gx8002-placed-rfft-cluster'
    fft_base=ROOT/'build/gx8002-source-rfft-generated-reverse-cluster'
    fft_objects=[fft_base/(row['name']+'.o') for row in evidence['placed_rfft']['source_component']['sources'] if row['name']!='descriptor']+[placed_rfft/'descriptor.o']
    fft_ld=(placed_rfft/'cluster.ld').read_text().replace('ENTRY(open_cfw_gx8002_backup_rfft)','')
    for section in ('source_cfft_256','source_rfft_inverse','source_rfft_forward'):
        fft_ld=fft_ld.replace('* (.'+section+')','*(.'+section+')').replace('*(.'+section+')',str(placed_rfft/'descriptor.o')+'(.'+section+')')
    for section in ('complex_coefficients','q14_pairs','bit_lengths','bit_reverse'):
        fft_ld=fft_ld.replace('*(.'+section+')',str(fft_base/'tables.o')+'(.'+section+')')
    ld=fft_ld+ld
    drc_stage4_set_gain=ROOT/'build/gx8002-drc-stage4-set-gain'
    assert evidence['drc_stage4_set_gain']['fits']
    stage4_gain_ld=(drc_stage4_set_gain/'spectrums.ld').read_text().replace('*(',str(drc_stage4_set_gain/'spectrums.o')+'(')
    for symbol in evidence['drc_stage4_set_gain']['helper_bindings']:
        stage4_gain_ld=re.sub(symbol+r' = 0x[0-9a-f]+;', '',stage4_gain_ld)
    ld=stage4_gain_ld+ld
    drc_initialize=ROOT/'build/gx8002-drc-initialize'
    assert evidence['drc_initialize']['sections']
    initialize_ld=(drc_initialize/'spectrums.ld').read_text().replace('*(',str(drc_initialize/'spectrums.o')+'(')
    for symbol in evidence['drc_initialize']['helper_bindings']:
        initialize_ld=re.sub(symbol+r' = 0x[0-9a-f]+;', '', initialize_ld)
    ld=initialize_ld+ld
    formatter_inputs.append(str(drc_initialize/'spectrums.o'))
    drc_stage4=ROOT/'build/gx8002-drc-stage4-initialize'
    assert evidence['drc_stage4']['fits']
    stage4_ld=(drc_stage4/'spectrums.ld').read_text().replace('*(',str(drc_stage4/'spectrums.o')+'(')
    for symbol in evidence['drc_stage4']['helper_bindings']:
        stage4_ld=re.sub(symbol+r' = 0x[0-9a-f]+;', '',stage4_ld)
    ld=stage4_ld+ld
    drc_stage3=ROOT/'build/gx8002-drc-stage3-initialize'
    assert evidence['drc_stage3']['fits']
    stage3_ld=(drc_stage3/'spectrums.ld').read_text().replace('*(',str(drc_stage3/'spectrums.o')+'(')
    for symbol in evidence['drc_stage3']['helper_bindings']:
        stage3_ld=re.sub(symbol+r' = 0x[0-9a-f]+;', '',stage3_ld)
    ld=stage3_ld+ld
    drc_stage2=ROOT/'build/gx8002-drc-stage2-initialize'
    assert evidence['drc_stage2']['fits']
    stage2_ld=(drc_stage2/'spectrums.ld').read_text().replace('*(',str(drc_stage2/'spectrums.o')+'(')
    for symbol in evidence['drc_stage2']['helper_bindings']:
        stage2_ld=re.sub(symbol+r' = 0x[0-9a-f]+;', '',stage2_ld)
    ld=stage2_ld+ld
    drc_stage1=ROOT/'build/gx8002-drc-stage1-cluster'
    drc_inputs=[ROOT/'build/gx8002-drc-stage1-initialize/spectrums.o',ROOT/'build/gx8002-backup-log-exp-wrappers/wrapper.o',ROOT/'build/gx8002-log-exp-probe/ef_log.c.o',ROOT/'build/gx8002-log-exp-placed/exp.o']
    drc_ld=(drc_stage1/'cluster.ld').read_text().replace('open_cfw_gx8002_memset = 0x100113c4;','')
    drc_ld=drc_ld.replace('*(.text.__ieee754_logf)',str(drc_inputs[2])+'(.text.__ieee754_logf)').replace('*(.text.__ieee754_expf)',str(drc_inputs[3])+'(.text.__ieee754_expf)').replace('*(.rodata*)',str(drc_inputs[3])+'(.rodata*)')
    drc_ld=re.sub(r'\.(log|exp|exp_constants)\b',lambda m:'.drc_'+m[1],drc_ld)
    ld=drc_ld+ld
    beam_entry=ROOT/'build/gx8002-beam-spectrums-entry'
    ld=(beam_entry/'entry.ld').read_text().replace('*(',str(beam_entry/'entry.o')+'(').replace('open_cfw_gx8002_beam_spectrums = 0x1000d2a4;','')+ld
    beam_peak=ROOT/'build/gx8002-backup-maxabs-q15'
    beam_spectrums=ROOT/'build/gx8002-beam-spectrums'
    assert evidence['beam_peak']['fits'] and evidence['beam_spectrums']['fits']
    ld=(beam_peak/'maxabs.ld').read_text().replace('.text ','.beam_peak ').replace('*(',str(beam_peak/'maxabs.o')+'(')+ld
    spectrum_ld=(beam_spectrums/'spectrums.ld').read_text().replace('*(',str(beam_spectrums/'spectrums.o')+'(')
    for symbol in evidence['beam_spectrums']['helper_bindings']:
        spectrum_ld=re.sub(symbol+r' = 0x[0-9a-f]+;', '', spectrum_ld)
    ld=spectrum_ld+'beam_peak_q15 = open_cfw_gx8002_backup_maxabs_q15;\n'+ld
    beam_shift=ROOT/'build/gx8002-beam-shift-q15'
    assert evidence['beam_shift']['fits']
    ld=(beam_shift/'shift.ld').read_text().replace('*(',str(beam_shift/'shift.o')+'(')+ld
    beam_fill=ROOT/'build/gx8002-beam-fill-q15'
    ld=(beam_fill/'fill.ld').read_text().replace('*(',str(beam_fill/'fill.o')+'(')+ld
    imcra_process=ROOT/'build/gx8002-imcra-process-placed'
    imcra_process_object=imcra_process/'process-native.o'
    process_ld=(imcra_process/'process.ld').read_text().replace('ENTRY(open_cfw_gx8002_imcra_process)','')
    process_ld=process_ld.replace('*(',str(imcra_process_object)+'(').replace('.prepare ','.imcra_process ').replace('.minimum ','.imcra_minimum ')
    for symbol in json.loads((ROOT/'docs/research/gx8002-imcra-process.json').read_text())['helper_bindings']:
        process_ld=re.sub(symbol+r' = 0x[0-9a-f]+;', '', process_ld)
    ld=process_ld+ld
    (out/'cluster.ld').write_text(ld);path=out/'cluster.elf'
    subprocess.run([pre+'ld','-T',str(out/'cluster.ld'),*formatter_inputs,str(drc_stage4_set_gain/'spectrums.o'),str(drc_stage4/'spectrums.o'),str(drc_stage3/'spectrums.o'),str(drc_stage2/'spectrums.o'),*[str(p) for p in drc_inputs],str(beam_entry/'entry.o'),str(beam_peak/'maxabs.o'),str(beam_spectrums/'spectrums.o'),str(beam_shift/'shift.o'),str(beam_fill/'fill.o'),str(imcra_process_object),*[str(p) for p in fft_objects],str(imcra_shift/'index.o'),str(backup_memmove/'memmove.o'),str(imcra_peak/'index.o'),str(imcra_state/'state.o'),str(imcra_state/'messages.o'),*[str(p) for p in power_objects],str(power_wrapper/'wrapper.o'),str(cosine/'cosine.o'),str(cosine/'table.o'),str(imcra_workspace/'index.o'),str(imcra_initialize/'index.o'),str(trigger_event/'trigger.o'),str(audio_irq_enable/'gain.o'),str(audio_suspend_resume/'wrappers.o'),str(audio_read_index/'index.o'),str(get_out_buffer/'index.o'),str(copy_q15/'copy.o'),str(dcache_clean/'dcache-clean-range-candidate.o'),str(queue_put/'queue.o'),str(record_callback/'callback.o'),str(dcache_invalid/'dcache-invalid-range-candidate.o'),str(get_context/'index.o'),str(mic_frame/'index.o'),str(lvp_system/'buffers.o'),str(lvp_system/'data.o'),str(reset/'reset.o'),str(pll/'pll.o'),str(timer/'timer.o'),str(irq/'entry.o'),str(exception/'vectors.S.o'),str(exception/'trap_c.c.o'),str(main/'main.o'),str(mode/'mode.o'),str(idle/'idle.o'),str(denoise/'denoise.o'),str(context/'context.o'),str(memset/'memset-candidate.o'),str(storage/'storage.o'),str(denoise_init/'initialize.o'),str(messages/'messages.o'),str(accessors/'accessors.o'),str(heap/'wrappers.o'),str(heap_init/'heap.o'),str(heap_data/'heap-data.o'),str(calloc/'calloc.o'),str(heap_merge/'merge.o'),str(heap_free/'free.o'),str(heap_malloc/'malloc.o'),str(heap_realloc/'realloc.o'),str(memcpy/'copy.o'),str(console/'wrappers.o'),str(console_state/'console.o'),str(uart_initialize/'initialize.o'),str(out/'frequency.o'),str(uart_configure/'configure.o'),str(uart_fifo/'fifo.o'),str(uart_interrupt/'interrupt.o'),str(request_irq/'request.o'),str(irq_storage/'storage.o'),str(out/'queue-init.o'),str(out/'queue-get.o'),str(event_tick/'tick.o'),str(event_storage/'storage.o'),str(crc/'candidate.o'),str(async_tick/'tick.o'),str(async_storage/'storage.o'),str(uart_registration/'callback.o'),str(app_power/'callbacks.o'),str(event_initialize/'callbacks.o'),str(pmu_registration/'callbacks.o'),str(pmu_initialize/'callbacks.o'),str(system_done/'callbacks.o'),str(device_list/'device.o'),str(gpio_initialize/'device.o'),str(timer_dispatch/'timer-dispatch-candidate.o'),str(timer_channel/'timer-channel-initialize-candidate.o'),str(timer_initialize/'timer-initialize-candidate.o'),str(flash_otp_read_api/'flash-otp-read-api-candidate.o'),str(strings/'strlen.o'),str(strings/'strncmp.o'),str(otp_configuration/'configuration.o'),str(otp_read/'otp-read.o'),str(otp_region/'otp-region.o'),str(otp_region/'otp-descriptor.o'),str(otp_status/'otp-status.o'),str(otp_lock/'otp-lock.o'),str(otp_erase/'otp-erase.o'),str(otp_transmit/'otp-transmit.o'),str(otp_write/'otp-write.o'),str(flash_read/'read.o'),str(page_program/'page-program.o'),str(block_range/'block-range.o'),str(sync/'sync.o'),str(range_erase/'erase.o'),str(chip_erase/'erase.o'),str(platform_read/'platform-read.o'),str(padmux/'erase.o'),str(gpio_output/'erase.o'),str(spi_cleanup/'dw-spi-cleanup-candidate.o'),str(spi_setup/'dw-spi-setup-candidate.o'),str(spi_register/'spi-register-master-candidate.o'),str(spi_transfer/'dw-spi-quick-transfer-candidate.o'),str(spi_probe/'dw-spi-probe-candidate.o'),str(spi_master/'master.o'),str(spi_irq/'dw-spi-irq-candidate.o'),str(board_pin_initialize/'erase.o'),str(board_pin_setup/'erase.o'),str(board_pin_data/'data.o'),str(padmux_init/'erase.o'),str(padmux_init/'defaults.o'),str(protection_callbacks/'erase.o'),str(protection_query/'erase.o'),str(protection_set/'erase.o'),str(platform_literals/'literals.o'),str(platform_config/'config.o'),str(platform_config/'entry.o'),str(flash_word_read/'transport.o'),str(flash_word_program/'transport.o'),str(flash_interrupt/'flash-interrupt.o'),str(flash_protection_data/'tables.o'),str(flash_protection_data/'profiles.o'),str(flash_protection_init/'protection-initialize.o'),str(flash_names/'names.o'),str(flash_discover/'discover.o'),str(flash_quad/'transport.o'),str(flash_status_write/'initialize.o'),str(flash_transport/'transport.o'),str(flash_getinfo/'info.o'),str(flash_gettype/'info.o'),str(flash_storage/'state.o'),str(flash_storage/'table.o'),str(flash_interface/'initialize.o'),str(flash_probe/'flash-probe-candidate.o'),str(flash_info_api/'flash-info-api-candidate.o'),str(flash_type/'flash-type-api-candidate.o'),str(digital_control/'digital-control-candidate.o'),str(icache_enable/'device.o'),str(dcache_control/'enable.o'),str(dcache_control/'disable_upstream.o'),str(cache_initialize/'control.o'),str(state_obj),str(dma_irq/'irq.o'),str(dma_deallocate/'deallocate.o'),str(dma_storage/'storage.o'),str(dma_initialize/'initialize.o'),str(irq_initialize/'device.o'),str(rtc_initialize/'device.o'),str(rtc_isr/'device.o'),str(rtc_ticks/'start.o'),str(rtc_ticks/'set.o'),str(uart_putc/'putc.o'),str(uart_descriptors/'descriptors.o'),str(out/'printf-output.o'),str(out/'printf-reverse.o'),str(out/'printf-integer.o'),*[str(division/n) for n in ('_udivdi3.o','_umoddi3.o','_clz.o')],str(source_select/'source.o'),str(module_source/'source.o'),str(rates/'divider.o'),str(rates/'dto.o'),str(lookup_obj),str(gate_obj),str(system/'system.o'),str(clock/'clock.o'),str(data/'data.o'),str(trim/'trim.o'),str(ldo/'ldo.o'),str(predicate/'predicate.o'),*[str(board/(name+'.o')) for name in ('backup_board_initialize','backup_status','analog_config_update_enable')],'-o',str(path)],check=True)
    payload=path.read_bytes()
    elf=Elf32(payload,'backup startup')
    verify_formatter(elf,evidence['printf_source'])
    phoff=struct.unpack_from('<I',payload,28)[0]
    phsize,phcount=struct.unpack_from('<HH',payload,42)
    segments=[]
    for i in range(phcount):
        kind,offset,address,physical,filesize,memsize,flags,alignment=struct.unpack_from('<8I',payload,phoff+i*phsize)
        if kind==1:
            assert flags&3!=3, ('Writable executable LOAD segment',hex(address))
            segments.append({'address':address,'file_bytes':filesize,'memory_bytes':memsize,'flags':flags})
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    for name in ('open_cfw_gx8002_drc_stage4_set_gain','open_cfw_gx8002_drc_stage4_initialize','open_cfw_gx8002_drc_stage3_initialize','open_cfw_gx8002_drc_stage2_initialize','open_cfw_gx8002_drc_stage1_initialize','drc_logf','drc_expf','__ieee754_logf','__ieee754_expf','beamforming_triMic_spectrums','beam_peak_q15','open_cfw_gx8002_backup_maxabs_q15','open_cfw_gx8002_beam_spectrums','beam_shift_q15','beam_fill_q15','open_cfw_gx8002_imcra_process','open_cfw_imcra_min_scan','__ieee754_powf','__ieee754_sqrtf','open_cfw_gx8002_scale_float','open_cfw_gx8002_copy_float_sign','open_cfw_gx8002_float_absolute','open_cfw_gx8002_powf','csky_cos_f32','sinTable_f32','open_cfw_gx8002_backup_imcra_workspace','open_cfw_gx8002_backup_imcra_initialize','backup_imcra_error','LvpTriggerAppEvent','open_cfw_gx8002_app_event_queue','open_cfw_gx8002_audio_interrupt_enable','open_cfw_gx8002_backup_audio_suspend','open_cfw_gx8002_backup_audio_resume','open_cfw_gx8002_backup_audio_read_index','open_cfw_gx8002_backup_get_out_buffer','open_cfw_gx8002_backup_copy_q15','open_cfw_gx8002_dcache_clean_range','LvpQueuePut','denoise_callback_44694','open_cfw_gx8002_backup_denoise_record_callback','open_cfw_gx8002_dcache_invalid_range','open_cfw_gx8002_backup_get_context','open_cfw_gx8002_mic_frame','reset_handler','system_init','clear_bss','__Vectors','open_cfw_gx8002_backup_preserve_memory','board_init','clk_init','open_cfw_gx8002_backup_trim_state','open_cfw_gx8002_backup_ldo_control','gx_clock_set_module_enable','__module_get_info','gx_clock_param_table','gx_clock_set_module_source','gx_clock_set_div','gx_clock_set_dto','gx_clock_set_pll','gx_clock_set_pll_no_block','open_cfw_gx8002_clock_time_us','gx_irq_handler','Default_Handler','trap_c','g_trap_sp','g_top_trapstack','main','LvpInitMode','LvpModeTick','lvp_idle_mode_info','lvp_denoise_mode_info','open_cfw_gx8002_backup_context_initialize','memset','open_cfw_gx8002_backup_denoise_init','denoise_status_3c8f8','rt_system_heap_init','backup_heap_merge','backup_heap_state','backup_rt_free','rt_free','backup_heap_free_range','backup_heap_free_invalid','backup_heap_free_details','rt_malloc','backup_rt_malloc','backup_heap_malloc_align','backup_heap_malloc_large','rt_realloc','backup_rt_realloc','backup_heap_realloc_large','memcpy','open_cfw_gx8002_memcpy','backup_console_putc','backup_console_port','open_cfw_gx8002_backup_console_port','gx_console_init','gx_uart_init','open_cfw_gx8002_uart_initialize','open_cfw_gx8002_platform_gate','open_cfw_gx8002_clock_frequency','open_cfw_gx8002_uart_configure','open_cfw_gx8002_uart_fifo_depth','open_cfw_gx8002_uart_interrupt','open_cfw_gx8002_request_irq','open_cfw_gx8002_backup_request_irq','open_cfw_gx8002_irq_table','open_cfw_gx8002_backup_irq_table','open_cfw_gx8002_irq_saved_enable','UartMessageAsyncTick','UartMessageAsyncRegist','s_uart_recv_pack_queue','s_uart_msg_regist_array','crc32','crc32_no_comp','LvpQueueInit','LvpQueueGet','LvpAppEventTick','LvpInitializeAppEvent','open_cfw_gx8002_timer_dispatch','open_cfw_timer_slots','open_cfw_gx8002_timer_channel_initialize','gx_timer_init','open_cfw_gx8002_timer_initialize','open_cfw_gx8002_flash_otp_read_api','strlen','strncmp','open_cfw_gx8002_flash_otp_configuration',*OTP_BINDINGS,'open_cfw_gx8002_flash_otp_read','open_cfw_gx8002_flash_otp_descriptor',*('open_cfw_gx8002_'+row[0] for row in OTP_REGION_ROWS),'open_cfw_gx8002_flash_otp_status','open_cfw_gx8002_flash_otp_lock','open_cfw_gx8002_flash_otp_erase','open_cfw_gx8002_flash_otp_transmit','open_cfw_gx8002_flash_otp_write','open_cfw_gx8002_flash_read','open_cfw_gx8002_backup_program_pages','open_cfw_gx8002_flash_page_program','open_cfw_gx8002_flash_block_range','open_cfw_gx8002_flash_sync','open_cfw_gx8002_flash_erase','open_cfw_gx8002_backup_erase_all','open_cfw_gx8002_flash_chip_erase','open_cfw_gx8002_platform_read','open_cfw_gx8002_padmux_check','open_cfw_gx8002_gpio_set_direction','open_cfw_gx8002_dw_spi_cleanup','open_cfw_gx8002_dw_spi_setup','open_cfw_gx8002_spi_register_master','open_cfw_gx8002_dw_spi_quick_transfer','open_cfw_gx8002_dw_spi_probe','open_cfw_gx8002_backup_spi_master','open_cfw_gx8002_backup_spi_device_state','open_cfw_gx8002_dw_spi_irq','open_cfw_gx8002_backup_board_pin_initialize','open_cfw_gx8002_board_pin_setup','open_cfw_gx8002_board_pin_configure','open_cfw_gx8002_backup_board_pins','open_cfw_gx8002_backup_board_initialized','open_cfw_gx8002_gpio_set_level','open_cfw_gx8002_padmux_init','open_cfw_gx8002_padmux_defaults','open_cfw_gx8002_backup_padmux_defaults','open_cfw_gx8002_padmux_set','open_cfw_gx8002_backup_flash_protection_query','open_cfw_gx8002_backup_flash_protection_set','open_cfw_gx8002_flash_write_protect_mode','open_cfw_gx8002_flash_write_protect_status','open_cfw_gx8002_flash_write_protect_lock','open_cfw_gx8002_flash_write_protect_unlock','open_cfw_gx8002_backup_platform_literals','open_cfw_gx8002_backup_otp_error','open_cfw_gx8002_backup_otp_model','open_cfw_gx8002_backup_flash_probe_slot','open_cfw_gx8002_backup_platform_dispatch','open_cfw_gx8002_platform_config','open_cfw_gx8002_platform_config_entry','open_cfw_gx8002_platform_config_body','open_cfw_gx8002_flash_word_read','open_cfw_gx8002_flash_word_program','open_cfw_gx8002_flash_interrupt','open_cfw_gx8002_flash_protection_initialize','open_cfw_gx8002_flash_protection_profiles','open_cfw_gx8002_flash_protection_256k','open_cfw_gx8002_flash_protection_512k','open_cfw_gx8002_flash_protection_1024k','open_cfw_gx8002_flash_name_p25q21l','open_cfw_gx8002_flash_name_p25q40l','open_cfw_gx8002_flash_name_p25q80l','open_cfw_gx8002_flash_name_en25s20a','open_cfw_gx8002_flash_name_en25s40a','open_cfw_gx8002_flash_name_zb25wq80a','open_cfw_gx8002_flash_discover','open_cfw_gx8002_flash_wait_ready','open_cfw_gx8002_flash_quad_enable','open_cfw_gx8002_flash_quad_enable_pair','open_cfw_gx8002_flash_device_config','backup_flash_status_write','backup_flash_command_read','open_cfw_gx8002_flash_command_read','open_cfw_gx8002_flash_command_write','open_cfw_gx8002_flash_getinfo','open_cfw_gx8002_flash_gettype','open_cfw_gx8002_flash_interface','open_cfw_gx8002_flash_state','open_cfw_gx8002_flash_probe_callback','open_cfw_gx8002_flash_interface_initialize','gx_spi_flash_probe','open_cfw_gx8002_flash_probe_state','gx_spi_flash_getinfo','open_cfw_gx8002_flash_info_api','gx_spi_flash_gettype','open_cfw_gx8002_flash_type_api','gx_analog_get_ldo_dig_ctrl','open_cfw_gx8002_digital_control','gx_icache_enable','gx_dcache_disable','open_cfw_gx8002_dcache_disable_upstream','gx_dcache_enable','gx_cache_init','open_cfw_gx8002_cache_initialize','open_cfw_gx8002_irq_save','open_cfw_gx8002_irq_restore','open_cfw_gx8002_backup_dma_deallocate','open_cfw_gx8002_backup_dma_irq_handler','open_cfw_gx8002_dma_irq_handler','open_cfw_gx8002_dma_state','open_cfw_gx8002_dma_callbacks','gx_dma_init','open_cfw_gx8002_dma_initialize','open_cfw_gx8002_dma_resource','gx_irq_init','gx_rtc_init','gx_clock_get_module_frequence','gx_request_irq','open_cfw_gx8002_rtc_error','open_cfw_gx8002_rtc_isr','open_cfw_gx8002_rtc_callback_state','gx_rtc_start_tick','gx_rtc_set_tick','gx_gpio_init','open_cfw_gx8002_gpio_initialize','device_list_init','open_cfw_gx8002_device_heads','LvpSystemInit','open_cfw_gx8002_backup_lvp_system_initialize','LvpSystemDone','LvpPmuInit','gx_pmu_get_wakeup_source','LvpSuspendInfoRegist','LvpResumeInfoRegist','s_handle','_LvpAppSuspend','_LvpAppResume','s_app_misc_event_queue','s_app_misc_event_queue_buffer','denoise_prepare_428e8','backup_putchar','backup_uart_putc','backup_uart_descriptors','open_cfw_gx8002_uart_descriptors','_putchar','_out_char','printf','printf_','_out_rev','_ntoa_long','_ntoa_format','_ntoa_long_long','__udivdi3','__umoddi3','__clz_tab'):
        symbol=next(s for s in elf.symbols() if s['name']==name);assert symbol['section'] not in (0,0xfff1)
    for original_path,mapping in ((drc_stage4_set_gain/'spectrums.elf',{}),(drc_stage4/'spectrums.elf',{}),(drc_stage3/'spectrums.elf',{}),(drc_stage2/'spectrums.elf',{}),(drc_stage1/'cluster.elf',{'.log':'.drc_log','.exp':'.drc_exp','.exp_constants':'.drc_exp_constants'}),(beam_entry/'entry.elf',{}),(beam_peak/'maxabs.elf',{'.text':'.beam_peak'}),(beam_spectrums/'spectrums.elf',{}),(beam_shift/'shift.elf',{}),(beam_fill/'fill.elf',{}),(imcra_process/'process.elf',{'.prepare':'.imcra_process','.minimum':'.imcra_minimum'}),(placed_rfft/'cluster.elf',{}),(imcra_shift/'index.elf',{}),(backup_memmove/'memmove.elf',{'.text':'.backup_memmove'}),(imcra_peak/'index.elf',{}),(imcra_state/'state.elf',{}),(power/'power.elf',{'.'+n:'.math_'+n for n in ('power','sqrt','scale','sign','absolute')}),(power_wrapper/'wrapper.elf',{}),(cosine/'cosine.elf',{}),(imcra_workspace/'index.elf',{}),(imcra_initialize/'index.elf',{}),(trigger_event/'trigger.elf',{}),(audio_irq_enable/'gain.elf',{'.text':'.audio_irq_enable'}),(audio_suspend_resume/'wrappers.elf',{}),(audio_read_index/'index.elf',{}),(get_out_buffer/'index.elf',{'.text':'.get_out_buffer'}),(copy_q15/'copy.elf',{'.text':'.copy_q15'}),(dcache_clean/'dcache-clean-range-candidate.elf',{'.text':'.dcache_clean'}),(queue_put/'queue.elf',{}),(record_callback/'callback.elf',{'.callback':'.denoise_record_callback'}),(dcache_invalid/'dcache-invalid-range-candidate.elf',{'.text':'.dcache_invalid'}),(get_context/'index.elf',{'.text':'.get_context'}),(mic_frame/'index.elf',{'.text':'.mic_frame'}),(lvp_system/'buffers.elf',{'.text.initialize':'.lvp_system'}),(reset/'reset.elf',{}),(system/'system.elf',{'.text':'.system'}),(predicate/'predicate.elf',{'.text':'.predicate'}),(board/'board.elf',{}),(clock/'clock.elf',{'.text':'.clock'}),(platform_read/'platform-read.elf',{}),(padmux/'erase.elf',{}),(gpio_output/'erase.elf',{}),(spi_cleanup/'dw-spi-cleanup-candidate.elf',{'.text':'.spi_cleanup'}),(spi_setup/'dw-spi-setup-candidate.elf',{'.text':'.spi_setup'}),(spi_register/'spi-register-master-candidate.elf',{'.text':'.spi_register'}),(spi_transfer/'dw-spi-quick-transfer-candidate.elf',{'.text':'.spi_transfer'}),(spi_probe/'dw-spi-probe-candidate.elf',{'.text':'.spi_probe'}),(spi_master/'master.elf',{}),(spi_irq/'dw-spi-irq-candidate.elf',{'.text':'.spi_irq'}),(board_pin_initialize/'erase.elf',{}),(board_pin_setup/'erase.elf',{}),(board_pin_data/'data.elf',{}),(padmux_init/'erase.elf',{}),(trim/'trim.elf',{'.text':'.trim'}),(ldo/'ldo.elf',{'.text':'.ldo'}),(tables/'tables.elf',{'.text':'.lookup'}),(gate/'gate.elf',{'.text':'.gate','.rodata':'.gate_switch'}),(source_select/'source.elf',{'.text':'.source_select'}),(module_source/'source.elf',{'.text':'.module_source'}),(rates/'divider.elf',{'.text':'.divider'}),(rates/'dto.elf',{'.text':'.dto'}),(pll/'pll.elf',{}),(timer/'timer.elf',{}),(irq/'entry.elf',{'.text':'.irq'}),(exception/'exception.elf',{}),(main/'main.elf',{}),(mode/'mode.elf',{}),(idle/'idle.elf',{}),(denoise/'denoise.elf',{}),(context/'context.elf',{}),(memset/'memset-candidate.elf',{'.text':'.memset'}),(storage/'storage.elf',{}),(denoise_init/'initialize.elf',{}),(messages/'messages.elf',{}),(accessors/'accessors.elf',{}),(heap/'wrappers.elf',{}),(heap_init/'heap.elf',{}),(heap_data/'data.elf',{}),(calloc/'calloc.elf',{}),(heap_merge/'merge.elf',{}),(heap_free/'free.elf',{}),(heap_malloc/'malloc.elf',{}),(heap_realloc/'realloc.elf',{}),(memcpy/'copy.elf',{'.text':'.memcpy'}),(console/'wrappers.elf',{}),(uart_putc/'putc.elf',{}),(uart_descriptors/'uart.elf',{}),(uart_initialize/'initialize.elf',{'.init':'.uart_init'}),(frequency/'frequency.elf',{'.text':'.frequency','.rodata':'.frequency_switch'}),(uart_configure/'configure.elf',{'.configure':'.uart_configure'}),(uart_fifo/'fifo.elf',{'.text':'.uart_fifo'}),(uart_interrupt/'interrupt.elf',{'.text':'.uart_interrupt','.fifo':'.uart_fifo','.tx':'.uart_tx'}),(request_irq/'request.elf',{'.text':'.request_irq'}),(irq_storage/'storage.elf',{}),(queue_initialize/'queue.elf',{}),(event_tick/'tick.elf',{}),(event_storage/'storage.elf',{}),(crc/'candidate.elf',{}),(async_tick/'tick.elf',{}),(async_storage/'storage.elf',{}),(uart_registration/'callback.elf',{'.text':'.uart_registration'}),(app_power/'callbacks.elf',{}),(event_initialize/'callbacks.elf',{}),(pmu_registration/'callbacks.elf',{}),(pmu_initialize/'callbacks.elf',{}),(system_done/'callbacks.elf',{}),(device_list/'device.elf',{}),(gpio_initialize/'device.elf',{}),(rtc_ticks/'ticks.elf',{}),(rtc_isr/'device.elf',{}),(rtc_initialize/'device.elf',{}),(irq_initialize/'device.elf',{}),(dma_initialize/'initialize.elf',{'.text':'.dma_initialize'}),(dma_storage/'storage.elf',{}),(dma_irq/'irq.elf',{'.text':'.dma_irq'}),(dma_deallocate/'deallocate.elf',{'.text':'.dma_deallocate'}),(irq_state/'state.elf',{}),(cache_initialize/'initialize.elf',{'.text':'.cache_initialize'}),(dcache_control/'control.elf',{}),(flash_otp_read_api/'flash-otp-read-api-candidate.elf',{'.text':'.flash_otp_read_api'}),(strings/'strings.elf',{}),(otp_configuration/'configuration.elf',{'.text':'.otp_configuration'}),(otp_read/'otp-read.elf',{}),(otp_region/'otp-region.elf',{}),(otp_status/'otp-status.elf',{}),(otp_lock/'otp-lock.elf',{}),(otp_erase/'otp-erase.elf',{}),(otp_transmit/'otp-transmit.elf',{}),(otp_write/'otp-write.elf',{}),(flash_read/'read.elf',{}),(page_program/'page-program.elf',{}),(block_range/'block-range.elf',{}),(sync/'sync.elf',{}),(range_erase/'erase.elf',{}),(chip_erase/'erase.elf',{}),(protection_callbacks/'erase.elf',{}),(protection_query/'erase.elf',{}),(protection_set/'erase.elf',{}),(platform_literals/'literals.elf',{}),(platform_config/'config.elf',{}),(flash_word_read/'transport.elf',{}),(flash_word_program/'transport.elf',{}),(flash_interrupt/'flash-interrupt.elf',{}),(flash_protection_data/'data.elf',{}),(flash_protection_init/'protection-initialize.elf',{}),(flash_names/'names.elf',{}),(flash_discover/'discover.elf',{}),(flash_quad/'transport.elf',{}),(flash_status_write/'initialize.elf',{'.text':'.flash_status_write'}),(flash_transport/'transport.elf',{}),(flash_getinfo/'info.elf',{}),(flash_gettype/'info.elf',{}),(flash_storage/'storage.elf',{}),(flash_interface/'initialize.elf',{'.text':'.flash_interface'}),(flash_probe/'flash-probe-candidate.elf',{'.text':'.flash_probe'}),(flash_info_api/'flash-info-api-candidate.elf',{'.text':'.flash_info_api'}),(flash_type/'flash-type-api-candidate.elf',{'.text':'.flash_type'}),(digital_control/'digital-control-candidate.elf',{'.text':'.digital_control'}),(icache_enable/'device.elf',{}),(timer_initialize/'timer-initialize-candidate.elf',{'.text':'.timer_initialize'}),(timer_channel/'timer-channel-initialize-candidate.elf',{'.text':'.timer_channel'}),(timer_storage/'storage.elf',{}),(timer_dispatch/'timer-dispatch-candidate.elf',{'.text':'.timer_dispatch','.timer_state':'.timer_slots'}),(printf_output/'output.elf',{}),(printf_output/'reverse.elf',{}),(division/'division.elf',{})):
        original=Elf32(original_path.read_bytes(),'component')
        for section in original.sections:
            if original_path==lvp_system/'buffers.elf' and section['name']=='.rodata.sys_version':
                owner=next(s for s in elf.sections if s['name']=='.denoise_msg_single_fail')
                assert owner['address']+owner['size']-1==section['address']
                assert elf.contents(owner)[-1:]==original.contents(section)==b'\0'
                assert next(s for s in elf.symbols() if s['name']=='sys_version')['value']==section['address']
                continue
            if section['flags']&2 and section['size']:
                linked=next(s for s in elf.sections if s['name']==mapping.get(section['name'],section['name']))
                assert linked['address']==section['address'] and elf.contents(linked)==original.contents(section), (str(original_path), section['name'], linked['name'])
    state_elf=Elf32((console_state/'console.elf').read_bytes(),'console state')
    for before,after in (('.init','.console_init'),('.port','.console_port')):
        a=next(s for s in state_elf.sections if s['name']==before);b=next(s for s in elf.sections if s['name']==after)
        assert (a['address'],a['size'],a['type'])==(b['address'],b['size'],b['type'])
        if a['type']!=8:assert state_elf.contents(a)==elf.contents(b)
    wrapper_elf=Elf32((printf_output/'wrapper.elf').read_bytes(),'printf wrapper')
    original=next(s for s in wrapper_elf.sections if s['name']=='.printf_wrapper')
    linked=next(s for s in elf.sections if s['name']=='.printf_wrapper')
    assert original['address']==linked['address'] and wrapper_elf.contents(original)==elf.contents(linked)
    integer_elf=Elf32((printf_output/'integer.elf').read_bytes(),'printf integer')
    original=next(s for s in integer_elf.sections if s['name']=='.text._ntoa_long')
    linked=next(s for s in elf.sections if s['name']=='.printf_long')
    assert original['address']==linked['address'] and integer_elf.contents(original)==elf.contents(linked)
    original=next(s for s in integer_elf.sections if s['name']=='.text._ntoa_format')
    linked=next(s for s in elf.sections if s['name']=='.printf_format')
    assert original['address']==linked['address'] and integer_elf.contents(original)==elf.contents(linked)
    wide_elf=Elf32((printf_output/'long-long.elf').read_bytes(),'printf wide integer')
    original=next(s for s in wide_elf.sections if s['name']=='.printf_long_long')
    linked=next(s for s in elf.sections if s['name']=='.printf_long_long')
    assert original['address']==linked['address'] and wide_elf.contents(original)==elf.contents(linked)
    assert evidence['predicate']['fits'] and all(row['fits'] for row in evidence['board']['sections'])
    assert evidence['clock']['fits_stock_envelope'] and evidence['ldo']['fits']
    assert all(row['fits'] for row in evidence['tables']['upstream_evidence']['sections'])
    assert evidence['module_source']['fits']
    assert all(row['fits'] for row in evidence['rates']['functions'])
    assert all(row['fits'] for row in evidence['pll']['functions'])
    assert evidence['timer']['fits']
    system_size=next(s['size'] for s in elf.sections if s['name']=='.system')
    fits=system_size<=164;assert fits
    ranges=sorted((s['address']&0xfffffff,(s['address']&0xfffffff)+s['size']) for s in elf.sections if s['flags']&2 and s['size'])
    assert all(a[1]<=b[0] for a,b in zip(ranges,ranges[1:]))
    (out/'cluster.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    report={'load_segments':segments,'components':evidence,'elf_sha256':sha(path.read_bytes()),'sections':[{'name':s['name'],'address':s['address'],'bytes':s['size']} for s in elf.sections if s['flags']&2 and s['size']],'absolute_symbols':[s for s in elf.symbols() if s['section']==0xfff1 and s['type']!=4 and s['name']],'source_admitted':False,'system_envelope_bytes':164,'system_bytes':system_size,'fits':fits,'limits':['Reset calls compiled system_init; system_init calls compiled clear_bss and references source vectors. Component bytes/addresses unchanged. Preservation predicate and complete board/status/analog helpers are linked source. Clock initialization, source clock data, trim and LDO are now linked source. Module gate and its lookup/parameter tables are linked source. Clock-source selector also linked as source. Module-source setter shares source lookup/table. Divider setter also links source lookup. DTO setter also links source lookup. Both PLL setters are linked source. The microsecond timer is linked source without a division dependency. The architecture IRQ entry is linked source assembly. Upstream default exception handling and its BSS stack are linked source. Upstream denoise-mode main is linked source; mode initialization/tick, mode list and mode state are linked source. Idle callbacks/record/messages are linked source. Denoise record/done/buffer wrappers are linked source. Context initialization is linked source. Context clearing uses linked C memset. Context header/frame/output/microphone storage is allocated from C declarations. Denoise initializer, its twelve diagnostic strings, status reader and sample-rate reader are linked source. Four additional context readers use allocated header storage. Five allocation wrappers, heap initialization, calloc, heap-state storage and heap coalescing are linked source; free also links the recovered merger; malloc and its diagnostics are linked source; realloc and its diagnostic are linked source; its memcpy dependency now resolves to verified C. Free diagnostic strings are compiled from C literals and linked at their recovered addresses. Denoise tick, initializer subsystem/data dependencies, four other main subsystem callees remain external bindings; IRQ table storage is now allocated from C. System initializer fits its original envelope; this remains an unadmitted component. Authenticated SDK 32-bit and 64-bit integer digit conversion and their formatting callee are linked to source reverse output. Wide integer quotient/remainder and the bit-length table are linked from pinned libgcc source. Authenticated SDK reverse-output helper is linked. Authenticated SDK printf wrapper is linked, with the formatter engine and its complete source arithmetic dependencies now linked. Authenticated SDK character callback calls linked putchar. Console and putchar wrappers call linked C UART output; UART descriptor defaults are source-allocated; console initializer and port BSS are source-allocated. UART initialization and its clock gate are source-linked; frequency lookup and its generated switch table are source-linked; UART configuration, its arithmetic and FIFO-depth query are source-linked; interrupt handling, its transmit helper and registration are source-linked; IRQ table and saved-enable storage are allocated from C declarations, and complete descriptor field semantics remain pending. Composed execution and full firmware admission pending.']}
    (ROOT/'docs/research/gx8002-backup-startup-cluster.json').write_text(json.dumps(report,indent=2)+'\n');return report


if __name__=='__main__':print(build()['sections'])
