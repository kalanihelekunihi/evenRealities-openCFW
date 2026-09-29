
undefined4 FUN_005908a0(int param_1,int param_2)

{
  int iVar1;
  uint *puVar2;
  undefined4 uVar3;
  int iVar4;
  
  iVar1 = DAT_00590d34;
  iVar4 = *(int *)(param_1 + 4);
  if (*(int *)(DAT_00590d34 + iVar4 * 0x1000 + 0x218) << 0x1d < 0) {
    FUN_00590cf4(param_1,1);
  }
  if (*(int *)(iVar1 + iVar4 * 0x1000 + 0x20c) << 0x1d < 0) {
    FUN_00590cf4(param_1,0);
  }
  if ((param_2 << 0x1b < 0) && (*(int *)(param_1 + 0x40) != -1)) {
    puVar2 = (uint *)(iVar1 + iVar4 * 0x1000 + 0x20c);
    *puVar2 = *puVar2 & 0xfffffffd;
    if (*(int *)(iVar1 + iVar4 * 0x1000 + 0x21c) << 0x1f < 0) {
      return 9;
    }
    if (*(int *)(param_1 + 0x4c) == *(int *)(param_1 + 0x40)) {
      uVar3 = *(undefined4 *)(param_1 + 0x3c);
    }
    else {
      uVar3 = *(undefined4 *)(param_1 + 0x40);
    }
    *(undefined4 *)(param_1 + 0x4c) = uVar3;
    *(undefined4 *)(iVar1 + iVar4 * 0x1000 + 0x224) = uVar3;
    *(uint *)(iVar1 + iVar4 * 0x1000 + 0x220) = *(uint *)(param_1 + 0x54) >> 2;
    *(uint *)(iVar1 + iVar4 * 0x1000 + 0x21c) = *(uint *)(iVar1 + iVar4 * 0x1000 + 0x21c) | 1;
  }
  if ((param_2 << 0x1c < 0) && (*(int *)(param_1 + 0x48) != -1)) {
    puVar2 = (uint *)(iVar1 + iVar4 * 0x1000 + 0x218);
    *puVar2 = *puVar2 & 0xfffffffd;
    if (*(int *)(iVar1 + iVar4 * 0x1000 + 0x21c) << 0x1e < 0) {
      return 9;
    }
    if (*(int *)(param_1 + 0x50) == *(int *)(param_1 + 0x48)) {
      uVar3 = *(undefined4 *)(param_1 + 0x44);
    }
    else {
      uVar3 = *(undefined4 *)(param_1 + 0x48);
    }
    *(undefined4 *)(param_1 + 0x50) = uVar3;
    *(undefined4 *)(iVar1 + iVar4 * 0x1000 + 0x22c) = uVar3;
    *(uint *)(iVar1 + iVar4 * 0x1000 + 0x228) = *(uint *)(param_1 + 0x58) >> 2;
    *(uint *)(iVar1 + iVar4 * 0x1000 + 0x21c) = *(uint *)(iVar1 + iVar4 * 0x1000 + 0x21c) | 2;
  }
  if (param_2 << 0x1f < 0) {
    FUN_005909b6(param_1);
  }
  return 0;
}

