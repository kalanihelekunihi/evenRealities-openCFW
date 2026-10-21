/* SPDX-License-Identifier: MIT */
ENTRY(opencfw_provider_42052a)
PHDRS { text PT_LOAD FLAGS(5); }

opencfw_boot_reset_commands = opencfw_provider_42052a;
opencfw_boot_read_mode = opencfw_provider_420f10;
opencfw_boot_timing_apply = opencfw_provider_4201ba;
opencfw_bl_mspi_blocking_transfer = 0x4262e1;
opencfw_bl_clear = 0x426c11;
opencfw_bl_transfer_error = 0x415faf;
opencfw_bl_delay = 0x41f9d9;
opencfw_bl_log = 0x4176cf;
opencfw_hal_mspi_disable = 0x4250f1;
opencfw_hal_mspi_device_configure = 0x424be5;
opencfw_hal_mspi_enable = 0x425067;
opencfw_hal_mspi_control = 0x4251c1;
opencfw_hal_mspi_control_latency = 0x41ff35;
opencfw_publish_device_mode = 0x41fadd;
opencfw_provider_420002 = 0x420003;

SECTIONS {
  . = 0x10000;
  .text : { *(.text*) *(.rodata*) } :text
  /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) }
}
