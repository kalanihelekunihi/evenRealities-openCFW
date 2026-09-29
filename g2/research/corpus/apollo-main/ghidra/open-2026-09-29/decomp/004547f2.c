
int FUN_004547f2(undefined4 param_1)

{
  int iVar1;
  int iVar2;
  
  iVar1 = FUN_00454770(param_1);
  iVar2 = FUN_0044f718(iVar1 + 1);
  if (iVar2 == 0) {
    iVar2 = 0;
  }
  else {
    FUN_00454738(iVar2,param_1,iVar1);
    *(undefined1 *)(iVar2 + iVar1) = 0;
  }
  return iVar2;
}

