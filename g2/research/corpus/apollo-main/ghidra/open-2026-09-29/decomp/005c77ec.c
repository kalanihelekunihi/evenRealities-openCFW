
undefined4 FUN_005c77ec(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  uint uVar2;
  
  if ((int)((uint)*(byte *)(param_1 + 0x4d) << 0x1f) < 0) {
    FUN_005c173e(param_1,*(undefined4 *)(DAT_005c7894 + (uint)*(byte *)(param_1 + 0x4c) * 4));
  }
  else {
    iVar1 = FUN_0044f718(*(int *)(param_1 + 0x38) << 1);
    FUN_00454738(iVar1,*(undefined4 *)(DAT_005c7894 + (uint)*(byte *)(param_1 + 0x4c) * 4),
                 *(int *)(param_1 + 0x38) << 1);
    for (uVar2 = 0; uVar2 < *(uint *)(param_1 + 0x38); uVar2 = uVar2 + 1) {
      *(ushort *)(iVar1 + uVar2 * 2) = *(ushort *)(iVar1 + uVar2 * 2) & 0xfbff;
    }
    FUN_005c173e(param_1,iVar1);
    FUN_0044f758(iVar1);
  }
  return param_4;
}

