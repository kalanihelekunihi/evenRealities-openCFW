
undefined4
PB_RxOnboardingEvent(undefined4 param_1,byte *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 local_20;
  undefined4 local_1c;
  uint local_18;
  undefined4 local_14;
  undefined4 uStack_c;
  
  uStack_c = param_4;
  if (param_2 == (byte *)0x0) {
    FUN_00439c04(&local_20,DAT_004a8538,0x14);
    local_1c = CONCAT22(local_1c._2_2_,1);
    APP_errorFaultHandler(&local_20);
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      local_1c = DAT_004a84e8;
      local_20 = 0xf2;
      FUN_0043d574(1,DAT_004a8540,DAT_004a84d4,DAT_004a853c);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_004a84f0);
    }
    uVar2 = 2;
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      local_14 = *(undefined4 *)(param_2 + 4);
      local_18 = (uint)*param_2;
      local_1c = DAT_004a8544;
      local_20 = 0xf6;
      FUN_0043d574(4,DAT_004a8540,DAT_004a84d4,DAT_004a853c);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      local_20 = *(undefined4 *)(param_2 + 4);
      compress_log_output(0x10800000,DAT_004a8548,DAT_004a8548,*param_2);
    }
    onboarding_common_data_handler(3,param_2,0xc);
    uVar2 = 0;
  }
  return uVar2;
}

