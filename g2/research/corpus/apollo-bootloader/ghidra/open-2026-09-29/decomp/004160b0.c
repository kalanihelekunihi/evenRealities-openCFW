
undefined4 FUN_004160b0(void)

{
  int *piVar1;
  int iVar2;
  undefined4 uVar3;
  
  iVar2 = FUN_0041602a();
  if (iVar2 == 0) {
    iVar2 = FUN_00418b56();
    piVar1 = DAT_0041658c;
    if ((iVar2 == 1) && (*DAT_0041658c == 1)) {
      FUN_00416028();
      *piVar1 = 2;
      FUN_00418148();
      return 0;
    }
    uVar3 = 0xffffffff;
  }
  else {
    uVar3 = 0xfffffffa;
  }
  return uVar3;
}

