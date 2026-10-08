ENTRY(opencfw_boot_startup_initialize_abi)
PHDRS {
  gx_cfg PT_LOAD FLAGS(4);
  root_shared_cfg PT_LOAD FLAGS(4);
  ton_rows PT_LOAD FLAGS(4);
  source_text PT_LOAD FLAGS(5);
  source_cache PT_LOAD FLAGS(5);
  source_idle PT_LOAD FLAGS(5);
  initializer_table PT_LOAD FLAGS(4);
  context_config PT_LOAD FLAGS(4);
  gpio_descriptors PT_LOAD FLAGS(4);
  gpio_irqnums PT_LOAD FLAGS(4);
  service_mutex_attributes PT_LOAD FLAGS(4);
  service_mutex_name PT_LOAD FLAGS(4);
  uart_context_pool PT_LOAD FLAGS(6);
  adc_context_pool PT_LOAD FLAGS(6);
  iom_context_pool PT_LOAD FLAGS(6);
  storage_callbacks PT_LOAD FLAGS(5);
  storage_ranges PT_LOAD FLAGS(4);
  device_clock PT_LOAD FLAGS(4);
  cmdq_resources PT_LOAD FLAGS(4);
  runtime_ids PT_LOAD FLAGS(4);
  runtime_values PT_LOAD FLAGS(4);
  boot_modes PT_LOAD FLAGS(4);
  boot_path PT_LOAD FLAGS(4);
  timer_task_adapter PT_LOAD FLAGS(5);
  timer_callback_adapter PT_LOAD FLAGS(5);
  manager_task_adapter PT_LOAD FLAGS(5);
  event_task_adapter PT_LOAD FLAGS(5);
  dfu_init_adapter PT_LOAD FLAGS(5);
  dfu_task_body PT_LOAD FLAGS(5);
  dfu_name PT_LOAD FLAGS(4);
  event_queue_name PT_LOAD FLAGS(4);
  event_mutex_name PT_LOAD FLAGS(4);
  event_thread_name PT_LOAD FLAGS(4);
  expand_adapter PT_LOAD FLAGS(5);
  error_string PT_LOAD FLAGS(4);
  zero_adapter PT_LOAD FLAGS(5);
  records PT_LOAD FLAGS(4);
  callback_text PT_LOAD FLAGS(5);
  source_path PT_LOAD FLAGS(4);
  manager_attributes PT_LOAD FLAGS(4);
  banner_string PT_LOAD FLAGS(4);
  function_string PT_LOAD FLAGS(4);
  module_string PT_LOAD FLAGS(4);
  manager_name PT_LOAD FLAGS(4);
  idle_name PT_LOAD FLAGS(4);
  timer_name PT_LOAD FLAGS(4);
}

opencfw_boot_platform_system_init = opencfw_boot_main_init;
opencfw_boot_platform_terminal = 0x4329c5;
opencfw_provider_41f9d8 = opencfw_boot_delay_scaled;
opencfw_provider_41f9f8 = opencfw_boot_init_table_default;
opencfw_provider_41f846 = opencfw_boot_platform_configure;
opencfw_provider_41ac44 = opencfw_boot_coprocessor_enable;
opencfw_provider_41ac5a = opencfw_boot_fp_lazy_mode;

opencfw_provider_41e1e8 = opencfw_boot_icache_enable;
opencfw_provider_41e266 = opencfw_boot_dcache_enable;
opencfw_provider_41ba80 = opencfw_boot_control_mode_two;
opencfw_provider_415fae = opencfw_boot_plain_printf;
opencfw_provider_41fd70 = opencfw_boot_allocator_init;
opencfw_boot_fs_mutex_acquire = opencfw_boot_mutex_acquire;
opencfw_boot_fs_mutex_release = opencfw_boot_mutex_release;
opencfw_boot_allocator_log = 0x08002101;
printf = 0x08002111;

opencfw_provider_4176ce = opencfw_boot_elog_output;
opencfw_provider_416058 = opencfw_boot_kernel_initialize;
opencfw_provider_4160fe = opencfw_boot_thread_new;
opencfw_provider_41b2f8 = opencfw_bl_mask_interrupts;

opencfw_provider_4160b0 = opencfw_boot_kernel_start;
/* TEST/CUT USE ONLY. These aliases branch into the locked bootloader image;
 * they are not source implementations and must never satisfy a full
 * source-build dependency. Use only in a harness that maps the exact image. */

