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
 /DISCARD/ : { *(*) }
}
