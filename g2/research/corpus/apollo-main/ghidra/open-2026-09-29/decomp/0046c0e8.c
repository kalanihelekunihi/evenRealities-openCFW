
longlong SVC_Settings_AutoBrightnessClose(void)

{
  int iVar1;
  uint unaff_r5;
  
  iVar1 = productModeGet();
  if (iVar1 != 1) {
    iVar1 = FUN_0045a568();
    if (iVar1 == 1) {
      HUB_Close(4);
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        unaff_r5 = 0x19a;
        FUN_0043d574(4,PTR_s_service_settings_0046c664,DAT_0046c660,DAT_0046c6dc,0x19a,DAT_0046c6d8)
        ;
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_0046c6e0,DAT_0046c6e0);
      }
    }
  }
  return (ulonglong)unaff_r5 << 0x20;
}

