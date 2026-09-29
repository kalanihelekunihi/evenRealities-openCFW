
undefined4 FUN_005d7782(int param_1,int param_2)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  
  uVar1 = 4;
  iVar2 = param_1;
  if (param_1 < 0) {
    iVar2 = -param_1;
  }
  iVar3 = param_2;
  if (param_2 < 0) {
    iVar3 = -param_2;
  }
  if (iVar3 * 0xc < iVar2) {
    if (param_1 < 0) {
      uVar1 = 0xfffffffe;
    }
    else {
      uVar1 = 2;
    }
  }
  else if (iVar2 * 0xc < iVar3) {
    if (param_2 < 0) {
      uVar1 = 1;
    }
    else {
      uVar1 = 0xffffffff;
    }
  }
  return uVar1;
}