opencfw_bl_task_return = 0x41b391;
opencfw_bl_stack_overflow = 0x41b601;

opencfw_boot_nor_init = opencfw_provider_420476;
opencfw_boot_nor_read_jedec_id = opencfw_bl_nor_read_jedec_id;








opencfw_provider_4205f4 = opencfw_bl_mspi_status_transfer;
opencfw_boot_status_transfer = opencfw_bl_mspi_status_transfer;
opencfw_bl_status_transfer_error = opencfw_boot_plain_printf;

opencfw_boot_nor_mspi_init = opencfw_provider_420254;
opencfw_boot_mspi_handle_init = opencfw_provider_424a5a;
opencfw_bl_mspi_handle_initialize = opencfw_provider_424a5a;
opencfw_hal_power_control = opencfw_bl_power_control;


opencfw_bl_log = opencfw_boot_elog_output;

opencfw_bl_transfer_error = opencfw_boot_plain_printf;
opencfw_bl_delay = opencfw_boot_delay_scaled;

opencfw_publish_device_mode = opencfw_publish_mspi_mode;


/* Native termination alias supplied by source assembler. */
opencfw_provider_4160e8 = opencfw_boot_tick_get;
opencfw_provider_416816 = opencfw_bl_queue_create;
opencfw_provider_416920 = opencfw_bl_queue_get;
opencfw_provider_42dca2 = opencfw_boot_dfu_send;
opencfw_boot_dfu_queue_put = opencfw_bl_queue_put;
opencfw_boot_dfu_flags_set = opencfw_provider_41623a;
opencfw_boot_dfu_log = 0x08002121;

opencfw_bl_kernel_queue_create_static = opencfw_boot_timer_queue_fresh;
opencfw_bl_malloc_failed = 0x41b5f7;
opencfw_boot_dfu_queue_new = opencfw_bl_queue_create;
opencfw_boot_dfu_thread_new = opencfw_boot_thread_new;
opencfw_boot_dfu_panic = opencfw_bl_mask_interrupts;
opencfw_boot_dfu_flags_wait = opencfw_provider_4162c4;
opencfw_boot_dfu_terminal = 0x42e1db;
opencfw_boot_dfu_queue_get = opencfw_bl_queue_get;

/* Native DFU error transaction from platform_control/control.c. */
opencfw_boot_runtime_call = opencfw_boot_cache_maintain;
opencfw_boot_log = opencfw_boot_elog_output;
/* Explicit initializer child boundaries; bodies are source linked. */
/* opencfw_bl_descriptor_register is now source owned. */
/* ADC initializer is source-owned. */
/* ADC control/getters now source owned. */
/* ADC profile transfer now source-owned. */
/* ADC context configure now source-owned. */
/* ADC profile apply now source-owned. */
/* ADC channel configure now source-owned. */
/* ADC activate now source-owned. */
/* ADC enable now source-owned. */
/* ADC command now source-owned. */
/* ADC enumerate now source-owned. */
/* ADC disable now source-owned. */
/* ADC normalize now source-owned. */
/* ADC metadata reset is source-owned; no peripheral-drain inference. */
opencfw_bl_generic_log = opencfw_boot_plain_printf;
/* register_mode source-owned. */
/* post_context_register source-owned. */
opencfw_bl_post_configure = opencfw_boot_control_power_apply;
/* post_validate source-owned. */
/* post_activate source-owned. */
/* post_enable source-owned. */
/* post_precommit source-owned. */
/* post_finish source-owned. */
opencfw_bl_post_record_initialized = opencfw_boot_control_mode_one;
opencfw_bl_context_claim = opencfw_boot_context_claim;
opencfw_bl_config_transaction = opencfw_boot_context_transaction;
opencfw_bl_instance_configure = opencfw_boot_context_configure;
opencfw_bl_context_enable = opencfw_boot_context_enable;
opencfw_bl_config_retry = opencfw_boot_context_retry;
opencfw_bl_context_interrupt_enable = opencfw_boot_context_interrupt_enable;
opencfw_bl_context_nvic_enable = opencfw_boot_context_nvic_enable;
opencfw_bl_semaphore_create = opencfw_boot_semaphore_create;
/* service_guard source-owned. */
/* service_commit source-owned. */
/* service_wake source-owned. */
/* service_sleep source-owned. */
opencfw_bl_mutex_create = opencfw_provider_416610;
opencfw_bl_logger_output = opencfw_boot_elog_output;

