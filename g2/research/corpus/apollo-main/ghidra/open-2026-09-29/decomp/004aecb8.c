
undefined4 _kvdbUpdataAlsScale(void)

{
  int iVar1;
  char acStack_10 [8];
  short sStack_8;
  
  iVar1 = SVC_KvdbBlobRead(PTR_s_kvAlsScale_004aedfc,acStack_10,0xc);
  if (0 < iVar1) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,PTR_s_kv_als_scale_004aee0c,DAT_004aee08,PTR_s__kvdbUpdataAlsScale_004aee04,
                   0x20,PTR_s_version__d__d__004aee00,acStack_10[0],1);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10800000,PTR_s__kv_als_scale_version__d__d__004aee10,
                          PTR_s__kv_als_scale_version__d__d__004aee10,acStack_10[0],1);
    }
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,PTR_s_kv_als_scale_004aee0c,DAT_004aee08,PTR_s__kvdbUpdataAlsScale_004aee04,
                   0x21,PTR_s_crc_0x_x_0x_x__004aee14,sStack_8,*(undefined2 *)(DAT_004aedf8 + 8));
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10800000,PTR_s__kv_als_scale_crc_0x_x_0x_x__004aee18,
                          PTR_s__kv_als_scale_crc_0x_x_0x_x__004aee18,sStack_8,
                          *(undefined2 *)(DAT_004aedf8 + 8));
    }
    if ((sStack_8 != *(short *)(DAT_004aedf8 + 8)) && (acStack_10[0] == '\0')) {
      SVC_KvdbWriteAlsScale();
    }
    return 0;
  }
  SVC_KvdbWriteAlsScale(DAT_004aedf8);
  return 0;
}

