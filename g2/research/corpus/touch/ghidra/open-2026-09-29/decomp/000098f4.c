
undefined4 Cy_SCB_I2C_Init(uint *param_1,byte *param_2,byte *param_3)

{
  byte bVar1;
  int iVar2;
  uint uVar3;
  byte bVar4;
  uint uVar5;
  undefined4 uVar6;
  
  uVar6 = DAT_00009ad4;
  if (((param_1 != (uint *)0x0) && (param_2 != (byte *)0x0)) && (param_3 != (byte *)0x0)) {
    if (2 < (byte)(*param_2 - 1)) {
      software_bkpt(1);
    }
    if ((param_2[1] != 0) && (param_2[5] != 0)) {
      software_bkpt(1);
    }
    if ((char)param_2[3] < '\0') {
      software_bkpt(1);
    }
    if ((int)((uint)param_2[4] << 0x1f) < 0) {
      software_bkpt(1);
    }
    if (0x10 < *(uint *)(param_2 + 0x10)) {
      software_bkpt(1);
    }
    if (0x10 < *(uint *)(param_2 + 0xc)) {
      software_bkpt(1);
    }
    bVar1 = *param_2;
    if (param_2[5] == 0) {
      uVar3 = 0;
    }
    else {
      uVar3 = 0x10000;
    }
    if (param_2[8] == 0) {
      uVar5 = 0;
    }
    else {
      uVar5 = 0x100;
    }
    *param_1 = uVar3 | uVar5;
    if (param_2[6] == 0) {
      uVar3 = 0x800;
    }
    else {
      uVar3 = 0;
    }
    param_1[0x18] =
         *(int *)(param_2 + 0x10) - 1U & 0xf | uVar3 | (*(int *)(param_2 + 0xc) + -1) * 0x10 & 0xffU
         | (uint)*param_2 << 0x1e;
    *param_1 = *param_1 & DAT_00009aac;
    if (bVar1 == 2) {
      bVar4 = 0;
    }
    else if (param_2[7] == 0) {
      bVar4 = 0;
    }
    else {
      bVar4 = 1;
    }
    if (param_2[7] == 0) {
      uVar3 = 0;
    }
    else {
      uVar3 = 0x80000000;
    }
    param_1[0x20] = uVar3;
    if ((*param_2 == 1) || (param_2[9] == 0)) {
      param_1[0xc0] = 0x107;
      uVar3 = DAT_00009ab8;
    }
    else {
      param_1[0xc0] = DAT_00009ab0;
      uVar3 = DAT_00009ab4;
    }
    param_1[0x1c] = uVar3;
    if (param_2[1] == 0) {
      uVar3 = 0;
    }
    else {
      uVar3 = 0xf;
    }
    param_1[0xc1] = uVar3;
    param_1[0xc4] = (param_2[3] & 0x7f) << 1 | (uint)param_2[4] << 0x10;
    param_1[0x80] = 0x107;
    if (param_2[2] == 0) {
      uVar3 = 1;
    }
    else {
      uVar3 = 8;
    }
    param_1[0x81] = uVar3;
    *(undefined4 *)((int)param_1 + DAT_00009abc) = 0;
    *(undefined4 *)((int)param_1 + DAT_00009ac0) = 0;
    *(undefined4 *)((int)param_1 + DAT_00009ac4) = 0;
    *(undefined4 *)((int)param_1 + DAT_00009ac8) = 0;
    *(undefined4 *)((int)param_1 + DAT_00009acc) = 0;
    iVar2 = DAT_00009ad0;
    if (bVar1 == 2) {
      uVar6 = 0;
    }
    else {
      uVar6 = 0x1d1;
    }
    *(undefined4 *)((int)param_1 + DAT_00009ad0) = uVar6;
    if (param_2[7] == 0) {
      uVar3 = 0;
    }
    else if (bVar1 == 2) {
      uVar3 = 0;
    }
    else {
      uVar3 = 0x3000000;
    }
    *(uint *)((int)param_1 + DAT_00009ad0) = *(uint *)((int)param_1 + iVar2) | uVar3;
    *param_3 = param_2[1];
    param_3[1] = param_2[2];
    *(undefined2 *)(param_3 + 0x50) = *(undefined2 *)(param_2 + 0x14);
    param_3[2] = bVar4;
    param_3[4] = 0;
    param_3[5] = 0;
    param_3[6] = 0;
    param_3[7] = 0x10;
    param_3[8] = 0;
    param_3[9] = 0;
    param_3[10] = 0;
    param_3[0xb] = 0;
    param_3[0x18] = 0;
    param_3[0x19] = 0;
    param_3[0x1a] = 0;
    param_3[0x1b] = 0;
    param_3[0x20] = 0;
    param_3[0x21] = 0;
    param_3[0x22] = 0;
    param_3[0x23] = 0;
    param_3[0x40] = 0;
    param_3[0x41] = 0;
    param_3[0x42] = 0;
    param_3[0x43] = 0;
    param_3[0x3c] = 0;
    param_3[0x3d] = 0;
    param_3[0x3e] = 0;
    param_3[0x3f] = 0;
    param_3[0x30] = 0;
    param_3[0x31] = 0;
    param_3[0x32] = 0;
    param_3[0x33] = 0;
    param_3[0x2c] = 0;
    param_3[0x2d] = 0;
    param_3[0x2e] = 0;
    param_3[0x2f] = 0;
    param_3[0x44] = 0;
    param_3[0x45] = 0;
    param_3[0x46] = 0;
    param_3[0x47] = 0;
    param_3[0x48] = 0;
    param_3[0x49] = 0;
    param_3[0x4a] = 0;
    param_3[0x4b] = 0;
    param_3[0x4c] = 0;
    param_3[0x4d] = 0;
    param_3[0x4e] = 0;
    param_3[0x4f] = 0;
    uVar6 = 0;
  }
  return uVar6;
}

