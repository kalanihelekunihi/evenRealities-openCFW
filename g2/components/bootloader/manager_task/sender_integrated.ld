ENTRY(opencfw_boot_manager_task)
opencfw_provider_42e254 = 0x42e255;
opencfw_provider_42e278 = 0x42e279;
opencfw_provider_42e2ea = 0x42e2eb;
opencfw_provider_4162c4 = 0x4162c5;
opencfw_provider_4160e8 = 0x4160e9;
opencfw_provider_42dca2 = opencfw_boot_dfu_send;
opencfw_provider_4176ce = 0x4176cf;
SECTIONS { . = 0x10000; .text : { *(.text*) *(.rodata*) }
/DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) } }

SECTIONS { . = 0x10000; .text : { *(.text*) } .rodata : { *(.rodata*) } .data : { *(.data*) } .bss : { *(.bss*) } .boot_thread_name 0x4341a4 : { *(.boot_thread_name) } /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) } }
opencfw_boot_dfu_queue_get = 0x416921;
opencfw_boot_dfu_runtime_enable = 0x42ddf3;
opencfw_boot_dfu_error_transaction = 0x42de0f;
opencfw_boot_dfu_log = 0x08002121;
opencfw_boot_stream_mode = 0x42d84d;
opencfw_boot_file_open = 0x4153a5;
opencfw_boot_file_read = 0x415485;
opencfw_boot_file_close = 0x415447;
opencfw_boot_verify = 0x42d891;
opencfw_boot_program = 0x42dae9;
opencfw_boot_vector_handoff = 0x42dc91;
opencfw_boot_dfu_task = 0x42de59;
opencfw_boot_dfu_queue_new = 0x416817;
opencfw_boot_dfu_queue_put = 0x4168a3;
opencfw_boot_dfu_thread_new = 0x4160ff;
opencfw_boot_dfu_thread_terminate = 0x416201;
opencfw_boot_dfu_flags_set = 0x41623b;
opencfw_boot_dfu_flags_wait = 0x4162c5;
opencfw_boot_dfu_panic = 0x41b2f9;
opencfw_boot_dfu_control_one = 0x42dd9b;
opencfw_boot_dfu_control_two = 0x42dda5;
opencfw_boot_dfu_runtime_context = 0x42dd69;
opencfw_boot_dfu_terminal = 0x42e1db;
