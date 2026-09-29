
int FUN_004397d0(int param_1)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  
  iVar1 = 0;
  for (uVar3 = *(uint *)(param_1 + 4);
      (((iVar2 = iVar1, uVar3 != 0 && (iVar2 = iVar1 + 1, uVar3 >> 1 != 0)) &&
       (iVar2 = iVar1 + 2, uVar3 >> 2 != 0)) && (iVar2 = iVar1 + 3, uVar3 >> 3 != 0));
      uVar3 = uVar3 >> 4) {
    iVar1 = iVar1 + 4;
  }
  return iVar2;
}

