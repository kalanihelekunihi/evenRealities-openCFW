
undefined8 ui_onboarding_main_sub_004A9F84(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  byte bVar1;
  byte *pbVar2;
  undefined4 *puVar3;
  int iVar4;
  
  puVar3 = DAT_004aab70;
  osMutexAcquire(*DAT_004aab70,0xffffffff);
  pbVar2 = DAT_004aa200;
  bVar1 = *DAT_004aa200;
  if (bVar1 == 0) {
    *DAT_004aa200 = 1;
    pbVar2[1] = 0;
  }
  else if (bVar1 == 2) {
    DAT_004aa200[1] = DAT_004aa200[1] + 1;
  }
  else if (bVar1 < 2) {
    *DAT_004aa200 = 2;
    pbVar2[1] = 0;
  }
  else if (bVar1 != 4) {
    if (3 < bVar1) {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        param_2 = 0x8a6;
        param_3 = DAT_004aaaa0;
        FUN_0043d574(2,DAT_004aab68,DAT_004aab64,DAT_004aab74,0x8a6,DAT_004aaaa0,*pbVar2);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x8400000,DAT_004aab6c,DAT_004aab6c,*pbVar2);
      }
      osMutexRelease(*puVar3);
      goto LAB_004a9fbc;
    }
    *DAT_004aa200 = 4;
    pbVar2[1] = 0;
  }
  osMutexRelease(*puVar3);
  ui_onboarding_main_sub_004A9EDC();
LAB_004a9fbc:
  return CONCAT44(param_3,param_2);
}

