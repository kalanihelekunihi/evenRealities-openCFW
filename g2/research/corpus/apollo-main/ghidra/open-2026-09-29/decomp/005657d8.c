
int FUN_005657d8(uint *param_1)

{
  int *piVar1;
  int iVar2;
  uint uVar3;
  bool bVar4;
  int iVar5;
  uint *puVar6;
  uint uVar7;
  int iVar8;
  uint uVar9;
  byte bVar10;
  int iVar11;
  uint uVar12;
  byte bVar13;
  bool bVar14;
  bool bVar15;
  float fVar16;
  undefined4 uVar17;
  undefined4 uVar18;
  undefined4 uVar19;
  undefined4 uVar20;
  float fVar21;
  float fVar22;
  float fVar23;
  float fVar24;
  float fVar25;
  float fVar26;
  float fVar27;
  undefined8 uVar28;
  float fVar29;
  undefined8 unaff_d10;
  float fVar30;
  float fVar31;
  float fVar32;
  float fVar33;
  float fVar34;
  float fVar35;
  undefined8 unaff_d15;
  undefined8 uVar36;
  char local_108;
  char local_107;
  undefined1 local_106;
  byte local_105;
  int local_104;
  int local_100;
  float local_fc;
  float local_f8;
  float local_f4;
  float local_f0;
  float local_ec;
  float local_e8;
  float local_e4;
  float local_e0;
  float local_dc;
  float local_d8;
  float local_d4;
  float local_d0;
  float local_cc;
  float local_c8;
  byte local_c4;
  float local_c0;
  float local_bc;
  float local_b8;
  float local_b4;
  float local_b0;
  float local_ac;
  float local_a8;
  float local_a4;
  float local_a0;
  float local_9c;
  float local_98;
  float local_94;
  float local_90;
  float local_70;
  float local_6c;
  
  FUN_0048949c(&local_108,0x48);
  piVar1 = DAT_0056640c;
  local_108 = '\x01';
  local_106 = 1;
  uVar9 = 0;
  do {
    local_b0 = (float)unaff_d15;
    local_ac = (float)((ulonglong)unaff_d15 >> 0x20);
LAB_0056580e:
    iVar5 = local_104;
    if (*param_1 <= uVar9) {
      if (local_107 == '\x01') {
        fVar29 = DAT_0056722c;
        local_6c = DAT_0056722c;
        if (local_108 == '\0') {
          fVar29 = local_cc;
          local_6c = local_c8;
        }
        iVar5 = *piVar1;
        local_70 = fVar29;
        if (*(char *)(iVar5 + 0x1bc) != '\0') {
          local_70 = *(float *)(iVar5 + 0xec) * fVar29 + *(float *)(iVar5 + 0xf0) * local_6c +
                     *(float *)(iVar5 + 0xf4);
          local_6c = *(float *)(iVar5 + 0xf8) * fVar29 + *(float *)(iVar5 + 0xfc) * local_6c +
                     *(float *)(iVar5 + 0x100);
        }
        *(undefined4 *)(iVar5 + 0x24) = 0x1ff;
        iVar5 = FUN_00564974(local_f4,local_f0,local_70,local_6c);
        if (iVar5 != 0) goto LAB_005671fc;
      }
      return 0;
    }
    puVar6 = (uint *)*piVar1;
    puVar6[9] = 0;
    bVar10 = *(byte *)(param_1[2] + uVar9);
    uVar12 = (uint)bVar10;
    uVar7 = uVar12 & 0x6f;
    local_fc = local_f4;
    local_f8 = local_f0;
    uVar9 = uVar9 + 1;
    bVar15 = -1 < (int)(uVar12 << 0x1b);
    bVar13 = local_c4 & 0x6f;
    if (uVar7 == 1) {
      if ((local_107 == '\x01') && (local_104 != 0)) {
        fVar29 = DAT_00565904;
        local_bc = DAT_00565904;
        if (local_108 == '\0') {
          fVar29 = local_cc;
          local_bc = local_c8;
        }
        local_c0 = fVar29;
        if ((char)puVar6[0x6f] != '\0') {
          local_c0 = (float)puVar6[0x3b] * fVar29 + (float)puVar6[0x3c] * local_bc +
                     (float)puVar6[0x3d];
          local_bc = (float)puVar6[0x3e] * fVar29 + (float)puVar6[0x3f] * local_bc +
                     (float)puVar6[0x40];
        }
        puVar6[9] = 0x1ff;
        iVar2 = FUN_00564974(local_f4,local_f0,local_c0,local_bc);
        if (iVar2 != 0) goto LAB_005658d2;
      }
      local_108 = '\0';
      local_106 = 1;
      local_100 = iVar5;
      if (bVar15) {
        local_f4 = *(float *)(param_1[3] + iVar5 * 4);
        local_f0 = *(float *)(param_1[3] + (iVar5 + 1) * 4);
      }
      else {
        local_f4 = local_dc + *(float *)(param_1[3] + iVar5 * 4);
        local_f0 = local_d8 + *(float *)(param_1[3] + (iVar5 + 1) * 4);
      }
      local_104 = iVar5 + 2;
      local_cc = local_f4;
      local_c8 = local_f0;
LAB_00566188:
      local_d8 = local_f0;
      iVar5 = *piVar1;
      local_dc = local_f4;
      local_c4 = bVar10;
      if (*(char *)(iVar5 + 0x1bc) != '\0') {
        fVar29 = *(float *)(iVar5 + 0xf0) * local_f0;
        local_f0 = *(float *)(iVar5 + 0xf8) * local_f4 + *(float *)(iVar5 + 0xfc) * local_f0 +
                   *(float *)(iVar5 + 0x100);
        local_f4 = *(float *)(iVar5 + 0xec) * local_f4 + fVar29 + *(float *)(iVar5 + 0xf4);
      }
    }
    else {
      if (uVar12 == 0 || uVar12 == 0x80) {
        if (local_108 == '\x01') {
          local_f4 = 0.0;
          local_f0 = 0.0;
        }
        else {
          local_f4 = local_cc;
          local_f0 = local_c8;
        }
        local_106 = 0;
        local_107 = '\0';
        goto LAB_00566188;
      }
      if ((local_104 == 0) && (local_108 = '\x01', (char)puVar6[0x6f] != '\0')) {
        local_fc = (float)puVar6[0x3b] * local_f4 + (float)puVar6[0x3c] * local_f0 +
                   (float)puVar6[0x3d];
        local_f8 = (float)puVar6[0x3e] * local_f4 + (float)puVar6[0x3f] * local_f0 +
                   (float)puVar6[0x40];
      }
      local_106 = 0;
      if (uVar7 == 6) {
        uVar3 = param_1[3];
        local_ec = *(float *)(uVar3 + local_104 * 4);
        local_e8 = *(float *)(uVar3 + (local_104 + 1) * 4);
        local_e4 = *(float *)(uVar3 + (local_104 + 2) * 4);
        local_e0 = *(float *)(uVar3 + (local_104 + 3) * 4);
        local_104 = local_104 + 4;
        if (!bVar15) {
          local_ec = local_ec + local_dc;
          local_e8 = local_e8 + local_d8;
          local_e4 = local_e4 + local_dc;
          local_e0 = local_e0 + local_d8;
        }
LAB_00565bd0:
        local_d4 = local_e4;
        local_d0 = local_e0;
        if ((char)puVar6[0x6f] != '\0') {
          fVar29 = (float)puVar6[0x3c] * local_e8;
          local_e8 = (float)puVar6[0x3e] * local_ec + (float)puVar6[0x3f] * local_e8 +
                     (float)puVar6[0x40];
          fVar21 = (float)puVar6[0x3e] * local_e4;
          local_e4 = (float)puVar6[0x3b] * local_e4 + (float)puVar6[0x3c] * local_e0 +
                     (float)puVar6[0x3d];
          local_e0 = fVar21 + (float)puVar6[0x3f] * local_e0 + (float)puVar6[0x40];
          local_ec = (float)puVar6[0x3b] * local_ec + fVar29 + (float)puVar6[0x3d];
        }
      }
      else {
        if (uVar7 == 5) {
          local_ec = *(float *)(param_1[3] + local_104 * 4);
          local_e8 = *(float *)(param_1[3] + (local_104 + 1) * 4);
          local_104 = local_104 + 2;
          if (!bVar15) {
            local_ec = local_ec + local_dc;
            local_e8 = local_e8 + local_d8;
          }
        }
        else {
          if (uVar7 != 7) {
            if (uVar7 == 8) {
              if ((bVar13 == 5 || bVar13 == 7) || (bVar13 == 6 || bVar13 == 8)) {
                local_ec = local_dc * 2.0 - local_d4;
                local_e8 = local_d8 * 2.0 - local_d0;
              }
              else {
                local_ec = local_dc;
                local_e8 = local_d8;
              }
              local_e4 = *(float *)(param_1[3] + local_104 * 4);
              local_e0 = *(float *)(param_1[3] + (local_104 + 1) * 4);
              local_104 = local_104 + 2;
              if (!bVar15) {
                local_e4 = local_e4 + local_dc;
                local_e0 = local_e0 + local_d8;
              }
              goto LAB_00565bd0;
            }
            if ((uVar12 & 0xf) == 9) {
              uVar3 = param_1[3];
              local_ec = *(float *)(uVar3 + local_104 * 4);
              local_e8 = *(float *)(uVar3 + (local_104 + 1) * 4);
              local_e4 = *(float *)(uVar3 + (local_104 + 2) * 4);
              local_104 = local_104 + 3;
              local_d4 = local_dc;
              local_d0 = local_d8;
              local_105 = bVar10;
            }
            goto LAB_00565c84;
          }
          if ((bVar13 == 5 || bVar13 == 7) || (bVar13 == 6 || bVar13 == 8)) {
            local_ec = local_dc * 2.0 - local_d4;
            local_e8 = local_d8 * 2.0 - local_d0;
          }
          else {
            local_ec = local_dc;
            local_e8 = local_d8;
          }
        }
        local_d4 = local_ec;
        local_d0 = local_e8;
        if ((char)puVar6[0x6f] != '\0') {
          fVar29 = (float)puVar6[0x3c] * local_e8;
          local_e8 = (float)puVar6[0x3e] * local_ec + (float)puVar6[0x3f] * local_e8 +
                     (float)puVar6[0x40];
          local_ec = (float)puVar6[0x3b] * local_ec + fVar29 + (float)puVar6[0x3d];
        }
      }
LAB_00565c84:
      if (uVar7 == 4) {
        local_f4 = local_dc;
        if (bVar15) {
          local_f0 = *(float *)(param_1[3] + local_104 * 4);
LAB_00566156:
          local_104 = local_104 + 1;
        }
        else {
          iVar5 = local_104 * 4;
          local_104 = local_104 + 1;
          local_f0 = local_d8 + *(float *)(param_1[3] + iVar5);
        }
        goto LAB_00566188;
      }
      if (uVar7 == 3) {
        if (bVar15) {
          local_f4 = *(float *)(param_1[3] + local_104 * 4);
        }
        else {
          local_f4 = local_dc + *(float *)(param_1[3] + local_104 * 4);
        }
        local_104 = local_104 + 1;
        local_f0 = local_d8;
        goto LAB_00566188;
      }
      if (uVar7 == 10) {
        fVar29 = *(float *)(param_1[3] + local_104 * 4);
        local_104 = local_104 + 1;
        if (local_108 == '\x01') {
          fVar16 = (float)puVar6[0xc];
          fVar21 = local_fc;
          if ((int)((uint)(local_fc < fVar16) << 0x1f) < 0) {
            fVar21 = fVar16;
          }
          fVar23 = (float)puVar6[0xd];
          if ((int)((uint)(fVar23 < fVar21) << 0x1f) < 0) {
            fVar21 = fVar23;
          }
          fVar26 = local_f8;
          if ((int)((uint)(local_f8 < fVar16) << 0x1f) < 0) {
            fVar26 = fVar16;
          }
          if ((int)((uint)(fVar23 < fVar26) << 0x1f) < 0) {
            fVar26 = fVar23;
          }
          uVar3 = puVar6[3];
          if (puVar6[0xb] == 0) {
            if (uVar3 < *puVar6) {
              *(undefined1 *)(puVar6[7] + uVar3) = 1;
              *(int *)(*piVar1 + 0xc) = *(int *)(*piVar1 + 0xc) + 1;
            }
            else {
              puVar6[3] = uVar3 + 1;
              puVar6[10] = 2;
              puVar6[0xb] = 1;
            }
          }
          else {
            puVar6[3] = uVar3 + 1;
          }
          iVar2 = *piVar1;
          iVar5 = *(int *)(iVar2 + 8);
          if (*(int *)(iVar2 + 0x2c) == 0) {
            uVar3 = iVar5 + 1;
            if (uVar3 < *(uint *)(iVar2 + 4)) {
              iVar8 = *(int *)(iVar2 + 0x10);
              *(float *)(iVar8 + iVar5 * 4) = fVar21;
              *(uint *)(iVar2 + 8) = uVar3;
              *(float *)(iVar8 + uVar3 * 4) = fVar26;
              *(int *)(iVar2 + 8) = iVar5 + 2;
            }
            else {
              *(int *)(iVar2 + 8) = iVar5 + 2;
              *(undefined4 *)(iVar2 + 0x28) = 2;
              *(undefined4 *)(iVar2 + 0x2c) = 1;
            }
          }
          else {
            *(int *)(iVar2 + 8) = iVar5 + 2;
          }
          local_108 = '\0';
        }
        iVar5 = (int)fVar29 / 2;
        if (0 < iVar5) {
          do {
            if (bVar15) {
              local_f4 = *(float *)(param_1[3] + local_104 * 4);
              local_f0 = *(float *)(param_1[3] + (local_104 + 1) * 4);
            }
            else {
              local_f4 = *(float *)(param_1[3] + local_104 * 4) + local_dc;
              local_f0 = *(float *)(param_1[3] + (local_104 + 1) * 4) + local_d8;
            }
            local_104 = local_104 + 2;
            local_d8 = local_f0;
            iVar2 = *piVar1;
            local_dc = local_f4;
            if (*(char *)(iVar2 + 0x1bc) != '\0') {
              fVar29 = *(float *)(iVar2 + 0xf0) * local_f0;
              local_f0 = *(float *)(iVar2 + 0xf8) * local_f4 + *(float *)(iVar2 + 0xfc) * local_f0 +
                         *(float *)(iVar2 + 0x100);
              local_f4 = *(float *)(iVar2 + 0xec) * local_f4 + fVar29 + *(float *)(iVar2 + 0xf4);
            }
            local_c4 = bVar10;
            iVar2 = FUN_00564974(local_fc,local_f8,local_f4,local_f0);
            if (iVar2 != 0) goto LAB_005658d2;
            local_fc = local_f4;
            local_f8 = local_f0;
            iVar5 = iVar5 + -1;
          } while (iVar5 != 0);
        }
        fVar16 = local_f0;
        fVar21 = local_f4;
        fVar29 = local_dc - local_cc;
        bVar15 = fVar29 == 0.0;
        if (bVar15) {
          fVar29 = local_d8 - local_c8;
        }
        if (!bVar15 || (!bVar15 || fVar29 != 0.0)) {
          local_f0 = local_c8;
          local_fc = local_f4;
          local_f8 = fVar16;
          local_f4 = local_cc;
          local_d8 = local_c8;
          iVar5 = *piVar1;
          local_dc = local_cc;
          if (*(char *)(iVar5 + 0x1bc) != '\0') {
            local_f4 = *(float *)(iVar5 + 0xec) * local_cc + *(float *)(iVar5 + 0xf0) * local_c8 +
                       *(float *)(iVar5 + 0xf4);
            local_f0 = *(float *)(iVar5 + 0xf8) * local_cc + *(float *)(iVar5 + 0xfc) * local_c8 +
                       *(float *)(iVar5 + 0x100);
          }
          iVar2 = FUN_00564974(fVar21,fVar16,local_f4,local_f0);
          if (iVar2 != 0) {
LAB_005658d2:
            FUN_0051778c(0);
            FUN_00517796(0);
            FUN_0051565c(iVar2);
            FUN_0051778c(0);
            FUN_00517796(0);
            FUN_0051565c(iVar2);
            return iVar2;
          }
        }
        local_107 = '\0';
      }
      else {
        if (uVar7 != 0xb) {
          if (bVar15) {
            local_f4 = *(float *)(param_1[3] + local_104 * 4);
            local_104 = local_104 + 1;
            local_f0 = *(float *)(param_1[3] + local_104 * 4);
            goto LAB_00566156;
          }
          local_f4 = *(float *)(param_1[3] + local_104 * 4) + local_dc;
          local_f0 = *(float *)(param_1[3] + (local_104 + 1) * 4) + local_d8;
          local_104 = local_104 + 2;
          goto LAB_00566188;
        }
        iVar5 = local_104 * 4;
        local_104 = local_104 + 1;
        fVar29 = *(float *)(param_1[3] + iVar5);
        if (local_108 == '\x01') {
          fVar21 = (float)puVar6[0xc];
          fVar16 = local_fc;
          if ((int)((uint)(local_fc < fVar21) << 0x1f) < 0) {
            fVar16 = fVar21;
          }
          fVar23 = (float)puVar6[0xd];
          if ((int)((uint)(fVar23 < fVar16) << 0x1f) < 0) {
            fVar16 = fVar23;
          }
          if (-1 < (int)((uint)(local_f8 < fVar21) << 0x1f)) {
            fVar21 = local_f8;
          }
          if ((int)((uint)(fVar23 < fVar21) << 0x1f) < 0) {
            fVar21 = fVar23;
          }
          uVar3 = puVar6[3];
          if (puVar6[0xb] == 0) {
            if (uVar3 < *puVar6) {
              *(undefined1 *)(puVar6[7] + uVar3) = 1;
              *(int *)(*piVar1 + 0xc) = *(int *)(*piVar1 + 0xc) + 1;
            }
            else {
              puVar6[3] = uVar3 + 1;
              puVar6[10] = 2;
              puVar6[0xb] = 1;
            }
          }
          else {
            puVar6[3] = uVar3 + 1;
          }
          iVar2 = *piVar1;
          iVar5 = *(int *)(iVar2 + 8);
          if (*(int *)(iVar2 + 0x2c) == 0) {
            uVar3 = iVar5 + 1;
            if (uVar3 < *(uint *)(iVar2 + 4)) {
              iVar8 = *(int *)(iVar2 + 0x10);
              *(float *)(iVar8 + iVar5 * 4) = fVar16;
              *(uint *)(iVar2 + 8) = uVar3;
              *(float *)(iVar8 + uVar3 * 4) = fVar21;
              *(int *)(iVar2 + 8) = iVar5 + 2;
            }
            else {
              *(int *)(iVar2 + 8) = iVar5 + 2;
              *(undefined4 *)(iVar2 + 0x28) = 2;
              *(undefined4 *)(iVar2 + 0x2c) = 1;
            }
          }
          else {
            *(int *)(iVar2 + 8) = iVar5 + 2;
          }
          local_108 = '\0';
        }
        iVar5 = (int)fVar29 / 2;
        if (0 < iVar5) {
          do {
            if (bVar15) {
              local_f4 = *(float *)(param_1[3] + local_104 * 4);
              local_f0 = *(float *)(param_1[3] + (local_104 + 1) * 4);
            }
            else {
              local_f4 = *(float *)(param_1[3] + local_104 * 4) + local_dc;
              local_f0 = *(float *)(param_1[3] + (local_104 + 1) * 4) + local_d8;
            }
            local_104 = local_104 + 2;
            local_d8 = local_f0;
            iVar2 = *piVar1;
            local_dc = local_f4;
            if (*(char *)(iVar2 + 0x1bc) != '\0') {
              fVar29 = *(float *)(iVar2 + 0xf0) * local_f0;
              local_f0 = *(float *)(iVar2 + 0xf8) * local_f4 + *(float *)(iVar2 + 0xfc) * local_f0 +
                         *(float *)(iVar2 + 0x100);
              local_f4 = *(float *)(iVar2 + 0xec) * local_f4 + fVar29 + *(float *)(iVar2 + 0xf4);
            }
            local_c4 = bVar10;
            iVar2 = FUN_00564974(local_fc,local_f8,local_f4,local_f0);
            if (iVar2 != 0) goto LAB_005658d2;
            local_fc = local_f4;
            local_f8 = local_f0;
            iVar5 = iVar5 + -1;
          } while (iVar5 != 0);
        }
      }
    }
    fVar25 = local_d0;
    fVar26 = local_d4;
    fVar23 = local_d8;
    fVar16 = local_dc;
    fVar21 = local_f0;
    fVar29 = local_f4;
    if (local_108 == '\x01') {
      puVar6 = (uint *)*piVar1;
      fVar22 = (float)puVar6[0xc];
      fVar27 = local_fc;
      if ((int)((uint)(local_fc < fVar22) << 0x1f) < 0) {
        fVar27 = fVar22;
      }
      fVar24 = (float)puVar6[0xd];
      if ((int)((uint)(fVar24 < fVar27) << 0x1f) < 0) {
        fVar27 = fVar24;
      }
      fVar30 = local_f8;
      if ((int)((uint)(local_f8 < fVar22) << 0x1f) < 0) {
        fVar30 = fVar22;
      }
      if ((int)((uint)(fVar24 < fVar30) << 0x1f) < 0) {
        fVar30 = fVar24;
      }
      uVar3 = puVar6[3];
      if (puVar6[0xb] == 0) {
        if (uVar3 < *puVar6) {
          *(undefined1 *)(puVar6[7] + uVar3) = 1;
          *(int *)(*piVar1 + 0xc) = *(int *)(*piVar1 + 0xc) + 1;
        }
        else {
          puVar6[3] = uVar3 + 1;
          puVar6[10] = 2;
          puVar6[0xb] = 1;
        }
      }
      else {
        puVar6[3] = uVar3 + 1;
      }
      iVar2 = *piVar1;
      iVar5 = *(int *)(iVar2 + 8);
      if (*(int *)(iVar2 + 0x2c) == 0) {
        uVar3 = iVar5 + 1;
        if (uVar3 < *(uint *)(iVar2 + 4)) {
          iVar8 = *(int *)(iVar2 + 0x10);
          *(float *)(iVar8 + iVar5 * 4) = fVar27;
          *(uint *)(iVar2 + 8) = uVar3;
          *(float *)(iVar8 + uVar3 * 4) = fVar30;
          *(int *)(iVar2 + 8) = iVar5 + 2;
        }
        else {
          *(int *)(iVar2 + 8) = iVar5 + 2;
          *(undefined4 *)(iVar2 + 0x28) = 2;
          *(undefined4 *)(iVar2 + 0x2c) = 1;
        }
      }
      else {
        *(int *)(iVar2 + 8) = iVar5 + 2;
      }
      local_108 = '\0';
    }
    if (uVar7 == 5 || uVar7 == 7) {
      local_b0 = local_f4;
      local_ac = local_f0;
      iVar5 = 1;
      uVar28 = CONCAT44(local_e8,local_ec);
      local_b8 = local_fc;
      local_b4 = local_f8;
      uVar36 = CONCAT44(local_f0,local_f4);
      do {
        puVar6 = (uint *)*piVar1;
        bVar4 = false;
        fVar16 = (float)puVar6[0xd];
        bVar15 = NAN(fVar16) || NAN(local_b8);
        if (fVar16 >= local_b8) {
          bVar15 = NAN(fVar16) || NAN(local_b4);
        }
        fVar23 = (float)uVar28;
        fVar26 = (float)((ulonglong)uVar28 >> 0x20);
        fVar27 = (float)((ulonglong)uVar36 >> 0x20);
        fVar25 = (float)uVar36;
        if ((fVar16 < local_b8 || fVar16 < local_b4) == bVar15) {
          fVar22 = (float)puVar6[0xc];
          bVar15 = NAN(local_b8) || NAN(fVar22);
          if (local_b8 >= fVar22) {
            bVar15 = NAN(local_b4) || NAN(fVar22);
          }
          if ((local_b8 < fVar22 || local_b4 < fVar22) == bVar15) {
            bVar15 = NAN(fVar16) || NAN(fVar23);
            if (fVar16 >= fVar23) {
              bVar15 = NAN(fVar16) || NAN(fVar26);
            }
            if ((fVar16 < fVar23 || fVar16 < fVar26) == bVar15) {
              bVar15 = NAN(fVar23) || NAN(fVar22);
              if (fVar23 >= fVar22) {
                bVar15 = NAN(fVar26) || NAN(fVar22);
              }
              if ((fVar23 < fVar22 || fVar26 < fVar22) == bVar15) {
                bVar15 = NAN(fVar16) || NAN(fVar25);
                fVar24 = local_b8;
                if (fVar16 >= fVar25) {
                  bVar15 = NAN(fVar16) || NAN(fVar27);
                  fVar24 = fVar27;
                }
                if ((fVar16 < fVar25 || fVar16 < fVar27) == bVar15) {
                  bVar15 = NAN(fVar25) || NAN(fVar22);
                  if (fVar25 >= fVar22) {
                    bVar15 = NAN(fVar24) || NAN(fVar22);
                  }
                  if ((fVar25 < fVar22 || fVar24 < fVar22) == bVar15) {
                    bVar4 = true;
                  }
                }
              }
            }
          }
        }
        fVar22 = (float)puVar6[0xc] + DAT_00566410;
        bVar15 = NAN(local_b8) || NAN(fVar22);
        fVar16 = fVar16 + DAT_00566414;
        if (local_b8 < fVar22) {
          bVar15 = NAN(fVar23) || NAN(fVar22);
        }
        bVar14 = local_b8 < fVar22 && fVar23 < fVar22;
        if (bVar14 != bVar15) {
          bVar14 = fVar25 < fVar22;
          bVar15 = NAN(fVar25) || NAN(fVar22);
        }
        if (bVar14 == bVar15) {
          bVar15 = NAN(fVar16) || NAN(local_b8);
          if (fVar16 < local_b8) {
            bVar15 = NAN(fVar16) || NAN(fVar23);
          }
          bVar14 = fVar16 < local_b8 && fVar16 < fVar23;
          if (bVar14 != bVar15) {
            bVar14 = fVar16 < fVar25;
            bVar15 = NAN(fVar16) || NAN(fVar25);
          }
          if (bVar14 != bVar15) goto LAB_00566408;
          bVar15 = NAN(local_b4) || NAN(fVar22);
          if (local_b4 < fVar22) {
            bVar15 = NAN(fVar26) || NAN(fVar22);
          }
          bVar14 = local_b4 < fVar22 && fVar26 < fVar22;
          if (bVar14 != bVar15) {
            bVar14 = fVar27 < fVar22;
            bVar15 = NAN(fVar27) || NAN(fVar22);
          }
          if (bVar14 != bVar15) goto LAB_00566408;
          bVar15 = fVar16 < local_b4;
          bVar14 = bVar15 && (bVar15 && fVar16 < fVar26);
          if (bVar15 && (bVar15 && fVar16 < fVar26)) {
            bVar14 = fVar16 < fVar27;
          }
          if (bVar14) goto LAB_00566408;
          bVar15 = true;
        }
        else {
LAB_00566408:
          bVar15 = false;
        }
        if (bVar4) {
          if (bVar15) {
LAB_00566424:
            uVar7 = puVar6[3];
            if (puVar6[0xb] == 0) {
              if (uVar7 < *puVar6) {
                *(undefined1 *)(puVar6[7] + uVar7) = 5;
                *(int *)(*piVar1 + 0xc) = *(int *)(*piVar1 + 0xc) + 1;
              }
              else {
                puVar6[10] = 2;
                puVar6[3] = puVar6[3] + 1;
                puVar6[0xb] = 1;
              }
            }
            else {
              puVar6[3] = uVar7 + 1;
            }
            iVar8 = *piVar1;
            iVar2 = *(int *)(iVar8 + 8);
            if (*(int *)(iVar8 + 0x2c) == 0) {
              uVar12 = *(uint *)(iVar8 + 4);
              uVar7 = iVar2 + 1;
              if (uVar7 < uVar12) {
                iVar11 = *(int *)(iVar8 + 0x10);
                *(float *)(iVar11 + iVar2 * 4) = fVar23;
                *(uint *)(iVar8 + 8) = uVar7;
                *(float *)(iVar11 + uVar7 * 4) = fVar26;
                uVar7 = iVar2 + 3;
                *(int *)(iVar8 + 8) = iVar2 + 2;
                if (uVar7 < uVar12) {
                  *(float *)(iVar11 + (iVar2 + 2) * 4) = fVar25;
                  *(uint *)(iVar8 + 8) = uVar7;
                  *(float *)(iVar11 + uVar7 * 4) = fVar27;
                  *(int *)(iVar8 + 8) = iVar2 + 4;
                }
                else {
                  *(undefined4 *)(iVar8 + 0x28) = 2;
                  *(int *)(iVar8 + 8) = iVar2 + 4;
                  *(undefined4 *)(iVar8 + 0x2c) = 1;
                }
                goto LAB_005665ee;
              }
              *(int *)(iVar8 + 8) = iVar2 + 2;
              *(undefined4 *)(iVar8 + 0x28) = 2;
              *(undefined4 *)(iVar8 + 0x2c) = 1;
            }
            else {
              *(int *)(iVar8 + 8) = iVar2 + 2;
            }
            *(int *)(iVar8 + 8) = *(int *)(iVar8 + 8) + 2;
          }
          else {
LAB_00566446:
            iVar2 = FUN_00564974(local_b8,local_b4,fVar25,fVar27);
            if (iVar2 != 0) {
              FUN_0051778c(0);
              FUN_00517796(0);
              FUN_0051565c(iVar2);
              FUN_0051778c(0);
              FUN_00517796(0);
              FUN_0051565c(iVar2);
              return iVar2;
            }
          }
LAB_005665ee:
          iVar5 = iVar5 + -1;
          iVar2 = *piVar1;
          if (*(int *)(iVar2 + 700) != 0) {
            iVar8 = *(int *)(iVar2 + 700) + -1;
            *(int *)(iVar2 + 700) = iVar8;
            iVar2 = iVar2 + iVar8 * 0x18;
            local_b8 = *(float *)(iVar2 + 0x1cc);
            local_b4 = *(float *)(iVar2 + 0x1d0);
            uVar36 = *(undefined8 *)(iVar2 + 0x1dc);
            uVar28 = *(undefined8 *)(iVar2 + 0x1d4);
          }
        }
        else {
          if (!bVar15) goto LAB_00566446;
          if (9 < (int)puVar6[0xaf]) goto LAB_00566424;
          fVar22 = (local_b4 + fVar26) * 0.5;
          fVar16 = (local_b8 + fVar23) * 0.5;
          fVar25 = (fVar23 + fVar25) * 0.5;
          fVar23 = (fVar26 + fVar27) * 0.5;
          fVar26 = (fVar16 + fVar25) * 0.5;
          puVar6[puVar6[0xaf] * 6 + 0x73] = (uint)fVar26;
          fVar27 = (fVar22 + fVar23) * 0.5;
          puVar6[puVar6[0xaf] * 6 + 0x74] = (uint)fVar27;
          uVar28 = CONCAT44(fVar22,fVar16);
          puVar6[puVar6[0xaf] * 6 + 0x75] = (uint)fVar25;
          uVar36 = CONCAT44(fVar27,fVar26);
          iVar5 = iVar5 + 1;
          puVar6[puVar6[0xaf] * 6 + 0x76] = (uint)fVar23;
          puVar6[puVar6[0xaf] * 6 + 0x77] = (uint)fVar29;
          puVar6[puVar6[0xaf] * 6 + 0x78] = (uint)fVar21;
          puVar6[0xaf] = puVar6[0xaf] + 1;
        }
      } while (iVar5 != 0);
      local_b0 = (float)uVar36;
      local_ac = (float)((ulonglong)uVar36 >> 0x20);
      goto LAB_0056580e;
    }
    if (uVar7 == 6 || uVar7 == 8) {
      iVar5 = FUN_005653a0(local_fc,local_f8,local_ec,local_e8,local_e4,local_e0,local_f4,local_f0);
joined_r0x0056717a:
      if (iVar5 != 0) goto LAB_005671fc;
      goto LAB_0056580e;
    }
    if ((uVar12 & 0xf) != 9) {
      if (uVar7 == 10 || uVar7 == 0xb) goto LAB_0056580e;
      if ((uVar7 == 2 || uVar7 == 4) || uVar7 == 3) {
        iVar5 = FUN_00564974(local_fc,local_f8,local_f4,local_f0);
      }
      else {
        if (uVar7 == 1) {
          puVar6 = (uint *)*piVar1;
          fVar21 = (float)puVar6[0xc];
          if ((int)((uint)(local_f4 < fVar21) << 0x1f) < 0) {
            fVar29 = fVar21;
          }
          fVar16 = (float)puVar6[0xd];
          if ((int)((uint)(fVar16 < fVar29) << 0x1f) < 0) {
            fVar29 = fVar16;
          }
          fVar23 = local_f0;
          if ((int)((uint)(local_f0 < fVar21) << 0x1f) < 0) {
            fVar23 = fVar21;
          }
          if ((int)((uint)(fVar16 < fVar23) << 0x1f) < 0) {
            fVar23 = fVar16;
          }
          uVar7 = puVar6[3];
          if (puVar6[0xb] == 0) {
            if (uVar7 < *puVar6) {
              *(undefined1 *)(puVar6[7] + uVar7) = 1;
              *(int *)(*piVar1 + 0xc) = *(int *)(*piVar1 + 0xc) + 1;
            }
            else {
              puVar6[3] = uVar7 + 1;
              puVar6[10] = 2;
              puVar6[0xb] = 1;
            }
          }
          else {
            puVar6[3] = uVar7 + 1;
          }
          iVar5 = *piVar1;
          if (*(int *)(iVar5 + 0x2c) == 0) {
            iVar2 = *(int *)(iVar5 + 8);
            uVar7 = iVar2 + 1;
            if (*(uint *)(iVar5 + 4) <= uVar7) {
              *(int *)(iVar5 + 8) = iVar2 + 2;
              *(undefined4 *)(iVar5 + 0x28) = 2;
              *(undefined4 *)(iVar5 + 0x2c) = 1;
              goto LAB_0056580e;
            }
            iVar8 = *(int *)(iVar5 + 0x10);
            *(float *)(iVar8 + iVar2 * 4) = fVar29;
            *(uint *)(iVar5 + 8) = uVar7;
            *(float *)(iVar8 + uVar7 * 4) = fVar23;
          }
          else {
            iVar2 = *(int *)(iVar5 + 8);
          }
          *(int *)(iVar5 + 8) = iVar2 + 2;
          goto LAB_0056580e;
        }
        *(undefined4 *)(*piVar1 + 0x24) = 0x100;
        iVar5 = FUN_00564974(local_fc,local_f8,local_f4,local_f0);
      }
      goto joined_r0x0056717a;
    }
    fVar29 = ABS(local_d4);
    if (-1 < (int)((uint)(ABS(local_d4) < ABS(local_dc)) << 0x1f)) {
      fVar29 = ABS(local_dc);
    }
    fVar21 = local_d4 - local_dc;
    if ((int)((uint)(fVar21 < 0.0) << 0x1f) < 0) {
      fVar21 = local_dc - local_d4;
    }
    if (fVar21 <= fVar29 * DAT_00566998) {
      fVar29 = ABS(local_d0);
      if (-1 < (int)((uint)(ABS(local_d0) < ABS(local_d8)) << 0x1f)) {
        fVar29 = ABS(local_d8);
      }
      fVar21 = local_d0 - local_d8;
      if ((int)((uint)(fVar21 < 0.0) << 0x1f) < 0) {
        fVar21 = local_d8 - local_d0;
      }
      if (fVar21 <= fVar29 * DAT_00566998) goto LAB_0056580e;
    }
    fVar29 = (float)unaff_d10;
    fVar21 = ABS(local_ec);
    bVar15 = DAT_00566a78 <= fVar21;
    if (bVar15) {
      fVar29 = ABS(local_e8);
    }
    unaff_d10 = CONCAT44(fVar21,fVar29);
    fVar27 = local_e8;
    if (bVar15) {
      fVar27 = DAT_00566a78;
    }
    if (!bVar15 || (!bVar15 || fVar29 < fVar27)) {
      iVar5 = FUN_00564974(local_fc,local_f8,local_f4,local_f0);
      if (iVar5 != 0) goto LAB_00566cee;
      goto LAB_0056580e;
    }
    bVar13 = local_105 >> 6 & 1;
    bVar10 = bVar13;
    if ((int)((uint)local_105 << 0x1a) < 0) {
      bVar10 = bVar13 ^ 1;
    }
    fVar22 = local_e4 * DAT_00566a7c;
    fVar27 = (float)FUN_0050968c(fVar22);
    fVar22 = (float)FUN_00509690(fVar22);
    local_a8 = fVar25 * fVar27 - fVar26 * fVar22;
    fVar30 = local_a8 / fVar29;
    local_b4 = fVar23 * fVar27 - fVar16 * fVar22;
    fVar25 = fVar26 * fVar27 + fVar25 * fVar22;
    fVar31 = fVar16 * fVar27 + fVar23 * fVar22;
    fVar24 = fVar25 / fVar21;
    fVar32 = fVar31 / fVar21;
    fVar33 = local_b4 / fVar29;
    fVar26 = fVar24 + fVar32;
    fVar16 = fVar30 + fVar33;
    fVar34 = fVar24 - fVar32;
    fVar35 = fVar30 - fVar33;
    fVar23 = fVar34 * fVar34 + fVar35 * fVar35;
    if (fVar23 == 0.0) {
      iVar5 = 0x100;
      goto LAB_005671fc;
    }
    local_b8 = 1.0 / fVar23 + -0.25;
    if ((int)((uint)(local_b8 < 0.0) << 0x1f) < 0) {
      local_b8 = 0.0;
      fVar16 = (float)FUN_004397a8(fVar23 * 0.25);
      fVar29 = fVar29 * fVar16;
      fVar21 = fVar21 * fVar16;
      unaff_d10 = CONCAT44(fVar21,fVar29);
      fVar24 = fVar25 / fVar21;
      fVar30 = local_a8 / fVar29;
      fVar32 = fVar31 / fVar21;
      fVar33 = local_b4 / fVar29;
      fVar26 = fVar24 + fVar32;
      fVar16 = fVar30 + fVar33;
      fVar34 = fVar24 - fVar32;
      fVar35 = fVar30 - fVar33;
    }
    fVar21 = (float)FUN_004397a8(local_b8);
    local_b8 = fVar21 * fVar34;
    fVar31 = fVar26 * 0.5 + fVar21 * fVar35;
    fVar34 = fVar16 * 0.5 - local_b8;
    fVar23 = (float)FUN_0050969c(fVar30 - fVar34,fVar24 - fVar31);
    fVar29 = (float)FUN_0050969c(fVar33 - fVar34,fVar32 - fVar31);
    fVar23 = fVar23 * DAT_00566a80;
    fVar29 = fVar29 * DAT_00566a80;
    fVar25 = fVar29 - fVar23;
    if ((int)((uint)(fVar25 < 0.0) << 0x1f) < 0) {
      fVar25 = fVar25 + DAT_00566a84;
    }
    if (((-1 < (int)((uint)(fVar25 < DAT_00566a88) << 0x1f)) || (bVar10 == 0)) &&
       ((fVar25 < DAT_00566a88 || (bVar10 != 0)))) {
      fVar31 = fVar26 * 0.5 - fVar21 * fVar35;
      fVar34 = fVar16 * 0.5 + local_b8;
      fVar23 = (float)FUN_0050969c(fVar30 - fVar34,fVar24 - fVar31);
      fVar29 = (float)FUN_0050969c(fVar33 - fVar34,fVar32 - fVar31);
      fVar23 = fVar23 * DAT_00566a80;
      fVar29 = fVar29 * DAT_00566a80;
    }
    fVar16 = DAT_0056705c;
    fVar21 = DAT_00566a7c;
    fVar32 = (float)((ulonglong)unaff_d10 >> 0x20);
    fVar30 = (float)unaff_d10;
    fVar24 = fVar31 * fVar32 * fVar27 - fVar34 * fVar30 * fVar22;
    fVar25 = fVar31 * fVar32 * fVar22 + fVar34 * fVar30 * fVar27;
    fVar26 = fVar23;
    if (bVar13 == 0) {
      fVar26 = fVar29;
      fVar29 = fVar23;
    }
    if ((int)((uint)(fVar29 < fVar26) << 0x1f) < 0) {
      fVar29 = fVar29 + DAT_00566a84;
    }
    fVar23 = (local_e4 / DAT_00566a88) * DAT_00566a8c;
    if (bVar13 == 0) {
      unaff_d15 = CONCAT44(local_ac,local_b0);
      iVar5 = 1;
      while ((int)((uint)(fVar26 < fVar29) << 0x1f) < 0) {
        fVar27 = fVar29 + DAT_00567060;
        iVar2 = (uint)(fVar26 < fVar27) << 0x1f;
        fVar21 = DAT_00567060;
        if (iVar2 < 0) {
          fVar21 = fVar27;
        }
        if (-1 < iVar2) {
          fVar21 = fVar26;
        }
        if (-1 < (int)((uint)(fVar26 < fVar27) << 0x1f)) {
          iVar5 = iVar5 + 2;
        }
        fVar29 = fVar29 * fVar16;
        fVar31 = fVar21 * fVar16 - fVar29;
        fVar21 = (float)FUN_00563f40(fVar31 * 0.25);
        fVar21 = fVar21 * DAT_00567064;
        fVar22 = (float)FUN_0050968c(fVar31);
        local_a0 = (float)FUN_00509690(fVar31);
        local_94 = fVar22 + fVar21 * local_a0;
        local_90 = local_a0 - fVar21 * fVar22;
        local_ac = 1.0;
        local_a8 = 0.0;
        local_9c = 1.0;
        local_a4 = fVar22;
        local_98 = fVar21;
        uVar17 = FUN_0050968c(fVar29);
        uVar18 = FUN_00509690(fVar29);
        uVar19 = FUN_0050968c(fVar23);
        uVar20 = FUN_00509690(fVar23);
        if (iVar5 << 0x1f < 0) {
          local_ac = local_fc;
          local_a8 = local_f8;
        }
        else {
          FUN_0051a660(uVar17,uVar18,0x3f800000,0x3f800000,DAT_00567068,DAT_00567068,&local_ac);
          FUN_0051a660(uVar19,uVar20,fVar32,fVar30,fVar24,fVar25,&local_ac);
          iVar2 = *piVar1;
          if (*(char *)(iVar2 + 0x21) != '\0') {
            fVar29 = *(float *)(iVar2 + 0x3c) * local_a8;
            local_a8 = *(float *)(iVar2 + 0x44) * local_ac + *(float *)(iVar2 + 0x48) * local_a8 +
                       *(float *)(iVar2 + 0x4c);
            local_ac = *(float *)(iVar2 + 0x38) * local_ac + fVar29 + *(float *)(iVar2 + 0x40);
          }
        }
        FUN_0051a660(uVar17,uVar18,0x3f800000,0x3f800000,DAT_00567068,DAT_00567068,&local_9c);
        FUN_0051a660(uVar19,uVar20,fVar32,fVar30,fVar24,fVar25,&local_9c);
        FUN_0051a660(uVar17,uVar18,0x3f800000,0x3f800000,DAT_00567068,DAT_00567068,&local_94);
        FUN_0051a660(uVar19,uVar20,fVar32,fVar30,fVar24,fVar25,&local_94);
        if (iVar5 << 0x1e < 0) {
          local_a4 = local_f4;
          local_a0 = local_f0;
        }
        else {
          FUN_0051a660(uVar17,uVar18,0x3f800000,0x3f800000,DAT_00567068,DAT_00567068,&local_a4);
          FUN_0051a660(uVar19,uVar20,fVar32,fVar30,fVar24,fVar25,&local_a4);
          iVar5 = *piVar1;
          if (*(char *)(iVar5 + 0x21) != '\0') {
            fVar29 = *(float *)(iVar5 + 0x3c) * local_a0;
            local_a0 = *(float *)(iVar5 + 0x44) * local_a4 + *(float *)(iVar5 + 0x48) * local_a0 +
                       *(float *)(iVar5 + 0x4c);
            local_a4 = *(float *)(iVar5 + 0x38) * local_a4 + fVar29 + *(float *)(iVar5 + 0x40);
          }
        }
        iVar5 = *piVar1;
        if (*(char *)(iVar5 + 0x21) != '\0') {
          fVar29 = *(float *)(iVar5 + 0x3c) * local_98;
          local_98 = *(float *)(iVar5 + 0x44) * local_9c + *(float *)(iVar5 + 0x48) * local_98 +
                     *(float *)(iVar5 + 0x4c);
          fVar21 = *(float *)(iVar5 + 0x3c) * local_90;
          local_90 = *(float *)(iVar5 + 0x44) * local_94 + *(float *)(iVar5 + 0x48) * local_90 +
                     *(float *)(iVar5 + 0x4c);
          local_9c = *(float *)(iVar5 + 0x38) * local_9c + fVar29 + *(float *)(iVar5 + 0x40);
          local_94 = *(float *)(iVar5 + 0x38) * local_94 + fVar21 + *(float *)(iVar5 + 0x40);
        }
        iVar5 = FUN_005653a0(local_ac,local_a8,local_9c,local_98,local_94,local_90,local_a4,local_a0
                            );
        if (iVar5 != 0) goto LAB_00566cdc;
        iVar5 = 0;
        fVar29 = fVar27;
      }
    }
    else {
      unaff_d15 = CONCAT44(local_ac,local_b0);
      iVar5 = 1;
      while ((int)((uint)(fVar26 < fVar29) << 0x1f) < 0) {
        fVar27 = fVar26 + DAT_00566d24;
        iVar2 = (uint)(fVar27 < fVar29) << 0x1f;
        fVar16 = DAT_00566d24;
        if (iVar2 < 0) {
          fVar16 = fVar27;
        }
        if (-1 < iVar2) {
          fVar16 = fVar29;
        }
        if (-1 < (int)((uint)(fVar27 < fVar29) << 0x1f)) {
          iVar5 = iVar5 + 2;
        }
        fVar26 = fVar26 * fVar21;
        fVar31 = fVar16 * fVar21 - fVar26;
        fVar16 = (float)FUN_00563f40(fVar31 * 0.25);
        fVar16 = fVar16 * DAT_00566d28;
        fVar22 = (float)FUN_0050968c(fVar31);
        local_a0 = (float)FUN_00509690(fVar31);
        local_94 = fVar22 + fVar16 * local_a0;
        local_90 = local_a0 - fVar16 * fVar22;
        local_ac = 1.0;
        local_a8 = 0.0;
        local_9c = 1.0;
        local_a4 = fVar22;
        local_98 = fVar16;
        uVar17 = FUN_0050968c(fVar26);
        uVar18 = FUN_00509690(fVar26);
        uVar19 = FUN_0050968c(fVar23);
        uVar20 = FUN_00509690(fVar23);
        if (iVar5 << 0x1f < 0) {
          local_ac = local_fc;
          local_a8 = local_f8;
        }
        else {
          FUN_0051a660(uVar17,uVar18,0x3f800000,0x3f800000,DAT_00566e08,DAT_00566e08,&local_ac);
          FUN_0051a660(uVar19,uVar20,fVar32,fVar30,fVar24,fVar25,&local_ac);
          iVar2 = *piVar1;
          if (*(char *)(iVar2 + 0x21) != '\0') {
            fVar16 = *(float *)(iVar2 + 0x3c) * local_a8;
            local_a8 = *(float *)(iVar2 + 0x44) * local_ac + *(float *)(iVar2 + 0x48) * local_a8 +
                       *(float *)(iVar2 + 0x4c);
            local_ac = *(float *)(iVar2 + 0x38) * local_ac + fVar16 + *(float *)(iVar2 + 0x40);
          }
        }
        FUN_0051a660(uVar17,uVar18,0x3f800000,0x3f800000,DAT_00566e08,DAT_00566e08,&local_9c);
        FUN_0051a660(uVar19,uVar20,fVar32,fVar30,fVar24,fVar25,&local_9c);
        FUN_0051a660(uVar17,uVar18,0x3f800000,0x3f800000,DAT_00566e08,DAT_00566e08,&local_94);
        FUN_0051a660(uVar19,uVar20,fVar32,fVar30,fVar24,fVar25,&local_94);
        if (iVar5 << 0x1e < 0) {
          local_a4 = local_f4;
          local_a0 = local_f0;
        }
        else {
          FUN_0051a660(uVar17,uVar18,0x3f800000,0x3f800000,DAT_00566e08,DAT_00566e08,&local_a4);
          FUN_0051a660(uVar19,uVar20,fVar32,fVar30,fVar24,fVar25,&local_a4);
          iVar5 = *piVar1;
          if (*(char *)(iVar5 + 0x21) != '\0') {
            fVar16 = *(float *)(iVar5 + 0x3c) * local_a0;
            local_a0 = *(float *)(iVar5 + 0x44) * local_a4 + *(float *)(iVar5 + 0x48) * local_a0 +
                       *(float *)(iVar5 + 0x4c);
            local_a4 = *(float *)(iVar5 + 0x38) * local_a4 + fVar16 + *(float *)(iVar5 + 0x40);
          }
        }
        iVar5 = *piVar1;
        if (*(char *)(iVar5 + 0x21) != '\0') {
          fVar16 = *(float *)(iVar5 + 0x3c) * local_98;
          local_98 = *(float *)(iVar5 + 0x44) * local_9c + *(float *)(iVar5 + 0x48) * local_98 +
                     *(float *)(iVar5 + 0x4c);
          fVar26 = *(float *)(iVar5 + 0x3c) * local_90;
          local_90 = *(float *)(iVar5 + 0x44) * local_94 + *(float *)(iVar5 + 0x48) * local_90 +
                     *(float *)(iVar5 + 0x4c);
          local_9c = *(float *)(iVar5 + 0x38) * local_9c + fVar16 + *(float *)(iVar5 + 0x40);
          local_94 = *(float *)(iVar5 + 0x38) * local_94 + fVar26 + *(float *)(iVar5 + 0x40);
        }
        iVar5 = FUN_005653a0(local_ac,local_a8,local_9c,local_98,local_94,local_90,local_a4,local_a0
                            );
        if (iVar5 != 0) goto LAB_00566cdc;
        iVar5 = 0;
        fVar26 = fVar27;
      }
    }
  } while( true );
LAB_00566cdc:
  FUN_0051778c(0);
  FUN_00517796(0);
  FUN_0051565c(iVar5);
LAB_00566cee:
  FUN_0051778c(0);
  FUN_00517796(0);
  FUN_0051565c(iVar5);
LAB_005671fc:
  FUN_0051778c(0);
  FUN_00517796(0);
  FUN_0051565c(iVar5);
  return iVar5;
}

