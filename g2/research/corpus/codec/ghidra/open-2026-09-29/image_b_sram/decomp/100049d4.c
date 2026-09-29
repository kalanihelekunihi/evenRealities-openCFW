
undefined4
gx8002_backup_dma_configure
          (undefined4 param_1,undefined4 param_2,int param_3,uint param_4,uint *param_5)

{
  int *piVar1;
  undefined4 uVar2;
  uint uVar3;
  uint uVar4;
  int iVar5;
  uint uVar6;
  int iVar7;
  int iVar8;
  uint uVar9;
  undefined4 uStack_44;
  undefined4 uStack_40;
  uint uStack_38;
  
  piVar1 = DAT_10004b68;
  uVar9 = param_5[6] << 0xb | param_5[1] << 0xe | 0x18000001 | *param_5 * 2 | *param_5 << 4;
  if (param_5[7] != 0) {
    if (param_5[7] != 1) {
      return 0xffffffff;
    }
    uVar9 = uVar9 | 0x100;
  }
  if (param_5[2] != 0) {
    if (param_5[2] != 1) {
      return 0xffffffff;
    }
    uVar9 = uVar9 | 0x400;
  }
  uVar3 = param_5[9];
  if (uVar3 != 0) {
    if (uVar3 == 1) {
      uVar3 = param_5[4];
      uVar9 = uVar9 | 0x800000;
      goto joined_r0x10004a40;
    }
    if (uVar3 == 2) {
      uVar9 = uVar9 | 0x1000000;
    }
    else {
      if (uVar3 != 3) {
        return 0xffffffff;
      }
      uVar9 = uVar9 | 0x1800000;
    }
  }
  uVar3 = param_5[4];
joined_r0x10004a40:
  if (uVar3 != 0) {
    if (uVar3 == 1) {
      uVar9 = uVar9 | 0x2000000;
    }
    else if (uVar3 == 2) {
      uVar9 = uVar9 | 0x4000000;
    }
    else {
      if (uVar3 != 3) {
        return 0xffffffff;
      }
      uVar9 = uVar9 | 0x6000000;
    }
  }
  uVar9 = param_5[0xb] << 0x14 | uVar9;
  uVar3 = 0;
  if (param_5[10] != 0) {
    if (param_5[10] != 1) {
      return 0xffffffff;
    }
    uVar3 = 0x400;
  }
  if (param_5[5] != 0) {
    if (param_5[5] != 1) {
      return 0xffffffff;
    }
    uVar3 = uVar3 | 0x800;
  }
  uVar6 = param_5[8];
  uVar4 = param_5[3];
  iVar7 = *DAT_10004b68;
  iVar5 = 1 << (param_4 & 0x3f);
  *(int *)(iVar7 + 0x338) = iVar5;
  *(int *)(iVar7 + 0x340) = iVar5;
  iVar8 = param_4 * 0x58;
  *(int *)(iVar7 + 0x348) = iVar5;
  *(int *)(iVar7 + 0x350) = iVar5;
  *(int *)(iVar7 + 0x358) = iVar5;
  uStack_44 = gx8002_dma_bus_address(param_2);
  *(undefined4 *)(iVar8 + iVar7) = uStack_44;
  iVar7 = *piVar1;
  uStack_40 = gx8002_dma_bus_address(param_1);
  iVar5 = *piVar1 + iVar8;
  *(undefined4 *)(iVar7 + iVar8 + 8) = uStack_40;
  *(uint *)(iVar5 + 0x18) = uVar9;
  *(uint *)(iVar5 + 0x40) = uVar3;
  *(uint *)(iVar5 + 0x44) = uVar6 << 0xb | uVar4 << 7 | 2;
  iVar5 = (uint)(param_3 != (param_3 / 0xfff) * 0xfff) + param_3 / 0xfff;
  if (0x1a0 < (uint)(iVar5 * 0x18)) {
    return 0xffffffff;
  }
  uStack_38 = uVar9;
  gx8002_backup_dma_descriptors
            (&uStack_44,piVar1[param_4 + 0xda],iVar5,param_3,1 << (*param_5 & 0x3f) & 0xff);
  iVar5 = *piVar1;
  uVar2 = gx8002_dma_bus_address(piVar1[param_4 + 0xda]);
  *(undefined4 *)(iVar8 + iVar5 + 0x10) = uVar2;
  return 0;
}

