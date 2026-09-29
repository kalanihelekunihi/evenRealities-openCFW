
int FUN_00516e0c(uint *param_1)

{
  byte bVar1;
  undefined4 uVar2;
  int *piVar3;
  int iVar4;
  undefined4 *puVar5;
  int iVar6;
  int iVar7;
  byte bVar8;
  uint uVar9;
  uint uVar10;
  undefined4 uVar11;
  undefined4 uVar12;
  int iVar13;
  int iVar14;
  undefined8 uVar15;
  char local_7c;
  char local_7b;
  char local_7a;
  undefined4 local_70;
  undefined4 local_6c;
  undefined4 local_68;
  undefined4 local_64;
  undefined4 local_60;
  undefined4 local_5c;
  undefined4 local_58;
  undefined4 local_54;
  undefined8 local_40;
  
  piVar3 = DAT_00517850;
  iVar4 = *DAT_00517850;
  iVar14 = (int)(((float)param_1[0x10] + (float)param_1[0x12]) * 0.5);
  iVar13 = (int)(((float)param_1[0x11] + (float)param_1[0x13]) * 0.5);
  iVar7 = iVar14 << 0x10;
  iVar6 = iVar13 << 0x10;
  *(int *)(iVar4 + 0x2c8) = iVar14;
  *(int *)(iVar4 + 0x2cc) = iVar13;
  *(int *)(iVar4 + 0x2d0) = iVar7;
  *(int *)(iVar4 + 0x2d4) = iVar6;
  puVar5 = (undefined4 *)FUN_00514aec(2);
  if (puVar5 != (undefined4 *)0x0) {
    *puVar5 = 0x10c;
    puVar5[1] = iVar7;
    puVar5[2] = 0x128;
    puVar5[3] = iVar6;
  }
  FUN_0048949c(&local_7c,0x48);
  uVar2 = DAT_005171f0;
  local_7c = '\x01';
  local_7b = '\x01';
  local_7a = '\x01';
  uVar10 = 0;
LAB_00516f82:
  while( true ) {
    do {
      if (*param_1 <= uVar10) {
        if (local_7b == '\x01') {
          uVar15 = CONCAT44(DAT_005171f4,DAT_005171f4);
          if (local_7c == '\0') {
            uVar15 = local_40;
          }
          uVar11 = *(undefined4 *)(*piVar3 + 0x2d4);
          uVar12 = *(undefined4 *)(*piVar3 + 0x2d0);
          puVar5 = (undefined4 *)FUN_00514aec(7);
          if (puVar5 != (undefined4 *)0x0) {
            uVar10 = *(uint *)(*piVar3 + 0x8c) & 0x7800000;
            if (*(char *)(*DAT_00517858 + 8) == '\x01') {
              uVar10 = uVar10 | *(uint *)(*DAT_00517858 + 0xc) & 0xc0000000;
            }
            *puVar5 = 800;
            puVar5[2] = 0x324;
            puVar5[1] = local_68;
            puVar5[3] = local_64;
            puVar5[4] = 0x330;
            puVar5[5] = (int)uVar15;
            puVar5[6] = 0x334;
            puVar5[7] = (int)((ulonglong)uVar15 >> 0x20);
            puVar5[8] = 0x140;
            puVar5[9] = uVar12;
            puVar5[10] = 0x144;
            puVar5[0xb] = uVar11;
            puVar5[0xc] = uVar2;
            puVar5[0xd] = uVar10 | 4;
          }
        }
        return 0;
      }
      bVar1 = *(byte *)(param_1[2] + uVar10);
      uVar10 = uVar10 + 1;
      iVar4 = FUN_005156b8(param_1,bVar1,&local_7c);
      uVar12 = local_6c;
      uVar11 = local_70;
      bVar8 = bVar1 & 0x6f;
      if (iVar4 != 0) goto LAB_00517130;
    } while (local_7a != '\0');
    if (bVar8 != 6 && bVar8 != 8) break;
    iVar4 = *piVar3;
    uVar11 = *(undefined4 *)(iVar4 + 0x2d4);
    uVar12 = *(undefined4 *)(iVar4 + 0x2d0);
    if (*(int *)(iVar4 + 0x88) == 0) {
      uVar9 = 0;
    }
    else {
      uVar9 = 0x7800000;
    }
    if (*(char *)(*DAT_00517858 + 8) == '\x01') {
      uVar9 = uVar9 | *(uint *)(*DAT_00517858 + 0xc) & 0xc0000000;
    }
    puVar5 = (undefined4 *)FUN_00514aec(0x10);
    if (puVar5 != (undefined4 *)0x0) {
      *puVar5 = 0x328;
      puVar5[2] = 0x32c;
      puVar5[1] = local_70;
      puVar5[4] = 800;
      puVar5[3] = local_6c;
      puVar5[6] = 0x324;
      puVar5[5] = local_70;
      puVar5[8] = 0x330;
      puVar5[7] = local_6c;
      puVar5[10] = 0x334;
      puVar5[9] = local_68;
      puVar5[0xc] = 0x140;
      puVar5[0xd] = uVar12;
      puVar5[0xb] = local_64;
      puVar5[0xe] = 0x144;
      puVar5[0xf] = uVar11;
      puVar5[0x10] = uVar2;
      puVar5[0x11] = uVar9 | 4;
      puVar5[0x12] = 0x330;
      puVar5[0x14] = 0x334;
      puVar5[0x13] = local_60;
      puVar5[0x16] = 0x340;
      puVar5[0x15] = local_5c;
      puVar5[0x18] = 0x344;
      puVar5[0x17] = local_58;
      puVar5[0x1a] = 0x350;
      puVar5[0x19] = local_54;
      puVar5[0x1c] = 0x354;
      puVar5[0x1b] = local_68;
      puVar5[0x1e] = uVar2;
      puVar5[0x1d] = local_64;
      puVar5[0x1f] = uVar9 | 7;
    }
  }
  if (bVar8 != 2) {
    if ((bVar8 == 5) || (bVar8 == 7)) {
      iVar4 = *piVar3;
      uVar11 = *(undefined4 *)(iVar4 + 0x2d4);
      uVar12 = *(undefined4 *)(iVar4 + 0x2d0);
      if (*(int *)(iVar4 + 0x88) == 0) {
        uVar9 = 0;
      }
      else {
        uVar9 = 0x7800000;
      }
      if (*(char *)(*DAT_00517858 + 8) == '\x01') {
        uVar9 = uVar9 | *(uint *)(*DAT_00517858 + 0xc) & 0xc0000000;
      }
      puVar5 = (undefined4 *)FUN_00514aec(0xe);
      if (puVar5 != (undefined4 *)0x0) {
        *puVar5 = 0x328;
        puVar5[2] = 0x32c;
        puVar5[1] = local_70;
        puVar5[4] = 800;
        puVar5[3] = local_6c;
        puVar5[6] = 0x324;
        puVar5[5] = local_70;
        puVar5[8] = 0x330;
        puVar5[7] = local_6c;
        puVar5[10] = 0x334;
        puVar5[9] = local_68;
        puVar5[0xc] = 0x140;
        puVar5[0xd] = uVar12;
        puVar5[0xb] = local_64;
        puVar5[0xe] = 0x144;
        puVar5[0xf] = uVar11;
        puVar5[0x10] = uVar2;
        puVar5[0x11] = uVar9 | 4;
        puVar5[0x12] = 0x330;
        puVar5[0x14] = 0x334;
        puVar5[0x13] = local_60;
        puVar5[0x16] = 0x340;
        puVar5[0x15] = local_5c;
        puVar5[0x18] = 0x344;
        puVar5[0x17] = local_68;
        puVar5[0x1a] = uVar2;
        puVar5[0x19] = local_64;
        puVar5[0x1b] = uVar9 | 6;
      }
      goto LAB_00516f82;
    }
    if ((bVar1 & 0xf) == 9) {
      puVar5 = (undefined4 *)FUN_00514aec(2);
      if (puVar5 != (undefined4 *)0x0) {
        *puVar5 = 0x328;
        puVar5[1] = uVar11;
        puVar5[2] = 0x32c;
        puVar5[3] = uVar12;
      }
      iVar4 = FUN_0051a8ec(param_1,&local_7c);
      if (iVar4 != 0) {
LAB_00517130:
        iVar6 = *piVar3;
        *(undefined4 *)(iVar6 + 0x114) = 0;
        *(undefined4 *)(iVar6 + 0x118) = 0;
        FUN_0051565c(iVar4);
        return iVar4;
      }
    }
    else if (bVar8 == 10 || bVar8 == 0xb) goto LAB_00516f82;
  }
  uVar11 = *(undefined4 *)(*piVar3 + 0x2d4);
  uVar12 = *(undefined4 *)(*piVar3 + 0x2d0);
  puVar5 = (undefined4 *)FUN_00514aec(7);
  if (puVar5 != (undefined4 *)0x0) {
    uVar9 = *(uint *)(*piVar3 + 0x8c) & 0x7800000;
    if (*(char *)(*DAT_00517858 + 8) == '\x01') {
      uVar9 = *(uint *)(*DAT_00517858 + 0xc) & 0xc0000000 | uVar9;
    }
    *puVar5 = 800;
    puVar5[2] = 0x324;
    puVar5[1] = local_70;
    puVar5[4] = 0x330;
    puVar5[3] = local_6c;
    puVar5[6] = 0x334;
    puVar5[5] = local_68;
    puVar5[8] = 0x140;
    puVar5[9] = uVar12;
    puVar5[7] = local_64;
    puVar5[10] = 0x144;
    puVar5[0xb] = uVar11;
    puVar5[0xc] = uVar2;
    puVar5[0xd] = uVar9 | 4;
  }
  goto LAB_00516f82;
}

