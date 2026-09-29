
undefined4 FUN_0049ebb6(char param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  if (param_1 == '\x02') {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(3,DAT_0049efbc,DAT_0049efb8,DAT_0049efcc,99,DAT_0049efc8,param_3,param_4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0xc000000,DAT_0049efd0,DAT_0049efd0);
    }
    FUN_004ac16c(2);
    iVar1 = SVC_Settings_InputEventCheck();
    if (iVar1 == 1) {
      iVar1 = FUN_0049ead8();
      if (iVar1 == 1) {
        DRV_BuzzerPlay(3);
      }
      FUN_00474100();
    }
    iVar1 = FUN_0045a568();
    if (iVar1 == 1) {
      onboarding_check_start_disp(0);
    }
    iVar1 = FUN_0049ead8();
    if (iVar1 == 1) {
      onboarding_notify_wear_status_to_app(1);
    }
    goto LAB_0049ecfa;
  }
  if (param_1 != '\x01') {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(2,DAT_0049efbc,DAT_0049efb8,DAT_0049efcc,0x7f,DAT_0049efdc,param_1);
    }
    iVar1 = FUN_0043d0ce();
    if (-1 < iVar1 << 0x1f) {
      iVar1 = FUN_0043d0ce();
      if (-1 < iVar1 << 0x1d) goto LAB_0049ecfa;
    }
    compress_log_output(0x8400000,DAT_0049efe0,DAT_0049efe0,param_1);
    goto LAB_0049ecfa;
  }
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(3,DAT_0049efbc,DAT_0049efb8,DAT_0049efcc,0x76,DAT_0049efd4);
  }
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1f < 0) {
LAB_0049ec7e:
    compress_log_output(0xc000000,DAT_0049efd8);
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1d < 0) goto LAB_0049ec7e;
  }
  iVar1 = FUN_0049ead8();
  if (iVar1 == 1) {
    FUN_0047432c();
    onboarding_notify_wear_status_to_app(0);
  }
  else {
    iVar1 = SVC_Settings_InputEventCheck();
    if (iVar1 == 1) {
      FUN_00474100();
    }
  }
LAB_0049ecfa:
  FUN_0047243a();
  return 0;
}