SECTIONS {
  .gx_cfg 0x434164 : { KEEP(*(.rodata.opencfw_gx_cfg)) } :gx_cfg
  .root_shared_cfg 0x434024 : { KEEP(*(.rodata.opencfw_root_shared_cfg)) } :root_shared_cfg
  .ton_rows 0x433f20 : { KEEP(*(.rodata.opencfw_ton_rows)) } :ton_rows
  . = 0x10000;
  .storage_read 0x430a9c : { KEEP(*(.text.storage_read)) } :storage_callbacks
  .storage_program 0x430ac4 : { KEEP(*(.text.storage_program)) } :storage_callbacks
  .storage_erase 0x430aec : { KEEP(*(.text.storage_erase)) } :storage_callbacks
  /* Native compiled source in its own bounded segment. This avoids exceeding
   * the 64KiB relocated source slot; no locked executable bytes are retained. */
  /* Assembly input sections may declare byte alignment. Keep each object
   * after mixed rodata aligned; verify_code_alignment checks actual $t PCs. */
  .source_idle 0x50000 : {
    KEEP(*startup_events_a.o(.text* .rodata*))
    KEEP(*pcm22_sequence5.o(.text* .rodata*))
    KEEP(*pcm22_hot_transitions.o(.text* .rodata*))
    KEEP(*spot_sleep_wrappers.o(.text* .rodata*))
    KEEP(*idle_chain.o(.text* .rodata*))
    KEEP(*tickless_native.o(.text* .rodata*))
    KEEP(*sysctrl_sleep.o(.text* .rodata*))
    KEEP(*sleep_helpers.o(.text* .rodata*))
    KEEP(*sleep_policy.o(.text* .rodata*))
  } :source_idle
  .source_cache 0x30000 : {
    . = ALIGN(4);
    KEEP(*startup_gx_event.o(.text* .rodata*))
    KEEP(*startup_gx_children.o(.text* .rodata*))
    KEEP(*startup_gx_adapters.o(.text*))
    KEEP(*timer_support.o(.text* .rodata*))
    KEEP(*startup_event_a_trim.o(.text* .rodata*))
    KEEP(*startup_event_a_transitions.o(.text* .rodata*))
    KEEP(*startup_event_a_sequences_0_2.o(.text* .rodata*))
    KEEP(*pcm22_handlers.o(.text* .rodata*))
    KEEP(*pcm22_sequence8.o(.text* .rodata*))
    KEEP(*pcm22_sequence6.o(.text* .rodata*))
    KEEP(*pcm22_sequence20.o(.text* .rodata*))
    KEEP(*pcm21_boost.o(.text* .rodata*))
    KEEP(*pcm22_handler15.o(.text* .rodata*))
    KEEP(*pcm22_handler16.o(.text* .rodata*))
    KEEP(*pcm22_handler17.o(.text* .rodata*))
    KEEP(*pcm22_handler3.o(.text* .rodata*))
    KEEP(*handler1-softfp.o(.text* .rodata*))
    KEEP(*initialized_data.o(.text* .rodata*))


    KEEP(*root_clock_coupled.o(.text* .rodata*))
    KEEP(*startup_root_entry.o(.text*))
    KEEP(*startup_ton_hooks.o(.text* .rodata*))
    *cache_enable.o(.text*)
    . = ALIGN(4);
    *control_request_state.o(.text*)
    . = ALIGN(4);
    *control_request_clock.o(.text*)
    . = ALIGN(4);
    *control_request_transactions.o(.text*)
    . = ALIGN(4);
    *control_request34.o(.text*)
    . = ALIGN(4);
    *control_request_helpers.o(.text*)
    . = ALIGN(4);
    *queue_descriptors.o(.text*)
    . = ALIGN(4);
    *mode_publisher.o(.text* .rodata*)
    . = ALIGN(4);
    *mode_publisher_abi.o(.text*)
    . = ALIGN(4);
    *serial_mode_switch.o(.text* .rodata*)
    . = ALIGN(4);
    *xip_address_mode.o(.text* .rodata*)
    . = ALIGN(4);
    *timing_scan.o(.text* .rodata*)
    . = ALIGN(4);
    *nor_timing_wrapper.o(.text* .rodata*)
    . = ALIGN(4);
    *nor_commands.o(.text* .rodata*)
    . = ALIGN(4);
    *init_table.o(.text* .rodata*)
    . = ALIGN(4);
    *qsort.o(.text* .rodata*)
    . = ALIGN(4);
    *initializer_callbacks.o(.text* .rodata*)
    . = ALIGN(4);
    *mode_register.o(.text* .rodata*)
    . = ALIGN(4);
    *platform_finish.o(.text* .rodata*)
    . = ALIGN(4);
    *context_interrupt.o(.text* .rodata*)
    . = ALIGN(4);
    *context_claim.o(.text* .rodata*)
    . = ALIGN(4);
    *context_transaction.o(.text* .rodata*)
    . = ALIGN(4);
    *context_instance.o(.text* .rodata*)
    . = ALIGN(4);
    *context_clock.o(.text* .rodata*)
    . = ALIGN(4);
    *context_queue.o(.text* .rodata*)
    . = ALIGN(4);
    *context_retry.o(.text* .rodata*)
    . = ALIGN(4);
    *context_nvic.o(.text* .rodata*)
    . = ALIGN(4);
    *semaphore_create.o(.text* .rodata*)
    . = ALIGN(4);
    KEEP(*context_events.o(.text* .rodata*))
    . = ALIGN(4);
    KEEP(*context_irq.o(.text* .rodata*))
    . = ALIGN(4);
    KEEP(*gpio_descriptors.o(.text* .rodata*))
    . = ALIGN(4);
    KEEP(*service_records.o(.text* .rodata*))
    KEEP(*elog_setters.o(.text* .rodata*))
    KEEP(*elog_output.o(.text* .rodata*))
    KEEP(*elog_uart_tx.o(.text* .rodata*))
    KEEP(*startup_alternatives.o(.text* .rodata*))
    KEEP(*startup_config_leaves.o(.text* .rodata*))
    KEEP(*plain_printf.o(.text* .rodata*))
    KEEP(*startup_clock_config.o(.text* .rodata*))
    KEEP(*clock_generators.o(.text* .rodata*))
    KEEP(*clock_pll_math.o(.text* .rodata*))
    KEEP(*clock_pll_rounding.o(.text* .rodata*))
    KEEP(*clock_pll_mod.o(.text* .rodata*))
    KEEP(*uart_rx.o(.text* .rodata*))
    KEEP(*power_special_mode.o(.text* .rodata*))
    . = ALIGN(4);
    KEEP(*startup_shutdown.o(.text* .rodata*))
    . = ALIGN(4);
    KEEP(*startup_power_config.o(.text* .rodata*))
    KEEP(*startup_initialize_leaves.o(.text* .rodata*))
    KEEP(*startup_runtime.o(.text* .rodata*))
    KEEP(*startup_spot_handlers.o(.text* .rodata*))
    KEEP(*startup_spot_timer.o(.text* .rodata*))
    KEEP(*startup_spot_events.o(.text* .rodata*))
    KEEP(*startup_clockmux.o(.text* .rodata*))
    KEEP(*startup_clockmux_entry.o(.text* .rodata*))
    KEEP(*startup_clockmux_dependencies.o(.text* .rodata*))
    KEEP(*startup_power_register_read.o(.text* .rodata*))
    KEEP(*startup_cache_maintenance.o(.text* .rodata*))
    KEEP(*startup_memory_config.o(.text* .rodata*))
    KEEP(*mutex_kernel.o(.text* .rodata*))
    KEEP(*isr_delivery.o(.text* .rodata*))
    KEEP(*mutex.o(.text* .rodata*))
    KEEP(*uart_context.o(.text* .rodata*))
    KEEP(*adc_context.o(.text* .rodata*))
    . = ALIGN(4);
    KEEP(*adc_control.o(.text* .rodata*))
    KEEP(*adc_configuration.o(.text* .rodata*))
    KEEP(*adc_samples.o(.text* .rodata*))
    KEEP(*adc_profile.o(.text* .rodata*))
    . = ALIGN(4);
    *post_bringup.o(.text* .rodata*)
    . = ALIGN(4);
    *platform_bringup.o(.text* .rodata*)
  } :source_cache
  .text 0x10000 : { KEEP(*startup_ton_gate.o(.text*)) KEEP(*idle_cleanup.o(.text*)) KEEP(*runtime_action.o(.text* .rodata*)) KEEP(*native_deinit.o(.text* .rodata*)) KEEP(*teardown.o(.text* .rodata*)) KEEP(*teardown_native_aliases.o(.text* .rodata*)) KEEP(*exception_entry.o(.text*)) KEEP(*reset.o(.text*)) KEEP(*fpu.o(.text*)) *(.text*) *(.rodata) *(.rodata.str*) *(.rodata.cst*) } :source_text

  .boot_initializer_callbacks 0x433440 : { KEEP(*(.boot_initializer_callbacks)) } :initializer_table
  .boot_iom_context_pool 0x2001455c (NOLOAD) : { KEEP(*(.bss.boot_iom_context_pool)) } :iom_context_pool
  .boot_context_config 0x433d58 : { KEEP(*(.boot_context_config)) } :context_config

  .boot_service_mutex_attributes 0x433d28 : { KEEP(*(.boot_service_mutex_attributes)) } :service_mutex_attributes
  .boot_service_mutex_name 0x433f50 : { KEEP(*(.boot_service_mutex_name)) } :service_mutex_name
  .boot_uart_context_pool 0x20024400 (NOLOAD) : { KEEP(*(.bss.boot_uart_context_pool)) } :uart_context_pool
  .boot_adc_context_pool 0x20026df0 (NOLOAD) : { KEEP(*(.bss.boot_adc_context_pool)) } :adc_context_pool

  .boot_gpio_descriptors 0x42f674 : { KEEP(*(.boot_gpio_descriptors)) } :gpio_descriptors
  .boot_gpio_irqnums 0x43409c : { KEEP(*(.boot_gpio_irqnums)) } :gpio_irqnums

  .cmdq_resources 0x430880 : { KEEP(*(.cmdq_resources)) } :cmdq_resources

  . = 0x415326;
  .boot_expand_adapter : { KEEP(*(.boot_expand_adapter)) } :expand_adapter

  . = 0x431340;
  .rodata.main_file : { KEEP(*(.rodata.main_file)) } :source_path

  . = 0x43198c;
  .rodata.mode_error : { KEEP(*(.rodata.mode_error)) } :error_string

  . = 0x431e38;
  .boot_zero_adapter : { KEEP(*(.boot_zero_adapter)) } :zero_adapter

  . = 0x433024;
  .rodata.manager_attributes : { KEEP(*(.rodata.manager_attributes)) } :manager_attributes

  . = 0x4330d8;
  .boot_init_records : { KEEP(*(.boot_init_records)) } :records

  . = 0x42e39c;
  .callback_text : { KEEP(*(.callback_text)) } :callback_text

  . = 0x433360;
  .rodata.boot_banner : { KEEP(*(.rodata.boot_banner)) } :banner_string

  . = 0x43411c;
  .rodata.main_function : { KEEP(*(.rodata.main_function)) } :function_string

  . = 0x434124;
  .rodata.main_module : { KEEP(*(.rodata.main_module)) } :module_string

  . = 0x434134;
  .rodata.manager_name : { KEEP(*(.rodata.manager_name)) } :manager_name

  . = 0x43412c;
  .boot_idle_name : { KEEP(*(.boot_idle_name)) } :idle_name

  . = 0x43413c;
  .boot_timer_name : { KEEP(*(.boot_timer_name)) } :timer_name

  .timer_callback_adapter 0x41639a : { KEEP(*(.timer_callback_adapter)) } :timer_callback_adapter
  .timer_task_adapter 0x419444 : { KEEP(*(.timer_task_adapter)) } :timer_task_adapter
  .manager_task_adapter 0x42e2f8 : { KEEP(*(.manager_task_adapter)) } :manager_task_adapter
  .event_task_adapter 0x42e644 : { KEEP(*(.event_task_adapter)) } :event_task_adapter
  .event_queue_name 0x433b3c : { KEEP(*(.event_queue_name)) } :event_queue_name
  .event_mutex_name 0x433b50 : { KEEP(*(.event_mutex_name)) } :event_mutex_name
  .event_thread_name 0x433f68 : { KEEP(*(.event_thread_name)) } :event_thread_name
  .dfu_init_adapter 0x42ddae : { KEEP(*(.dfu_init_adapter)) } :dfu_init_adapter
  .boot_dfu_orchestrator 0x42dd14 : { KEEP(*(.boot_dfu_orchestrator)) } :dfu_task_body
  .boot_thread_name 0x4341a4 : { KEEP(*(.boot_thread_name)) } :dfu_name
  .boot_modes 0x42dad0 : { KEEP(*(.boot_modes)) } :boot_modes
  .boot_path 0x4336e4 : { KEEP(*(.boot_path)) } :boot_path
  .boot_platform_config 0x433d98 : { KEEP(*(.boot_platform_config)) } :runtime_ids
  .boot_device_clock_factors 0x433754 : { KEEP(*(.boot_device_clock_factors)) } :device_clock
  .boot_storage_range_table 0x43401c : { KEEP(*(.boot_storage_range_table)) } :storage_ranges
  .boot_runtime_values 0x434158 : { KEEP(*(.boot_runtime_values)) } :runtime_values
  /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) }
}

