ENTRY(Cy_Flash_WriteRow)
memcpy = 0xAA2D;
SECTIONS {
 .assembly 0x4480 : { *assembly.o(.text) }
 .process 0x8BF4 : { *(.text.ProcessStatusCode) }
 .valid 0x8C74 : { *(.text.Cy_Flash_ValidAddr) }
 .row 0x8CA8 : { *(.text.Cy_Flash_GetRowNum) }
 .backup 0x8CC4 : { *(.text.Cy_Flash_ClockBackup) }
 .config 0x8D00 : { *(.text.Cy_Flash_ClockConfig) }
 .restore 0x8D20 : { *(.text.Cy_Flash_ClockRestore) }
 .write_row 0x8D50 : { *(.text.Cy_Flash_WriteRow) }
 .switch 0xB51C : { *(.rodata.ProcessStatusCode) }
 .backup_state 0x20000F04 (NOLOAD) : { *(.bss.cySysFlashBackup) }
 /DISCARD/ : { *(.ARM.exidx*) *(.comment*) }
}
