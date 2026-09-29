
undefined4 lfs_alloc_lookahead(int param_1,int param_2)

{
  uint uVar1;
  
  uVar1 = *(int *)(param_1 + 0x6c) + (param_2 - *(int *)(param_1 + 0x54));
  uVar1 = uVar1 - *(uint *)(param_1 + 0x6c) * (uVar1 / *(uint *)(param_1 + 0x6c));
  if (uVar1 < *(uint *)(param_1 + 0x58)) {
    *(byte *)(*(int *)(param_1 + 100) + (uVar1 >> 3)) =
         *(byte *)(*(int *)(param_1 + 100) + (uVar1 >> 3)) | (byte)(1 << (uVar1 & 7));
  }
  return 0;
}

