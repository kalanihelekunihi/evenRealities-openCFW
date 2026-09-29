
undefined4 FUN_10005a7c(void)

{
  int *piVar1;
  int iVar2;
  undefined4 uVar3;
  
  piVar1 = DAT_10005aa4;
  if ((*DAT_10005aa4 == 0) && (iVar2 = FUN_10006170(), iVar2 != 0)) {
    iVar2 = FUN_10006184();
    uVar3 = 0;
    if (iVar2 == 3) {
      uVar3 = 1;
      piVar1[1] = 1;
    }
  }
  else {
    uVar3 = 0;
  }
  return uVar3;
}

