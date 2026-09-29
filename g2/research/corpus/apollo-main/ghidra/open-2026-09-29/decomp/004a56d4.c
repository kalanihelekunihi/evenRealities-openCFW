
void DRV_IMUDataParserCallback(byte *param_1)

{
  int *piVar1;
  short *psVar2;
  char *pcVar3;
  char *pcVar4;
  int *piVar5;
  int iVar6;
  uint uVar7;
  int local_40;
  int local_3c;
  int local_38;
  int local_34;
  int local_30;
  int local_2c;
  int local_28;
  int local_24;
  int local_20;
  
  piVar1 = DAT_004a60e4;
  uVar7 = DAT_004a60e4[2];
  if (uVar7 < 0x14) {
    DAT_004a60e4[uVar7 * 0x1c + 3] =
         (*(uint *)(DAT_004a5ed8 + (uint)*DAT_004a5ee0 * 0x10 + 4) / 1000) *
         (uVar7 - DAT_004a60e4[1]) + *DAT_004a60e4;
    if ((int)((uint)*param_1 << 0x1f) < 0) {
      FUN_0043c0e4(&local_28,0xc,0);
      *(byte *)(piVar1 + uVar7 * 0x1c + 4) = *(byte *)(piVar1 + uVar7 * 0x1c + 4) | 1;
      *(undefined2 *)((int)piVar1 + uVar7 * 0x70 + 0x12) = *(undefined2 *)(param_1 + 6);
      *(undefined2 *)(piVar1 + uVar7 * 0x1c + 5) = *(undefined2 *)(param_1 + 8);
      *(undefined2 *)((int)piVar1 + uVar7 * 0x70 + 0x16) = *(undefined2 *)(param_1 + 10);
      local_28 = *(short *)(param_1 + 6) * 8 - *DAT_004a6368;
      local_24 = *(short *)(param_1 + 8) * 8 - DAT_004a6368[1];
      local_20 = *(short *)(param_1 + 10) * 8 - DAT_004a6368[2];
      semantic_fixed_vector_to_float(&local_28,piVar1 + uVar7 * 0x1c + 0xd,0x10,3);
    }
    psVar2 = DAT_004a636c;
    if ((((*param_1 & 0x30) == 0x30) &&
        (iVar6 = FUN_00507c94(DAT_004a6370,param_1 + 0x1a,param_1 + 0x23,DAT_004a636c), iVar6 != -1)
        ) && (*(char *)((int)psVar2 + 0x4d) != '\0')) {
      if ((char)psVar2[0x23] != '\0') {
        *DAT_004a6374 = 1;
        pcVar3 = DAT_004a6378;
        *DAT_004a6378 = (char)psVar2[0x22];
        pcVar4 = DAT_004a637c;
        *DAT_004a637c = *(char *)((int)psVar2 + 0x45);
        piVar5 = DAT_004a6380;
        *DAT_004a6380 = *(int *)(psVar2 + 0x1c);
        piVar5[1] = *(int *)(psVar2 + 0x1e);
        piVar5[2] = *(int *)(psVar2 + 0x20);
        *(char *)(piVar1 + uVar7 * 0x1c + 0x1e) = (char)psVar2[0x22];
        *(undefined1 *)((int)piVar1 + uVar7 * 0x70 + 0x79) = *(undefined1 *)((int)psVar2 + 0x45);
        if (*pcVar3 != '\0') {
          *DAT_004a5d2c = 1;
        }
        if (*pcVar4 != '\0') {
          *DAT_004a5d2c = 0;
        }
      }
      if ((char)psVar2[0x1b] != '\0') {
        FUN_0043c0e4(&local_34,0xc,0);
        *(byte *)(piVar1 + uVar7 * 0x1c + 4) = *(byte *)(piVar1 + uVar7 * 0x1c + 4) | 8;
        *(short *)((int)piVar1 + uVar7 * 0x70 + 0x1e) = psVar2[0x18];
        *(short *)(piVar1 + uVar7 * 0x1c + 8) = psVar2[0x19];
        *(short *)((int)piVar1 + uVar7 * 0x70 + 0x22) = psVar2[0x1a];
        local_34 = psVar2[0x18] * 0x1333 - *DAT_004a6380;
        local_30 = psVar2[0x19] * 0x1333 - DAT_004a6380[1];
        local_2c = psVar2[0x1a] * 0x1333 - DAT_004a6380[2];
        semantic_fixed_vector_to_float(&local_34,piVar1 + uVar7 * 0x1c + 0x13,0x10,3);
      }
      if ((char)psVar2[4] != '\0') {
        *(byte *)(piVar1 + uVar7 * 0x1c + 4) = *(byte *)(piVar1 + uVar7 * 0x1c + 4) | 0x20;
        piVar1[uVar7 * 0x1c + 9] = (int)*psVar2 << 0x10;
        piVar1[uVar7 * 0x1c + 10] = (int)psVar2[1] << 0x10;
        piVar1[uVar7 * 0x1c + 0xb] = (int)psVar2[2] << 0x10;
        piVar1[uVar7 * 0x1c + 0xc] = (int)psVar2[3] << 0x10;
      }
      if (((char)psVar2[9] != '\0') && ((char)psVar2[0xb] != '\0')) {
        *(byte *)(piVar1 + uVar7 * 0x1c + 4) = *(byte *)(piVar1 + uVar7 * 0x1c + 4) | 0x20;
        piVar1[uVar7 * 0x1c + 9] = (int)psVar2[5] << 0x10;
        piVar1[uVar7 * 0x1c + 10] = (int)psVar2[6] << 0x10;
        piVar1[uVar7 * 0x1c + 0xb] = (int)psVar2[7] << 0x10;
        piVar1[uVar7 * 0x1c + 0xc] = (int)psVar2[8] << 0x10;
      }
      if (((char)psVar2[0x10] != '\0') && ((char)psVar2[0x12] != '\0')) {
        *(byte *)(piVar1 + uVar7 * 0x1c + 4) = *(byte *)(piVar1 + uVar7 * 0x1c + 4) | 0x20;
        piVar1[uVar7 * 0x1c + 9] = (int)psVar2[0xc] << 0x10;
        piVar1[uVar7 * 0x1c + 10] = (int)psVar2[0xd] << 0x10;
        piVar1[uVar7 * 0x1c + 0xb] = (int)psVar2[0xe] << 0x10;
        piVar1[uVar7 * 0x1c + 0xc] = (int)psVar2[0xf] << 0x10;
      }
      if ((*(byte *)(piVar1 + uVar7 * 0x1c + 4) & 0x3f) >> 5 != 0) {
        semantic_fixed_vector_to_float
                  (piVar1 + uVar7 * 0x1c + 9,piVar1 + uVar7 * 0x1c + 0x16,0x1e,4);
        semantic_quaternion_to_euler(piVar1 + uVar7 * 0x1c + 0x16,piVar1 + uVar7 * 0x1c + 0x1a);
        iVar6 = piVar1[uVar7 * 0x1c + 0x1a];
        piVar1[uVar7 * 0x1c + 0x1a] = piVar1[uVar7 * 0x1c + 0x1b];
        piVar1[uVar7 * 0x1c + 0x1b] = (int)((float)piVar1[uVar7 * 0x1c + 0x1c] * -1.0);
        piVar1[uVar7 * 0x1c + 0x1c] = iVar6;
      }
      piVar5 = DAT_004a6570;
      if ((char)psVar2[0x16] != '\0') {
        *DAT_004a6570 = (int)psVar2[0x13] << 4;
        piVar5[1] = (int)psVar2[0x14] << 4;
        piVar5[2] = (int)psVar2[0x15] << 4;
      }
      FUN_0043c0e4(psVar2,0x50,0);
    }
    if ((int)((uint)*param_1 << 0x1e) < 0) {
      FUN_0043c0e4(&local_40,0xc,0);
      *(byte *)(piVar1 + uVar7 * 0x1c + 4) = *(byte *)(piVar1 + uVar7 * 0x1c + 4) | 2;
      *(undefined2 *)(piVar1 + uVar7 * 0x1c + 6) = *(undefined2 *)(param_1 + 0xc);
      *(undefined2 *)((int)piVar1 + uVar7 * 0x70 + 0x1a) = *(undefined2 *)(param_1 + 0xe);
      *(undefined2 *)(piVar1 + uVar7 * 0x1c + 7) = *(undefined2 *)(param_1 + 0x10);
      local_40 = *(short *)(param_1 + 0xc) * 4000 - *DAT_004a6570;
      local_3c = *(short *)(param_1 + 0xe) * 4000 - DAT_004a6570[1];
      local_38 = *(short *)(param_1 + 0x10) * 4000 - DAT_004a6570[2];
      semantic_fixed_vector_to_float(&local_40,piVar1 + uVar7 * 0x1c + 0x10,0x10,3);
    }
    piVar1[2] = piVar1[2] + 1;
    if (0x13 < (uint)piVar1[2]) {
      piVar1[2] = 0;
    }
  }
  else {
    iVar6 = FUN_0043d0ce();
    if (iVar6 << 0x1e < 0) {
      local_3c = DAT_004a625c;
      local_40 = 0x51c;
      FUN_0043d574(1,DAT_004a6268,DAT_004a6264,DAT_004a6260);
    }
    iVar6 = FUN_0043d0ce();
    if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_004a626c,DAT_004a626c);
    }
  }
  return;
}

