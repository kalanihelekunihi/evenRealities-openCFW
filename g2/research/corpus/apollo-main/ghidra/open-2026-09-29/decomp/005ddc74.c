
void FUN_005ddc74(int *param_1)

{
  uint uVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  
  if (param_1[7] != -1) {
    uVar3 = param_1[7] + 1;
    for (uVar4 = param_1[9]; uVar4 < (uint)param_1[10]; uVar4 = uVar4 + 1) {
      iVar2 = param_1[4] + uVar4 * 0xc;
      uVar5 = (uint)*(byte *)(iVar2 + 0x13) |
              (uint)*(byte *)(iVar2 + 0x11) << 0x10 | (uint)*(byte *)(iVar2 + 0x10) << 0x18 |
              (uint)*(byte *)(iVar2 + 0x12) << 8;
      uVar6 = (uint)*(byte *)(iVar2 + 0x1b) |
              (uint)*(byte *)(iVar2 + 0x19) << 0x10 | (uint)*(byte *)(iVar2 + 0x18) << 0x18 |
              (uint)*(byte *)(iVar2 + 0x1a) << 8;
      if (uVar3 < uVar5) {
        uVar3 = uVar5;
      }
      while( true ) {
        if ((((uint)*(byte *)(iVar2 + 0x17) |
             (uint)*(byte *)(iVar2 + 0x15) << 0x10 | (uint)*(byte *)(iVar2 + 0x14) << 0x18 |
             (uint)*(byte *)(iVar2 + 0x16) << 8) < uVar3) || (uVar5 + (-1 - uVar3) < uVar6))
        goto LAB_005ddcb6;
        uVar1 = (uVar3 + uVar6) - uVar5;
        if (uVar1 != 0) break;
        if (uVar3 == 0xffffffff) goto LAB_005ddc82;
        uVar3 = uVar3 + 1;
      }
      if (uVar1 < *(uint *)(*param_1 + 0x10)) {
        param_1[7] = uVar3;
        param_1[8] = uVar1;
        param_1[9] = uVar4;
        return;
      }
LAB_005ddcb6:
    }
  }
LAB_005ddc82:
  *(undefined1 *)(param_1 + 6) = 0;
  return;
}

