
undefined4 _kvdbUpdataTimeFormat(void)

{
  int iVar1;
  char acStack_10 [8];
  short sStack_8;
  
  iVar1 = SVC_KvdbBlobRead(PTR_s_kvTimeFormat_0049afe8,acStack_10,0xc);
  if (0 < iVar1) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,PTR_s_kv_tz_0049aff8,DAT_0049aff4,PTR_s__kvdbUpdataTimeFormat_0049aff0,0x23,
                   PTR_s_version__d__d__0049afec,acStack_10[0],1);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10800000,PTR_s__kv_tz_version__d__d__0049affc,
                          PTR_s__kv_tz_version__d__d__0049affc,acStack_10[0],1);
    }
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,PTR_s_kv_tz_0049aff8,DAT_0049aff4,PTR_s__kvdbUpdataTimeFormat_0049aff0,0x24,
                   PTR_s_crc_0x_x_0x_x__0049b000,sStack_8,*(undefined2 *)(DAT_0049afe4 + 8));
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10800000,PTR_s__kv_tz_crc_0x_x_0x_x__0049b004,
                          PTR_s__kv_tz_crc_0x_x_0x_x__0049b004,sStack_8,
                          *(undefined2 *)(DAT_0049afe4 + 8));
    }
    if ((sStack_8 != *(short *)(DAT_0049afe4 + 8)) && (acStack_10[0] == '\0')) {
      SVC_KvdbWriteTimeFormat();
    }
    return 0;
  }
  SVC_KvdbWriteTimeFormat(DAT_0049afe4);
  return 0;
}

