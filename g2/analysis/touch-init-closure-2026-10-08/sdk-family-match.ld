
__aeabi_uidiv = 0xa6c1; __aeabi_uidivmod = 0xa7cd; memset = 0xa9d5;
Cy_Flash_WriteRow = 0x8d51; memcpy = 0xaa2d;
SECTIONS {
 .match_ReadSimpleMode 0x7e44 : { *(.text.ReadSimpleMode) }
 .match_CalcChecksum 0x7e68 : { *(.text.CalcChecksum) }
 .match_WriteRow 0x7ea4 : { *(.text.WriteRow) }
 .match_CalculateRowChecksum 0x7f6c : { *(.text.CalculateRowChecksum) }
 .match_GetStoredRowChecksum 0x7f78 : { *(.text.GetStoredRowChecksum) }
 .match_CheckRowChecksum 0x7f7c : { *(.text.CheckRowChecksum) }
 .match_GetStoredSeqNum 0x7fa0 : { *(.text.GetStoredSeqNum) }
 .match_DefineLastWrittenRow 0x7fa4 : { *(.text.DefineLastWrittenRow) }
 .match_CheckLastWrittenRowIntegrity 0x8058 : { *(.text.CheckLastWrittenRowIntegrity) }
 .match_GetNextRowPointer 0x810c : { *(.text.GetNextRowPointer) }
 .match_GetReadRowPointer 0x812a : { *(.text.GetReadRowPointer) }
 .match_CopyHistoricData 0x814c : { *(.text.CopyHistoricData) }
 .match_ReadExtendedMode 0x82e0 : { *(.text.ReadExtendedMode) }
 .match_Cy_Em_EEPROM_Read 0x8a78 : { *(.text.Cy_Em_EEPROM_Read) }
 .match_GetPhysicalSize 0x8200 : { *(.text.GetPhysicalSize) }
 .match_CheckRanges 0x8220 : { *(.text.CheckRanges) }
 .match_ComputeEEPROMProgramSize 0x828c : { *(.text.ComputeEEPROMProgramSize) }
 .match_Cy_Em_EEPROM_Init_BD 0x898c : { *(.text.Cy_Em_EEPROM_Init_BD) }
 .match_Cy_Em_EEPROM_Init 0x8a38 : { *(.text.Cy_Em_EEPROM_Init) }
 .provider 0x20000ed4 (NOLOAD) : { *(.bss._mtb_emeeprom_bsd) }
 .scratch 0x20000cd4 (NOLOAD) : { *(.bss.writeRamBuffer) }

 .match_read_size 0x4780 : { *(.text.mtb_block_storage_pdl_read_size) }
 .match_program_size 0x4784 : { *(.text.mtb_block_storage_pdl_program_size) }
 .match_erase_size 0x4788 : { *(.text.mtb_block_storage_pdl_erase_size) }
 .match_erase_value 0x478c : { *(.text.mtb_block_storage_pdl_erase_value) }
 .match_is_in_range 0x4790 : { *(.text.mtb_block_storage_pdl_is_in_range) }
 .match_is_erase_required 0x47aa : { *(.text.mtb_block_storage_pdl_is_erase_required) }
 .match_erase 0x47b0 : { *(.text.mtb_block_storage_pdl_erase) }
 .match_program 0x4810 : { *(.text.mtb_block_storage_pdl_program) }
 .match_read 0x4860 : { *(.text.mtb_block_storage_pdl_read) }
 .match_create 0x486c : { *(.text.mtb_block_storage_create_pdl) }
 .wrapper 0x100000 : { *(.text.touch_application_eeprom_init) }
 .factory : { *(.rodata.touch_factory_eeprom_configuration) }
 .match_EraseRow 0x7f08 : { *(.text.EraseRow) }
 .match_WriteRowWrap 0x8554 : { *(.text.WriteRowWrap) }
 .match_WriteSimpleMode 0x85d4 : { *(.text.WriteSimpleMode) }
 .match_CopyHeadersData 0x8680 : { *(.text.CopyHeadersData) }
 .match_WriteExtendedMode 0x8808 : { *(.text.WriteExtendedMode) }
 .match_EraseRowWrap 0x890c : { *(.text.EraseRowWrap) }
 .match_Cy_Em_EEPROM_Write 0x8aac : { *(.text.Cy_Em_EEPROM_Write) }
 .match_Cy_Em_EEPROM_Erase 0x8ae0 : { *(.text.Cy_Em_EEPROM_Erase) }
 /DISCARD/ : { *(*) }
}
touch_eeprom_init_bd = 0x898d;
touch_eeprom_init = 0x8a39;
touch_provider_init = 0x486d;
touch_provider_read_size = 0x4781;
touch_provider_program_size = 0x4785;
touch_provider_erase_size = 0x4789;
touch_provider_erase_value = 0x478d;
touch_provider_in_range = 0x4791;
touch_storage_copy = 0x4861;
touch_storage_program = 0x4811;
touch_storage_zero = 0x47b1;
touch_storage_no_erase = 0x47ab;
