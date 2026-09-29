
longlong FUN_004ed9b6(undefined4 param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  int *piVar2;
  int iVar3;
  
  piVar1 = DAT_004ee6fc;
  if (*DAT_004ee6f8 == 0) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      param_2 = 0x104;
      FUN_0043d574(2,DAT_004edaa8,DAT_004edaa4,DAT_004edab4,0x104,DAT_004edab0,param_4);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_004edab8,DAT_004edab8);
    }
  }
  else {
    if (*(int *)(DAT_004ee700 + *DAT_004ee6fc * 8 + 4) != 0) {
      FUN_0044d878(*(undefined4 *)(DAT_004ee700 + *DAT_004ee6fc * 8 + 4));
    }
    FUN_004edac4(*piVar1);
    piVar2 = DAT_004edac0;
    piVar1 = DAT_004eda88;
    if ((*DAT_004edabc == 1) && (*DAT_004edac0 != 0)) {
      if ((*DAT_004eda88 != 0) || (iVar3 = FUN_0043e2ea(*DAT_004eda88), iVar3 != 0)) {
        FUN_00450500(*piVar1,DAT_004eda90);
      }
      *DAT_004eda78 = 0;
      *DAT_004eda84 = 0;
      *DAT_004eda8c = 0;
      FUN_0044d878(*piVar2);
      FUN_004eef7c(*piVar2);
    }
  }
  return (ulonglong)param_2 << 0x20;
}

