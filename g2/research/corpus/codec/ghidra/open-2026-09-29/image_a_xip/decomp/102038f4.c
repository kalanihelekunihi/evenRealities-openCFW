
undefined4
gx8002_dma_configure(undefined4 param_1,undefined4 param_2,int param_3,int param_4,uint *param_5)

{
  int *piVar1;
  uint uVar2;
  undefined4 uVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  undefined4 uStack_44;
  undefined4 uStack_40;
  uint uStack_38;
  
  piVar1 = DAT_10203a48;
  uVar2 = param_5[6] << 0xb | param_5[1] << 0xe | 0x18000001 | *param_5 * 2 | *param_5 << 4;
  if (param_5[7] != 0) {
    if (param_5[7] != 1) {
      return 0xffffffff;
    }
    uVar2 = uVar2 | 0x100;
  }
  if (param_5[2] != 0) {
    if (param_5[2] != 1) {
      return 0xffffffff;
    }
    uVar2 = uVar2 | 0x400;
  }
  uVar4 = param_5[9];
  if (uVar4 != 0) {
    if (uVar4 == 1) {
      uVar2 = uVar2 | 0x800000;
    }
    else if (uVar4 == 2) {
      uVar2 = uVar2 | 0x1000000;
    }
    else {
      if (uVar4 != 3) {
        return 0xffffffff;
      }
      uVar2 = uVar2 | 0x1800000;
    }
  }
  uVar4 = param_5[4];
  if (uVar4 != 0) {
    if (uVar4 == 1) {
      uVar2 = uVar2 | 0x2000000;
    }
    else if (uVar4 == 2) {
      uVar2 = uVar2 | 0x4000000;
    }
    else {
      if (uVar4 != 3) {
        return 0xffffffff;
      }
      uVar2 = uVar2 | 0x6000000;
    }
  }
  uVar2 = param_5[0xb] << 0x14 | uVar2;
  uVar4 = 0;
  if (param_5[10] != 0) {
    if (param_5[10] != 1) {
      return 0xffffffff;
    }
    uVar4 = 0x400;
  }
  if (param_5[5] != 0) {
    if (param_5[5] != 1) {
      return 0xffffffff;
    }
    uVar4 = uVar4 | 0x800;
  }
  uVar6 = param_5[8];
  uVar5 = param_5[3];
  gx8002_dma_clear(param_4);
  iVar7 = param_4 * 0x58;
  iVar8 = *piVar1;
  uStack_44 = virt_to_dma(param_2);
  *(undefined4 *)(iVar7 + iVar8) = uStack_44;
  iVar9 = *piVar1;
  uStack_40 = virt_to_dma(param_1);
  iVar8 = *piVar1 + iVar7;
  *(undefined4 *)(iVar9 + iVar7 + 8) = uStack_40;
  *(uint *)(iVar8 + 0x18) = uVar2;
  *(uint *)(iVar8 + 0x40) = uVar4;
  *(uint *)(iVar8 + 0x44) = uVar6 << 0xb | uVar5 << 7 | 2;
  iVar8 = (uint)(param_3 != (param_3 / 0xfff) * 0xfff) + param_3 / 0xfff;
  if (0x1a0 < (uint)(iVar8 * 0x18)) {
    return 0xffffffff;
  }
  uStack_38 = uVar2;
  gx8002_dma_descriptors
            (&uStack_44,piVar1[param_4 + 0xda],iVar8,param_3,1 << (*param_5 & 0x3f) & 0xff);
  iVar8 = *piVar1;
  uVar3 = virt_to_dma(piVar1[param_4 + 0xda]);
  *(undefined4 *)(iVar7 + iVar8 + 0x10) = uVar3;
  return 0;
}

