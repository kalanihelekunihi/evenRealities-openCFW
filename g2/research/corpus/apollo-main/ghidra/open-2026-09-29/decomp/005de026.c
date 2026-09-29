
void FUN_005de026(int *param_1)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  
  if (param_1[7] != -1) {
    uVar3 = param_1[7] + 1;
    for (uVar4 = param_1[9]; uVar4 < (uint)param_1[10]; uVar4 = uVar4 + 1) {
      iVar1 = param_1[4] + uVar4 * 0xc;
      uVar5 = (uint)*(byte *)(iVar1 + 0x13) |
              (uint)*(byte *)(iVar1 + 0x11) << 0x10 | (uint)*(byte *)(iVar1 + 0x10) << 0x18 |
              (uint)*(byte *)(iVar1 + 0x12) << 8;
      uVar2 = (uint)*(byte *)(iVar1 + 0x1b) |
              (uint)*(byte *)(iVar1 + 0x19) << 0x10 | (uint)*(byte *)(iVar1 + 0x18) << 0x18 |
              (uint)*(byte *)(iVar1 + 0x1a) << 8;
      if (uVar3 < uVar5) {
        uVar3 = uVar5;
      }
      if (((uVar3 <= ((uint)*(byte *)(iVar1 + 0x17) |
                     (uint)*(byte *)(iVar1 + 0x15) << 0x10 | (uint)*(byte *)(iVar1 + 0x14) << 0x18 |
                     (uint)*(byte *)(iVar1 + 0x16) << 8)) && (uVar2 != 0)) &&
         (uVar2 < *(uint *)(*param_1 + 0x10))) {
        param_1[7] = uVar3;
        param_1[8] = uVar2;
        param_1[9] = uVar4;
        return;
      }
    }
  }
  *(undefined1 *)(param_1 + 6) = 0;
  return;
}

