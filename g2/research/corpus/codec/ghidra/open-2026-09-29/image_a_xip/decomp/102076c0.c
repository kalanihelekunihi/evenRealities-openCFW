
undefined4 gx8002_register_suspend(int *param_1)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  
  iVar1 = iRam10207714;
  iVar4 = 0;
  iVar3 = 8;
  do {
    if (*(int *)(iVar4 * 8 + iRam10207714 + 0x10) == *param_1) {
      func_0x10025738(iRam10207714 + (iVar4 + 2) * 8,param_1,8);
      goto LAB_102076e4;
    }
    iVar4 = iVar4 + 1;
    iVar3 = iVar3 + -1;
  } while (iVar3 != 0);
  if ((*(uint *)(iRam10207714 + 8) < 8) && (*param_1 != 0)) {
    func_0x10025738(iRam10207714 + (*(uint *)(iRam10207714 + 8) + 2) * 8,param_1,8);
    *(int *)(iVar1 + 8) = *(int *)(iVar1 + 8) + 1;
LAB_102076e4:
    uVar2 = 0;
  }
  else {
    uVar2 = 0xffffffff;
  }
  return uVar2;
}

