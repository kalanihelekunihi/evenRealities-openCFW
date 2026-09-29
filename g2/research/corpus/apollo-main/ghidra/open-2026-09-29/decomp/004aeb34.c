
undefined4 _kvdbUpdataSetting(void)

{
  int iVar1;
  byte abStack_20 [24];
  short sStack_8;
  
  iVar1 = SVC_KvdbBlobRead(PTR_s_kvSetting_004aec78,abStack_20,0x1c);
  if (0 < iVar1) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,PTR_s_kv_tz_004aec88,DAT_004aec84,PTR_s__kvdbUpdataSetting_004aec80,0x31,
                   PTR_s_version__d__d__004aec7c,abStack_20[0],4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10800000,PTR_s__kv_tz_version__d__d__004aec8c,
                          PTR_s__kv_tz_version__d__d__004aec8c,abStack_20[0],4);
    }
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,PTR_s_kv_tz_004aec88,DAT_004aec84,PTR_s__kvdbUpdataSetting_004aec80,0x32,
                   PTR_s_crc_0x_x_0x_x__004aec90,sStack_8,*(undefined2 *)(DAT_004aec74 + 0x18));
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10800000,PTR_s__kv_tz_crc_0x_x_0x_x__004aec94,
                          PTR_s__kv_tz_crc_0x_x_0x_x__004aec94,sStack_8,
                          *(undefined2 *)(DAT_004aec74 + 0x18));
    }
    if ((sStack_8 != *(short *)(DAT_004aec74 + 0x18)) && (abStack_20[0] < 4)) {
      SVC_KvdbWriteSetting();
    }
    return 0;
  }
  SVC_KvdbWriteSetting(DAT_004aec74);
  return 0;
}

