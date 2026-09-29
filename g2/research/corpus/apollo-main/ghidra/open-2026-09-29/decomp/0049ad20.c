
undefined4 _kvdbUpdataUniversalSetting(void)

{
  int iVar1;
  byte local_18 [18];
  short local_6;
  
  iVar1 = SVC_KvdbBlobRead(PTR_s_kvUniversalSetting_0049ae64,local_18,0x14);
  if (0 < iVar1) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,PTR_s_kvdb_universal_setting_0049ae74,DAT_0049ae70,
                   PTR_s__kvdbUpdataUniversalSetting_0049ae6c,0x26,PTR_s_version__d__d__0049ae68,
                   local_18[0],3);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10800000,PTR_s__kvdb_universal_setting_version___0049ae78,
                          PTR_s__kvdb_universal_setting_version___0049ae78,local_18[0],3);
    }
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,PTR_s_kvdb_universal_setting_0049ae74,DAT_0049ae70,
                   PTR_s__kvdbUpdataUniversalSetting_0049ae6c,0x27,PTR_s_crc_0x_x_0x_x__0049ae7c,
                   local_6,*(undefined2 *)(DAT_0049ae60 + 0x12));
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10800000,PTR_s__kvdb_universal_setting_crc_0x_x_0049ae80,
                          PTR_s__kvdb_universal_setting_crc_0x_x_0049ae80,local_6,
                          *(undefined2 *)(DAT_0049ae60 + 0x12));
    }
    if ((local_6 != *(short *)(DAT_0049ae60 + 0x12)) && (local_18[0] < 3)) {
      SVC_KvdbWriteUniversalSetting();
    }
    return 0;
  }
  SVC_KvdbWriteUniversalSetting(DAT_0049ae60);
  return 0;
}

