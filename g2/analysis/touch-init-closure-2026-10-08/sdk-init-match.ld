mtb_block_storage_cat2_create = 0x486d;
__aeabi_uidiv = 0xa6c1; __aeabi_uidivmod = 0xa7cd; memset = 0xa9d5;
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
 /DISCARD/ : { *(*) }
}
