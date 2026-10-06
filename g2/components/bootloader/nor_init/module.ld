/* SPDX-License-Identifier: MIT */
ENTRY(opencfw_provider_420476)
PHDRS {
  text PT_LOAD FLAGS(5);
}
opencfw_boot_nor_init = opencfw_provider_420476;
opencfw_boot_nor_read_jedec_id = opencfw_bl_nor_read_jedec_id;
opencfw_provider_420254 = 0x420255;
opencfw_provider_41f9d8 = 0x41f9d9;
opencfw_provider_42052a = 0x42052b;
opencfw_provider_420f10 = 0x420f11;
opencfw_provider_4201ba = 0x4201bb;
opencfw_provider_420890 = 0x420891;
opencfw_provider_420c5c = 0x420c5d;
opencfw_provider_41fe62 = 0x41fe63;
opencfw_provider_41fe28 = 0x41fe29;
opencfw_provider_4176ce = 0x4176cf;
opencfw_provider_4205f4 = opencfw_bl_mspi_status_transfer;
opencfw_boot_status_transfer = opencfw_bl_mspi_status_transfer;
opencfw_bl_mspi_blocking_transfer = 0x4262e1;
opencfw_bl_status_transfer_error = 0x415faf;

SECTIONS {
  . = 0x10000;
  .text : { *(.text*) *(.rodata*) } :text
  /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) }
}
