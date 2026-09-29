
undefined8 SVC_Settings_InputEventCheck(void)

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
          unaff_r5 = 0x2a;
          FUN_0043d574(2,DAT_0046bb74,DAT_0046bb70,DAT_0046bae8,0x2a,DAT_0046bb7c);
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0x8000000,DAT_0046bb80,DAT_0046bb80);
        }
        uVar2 = 0;
      }
      else {
        iVar1 = FUN_004acad0();
        if (iVar1 == 1) {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            unaff_r5 = 0x30;
            FUN_0043d574(2,DAT_0046bb74,DAT_0046bb70,DAT_0046bae8,0x30,DAT_0046bb84);
          }
          iVar1 = FUN_0043d0ce();
          if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
            compress_log_output(0x8000000,DAT_0046bb88,DAT_0046bb88);
          }
          uVar2 = 0;
        }
        else {
          iVar1 = settings_get_config();
          if (*(char *)(iVar1 + 0x15) == '\x01') {
            iVar1 = FUN_0043d0ce();
            if (iVar1 << 0x1e < 0) {
              unaff_r5 = 0x36;
              FUN_0043d574(2,DAT_0046bb74,DAT_0046bb70,DAT_0046bae8,0x36,DAT_0046bb8c);
            }
            iVar1 = FUN_0043d0ce();
            if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
              compress_log_output(0x8000000,PTR_s__service_settings_silent_mode__i_0046be6c,
                                  PTR_s__service_settings_silent_mode__i_0046be6c);
            }
            uVar2 = 0;
          }
          else {
            uVar2 = 1;
          }
        }
      }
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        unaff_r5 = 0x24;
        FUN_0043d574(2,DAT_0046bb74,DAT_0046bb70,DAT_0046bae8,0x24,DAT_0046bae4);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x8000000,DAT_0046bb78,DAT_0046bb78);
      }
      uVar2 = 0;
    }
  }
  return CONCAT44(unaff_r5,uVar2);
}

