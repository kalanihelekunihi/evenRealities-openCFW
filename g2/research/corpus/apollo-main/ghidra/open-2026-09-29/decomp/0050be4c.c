
void FUN_0050be4c(int *param_1)

{
  int *piVar1;
  int *piVar2;
  int iVar3;
  int iVar4;
  uint local_20;
  undefined4 local_1c;
  undefined1 auStack_18 [12];
  
  *DAT_0050c960 = 0;
  *DAT_0050c964 = 0;
  iVar4 = *param_1;
  if ((iVar4 == 0) || (iVar3 = FUN_0043e2ea(iVar4), piVar1 = DAT_0050c520, iVar3 == 0)) {
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      local_1c = DAT_0050c968;
      local_20 = 0x7a2;
      FUN_0043d574(2,DAT_0050c2fc,DAT_0050c2f8,DAT_0050c96c);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_0050c970,DAT_0050c970);
    }
    *DAT_0050c27c = 0;
  }
  else if (*DAT_0050c520 == 0) {
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      local_1c = DAT_0050c974;
      local_20 = 0x7a9;
      FUN_0043d574(2,DAT_0050c2fc,DAT_0050c2f8,DAT_0050c96c);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_0050c978);
    }
    *DAT_0050c27c = 0;
  }
  else {
    for (iVar3 = 0; iVar3 < 4; iVar3 = iVar3 + 1) {
      if (*(int *)(iVar3 * 0x30 + DAT_0050bf98 + 4) == iVar4) {
        FUN_0050b5f4(iVar3 * 0x30 + DAT_0050bf98);
        break;
      }
    }
    *DAT_0050c27c = 0;
    piVar2 = DAT_0050c524;
    if (((*piVar1 == 1) && (*DAT_0050c524 != 0)) &&
       (iVar4 = ui_common_api_fn_00509dfa(*DAT_0050c524), iVar4 == 0)) {
      FUN_0043c0e4(auStack_18,10,0);
      FUN_0043c0e4(auStack_18,10,0);
      ui_common_api_fn_00509e14(*piVar2,auStack_18,7);
      iVar4 = ui_onboarding_main_sub_004A979C(auStack_18,0,&local_20);
      if (iVar4 == 0) {
        FUN_0050a670(local_20 & 0xff,local_1c);
      }
    }
  }
  return;
}

