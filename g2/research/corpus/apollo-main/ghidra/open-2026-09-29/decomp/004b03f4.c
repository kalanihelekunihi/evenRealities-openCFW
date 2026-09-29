
undefined4 _kvdbUpdataTerminalMode(void)

{
  int iVar1;
  char local_8 [2];
  short local_6;
  
  iVar1 = SVC_KvdbBlobRead(PTR_s_kvTerminalMode_004b0534,local_8,4);
  if (0 < iVar1) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,PTR_s_kv_terminal_mode_004b0544,DAT_004b0540,
                   PTR_s__kvdbUpdataTerminalMode_004b053c,0x1e,PTR_s_version__d__d__004b0538,
                   local_8[0],1);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10800000,PTR_s__kv_terminal_mode_version__d__d__004b0548,
                          PTR_s__kv_terminal_mode_version__d__d__004b0548,local_8[0],1);
    }
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,PTR_s_kv_terminal_mode_004b0544,DAT_004b0540,
                   PTR_s__kvdbUpdataTerminalMode_004b053c,0x1f,PTR_s_crc_0x_x_0x_x__004b054c,local_6
                   ,*(undefined2 *)(DAT_004b0530 + 2));
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10800000,PTR_s__kv_terminal_mode_crc_0x_x_0x_x__004b0550,
                          PTR_s__kv_terminal_mode_crc_0x_x_0x_x__004b0550,local_6,
                          *(undefined2 *)(DAT_004b0530 + 2));
    }
    if ((local_6 != *(short *)(DAT_004b0530 + 2)) && (local_8[0] == '\0')) {
      SVC_KvdbWriteTerminalMode();
    }
    return 0;
  }
  SVC_KvdbWriteTerminalMode(DAT_004b0530);
  return 0;
}

