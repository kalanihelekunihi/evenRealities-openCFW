
undefined4 FUN_00564974(float param_1,float param_2,float param_3,float param_4)

{
  bool bVar1;
  int *piVar2;
  bool bVar3;
  int iVar4;
  uint *puVar5;
  int iVar6;
  bool bVar7;
  undefined1 uVar8;
  uint uVar9;
  int iVar10;
  uint uVar11;
  uint uVar12;
  float fVar13;
  float extraout_s1;
  float extraout_s1_00;
  float fVar14;
  float fVar15;
  float extraout_s2;
  float fVar16;
  float extraout_s3;
  float fVar17;
  float fVar18;
  float local_38;
  float local_34;
  undefined4 local_30;
  undefined4 local_2c;
  
  piVar2 = DAT_00564a40;
  bVar3 = false;
  puVar5 = (uint *)*DAT_00564a40;
  fVar13 = (float)puVar5[0xd];
  if ((fVar13 < param_1 || (fVar13 < param_1 || fVar13 < param_2)) ||
     (fVar17 = (float)puVar5[0xc], param_1 < fVar17 || (param_1 < fVar17 || param_2 < fVar17))) {
    bVar3 = true;
  }
  bVar7 = false;
  bVar1 = fVar13 < param_3;
  fVar17 = param_2;
  if (!bVar1) {
    fVar17 = param_4;
  }
  if ((bVar1 || (bVar1 || fVar13 < fVar17)) ||
     (fVar13 = (float)puVar5[0xc], param_3 < fVar13 || (param_3 < fVar13 || fVar17 < fVar13))) {
    bVar7 = true;
  }
  local_38 = 0.0;
  local_34 = 0.0;
  local_30 = 0;
  local_2c = 0;
  if (!bVar7 && !bVar3) {
    if (puVar5[9] == 0x100) {
      uVar9 = puVar5[3];
      if (puVar5[0xb] != 0) {
        puVar5[3] = uVar9 + 1;
        *(undefined4 *)(*piVar2 + 0x24) = 0;
        return 0;
      }
      if (uVar9 < *puVar5) {
        *(undefined1 *)(puVar5[7] + uVar9) = 0;
        *(int *)(*piVar2 + 0xc) = *(int *)(*piVar2 + 0xc) + 1;
        *(undefined4 *)(*piVar2 + 0x24) = 0;
        return 0;
      }
      puVar5[10] = 2;
      puVar5[3] = uVar9 + 1;
      puVar5[0xb] = 1;
      *(undefined4 *)(*piVar2 + 0x24) = 0;
      return 0;
    }
    if (puVar5[9] == 0x1ff) goto LAB_0056505c;
    uVar9 = puVar5[3];
    if (puVar5[0xb] == 0) {
      if (uVar9 < *puVar5) {
        *(undefined1 *)(puVar5[7] + uVar9) = 2;
        *(int *)(*piVar2 + 0xc) = *(int *)(*piVar2 + 0xc) + 1;
      }
      else {
        puVar5[3] = uVar9 + 1;
        puVar5[10] = 2;
        puVar5[0xb] = 1;
      }
    }
    else {
      puVar5[3] = uVar9 + 1;
    }
    iVar6 = *piVar2;
    iVar4 = *(int *)(iVar6 + 8);
    if (*(int *)(iVar6 + 0x2c) != 0) goto LAB_0056538a;
    uVar9 = iVar4 + 1;
    if (uVar9 < *(uint *)(iVar6 + 4)) {
      iVar10 = *(int *)(iVar6 + 0x10);
      *(float *)(iVar10 + iVar4 * 4) = param_3;
      *(uint *)(iVar6 + 8) = uVar9;
      *(float *)(iVar10 + uVar9 * 4) = param_4;
      *(int *)(iVar6 + 8) = iVar4 + 2;
      return 0;
    }
    goto LAB_00565370;
  }
  if (!(bool)(bVar7 ^ 1U | bVar3)) {
    FUN_005640e4(param_1,param_2,&local_38,0);
    puVar5 = (uint *)*piVar2;
    uVar8 = 2;
    if (puVar5[9] == 0x1ff) {
      uVar8 = 0x82;
    }
    uVar9 = puVar5[3];
    if (puVar5[0xb] == 0) {
      if (uVar9 < *puVar5) {
        *(undefined1 *)(puVar5[7] + uVar9) = uVar8;
        *(int *)(*piVar2 + 0xc) = *(int *)(*piVar2 + 0xc) + 1;
      }
      else {
        puVar5[10] = 2;
        puVar5[3] = puVar5[3] + 1;
        puVar5[0xb] = 1;
      }
    }
    else {
      puVar5[3] = uVar9 + 1;
    }
    puVar5 = (uint *)*piVar2;
    uVar9 = puVar5[2];
    if (puVar5[0xb] == 0) {
      uVar11 = uVar9 + 1;
      if (uVar11 < puVar5[1]) {
        uVar12 = puVar5[4];
        *(float *)(uVar12 + uVar9 * 4) = local_38;
        puVar5[2] = uVar11;
        *(float *)(uVar12 + uVar11 * 4) = local_34;
        puVar5[2] = uVar9 + 2;
      }
      else {
        puVar5[2] = uVar9 + 2;
        puVar5[10] = 2;
        puVar5[0xb] = 1;
      }
    }
    else {
      puVar5[2] = uVar9 + 2;
    }
    fVar17 = (float)puVar5[0xc];
    iVar4 = (uint)(param_3 < fVar17) << 0x1f;
    fVar13 = extraout_s1;
    if (iVar4 < 0) {
      fVar13 = fVar17;
    }
    if (-1 < iVar4) {
      fVar13 = param_3;
    }
    fVar15 = (float)puVar5[0xd];
    if ((int)((uint)(fVar15 < fVar13) << 0x1f) < 0) {
      fVar13 = fVar15;
    }
    if ((int)((uint)(param_4 < fVar17) << 0x1f) < 0) {
      param_4 = fVar17;
    }
    if ((int)((uint)(fVar15 < param_4) << 0x1f) < 0) {
      param_4 = fVar15;
    }
    if (puVar5[9] == 0x100) {
      uVar9 = puVar5[3];
      if (puVar5[0xb] != 0) {
        puVar5[3] = uVar9 + 1;
        *(undefined4 *)(*piVar2 + 0x24) = 0;
        return 0;
      }
      if (uVar9 < *puVar5) {
        *(undefined1 *)(puVar5[7] + uVar9) = 0x80;
        *(int *)(*piVar2 + 0xc) = *(int *)(*piVar2 + 0xc) + 1;
        *(undefined4 *)(*piVar2 + 0x24) = 0;
        return 0;
      }
      puVar5[3] = uVar9 + 1;
      puVar5[10] = 2;
      puVar5[0xb] = 1;
      *(undefined4 *)(*piVar2 + 0x24) = 0;
      return 0;
    }
    if (puVar5[9] == 0x1ff) {
      puVar5[9] = 0;
      return 0;
    }
    uVar9 = puVar5[3];
    if (puVar5[0xb] == 0) {
      if (uVar9 < *puVar5) {
        *(undefined1 *)(puVar5[7] + uVar9) = 0x82;
        *(int *)(*piVar2 + 0xc) = *(int *)(*piVar2 + 0xc) + 1;
      }
      else {
        puVar5[3] = uVar9 + 1;
        puVar5[10] = 2;
        puVar5[0xb] = 1;
      }
    }
    else {
      puVar5[3] = uVar9 + 1;
    }
    iVar6 = *piVar2;
    iVar4 = *(int *)(iVar6 + 8);
    if (*(int *)(iVar6 + 0x2c) == 0) {
      uVar9 = iVar4 + 1;
      if (uVar9 < *(uint *)(iVar6 + 4)) {
        iVar10 = *(int *)(iVar6 + 0x10);
        *(float *)(iVar10 + iVar4 * 4) = fVar13;
        *(uint *)(iVar6 + 8) = uVar9;
        *(float *)(iVar10 + uVar9 * 4) = param_4;
        *(int *)(iVar6 + 8) = iVar4 + 2;
        return 0;
      }
      goto LAB_00565370;
    }
    goto LAB_0056538a;
  }
  if ((bool)(bVar3 & (bVar7 ^ 1U))) {
    FUN_005640e4(param_1,param_2,&local_38,1);
    puVar5 = (uint *)*piVar2;
    uVar9 = puVar5[3];
    if (puVar5[0xb] == 0) {
      if (uVar9 < *puVar5) {
        *(undefined1 *)(puVar5[7] + uVar9) = 0x82;
        *(int *)(*piVar2 + 0xc) = *(int *)(*piVar2 + 0xc) + 1;
      }
      else {
        puVar5[10] = 2;
        puVar5[3] = puVar5[3] + 1;
        puVar5[0xb] = 1;
      }
    }
    else {
      puVar5[3] = uVar9 + 1;
    }
    puVar5 = (uint *)*piVar2;
    uVar9 = puVar5[2];
    if (puVar5[0xb] == 0) {
      uVar11 = uVar9 + 1;
      if (uVar11 < puVar5[1]) {
        uVar12 = puVar5[4];
        *(float *)(uVar12 + uVar9 * 4) = local_38;
        puVar5[2] = uVar11;
        *(float *)(uVar12 + uVar11 * 4) = local_34;
        puVar5[2] = uVar9 + 2;
      }
      else {
        puVar5[2] = uVar9 + 2;
        puVar5[10] = 2;
        puVar5[0xb] = 1;
      }
    }
    else {
      puVar5[2] = uVar9 + 2;
    }
    if (puVar5[9] == 0x100) {
      uVar9 = puVar5[3];
      if (puVar5[0xb] != 0) {
        puVar5[3] = uVar9 + 1;
        *(undefined4 *)(*piVar2 + 0x24) = 0;
        return 0;
      }
      if (uVar9 < *puVar5) {
        *(undefined1 *)(puVar5[7] + uVar9) = 0;
        *(int *)(*piVar2 + 0xc) = *(int *)(*piVar2 + 0xc) + 1;
        *(undefined4 *)(*piVar2 + 0x24) = 0;
        return 0;
      }
      puVar5[3] = uVar9 + 1;
      puVar5[10] = 2;
      puVar5[0xb] = 1;
      *(undefined4 *)(*piVar2 + 0x24) = 0;
      return 0;
    }
    if (puVar5[9] == 0x1ff) goto LAB_0056505c;
    uVar9 = puVar5[3];
    if (puVar5[0xb] == 0) {
      if (uVar9 < *puVar5) {
        *(undefined1 *)(puVar5[7] + uVar9) = 2;
        *(int *)(*piVar2 + 0xc) = *(int *)(*piVar2 + 0xc) + 1;
      }
      else {
        puVar5[3] = uVar9 + 1;
        puVar5[10] = 2;
        puVar5[0xb] = 1;
      }
    }
    else {
      puVar5[3] = uVar9 + 1;
    }
    iVar6 = *piVar2;
    iVar4 = *(int *)(iVar6 + 8);
    if (*(int *)(iVar6 + 0x2c) == 0) {
      uVar9 = iVar4 + 1;
      if (uVar9 < *(uint *)(iVar6 + 4)) {
        iVar10 = *(int *)(iVar6 + 0x10);
        *(float *)(iVar10 + iVar4 * 4) = param_3;
        *(uint *)(iVar6 + 8) = uVar9;
        *(float *)(iVar10 + uVar9 * 4) = param_4;
        *(int *)(iVar6 + 8) = iVar4 + 2;
        return 0;
      }
      goto LAB_00565370;
    }
    goto LAB_0056538a;
  }
  iVar6 = FUN_005640e4(param_3,param_4,param_1,param_2,&local_38,1);
  puVar5 = (uint *)*piVar2;
  fVar13 = (float)puVar5[0xc];
  iVar4 = (uint)(param_1 < fVar13) << 0x1f;
  fVar17 = extraout_s3;
  if (iVar4 < 0) {
    fVar17 = fVar13;
  }
  if (-1 < iVar4) {
    fVar17 = param_1;
  }
  fVar15 = (float)puVar5[0xd];
  if ((int)((uint)(fVar15 < fVar17) << 0x1f) < 0) {
    fVar17 = fVar15;
  }
  iVar4 = (uint)(param_2 < fVar13) << 0x1f;
  fVar14 = extraout_s1_00;
  if (iVar4 < 0) {
    fVar14 = fVar13;
  }
  if (-1 < iVar4) {
    fVar14 = param_2;
  }
  if ((int)((uint)(fVar15 < fVar14) << 0x1f) < 0) {
    fVar14 = fVar15;
  }
  iVar4 = (uint)(param_3 < fVar13) << 0x1f;
  fVar16 = extraout_s2;
  if (iVar4 < 0) {
    fVar16 = fVar13;
  }
  if (-1 < iVar4) {
    fVar16 = param_3;
  }
  if ((int)((uint)(fVar15 < fVar16) << 0x1f) < 0) {
    fVar16 = fVar15;
  }
  if (-1 < (int)((uint)(param_4 < fVar13) << 0x1f)) {
    fVar13 = param_4;
  }
  if ((int)((uint)(fVar15 < fVar13) << 0x1f) < 0) {
    fVar13 = fVar15;
  }
  if (iVar6 == 2) {
    uVar9 = puVar5[3];
    if (puVar5[0xb] == 0) {
      if (uVar9 < *puVar5) {
        *(undefined1 *)(puVar5[7] + uVar9) = 0x82;
        *(int *)(*piVar2 + 0xc) = *(int *)(*piVar2 + 0xc) + 1;
      }
      else {
        puVar5[3] = uVar9 + 1;
        puVar5[10] = 2;
        puVar5[0xb] = 1;
      }
    }
    else {
      puVar5[3] = uVar9 + 1;
    }
    puVar5 = (uint *)*piVar2;
    uVar8 = 2;
    if (puVar5[9] == 0x1ff) {
      uVar8 = 0x82;
    }
    fVar15 = ABS(fVar17);
    if (-1 < (int)((uint)(ABS(fVar17) < ABS(local_38)) << 0x1f)) {
      fVar15 = ABS(local_38);
    }
    fVar18 = fVar17 - local_38;
    if ((int)((uint)(fVar18 < 0.0) << 0x1f) < 0) {
      fVar18 = local_38 - fVar17;
    }
    if (fVar18 <= fVar15 * DAT_0056539c) {
LAB_00565162:
      uVar9 = puVar5[2];
      if (puVar5[0xb] == 0) {
        uVar11 = uVar9 + 1;
        if (puVar5[1] <= uVar11) {
          puVar5[2] = uVar9 + 2;
          puVar5[10] = 2;
          puVar5[0xb] = 1;
          goto LAB_005651a8;
        }
        uVar12 = puVar5[4];
        *(float *)(uVar12 + uVar9 * 4) = local_38;
        puVar5[2] = uVar11;
        *(float *)(uVar12 + uVar11 * 4) = local_34;
        puVar5[2] = uVar9 + 2;
        uVar9 = puVar5[3];
        if (uVar9 < *puVar5) {
          *(undefined1 *)(puVar5[7] + uVar9) = uVar8;
          *(int *)(*piVar2 + 0xc) = *(int *)(*piVar2 + 0xc) + 1;
        }
        else {
          puVar5[3] = uVar9 + 1;
          puVar5[10] = 2;
          puVar5[0xb] = 1;
        }
      }
      else {
        puVar5[2] = uVar9 + 2;
LAB_005651a8:
        puVar5[3] = puVar5[3] + 1;
      }
      iVar4 = *piVar2;
      if (*(int *)(iVar4 + 0x2c) == 0) {
        iVar6 = *(int *)(iVar4 + 8);
        uVar9 = iVar6 + 1;
        if (uVar9 < *(uint *)(iVar4 + 4)) {
          iVar10 = *(int *)(iVar4 + 0x10);
          *(undefined4 *)(iVar10 + iVar6 * 4) = local_30;
          *(uint *)(iVar4 + 8) = uVar9;
          *(undefined4 *)(iVar10 + uVar9 * 4) = local_2c;
          *(int *)(iVar4 + 8) = iVar6 + 2;
        }
        else {
LAB_00565276:
          *(undefined4 *)(iVar4 + 0x28) = 2;
          *(int *)(iVar4 + 8) = *(int *)(iVar4 + 8) + 2;
          *(undefined4 *)(iVar4 + 0x2c) = 1;
        }
      }
      else {
        iVar6 = *(int *)(iVar4 + 8);
LAB_00565286:
        *(int *)(iVar4 + 8) = iVar6 + 2;
      }
    }
    else {
      fVar17 = ABS(fVar14);
      if (-1 < (int)((uint)(ABS(fVar14) < ABS(local_34)) << 0x1f)) {
        fVar17 = ABS(local_34);
      }
      fVar15 = fVar14 - local_34;
      if ((int)((uint)(fVar15 < 0.0) << 0x1f) < 0) {
        fVar15 = local_34 - fVar14;
      }
      if (fVar15 <= fVar17 * DAT_0056539c) goto LAB_00565162;
      uVar9 = puVar5[2];
      if (puVar5[0xb] == 0) {
        uVar11 = uVar9 + 1;
        if (puVar5[1] <= uVar11) {
          puVar5[2] = uVar9 + 2;
          puVar5[10] = 2;
          puVar5[0xb] = 1;
          goto LAB_00565234;
        }
        uVar12 = puVar5[4];
        *(undefined4 *)(uVar12 + uVar9 * 4) = local_30;
        puVar5[2] = uVar11;
        *(undefined4 *)(uVar12 + uVar11 * 4) = local_2c;
        puVar5[2] = uVar9 + 2;
        uVar9 = puVar5[3];
        if (uVar9 < *puVar5) {
          *(undefined1 *)(puVar5[7] + uVar9) = uVar8;
          *(int *)(*piVar2 + 0xc) = *(int *)(*piVar2 + 0xc) + 1;
        }
        else {
          puVar5[3] = uVar9 + 1;
          puVar5[10] = 2;
          puVar5[0xb] = 1;
        }
      }
      else {
        puVar5[2] = uVar9 + 2;
LAB_00565234:
        puVar5[3] = puVar5[3] + 1;
      }
      iVar4 = *piVar2;
      iVar6 = *(int *)(iVar4 + 8);
      if (*(int *)(iVar4 + 0x2c) != 0) goto LAB_00565286;
      uVar9 = iVar6 + 1;
      if (*(uint *)(iVar4 + 4) <= uVar9) goto LAB_00565276;
      iVar10 = *(int *)(iVar4 + 0x10);
      *(float *)(iVar10 + iVar6 * 4) = local_38;
      *(uint *)(iVar4 + 8) = uVar9;
      *(float *)(iVar10 + uVar9 * 4) = local_34;
      *(int *)(iVar4 + 8) = iVar6 + 2;
    }
    puVar5 = (uint *)*piVar2;
    if (puVar5[9] == 0x100) {
      uVar9 = puVar5[3];
      if (puVar5[0xb] != 0) {
        puVar5[3] = uVar9 + 1;
        *(undefined4 *)(*piVar2 + 0x24) = 0;
        return 0;
      }
      if (uVar9 < *puVar5) {
        *(undefined1 *)(puVar5[7] + uVar9) = 0x80;
        *(int *)(*piVar2 + 0xc) = *(int *)(*piVar2 + 0xc) + 1;
        *(undefined4 *)(*piVar2 + 0x24) = 0;
        return 0;
      }
      puVar5[10] = 2;
      puVar5[3] = uVar9 + 1;
      puVar5[0xb] = 1;
      *(undefined4 *)(*piVar2 + 0x24) = 0;
      return 0;
    }
    if (puVar5[9] == 0x1ff) {
      puVar5[9] = 0;
      return 0;
    }
    uVar9 = puVar5[3];
    if (puVar5[0xb] == 0) {
      if (uVar9 < *puVar5) {
        *(undefined1 *)(puVar5[7] + uVar9) = 0x82;
        *(int *)(*piVar2 + 0xc) = *(int *)(*piVar2 + 0xc) + 1;
      }
      else {
        puVar5[3] = uVar9 + 1;
        puVar5[10] = 2;
        puVar5[0xb] = 1;
      }
    }
    else {
      puVar5[3] = uVar9 + 1;
    }
  }
  else {
    fVar15 = ABS(fVar17);
    if (-1 < (int)((uint)(ABS(fVar17) < ABS(fVar16)) << 0x1f)) {
      fVar15 = ABS(fVar16);
    }
    fVar18 = fVar17 - fVar16;
    if ((int)((uint)(fVar18 < 0.0) << 0x1f) < 0) {
      fVar18 = fVar16 - fVar17;
    }
    if (fVar15 * DAT_00564f5c < fVar18) {
      fVar15 = ABS(fVar14);
      if (-1 < (int)((uint)(ABS(fVar14) < ABS(fVar13)) << 0x1f)) {
        fVar15 = ABS(fVar13);
      }
      fVar18 = fVar14 - fVar13;
      if ((int)((uint)(fVar18 < 0.0) << 0x1f) < 0) {
        fVar18 = fVar13 - fVar14;
      }
      if (fVar15 * DAT_00564f5c < fVar18) {
        uVar9 = puVar5[3];
        if (puVar5[0xb] == 0) {
          if (uVar9 < *puVar5) {
            *(undefined1 *)(puVar5[7] + uVar9) = 0x82;
            *(int *)(*piVar2 + 0xc) = *(int *)(*piVar2 + 0xc) + 1;
          }
          else {
            puVar5[3] = uVar9 + 1;
            puVar5[10] = 2;
            puVar5[0xb] = 1;
          }
        }
        else {
          puVar5[3] = uVar9 + 1;
        }
        iVar4 = *piVar2;
        if ((int)((uint)(ABS((fVar17 - param_1) * (param_4 - param_2) +
                             (param_2 - fVar13) * (param_3 - param_1)) <
                        ABS((fVar16 - param_1) * (param_4 - param_2) +
                            (param_2 - fVar14) * (param_3 - param_1))) << 0x1f) < 0) {
          if (*(int *)(iVar4 + 0x2c) == 0) {
            iVar6 = *(int *)(iVar4 + 8);
            uVar9 = iVar6 + 1;
            if (uVar9 < *(uint *)(iVar4 + 4)) {
              iVar10 = *(int *)(iVar4 + 0x10);
              *(float *)(iVar10 + iVar6 * 4) = fVar17;
              *(uint *)(iVar4 + 8) = uVar9;
              *(float *)(iVar10 + uVar9 * 4) = fVar13;
              *(int *)(iVar4 + 8) = iVar6 + 2;
            }
            else {
LAB_00564fd4:
              *(undefined4 *)(iVar4 + 0x28) = 2;
              *(int *)(iVar4 + 8) = *(int *)(iVar4 + 8) + 2;
              *(undefined4 *)(iVar4 + 0x2c) = 1;
            }
          }
          else {
LAB_00564fe6:
            *(int *)(iVar4 + 8) = *(int *)(iVar4 + 8) + 2;
          }
        }
        else {
          if (*(int *)(iVar4 + 0x2c) != 0) goto LAB_00564fe6;
          iVar6 = *(int *)(iVar4 + 8);
          uVar9 = iVar6 + 1;
          if (*(uint *)(iVar4 + 4) <= uVar9) goto LAB_00564fd4;
          iVar10 = *(int *)(iVar4 + 0x10);
          *(float *)(iVar10 + iVar6 * 4) = fVar16;
          *(uint *)(iVar4 + 8) = uVar9;
          *(float *)(iVar10 + uVar9 * 4) = fVar14;
          *(int *)(iVar4 + 8) = iVar6 + 2;
        }
      }
    }
    puVar5 = (uint *)*piVar2;
    if (puVar5[9] == 0x100) {
      uVar9 = puVar5[3];
      if (puVar5[0xb] != 0) {
        puVar5[3] = uVar9 + 1;
        *(undefined4 *)(*piVar2 + 0x24) = 0;
        return 0;
      }
      if (uVar9 < *puVar5) {
        *(undefined1 *)(puVar5[7] + uVar9) = 0x80;
        *(int *)(*piVar2 + 0xc) = *(int *)(*piVar2 + 0xc) + 1;
        *(undefined4 *)(*piVar2 + 0x24) = 0;
        return 0;
      }
      puVar5[3] = uVar9 + 1;
      puVar5[10] = 2;
      puVar5[0xb] = 1;
      *(undefined4 *)(*piVar2 + 0x24) = 0;
      return 0;
    }
    if (puVar5[9] == 0x1ff) {
LAB_0056505c:
      puVar5[9] = 0;
      return 0;
    }
    uVar9 = puVar5[3];
    if (puVar5[0xb] == 0) {
      if (uVar9 < *puVar5) {
        *(undefined1 *)(puVar5[7] + uVar9) = 0x82;
        *(int *)(*piVar2 + 0xc) = *(int *)(*piVar2 + 0xc) + 1;
      }
      else {
        puVar5[3] = uVar9 + 1;
        puVar5[10] = 2;
        puVar5[0xb] = 1;
      }
    }
    else {
      puVar5[3] = uVar9 + 1;
    }
  }
  iVar6 = *piVar2;
  iVar4 = *(int *)(iVar6 + 8);
  if (*(int *)(iVar6 + 0x2c) != 0) {
LAB_0056538a:
    *(int *)(iVar6 + 8) = iVar4 + 2;
    return 0;
  }
  uVar9 = iVar4 + 1;
  if (uVar9 < *(uint *)(iVar6 + 4)) {
    iVar10 = *(int *)(iVar6 + 0x10);
    *(float *)(iVar10 + iVar4 * 4) = fVar16;
    *(uint *)(iVar6 + 8) = uVar9;
    *(float *)(iVar10 + uVar9 * 4) = fVar13;
    *(int *)(iVar6 + 8) = iVar4 + 2;
    return 0;
  }
LAB_00565370:
  *(undefined4 *)(iVar6 + 0x28) = 2;
  *(int *)(iVar6 + 8) = *(int *)(iVar6 + 8) + 2;
  *(undefined4 *)(iVar6 + 0x2c) = 1;
  return 0;
}

