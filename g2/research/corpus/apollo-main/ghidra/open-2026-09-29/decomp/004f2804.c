
int FUN_004f2804(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  iVar4 = DAT_004f3254;
  if ((param_1 < 0) || (*DAT_004f3250 <= param_1)) {
    iVar1 = 0;
  }
  else {
    iVar1 = *(int *)(DAT_004f3254 + param_1 * 4);
    if (iVar1 == 0) {
      iVar1 = 0;
    }
    else {
      iVar2 = FUN_0043fce0(iVar1);
      iVar1 = FUN_0043fdda(iVar1);
      if (param_1 == 0) {
        iVar1 = 0;
      }
      else {
        iVar1 = iVar2 - (0x120 - iVar1) / 2;
        if ((0 < param_1) && (iVar4 = *(int *)(iVar4 + param_1 * 4 + -4), iVar4 != 0)) {
          iVar3 = FUN_0043fce0(iVar4);
          iVar4 = FUN_0043fdda(iVar4);
          iVar4 = iVar4 + iVar3 + -0x1e;
          if (iVar1 < iVar4) {
            iVar1 = iVar4;
          }
        }
      }
      if (iVar1 < 0) {
        iVar1 = 0;
      }
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        FUN_0043d574(4,DAT_004f2eb4,DAT_004f2eb0,DAT_004f325c,0x599,DAT_004f3258,param_1,iVar2,iVar1
                     ,param_4);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x10c00000,DAT_004f3364,DAT_004f3364,param_1,iVar2,iVar1);
      }
    }
  }
  return iVar1;
}

