
longlong SVC_Settings_SaveSettingConfigToKV(void)

{
  int iVar1;
  uint unaff_r5;
  
  if (*(short *)(*(int *)(DAT_0046c694 + 4) + 0x18) != *(short *)(DAT_0046c6a8 + 0x18)) {
    SVC_KvdbWriteSetting();
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      unaff_r5 = 0x163;
      FUN_0043d574(3,PTR_s_service_settings_0046c664,DAT_0046c660,DAT_0046c6b0,0x163,DAT_0046c6ac);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0xc000000,DAT_0046c6b4,DAT_0046c6b4);
    }
    SVC_Settings_DumpSettingConfig();
  }
  return (ulonglong)unaff_r5 << 0x20;
}