opencfw_provider_41602a = opencfw_bl_context_guard;




opencfw_boot_control_log = 0x08002131;




opencfw_hal_delay_us = opencfw_boot_delay_us_math;


/* Accepted UART power branch source-owned. */

opencfw_boot_nor_prog = opencfw_provider_420b0c;
opencfw_boot_nor_erase = opencfw_provider_420a08;
opencfw_boot_fs_error = opencfw_boot_plain_printf;

opencfw_boot_control_delay_us = opencfw_boot_delay_us_math;



opencfw_bl_delay_raw = opencfw_boot_delay_raw;
/* Stock416088 no-argument uint32 wrapper, direct differential216 cases. */
opencfw_bl_kernel_state = opencfw_boot_kernel_state;
opencfw_bl_task_delay = 0x416379;



opencfw_bl_printf = opencfw_boot_plain_printf;




opencfw_bl_critical_save = opencfw_boot_control_critical_save;
opencfw_bl_delay_us = opencfw_hal_delay_us;
opencfw_bl_clock_request = clock_request;

opencfw_boot_rom_mram_program = 0x0200ff21;
opencfw_boot_power_control = opencfw_boot_power_callback;

/* Mode0 wait is not exercised by reset mode1; remains an explicit source gap. */
/* Native INFO dispatch; only resident ROM read body is external. */
opencfw_boot_rom48 = 0x00000049;

