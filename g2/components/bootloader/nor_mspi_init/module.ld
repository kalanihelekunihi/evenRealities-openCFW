/* SPDX-License-Identifier: MIT */
ENTRY(opencfw_provider_420254)
PHDRS { text PT_LOAD FLAGS(5); }

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

SECTIONS {
  . = 0x10000;
  .text : { *(.text*) *(.rodata*) } :text
  /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) }
}
