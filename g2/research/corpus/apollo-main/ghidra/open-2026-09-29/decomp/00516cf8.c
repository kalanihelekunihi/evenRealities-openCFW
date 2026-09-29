
undefined4 FUN_00516cf8(int param_1)

{
  bool bVar1;
  undefined4 *puVar2;
  int iVar3;
  undefined4 uVar4;
  uint uVar5;
  uint uVar6;
  
  iVar3 = *DAT_00517850;
  bVar1 = false;
  if (*(char *)(iVar3 + 0x7c) == '\0') {
    if (*(int *)(iVar3 + 0x110) == 1) {
      FUN_00517e18(*(undefined4 *)(param_1 + 0xc),*(undefined4 *)(param_1 + 0x10),
                   *(undefined4 *)(param_1 + 0x1c),*(undefined4 *)(param_1 + 0x20),
                   *(undefined4 *)(param_1 + 0x24),*(undefined4 *)(param_1 + 0x28),
                   *(undefined4 *)(param_1 + 0x14),*(undefined4 *)(param_1 + 0x18));
      return 0;
    }
    bVar1 = true;
  }
  if (*(char *)(iVar3 + 0x2e4) != '\0') {
    FUN_00517e18(*(undefined4 *)(param_1 + 0xc),*(undefined4 *)(param_1 + 0x10),
                 *(undefined4 *)(param_1 + 0x1c),*(undefined4 *)(param_1 + 0x20),
                 *(undefined4 *)(param_1 + 0x24),*(undefined4 *)(param_1 + 0x28),
                 *(undefined4 *)(param_1 + 0x14),*(undefined4 *)(param_1 + 0x18));
    return 0;
  }
  uVar5 = 7;
  if (bVar1) {
    uVar5 = 9;
  }
  uVar6 = 0;
  if (*(int *)(iVar3 + 0x88) != 0) {
    if ((*(int *)(iVar3 + 0x114) == 0) || (bVar1)) {
      uVar6 = 0x7800000;
    }
    else {
      uVar6 = 0x4000000;
    }
  }
  uVar6 = uVar6 & *(uint *)(iVar3 + 0x8c);
  if (*(char *)(*DAT_005171ec + 8) == '\x01') {
    uVar6 = uVar6 | *(uint *)(*DAT_005171ec + 0xc) & 0xc0000000;
  }
  puVar2 = (undefined4 *)FUN_00514aec(9);
  if (puVar2 != (undefined4 *)0x0) {
    *puVar2 = 800;
    uVar4 = *(undefined4 *)(param_1 + 0xc);
    puVar2[2] = 0x324;
    puVar2[1] = uVar4;
    uVar4 = *(undefined4 *)(param_1 + 0x10);
    puVar2[4] = 0x330;
    puVar2[3] = uVar4;
    uVar4 = *(undefined4 *)(param_1 + 0x1c);
    puVar2[6] = 0x334;
    puVar2[5] = uVar4;
    uVar4 = *(undefined4 *)(param_1 + 0x20);
    puVar2[8] = 0x340;
    puVar2[7] = uVar4;
    uVar4 = *(undefined4 *)(param_1 + 0x24);
    puVar2[10] = 0x344;
    puVar2[9] = uVar4;
    uVar4 = *(undefined4 *)(param_1 + 0x28);
    puVar2[0xc] = 0x350;
    puVar2[0xb] = uVar4;
    uVar4 = *(undefined4 *)(param_1 + 0x14);
    puVar2[0xe] = 0x354;
    puVar2[0xd] = uVar4;
    uVar4 = DAT_005171f0;
    puVar2[0xf] = *(undefined4 *)(param_1 + 0x18);
    puVar2[0x10] = uVar4;
    puVar2[0x11] = uVar5 | uVar6;
  }
  return 0;
}

