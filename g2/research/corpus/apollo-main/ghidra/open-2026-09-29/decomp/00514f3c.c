
/* WARNING: Instruction at (ram,0x00562a56) overlaps instruction at (ram,0x00562a54)
    */

void FUN_00514f3c(uint *param_1,uint param_2,uint param_3,uint param_4,uint param_5)

{
  int iVar1;
  uint extraout_r1;
  uint uVar2;
  float *pfVar3;
  uint uVar4;
  uint uVar5;
  int iVar6;
  float *pfVar7;
  float *pfVar8;
  float *pfVar9;
  float *pfVar10;
  float *pfVar11;
  byte bVar12;
  bool bVar13;
  byte bVar14;
  bool bVar15;
  uint in_fpscr;
  float fVar16;
  float fVar17;
  float fVar18;
  float fVar19;
  float fVar20;
  float fVar21;
  float fVar22;
  float fVar23;
  float fVar24;
  float fVar25;
  ulonglong unaff_d9;
  float fVar26;
  float fVar27;
  float fVar28;
  float fVar29;
  float fVar30;
  float fVar31;
  float fVar32;
  float fVar33;
  char local_f0;
  char local_ef;
  undefined1 local_ee;
  byte local_ed;
  int local_ec;
  int local_e8;
  float local_e4;
  float local_e0;
  float local_dc;
  float local_d8;
  float local_d4;
  float local_d0;
  float local_cc;
  float local_c8;
  float local_c4;
  float local_c0;
  float local_bc;
  float local_b8;
  float local_b4;
  float local_b0;
  byte local_ac;
  float local_a8 [6];
  uint local_90;
  float local_8c [8];
  float *local_6c;
  
  if (param_1 == (uint *)0x0) {
    FUN_0051565c(1);
    return;
  }
  param_1[2] = param_3;
  param_1[3] = param_5;
  *param_1 = param_2;
  param_1[1] = param_4;
  FUN_00514e0c();
  FUN_0048949c(&local_f0,0x48);
  local_f0 = '\x01';
  local_ef = '\x01';
  uVar2 = extraout_r1;
  if (*param_1 != 0) {
    uVar2 = *(byte *)param_1[2] & 0xffffff6f;
  }
  if (*param_1 != 0 && uVar2 != 1) {
    in_fpscr = in_fpscr & 0xfffffff;
    fVar20 = (float)param_1[4];
    if (0.0 < (float)param_1[4]) {
      fVar20 = DAT_00561de8;
    }
    param_1[4] = (uint)fVar20;
    fVar20 = (float)param_1[5];
    if (0.0 < (float)param_1[5]) {
      fVar20 = DAT_00561de8;
    }
    param_1[5] = (uint)fVar20;
    fVar20 = (float)param_1[6];
    if ((float)param_1[6] < 0.0) {
      fVar20 = DAT_00561de8;
    }
    param_1[6] = (uint)fVar20;
    fVar20 = (float)param_1[7];
    if ((float)param_1[7] < 0.0) {
      fVar20 = DAT_00561de8;
    }
    param_1[7] = (uint)fVar20;
  }
  if (*param_1 != 0) {
    local_90 = 0;
    do {
      bVar12 = *(byte *)(param_1[2] + local_90);
      uVar2 = (uint)bVar12;
      local_e4 = local_dc;
      local_e0 = local_d8;
      bVar15 = (int)(uVar2 << 0x1b) < 0;
      uVar5 = uVar2 & 0x6f;
      bVar14 = local_ac & 0x6f;
      if (uVar5 == 1) {
        if ((local_ef == '\x01') && (local_ec != 0)) {
          fVar20 = DAT_00561de8;
          fVar21 = DAT_00561de8;
          if (local_f0 == '\0') {
            fVar20 = local_b4;
            fVar21 = local_b0;
          }
          in_fpscr = in_fpscr & 0xfffffff;
          fVar22 = (float)param_1[4];
          if (fVar20 < (float)param_1[4]) {
            fVar22 = fVar20;
          }
          param_1[4] = (uint)fVar22;
          fVar22 = (float)param_1[5];
          if (fVar21 < (float)param_1[5]) {
            fVar22 = fVar21;
          }
          param_1[5] = (uint)fVar22;
          if (fVar20 <= (float)param_1[6]) {
            fVar20 = (float)param_1[6];
          }
          param_1[6] = (uint)fVar20;
          if (fVar21 <= (float)param_1[7]) {
            fVar21 = (float)param_1[7];
          }
          param_1[7] = (uint)fVar21;
        }
        local_f0 = '\0';
        local_ee = 1;
        local_e8 = local_ec;
        uVar2 = param_1[3];
        local_dc = *(float *)(uVar2 + local_ec * 4);
        if (bVar15) {
          local_dc = local_c4 + local_dc;
          local_d8 = local_c0 + *(float *)(uVar2 + (local_ec + 1) * 4);
        }
        else {
          local_d8 = *(float *)(uVar2 + (local_ec + 1) * 4);
        }
        local_ec = local_ec + 2;
        local_b4 = local_dc;
        local_b0 = local_d8;
LAB_00562754:
        local_c4 = local_dc;
        local_c0 = local_d8;
        iVar6 = local_ec;
        local_ac = bVar12;
      }
      else {
        if (uVar2 == 0 || uVar2 == 0x80) {
          if (local_f0 == '\x01') {
            local_dc = 0.0;
            local_d8 = 0.0;
          }
          else {
            local_dc = local_b4;
            local_d8 = local_b0;
          }
          local_ee = 0;
          local_ef = '\0';
          goto LAB_00562754;
        }
        if (local_ec == 0) {
          local_f0 = '\x01';
        }
        local_ee = 0;
        if (uVar5 == 6) {
          uVar2 = param_1[3];
          local_d4 = *(float *)(uVar2 + local_ec * 4);
          local_d0 = *(float *)(uVar2 + (local_ec + 1) * 4);
          local_cc = *(float *)(uVar2 + (local_ec + 2) * 4);
          local_c8 = *(float *)(uVar2 + (local_ec + 3) * 4);
          local_ec = local_ec + 4;
          if (bVar15) {
            local_d4 = local_d4 + local_c4;
            local_d0 = local_d0 + local_c0;
            local_cc = local_cc + local_c4;
            local_c8 = local_c8 + local_c0;
            local_bc = local_cc;
            local_b8 = local_c8;
            goto LAB_00561f3e;
          }
LAB_00562014:
          local_bc = local_cc;
          local_b8 = local_c8;
LAB_00561edc:
          uVar2 = param_1[3];
          local_dc = *(float *)(uVar2 + local_ec * 4);
          local_ec = local_ec + 1;
LAB_005620a8:
          local_d8 = *(float *)(uVar2 + local_ec * 4);
          local_ec = local_ec + 1;
          goto LAB_00562754;
        }
        if (uVar5 == 5) {
          local_d4 = *(float *)(param_1[3] + local_ec * 4);
          local_d0 = *(float *)(param_1[3] + (local_ec + 1) * 4);
          local_ec = local_ec + 2;
          local_bc = local_d4;
          local_b8 = local_d0;
          if (!bVar15) goto LAB_00561edc;
          local_d4 = local_d4 + local_c4;
          local_d0 = local_d0 + local_c0;
          local_bc = local_d4;
          local_b8 = local_d0;
LAB_00561f3e:
          local_dc = *(float *)(param_1[3] + local_ec * 4) + local_c4;
          local_d8 = *(float *)(param_1[3] + (local_ec + 1) * 4) + local_c0;
          local_ec = local_ec + 2;
          goto LAB_00562754;
        }
        if (uVar5 == 7) {
          if ((bVar14 == 5 || bVar14 == 7) ||
             (local_d4 = local_c4, local_d0 = local_c0, fVar20 = local_c4, fVar21 = local_c0,
             bVar14 == 6 || bVar14 == 8)) {
            local_d4 = local_c4 * 2.0 - local_bc;
            local_d0 = local_c0 * 2.0 - local_b8;
            fVar20 = local_d4;
            fVar21 = local_d0;
          }
LAB_00561f3a:
          local_b8 = fVar21;
          local_bc = fVar20;
          if (!bVar15) goto LAB_00561edc;
          goto LAB_00561f3e;
        }
        if (uVar5 == 8) {
          if ((bVar14 == 5 || bVar14 == 7) || (bVar14 == 6 || bVar14 == 8)) {
            local_d4 = local_c4 * 2.0 - local_bc;
            local_d0 = local_c0 * 2.0 - local_b8;
          }
          else {
            local_d4 = local_c4;
            local_d0 = local_c0;
          }
          local_cc = *(float *)(param_1[3] + local_ec * 4);
          local_c8 = *(float *)(param_1[3] + (local_ec + 1) * 4);
          local_ec = local_ec + 2;
          if (!bVar15) goto LAB_00562014;
          local_cc = local_cc + local_c4;
          local_c8 = local_c8 + local_c0;
          local_bc = local_cc;
          local_b8 = local_c8;
          goto LAB_00561f3e;
        }
        if ((uVar2 & 0xf) == 9) {
          uVar2 = param_1[3];
          local_d4 = *(float *)(uVar2 + local_ec * 4);
          local_d0 = *(float *)(uVar2 + (local_ec + 1) * 4);
          local_cc = *(float *)(uVar2 + (local_ec + 2) * 4);
          local_ec = local_ec + 3;
          local_b8 = local_c0;
          local_bc = local_c4;
          local_ed = bVar12;
        }
        if (uVar5 == 4) {
          uVar2 = param_1[3];
          local_dc = local_c4;
          if (!bVar15) goto LAB_005620a8;
          iVar6 = local_ec * 4;
          local_ec = local_ec + 1;
          local_d8 = local_c0 + *(float *)(uVar2 + iVar6);
          goto LAB_00562754;
        }
        if (uVar5 == 3) {
          local_dc = *(float *)(param_1[3] + local_ec * 4);
          if (bVar15) {
            local_dc = local_c4 + local_dc;
          }
          local_ec = local_ec + 1;
          local_d8 = local_c0;
          goto LAB_00562754;
        }
        if (uVar5 == 10) {
          iVar6 = local_ec + 1;
          fVar21 = *(float *)(param_1[3] + local_ec * 4);
          uVar2 = in_fpscr & 0xfffffff;
          fVar20 = (float)param_1[4];
          if (local_dc < (float)param_1[4]) {
            fVar20 = local_dc;
          }
          param_1[4] = (uint)fVar20;
          fVar20 = (float)param_1[5];
          if (local_d8 < (float)param_1[5]) {
            fVar20 = local_d8;
          }
          param_1[5] = (uint)fVar20;
          fVar20 = local_dc;
          if (local_dc <= (float)param_1[6]) {
            fVar20 = (float)param_1[6];
          }
          param_1[6] = (uint)fVar20;
          fVar20 = local_d8;
          if (local_d8 <= (float)param_1[7]) {
            fVar20 = (float)param_1[7];
          }
          param_1[7] = (uint)fVar20;
          uVar5 = (int)fVar21 / 2;
          if (0 < (int)uVar5) {
            if ((int)(uVar5 << 0x1f) < 0) {
              uVar4 = param_1[3];
              local_dc = *(float *)(uVar4 + iVar6 * 4);
              if (bVar15) {
                local_dc = local_dc + local_c4;
                local_d8 = *(float *)(uVar4 + (local_ec + 2) * 4) + local_c0;
              }
              else {
                local_d8 = *(float *)(uVar4 + (local_ec + 2) * 4);
              }
              local_c4 = local_dc;
              local_c0 = local_d8;
              fVar20 = (float)param_1[4];
              if (local_dc < (float)param_1[4]) {
                fVar20 = local_dc;
              }
              param_1[4] = (uint)fVar20;
              fVar20 = (float)param_1[5];
              if (local_d8 < (float)param_1[5]) {
                fVar20 = local_d8;
              }
              param_1[5] = (uint)fVar20;
              fVar20 = local_dc;
              if (local_dc <= (float)param_1[6]) {
                fVar20 = (float)param_1[6];
              }
              param_1[6] = (uint)fVar20;
              fVar20 = local_d8;
              if (local_d8 <= (float)param_1[7]) {
                fVar20 = (float)param_1[7];
              }
              param_1[7] = (uint)fVar20;
              iVar6 = local_ec + 3;
              local_ac = bVar12;
            }
            local_ec = iVar6;
            for (uVar5 = uVar5 >> 1; iVar6 = local_ec, uVar5 != 0; uVar5 = uVar5 - 1) {
              uVar4 = param_1[3];
              local_dc = *(float *)(uVar4 + local_ec * 4);
              if (bVar15) {
                local_dc = local_dc + local_c4;
                local_d8 = *(float *)(uVar4 + (local_ec + 1) * 4) + local_c0;
              }
              else {
                local_d8 = *(float *)(uVar4 + (local_ec + 1) * 4);
              }
              fVar20 = (float)param_1[4];
              if (local_dc < (float)param_1[4]) {
                fVar20 = local_dc;
              }
              param_1[4] = (uint)fVar20;
              fVar20 = (float)param_1[5];
              if (local_d8 < (float)param_1[5]) {
                fVar20 = local_d8;
              }
              param_1[5] = (uint)fVar20;
              fVar20 = local_dc;
              if (local_dc <= (float)param_1[6]) {
                fVar20 = (float)param_1[6];
              }
              param_1[6] = (uint)fVar20;
              fVar20 = local_d8;
              if (local_d8 <= (float)param_1[7]) {
                fVar20 = (float)param_1[7];
              }
              param_1[7] = (uint)fVar20;
              uVar4 = param_1[3];
              fVar20 = *(float *)(uVar4 + (local_ec + 2) * 4);
              if (bVar15) {
                local_d8 = *(float *)(uVar4 + (local_ec + 3) * 4) + local_d8;
                local_dc = fVar20 + local_dc;
              }
              else {
                local_d8 = *(float *)(uVar4 + (local_ec + 3) * 4);
                local_dc = fVar20;
              }
              local_ec = local_ec + 4;
              fVar20 = (float)param_1[4];
              if (local_dc < (float)param_1[4]) {
                fVar20 = local_dc;
              }
              param_1[4] = (uint)fVar20;
              fVar20 = (float)param_1[5];
              if (local_d8 < (float)param_1[5]) {
                fVar20 = local_d8;
              }
              param_1[5] = (uint)fVar20;
              fVar20 = local_dc;
              if (local_dc <= (float)param_1[6]) {
                fVar20 = (float)param_1[6];
              }
              param_1[6] = (uint)fVar20;
              fVar20 = local_d8;
              if (local_d8 <= (float)param_1[7]) {
                fVar20 = (float)param_1[7];
              }
              param_1[7] = (uint)fVar20;
              local_c4 = local_dc;
              local_c0 = local_d8;
              local_ac = bVar12;
            }
          }
          local_ec = iVar6;
          in_fpscr = uVar2 | (uint)(local_c4 - local_b4 == 0.0) << 0x1e;
          bVar12 = 0;
          if ((byte)(in_fpscr >> 0x1e) != 0) {
            in_fpscr = uVar2 | (uint)(local_c0 - local_b0 == 0.0) << 0x1e;
            bVar12 = (byte)(in_fpscr >> 0x1e);
          }
          local_e4 = local_dc;
          local_e0 = local_d8;
          if (bVar12 == 0) {
            local_d8 = local_b0;
            local_dc = local_b4;
            local_c4 = local_b4;
            local_c0 = local_b0;
            in_fpscr = in_fpscr & 0xfffffff;
            fVar20 = (float)param_1[4];
            if (local_b4 < (float)param_1[4]) {
              fVar20 = local_b4;
            }
            param_1[4] = (uint)fVar20;
            fVar20 = (float)param_1[5];
            if (local_b0 < (float)param_1[5]) {
              fVar20 = local_b0;
            }
            param_1[5] = (uint)fVar20;
            fVar20 = local_b4;
            if (local_b4 <= (float)param_1[6]) {
              fVar20 = (float)param_1[6];
            }
            param_1[6] = (uint)fVar20;
            fVar20 = local_b0;
            if (local_b0 <= (float)param_1[7]) {
              fVar20 = (float)param_1[7];
            }
            param_1[7] = (uint)fVar20;
          }
          local_ef = '\0';
          iVar6 = local_ec;
        }
        else {
          fVar20 = local_bc;
          fVar21 = local_b8;
          if (uVar5 != 0xb) goto LAB_00561f3a;
          iVar6 = local_ec + 1;
          fVar21 = *(float *)(param_1[3] + local_ec * 4);
          in_fpscr = in_fpscr & 0xfffffff;
          fVar20 = (float)param_1[4];
          if (local_dc < (float)param_1[4]) {
            fVar20 = local_dc;
          }
          param_1[4] = (uint)fVar20;
          fVar20 = (float)param_1[5];
          if (local_d8 < (float)param_1[5]) {
            fVar20 = local_d8;
          }
          param_1[5] = (uint)fVar20;
          fVar20 = local_dc;
          if (local_dc <= (float)param_1[6]) {
            fVar20 = (float)param_1[6];
          }
          param_1[6] = (uint)fVar20;
          fVar20 = local_d8;
          if (local_d8 <= (float)param_1[7]) {
            fVar20 = (float)param_1[7];
          }
          param_1[7] = (uint)fVar20;
          uVar2 = (int)fVar21 / 2;
          if (0 < (int)uVar2) {
            if ((int)(uVar2 << 0x1f) < 0) {
              uVar5 = param_1[3];
              local_dc = *(float *)(uVar5 + iVar6 * 4);
              if (bVar15) {
                local_dc = local_dc + local_c4;
                local_d8 = *(float *)(uVar5 + (local_ec + 2) * 4) + local_c0;
              }
              else {
                local_d8 = *(float *)(uVar5 + (local_ec + 2) * 4);
              }
              local_c4 = local_dc;
              local_c0 = local_d8;
              fVar20 = (float)param_1[4];
              if (local_dc < (float)param_1[4]) {
                fVar20 = local_dc;
              }
              param_1[4] = (uint)fVar20;
              fVar20 = (float)param_1[5];
              if (local_d8 < (float)param_1[5]) {
                fVar20 = local_d8;
              }
              param_1[5] = (uint)fVar20;
              fVar20 = local_dc;
              if (local_dc <= (float)param_1[6]) {
                fVar20 = (float)param_1[6];
              }
              param_1[6] = (uint)fVar20;
              fVar20 = local_d8;
              if (local_d8 <= (float)param_1[7]) {
                fVar20 = (float)param_1[7];
              }
              param_1[7] = (uint)fVar20;
              iVar6 = local_ec + 3;
              local_ac = bVar12;
            }
            local_ec = iVar6;
            local_e4 = local_dc;
            local_e0 = local_d8;
            for (uVar2 = uVar2 >> 1; iVar6 = local_ec, local_dc = local_e4, local_d8 = local_e0,
                uVar2 != 0; uVar2 = uVar2 - 1) {
              uVar5 = param_1[3];
              local_dc = *(float *)(uVar5 + local_ec * 4);
              if (bVar15) {
                local_dc = local_dc + local_c4;
                local_d8 = *(float *)(uVar5 + (local_ec + 1) * 4) + local_c0;
              }
              else {
                local_d8 = *(float *)(uVar5 + (local_ec + 1) * 4);
              }
              fVar20 = (float)param_1[4];
              if (local_dc < (float)param_1[4]) {
                fVar20 = local_dc;
              }
              param_1[4] = (uint)fVar20;
              fVar20 = (float)param_1[5];
              if (local_d8 < (float)param_1[5]) {
                fVar20 = local_d8;
              }
              param_1[5] = (uint)fVar20;
              fVar20 = local_dc;
              if (local_dc <= (float)param_1[6]) {
                fVar20 = (float)param_1[6];
              }
              param_1[6] = (uint)fVar20;
              fVar20 = local_d8;
              if (local_d8 <= (float)param_1[7]) {
                fVar20 = (float)param_1[7];
              }
              param_1[7] = (uint)fVar20;
              uVar5 = param_1[3];
              fVar20 = *(float *)(uVar5 + (local_ec + 2) * 4);
              if (bVar15) {
                local_d8 = *(float *)(uVar5 + (local_ec + 3) * 4) + local_d8;
                local_dc = fVar20 + local_dc;
              }
              else {
                local_d8 = *(float *)(uVar5 + (local_ec + 3) * 4);
                local_dc = fVar20;
              }
              local_ec = local_ec + 4;
              fVar20 = (float)param_1[4];
              if (local_dc < (float)param_1[4]) {
                fVar20 = local_dc;
              }
              param_1[4] = (uint)fVar20;
              fVar20 = (float)param_1[5];
              if (local_d8 < (float)param_1[5]) {
                fVar20 = local_d8;
              }
              param_1[5] = (uint)fVar20;
              fVar20 = local_dc;
              if (local_dc <= (float)param_1[6]) {
                fVar20 = (float)param_1[6];
              }
              param_1[6] = (uint)fVar20;
              fVar20 = local_d8;
              if (local_d8 <= (float)param_1[7]) {
                fVar20 = (float)param_1[7];
              }
              param_1[7] = (uint)fVar20;
              local_e4 = local_dc;
              local_e0 = local_d8;
              local_c4 = local_dc;
              local_c0 = local_d8;
              local_ac = bVar12;
            }
          }
        }
      }
      local_ec = iVar6;
      bVar12 = *(byte *)(param_1[2] + local_90) & 0x6f;
      if (bVar12 == 6 || bVar12 == 8) {
        local_a8[0] = 0.0;
        local_a8[1] = 0.0;
        uVar2 = in_fpscr & 0xfffffff;
        fVar20 = (float)param_1[4];
        if (local_dc <= (float)param_1[4]) {
          fVar20 = local_dc;
        }
        param_1[4] = (uint)fVar20;
        fVar20 = (float)param_1[5];
        if (local_d8 <= (float)param_1[5]) {
          fVar20 = local_d8;
        }
        param_1[5] = (uint)fVar20;
        fVar20 = (float)param_1[6];
        if ((float)param_1[6] <= local_dc) {
          fVar20 = local_dc;
        }
        param_1[6] = (uint)fVar20;
        fVar20 = (float)param_1[7];
        if ((float)param_1[7] <= local_d8) {
          fVar20 = local_d8;
        }
        local_a8[2] = (float)param_1[4];
        param_1[7] = (uint)fVar20;
        fVar22 = DAT_00562948;
        fVar21 = DAT_00562944;
        fVar20 = DAT_00562940;
        local_a8[3] = (float)param_1[5];
        local_a8[4] = (float)param_1[6];
        local_a8[5] = (float)param_1[7];
        local_8c[0] = local_d4;
        uVar5 = uVar2 | (uint)(local_d4 < local_a8[2]) << 0x1f;
        in_fpscr = uVar5 | (uint)(NAN(local_d4) || NAN(local_a8[2])) << 0x1c;
        local_8c[1] = local_d0;
        local_8c[2] = local_cc;
        local_8c[3] = local_c8;
        bVar12 = (byte)(uVar5 >> 0x1f);
        bVar14 = (byte)(in_fpscr >> 0x1c) & 1;
        if (bVar12 == bVar14) {
          in_fpscr = uVar2 | (uint)(local_a8[4] < local_d4) << 0x1f |
                     (uint)(NAN(local_a8[4]) || NAN(local_d4)) << 0x1c;
          bVar14 = (byte)(in_fpscr >> 0x18);
          bVar12 = bVar14 >> 7;
          bVar14 = bVar14 >> 4 & 1;
        }
        if (bVar12 == bVar14) {
          uVar2 = in_fpscr & 0xfffffff;
          uVar5 = uVar2 | (uint)(local_d0 < local_a8[3]) << 0x1f;
          in_fpscr = uVar5 | (uint)(NAN(local_d0) || NAN(local_a8[3])) << 0x1c;
          bVar12 = (byte)(uVar5 >> 0x1f);
          bVar14 = (byte)(in_fpscr >> 0x1c) & 1;
          if (bVar12 == bVar14) {
            in_fpscr = uVar2 | (uint)(local_a8[5] < local_d0) << 0x1f |
                       (uint)(NAN(local_a8[5]) || NAN(local_d0)) << 0x1c;
            bVar14 = (byte)(in_fpscr >> 0x18);
            bVar12 = bVar14 >> 7;
            bVar14 = bVar14 >> 4 & 1;
          }
          if (bVar12 == bVar14) {
            uVar2 = in_fpscr & 0xfffffff;
            uVar5 = uVar2 | (uint)(local_cc < local_a8[2]) << 0x1f;
            in_fpscr = uVar5 | (uint)(NAN(local_cc) || NAN(local_a8[2])) << 0x1c;
            bVar12 = (byte)(uVar5 >> 0x1f);
            bVar14 = (byte)(in_fpscr >> 0x1c) & 1;
            if (bVar12 == bVar14) {
              in_fpscr = uVar2 | (uint)(local_a8[4] < local_cc) << 0x1f |
                         (uint)(NAN(local_a8[4]) || NAN(local_cc)) << 0x1c;
              bVar14 = (byte)(in_fpscr >> 0x18);
              bVar12 = bVar14 >> 7;
              bVar14 = bVar14 >> 4 & 1;
            }
            if (bVar12 == bVar14) {
              uVar2 = in_fpscr & 0xfffffff;
              uVar5 = uVar2 | (uint)(local_c8 < local_a8[3]) << 0x1f;
              in_fpscr = uVar5 | (uint)(NAN(local_c8) || NAN(local_a8[3])) << 0x1c;
              bVar12 = (byte)(uVar5 >> 0x1f);
              bVar14 = (byte)(in_fpscr >> 0x1c) & 1;
              if (bVar12 == bVar14) {
                in_fpscr = uVar2 | (uint)(local_a8[5] < local_c8) << 0x1f |
                           (uint)(NAN(local_a8[5]) || NAN(local_c8)) << 0x1c;
                bVar14 = (byte)(in_fpscr >> 0x18);
                bVar12 = bVar14 >> 7;
                bVar14 = bVar14 >> 4 & 1;
              }
              if (bVar12 == bVar14) goto LAB_0056385a;
            }
          }
        }
        local_8c[6] = local_dc;
        local_8c[7] = local_d8;
        local_8c[4] = local_e4;
        pfVar7 = local_8c + 4;
        pfVar11 = local_8c;
        local_8c[5] = local_e0;
        pfVar8 = local_8c + 2;
        pfVar9 = local_8c + 6;
        pfVar10 = local_a8 + 2;
        iVar6 = 2;
        local_6c = local_a8;
        do {
          fVar23 = *pfVar7;
          fVar26 = *pfVar11;
          fVar25 = *pfVar8;
          unaff_d9 = CONCAT44(fVar26,fVar25);
          fVar24 = *pfVar9;
          fVar28 = fVar23 * -3.0 + fVar26 * 9.0 + fVar25 * -9.0 + fVar24 * 3.0;
          uVar5 = 0;
          uVar2 = in_fpscr & 0xfffffff;
          fVar27 = fVar23 * 6.0 + fVar26 * -12.0 + fVar25 * 6.0;
          fVar19 = fVar23 * -3.0 + fVar26 * 3.0;
          if (fVar20 <= ABS(fVar28)) {
            fVar19 = fVar27 * fVar27 - fVar19 * 4.0 * fVar28;
            uVar2 = uVar2 | (uint)(fVar19 < fVar22) << 0x1f;
            in_fpscr = uVar2 | (uint)(NAN(fVar19) || NAN(fVar22)) << 0x1c;
            if ((byte)(uVar2 >> 0x1f) == ((byte)(in_fpscr >> 0x1c) & 1)) {
              fVar19 = (float)FUN_004397a8();
              fVar16 = (fVar19 - fVar27) / (fVar28 * 2.0);
              uVar2 = in_fpscr & 0xfffffff;
              if ((fVar22 <= fVar16) && (fVar16 < fVar21)) {
                local_a8[0] = fVar16;
                uVar5 = 1;
              }
              fVar19 = (-fVar27 - fVar19) / (fVar28 * 2.0);
              uVar4 = uVar2 | (uint)(fVar19 < fVar22) << 0x1f;
              in_fpscr = uVar4 | (uint)(NAN(fVar19) || NAN(fVar22)) << 0x1c;
              if (((byte)(uVar4 >> 0x1f) == ((byte)(in_fpscr >> 0x1c) & 1)) &&
                 (in_fpscr = uVar2, fVar19 < fVar21)) {
                pfVar3 = local_6c + uVar5;
                uVar5 = uVar5 + 1;
                *pfVar3 = fVar19;
              }
              if (uVar5 != 0) goto LAB_005629ce;
            }
          }
          else {
            fVar28 = ABS(fVar27);
            uVar5 = uVar2 | (uint)(fVar28 < fVar22) << 0x1f;
            in_fpscr = uVar5 | (uint)(NAN(fVar28) || NAN(fVar22)) << 0x1c;
            bVar12 = (byte)(uVar5 >> 0x1f);
            bVar14 = (byte)(in_fpscr >> 0x1c) & 1;
            if (bVar12 == bVar14) {
              fVar28 = -(fVar19 / fVar27);
              in_fpscr = uVar2 | (uint)(fVar28 < fVar22) << 0x1f |
                         (uint)(NAN(fVar28) || NAN(fVar22)) << 0x1c;
              bVar14 = (byte)(in_fpscr >> 0x18);
              bVar12 = bVar14 >> 7;
              bVar14 = bVar14 >> 4 & 1;
            }
            if ((bVar12 == bVar14) && (in_fpscr = in_fpscr & 0xfffffff, fVar28 < fVar21)) {
              local_a8[0] = fVar28;
              uVar5 = 1;
LAB_005629ce:
              iVar1 = 0;
              if ((int)(uVar5 << 0x1f) < 0) {
                fVar19 = 1.0 - local_a8[0];
                fVar19 = fVar19 * fVar19 * fVar19 * fVar23 +
                         fVar19 * 3.0 * fVar19 * local_a8[0] * fVar26 +
                         fVar19 * 3.0 * local_a8[0] * local_a8[0] * fVar25 +
                         local_a8[0] * local_a8[0] * local_a8[0] * fVar24;
                fVar27 = *pfVar10;
                if (fVar19 <= *pfVar10) {
                  fVar27 = fVar19;
                }
                *pfVar10 = fVar27;
                fVar27 = pfVar10[2];
                uVar2 = in_fpscr & 0xfffffff | (uint)(fVar19 < fVar27) << 0x1f;
                in_fpscr = uVar2 | (uint)(NAN(fVar19) || NAN(fVar27)) << 0x1c;
                if ((byte)(uVar2 >> 0x1f) != ((byte)(in_fpscr >> 0x1c) & 1)) {
                  fVar19 = fVar27;
                }
                pfVar10[2] = fVar19;
                iVar1 = 1;
              }
              if (uVar5 >> 1 != 0) {
                do {
                  fVar20 = local_a8[iVar1];
                  fVar21 = 1.0 - fVar20;
                  fVar21 = fVar21 * fVar21 * fVar21 * fVar23 +
                           fVar21 * 3.0 * fVar21 * fVar20 * fVar26 +
                           fVar21 * 3.0 * fVar20 * fVar20 * fVar25 +
                           fVar20 * fVar20 * fVar20 * fVar24;
                  fVar20 = *pfVar10;
                  if (-1 < (int)((uint)(*pfVar10 < fVar21) << 0x1f)) {
                    fVar20 = fVar21;
                  }
                  *pfVar10 = fVar20;
                  if (fVar21 < pfVar10[2]) {
                    fVar21 = pfVar10[2];
                  }
                  pfVar10[2] = fVar21;
                  fVar20 = local_a8[iVar1 + 1];
                  fVar21 = 1.0 - fVar20;
                  fVar21 = fVar21 * fVar21 * fVar21 * fVar23 +
                           fVar21 * 3.0 * fVar21 * fVar20 * fVar26 +
                           fVar21 * 3.0 * fVar20 * fVar20 * fVar25 +
                           fVar20 * fVar20 * fVar20 * fVar24;
                  fVar20 = *pfVar10;
                  if (-1 < (int)((uint)(*pfVar10 < fVar21) << 0x1f)) {
                    fVar20 = fVar21;
                  }
                  *pfVar10 = fVar20;
                  fVar20 = pfVar10[2];
                  if (pfVar10[2] <= fVar21) {
                    fVar20 = fVar21;
                  }
                  pfVar10[2] = fVar20;
                  loopEnd();
                  iVar1 = 0;
                } while( true );
              }
            }
          }
          pfVar7 = pfVar7 + 1;
          pfVar10 = pfVar10 + 1;
          pfVar9 = pfVar9 + 1;
          pfVar8 = pfVar8 + 1;
          pfVar11 = pfVar11 + 1;
          iVar6 = iVar6 + -1;
        } while (iVar6 != 0);
        param_1[4] = (uint)local_a8[2];
        param_1[5] = (uint)local_a8[3];
        param_1[6] = (uint)local_a8[4];
        param_1[7] = (uint)local_a8[5];
      }
      else if ((bVar12 == 1 || bVar12 == 2) || (bVar12 == 4 || bVar12 == 3)) {
LAB_00563802:
        in_fpscr = in_fpscr & 0xfffffff;
        fVar20 = (float)param_1[4];
        if (local_dc < (float)param_1[4]) {
          fVar20 = local_dc;
        }
        param_1[4] = (uint)fVar20;
        fVar20 = (float)param_1[5];
        if (local_d8 < (float)param_1[5]) {
          fVar20 = local_d8;
        }
        param_1[5] = (uint)fVar20;
        fVar20 = local_dc;
        if (local_dc <= (float)param_1[6]) {
          fVar20 = (float)param_1[6];
        }
        param_1[6] = (uint)fVar20;
        fVar20 = local_d8;
        if (local_d8 <= (float)param_1[7]) {
          fVar20 = (float)param_1[7];
        }
        param_1[7] = (uint)fVar20;
      }
      else if (bVar12 == 5 || bVar12 == 7) {
        uVar2 = in_fpscr & 0xfffffff;
        fVar20 = (float)param_1[4];
        if (local_dc <= (float)param_1[4]) {
          fVar20 = local_dc;
        }
        param_1[4] = (uint)fVar20;
        fVar20 = (float)param_1[5];
        if (local_d8 <= (float)param_1[5]) {
          fVar20 = local_d8;
        }
        param_1[5] = (uint)fVar20;
        fVar20 = (float)param_1[6];
        if ((float)param_1[6] <= local_dc) {
          fVar20 = local_dc;
        }
        param_1[6] = (uint)fVar20;
        fVar20 = (float)param_1[7];
        if ((float)param_1[7] <= local_d8) {
          fVar20 = local_d8;
        }
        fVar21 = (float)param_1[4];
        param_1[7] = (uint)fVar20;
        uVar5 = uVar2 | (uint)(local_d4 < fVar21) << 0x1f;
        in_fpscr = uVar5 | (uint)(NAN(local_d4) || NAN(fVar21)) << 0x1c;
        fVar20 = (float)param_1[5];
        fVar22 = (float)param_1[6];
        fVar19 = (float)param_1[7];
        bVar12 = (byte)(uVar5 >> 0x1f);
        bVar14 = (byte)(in_fpscr >> 0x1c) & 1;
        if (bVar12 == bVar14) {
          in_fpscr = uVar2 | (uint)(fVar22 < local_d4) << 0x1f |
                     (uint)(NAN(fVar22) || NAN(local_d4)) << 0x1c;
          bVar14 = (byte)(in_fpscr >> 0x18);
          bVar12 = bVar14 >> 7;
          bVar14 = bVar14 >> 4 & 1;
        }
        if (bVar12 == bVar14) {
          uVar2 = in_fpscr & 0xfffffff;
          uVar5 = uVar2 | (uint)(local_d0 < fVar20) << 0x1f;
          in_fpscr = uVar5 | (uint)(NAN(local_d0) || NAN(fVar20)) << 0x1c;
          bVar12 = (byte)(uVar5 >> 0x1f);
          bVar14 = (byte)(in_fpscr >> 0x1c) & 1;
          if (bVar12 == bVar14) {
            in_fpscr = uVar2 | (uint)(fVar19 < local_d0) << 0x1f |
                       (uint)(NAN(fVar19) || NAN(local_d0)) << 0x1c;
            bVar14 = (byte)(in_fpscr >> 0x18);
            bVar12 = bVar14 >> 7;
            bVar14 = bVar14 >> 4 & 1;
          }
          if (bVar12 == bVar14) goto LAB_0056385a;
        }
        fVar23 = local_d4 * 2.0 + local_e4 * -2.0;
        fVar24 = (local_dc * 2.0 + local_d4 * -2.0) - fVar23;
        fVar25 = ABS(fVar24);
        bVar15 = NAN(fVar25) || NAN(DAT_00562d68);
        uVar2 = in_fpscr & 0xfffffff | (uint)(fVar25 < DAT_00562d68) << 0x1f;
        bVar13 = SUB41(uVar2 >> 0x1f,0);
        if (bVar13 == bVar15) {
          fVar23 = -(fVar23 / fVar24);
          bVar15 = NAN(fVar23) || NAN(DAT_00562d68);
          uVar2 = in_fpscr & 0xfffffff | (uint)(fVar23 < DAT_00562d68) << 0x1f;
          bVar13 = SUB41(uVar2 >> 0x1f,0);
        }
        if ((bVar13 == bVar15) && (uVar2 = uVar2 & 0xfffffff, fVar23 < DAT_00562d6c)) {
          fVar24 = 1.0 - fVar23;
          fVar23 = fVar24 * fVar24 * local_e4 + fVar24 * 2.0 * fVar23 * local_d4 +
                   fVar23 * fVar23 * local_dc;
          if (fVar23 <= fVar21) {
            fVar21 = fVar23;
          }
          if (fVar22 <= fVar23) {
            fVar22 = fVar23;
          }
        }
        fVar23 = local_d0 * 2.0 + local_e0 * -2.0;
        fVar24 = (local_d8 * 2.0 + local_d0 * -2.0) - fVar23;
        fVar25 = ABS(fVar24);
        uVar5 = uVar2 & 0xfffffff | (uint)(fVar25 < DAT_00562d68) << 0x1f;
        in_fpscr = uVar5 | (uint)(NAN(fVar25) || NAN(DAT_00562d68)) << 0x1c;
        bVar12 = (byte)(uVar5 >> 0x1f);
        bVar14 = (byte)(in_fpscr >> 0x1c) & 1;
        if (bVar12 == bVar14) {
          fVar23 = -(fVar23 / fVar24);
          in_fpscr = uVar2 & 0xfffffff | (uint)(fVar23 < DAT_00562d68) << 0x1f |
                     (uint)(NAN(fVar23) || NAN(DAT_00562d68)) << 0x1c;
          bVar14 = (byte)(in_fpscr >> 0x18);
          bVar12 = bVar14 >> 7;
          bVar14 = bVar14 >> 4 & 1;
        }
        if ((bVar12 == bVar14) && (in_fpscr = in_fpscr & 0xfffffff, fVar23 < DAT_00562d6c)) {
          fVar24 = 1.0 - fVar23;
          fVar23 = fVar24 * fVar24 * local_e0 + fVar24 * 2.0 * fVar23 * local_d0 +
                   fVar23 * fVar23 * local_d8;
          if (fVar23 <= fVar20) {
            fVar20 = fVar23;
          }
          if (fVar19 <= fVar23) {
            fVar19 = fVar23;
          }
        }
        param_1[4] = (uint)fVar21;
        param_1[5] = (uint)fVar20;
        param_1[6] = (uint)fVar22;
        param_1[7] = (uint)fVar19;
      }
      else if ((*(byte *)(param_1[2] + local_90) & 0xf) == 9) {
        fVar21 = ABS(local_d4);
        uVar2 = in_fpscr & 0xfffffff;
        in_fpscr = uVar2 | (uint)(fVar21 < DAT_00562fd4) << 0x1f;
        bVar12 = -(char)((int)in_fpscr >> 0x1f);
        fVar20 = (float)unaff_d9;
        if (bVar12 == 0) {
          fVar20 = ABS(local_d0);
          unaff_d9 = (ulonglong)(uint)fVar20;
          in_fpscr = uVar2 | (uint)(fVar20 < DAT_00562fd4) << 0x1f;
          bVar12 = (byte)(in_fpscr >> 0x1f);
        }
        if (bVar12 != 0) goto LAB_00563802;
        local_a8[5] = local_cc;
        fVar25 = local_cc * DAT_00562fd8;
        local_a8[3] = local_bc;
        local_a8[2] = local_b8;
        local_a8[1] = local_c4;
        local_a8[0] = local_c0;
        local_a8[4] = (float)FUN_0050968c(fVar25);
        fVar23 = (float)FUN_00509690(fVar25);
        fVar29 = local_a8[3] * local_a8[4] + local_a8[2] * fVar23;
        fVar30 = fVar29 / fVar21;
        fVar27 = local_a8[2] * local_a8[4] - local_a8[3] * fVar23;
        fVar31 = local_a8[1] * local_a8[4] + local_a8[0] * fVar23;
        fVar28 = fVar31 / fVar21;
        fVar32 = local_a8[0] * local_a8[4] - local_a8[1] * fVar23;
        fVar22 = fVar30 + fVar28;
        fVar26 = fVar27 / fVar20;
        unaff_d9 = CONCAT44(fVar26,fVar20);
        fVar16 = fVar32 / fVar20;
        fVar19 = fVar26 + fVar16;
        fVar33 = fVar30 - fVar28;
        fVar26 = fVar26 - fVar16;
        fVar24 = fVar33 * fVar33 + fVar26 * fVar26;
        uVar2 = in_fpscr & 0xfffffff;
        in_fpscr = uVar2 | (uint)(fVar24 == 0.0) << 0x1e;
        if ((byte)(in_fpscr >> 0x1e) != 0) goto LAB_0056385a;
        local_8c[0] = 1.0 / fVar24 + -0.25;
        if (local_8c[0] < 0.0) {
          local_8c[0] = 0.0;
          fVar22 = (float)FUN_004397a8(fVar24 * 0.25);
          fVar21 = fVar21 * fVar22;
          fVar20 = fVar20 * fVar22;
          fVar30 = fVar29 / fVar21;
          fVar27 = fVar27 / fVar20;
          unaff_d9 = CONCAT44(fVar27,fVar20);
          fVar28 = fVar31 / fVar21;
          fVar22 = fVar30 + fVar28;
          fVar16 = fVar32 / fVar20;
          fVar19 = fVar27 + fVar16;
          fVar33 = fVar30 - fVar28;
          fVar26 = fVar27 - fVar16;
        }
        fVar24 = (float)FUN_004397a8(local_8c[0]);
        fVar31 = fVar22 * 0.5 + fVar24 * fVar26;
        fVar32 = fVar19 * 0.5 - fVar24 * fVar33;
        fVar27 = (float)FUN_0050969c((float)(unaff_d9 >> 0x20) - fVar32,fVar30 - fVar31);
        fVar29 = (float)unaff_d9;
        fVar28 = (float)FUN_0050969c(fVar16 - fVar32,fVar28 - fVar31);
        fVar20 = DAT_00562fec;
        fVar27 = fVar28 * DAT_00562fdc - fVar27 * DAT_00562fdc;
        if (fVar27 < 0.0) {
          fVar27 = fVar27 + DAT_00562fe0;
        }
        bVar12 = local_ed >> 6;
        bVar14 = bVar12 & 1;
        if ((int)((uint)local_ed << 0x1a) < 0) {
          bVar14 = bVar14 ^ 1;
        }
        if (((DAT_00562fe4 <= fVar27) || (bVar14 == 0)) &&
           ((fVar27 < DAT_00562fe4 || (bVar14 != 0)))) {
          fVar31 = fVar22 * 0.5 - fVar24 * fVar26;
          fVar32 = fVar19 * 0.5 + fVar24 * fVar33;
        }
        fVar22 = fVar31 * fVar21 * fVar23 + fVar32 * fVar29 * local_a8[4];
        uVar5 = uVar2 & 0xfffffff | (uint)(local_a8[5] == 0.0) << 0x1e;
        fVar19 = fVar31 * fVar21 * local_a8[4] - fVar32 * fVar29 * fVar23;
        local_a8[4] = DAT_00563958;
        bVar14 = (byte)(uVar5 >> 0x1e);
        if (bVar14 == 0) {
          uVar5 = uVar2 & 0xfffffff | (uint)(local_a8[5] == DAT_00562fe4) << 0x1e;
          bVar14 = (byte)(uVar5 >> 0x1e);
        }
        if (bVar14 == 0) {
          uVar2 = uVar5 & 0xfffffff | (uint)(local_a8[5] == DAT_00562fe8) << 0x1e;
          bVar14 = (byte)(uVar2 >> 0x1e);
          if (bVar14 == 0) {
            uVar2 = uVar5 & 0xfffffff | (uint)(local_a8[5] == DAT_00562ff0) << 0x1e;
            bVar14 = (byte)(uVar2 >> 0x1e);
          }
          fVar31 = -1.0;
          if (bVar14 == 0) {
            fVar23 = (float)FUN_00563f40(fVar25);
            fVar27 = (float)FUN_0058ec74((fVar29 * fVar23) / fVar21);
            fVar27 = -fVar27;
            fVar23 = (float)FUN_00563f40(fVar25);
            fVar28 = (float)FUN_0058ec74((fVar29 * fVar23) / fVar21);
            fVar28 = DAT_005633a4 - fVar28;
            fVar23 = (float)FUN_0050968c(fVar27);
            fVar24 = (float)FUN_0050968c(fVar25);
            fVar26 = (float)FUN_00509690(fVar27);
            fVar16 = (float)FUN_00509690(fVar25);
            fVar24 = (fVar19 + fVar21 * fVar23 * fVar24) - fVar29 * fVar26 * fVar16;
            fVar23 = (float)FUN_0050968c(fVar28);
            fVar26 = (float)FUN_0050968c(fVar25);
            fVar16 = (float)FUN_00509690(fVar28);
            fVar30 = (float)FUN_00509690(fVar25);
            fVar16 = (fVar19 + fVar21 * fVar23 * fVar26) - fVar29 * fVar16 * fVar30;
            uVar2 = uVar2 & 0xfffffff;
            fVar23 = fVar16;
            fVar26 = fVar27;
            if (fVar16 < fVar24) {
              fVar23 = fVar24;
              fVar26 = fVar28;
              fVar24 = fVar16;
              fVar28 = fVar27;
            }
            fVar27 = (float)FUN_0050968c(fVar26);
            fVar16 = (float)FUN_00509690(fVar25);
            fVar26 = (float)FUN_00509690(fVar26);
            fVar30 = (float)FUN_0050968c(fVar25);
            fVar27 = (fVar22 + fVar21 * fVar27 * fVar16 + fVar29 * fVar26 * fVar30) - fVar22;
            uVar2 = uVar2 & 0xfffffff | (uint)(fVar27 < 0.0) << 0x1f | (uint)(fVar27 == 0.0) << 0x1e
            ;
            uVar5 = uVar2 | (uint)NAN(fVar27) << 0x1c;
            fVar16 = fVar24 - fVar19;
            bVar14 = (byte)(uVar2 >> 0x18);
            fVar26 = fVar31;
            if (!(bool)(bVar14 >> 6 & 1) && bVar14 >> 7 == ((byte)(uVar5 >> 0x1c) & 1)) {
              fVar26 = 1.0;
            }
            fVar27 = (float)FUN_004397a8(fVar16 * fVar16 + fVar27 * fVar27);
            fVar27 = (float)FUN_0058ecbc(fVar16 / fVar27);
            fVar27 = (float)FUN_00577c3c(fVar20 + fVar26 * fVar27,fVar20);
            fVar26 = (float)FUN_0050968c(fVar28);
            fVar16 = (float)FUN_00509690(fVar25);
            fVar28 = (float)FUN_00509690(fVar28);
            fVar30 = (float)FUN_0050968c(fVar25);
            fVar28 = (fVar22 + fVar21 * fVar26 * fVar16 + fVar29 * fVar28 * fVar30) - fVar22;
            uVar5 = uVar5 & 0xfffffff | (uint)(fVar28 < 0.0) << 0x1f | (uint)(fVar28 == 0.0) << 0x1e
            ;
            uVar2 = uVar5 | (uint)NAN(fVar28) << 0x1c;
            fVar16 = fVar23 - fVar19;
            bVar14 = (byte)(uVar5 >> 0x18);
            fVar26 = fVar31;
            if (!(bool)(bVar14 >> 6 & 1) && bVar14 >> 7 == ((byte)(uVar2 >> 0x1c) & 1)) {
              fVar26 = 1.0;
            }
            fVar28 = (float)FUN_004397a8(fVar16 * fVar16 + fVar28 * fVar28);
            fVar28 = (float)FUN_0058ecbc(fVar16 / fVar28);
            fVar28 = (float)FUN_00577c3c(fVar20 + fVar26 * fVar28,fVar20);
            fVar26 = (float)FUN_00563f40(fVar25);
            fVar33 = (float)FUN_0058ec74(fVar29 / (fVar26 * fVar21));
            fVar26 = (float)FUN_00563f40(fVar25);
            fVar32 = (float)FUN_0058ec74(fVar29 / (fVar26 * fVar21));
            fVar32 = fVar32 + DAT_005633a4;
            fVar26 = (float)FUN_0050968c(fVar33);
            fVar16 = (float)FUN_00509690(fVar25);
            fVar30 = (float)FUN_00509690(fVar33);
            fVar17 = (float)FUN_0050968c(fVar25);
            fVar26 = fVar22 + fVar21 * fVar26 * fVar16 + fVar29 * fVar30 * fVar17;
            fVar16 = (float)FUN_0050968c(fVar32);
            fVar30 = (float)FUN_00509690(fVar25);
            fVar17 = (float)FUN_00509690(fVar32);
            fVar18 = (float)FUN_0050968c(fVar25);
            fVar17 = fVar22 + fVar21 * fVar16 * fVar30 + fVar29 * fVar17 * fVar18;
            uVar2 = uVar2 & 0xfffffff;
            fVar16 = fVar17;
            fVar30 = fVar33;
            if (fVar17 < fVar26) {
              fVar16 = fVar26;
              fVar30 = fVar32;
              fVar26 = fVar17;
              fVar32 = fVar33;
            }
            local_a8[4] = (float)FUN_0050968c(fVar30);
            fVar33 = (float)FUN_0050968c(fVar25);
            fVar30 = (float)FUN_00509690(fVar30);
            fVar17 = (float)FUN_00509690(fVar25);
            fVar18 = fVar26 - fVar22;
            uVar2 = uVar2 & 0xfffffff | (uint)(fVar18 < 0.0) << 0x1f | (uint)(fVar18 == 0.0) << 0x1e
            ;
            uVar5 = uVar2 | (uint)NAN(fVar18) << 0x1c;
            fVar33 = ((fVar19 + fVar21 * local_a8[4] * fVar33) - fVar29 * fVar30 * fVar17) - fVar19;
            bVar14 = (byte)(uVar2 >> 0x18);
            fVar30 = fVar31;
            if (!(bool)(bVar14 >> 6 & 1) && bVar14 >> 7 == ((byte)(uVar5 >> 0x1c) & 1)) {
              fVar30 = 1.0;
            }
            fVar17 = (float)FUN_004397a8(fVar33 * fVar33 + fVar18 * fVar18);
            fVar33 = (float)FUN_0058ecbc(fVar33 / fVar17);
            fVar30 = (float)FUN_00577c3c(fVar20 + fVar30 * fVar33,fVar20);
            fVar33 = (float)FUN_0050968c(fVar32);
            fVar17 = (float)FUN_0050968c(fVar25);
            fVar32 = (float)FUN_00509690(fVar32);
            fVar25 = (float)FUN_00509690(fVar25);
            fVar18 = fVar16 - fVar22;
            uVar2 = uVar5 & 0xfffffff | (uint)(fVar18 < 0.0) << 0x1f | (uint)(fVar18 == 0.0) << 0x1e
            ;
            uVar5 = uVar2 | (uint)NAN(fVar18) << 0x1c;
            fVar21 = ((fVar19 + fVar33 * fVar21 * fVar17) - fVar32 * fVar29 * fVar25) - fVar19;
            bVar14 = (byte)(uVar2 >> 0x18);
            if (!(bool)(bVar14 >> 6 & 1) && bVar14 >> 7 == ((byte)(uVar5 >> 0x1c) & 1)) {
              fVar31 = 1.0;
            }
            fVar25 = (float)FUN_004397a8(fVar21 * fVar21 + fVar18 * fVar18);
            fVar21 = (float)FUN_0058ecbc(fVar21 / fVar25);
            fVar21 = fVar20 + fVar31 * fVar21;
          }
          else {
            fVar24 = -fVar29;
            fVar23 = (float)FUN_004397a8(fVar24 * fVar24);
            fVar23 = (float)FUN_0058ecbc(fVar24 / fVar23);
            fVar27 = (float)FUN_00577c3c(fVar20 + fVar23 * -1.0,fVar20);
            fVar23 = (float)FUN_004397a8(fVar29 * fVar29);
            fVar23 = (float)FUN_0058ecbc(fVar29 / fVar23);
            fVar28 = (float)FUN_00577c3c(fVar20 + fVar23 * -1.0,fVar20);
            fVar16 = -fVar21;
            uVar2 = uVar2 & 0xfffffff | (uint)(fVar16 < 0.0) << 0x1f | (uint)(fVar16 == 0.0) << 0x1e
            ;
            uVar5 = uVar2 | (uint)NAN(fVar16) << 0x1c;
            fVar24 = fVar19 - fVar29;
            fVar23 = fVar19 + fVar29;
            fVar26 = fVar22 - fVar21;
            bVar14 = (byte)(uVar2 >> 0x18);
            fVar25 = fVar31;
            if (!(bool)(bVar14 >> 6 & 1) && bVar14 >> 7 == ((byte)(uVar5 >> 0x1c) & 1)) {
              fVar25 = 1.0;
            }
            fVar16 = (float)FUN_004397a8(fVar16 * fVar16);
            fVar16 = (float)FUN_0058ecbc(DAT_00563484 / fVar16);
            fVar30 = (float)FUN_00577c3c(fVar20 + fVar25 * fVar16,fVar20);
            uVar2 = uVar5 & 0xfffffff | (uint)(fVar21 < 0.0) << 0x1f | (uint)(fVar21 == 0.0) << 0x1e
            ;
            uVar5 = uVar2 | (uint)NAN(fVar21) << 0x1c;
            fVar16 = fVar22 + fVar21;
            bVar14 = (byte)(uVar2 >> 0x18);
            if (!(bool)(bVar14 >> 6 & 1) && bVar14 >> 7 == ((byte)(uVar5 >> 0x1c) & 1)) {
              fVar31 = 1.0;
            }
            fVar21 = (float)FUN_004397a8(fVar21 * fVar21);
            fVar21 = (float)FUN_0058ecbc(DAT_00563484 / fVar21);
            fVar21 = fVar20 + fVar31 * fVar21;
          }
        }
        else {
          fVar23 = -fVar21;
          fVar20 = (float)FUN_004397a8(fVar23 * fVar23);
          fVar20 = (float)FUN_0058ecbc(fVar23 / fVar20);
          fVar27 = (float)FUN_00577c3c(DAT_00563558 + fVar20 * -1.0,DAT_00563558);
          fVar20 = (float)FUN_004397a8(fVar21 * fVar21);
          fVar20 = (float)FUN_0058ecbc(fVar21 / fVar20);
          fVar28 = (float)FUN_00577c3c(DAT_00563558 + fVar20 * -1.0,DAT_00563558);
          fVar20 = -fVar29;
          uVar2 = uVar5 & 0xfffffff | (uint)(fVar20 < 0.0) << 0x1f | (uint)(fVar20 == 0.0) << 0x1e;
          uVar5 = uVar2 | (uint)NAN(fVar20) << 0x1c;
          fVar24 = fVar19 - fVar21;
          fVar23 = fVar19 + fVar21;
          fVar26 = fVar22 - fVar29;
          bVar14 = (byte)(uVar2 >> 0x18);
          if ((bool)(bVar14 >> 6 & 1) || bVar14 >> 7 != ((byte)(uVar5 >> 0x1c) & 1)) {
            fVar21 = -1.0;
          }
          else {
            fVar21 = 1.0;
          }
          fVar20 = (float)FUN_004397a8(fVar20 * fVar20);
          fVar25 = (float)FUN_0058ecbc(DAT_0056355c / fVar20);
          fVar20 = DAT_00563558;
          fVar30 = (float)FUN_00577c3c(DAT_00563558 + fVar21 * fVar25,DAT_00563558);
          uVar2 = uVar5 & 0xfffffff | (uint)(fVar29 < 0.0) << 0x1f | (uint)(fVar29 == 0.0) << 0x1e;
          uVar5 = uVar2 | (uint)NAN(fVar29) << 0x1c;
          fVar16 = fVar22 + fVar29;
          bVar14 = (byte)(uVar2 >> 0x18);
          if ((bool)(bVar14 >> 6 & 1) || bVar14 >> 7 != ((byte)(uVar5 >> 0x1c) & 1)) {
            fVar21 = -1.0;
          }
          else {
            fVar21 = 1.0;
          }
          fVar25 = (float)FUN_004397a8(fVar29 * fVar29);
          fVar25 = (float)FUN_0058ecbc(DAT_0056355c / fVar25);
          fVar21 = fVar20 + fVar21 * fVar25;
        }
        fVar31 = -1.0;
        fVar21 = (float)FUN_00577c3c(fVar21,fVar20);
        fVar25 = local_a8[2] - fVar22;
        uVar2 = uVar5 & 0xfffffff | (uint)(fVar25 < 0.0) << 0x1f | (uint)(fVar25 == 0.0) << 0x1e;
        uVar5 = uVar2 | (uint)NAN(fVar25) << 0x1c;
        fVar29 = local_a8[3] - fVar19;
        bVar14 = (byte)(uVar2 >> 0x18);
        fVar20 = fVar31;
        if (!(bool)(bVar14 >> 6 & 1) && bVar14 >> 7 == ((byte)(uVar5 >> 0x1c) & 1)) {
          fVar20 = 1.0;
        }
        fVar25 = (float)FUN_004397a8(fVar29 * fVar29 + fVar25 * fVar25);
        fVar29 = (float)FUN_0058ecbc(fVar29 / fVar25);
        fVar25 = DAT_00563954;
        fVar20 = (float)FUN_00577c3c(DAT_00563954 + fVar20 * fVar29,DAT_00563954);
        fVar22 = local_a8[0] - fVar22;
        uVar2 = uVar5 & 0xfffffff | (uint)(fVar22 < 0.0) << 0x1f | (uint)(fVar22 == 0.0) << 0x1e;
        in_fpscr = uVar2 | (uint)NAN(fVar22) << 0x1c;
        fVar19 = local_a8[1] - fVar19;
        unaff_d9 = CONCAT44(fVar19,fVar20);
        bVar14 = (byte)(uVar2 >> 0x18);
        if (!(bool)(bVar14 >> 6 & 1) && bVar14 >> 7 == ((byte)(in_fpscr >> 0x1c) & 1)) {
          fVar31 = 1.0;
        }
        fVar22 = (float)FUN_004397a8(fVar19 * fVar19 + fVar22 * fVar22);
        fVar22 = (float)FUN_0058ecbc(fVar19 / fVar22);
        fVar22 = (float)FUN_00577c3c(fVar25 + fVar31 * fVar22,fVar25);
        if ((bVar12 & 1) == 0) {
          unaff_d9 = (ulonglong)(uint)fVar22;
          fVar22 = fVar20;
        }
        bVar15 = false;
        fVar20 = (float)unaff_d9;
        in_fpscr = in_fpscr & 0xfffffff;
        if (fVar20 <= fVar22) {
          if (fVar27 < fVar20 || (fVar27 < fVar20 || fVar22 < fVar27)) goto LAB_0056364c;
LAB_00563680:
          bVar13 = fVar28 < (float)unaff_d9;
          if (bVar13 || (bVar13 || fVar22 < fVar28)) goto LAB_005636aa;
LAB_005636c4:
          if (bVar15) goto LAB_005636dc;
          bVar13 = fVar30 < (float)unaff_d9;
          if (bVar13 || (bVar13 || fVar22 < fVar30)) goto LAB_005636f0;
LAB_0056370c:
          bVar15 = fVar21 < (float)unaff_d9;
          if (bVar15 || (bVar15 || fVar22 < fVar21)) goto LAB_00563736;
        }
        else {
          unaff_d9 = (ulonglong)(uint)fVar22;
          bVar15 = true;
          bVar13 = fVar22 <= fVar27;
          fVar22 = fVar20;
          if (bVar13 && (bVar13 && fVar27 <= fVar20)) {
LAB_0056364c:
            fVar24 = local_a8[3];
            if (local_a8[1] <= local_a8[3]) {
              fVar24 = local_a8[1];
            }
            if (!bVar15) goto LAB_00563680;
          }
          bVar13 = (float)unaff_d9 <= fVar28;
          if (bVar13 && (bVar13 && fVar28 <= fVar22)) {
LAB_005636aa:
            fVar23 = local_a8[3];
            if (local_a8[3] <= local_a8[1]) {
              fVar23 = local_a8[1];
            }
            goto LAB_005636c4;
          }
LAB_005636dc:
          bVar13 = (float)unaff_d9 <= fVar30;
          if (bVar13 && (bVar13 && fVar30 <= fVar22)) {
LAB_005636f0:
            fVar26 = local_a8[2];
            if (local_a8[0] <= local_a8[2]) {
              fVar26 = local_a8[0];
            }
            if (!bVar15) goto LAB_0056370c;
          }
          bVar15 = (float)unaff_d9 <= fVar21;
          if (bVar15 && (bVar15 && fVar21 <= fVar22)) {
LAB_00563736:
            fVar16 = local_a8[2];
            if (local_a8[2] <= local_a8[0]) {
              fVar16 = local_a8[0];
            }
          }
        }
        fVar20 = (float)param_1[4];
        if (fVar24 < (float)param_1[4]) {
          fVar20 = fVar24;
        }
        param_1[4] = (uint)fVar20;
        fVar20 = (float)param_1[5];
        if (fVar26 < (float)param_1[5]) {
          fVar20 = fVar26;
        }
        param_1[5] = (uint)fVar20;
        fVar20 = (float)param_1[6];
        if ((float)param_1[6] < fVar24) {
          fVar20 = fVar24;
        }
        param_1[6] = (uint)fVar20;
        fVar20 = (float)param_1[7];
        if ((float)param_1[7] < fVar26) {
          fVar20 = fVar26;
        }
        param_1[7] = (uint)fVar20;
        fVar20 = (float)param_1[4];
        if (fVar23 < (float)param_1[4]) {
          fVar20 = fVar23;
        }
        param_1[4] = (uint)fVar20;
        fVar20 = (float)param_1[5];
        if (fVar16 < (float)param_1[5]) {
          fVar20 = fVar16;
        }
        param_1[5] = (uint)fVar20;
        fVar20 = (float)param_1[6];
        if ((float)param_1[6] < fVar23) {
          fVar20 = fVar23;
        }
        param_1[6] = (uint)fVar20;
        fVar20 = (float)param_1[7];
        if ((float)param_1[7] < fVar16) {
          fVar20 = fVar16;
        }
        param_1[7] = (uint)fVar20;
      }
LAB_0056385a:
      local_90 = local_90 + 1;
    } while (local_90 < *param_1);
  }
  iVar6 = (int)(float)param_1[4];
  fVar20 = (float)VectorSignedToFloat(iVar6,(byte)(in_fpscr >> 0x16) & 3);
  in_fpscr = in_fpscr & 0xfffffff;
  uVar2 = VectorSignedToFloat(iVar6 - (uint)((float)param_1[4] < fVar20),
                              (byte)(in_fpscr >> 0x16) & 3);
  param_1[4] = uVar2;
  iVar6 = (int)(float)param_1[5];
  fVar20 = (float)VectorSignedToFloat(iVar6,(byte)(in_fpscr >> 0x16) & 3);
  uVar2 = VectorSignedToFloat(iVar6 - (uint)((float)param_1[5] < fVar20),
                              (byte)(in_fpscr >> 0x16) & 3);
  param_1[5] = uVar2;
  iVar6 = (int)(float)param_1[6];
  fVar20 = (float)VectorSignedToFloat(iVar6,(byte)(in_fpscr >> 0x16) & 3);
  uVar2 = VectorSignedToFloat((uint)(fVar20 < (float)param_1[6]) + iVar6,
                              (byte)(in_fpscr >> 0x16) & 3);
  param_1[6] = uVar2;
  iVar6 = (int)(float)param_1[7];
  fVar20 = (float)VectorSignedToFloat(iVar6,(byte)(in_fpscr >> 0x16) & 3);
  uVar2 = VectorSignedToFloat((uint)(fVar20 < (float)param_1[7]) + iVar6,
                              (byte)(in_fpscr >> 0x16) & 3);
  param_1[7] = uVar2;
  param_1[0x14] = (uint)((float)param_1[6] - (float)param_1[4]);
  param_1[0x15] = (uint)((float)param_1[7] - (float)param_1[5]);
  return;
}

