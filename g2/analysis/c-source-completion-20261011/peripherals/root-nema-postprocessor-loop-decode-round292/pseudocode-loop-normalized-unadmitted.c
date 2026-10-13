
void native_path_process(uint *param_1)

{
  undefined4 uVar1;
  float *pfVar2;
  uint extraout_r1;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  int iVar6;
  float *pfVar7;
  int iVar8;
  float *pfVar9;
  float *pfVar10;
  float *pfVar11;
  float *pfVar12;
  byte bVar13;
  bool bVar14;
  byte bVar15;
  bool bVar16;
  uint in_fpscr;
  float fVar17;
  float fVar18;
  float fVar19;
  float fVar20;
  float fVar21;
  float fVar22;
  ulonglong unaff_d9;
  float fVar23;
  float fVar24;
  float fVar25;
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
  
  func_0x00514e0c();
  func_0x0048949c(&local_f0,0x48);
  local_f0 = '\x01';
  local_ef = '\x01';
  uVar3 = extraout_r1;
  if (*param_1 != 0) {
    uVar3 = *(byte *)param_1[2] & 0xffffff6f;
  }
  if (*param_1 != 0 && uVar3 != 1) {
    fVar17 = (float)param_1[4];
    in_fpscr = in_fpscr & 0xfffffff;
    if (0.0 < fVar17) {
      fVar17 = 0.0;
    }
    param_1[4] = (uint)fVar17;
    fVar17 = (float)param_1[5];
    if (0.0 < fVar17) {
      fVar17 = 0.0;
    }
    param_1[5] = (uint)fVar17;
    fVar17 = (float)param_1[6];
    if (fVar17 < 0.0) {
      fVar17 = 0.0;
    }
    param_1[6] = (uint)fVar17;
    fVar17 = (float)param_1[7];
    if (fVar17 < 0.0) {
      fVar17 = 0.0;
    }
    param_1[7] = (uint)fVar17;
  }
  if (*param_1 != 0) {
    local_90 = 0;
    do {
      bVar13 = *(byte *)(param_1[2] + local_90);
      uVar3 = (uint)bVar13;
      local_e4 = local_dc;
      local_e0 = local_d8;
      bVar16 = (int)(uVar3 << 0x1b) < 0;
      uVar5 = uVar3 & 0x6f;
      bVar15 = local_ac & 0x6f;
      if (uVar5 == 1) {
        if ((local_ef == '\x01') && (local_ec != 0)) {
          fVar17 = 0.0;
          fVar20 = 0.0;
          if (local_f0 == '\0') {
            fVar17 = local_b4;
            fVar20 = local_b0;
          }
          in_fpscr = in_fpscr & 0xfffffff;
          fVar21 = (float)param_1[4];
          if (fVar17 < (float)param_1[4]) {
            fVar21 = fVar17;
          }
          param_1[4] = (uint)fVar21;
          fVar21 = (float)param_1[5];
          if (fVar20 < (float)param_1[5]) {
            fVar21 = fVar20;
          }
          param_1[5] = (uint)fVar21;
          if (fVar17 <= (float)param_1[6]) {
            fVar17 = (float)param_1[6];
          }
          param_1[6] = (uint)fVar17;
          if (fVar20 <= (float)param_1[7]) {
            fVar20 = (float)param_1[7];
          }
          param_1[7] = (uint)fVar20;
        }
        local_f0 = '\0';
        local_ee = 1;
        local_e8 = local_ec;
        uVar3 = param_1[3];
        local_dc = *(float *)(uVar3 + local_ec * 4);
        if (bVar16) {
          local_dc = local_c4 + local_dc;
          local_d8 = local_c0 + *(float *)(uVar3 + (local_ec + 1) * 4);
        }
        else {
          local_d8 = *(float *)(uVar3 + (local_ec + 1) * 4);
        }
        local_ec = local_ec + 2;
        local_b4 = local_dc;
        local_b0 = local_d8;
LAB_00562754:
        local_c4 = local_dc;
        local_c0 = local_d8;
        iVar6 = local_ec;
        local_ac = bVar13;
      }
      else {
        if (uVar3 == 0 || uVar3 == 0x80) {
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
          uVar3 = param_1[3];
          local_d4 = *(float *)(uVar3 + local_ec * 4);
          local_d0 = *(float *)(uVar3 + (local_ec + 1) * 4);
          local_cc = *(float *)(uVar3 + (local_ec + 2) * 4);
          local_c8 = *(float *)(uVar3 + (local_ec + 3) * 4);
          local_ec = local_ec + 4;
          if (bVar16) {
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
          uVar3 = param_1[3];
          local_dc = *(float *)(uVar3 + local_ec * 4);
          local_ec = local_ec + 1;
LAB_005620a8:
          local_d8 = *(float *)(uVar3 + local_ec * 4);
          local_ec = local_ec + 1;
          goto LAB_00562754;
        }
        if (uVar5 == 5) {
          local_d4 = *(float *)(param_1[3] + local_ec * 4);
          local_d0 = *(float *)(param_1[3] + (local_ec + 1) * 4);
          local_ec = local_ec + 2;
          local_bc = local_d4;
          local_b8 = local_d0;
          if (!bVar16) goto LAB_00561edc;
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
          if ((bVar15 == 5 || bVar15 == 7) ||
             (local_d4 = local_c4, local_d0 = local_c0, fVar17 = local_c4, fVar20 = local_c0,
             bVar15 == 6 || bVar15 == 8)) {
            local_d4 = local_c4 * 2.0 - local_bc;
            local_d0 = local_c0 * 2.0 - local_b8;
            fVar17 = local_d4;
            fVar20 = local_d0;
          }
LAB_00561f3a:
          local_b8 = fVar20;
          local_bc = fVar17;
          if (!bVar16) goto LAB_00561edc;
          goto LAB_00561f3e;
        }
        if (uVar5 == 8) {
          if ((bVar15 == 5 || bVar15 == 7) || (bVar15 == 6 || bVar15 == 8)) {
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
          if (!bVar16) goto LAB_00562014;
          local_cc = local_cc + local_c4;
          local_c8 = local_c8 + local_c0;
          local_bc = local_cc;
          local_b8 = local_c8;
          goto LAB_00561f3e;
        }
        if ((uVar3 & 0xf) == 9) {
          uVar3 = param_1[3];
          local_d4 = *(float *)(uVar3 + local_ec * 4);
          local_d0 = *(float *)(uVar3 + (local_ec + 1) * 4);
          local_cc = *(float *)(uVar3 + (local_ec + 2) * 4);
          local_ec = local_ec + 3;
          local_b8 = local_c0;
          local_bc = local_c4;
          local_ed = bVar13;
        }
        if (uVar5 == 4) {
          uVar3 = param_1[3];
          local_dc = local_c4;
          if (!bVar16) goto LAB_005620a8;
          iVar6 = local_ec * 4;
          local_ec = local_ec + 1;
          local_d8 = local_c0 + *(float *)(uVar3 + iVar6);
          goto LAB_00562754;
        }
        if (uVar5 == 3) {
          local_dc = *(float *)(param_1[3] + local_ec * 4);
          if (bVar16) {
            local_dc = local_c4 + local_dc;
          }
          local_ec = local_ec + 1;
          local_d8 = local_c0;
          goto LAB_00562754;
        }
        if (uVar5 == 10) {
          iVar6 = local_ec + 1;
          fVar20 = *(float *)(param_1[3] + local_ec * 4);
          uVar3 = in_fpscr & 0xfffffff;
          fVar17 = (float)param_1[4];
          if (local_dc < (float)param_1[4]) {
            fVar17 = local_dc;
          }
          param_1[4] = (uint)fVar17;
          fVar17 = (float)param_1[5];
          if (local_d8 < (float)param_1[5]) {
            fVar17 = local_d8;
          }
          param_1[5] = (uint)fVar17;
          fVar17 = local_dc;
          if (local_dc <= (float)param_1[6]) {
            fVar17 = (float)param_1[6];
          }
          param_1[6] = (uint)fVar17;
          fVar17 = local_d8;
          if (local_d8 <= (float)param_1[7]) {
            fVar17 = (float)param_1[7];
          }
          param_1[7] = (uint)fVar17;
          uVar5 = (int)fVar20 / 2;
          if (0 < (int)uVar5) {
            if ((int)(uVar5 << 0x1f) < 0) {
              uVar4 = param_1[3];
              local_dc = *(float *)(uVar4 + iVar6 * 4);
              if (bVar16) {
                local_dc = local_dc + local_c4;
                local_d8 = *(float *)(uVar4 + (local_ec + 2) * 4) + local_c0;
              }
              else {
                local_d8 = *(float *)(uVar4 + (local_ec + 2) * 4);
              }
              local_c4 = local_dc;
              local_c0 = local_d8;
              fVar17 = (float)param_1[4];
              if (local_dc < (float)param_1[4]) {
                fVar17 = local_dc;
              }
              param_1[4] = (uint)fVar17;
              fVar17 = (float)param_1[5];
              if (local_d8 < (float)param_1[5]) {
                fVar17 = local_d8;
              }
              param_1[5] = (uint)fVar17;
              fVar17 = local_dc;
              if (local_dc <= (float)param_1[6]) {
                fVar17 = (float)param_1[6];
              }
              param_1[6] = (uint)fVar17;
              fVar17 = local_d8;
              if (local_d8 <= (float)param_1[7]) {
                fVar17 = (float)param_1[7];
              }
              param_1[7] = (uint)fVar17;
              iVar6 = local_ec + 3;
              local_ac = bVar13;
            }
            local_ec = iVar6;
            for (uVar5 = uVar5 >> 1; iVar6 = local_ec, uVar5 != 0; uVar5 = uVar5 - 1) {
              uVar4 = param_1[3];
              local_dc = *(float *)(uVar4 + local_ec * 4);
              if (bVar16) {
                local_dc = local_dc + local_c4;
                local_d8 = *(float *)(uVar4 + (local_ec + 1) * 4) + local_c0;
              }
              else {
                local_d8 = *(float *)(uVar4 + (local_ec + 1) * 4);
              }
              fVar17 = (float)param_1[4];
              if (local_dc < (float)param_1[4]) {
                fVar17 = local_dc;
              }
              param_1[4] = (uint)fVar17;
              fVar17 = (float)param_1[5];
              if (local_d8 < (float)param_1[5]) {
                fVar17 = local_d8;
              }
              param_1[5] = (uint)fVar17;
              fVar17 = local_dc;
              if (local_dc <= (float)param_1[6]) {
                fVar17 = (float)param_1[6];
              }
              param_1[6] = (uint)fVar17;
              fVar17 = local_d8;
              if (local_d8 <= (float)param_1[7]) {
                fVar17 = (float)param_1[7];
              }
              param_1[7] = (uint)fVar17;
              uVar4 = param_1[3];
              fVar17 = *(float *)(uVar4 + (local_ec + 2) * 4);
              if (bVar16) {
                local_d8 = *(float *)(uVar4 + (local_ec + 3) * 4) + local_d8;
                local_dc = fVar17 + local_dc;
              }
              else {
                local_d8 = *(float *)(uVar4 + (local_ec + 3) * 4);
                local_dc = fVar17;
              }
              local_ec = local_ec + 4;
              fVar17 = (float)param_1[4];
              if (local_dc < (float)param_1[4]) {
                fVar17 = local_dc;
              }
              param_1[4] = (uint)fVar17;
              fVar17 = (float)param_1[5];
              if (local_d8 < (float)param_1[5]) {
                fVar17 = local_d8;
              }
              param_1[5] = (uint)fVar17;
              fVar17 = local_dc;
              if (local_dc <= (float)param_1[6]) {
                fVar17 = (float)param_1[6];
              }
              param_1[6] = (uint)fVar17;
              fVar17 = local_d8;
              if (local_d8 <= (float)param_1[7]) {
                fVar17 = (float)param_1[7];
              }
              param_1[7] = (uint)fVar17;
              local_c4 = local_dc;
              local_c0 = local_d8;
              local_ac = bVar13;
            }
          }
          local_ec = iVar6;
          in_fpscr = uVar3 | (uint)(local_c4 - local_b4 == 0.0) << 0x1e;
          bVar13 = 0;
          if ((byte)(in_fpscr >> 0x1e) != 0) {
            in_fpscr = uVar3 | (uint)(local_c0 - local_b0 == 0.0) << 0x1e;
            bVar13 = (byte)(in_fpscr >> 0x1e);
          }
          local_e4 = local_dc;
          local_e0 = local_d8;
          if (bVar13 == 0) {
            local_d8 = local_b0;
            local_dc = local_b4;
            local_c4 = local_b4;
            local_c0 = local_b0;
            in_fpscr = in_fpscr & 0xfffffff;
            fVar17 = (float)param_1[4];
            if (local_b4 < (float)param_1[4]) {
              fVar17 = local_b4;
            }
            param_1[4] = (uint)fVar17;
            fVar17 = (float)param_1[5];
            if (local_b0 < (float)param_1[5]) {
              fVar17 = local_b0;
            }
            param_1[5] = (uint)fVar17;
            fVar17 = local_b4;
            if (local_b4 <= (float)param_1[6]) {
              fVar17 = (float)param_1[6];
            }
            param_1[6] = (uint)fVar17;
            fVar17 = local_b0;
            if (local_b0 <= (float)param_1[7]) {
              fVar17 = (float)param_1[7];
            }
            param_1[7] = (uint)fVar17;
          }
          local_ef = '\0';
          iVar6 = local_ec;
        }
        else {
          fVar17 = local_bc;
          fVar20 = local_b8;
          if (uVar5 != 0xb) goto LAB_00561f3a;
          iVar6 = local_ec + 1;
          fVar20 = *(float *)(param_1[3] + local_ec * 4);
          in_fpscr = in_fpscr & 0xfffffff;
          fVar17 = (float)param_1[4];
          if (local_dc < (float)param_1[4]) {
            fVar17 = local_dc;
          }
          param_1[4] = (uint)fVar17;
          fVar17 = (float)param_1[5];
          if (local_d8 < (float)param_1[5]) {
            fVar17 = local_d8;
          }
          param_1[5] = (uint)fVar17;
          fVar17 = local_dc;
          if (local_dc <= (float)param_1[6]) {
            fVar17 = (float)param_1[6];
          }
          param_1[6] = (uint)fVar17;
          fVar17 = local_d8;
          if (local_d8 <= (float)param_1[7]) {
            fVar17 = (float)param_1[7];
          }
          param_1[7] = (uint)fVar17;
          uVar3 = (int)fVar20 / 2;
          if (0 < (int)uVar3) {
            if ((int)(uVar3 << 0x1f) < 0) {
              uVar5 = param_1[3];
              local_dc = *(float *)(uVar5 + iVar6 * 4);
              if (bVar16) {
                local_dc = local_dc + local_c4;
                local_d8 = *(float *)(uVar5 + (local_ec + 2) * 4) + local_c0;
              }
              else {
                local_d8 = *(float *)(uVar5 + (local_ec + 2) * 4);
              }
              local_c4 = local_dc;
              local_c0 = local_d8;
              fVar17 = (float)param_1[4];
              if (local_dc < (float)param_1[4]) {
                fVar17 = local_dc;
              }
              param_1[4] = (uint)fVar17;
              fVar17 = (float)param_1[5];
              if (local_d8 < (float)param_1[5]) {
                fVar17 = local_d8;
              }
              param_1[5] = (uint)fVar17;
              fVar17 = local_dc;
              if (local_dc <= (float)param_1[6]) {
                fVar17 = (float)param_1[6];
              }
              param_1[6] = (uint)fVar17;
              fVar17 = local_d8;
              if (local_d8 <= (float)param_1[7]) {
                fVar17 = (float)param_1[7];
              }
              param_1[7] = (uint)fVar17;
              iVar6 = local_ec + 3;
              local_ac = bVar13;
            }
            local_ec = iVar6;
            local_e4 = local_dc;
            local_e0 = local_d8;
            for (uVar3 = uVar3 >> 1; iVar6 = local_ec, local_dc = local_e4, local_d8 = local_e0,
                uVar3 != 0; uVar3 = uVar3 - 1) {
              uVar5 = param_1[3];
              local_dc = *(float *)(uVar5 + local_ec * 4);
              if (bVar16) {
                local_dc = local_dc + local_c4;
                local_d8 = *(float *)(uVar5 + (local_ec + 1) * 4) + local_c0;
              }
              else {
                local_d8 = *(float *)(uVar5 + (local_ec + 1) * 4);
              }
              fVar17 = (float)param_1[4];
              if (local_dc < (float)param_1[4]) {
                fVar17 = local_dc;
              }
              param_1[4] = (uint)fVar17;
              fVar17 = (float)param_1[5];
              if (local_d8 < (float)param_1[5]) {
                fVar17 = local_d8;
              }
              param_1[5] = (uint)fVar17;
              fVar17 = local_dc;
              if (local_dc <= (float)param_1[6]) {
                fVar17 = (float)param_1[6];
              }
              param_1[6] = (uint)fVar17;
              fVar17 = local_d8;
              if (local_d8 <= (float)param_1[7]) {
                fVar17 = (float)param_1[7];
              }
              param_1[7] = (uint)fVar17;
              uVar5 = param_1[3];
              fVar17 = *(float *)(uVar5 + (local_ec + 2) * 4);
              if (bVar16) {
                local_d8 = *(float *)(uVar5 + (local_ec + 3) * 4) + local_d8;
                local_dc = fVar17 + local_dc;
              }
              else {
                local_d8 = *(float *)(uVar5 + (local_ec + 3) * 4);
                local_dc = fVar17;
              }
              local_ec = local_ec + 4;
              fVar17 = (float)param_1[4];
              if (local_dc < (float)param_1[4]) {
                fVar17 = local_dc;
              }
              param_1[4] = (uint)fVar17;
              fVar17 = (float)param_1[5];
              if (local_d8 < (float)param_1[5]) {
                fVar17 = local_d8;
              }
              param_1[5] = (uint)fVar17;
              fVar17 = local_dc;
              if (local_dc <= (float)param_1[6]) {
                fVar17 = (float)param_1[6];
              }
              param_1[6] = (uint)fVar17;
              fVar17 = local_d8;
              if (local_d8 <= (float)param_1[7]) {
                fVar17 = (float)param_1[7];
              }
              param_1[7] = (uint)fVar17;
              local_e4 = local_dc;
              local_e0 = local_d8;
              local_c4 = local_dc;
              local_c0 = local_d8;
              local_ac = bVar13;
            }
          }
        }
      }
      local_ec = iVar6;
      bVar13 = *(byte *)(param_1[2] + local_90) & 0x6f;
      if (bVar13 == 6 || bVar13 == 8) {
        local_a8[0] = 0.0;
        local_a8[1] = 0.0;
        uVar3 = in_fpscr & 0xfffffff;
        fVar17 = (float)param_1[4];
        if (local_dc <= (float)param_1[4]) {
          fVar17 = local_dc;
        }
        param_1[4] = (uint)fVar17;
        fVar17 = (float)param_1[5];
        if (local_d8 <= (float)param_1[5]) {
          fVar17 = local_d8;
        }
        param_1[5] = (uint)fVar17;
        fVar17 = (float)param_1[6];
        if ((float)param_1[6] <= local_dc) {
          fVar17 = local_dc;
        }
        param_1[6] = (uint)fVar17;
        fVar17 = (float)param_1[7];
        if ((float)param_1[7] <= local_d8) {
          fVar17 = local_d8;
        }
        local_a8[2] = (float)param_1[4];
        param_1[7] = (uint)fVar17;
        local_a8[3] = (float)param_1[5];
        local_a8[4] = (float)param_1[6];
        local_a8[5] = (float)param_1[7];
        local_8c[0] = local_d4;
        uVar5 = uVar3 | (uint)(local_d4 < local_a8[2]) << 0x1f;
        in_fpscr = uVar5 | (uint)(NAN(local_d4) || NAN(local_a8[2])) << 0x1c;
        local_8c[1] = local_d0;
        local_8c[2] = local_cc;
        local_8c[3] = local_c8;
        bVar13 = (byte)(uVar5 >> 0x1f);
        bVar15 = (byte)(in_fpscr >> 0x1c) & 1;
        if (bVar13 == bVar15) {
          in_fpscr = uVar3 | (uint)(local_a8[4] < local_d4) << 0x1f |
                     (uint)(NAN(local_a8[4]) || NAN(local_d4)) << 0x1c;
          bVar15 = (byte)(in_fpscr >> 0x18);
          bVar13 = bVar15 >> 7;
          bVar15 = bVar15 >> 4 & 1;
        }
        if (bVar13 == bVar15) {
          uVar3 = in_fpscr & 0xfffffff;
          uVar5 = uVar3 | (uint)(local_d0 < local_a8[3]) << 0x1f;
          in_fpscr = uVar5 | (uint)(NAN(local_d0) || NAN(local_a8[3])) << 0x1c;
          bVar13 = (byte)(uVar5 >> 0x1f);
          bVar15 = (byte)(in_fpscr >> 0x1c) & 1;
          if (bVar13 == bVar15) {
            in_fpscr = uVar3 | (uint)(local_a8[5] < local_d0) << 0x1f |
                       (uint)(NAN(local_a8[5]) || NAN(local_d0)) << 0x1c;
            bVar15 = (byte)(in_fpscr >> 0x18);
            bVar13 = bVar15 >> 7;
            bVar15 = bVar15 >> 4 & 1;
          }
          if (bVar13 == bVar15) {
            uVar3 = in_fpscr & 0xfffffff;
            uVar5 = uVar3 | (uint)(local_cc < local_a8[2]) << 0x1f;
            in_fpscr = uVar5 | (uint)(NAN(local_cc) || NAN(local_a8[2])) << 0x1c;
            bVar13 = (byte)(uVar5 >> 0x1f);
            bVar15 = (byte)(in_fpscr >> 0x1c) & 1;
            if (bVar13 == bVar15) {
              in_fpscr = uVar3 | (uint)(local_a8[4] < local_cc) << 0x1f |
                         (uint)(NAN(local_a8[4]) || NAN(local_cc)) << 0x1c;
              bVar15 = (byte)(in_fpscr >> 0x18);
              bVar13 = bVar15 >> 7;
              bVar15 = bVar15 >> 4 & 1;
            }
            if (bVar13 == bVar15) {
              uVar3 = in_fpscr & 0xfffffff;
              uVar5 = uVar3 | (uint)(local_c8 < local_a8[3]) << 0x1f;
              in_fpscr = uVar5 | (uint)(NAN(local_c8) || NAN(local_a8[3])) << 0x1c;
              bVar13 = (byte)(uVar5 >> 0x1f);
              bVar15 = (byte)(in_fpscr >> 0x1c) & 1;
              if (bVar13 == bVar15) {
                in_fpscr = uVar3 | (uint)(local_a8[5] < local_c8) << 0x1f |
                           (uint)(NAN(local_a8[5]) || NAN(local_c8)) << 0x1c;
                bVar15 = (byte)(in_fpscr >> 0x18);
                bVar13 = bVar15 >> 7;
                bVar15 = bVar15 >> 4 & 1;
              }
              if (bVar13 == bVar15) goto LAB_0056385a;
            }
          }
        }
        local_8c[6] = local_dc;
        local_8c[7] = local_d8;
        local_8c[4] = local_e4;
        pfVar7 = local_8c + 4;
        pfVar12 = local_8c;
        local_8c[5] = local_e0;
        pfVar2 = local_a8;
        pfVar9 = local_8c + 2;
        pfVar10 = local_8c + 6;
        pfVar11 = local_a8 + 2;
        iVar6 = 2;
        local_6c = pfVar2;
        do {
          fVar20 = *pfVar7;
          fVar23 = *pfVar12;
          fVar22 = *pfVar9;
          unaff_d9 = CONCAT44(fVar23,fVar22);
          fVar21 = *pfVar10;
          fVar26 = fVar20 * -3.0 + fVar23 * 9.0 + fVar22 * -9.0 + fVar21 * 3.0;
          iVar8 = 0;
          uVar3 = in_fpscr & 0xfffffff;
          fVar24 = fVar20 * 6.0 + fVar23 * -12.0 + fVar22 * 6.0;
          fVar17 = fVar20 * -3.0 + fVar23 * 3.0;
          if (1e-07 <= ABS(fVar26)) {
            fVar17 = fVar24 * fVar24 - fVar17 * 4.0 * fVar26;
            uVar3 = uVar3 | (uint)(fVar17 < 1.0000001e-07) << 0x1f;
            in_fpscr = uVar3 | (uint)NAN(fVar17) << 0x1c;
            if ((byte)(uVar3 >> 0x1f) == ((byte)(in_fpscr >> 0x1c) & 1)) {
              fVar17 = (float)func_0x004397a8(pfVar2);
              fVar18 = (fVar17 - fVar24) / (fVar26 * 2.0);
              uVar3 = in_fpscr & 0xfffffff;
              if ((1.0000001e-07 <= fVar18) && (fVar18 < 0.9999999)) {
                local_a8[0] = fVar18;
                iVar8 = 1;
              }
              fVar17 = (-fVar24 - fVar17) / (fVar26 * 2.0);
              uVar5 = uVar3 | (uint)(fVar17 < 1.0000001e-07) << 0x1f;
              in_fpscr = uVar5 | (uint)NAN(fVar17) << 0x1c;
              if (((byte)(uVar5 >> 0x1f) == ((byte)(in_fpscr >> 0x1c) & 1)) &&
                 (in_fpscr = uVar3, fVar17 < 0.9999999)) {
                pfVar2 = local_6c + iVar8;
                iVar8 = iVar8 + 1;
                *pfVar2 = fVar17;
              }
              pfVar2 = (float *)0x0;
              if (iVar8 != 0) goto LAB_005629ce;
            }
          }
          else {
            fVar26 = ABS(fVar24);
            uVar5 = uVar3 | (uint)(fVar26 < 1.0000001e-07) << 0x1f;
            in_fpscr = uVar5 | (uint)NAN(fVar26) << 0x1c;
            bVar13 = (byte)(uVar5 >> 0x1f);
            bVar15 = (byte)(in_fpscr >> 0x1c) & 1;
            if (bVar13 == bVar15) {
              fVar26 = -(fVar17 / fVar24);
              in_fpscr = uVar3 | (uint)(fVar26 < 1.0000001e-07) << 0x1f | (uint)NAN(fVar26) << 0x1c;
              bVar15 = (byte)(in_fpscr >> 0x18);
              bVar13 = bVar15 >> 7;
              bVar15 = bVar15 >> 4 & 1;
            }
            if ((bVar13 == bVar15) && (in_fpscr = in_fpscr & 0xfffffff, fVar26 < 0.9999999)) {
              local_a8[0] = fVar26;
              iVar8 = 1;
LAB_005629ce:
              uVar1 = 0;
              if (iVar8 << 0x1f < 0) {
                fVar17 = 1.0 - local_a8[0];
                fVar17 = fVar17 * fVar17 * fVar17 * fVar20 +
                         fVar17 * 3.0 * fVar17 * local_a8[0] * fVar23 +
                         fVar17 * 3.0 * local_a8[0] * local_a8[0] * fVar22 +
                         local_a8[0] * local_a8[0] * local_a8[0] * fVar21;
                fVar24 = *pfVar11;
                if (fVar17 <= *pfVar11) {
                  fVar24 = fVar17;
                }
                *pfVar11 = fVar24;
                fVar24 = pfVar11[2];
                uVar3 = in_fpscr & 0xfffffff | (uint)(fVar17 < fVar24) << 0x1f;
                in_fpscr = uVar3 | (uint)(NAN(fVar17) || NAN(fVar24)) << 0x1c;
                if ((byte)(uVar3 >> 0x1f) != ((byte)(in_fpscr >> 0x1c) & 1)) {
                  fVar17 = fVar24;
                }
                pfVar11[2] = fVar17;
                uVar1 = 1;
              }
              /* Native562a44..562b3a: root count inR7, odd index inR0.
                 Structural research draft; native/C geometry qualification pending. */
              uint loop_pairs = ((uint)iVar8) >> 1;
              iVar8 = (int)uVar1;
              while(loop_pairs != 0) {
              fVar17 = local_a8[iVar8];
              fVar24 = 1.0 - fVar17;
              fVar24 = fVar24 * fVar24 * fVar24 * fVar20 + fVar24 * 3.0 * fVar24 * fVar17 * fVar23 +
                       fVar24 * 3.0 * fVar17 * fVar17 * fVar22 + fVar17 * fVar17 * fVar17 * fVar21;
              fVar17 = *pfVar11;
              if (fVar24 <= *pfVar11) {
                fVar17 = fVar24;
              }
              *pfVar11 = fVar17;
              if (NAN(fVar24) || NAN(pfVar11[2])) {
                fVar24 = pfVar11[2];
              }
              pfVar11[2] = fVar24;
              fVar17 = local_a8[iVar8 + 1];
              fVar24 = 1.0 - fVar17;
              fVar20 = fVar24 * fVar24 * fVar24 * fVar20 + fVar24 * 3.0 * fVar24 * fVar17 * fVar23 +
                       fVar24 * 3.0 * fVar17 * fVar17 * fVar22 + fVar17 * fVar17 * fVar17 * fVar21;
              fVar17 = *pfVar11;
              if (fVar20 <= *pfVar11) {
                fVar17 = fVar20;
              }
              *pfVar11 = fVar17;
              fVar17 = pfVar11[2];
              uVar3 = in_fpscr & 0xfffffff | (uint)(fVar20 < fVar17) << 0x1f;
              in_fpscr = uVar3 | (uint)(NAN(fVar20) || NAN(fVar17)) << 0x1c;
              if ((byte)(uVar3 >> 0x1f) == ((byte)(in_fpscr >> 0x1c) & 1)) {
                fVar17 = fVar20;
              }
              pfVar11[2] = fVar17;
              iVar8 += 2;
              --loop_pairs;
              } /* Native LE decrements loop counter; no external call. */
            }
          }
          pfVar7 = pfVar7 + 1;
          pfVar11 = pfVar11 + 1;
          pfVar10 = pfVar10 + 1;
          pfVar9 = pfVar9 + 1;
          pfVar12 = pfVar12 + 1;
          iVar6 = iVar6 + -1;
        } while (iVar6 != 0);
        param_1[4] = (uint)local_a8[2];
        param_1[5] = (uint)local_a8[3];
        param_1[6] = (uint)local_a8[4];
        param_1[7] = (uint)local_a8[5];
      }
      else if ((bVar13 == 1 || bVar13 == 2) || (bVar13 == 4 || bVar13 == 3)) {
LAB_00563802:
        in_fpscr = in_fpscr & 0xfffffff;
        fVar17 = (float)param_1[4];
        if (local_dc < (float)param_1[4]) {
          fVar17 = local_dc;
        }
        param_1[4] = (uint)fVar17;
        fVar17 = (float)param_1[5];
        if (local_d8 < (float)param_1[5]) {
          fVar17 = local_d8;
        }
        param_1[5] = (uint)fVar17;
        fVar17 = local_dc;
        if (local_dc <= (float)param_1[6]) {
          fVar17 = (float)param_1[6];
        }
        param_1[6] = (uint)fVar17;
        fVar17 = local_d8;
        if (local_d8 <= (float)param_1[7]) {
          fVar17 = (float)param_1[7];
        }
        param_1[7] = (uint)fVar17;
      }
      else if (bVar13 == 5 || bVar13 == 7) {
        uVar3 = in_fpscr & 0xfffffff;
        fVar17 = (float)param_1[4];
        if (local_dc <= (float)param_1[4]) {
          fVar17 = local_dc;
        }
        param_1[4] = (uint)fVar17;
        fVar17 = (float)param_1[5];
        if (local_d8 <= (float)param_1[5]) {
          fVar17 = local_d8;
        }
        param_1[5] = (uint)fVar17;
        fVar17 = (float)param_1[6];
        if ((float)param_1[6] <= local_dc) {
          fVar17 = local_dc;
        }
        param_1[6] = (uint)fVar17;
        fVar17 = (float)param_1[7];
        if ((float)param_1[7] <= local_d8) {
          fVar17 = local_d8;
        }
        fVar20 = (float)param_1[4];
        param_1[7] = (uint)fVar17;
        uVar5 = uVar3 | (uint)(local_d4 < fVar20) << 0x1f;
        in_fpscr = uVar5 | (uint)(NAN(local_d4) || NAN(fVar20)) << 0x1c;
        fVar17 = (float)param_1[5];
        fVar21 = (float)param_1[6];
        fVar22 = (float)param_1[7];
        bVar13 = (byte)(uVar5 >> 0x1f);
        bVar15 = (byte)(in_fpscr >> 0x1c) & 1;
        if (bVar13 == bVar15) {
          in_fpscr = uVar3 | (uint)(fVar21 < local_d4) << 0x1f |
                     (uint)(NAN(fVar21) || NAN(local_d4)) << 0x1c;
          bVar15 = (byte)(in_fpscr >> 0x18);
          bVar13 = bVar15 >> 7;
          bVar15 = bVar15 >> 4 & 1;
        }
        if (bVar13 == bVar15) {
          uVar3 = in_fpscr & 0xfffffff;
          uVar5 = uVar3 | (uint)(local_d0 < fVar17) << 0x1f;
          in_fpscr = uVar5 | (uint)(NAN(local_d0) || NAN(fVar17)) << 0x1c;
          bVar13 = (byte)(uVar5 >> 0x1f);
          bVar15 = (byte)(in_fpscr >> 0x1c) & 1;
          if (bVar13 == bVar15) {
            in_fpscr = uVar3 | (uint)(fVar22 < local_d0) << 0x1f |
                       (uint)(NAN(fVar22) || NAN(local_d0)) << 0x1c;
            bVar15 = (byte)(in_fpscr >> 0x18);
            bVar13 = bVar15 >> 7;
            bVar15 = bVar15 >> 4 & 1;
          }
          if (bVar13 == bVar15) goto LAB_0056385a;
        }
        fVar23 = local_d4 * 2.0 + local_e4 * -2.0;
        fVar24 = (local_dc * 2.0 + local_d4 * -2.0) - fVar23;
        fVar26 = ABS(fVar24);
        bVar16 = NAN(fVar26);
        uVar3 = in_fpscr & 0xfffffff | (uint)(fVar26 < 1.0000001e-07) << 0x1f;
        bVar14 = SUB41(uVar3 >> 0x1f,0);
        if (bVar14 == bVar16) {
          fVar23 = -(fVar23 / fVar24);
          bVar16 = NAN(fVar23);
          uVar3 = in_fpscr & 0xfffffff | (uint)(fVar23 < 1.0000001e-07) << 0x1f;
          bVar14 = SUB41(uVar3 >> 0x1f,0);
        }
        if ((bVar14 == bVar16) && (uVar3 = uVar3 & 0xfffffff, fVar23 < 0.9999999)) {
          fVar24 = 1.0 - fVar23;
          fVar23 = fVar24 * fVar24 * local_e4 + fVar24 * 2.0 * fVar23 * local_d4 +
                   fVar23 * fVar23 * local_dc;
          if (fVar23 <= fVar20) {
            fVar20 = fVar23;
          }
          if (fVar21 <= fVar23) {
            fVar21 = fVar23;
          }
        }
        fVar23 = local_d0 * 2.0 + local_e0 * -2.0;
        fVar24 = (local_d8 * 2.0 + local_d0 * -2.0) - fVar23;
        fVar26 = ABS(fVar24);
        uVar5 = uVar3 & 0xfffffff | (uint)(fVar26 < 1.0000001e-07) << 0x1f;
        in_fpscr = uVar5 | (uint)NAN(fVar26) << 0x1c;
        bVar13 = (byte)(uVar5 >> 0x1f);
        bVar15 = (byte)(in_fpscr >> 0x1c) & 1;
        if (bVar13 == bVar15) {
          fVar23 = -(fVar23 / fVar24);
          in_fpscr = uVar3 & 0xfffffff | (uint)(fVar23 < 1.0000001e-07) << 0x1f |
                     (uint)NAN(fVar23) << 0x1c;
          bVar15 = (byte)(in_fpscr >> 0x18);
          bVar13 = bVar15 >> 7;
          bVar15 = bVar15 >> 4 & 1;
        }
        if ((bVar13 == bVar15) && (in_fpscr = in_fpscr & 0xfffffff, fVar23 < 0.9999999)) {
          fVar24 = 1.0 - fVar23;
          fVar23 = fVar24 * fVar24 * local_e0 + fVar24 * 2.0 * fVar23 * local_d0 +
                   fVar23 * fVar23 * local_d8;
          if (fVar23 <= fVar17) {
            fVar17 = fVar23;
          }
          if (fVar22 <= fVar23) {
            fVar22 = fVar23;
          }
        }
        param_1[4] = (uint)fVar20;
        param_1[5] = (uint)fVar17;
        param_1[6] = (uint)fVar21;
        param_1[7] = (uint)fVar22;
      }
      else if ((*(byte *)(param_1[2] + local_90) & 0xf) == 9) {
        fVar20 = ABS(local_d4);
        uVar3 = in_fpscr & 0xfffffff;
        in_fpscr = uVar3 | (uint)(fVar20 < 1.0000001e-05) << 0x1f;
        bVar13 = -(char)((int)in_fpscr >> 0x1f);
        fVar17 = (float)unaff_d9;
        if (bVar13 == 0) {
          fVar17 = ABS(local_d0);
          unaff_d9 = (ulonglong)(uint)fVar17;
          in_fpscr = uVar3 | (uint)(fVar17 < 1.0000001e-05) << 0x1f;
          bVar13 = (byte)(in_fpscr >> 0x1f);
        }
        if (bVar13 != 0) goto LAB_00563802;
        local_a8[5] = local_cc;
        fVar26 = local_cc * 0.017453292;
        local_a8[3] = local_bc;
        local_a8[2] = local_b8;
        local_a8[1] = local_c4;
        local_a8[0] = local_c0;
        local_a8[4] = (float)func_0x0050968c(fVar26);
        fVar23 = (float)func_0x00509690(fVar26);
        fVar28 = local_a8[3] * local_a8[4] + local_a8[2] * fVar23;
        fVar29 = fVar28 / fVar20;
        fVar30 = local_a8[2] * local_a8[4] - local_a8[3] * fVar23;
        fVar31 = local_a8[1] * local_a8[4] + local_a8[0] * fVar23;
        fVar25 = fVar31 / fVar20;
        fVar32 = local_a8[0] * local_a8[4] - local_a8[1] * fVar23;
        fVar21 = fVar29 + fVar25;
        fVar18 = fVar30 / fVar17;
        unaff_d9 = CONCAT44(fVar18,fVar17);
        fVar27 = fVar32 / fVar17;
        fVar22 = fVar18 + fVar27;
        fVar33 = fVar29 - fVar25;
        fVar18 = fVar18 - fVar27;
        fVar24 = fVar33 * fVar33 + fVar18 * fVar18;
        uVar3 = in_fpscr & 0xfffffff;
        in_fpscr = uVar3 | (uint)(fVar24 == 0.0) << 0x1e;
        if ((byte)(in_fpscr >> 0x1e) != 0) goto LAB_0056385a;
        local_8c[0] = 1.0 / fVar24 + -0.25;
        if (local_8c[0] < 0.0) {
          local_8c[0] = 0.0;
          fVar21 = (float)func_0x004397a8(fVar24 * 0.25);
          fVar20 = fVar20 * fVar21;
          fVar17 = fVar17 * fVar21;
          fVar29 = fVar28 / fVar20;
          fVar30 = fVar30 / fVar17;
          unaff_d9 = CONCAT44(fVar30,fVar17);
          fVar25 = fVar31 / fVar20;
          fVar21 = fVar29 + fVar25;
          fVar27 = fVar32 / fVar17;
          fVar22 = fVar30 + fVar27;
          fVar33 = fVar29 - fVar25;
          fVar18 = fVar30 - fVar27;
        }
        fVar17 = (float)func_0x004397a8(local_8c[0]);
        fVar31 = fVar21 * 0.5 + fVar17 * fVar18;
        fVar32 = fVar22 * 0.5 - fVar17 * fVar33;
        fVar24 = (float)func_0x0050969c((float)(unaff_d9 >> 0x20) - fVar32,fVar29 - fVar31);
        fVar28 = (float)unaff_d9;
        fVar30 = (float)func_0x0050969c(fVar27 - fVar32,fVar25 - fVar31);
        fVar24 = fVar30 * 57.29578 - fVar24 * 57.29578;
        if (fVar24 < 0.0) {
          fVar24 = fVar24 + 360.0;
        }
        bVar13 = local_ed >> 6;
        bVar15 = bVar13 & 1;
        if ((int)((uint)local_ed << 0x1a) < 0) {
          bVar15 = bVar15 ^ 1;
        }
        if (((180.0 <= fVar24) || (bVar15 == 0)) && ((fVar24 < 180.0 || (bVar15 != 0)))) {
          fVar31 = fVar21 * 0.5 - fVar17 * fVar18;
          fVar32 = fVar22 * 0.5 + fVar17 * fVar33;
        }
        fVar17 = fVar31 * fVar20 * fVar23 + fVar32 * fVar28 * local_a8[4];
        uVar5 = uVar3 & 0xfffffff | (uint)(local_a8[5] == 0.0) << 0x1e;
        fVar21 = fVar31 * fVar20 * local_a8[4] - fVar32 * fVar28 * fVar23;
        local_a8[4] = -1.0;
        bVar15 = (byte)(uVar5 >> 0x1e);
        if (bVar15 == 0) {
          uVar5 = uVar3 & 0xfffffff | (uint)(local_a8[5] == 180.0) << 0x1e;
          bVar15 = (byte)(uVar5 >> 0x1e);
        }
        if (bVar15 == 0) {
          uVar3 = uVar5 & 0xfffffff | (uint)(local_a8[5] == 90.0) << 0x1e;
          bVar15 = (byte)(uVar3 >> 0x1e);
          if (bVar15 == 0) {
            uVar3 = uVar5 & 0xfffffff | (uint)(local_a8[5] == 270.0) << 0x1e;
            bVar15 = (byte)(uVar3 >> 0x1e);
          }
          fVar29 = -1.0;
          if (bVar15 == 0) {
            fVar22 = (float)func_0x00563f40(fVar26);
            fVar18 = (float)func_0x0058ec74((fVar28 * fVar22) / fVar20);
            fVar18 = -fVar18;
            fVar22 = (float)func_0x00563f40(fVar26);
            fVar30 = (float)func_0x0058ec74((fVar28 * fVar22) / fVar20);
            fVar30 = 3.1415927 - fVar30;
            fVar22 = (float)func_0x0050968c(fVar18);
            fVar23 = (float)func_0x0050968c(fVar26);
            fVar24 = (float)func_0x00509690(fVar18);
            fVar25 = (float)func_0x00509690(fVar26);
            fVar23 = (fVar21 + fVar20 * fVar22 * fVar23) - fVar28 * fVar24 * fVar25;
            fVar22 = (float)func_0x0050968c(fVar30);
            fVar24 = (float)func_0x0050968c(fVar26);
            fVar25 = (float)func_0x00509690(fVar30);
            fVar27 = (float)func_0x00509690(fVar26);
            fVar25 = (fVar21 + fVar20 * fVar22 * fVar24) - fVar28 * fVar25 * fVar27;
            uVar3 = uVar3 & 0xfffffff;
            fVar22 = fVar25;
            fVar24 = fVar18;
            if (fVar25 < fVar23) {
              fVar22 = fVar23;
              fVar24 = fVar30;
              fVar23 = fVar25;
              fVar30 = fVar18;
            }
            fVar18 = (float)func_0x0050968c(fVar24);
            fVar25 = (float)func_0x00509690(fVar26);
            fVar24 = (float)func_0x00509690(fVar24);
            fVar27 = (float)func_0x0050968c(fVar26);
            fVar18 = (fVar17 + fVar20 * fVar18 * fVar25 + fVar28 * fVar24 * fVar27) - fVar17;
            uVar3 = uVar3 & 0xfffffff | (uint)(fVar18 < 0.0) << 0x1f | (uint)(fVar18 == 0.0) << 0x1e
            ;
            uVar5 = uVar3 | (uint)NAN(fVar18) << 0x1c;
            fVar25 = fVar23 - fVar21;
            bVar15 = (byte)(uVar3 >> 0x18);
            fVar24 = fVar29;
            if (!(bool)(bVar15 >> 6 & 1) && bVar15 >> 7 == ((byte)(uVar5 >> 0x1c) & 1)) {
              fVar24 = 1.0;
            }
            fVar18 = (float)func_0x004397a8(fVar25 * fVar25 + fVar18 * fVar18);
            fVar18 = (float)func_0x0058ecbc(fVar25 / fVar18);
            fVar18 = (float)func_0x00577c3c(fVar24 * fVar18 + 6.2831855,0x40c90fdb);
            fVar24 = (float)func_0x0050968c(fVar30);
            fVar25 = (float)func_0x00509690(fVar26);
            fVar30 = (float)func_0x00509690(fVar30);
            fVar27 = (float)func_0x0050968c(fVar26);
            fVar30 = (fVar17 + fVar20 * fVar24 * fVar25 + fVar28 * fVar30 * fVar27) - fVar17;
            uVar5 = uVar5 & 0xfffffff | (uint)(fVar30 < 0.0) << 0x1f | (uint)(fVar30 == 0.0) << 0x1e
            ;
            uVar3 = uVar5 | (uint)NAN(fVar30) << 0x1c;
            fVar25 = fVar22 - fVar21;
            bVar15 = (byte)(uVar5 >> 0x18);
            fVar24 = fVar29;
            if (!(bool)(bVar15 >> 6 & 1) && bVar15 >> 7 == ((byte)(uVar3 >> 0x1c) & 1)) {
              fVar24 = 1.0;
            }
            fVar30 = (float)func_0x004397a8(fVar25 * fVar25 + fVar30 * fVar30);
            fVar30 = (float)func_0x0058ecbc(fVar25 / fVar30);
            fVar30 = (float)func_0x00577c3c(fVar24 * fVar30 + 6.2831855,0x40c90fdb);
            fVar24 = (float)func_0x00563f40(fVar26);
            fVar32 = (float)func_0x0058ec74(fVar28 / (fVar24 * fVar20));
            fVar24 = (float)func_0x00563f40(fVar26);
            fVar31 = (float)func_0x0058ec74(fVar28 / (fVar24 * fVar20));
            fVar31 = fVar31 + 3.1415927;
            fVar24 = (float)func_0x0050968c(fVar32);
            fVar25 = (float)func_0x00509690(fVar26);
            fVar27 = (float)func_0x00509690(fVar32);
            fVar33 = (float)func_0x0050968c(fVar26);
            fVar24 = fVar17 + fVar20 * fVar24 * fVar25 + fVar28 * fVar27 * fVar33;
            fVar25 = (float)func_0x0050968c(fVar31);
            fVar27 = (float)func_0x00509690(fVar26);
            fVar33 = (float)func_0x00509690(fVar31);
            fVar19 = (float)func_0x0050968c(fVar26);
            fVar33 = fVar17 + fVar20 * fVar25 * fVar27 + fVar28 * fVar33 * fVar19;
            uVar3 = uVar3 & 0xfffffff;
            fVar25 = fVar33;
            fVar27 = fVar32;
            if (fVar33 < fVar24) {
              fVar25 = fVar24;
              fVar27 = fVar31;
              fVar24 = fVar33;
              fVar31 = fVar32;
            }
            local_a8[4] = (float)func_0x0050968c(fVar27);
            fVar32 = (float)func_0x0050968c(fVar26);
            fVar27 = (float)func_0x00509690(fVar27);
            fVar33 = (float)func_0x00509690(fVar26);
            fVar19 = fVar24 - fVar17;
            uVar3 = uVar3 & 0xfffffff | (uint)(fVar19 < 0.0) << 0x1f | (uint)(fVar19 == 0.0) << 0x1e
            ;
            uVar5 = uVar3 | (uint)NAN(fVar19) << 0x1c;
            fVar32 = ((fVar21 + fVar20 * local_a8[4] * fVar32) - fVar28 * fVar27 * fVar33) - fVar21;
            bVar15 = (byte)(uVar3 >> 0x18);
            fVar27 = fVar29;
            if (!(bool)(bVar15 >> 6 & 1) && bVar15 >> 7 == ((byte)(uVar5 >> 0x1c) & 1)) {
              fVar27 = 1.0;
            }
            fVar33 = (float)func_0x004397a8(fVar32 * fVar32 + fVar19 * fVar19);
            fVar32 = (float)func_0x0058ecbc(fVar32 / fVar33);
            fVar27 = (float)func_0x00577c3c(fVar27 * fVar32 + 6.2831855,0x40c90fdb);
            fVar32 = (float)func_0x0050968c(fVar31);
            fVar33 = (float)func_0x0050968c(fVar26);
            fVar31 = (float)func_0x00509690(fVar31);
            fVar26 = (float)func_0x00509690(fVar26);
            fVar19 = fVar25 - fVar17;
            uVar3 = uVar5 & 0xfffffff | (uint)(fVar19 < 0.0) << 0x1f | (uint)(fVar19 == 0.0) << 0x1e
            ;
            uVar5 = uVar3 | (uint)NAN(fVar19) << 0x1c;
            fVar20 = ((fVar21 + fVar32 * fVar20 * fVar33) - fVar31 * fVar28 * fVar26) - fVar21;
            bVar15 = (byte)(uVar3 >> 0x18);
            if (!(bool)(bVar15 >> 6 & 1) && bVar15 >> 7 == ((byte)(uVar5 >> 0x1c) & 1)) {
              fVar29 = 1.0;
            }
            fVar26 = (float)func_0x004397a8(fVar20 * fVar20 + fVar19 * fVar19);
            fVar20 = (float)func_0x0058ecbc(fVar20 / fVar26);
            fVar20 = fVar29 * fVar20 + 6.2831855;
          }
          else {
            fVar23 = -fVar28;
            fVar22 = (float)func_0x004397a8(fVar23 * fVar23);
            fVar22 = (float)func_0x0058ecbc(fVar23 / fVar22);
            fVar18 = (float)func_0x00577c3c(fVar22 * -1.0 + 6.2831855,0x40c90fdb);
            fVar22 = (float)func_0x004397a8(fVar28 * fVar28);
            fVar22 = (float)func_0x0058ecbc(fVar28 / fVar22);
            fVar30 = (float)func_0x00577c3c(fVar22 * -1.0 + 6.2831855,0x40c90fdb);
            fVar25 = -fVar20;
            uVar3 = uVar3 & 0xfffffff | (uint)(fVar25 < 0.0) << 0x1f | (uint)(fVar25 == 0.0) << 0x1e
            ;
            uVar5 = uVar3 | (uint)NAN(fVar25) << 0x1c;
            fVar23 = fVar21 - fVar28;
            fVar22 = fVar21 + fVar28;
            fVar24 = fVar17 - fVar20;
            bVar15 = (byte)(uVar3 >> 0x18);
            fVar26 = fVar29;
            if (!(bool)(bVar15 >> 6 & 1) && bVar15 >> 7 == ((byte)(uVar5 >> 0x1c) & 1)) {
              fVar26 = 1.0;
            }
            fVar25 = (float)func_0x004397a8(fVar25 * fVar25);
            fVar25 = (float)func_0x0058ecbc(0.0 / fVar25);
            fVar27 = (float)func_0x00577c3c(fVar26 * fVar25 + 6.2831855,0x40c90fdb);
            uVar3 = uVar5 & 0xfffffff | (uint)(fVar20 < 0.0) << 0x1f | (uint)(fVar20 == 0.0) << 0x1e
            ;
            uVar5 = uVar3 | (uint)NAN(fVar20) << 0x1c;
            fVar25 = fVar17 + fVar20;
            bVar15 = (byte)(uVar3 >> 0x18);
            if (!(bool)(bVar15 >> 6 & 1) && bVar15 >> 7 == ((byte)(uVar5 >> 0x1c) & 1)) {
              fVar29 = 1.0;
            }
            fVar20 = (float)func_0x004397a8(fVar20 * fVar20);
            fVar20 = (float)func_0x0058ecbc(0.0 / fVar20);
            fVar20 = fVar29 * fVar20 + 6.2831855;
          }
        }
        else {
          fVar23 = -fVar20;
          fVar22 = (float)func_0x004397a8(fVar23 * fVar23);
          fVar22 = (float)func_0x0058ecbc(fVar23 / fVar22);
          fVar18 = (float)func_0x00577c3c(fVar22 * -1.0 + 6.2831855,0x40c90fdb);
          fVar22 = (float)func_0x004397a8(fVar20 * fVar20);
          fVar22 = (float)func_0x0058ecbc(fVar20 / fVar22);
          fVar30 = (float)func_0x00577c3c(fVar22 * -1.0 + 6.2831855,0x40c90fdb);
          fVar26 = -fVar28;
          uVar3 = uVar5 & 0xfffffff | (uint)(fVar26 < 0.0) << 0x1f | (uint)(fVar26 == 0.0) << 0x1e;
          uVar5 = uVar3 | (uint)NAN(fVar26) << 0x1c;
          fVar23 = fVar21 - fVar20;
          fVar22 = fVar21 + fVar20;
          fVar24 = fVar17 - fVar28;
          bVar15 = (byte)(uVar3 >> 0x18);
          if ((bool)(bVar15 >> 6 & 1) || bVar15 >> 7 != ((byte)(uVar5 >> 0x1c) & 1)) {
            fVar20 = -1.0;
          }
          else {
            fVar20 = 1.0;
          }
          fVar26 = (float)func_0x004397a8(fVar26 * fVar26);
          fVar26 = (float)func_0x0058ecbc(0.0 / fVar26);
          fVar27 = (float)func_0x00577c3c(fVar20 * fVar26 + 6.2831855,0x40c90fdb);
          uVar3 = uVar5 & 0xfffffff | (uint)(fVar28 < 0.0) << 0x1f | (uint)(fVar28 == 0.0) << 0x1e;
          uVar5 = uVar3 | (uint)NAN(fVar28) << 0x1c;
          fVar25 = fVar17 + fVar28;
          bVar15 = (byte)(uVar3 >> 0x18);
          if ((bool)(bVar15 >> 6 & 1) || bVar15 >> 7 != ((byte)(uVar5 >> 0x1c) & 1)) {
            fVar20 = -1.0;
          }
          else {
            fVar20 = 1.0;
          }
          fVar26 = (float)func_0x004397a8(fVar28 * fVar28);
          fVar26 = (float)func_0x0058ecbc(0.0 / fVar26);
          fVar20 = fVar20 * fVar26 + 6.2831855;
        }
        fVar31 = -1.0;
        fVar26 = (float)func_0x00577c3c(fVar20,0x40c90fdb);
        fVar28 = local_a8[2] - fVar17;
        uVar3 = uVar5 & 0xfffffff | (uint)(fVar28 < 0.0) << 0x1f | (uint)(fVar28 == 0.0) << 0x1e;
        uVar5 = uVar3 | (uint)NAN(fVar28) << 0x1c;
        fVar29 = local_a8[3] - fVar21;
        bVar15 = (byte)(uVar3 >> 0x18);
        fVar20 = fVar31;
        if (!(bool)(bVar15 >> 6 & 1) && bVar15 >> 7 == ((byte)(uVar5 >> 0x1c) & 1)) {
          fVar20 = 1.0;
        }
        fVar28 = (float)func_0x004397a8(fVar29 * fVar29 + fVar28 * fVar28);
        fVar28 = (float)func_0x0058ecbc(fVar29 / fVar28);
        fVar20 = (float)func_0x00577c3c(fVar20 * fVar28 + 6.2831855,0x40c90fdb);
        fVar17 = local_a8[0] - fVar17;
        uVar3 = uVar5 & 0xfffffff | (uint)(fVar17 < 0.0) << 0x1f | (uint)(fVar17 == 0.0) << 0x1e;
        in_fpscr = uVar3 | (uint)NAN(fVar17) << 0x1c;
        fVar21 = local_a8[1] - fVar21;
        unaff_d9 = CONCAT44(fVar21,fVar20);
        bVar15 = (byte)(uVar3 >> 0x18);
        if (!(bool)(bVar15 >> 6 & 1) && bVar15 >> 7 == ((byte)(in_fpscr >> 0x1c) & 1)) {
          fVar31 = 1.0;
        }
        fVar17 = (float)func_0x004397a8(fVar21 * fVar21 + fVar17 * fVar17);
        fVar17 = (float)func_0x0058ecbc(fVar21 / fVar17);
        fVar17 = (float)func_0x00577c3c(fVar31 * fVar17 + 6.2831855,0x40c90fdb);
        if ((bVar13 & 1) == 0) {
          unaff_d9 = (ulonglong)(uint)fVar17;
          fVar17 = fVar20;
        }
        bVar16 = false;
        fVar20 = (float)unaff_d9;
        in_fpscr = in_fpscr & 0xfffffff;
        if (fVar20 <= fVar17) {
          if (fVar18 < fVar20 || (fVar18 < fVar20 || fVar17 < fVar18)) goto LAB_0056364c;
LAB_00563680:
          bVar14 = fVar30 < (float)unaff_d9;
          if (bVar14 || (bVar14 || fVar17 < fVar30)) goto LAB_005636aa;
LAB_005636c4:
          if (bVar16) goto LAB_005636dc;
          bVar14 = fVar27 < (float)unaff_d9;
          if (bVar14 || (bVar14 || fVar17 < fVar27)) goto LAB_005636f0;
LAB_0056370c:
          bVar16 = fVar26 < (float)unaff_d9;
          if (bVar16 || (bVar16 || fVar17 < fVar26)) goto LAB_00563736;
        }
        else {
          unaff_d9 = (ulonglong)(uint)fVar17;
          bVar16 = true;
          bVar14 = fVar17 <= fVar18;
          fVar17 = fVar20;
          if (bVar14 && (bVar14 && fVar18 <= fVar20)) {
LAB_0056364c:
            fVar23 = local_a8[3];
            if (local_a8[1] <= local_a8[3]) {
              fVar23 = local_a8[1];
            }
            if (!bVar16) goto LAB_00563680;
          }
          bVar14 = (float)unaff_d9 <= fVar30;
          if (bVar14 && (bVar14 && fVar30 <= fVar17)) {
LAB_005636aa:
            fVar22 = local_a8[3];
            if (local_a8[3] <= local_a8[1]) {
              fVar22 = local_a8[1];
            }
            goto LAB_005636c4;
          }
LAB_005636dc:
          bVar14 = (float)unaff_d9 <= fVar27;
          if (bVar14 && (bVar14 && fVar27 <= fVar17)) {
LAB_005636f0:
            fVar24 = local_a8[2];
            if (local_a8[0] <= local_a8[2]) {
              fVar24 = local_a8[0];
            }
            if (!bVar16) goto LAB_0056370c;
          }
          bVar16 = (float)unaff_d9 <= fVar26;
          if (bVar16 && (bVar16 && fVar26 <= fVar17)) {
LAB_00563736:
            fVar25 = local_a8[2];
            if (local_a8[2] <= local_a8[0]) {
              fVar25 = local_a8[0];
            }
          }
        }
        fVar17 = (float)param_1[4];
        if (fVar23 < (float)param_1[4]) {
          fVar17 = fVar23;
        }
        param_1[4] = (uint)fVar17;
        fVar17 = (float)param_1[5];
        if (fVar24 < (float)param_1[5]) {
          fVar17 = fVar24;
        }
        param_1[5] = (uint)fVar17;
        fVar17 = (float)param_1[6];
        if ((float)param_1[6] < fVar23) {
          fVar17 = fVar23;
        }
        param_1[6] = (uint)fVar17;
        fVar17 = (float)param_1[7];
        if ((float)param_1[7] < fVar24) {
          fVar17 = fVar24;
        }
        param_1[7] = (uint)fVar17;
        fVar17 = (float)param_1[4];
        if (fVar22 < (float)param_1[4]) {
          fVar17 = fVar22;
        }
        param_1[4] = (uint)fVar17;
        fVar17 = (float)param_1[5];
        if (fVar25 < (float)param_1[5]) {
          fVar17 = fVar25;
        }
        param_1[5] = (uint)fVar17;
        fVar17 = (float)param_1[6];
        if ((float)param_1[6] < fVar22) {
          fVar17 = fVar22;
        }
        param_1[6] = (uint)fVar17;
        fVar17 = (float)param_1[7];
        if ((float)param_1[7] < fVar25) {
          fVar17 = fVar25;
        }
        param_1[7] = (uint)fVar17;
      }
LAB_0056385a:
      local_90 = local_90 + 1;
    } while (local_90 < *param_1);
  }
  iVar6 = (int)(float)param_1[4];
  fVar17 = (float)VectorSignedToFloat(iVar6,(byte)(in_fpscr >> 0x16) & 3);
  in_fpscr = in_fpscr & 0xfffffff;
  uVar3 = VectorSignedToFloat(iVar6 - (uint)((float)param_1[4] < fVar17),
                              (byte)(in_fpscr >> 0x16) & 3);
  param_1[4] = uVar3;
  iVar6 = (int)(float)param_1[5];
  fVar17 = (float)VectorSignedToFloat(iVar6,(byte)(in_fpscr >> 0x16) & 3);
  uVar3 = VectorSignedToFloat(iVar6 - (uint)((float)param_1[5] < fVar17),
                              (byte)(in_fpscr >> 0x16) & 3);
  param_1[5] = uVar3;
  iVar6 = (int)(float)param_1[6];
  fVar17 = (float)VectorSignedToFloat(iVar6,(byte)(in_fpscr >> 0x16) & 3);
  uVar3 = VectorSignedToFloat((uint)(fVar17 < (float)param_1[6]) + iVar6,
                              (byte)(in_fpscr >> 0x16) & 3);
  param_1[6] = uVar3;
  iVar6 = (int)(float)param_1[7];
  fVar17 = (float)VectorSignedToFloat(iVar6,(byte)(in_fpscr >> 0x16) & 3);
  uVar3 = VectorSignedToFloat((uint)(fVar17 < (float)param_1[7]) + iVar6,
                              (byte)(in_fpscr >> 0x16) & 3);
  param_1[7] = uVar3;
  param_1[0x14] = (uint)((float)param_1[6] - (float)param_1[4]);
  param_1[0x15] = (uint)((float)param_1[7] - (float)param_1[5]);
  return;
}

