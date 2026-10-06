ENTRY(opencfw_boot_dfu_task)
SECTIONS { . = 0x10000; .text : { *(.text*) } .rodata : { *(.rodata*) } .data : { *(.data*) } .bss : { *(.bss*) } /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) } }
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
