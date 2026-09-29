
undefined8 FUN_005e4b68(int param_1,int param_2,int param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  int iStack_20;
  int iStack_1c;
  undefined4 uStack_18;
  
  iStack_20 = param_2;
  iStack_1c = param_3;
  uStack_18 = param_4;
  FUN_0043c0e4(&iStack_20,8,0);
  if (param_1 == 0) {
    iVar1 = 0;
  }
  else {
    FUN_0044e75e(param_1,&iStack_20);
    iVar2 = iStack_1c;
    iVar1 = FUN_0044e4bc(param_1);
    iVar1 = iVar1 + iVar2;
    if (100 < param_3) {
      param_2 = param_2 << 1;
    }
    if (param_2 < 1) {
      if (param_2 < 0) {
        iVar2 = ((param_2 + iVar2) / 0x1c) * 0x1c;
      }
    }
    else {
      iVar2 = ((param_2 + iVar2 + 0x1b) / 0x1c) * 0x1c;
    }
    if (iVar1 < 1) {
      iVar1 = 0;
    }
    else if (iVar2 < 0) {
      iVar1 = 0;
    }
    else if (iVar2 <= iVar1) {
      iVar1 = iVar2;
    }
  }
  return CONCAT44(iStack_20,iVar1);
}

