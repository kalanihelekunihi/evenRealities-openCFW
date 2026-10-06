ENTRY(opencfw_boot_reset_entry)
PHDRS {
  source_text PT_LOAD FLAGS(5);
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
opencfw_provider_41f9d8 = 0x41f9d9;
opencfw_provider_41f9f8 = 0x41f9f9;
opencfw_provider_41f846 = 0x41f847;
opencfw_provider_41ac44 = 0x41ac45;
opencfw_provider_41ac5a = 0x41ac5b;
opencfw_provider_41fa50 = 0x41fa51;
opencfw_provider_41e1e8 = 0x41e1e9;
opencfw_provider_41e266 = 0x41e267;
opencfw_provider_41ba80 = 0x41ba81;
opencfw_provider_415fae = 0x415faf;
opencfw_provider_41fd70 = opencfw_boot_allocator_init;
opencfw_boot_fs_mutex_acquire = 0x4166ab;
opencfw_boot_fs_mutex_release = 0x416711;
opencfw_boot_allocator_log = 0x08002101;
printf = 0x08002111;

opencfw_provider_4176ce = 0x4176cf;
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



opencfw_provider_4201ba = 0x4201bb;
opencfw_provider_420890 = 0x420891;
opencfw_provider_420c5c = 0x420c5d;


opencfw_provider_4205f4 = opencfw_bl_mspi_status_transfer;
opencfw_boot_status_transfer = opencfw_bl_mspi_status_transfer;
opencfw_bl_status_transfer_error = 0x415faf;

opencfw_boot_nor_mspi_init = opencfw_provider_420254;
opencfw_boot_mspi_handle_init = opencfw_provider_424a5a;
opencfw_bl_mspi_handle_initialize = opencfw_provider_424a5a;
opencfw_hal_power_control = 0x426809;
opencfw_hal_mspi_device_configure = 0x424be5;
opencfw_hal_mspi_control_latency = 0x41ff35;
opencfw_publish_mspi_mode = 0x41fadd;
opencfw_read_mspi_register_id = 0x41d90f;
opencfw_bl_log = 0x4176cf;

opencfw_bl_transfer_error = 0x415faf;
opencfw_bl_delay = 0x41f9d9;
opencfw_hal_mspi_control = 0x4251c1;
opencfw_publish_device_mode = 0x41fadd;


opencfw_provider_416200 = 0x416201;
opencfw_provider_4160e8 = opencfw_boot_tick_get;
opencfw_provider_416816 = opencfw_bl_queue_create;
opencfw_provider_416920 = opencfw_bl_queue_get;
opencfw_provider_42dca2 = opencfw_boot_dfu_send;
opencfw_boot_dfu_queue_put = opencfw_bl_queue_put;
opencfw_boot_dfu_flags_set = opencfw_provider_41623a;
opencfw_boot_dfu_log = 0x08002121;

opencfw_bl_kernel_queue_create_static = opencfw_boot_timer_queue_fresh;
opencfw_bl_kernel_queue_put_from_isr = 0x41a025;
opencfw_bl_kernel_queue_get_from_isr = 0x41a3b1;
opencfw_bl_malloc_failed = 0x41b5f7;
opencfw_boot_dfu_queue_new = opencfw_bl_queue_create;
opencfw_boot_dfu_thread_new = opencfw_boot_thread_new;
opencfw_boot_dfu_panic = opencfw_bl_mask_interrupts;
opencfw_boot_dfu_flags_wait = opencfw_provider_4162c4;
opencfw_boot_dfu_terminal = 0x42e1db;
opencfw_boot_dfu_queue_get = opencfw_bl_queue_get;

opencfw_boot_dfu_error_transaction = 0x42de0f;
opencfw_boot_runtime_call = 0x41e349;
opencfw_boot_log = 0x4176cf;
SECTIONS {
  . = 0x10000;
  .text : { KEEP(*exception_entry.o(.text*)) KEEP(*reset.o(.text*)) KEEP(*fpu.o(.text*)) *(.text*) *(.rodata) *(.rodata.str*) *(.rodata.cst*) } :source_text

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
  .boot_runtime_ids 0x433d98 : { KEEP(*(.boot_runtime_ids)) } :runtime_ids
  .boot_runtime_values 0x434158 : { KEEP(*(.boot_runtime_values)) } :runtime_values
  /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) }
}

opencfw_provider_41602a = opencfw_bl_context_guard;
opencfw_boot_isr_thread_notify = 0x418fe9;
opencfw_bl_event_flags_set_isr = 0x419bd3;

opencfw_boot_control_guard_begin = 0x41bd93;
opencfw_boot_control_guard_end = 0x41bde5;
opencfw_boot_control_mram = 0x42e8a5;
opencfw_boot_control_log = 0x08002131;

opencfw_hal_mspi_cq_init = 0x423f29;
opencfw_hal_mspi_cq_disable = 0x423fad;
opencfw_hal_mspi_cq_term = 0x423f55;
opencfw_hal_delay_us = 0x41d1c1;


opencfw_boot_control_power_apply_configure = 0x08002211;

opencfw_boot_nor_prog = 0x420b0d;
opencfw_boot_nor_erase = 0x420a09;
opencfw_boot_fs_error = 0x415faf;

opencfw_boot_control_delay_us = 0x41d1c1;

opencfw_boot_nor_read = 0x420f71;
