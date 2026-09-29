
undefined8 SVC_Settings_AppLaunchCheck(void)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 unaff_r5;
  
  iVar1 = productModeGet();
  if (iVar1 == 1) {
    uVar2 = 1;
  }
  else {
    iVar1 = semantic_OtaTransferActive();
    if (iVar1 == 0) {
      iVar1 = settings_get_config();
      if (*(char *)(iVar1 + 0x15) == '\x01') {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          unaff_r5 = 0x66;
          FUN_0043d574(2,DAT_0046bb74,DAT_0046bb70,DAT_0046bbac,0x66,DAT_0046be0c);
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0x8000000,DAT_0046c000,DAT_0046c000);
        }
        uVar2 = 0;
      }
      else {
        uVar2 = 1;
      }
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        unaff_r5 = 0x60;
        FUN_0043d574(2,DAT_0046bb74,DAT_0046bb70,DAT_0046bbac,0x60,DAT_0046bba8);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x8000000,DAT_0046bbb0,DAT_0046bbb0);
      }
      uVar2 = 0;
    }
  }
  return CONCAT44(unaff_r5,uVar2);
}

