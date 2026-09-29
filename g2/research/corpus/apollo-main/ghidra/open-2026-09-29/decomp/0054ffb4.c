
int FUN_0054ffb4(int param_1,undefined4 param_2,int param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  
  if (param_1 == 0) {
    iVar2 = param_1;
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      iVar2 = 0x1c5;
      param_2 = DAT_0055094c;
      FUN_0043d574(2,DAT_00550958,DAT_00550954,DAT_00550950,0x1c5,DAT_0055094c,0,param_4);
      param_3 = param_1;
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8400000,DAT_0055095c,DAT_0055095c,0,iVar2,param_2,param_3);
    }
  }
  else {
    for (iVar2 = 0; iVar2 < 10; iVar2 = iVar2 + 1) {
      if ((*(char *)(iVar2 * 0xc + DAT_00550948 + 10) != '\0') &&
         (*(int *)(iVar2 * 0xc + DAT_00550948 + 4) == param_1)) {
        return DAT_00550948 + iVar2 * 0xc;
      }
    }
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(2,DAT_00550958,DAT_00550954,DAT_00550950,0x1ce,DAT_00550960,param_1);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x8400000,DAT_00550bf0,DAT_00550bf0,param_1);
    }
  }
  return 0;
}

