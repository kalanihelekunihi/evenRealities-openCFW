SECTIONS {
  .g2_conversate_machine_context_200e3aec 0x200e3aec (NOLOAD) : {
    KEEP(*(.g2_conversate_machine_context_200e3aec))
  }
  .g2_conversate_ui_settings_extension_20071369 0x20071369 (NOLOAD) : {
    KEEP(*(.g2_conversate_ui_settings_extension_20071369))
  }
}
INSERT AFTER .bss;
ASSERT(SIZEOF(.g2_conversate_machine_context_200e3aec) == 8,
       "Conversate machine context size")
ASSERT(audio_conversate_machine_context_200e3aec == 0x200e3aec,
       "Conversate machine context address")
ASSERT(SIZEOF(.g2_conversate_ui_settings_extension_20071369) == 0x94,
       "Conversate UI settings extension size")
ASSERT(audio_conversate_ui_settings_extension_20071369 == 0x20071369,
       "Conversate UI settings extension address")
