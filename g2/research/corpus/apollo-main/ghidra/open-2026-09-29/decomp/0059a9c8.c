
void FUN_0059a9c8(int param_1,int param_2,int param_3)

{
  uint uVar1;
  uint uVar2;
  
  uVar1 = *(uint *)(param_1 + 8) >> 10;
  uVar2 = *(ushort *)(param_2 + param_3 * 4) * uVar1 + *(int *)(param_1 + 4);
  uVar1 = *(ushort *)(param_2 + param_3 * 4 + 2) * uVar1;
  *(uint *)(param_1 + 8) = uVar1;
  *(uint *)(param_1 + 0x10) = *(uint *)(param_1 + 0x10) | uVar2 >> 0x18;
  *(uint *)(param_1 + 4) = uVar2 & 0xffffff;
  if (uVar1 < 0x10000) {
    FUN_00439b54();
    return;
  }
  return;
}

