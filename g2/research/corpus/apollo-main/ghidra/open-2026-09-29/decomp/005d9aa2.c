
int FUN_005d9aa2(int param_1)

{
  uint uVar1;
  int iVar2;
  uint uVar3;
  
  uVar1 = *(uint *)(param_1 + 0x10);
  uVar3 = *(uint *)(param_1 + 0xc);
  if (uVar3 < uVar1) {
    iVar2 = (uVar1 - uVar3) + -1;
  }
  else {
    iVar2 = uVar1 + ((*(int *)(param_1 + 8) + -1) - uVar3);
  }
  return iVar2;
}

