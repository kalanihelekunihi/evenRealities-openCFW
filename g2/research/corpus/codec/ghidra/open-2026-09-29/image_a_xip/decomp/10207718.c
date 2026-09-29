
undefined4 gx8002_register_resume(int *param_1)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  
  iVar1 = iRam1020776c;
  iVar4 = 0;
  iVar3 = 8;
  do {
    if (*(int *)(iVar4 * 8 + iRam1020776c + 0x50) == *param_1) {
      func_0x10025738(iRam1020776c + (iVar4 + 10) * 8,param_1,8);
      goto LAB_1020773c;
    }
    iVar4 = iVar4 + 1;
    iVar3 = iVar3 + -1;
  } while (iVar3 != 0);
  if ((*(uint *)(iRam1020776c + 0xc) < 8) && (*param_1 != 0)) {
    func_0x10025738(iRam1020776c + (*(uint *)(iRam1020776c + 0xc) + 10) * 8,param_1,8);
    *(int *)(iVar1 + 0xc) = *(int *)(iVar1 + 0xc) + 1;
LAB_1020773c:
    uVar2 = 0;
  }
  else {
    uVar2 = 0xffffffff;
  }
  return uVar2;
}

