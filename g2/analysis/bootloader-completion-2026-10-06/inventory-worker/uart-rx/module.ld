ENTRY(opencfw_boot_uart_rx_start)
SECTIONS { . = 0x10000; .text : { *(.text*) *(.rodata*) } }
/* Independent module cuts only; integrated ELF binds critical-save natively. */
opencfw_bl_critical_save = 0x08001001;
opencfw_boot_delay_us_math = 0x08001011;
