
undefined4 FUN_004f2210(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  int *piVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  
  piVar2 = DAT_004f2bb0;
  piVar1 = DAT_004f2b98;
  if (*DAT_004f2bb0 != 0) {
    iVar5 = *DAT_004f2b98;
    iVar3 = FUN_0043fdda(*DAT_004f2bb0);
    iVar4 = 0;
    if (0 < *DAT_004f2b94 - *piVar1) {
      iVar4 = -(((iVar5 - iVar3) * param_1) / (*DAT_004f2b94 - *piVar1));
      if (iVar4 < 0) {
        iVar4 = 0;
      }
      if (iVar5 - iVar3 < iVar4) {
        iVar4 = iVar5 - iVar3;
      }
    }
    FUN_0043f142(*piVar2,iVar4);
  }
  return param_4;
}

