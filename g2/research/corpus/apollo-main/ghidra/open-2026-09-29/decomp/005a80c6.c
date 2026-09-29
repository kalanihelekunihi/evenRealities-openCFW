
int af_glyph_hints_reload(undefined4 *param_1,short *param_2,undefined4 param_3,undefined4 param_4)

{
  undefined1 uVar1;
  int iVar2;
  ushort *puVar3;
  undefined4 uVar4;
  int iVar5;
  undefined4 *puVar6;
  ushort *puVar7;
  int iVar8;
  short *psVar9;
  int iVar10;
  int iVar11;
  short sVar12;
  int iVar13;
  int iVar14;
  undefined4 uVar15;
  uint uVar16;
  undefined4 *puVar17;
  ushort *puVar18;
  byte *pbVar19;
  ushort *puVar20;
  ushort *puVar21;
  ushort *local_48;
  int local_44;
  uint local_40;
  ushort *local_3c;
  int local_38;
  int local_34;
  undefined4 local_30;
  undefined4 local_2c;
  undefined4 uStack_28;
  
  local_44 = 0;
  local_2c = param_1[1];
  local_30 = param_1[3];
  local_34 = param_1[2];
  local_38 = param_1[4];
  uVar15 = *param_1;
  param_1[6] = 0;
  param_1[9] = 0;
  param_1[0xb] = 0;
  param_1[0xe] = 0;
  param_1[0x15c] = 0;
  param_1[0x15f] = 0;
  uVar16 = (uint)*param_2;
  uStack_28 = param_4;
  if (uVar16 < 9) {
    if (param_1[10] == 0) {
      param_1[10] = param_1 + 0x2b2;
      param_1[8] = 8;
    }
  }
  else if ((uint)param_1[8] < uVar16) {
    if ((undefined4 *)param_1[10] == param_1 + 0x2b2) {
      param_1[10] = 0;
    }
    uVar16 = uVar16 + 3 & 0xfffffffc;
    uVar4 = ft_mem_realloc(uVar15,4,param_1[8],uVar16,param_1[10],&local_44);
    param_1[10] = uVar4;
    if (local_44 != 0) {
      return local_44;
    }
    param_1[8] = uVar16;
  }
  sVar12 = param_2[1];
  uVar16 = (int)sVar12 + 2;
  if (uVar16 < 0x61) {
    if (param_1[7] == 0) {
      param_1[7] = param_1 + 0x2ba;
      param_1[5] = 0x60;
    }
  }
  else if ((uint)param_1[5] < uVar16) {
    if ((undefined4 *)param_1[7] == param_1 + 0x2ba) {
      param_1[7] = 0;
    }
    uVar16 = (int)sVar12 + 0xbU & 0xfffffff8;
    uVar15 = ft_mem_realloc(uVar15,0x28,param_1[5],uVar16,param_1[7],&local_44);
    param_1[7] = uVar15;
    if (local_44 != 0) {
      return local_44;
    }
    param_1[5] = uVar16;
  }
  param_1[6] = (int)param_2[1];
  param_1[9] = (int)*param_2;
  *(undefined1 *)(param_1 + 0x11) = 2;
  *(undefined1 *)(param_1 + 0x162) = 0xff;
  iVar2 = FT_Outline_Get_Orientation(param_2);
  if (iVar2 == 1) {
    *(undefined1 *)(param_1 + 0x11) = 0xfe;
    *(undefined1 *)(param_1 + 0x162) = 1;
  }
  param_1[1] = local_2c;
  param_1[3] = local_30;
  param_1[2] = local_34;
  param_1[4] = local_38;
  param_1[0x2b0] = 0;
  param_1[0x2b1] = 0;
  puVar3 = (ushort *)param_1[7];
  if (param_1[6] != 0) {
    local_3c = puVar3 + param_1[6] * 0x14;
    local_40 = (uint)*(ushort *)(*(int *)(param_1[0x2af] + 4) + 0x44) * 0x14 >> 0xb;
    puVar17 = *(undefined4 **)(param_2 + 2);
    pbVar19 = *(byte **)(param_2 + 4);
    sVar12 = **(short **)(param_2 + 6);
    puVar20 = puVar3 + sVar12 * 0x14;
    iVar2 = 0;
    puVar18 = puVar3;
    local_48 = puVar20;
    for (; puVar3 < local_3c; puVar3 = puVar3 + 0x14) {
      *(byte *)(puVar3 + 1) = 4;
      *(byte *)((int)puVar3 + 3) = 4;
      puVar3[6] = (ushort)*puVar17;
      puVar3[7] = (ushort)puVar17[1];
      iVar5 = FT_MulFix(*puVar17,local_2c);
      *(int *)(puVar3 + 8) = local_34 + iVar5;
      *(undefined4 *)(puVar3 + 2) = *(undefined4 *)(puVar3 + 8);
      iVar5 = FT_MulFix(puVar17[1],local_30);
      *(int *)(puVar3 + 10) = local_38 + iVar5;
      *(undefined4 *)(puVar3 + 4) = *(undefined4 *)(puVar3 + 10);
      local_48[6] = (ushort)*(undefined4 *)(*(int *)(param_2 + 2) + sVar12 * 8);
      local_48[7] = (ushort)*(undefined4 *)(*(int *)(param_2 + 2) + sVar12 * 8 + 4);
      if ((*pbVar19 & 3) == 0) {
        *puVar3 = 1;
      }
      else if ((*pbVar19 & 3) == 2) {
        *puVar3 = 2;
      }
      else {
        *puVar3 = 0;
      }
      iVar8 = (int)(short)puVar3[6] - (int)(short)puVar20[6];
      iVar5 = (int)(short)puVar3[7] - (int)(short)puVar20[7];
      if (iVar8 < 0) {
        iVar8 = -iVar8;
      }
      if (iVar5 < 0) {
        iVar5 = -iVar5;
      }
      if (iVar5 + iVar8 < (int)local_40) {
        *puVar20 = *puVar20 | 0x20;
      }
      *(ushort **)(puVar3 + 0x12) = puVar20;
      *(ushort **)(puVar20 + 0x10) = puVar3;
      puVar20 = puVar3;
      if ((puVar3 == local_48) && (iVar2 = iVar2 + 1, iVar2 < *param_2)) {
        sVar12 = *(short *)(*(int *)(param_2 + 6) + iVar2 * 2);
        puVar20 = puVar18 + sVar12 * 0x14;
        local_48 = puVar20;
      }
      puVar17 = puVar17 + 2;
      pbVar19 = pbVar19 + 1;
    }
    puVar17 = (undefined4 *)param_1[10];
    puVar6 = puVar17 + param_1[9];
    psVar9 = *(short **)(param_2 + 6);
    sVar12 = 0;
    for (; puVar17 < puVar6; puVar17 = puVar17 + 1) {
      *puVar17 = puVar18 + sVar12 * 0x14;
      sVar12 = *psVar9 + 1;
      psVar9 = psVar9 + 1;
    }
    iVar8 = local_40 * 2;
    iVar2 = param_1[10];
    iVar5 = param_1[9];
    for (puVar17 = (undefined4 *)param_1[10]; puVar3 = puVar18,
        puVar17 < (undefined4 *)(iVar2 + iVar5 * 4); puVar17 = puVar17 + 1) {
      puVar7 = (ushort *)*puVar17;
      puVar3 = puVar7;
      for (puVar20 = *(ushort **)(puVar7 + 0x12); puVar20 != puVar7;
          puVar20 = *(ushort **)(puVar20 + 0x12)) {
        iVar10 = (int)(short)puVar3[6] - (int)(short)puVar20[6];
        iVar13 = (int)(short)puVar3[7] - (int)(short)puVar20[7];
        if (iVar10 < 0) {
          iVar10 = -iVar10;
        }
        if (iVar13 < 0) {
          iVar13 = -iVar13;
        }
        if (iVar8 + -1 <= iVar13 + iVar10) break;
        puVar3 = puVar20;
      }
      puVar3[0xc] = 0;
      puVar3[0xd] = 0;
      *(int *)(puVar3 + 0xe) = -*(int *)(puVar3 + 0xc);
      iVar10 = 0;
      iVar13 = 0;
      puVar20 = puVar3;
      puVar7 = puVar3;
      do {
        puVar21 = *(ushort **)(puVar20 + 0x10);
        iVar10 = (iVar10 + (short)puVar21[6]) - (int)(short)puVar20[6];
        iVar13 = (iVar13 + (short)puVar21[7]) - (int)(short)puVar20[7];
        iVar11 = iVar10;
        if (iVar10 < 0) {
          iVar11 = -iVar10;
        }
        iVar14 = iVar13;
        if (iVar13 < 0) {
          iVar14 = -iVar13;
        }
        if (iVar14 + iVar11 < (int)local_40) {
          *puVar21 = *puVar21 | 0x10;
        }
        else {
          *(int *)(puVar7 + 0xc) = ((int)puVar21 - (int)puVar7) / 0x28;
          *(int *)(puVar21 + 0xe) = -*(int *)(puVar7 + 0xc);
          uVar1 = af_direction_compute();
          *(undefined1 *)((int)puVar7 + 3) = uVar1;
          for (puVar7 = *(ushort **)(puVar7 + 0x10); puVar7 != puVar21;
              puVar7 = *(ushort **)(puVar7 + 0x10)) {
            *(undefined1 *)(puVar7 + 1) = uVar1;
            *(undefined1 *)((int)puVar7 + 3) = uVar1;
          }
          *(undefined1 *)(puVar21 + 1) = uVar1;
          *(int *)(puVar7 + 0xc) = ((int)puVar3 - (int)puVar7) / 0x28;
          *(int *)(puVar3 + 0xe) = -*(int *)(puVar7 + 0xc);
          iVar10 = 0;
          iVar13 = 0;
        }
        puVar20 = puVar21;
      } while (puVar21 != puVar3);
    }
    for (; puVar3 < local_3c; puVar3 = puVar3 + 0x14) {
      if (((-1 < (int)((uint)(byte)*puVar3 << 0x1b)) && ((byte)puVar3[1] == 4)) &&
         (*(byte *)((int)puVar3 + 3) == 4)) {
        iVar2 = *(int *)(puVar3 + 0xc);
        puVar20 = puVar3 + *(int *)(puVar3 + 0xe) * 0x14;
        if ((-1 < ((int)(short)puVar3[iVar2 * 0x14 + 6] - (int)(short)puVar3[6] ^
                  (int)(short)puVar3[6] - (int)(short)puVar20[6])) &&
           (-1 < ((int)(short)puVar3[7] - (int)(short)puVar20[7] ^
                 (int)(short)puVar3[iVar2 * 0x14 + 7] - (int)(short)puVar3[7]))) {
          *puVar3 = *puVar3 | 0x10;
          *(int *)(puVar20 + 0xc) = (int)((int)puVar3 + (iVar2 * 0x28 - (int)puVar20)) / 0x28;
          *(int *)(puVar3 + iVar2 * 0x14 + 0xe) = -*(int *)(puVar20 + 0xc);
        }
      }
    }
    for (; puVar18 < local_3c; puVar18 = puVar18 + 0x14) {
      if (-1 < (int)((uint)(byte)*puVar18 << 0x1b)) {
        if ((*puVar18 & 3) == 0) {
          if (*(byte *)((int)puVar18 + 3) == (byte)puVar18[1]) {
            if (*(byte *)((int)puVar18 + 3) == 4) {
              iVar2 = *(int *)(puVar18 + 0xc);
              puVar3 = puVar18 + *(int *)(puVar18 + 0xe) * 0x14;
              iVar5 = ft_corner_is_flat((int)(short)puVar18[6] - (int)(short)puVar3[6],
                                        (int)(short)puVar18[7] - (int)(short)puVar3[7],
                                        (int)(short)puVar18[iVar2 * 0x14 + 6] -
                                        (int)(short)puVar18[6],
                                        (int)(short)puVar18[iVar2 * 0x14 + 7] -
                                        (int)(short)puVar18[7]);
              if (iVar5 == 0) goto LAB_005a8520;
              *(int *)(puVar3 + 0xc) = (int)((int)puVar18 + (iVar2 * 0x28 - (int)puVar3)) / 0x28;
              *(int *)(puVar18 + iVar2 * 0x14 + 0xe) = -*(int *)(puVar3 + 0xc);
            }
          }
          else if ((int)(char)(byte)puVar18[1] + (int)(char)*(byte *)((int)puVar18 + 3) != 0)
          goto LAB_005a8520;
        }
        *puVar18 = *puVar18 | 0x10;
      }
LAB_005a8520:
    }
  }
  return local_44;
}

