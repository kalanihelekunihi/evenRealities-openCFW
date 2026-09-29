
uint FUN_004cd6e4(int param_1,uint *param_2)

{
  uint uVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  
  uVar3 = *param_2;
  uVar4 = *(int *)(*(int *)(param_1 + 0x68) + 0x1c) - 8;
  if (uVar3 / uVar4 == 0) {
    uVar1 = 0;
  }
  else {
    iVar2 = lfs_popc(uVar3 / uVar4 - 1);
    uVar1 = ((iVar2 + 2) * -4 + uVar3) / uVar4;
    iVar2 = lfs_popc(uVar1);
    *param_2 = iVar2 * -4 + (uVar3 - uVar1 * uVar4);
  }
  return uVar1;
}

