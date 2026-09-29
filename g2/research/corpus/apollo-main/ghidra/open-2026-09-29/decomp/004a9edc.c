
undefined8
ui_onboarding_main_sub_004A9EDC
          (undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  byte *pbVar2;
  undefined4 uVar3;
  int iVar4;
  
  pbVar2 = DAT_004a9f68;
  uVar3 = osKernelGetTickCount();
  *(undefined4 *)(pbVar2 + 4) = uVar3;
  bVar1 = *pbVar2;
  if (bVar1 == 0) {
    ui_onboarding_main_sub_004AA048();
  }
  else if (bVar1 == 2) {
    ui_onboarding_main_sub_004AA270(pbVar2[1]);
  }
  else if (bVar1 < 2) {
    ui_onboarding_main_sub_004AA0C8();
  }
  else if (bVar1 != 4) {
    if (bVar1 < 4) {
      ui_onboarding_main_sub_004AAA4C();
    }
    else {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        param_1 = 0x87a;
        param_2 = DAT_004aaaa0;
        FUN_0043d574(2,DAT_004aab68,DAT_004aab64,DAT_004aaaa4,0x87a,DAT_004aaaa0,*pbVar2,param_4);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x8400000,DAT_004aab6c,DAT_004aab6c,*pbVar2);
      }
    }
  }
  return CONCAT44(param_2,param_1);
}

