
undefined8 SVC_Settings_UledCtrlCheck(void)

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
      iVar1 = FUN_0049eb96();
      if (iVar1 == 0) {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          unaff_r5 = 0x4b;
          FUN_0043d574(2,DAT_0046bb74,DAT_0046bb70,DAT_0046bb94,0x4b,DAT_0046bb9c);
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0x8000000,DAT_0046bba0,DAT_0046bba0);
        }
        uVar2 = 0;
      }
      else {
        iVar1 = FUN_004acad0();
        if (iVar1 == 1) {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            unaff_r5 = 0x51;
            FUN_0043d574(2,DAT_0046bb74,DAT_0046bb70,DAT_0046bb94,0x51,DAT_0046bba4);
          }
          iVar1 = FUN_0043d0ce();
          if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
            compress_log_output(0x8000000,DAT_0046bfe4,DAT_0046bfe4);
          }
          uVar2 = 0;
        }
        else {
          uVar2 = 1;
        }
      }
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        unaff_r5 = 0x45;
        FUN_0043d574(2,DAT_0046bb74,DAT_0046bb70,DAT_0046bb94,0x45,DAT_0046bb90);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x8000000,DAT_0046bb98,DAT_0046bb98);
      }
      uVar2 = 0;
    }
  }
  return CONCAT44(unaff_r5,uVar2);
}

