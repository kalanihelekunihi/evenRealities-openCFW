
undefined4 FUN_0043e33e(undefined4 param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  iVar4 = *(int *)(param_2 + 4);
  if (iVar4 != 0) {
    iVar1 = FUN_0044e586(iVar4);
    iVar2 = FUN_0044e4aa(iVar4);
    iVar3 = FUN_0043dd86(iVar4,0);
    *(int *)(param_2 + 0x18) = (iVar3 + *(int *)(iVar4 + 0x18)) - iVar2;
    *(int *)(param_2 + 0x20) = *(int *)(param_2 + 0x18) + -1;
    iVar2 = FUN_0043dd90(iVar4,0);
    *(int *)(param_2 + 0x14) = (iVar2 + *(int *)(iVar4 + 0x14)) - iVar1;
    *(int *)(param_2 + 0x1c) = *(int *)(param_2 + 0x14) + -1;
  }
  *(undefined4 *)(param_2 + 0x24) = 2;
  *(uint *)(param_2 + 0x24) = *(uint *)(param_2 + 0x24) | 0x1000;
  if (iVar4 != 0) {
    *(uint *)(param_2 + 0x24) = *(uint *)(param_2 + 0x24) | 0x2000;
    *(uint *)(param_2 + 0x24) = *(uint *)(param_2 + 0x24) | 0x300;
  }
  *(uint *)(param_2 + 0x24) = *(uint *)(param_2 + 0x24) | 4;
  *(uint *)(param_2 + 0x24) = *(uint *)(param_2 + 0x24) | 0x10;
  *(uint *)(param_2 + 0x24) = *(uint *)(param_2 + 0x24) | 0x20;
  *(uint *)(param_2 + 0x24) = *(uint *)(param_2 + 0x24) | 0x40;
  *(uint *)(param_2 + 0x24) = *(uint *)(param_2 + 0x24) | 0x800;
  if (iVar4 != 0) {
    *(uint *)(param_2 + 0x24) = *(uint *)(param_2 + 0x24) | 0x8000;
  }
  return param_4;
}

