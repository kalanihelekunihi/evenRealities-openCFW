
undefined4 _kvdbUpdataTemperatureUnit(void)

{
  int iVar1;
  char acStack_10 [8];
  short sStack_8;
  
  iVar1 = SVC_KvdbBlobRead(PTR_s_kvTemperatureUnit_0049b16c,acStack_10,0xc);
  if (0 < iVar1) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,PTR_s_kv_tu_0049b17c,DAT_0049b178,PTR_s__kvdbUpdataTemperatureUnit_0049b174,
                   0x22,PTR_s_version__d__d__0049b170,acStack_10[0],1);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10800000,PTR_s__kv_tu_version__d__d__0049b180,
                          PTR_s__kv_tu_version__d__d__0049b180,acStack_10[0],1);
    }
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,PTR_s_kv_tu_0049b17c,DAT_0049b178,PTR_s__kvdbUpdataTemperatureUnit_0049b174,
                   0x23,PTR_s_crc_0x_x_0x_x__0049b184,sStack_8,*(undefined2 *)(DAT_0049b168 + 8));
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10800000,PTR_s__kv_tu_crc_0x_x_0x_x__0049b188,
                          PTR_s__kv_tu_crc_0x_x_0x_x__0049b188,sStack_8,
                          *(undefined2 *)(DAT_0049b168 + 8));
    }
    if ((sStack_8 != *(short *)(DAT_0049b168 + 8)) && (acStack_10[0] == '\0')) {
      SVC_KvdbWriteTemperatureUnit();
    }
    return 0;
  }
  SVC_KvdbWriteTemperatureUnit(DAT_0049b168);
  return 0;
}

