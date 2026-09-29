
undefined4 FUN_005909b6(int param_1)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint *puVar4;
  
  iVar1 = DAT_00590d34;
  iVar2 = *(int *)(param_1 + 4);
  iVar3 = *(int *)(DAT_00590d34 + iVar2 * 0x1000 + 0x4c);
  if (iVar3 << 0xc < 0) {
    puVar4 = (uint *)(DAT_00590d34 + iVar2 * 0x1000 + 0x4c);
    *puVar4 = *puVar4 & 0xfff7ffff;
  }
  if (iVar3 << 0xe < 0) {
    puVar4 = (uint *)(iVar1 + iVar2 * 0x1000 + 0x4c);
    *puVar4 = *puVar4 & 0xfffdffff;
  }
  if (iVar3 << 0xd < 0) {
    puVar4 = (uint *)(iVar1 + iVar2 * 0x1000 + 0x4c);
    *puVar4 = *puVar4 & 0xfffbffff;
  }
  if (iVar3 << 0xf < 0) {
    puVar4 = (uint *)(iVar1 + iVar2 * 0x1000 + 0x4c);
    *puVar4 = *puVar4 & 0xfffeffff;
  }
  return 0;
}

