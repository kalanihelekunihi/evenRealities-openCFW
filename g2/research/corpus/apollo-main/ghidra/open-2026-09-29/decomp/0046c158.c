
longlong settings_configure_auto_brightness(int param_1)

{
  int iVar1;
  uint unaff_r7;
  
  iVar1 = DAT_0046c6a8;
  if (param_1 == 1) {
    *(undefined1 *)(DAT_0046c6a8 + 2) = 1;
    iVar1 = FUN_00443484();
    if (iVar1 == 1) {
      SVC_Settings_AutoBrightnessOpen();
    }
  }
  else {
    *(undefined1 *)(DAT_0046c6a8 + 2) = 0;
    *(undefined4 *)(iVar1 + 4) = 0;
    SVC_Settings_AutoBrightnessClose();
  }
  return (ulonglong)unaff_r7 << 0x20;
}

