/* Isolated source-owned section-placement probe, not a complete image link.
 * The native package loads 0x10023400..0x10026d7c into IRAM.  This script
 * places only the independently attributed vector and initialized tail.
 * Unplaced code/XIP, runtime 0x2002 aliases, loader copy, and alternate
 * startup paths remain required final-link inputs.
 */
SECTIONS
{
  .gx8002_vectors 0x10023400 : { KEEP(*(.gx8002.vectors.23400)) }
  .gx8002_clock_boot_25cd0 0x10025cd0 : { KEEP(*(.gx8002.clock_boot.25cd0)) }
  .gx8002_clock_boot_25ce0 0x10025ce0 : { KEEP(*(.gx8002.clock_boot.25ce0)) }
  .gx8002_clock_boot_25cf4 0x10025cf4 : { KEEP(*(.gx8002.clock_boot.25cf4)) }
  .gx8002_flash_state 0x100264e4 : { KEEP(*(.gx8002.flash_state.264e4)) }
  .gx8002_flash_api 0x10026504 : { KEEP(*(.gx8002.flash_api.26504)) }
  .gx8002_otp_2657c 0x1002657c : { KEEP(*(.gx8002.otp_protect.2657c)) }
  .gx8002_otp_265a4 0x100265a4 : { KEEP(*(.gx8002.otp_protect.265a4)) }
  .gx8002_otp_265dc 0x100265dc : { KEEP(*(.gx8002.otp_protect.265dc)) }
  .gx8002_flash_catalog 0x10026624 : { KEEP(*(.gx8002.flash_catalog.26624)) }
  .gx8002_flash_otp 0x100266cc : { KEEP(*(.gx8002.flash_otp_config.266cc)) }
  .gx8002_module_table 0x100266e0 : { KEEP(*(.gx8002.module_table.266e0)) }
  .gx8002_module_config 0x10026880 : { KEEP(*(.gx8002.module_config.26880)) }
  .gx8002_clock_defaults 0x100268c8 : { KEEP(*(.gx8002.clock_defaults.268c8)) }
  .gx8002_clock_sources_26904 0x10026904 : { KEEP(*(.gx8002.clock_sources.26904)) }
  .gx8002_clock_sources_26954 0x10026954 : { KEEP(*(.gx8002.clock_sources.26954)) }
  .gx8002_board_state 0x100269a4 : { KEEP(*(.gx8002.board_state.269a4)) }
  .gx8002_uart_channels 0x10026a94 : { KEEP(*(.gx8002.uart_channels.26a94)) }
  .gx8002_aout_context 0x10026b94 : { KEEP(*(.gx8002.sram.aout_context)) }
  .gx8002_aout_ops 0x10026bc8 : { KEEP(*(.gx8002.sram.aout_operations)) }
  .gx8002_aout_config 0x10026c1c : { KEEP(*(.gx8002.sram.aout_configuration)) }
  .gx8002_uart_rx_config 0x10026c74 : { KEEP(*(.gx8002.uart_rx_config.26c74)) }
  .gx8002_kws_keywords 0x10026c7c : { KEEP(*(.gx8002.kws_keywords.26c7c)) }
  .gx8002_sample_prestate 0x10026d2c : { KEEP(*(.gx8002.sample_prestate.26d2c)) }
  .gx8002_sample_registration 0x10026d30 : { KEEP(*(.gx8002.sample_registration.26d30)) }
  .gx8002_request_initial 0x10026d5c : { KEEP(*(.gx8002.request_initial.26d5c)) }
  .gx8002_console_port 0x2002731c (NOLOAD) : { KEEP(*(.bss.gx8002.console_port.2731c)) }
}
ASSERT(SIZEOF(.gx8002_vectors) == 0x100, "vector extent differs from stock")
ASSERT(SIZEOF(.gx8002_clock_boot_25cd0) == 0x10, "low-power clock pair differs from stock")
ASSERT(SIZEOF(.gx8002_clock_boot_25ce0) == 0x14, "PLL adjustment data differs from stock")
ASSERT(SIZEOF(.gx8002_clock_boot_25cf4) == 0x10, "start-mode-1 clock pair differs from stock")
ASSERT(ADDR(.gx8002_clock_boot_25cd0) + SIZEOF(.gx8002_clock_boot_25cd0) == ADDR(.gx8002_clock_boot_25ce0),
       "clock pair and adjustment placement differ from stock")
ASSERT(ADDR(.gx8002_flash_state) == 0x100264e4, "tail start differs from stock")
ASSERT(ADDR(.gx8002_request_initial) + SIZEOF(.gx8002_request_initial) == 0x10026d7c,
       "tail end differs from stock")
ASSERT(SIZEOF(.gx8002_console_port) == 4, "console BSS word missing")
ASSERT(ADDR(.gx8002_console_port) >= 0x20026d80 &&
       ADDR(.gx8002_console_port) + SIZEOF(.gx8002_console_port) <= 0x2002ecec,
       "console BSS outside native clear range")
