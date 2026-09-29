
undefined4
FUN_005bd3a0(int *param_1,uint param_2,uint param_3,int param_4,int param_5,uint *param_6,
            uint *param_7,int param_8,int *param_9,uint *param_10)

{
  undefined3 uVar1;
  uint uVar2;
  undefined4 uVar3;
  uint uVar4;
  int iVar5;
  int iVar6;
  int *piVar7;
  uint uVar8;
  undefined1 uVar9;
  uint uVar10;
  uint uVar11;
  uint *puVar12;
  uint uVar13;
  uint uVar14;
  uint uVar15;
  undefined4 *puVar16;
  uint *puVar17;
  uint uVar18;
  uint uVar19;
  int iVar20;
  int iVar21;
  uint uVar22;
  undefined4 local_100;
  uint local_fc;
  uint local_e0 [16];
  uint local_a0 [31];
  
  local_fc = 0;
  local_a0[0] = 0;
  local_a0[1] = 0;
  local_a0[2] = 0;
  local_a0[3] = 0;
  local_a0[4] = 0;
  local_a0[5] = 0;
  local_a0[6] = 0;
  local_a0[7] = 0;
  local_a0[8] = 0;
  local_a0[9] = 0;
  local_a0[10] = 0;
  local_a0[0xb] = 0;
  local_a0[0xc] = 0;
  local_a0[0xd] = 0;
  local_a0[0xe] = 0;
  local_a0[0xf] = 0;
  uVar2 = param_2;
  piVar7 = param_1;
  do {
    local_a0[*piVar7] = local_a0[*piVar7] + 1;
    piVar7 = piVar7 + 1;
    uVar2 = uVar2 - 1;
  } while (uVar2 != 0);
  if (local_a0[0] == param_2) {
    *param_6 = 0;
    *param_7 = 0;
    uVar3 = 0;
  }
  else {
    for (uVar2 = 1; (uVar2 < 0x10 && (local_a0[uVar2] == 0)); uVar2 = uVar2 + 1) {
    }
    uVar8 = *param_7;
    if (*param_7 < uVar2) {
      uVar8 = uVar2;
    }
    for (uVar4 = 0xf; (uVar4 != 0 && (local_a0[uVar4] == 0)); uVar4 = uVar4 - 1) {
    }
    if (uVar4 < uVar8) {
      uVar8 = uVar4;
    }
    *param_7 = uVar8;
    iVar21 = 1 << (uVar2 & 0xff);
    for (uVar13 = uVar2; uVar13 < uVar4; uVar13 = uVar13 + 1) {
      if ((int)(iVar21 - local_a0[uVar13]) < 0) {
        return 0xfffffffd;
      }
      iVar21 = (iVar21 - local_a0[uVar13]) * 2;
    }
    iVar21 = iVar21 - local_a0[uVar4];
    if (iVar21 < 0) {
      uVar3 = 0xfffffffd;
    }
    else {
      local_a0[uVar4] = iVar21 + local_a0[uVar4];
      uVar14 = 0;
      local_e0[1] = 0;
      puVar12 = local_a0;
      puVar17 = local_e0 + 2;
      uVar13 = uVar4;
      while( true ) {
        puVar12 = puVar12 + 1;
        uVar13 = uVar13 - 1;
        if (uVar13 == 0) break;
        uVar14 = *puVar12 + uVar14;
        *puVar17 = uVar14;
        puVar17 = puVar17 + 1;
      }
      uVar13 = 0;
      do {
        iVar5 = *param_1;
        param_1 = param_1 + 1;
        if (iVar5 != 0) {
          param_10[local_e0[iVar5]] = uVar13;
          local_e0[iVar5] = local_e0[iVar5] + 1;
        }
        uVar13 = uVar13 + 1;
      } while (uVar13 < param_2);
      uVar14 = local_e0[uVar4];
      uVar11 = 0;
      local_e0[0] = 0;
      iVar5 = -1;
      uVar13 = -uVar8;
      local_a0[0x10] = 0;
      uVar19 = 0;
      uVar22 = 0;
      puVar12 = param_10;
      for (; (int)uVar2 <= (int)uVar4; uVar2 = uVar2 + 1) {
        uVar18 = local_a0[uVar2];
        while (uVar15 = uVar18 - 1, uVar18 != 0) {
          while ((int)(uVar8 + uVar13) < (int)uVar2) {
            iVar6 = iVar5 + 1;
            uVar13 = uVar8 + uVar13;
            uVar19 = uVar4 - uVar13;
            if (uVar8 < uVar4 - uVar13) {
              uVar19 = uVar8;
            }
            uVar10 = uVar2 - uVar13;
            uVar22 = 1 << (uVar10 & 0xff);
            if (uVar18 < uVar22) {
              iVar20 = (uVar22 - uVar15) + -1;
              puVar17 = local_a0 + uVar2;
              if (uVar10 < uVar19) {
                while (uVar10 = uVar10 + 1, uVar10 < uVar19) {
                  puVar17 = puVar17 + 1;
                  if ((uint)(iVar20 * 2) <= *puVar17) break;
                  iVar20 = iVar20 * 2 - *puVar17;
                }
              }
            }
            uVar22 = 1 << (uVar10 & 0xff);
            if (0x5a0 < uVar22 + *param_9) {
              return 0xfffffffd;
            }
            uVar19 = param_8 + *param_9 * 8;
            local_a0[iVar5 + 0x11] = uVar19;
            *param_9 = uVar22 + *param_9;
            if (iVar6 == 0) {
              *param_6 = uVar19;
              iVar5 = iVar6;
            }
            else {
              local_e0[iVar6] = uVar11;
              local_100 = CONCAT31(CONCAT21(local_100._2_2_,(char)uVar8),(char)uVar10);
              uVar10 = uVar11 >> (uVar13 - uVar8 & 0xff);
              local_fc = ((int)(uVar19 - local_a0[iVar5 + 0x10]) >> 3) - uVar10;
              puVar16 = (undefined4 *)(local_a0[iVar5 + 0x10] + uVar10 * 8);
              *puVar16 = local_100;
              puVar16[1] = local_fc;
              iVar5 = iVar6;
            }
          }
          uVar1 = CONCAT21(local_100._2_2_,(char)uVar2 - (char)uVar13);
          if (puVar12 < param_10 + uVar14) {
            if (*puVar12 < param_3) {
              if (*puVar12 < 0x100) {
                uVar9 = 0;
              }
              else {
                uVar9 = 0x60;
              }
              local_100 = CONCAT31(uVar1,uVar9);
              local_fc = *puVar12;
              puVar12 = puVar12 + 1;
            }
            else {
              local_100 = CONCAT31(uVar1,(char)*(undefined4 *)(param_5 + (*puVar12 - param_3) * 4) +
                                         'P');
              local_fc = *(uint *)(param_4 + (*puVar12 - param_3) * 4);
              puVar12 = puVar12 + 1;
            }
          }
          else {
            local_100 = CONCAT31(uVar1,0xc0);
          }
          for (uVar18 = uVar11 >> (uVar13 & 0xff); uVar18 < uVar22;
              uVar18 = (1 << (uVar2 - uVar13 & 0xff)) + uVar18) {
            puVar16 = (undefined4 *)(uVar19 + uVar18 * 8);
            *puVar16 = local_100;
            puVar16[1] = local_fc;
          }
          uVar18 = 1 << (uVar2 + 0xff & 0xff);
          while ((uVar11 & uVar18) != 0) {
            uVar11 = uVar11 ^ uVar18;
            uVar18 = uVar18 >> 1;
          }
          uVar11 = uVar11 ^ uVar18;
          for (; uVar18 = uVar15, ((1 << (uVar13 & 0xff)) - 1U & uVar11) != local_e0[iVar5];
              iVar5 = iVar5 + -1) {
            uVar13 = uVar13 - uVar8;
          }
        }
      }
      if ((iVar21 == 0) || (uVar4 == 1)) {
        uVar3 = 0;
      }
      else {
        uVar3 = 0xfffffffb;
      }
    }
  }
  return uVar3;
}

