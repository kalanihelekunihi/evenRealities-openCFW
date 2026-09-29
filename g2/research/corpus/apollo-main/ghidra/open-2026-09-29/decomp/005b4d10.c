
undefined8 FUN_005b4d10(undefined4 param_1,int param_2,undefined4 param_3)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    param_3 = 0xb6;
    FUN_0043d574(3,DAT_005b52d8,DAT_005b52d4,PTR_s_conversate_action_app_resume_005b5658,0xb6,
                 PTR_s_conversate_app_resume_005b5654);
  }
  iVar1 = FUN_0043d0ce();
  if (-1 < iVar1 << 0x1f) {
    iVar1 = FUN_0043d0ce();
    if (-1 < iVar1 << 0x1d) goto LAB_005b4d56;
  }
  compress_log_output(0xc000000,PTR_s__conversate_conversate_app_resum_005b565c);
LAB_005b4d56:
  if (param_2 == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      param_3 = 0xb9;
      FUN_0043d574(1,DAT_005b52d8,DAT_005b52d4,PTR_s_conversate_action_app_resume_005b5658,0xb9,
                   DAT_005b5418);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_005b5420,DAT_005b5420);
    }
    uVar2 = 0xffffffff;
  }
  else {
    if (*(char *)(param_2 + 5) == '\0') {
      AUDM_appRelease(4);
    }
    else {
      AUDM_appAcquire(4);
    }
    uVar2 = 0;
  }
  return CONCAT44(param_3,uVar2);
}