opencfw_boot_rom_delay_cycles = 0x00000041;

/* Stock426c10 three-argument fill; wrapper discards its return. */
opencfw_bl_clear = memset;

/* CQ adapters are narrower remaining IOM dependencies, not whole transaction cuts. */
/* CQ adapters now execute native IOM source and existing generic queue bodies. */

opencfw_boot_elog_snprintf = 0x41b219;
opencfw_boot_elog_vsnprintf = 0x41b25d;






opencfw_boot_power_register_update = opencfw_bl_power_register_update;
opencfw_boot_startup_power_initialize = 0x41c4b5;



/* Native indexed getter; clockmux caller supplies a valid output local. */
opencfw_power_register_read = opencfw_bl_power_register_read;

child_42252e = opencfw_boot_shutdown_debug_release;
child_41c17a = opencfw_bl_mspi_mode_leave;
child_41c2d8 = opencfw_boot_control_query;
child_41bf84 = opencfw_bl_mspi_mode_enter;
child_41b918 = opencfw_boot_startup_trim_version;
child_41c320 = opencfw_boot_startup_info_cache;
child_421548 = opencfw_boot_device_mode_wait;
child_41ce52 = opencfw_boot_startup_spot_dispatch;
child_41bbd0 = opencfw_boot_startup_mcu_memory;
child_41be36 = opencfw_boot_startup_shared_memory;
child_41b8ec = opencfw_boot_control_critical_save;

opencfw_provider_418a98 = opencfw_boot_idle_cleanup;

/* Explicit native idle chain and retained sleep-helper contracts. */
cleanup = opencfw_boot_idle_cleanup;
reschedule = opencfw_bl_kernel_reschedule;
suspend_scheduler = opencfw_bl_scheduler_suspend;
resume_scheduler = opencfw_bl_scheduler_resume;
buck_override = opencfw_boot_ton_gate_write;
power_state = power_state_wrapper;
delay_one = opencfw_hal_delay_us;
boost_service = boost_service_wrapper;
opencfw_provider_4189ac = idle_entry;
opencfw_provider_4181e4 = expected_idle_ticks;
opencfw_provider_418a00 = confirm_sleep;
opencfw_provider_418394 = step_ticks;
opencfw_provider_41b754 = tickless_sleep;
opencfw_provider_41a71e = deep_sleep;
ASSERT(SIZEOF(.source_idle) <= 65536, "idle source slot overflow")
ASSERT(SIZEOF(.text) <= 65536, "text source slot overflow")
ASSERT(SIZEOF(.source_cache) <= 65536, "cache source slot overflow")
