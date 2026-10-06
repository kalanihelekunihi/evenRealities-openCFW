/* SPDX-License-Identifier: MIT */
ENTRY(opencfw_provider_41866a)
PHDRS { text PT_LOAD FLAGS(5); }

opencfw_boot_task_block = 0x419187;
opencfw_boot_event_flags_wait = opencfw_provider_416590;
opencfw_boot_kernel_flags_wait = opencfw_provider_4199dc;
opencfw_provider_41602a = 0x41602b;
opencfw_bl_mask_interrupts = 0x41b2f9;
opencfw_bl_queue_runtime_mode = 0x418b57;
opencfw_bl_scheduler_suspend = 0x4181d9;
opencfw_bl_scheduler_resume = 0x418229;
opencfw_bl_kernel_reschedule = 0x41b3d1;
opencfw_bl_kernel_enter = 0x41b3e5;
opencfw_bl_kernel_exit = 0x41b3fd;
opencfw_boot_thread_notify_wait = 0x418dad;
opencfw_boot_thread_notify = 0x418e71;
opencfw_boot_isr_thread_notify = 0x418fe9;
opencfw_boot_tick_get = 0x41835b;

SECTIONS {
  . = 0x10000;
  .text : { *(.text*) *(.rodata*) } :text
  /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) }
}
