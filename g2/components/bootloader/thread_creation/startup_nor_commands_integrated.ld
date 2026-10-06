ENTRY(opencfw_boot_system_entry)
PHDRS {
  source_text PT_LOAD FLAGS(5);
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

opencfw_provider_421210 = 0x421211;
opencfw_provider_4176ce = 0x4176cf;
opencfw_provider_416058 = opencfw_boot_kernel_initialize;
opencfw_provider_4160fe = opencfw_boot_thread_new;
opencfw_provider_41b2f8 = opencfw_bl_mask_interrupts;
opencfw_bl_kernel_dynamic_thread = 0x417d17;
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
opencfw_provider_41fe62 = 0x41fe63;
opencfw_provider_41fe28 = 0x41fe29;
opencfw_provider_4205f4 = opencfw_bl_mspi_status_transfer;
opencfw_boot_status_transfer = opencfw_bl_mspi_status_transfer;
opencfw_bl_mspi_blocking_transfer = 0x4262e1;
opencfw_bl_status_transfer_error = 0x415faf;

opencfw_boot_nor_mspi_init = opencfw_provider_420254;
opencfw_boot_mspi_handle_init = opencfw_provider_424a5a;
opencfw_bl_mspi_handle_initialize = opencfw_provider_424a5a;
opencfw_hal_power_control = 0x426809;
opencfw_hal_mspi_configure = 0x424af1;
opencfw_hal_mspi_device_configure = 0x424be5;
opencfw_hal_mspi_enable = 0x425067;
opencfw_hal_mspi_deinitialize = 0x42516d;
opencfw_hal_mspi_interrupt_clear = 0x426507;
opencfw_hal_mspi_interrupt_enable = 0x426451;
opencfw_hal_mspi_control_latency = 0x41ff35;
opencfw_publish_mspi_mode = 0x41fadd;
opencfw_read_mspi_register_id = 0x41d90f;
opencfw_bl_interrupt_priority = 0x41fddf;
opencfw_bl_interrupt_enable = 0x41fdc1;
opencfw_bl_irq_guard_initialize = 0x41b8e1;
opencfw_bl_log = 0x4176cf;

opencfw_bl_transfer_error = 0x415faf;
opencfw_bl_delay = 0x41f9d9;
opencfw_hal_mspi_disable = 0x4250f1;
opencfw_hal_mspi_control = 0x4251c1;
opencfw_publish_device_mode = 0x41fadd;

SECTIONS {
  . = 0x10000;
  .text : { *(.text*) *(.rodata) } :source_text

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

  /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) }
}
