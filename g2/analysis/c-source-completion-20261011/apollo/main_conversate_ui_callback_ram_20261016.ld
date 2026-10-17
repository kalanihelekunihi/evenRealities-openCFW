SECTIONS {
  .g2_conversate_registry_context_200004d8 0x200004d8 (NOLOAD) : {
    KEEP(*(.g2_conversate_registry_context_200004d8))
  }
  .g2_conversate_ui_start_tick_20074390 0x20074390 (NOLOAD) : {
    KEEP(*(.g2_conversate_ui_start_tick_20074390))
  }
  .g2_conversate_ui_app_id_200743a0 0x200743a0 (NOLOAD) : {
    KEEP(*(.g2_conversate_ui_app_id_200743a0))
  }
}
INSERT AFTER .bss;
ASSERT(SIZEOF(.g2_conversate_registry_context_200004d8) == 8,
       "Conversate registry context accessed prefix size")
ASSERT(SIZEOF(.g2_conversate_ui_start_tick_20074390) == 4,
       "Conversate UI start tick size")
ASSERT(SIZEOF(.g2_conversate_ui_app_id_200743a0) == 4,
       "Conversate UI app id size")
ASSERT(audio_uart_registry_context_200004d8 == 0x200004d8,
       "Conversate registry context address")
ASSERT(audio_conversate_ui_start_tick_20074390 == 0x20074390,
       "Conversate UI start tick address")
ASSERT(audio_conversate_ui_app_id_200743a0 == 0x200743a0,
       "Conversate UI app id address")
