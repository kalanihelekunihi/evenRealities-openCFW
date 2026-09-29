
int FUN_00519290(float param_1,float param_2,float param_3,float param_4,float param_5,float param_6
                )

{
  char cVar1;
  byte bVar2;
  undefined8 uVar3;
  bool bVar4;
  int *piVar5;
  int iVar6;
  int iVar7;
  undefined4 uVar8;
  float *pfVar9;
  int iVar10;
  int iVar11;
  undefined4 uVar12;
  bool bVar13;
  float fVar14;
  float fVar15;
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
  float fVar26;
  float fVar27;
  float fVar28;
  float fVar29;
  float fVar30;
  float fVar31;
  float fVar32;
  float fVar33;
  float fVar34;
  undefined8 uVar35;
  undefined8 uVar36;
  undefined4 uVar37;
  float fVar38;
  float fVar39;
  float local_120;
  float local_11c;
  float local_110;
  float local_10c;
  float local_108;
  float local_104;
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
  float local_c4;
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
  float local_8c;
  float local_88;
  float local_84;
  float local_80;
  float local_7c;
  undefined4 uStack_78;
  undefined4 uStack_74;
  undefined4 uStack_70;
  
  piVar5 = DAT_00519ed8;
  iVar10 = 1;
  bVar4 = true;
  local_120 = param_5;
  local_11c = param_6;
  local_110 = param_4;
  local_10c = param_3;
  local_108 = param_1;
  local_104 = param_2;
  do {
    fVar14 = (local_108 + local_10c) * 0.5;
    fVar16 = (local_104 + local_110) * 0.5;
    fVar17 = (local_10c + local_120) * 0.5;
    fVar19 = (local_110 + local_11c) * 0.5;
    fVar26 = (fVar16 + fVar19) * 0.5;
    fVar29 = (fVar14 + fVar17) * 0.5;
    fVar27 = local_120 - local_108;
    fVar28 = local_11c - local_104;
    iVar11 = *piVar5;
    fVar30 = ABS((local_10c - local_120) * fVar28 + (local_11c - local_110) * fVar27);
    fVar27 = fVar27 * fVar27 + fVar28 * fVar28;
    fVar30 = fVar30 * fVar30;
    if ((int)((uint)*(byte *)(iVar11 + 0x7d) << 0x1f) < 0) {
      if (fVar27 < fVar30) goto LAB_00519384;
LAB_00519504:
      iVar10 = iVar10 + -1;
      if (*(char *)(iVar11 + 0x2e4) == '\0') {
        if (bVar4) {
          fVar16 = fVar29 - local_108;
          fVar14 = fVar26 - local_104;
          bVar4 = false;
          if (-1 < (int)((uint)(ABS(fVar16 * fVar16 + fVar14 * fVar14) < DAT_005194ec) << 0x1f)) {
            fVar17 = (float)FUN_004397a8();
            fVar16 = fVar16 * (1.0 / fVar17);
            fVar14 = fVar14 * (1.0 / fVar17);
            fVar19 = *(float *)(iVar11 + 0x130) * 0.5 * fVar14;
            fVar28 = local_108 - fVar19;
            fVar27 = *(float *)(iVar11 + 0x134) * 0.5 * fVar16;
            fVar30 = fVar27 + local_104;
            uVar36 = CONCAT44(fVar30,fVar28);
            local_ec = fVar29 - fVar19;
            local_e8 = fVar27 + fVar26;
            local_f4 = fVar19 + fVar29;
            local_f0 = fVar26 - fVar27;
            *(float *)(iVar11 + 400) = fVar28;
            *(float *)(iVar11 + 0x194) = fVar30;
            fVar19 = fVar19 + local_108;
            iVar11 = *piVar5;
            fVar27 = local_104 - fVar27;
            uVar35 = CONCAT44(fVar27,fVar19);
            *(float *)(iVar11 + 0x198) = local_ec;
            *(float *)(iVar11 + 0x19c) = local_e8;
            iVar11 = *piVar5;
            *(float *)(iVar11 + 0x1a0) = local_f4;
            *(float *)(iVar11 + 0x1a4) = local_f0;
            iVar11 = *piVar5;
            *(float *)(iVar11 + 0x1a8) = fVar19;
            *(float *)(iVar11 + 0x1ac) = fVar27;
            iVar11 = *piVar5;
            if (*(int *)(iVar11 + 0x110) == 0) {
              uVar8 = FUN_005226b2(*(undefined4 *)(iVar11 + 0x8c));
              FUN_00516b34(fVar28,fVar30,local_ec,local_e8,local_f4,local_f0,fVar19,fVar27);
              goto LAB_0051a2d0;
            }
            bVar13 = -1 < (int)((uint)*(byte *)(iVar11 + 0x7d) << 0x1b);
            uVar8 = FUN_0052266e(bVar13,0,bVar13,0);
            iVar11 = *piVar5;
            if (0.0 < *(float *)(iVar11 + 0x184)) {
              FUN_00516b34(*(undefined4 *)(iVar11 + 0x164),*(undefined4 *)(iVar11 + 0x168),
                           *(undefined4 *)(iVar11 + 0x16c),*(undefined4 *)(iVar11 + 0x170),
                           *(undefined4 *)(iVar11 + 0x174),*(undefined4 *)(iVar11 + 0x178),
                           *(undefined4 *)(iVar11 + 0x17c),*(undefined4 *)(iVar11 + 0x180));
              iVar11 = *piVar5;
              if ((int)((uint)(ABS(*(float *)(iVar11 + 0x188) * fVar14 -
                                   *(float *)(iVar11 + 0x18c) * fVar16) < DAT_0051987c) << 0x1f) < 0
                 ) {
                uVar36 = *(undefined8 *)(iVar11 + 0x16c);
                uVar35 = *(undefined8 *)(iVar11 + 0x174);
              }
              else {
                uVar3 = *(undefined8 *)(iVar11 + 0x16c);
                local_cc = fVar28;
                local_c8 = fVar30;
                if (*(int *)(iVar11 + 0x110) != 0) {
                  cVar1 = *(char *)(iVar11 + 0x2e2);
                  uVar12 = 0;
                  fVar25 = (float)((ulonglong)*(undefined8 *)(iVar11 + 0x174) >> 0x20);
                  fVar23 = (float)((ulonglong)uVar3 >> 0x20);
                  fVar24 = (float)*(undefined8 *)(iVar11 + 0x174);
                  fVar22 = (float)uVar3;
                  if ((cVar1 == '\0') || (*(int *)(iVar11 + 0x118) != 0)) {
                    if (-1 < (int)((uint)*(byte *)(iVar11 + 0x7d) << 0x1b)) {
                      uVar12 = FUN_0052266e(1,0,1,0);
                    }
                    FUN_00516b34(fVar22,fVar23,local_cc,local_c8,fVar24,fVar25,fVar19,fVar27);
                    bVar2 = *(byte *)(*piVar5 + 0x7d);
joined_r0x00519764:
                    if (-1 < (int)((uint)bVar2 << 0x1b)) {
                      FUN_005226b2(uVar12);
                    }
                  }
                  else if (cVar1 == '\x02') {
                    local_fc = *DAT_0051a364;
                    local_f8 = DAT_0051a364[1];
                    iVar11 = FUN_00522f50(fVar22,fVar23,fVar24,fVar25,fVar28,fVar30,fVar19,fVar27,
                                          &local_fc,&local_f8);
                    if (iVar11 != 0) {
                      iVar11 = *piVar5;
                      fVar19 = (float)FUN_004397a8(*(float *)(iVar11 + 0xec) *
                                                   *(float *)(iVar11 + 0xec) +
                                                   *(float *)(iVar11 + 0xf0) *
                                                   *(float *)(iVar11 + 0xf0));
                      fVar27 = (float)FUN_004397a8(*(float *)(iVar11 + 0xf8) *
                                                   *(float *)(iVar11 + 0xf8) +
                                                   *(float *)(iVar11 + 0xfc) *
                                                   *(float *)(iVar11 + 0xfc));
                      fVar19 = ABS(fVar19);
                      bVar13 = NAN(fVar19) || NAN(DAT_00519880);
                      if (fVar19 < DAT_00519880) {
                        bVar13 = NAN(ABS(fVar27)) || NAN(DAT_00519880);
                      }
                      bVar13 = (fVar19 < DAT_00519880 && ABS(fVar27) < DAT_00519880) == bVar13;
                      if (bVar13) {
                        FUN_00522622(1);
                      }
                      if ((int)((uint)*(byte *)(*piVar5 + 0x7d) << 0x1b) < 0) {
                        FUN_00522fb4(local_fc,local_f8,*(float *)(*piVar5 + 0x2d8) * 0.5);
                      }
                      else {
                        FUN_00523284();
                      }
                      if (bVar13) {
                        FUN_00522622(0);
                      }
                    }
                  }
                  else {
                    if (cVar1 != '\x01') goto LAB_0051989a;
                    if (*(char *)(iVar11 + 0x2e4) == '\0') {
                      if ((*(float *)(iVar11 + 0x158) <= 0.0) || (*(int *)(iVar11 + 0x128) != 1)) {
                        local_98 = *(float *)(iVar11 + 0x164);
                        local_94 = *(float *)(iVar11 + 0x168);
                        local_90 = *(float *)(iVar11 + 0x16c);
                        local_8c = *(float *)(iVar11 + 0x170);
                        local_88 = *(float *)(iVar11 + 0x174);
                        local_84 = *(float *)(iVar11 + 0x178);
                        pfVar9 = (float *)(iVar11 + 400);
                        local_80 = *(float *)(iVar11 + 0x17c);
                        local_7c = *(float *)(iVar11 + 0x180);
                        uStack_78 = *(undefined4 *)(iVar11 + 0x184);
                        uStack_74 = *(undefined4 *)(iVar11 + 0x188);
                        uStack_70 = *(undefined4 *)(iVar11 + 0x18c);
                      }
                      else {
                        local_98 = *(float *)(iVar11 + 0x138);
                        local_94 = *(float *)(iVar11 + 0x13c);
                        local_90 = *(float *)(iVar11 + 0x140);
                        local_8c = *(float *)(iVar11 + 0x144);
                        local_88 = *(float *)(iVar11 + 0x148);
                        local_84 = *(float *)(iVar11 + 0x14c);
                        pfVar9 = (float *)(iVar11 + 400);
                        local_80 = *(float *)(iVar11 + 0x150);
                        local_7c = *(float *)(iVar11 + 0x154);
                        uStack_78 = *(undefined4 *)(iVar11 + 0x158);
                        uStack_74 = *(undefined4 *)(iVar11 + 0x15c);
                        uStack_70 = *(undefined4 *)(iVar11 + 0x160);
                      }
                    }
                    else {
                      local_98 = *(float *)(iVar11 + 0x334);
                      local_94 = *(float *)(iVar11 + 0x338);
                      local_90 = *(float *)(iVar11 + 0x33c);
                      local_8c = *(float *)(iVar11 + 0x340);
                      local_88 = *(float *)(iVar11 + 0x344);
                      local_84 = *(float *)(iVar11 + 0x348);
                      pfVar9 = (float *)(iVar11 + 0x308);
                      local_80 = *(float *)(iVar11 + 0x34c);
                      local_7c = *(float *)(iVar11 + 0x350);
                      uStack_78 = *(undefined4 *)(iVar11 + 0x354);
                      uStack_74 = *(undefined4 *)(iVar11 + 0x358);
                      uStack_70 = *(undefined4 *)(iVar11 + 0x35c);
                    }
                    local_c4 = *pfVar9;
                    local_c0 = pfVar9[1];
                    local_bc = pfVar9[2];
                    local_b8 = pfVar9[3];
                    local_b4 = pfVar9[4];
                    local_b0 = pfVar9[5];
                    local_ac = pfVar9[6];
                    local_a8 = pfVar9[7];
                    local_a4 = pfVar9[8];
                    local_a0 = pfVar9[9];
                    local_9c = pfVar9[10];
                    iVar11 = FUN_005177a4(&local_c4,&local_98,pfVar9 + 0xb);
                    if ((((iVar11 != 1) || (iVar11 = FUN_005177a4(&local_bc,&local_90), iVar11 != 1)
                         ) || (iVar11 = FUN_005177a4(&local_b4,&local_88), iVar11 != 1)) ||
                       (iVar11 = FUN_005177a4(&local_ac,&local_80), iVar11 != 1)) {
                      iVar11 = FUN_0051785c(&local_c4,&local_90);
                      if ((iVar11 != 0) || (iVar11 = FUN_0051785c(&local_98,&local_c4), iVar11 != 0)
                         ) goto LAB_0051999a;
                      iVar11 = FUN_0051785c(&local_c4,&local_88);
                      if ((iVar11 == 0) && (iVar11 = FUN_0051785c(&local_98,&local_ac), iVar11 == 0)
                         ) {
                        iVar11 = (uint)(local_84 < local_8c) << 0x1f;
                        if (local_c0 < local_8c) {
                          if (iVar11 < 0) goto LAB_00519aaa;
                        }
                        else if (-1 < iVar11) goto LAB_00519aaa;
LAB_0051999a:
                        local_d0 = local_80;
                        local_d4 = local_7c;
                        local_d8 = local_b4;
                        local_dc = local_b0;
                        fVar30 = local_90;
                        fVar15 = local_8c;
                        fVar20 = local_c4;
                        fVar31 = local_c0;
                        fVar21 = local_ac;
                        fVar32 = local_a8;
                        fVar28 = local_88;
                        fVar18 = local_84;
                      }
                      else {
LAB_00519aaa:
                        local_d4 = local_94;
                        local_d0 = local_98;
                        local_d8 = local_bc;
                        local_dc = local_b8;
                        fVar30 = local_88;
                        fVar15 = local_84;
                        fVar20 = local_ac;
                        fVar31 = local_a8;
                        fVar21 = local_c4;
                        fVar32 = local_c0;
                        fVar28 = local_90;
                        fVar18 = local_8c;
                      }
                      local_e4 = *DAT_0051a654;
                      local_e0 = DAT_0051a654[1];
                      local_fc = *DAT_0051a658;
                      local_f8 = DAT_0051a658[1];
                      iVar11 = FUN_00522f50(fVar28,fVar18,fVar30,fVar15,fVar21,fVar32,fVar20,fVar31,
                                            &local_e4,&local_e0);
                      iVar6 = FUN_00522f50(local_d0,local_d4,fVar28,fVar18,fVar21,fVar32,local_d8,
                                           local_dc,&local_fc,&local_f8);
                      fVar30 = (float)FUN_00524218((local_fc - local_e4) * (local_fc - local_e4) +
                                                   (local_f8 - local_e0) * (local_f8 - local_e0));
                      iVar7 = *piVar5;
                      if (((*(float *)(iVar7 + 0x2dc) * *(float *)(iVar7 + 0x2d8) < fVar30) ||
                          (iVar6 == 0)) || (iVar11 == 0)) {
                        fVar28 = local_cc;
                        fVar18 = local_c8;
                        fVar21 = fVar19;
                        fVar32 = fVar27;
                        if (-1 < (int)((uint)*(byte *)(iVar7 + 0x7d) << 0x1b)) {
                          uVar12 = FUN_0052266e(1,0,1,0);
                          fVar28 = local_cc;
                          fVar18 = local_c8;
                        }
                      }
                      else {
                        fVar22 = local_e4;
                        fVar23 = local_e0;
                        fVar24 = local_fc;
                        fVar25 = local_f8;
                        if (-1 < (int)((uint)*(byte *)(iVar7 + 0x7d) << 0x1b)) {
                          uVar12 = FUN_0052266e(0,1,1,0);
                          fVar22 = local_e4;
                          fVar23 = local_e0;
                          fVar24 = local_fc;
                          fVar25 = local_f8;
                        }
                      }
                      FUN_00516b34(fVar22,fVar23,fVar28,fVar18,fVar24,fVar25,fVar21,fVar32);
                      bVar2 = *(byte *)(*piVar5 + 0x7d);
                      goto joined_r0x00519764;
                    }
                  }
                }
              }
            }
            iVar11 = *piVar5;
            if ((0.0 < *(float *)(iVar11 + 0x158)) && (*(int *)(iVar11 + 0x128) == 1)) {
              if ((int)((uint)(ABS(*(float *)(iVar11 + 0x15c) * fVar14 -
                                   *(float *)(iVar11 + 0x160) * fVar16) < DAT_0051987c) << 0x1f) < 0
                 ) {
                uVar36 = *(undefined8 *)(iVar11 + 0x140);
                uVar35 = *(undefined8 *)(iVar11 + 0x148);
              }
              else {
                uVar3 = *(undefined8 *)(iVar11 + 0x140);
                fVar28 = (float)uVar36;
                fVar30 = (float)((ulonglong)uVar36 >> 0x20);
                fVar19 = (float)uVar35;
                fVar27 = (float)((ulonglong)uVar35 >> 0x20);
                if (*(int *)(iVar11 + 0x110) != 0) {
                  cVar1 = *(char *)(iVar11 + 0x2e2);
                  uVar12 = 0;
                  fVar25 = (float)((ulonglong)*(undefined8 *)(iVar11 + 0x148) >> 0x20);
                  fVar23 = (float)((ulonglong)uVar3 >> 0x20);
                  fVar24 = (float)*(undefined8 *)(iVar11 + 0x148);
                  fVar22 = (float)uVar3;
                  if ((cVar1 == '\0') || (*(int *)(iVar11 + 0x118) != 0)) {
                    if (-1 < (int)((uint)*(byte *)(iVar11 + 0x7d) << 0x1b)) {
                      uVar12 = FUN_0052266e(1,0,1,0);
                    }
                    FUN_00516b34(fVar22,fVar23,fVar28,fVar30,fVar24,fVar25,fVar19,fVar27);
                    bVar2 = *(byte *)(*piVar5 + 0x7d);
joined_r0x00519bf4:
                    if (-1 < (int)((uint)bVar2 << 0x1b)) {
                      FUN_005226b2(uVar12);
                    }
                  }
                  else if (cVar1 == '\x02') {
                    local_fc = *DAT_0051a364;
                    local_f8 = DAT_0051a364[1];
                    iVar11 = FUN_00522f50(fVar22,fVar23,fVar24,fVar25,fVar28,fVar30,fVar19,fVar27,
                                          &local_fc,&local_f8);
                    if (iVar11 != 0) {
                      iVar11 = *piVar5;
                      fVar19 = (float)FUN_004397a8(*(float *)(iVar11 + 0xec) *
                                                   *(float *)(iVar11 + 0xec) +
                                                   *(float *)(iVar11 + 0xf0) *
                                                   *(float *)(iVar11 + 0xf0));
                      fVar27 = (float)FUN_004397a8(*(float *)(iVar11 + 0xf8) *
                                                   *(float *)(iVar11 + 0xf8) +
                                                   *(float *)(iVar11 + 0xfc) *
                                                   *(float *)(iVar11 + 0xfc));
                      fVar19 = ABS(fVar19);
                      bVar13 = NAN(fVar19) || NAN(DAT_00519ed4);
                      if (fVar19 < DAT_00519ed4) {
                        bVar13 = NAN(ABS(fVar27)) || NAN(DAT_00519ed4);
                      }
                      bVar13 = (fVar19 < DAT_00519ed4 && ABS(fVar27) < DAT_00519ed4) == bVar13;
                      if (bVar13) {
                        FUN_00522622(1);
                      }
                      if ((int)((uint)*(byte *)(*piVar5 + 0x7d) << 0x1b) < 0) {
                        FUN_00522fb4(local_fc,local_f8,*(float *)(*piVar5 + 0x2d8) * 0.5);
                      }
                      else {
                        FUN_00523284();
                      }
                      if (bVar13) {
                        FUN_00522622(0);
                      }
                    }
                  }
                  else {
                    if (cVar1 != '\x01') {
LAB_0051989a:
                      *(undefined4 *)(iVar11 + 0x114) = 0;
                      *(undefined4 *)(iVar11 + 0x118) = 0;
                      FUN_0051565c(0x1000000);
                      iVar10 = *piVar5;
                      *(undefined4 *)(iVar10 + 0x114) = 0;
                      *(undefined4 *)(iVar10 + 0x118) = 0;
                      FUN_0051565c(0x1000000);
                      return 0x1000000;
                    }
                    if (*(char *)(iVar11 + 0x2e4) == '\0') {
                      local_a8 = *(float *)(iVar11 + 0x138);
                      local_a4 = *(float *)(iVar11 + 0x13c);
                      local_a0 = *(float *)(iVar11 + 0x140);
                      local_9c = *(float *)(iVar11 + 0x144);
                      local_98 = *(float *)(iVar11 + 0x148);
                      local_94 = *(float *)(iVar11 + 0x14c);
                      pfVar9 = (float *)(iVar11 + 400);
                      local_90 = *(float *)(iVar11 + 0x150);
                      local_8c = *(float *)(iVar11 + 0x154);
                      local_88 = *(float *)(iVar11 + 0x158);
                      local_84 = *(float *)(iVar11 + 0x15c);
                      local_80 = *(float *)(iVar11 + 0x160);
                    }
                    else {
                      local_a8 = *(float *)(iVar11 + 0x334);
                      local_a4 = *(float *)(iVar11 + 0x338);
                      local_a0 = *(float *)(iVar11 + 0x33c);
                      local_9c = *(float *)(iVar11 + 0x340);
                      local_98 = *(float *)(iVar11 + 0x344);
                      local_94 = *(float *)(iVar11 + 0x348);
                      pfVar9 = (float *)(iVar11 + 0x308);
                      local_90 = *(float *)(iVar11 + 0x34c);
                      local_8c = *(float *)(iVar11 + 0x350);
                      local_88 = *(float *)(iVar11 + 0x354);
                      local_84 = *(float *)(iVar11 + 0x358);
                      local_80 = *(float *)(iVar11 + 0x35c);
                    }
                    local_d4 = *pfVar9;
                    local_d0 = pfVar9[1];
                    local_cc = pfVar9[2];
                    local_c8 = pfVar9[3];
                    local_c4 = pfVar9[4];
                    local_c0 = pfVar9[5];
                    local_bc = pfVar9[6];
                    local_b8 = pfVar9[7];
                    local_b4 = pfVar9[8];
                    local_b0 = pfVar9[9];
                    local_ac = pfVar9[10];
                    iVar11 = FUN_005177a4(&local_d4,&local_a8,pfVar9 + 0xb);
                    if ((((iVar11 != 1) || (iVar11 = FUN_005177a4(&local_cc,&local_a0), iVar11 != 1)
                         ) || (iVar11 = FUN_005177a4(&local_c4,&local_98), iVar11 != 1)) ||
                       (iVar11 = FUN_005177a4(&local_bc,&local_90), iVar11 != 1)) {
                      iVar11 = FUN_0051785c(&local_d4,&local_a0);
                      if ((iVar11 != 0) || (iVar11 = FUN_0051785c(&local_a8,&local_d4), iVar11 != 0)
                         ) goto LAB_00519dd2;
                      iVar11 = FUN_0051785c(&local_d4,&local_98);
                      if ((iVar11 == 0) && (iVar11 = FUN_0051785c(&local_a8,&local_bc), iVar11 == 0)
                         ) {
                        iVar11 = (uint)(local_94 < local_9c) << 0x1f;
                        if (local_d0 < local_9c) {
                          if (iVar11 < 0) goto LAB_00519ef6;
                        }
                        else if (-1 < iVar11) goto LAB_00519ef6;
LAB_00519dd2:
                        local_d8 = local_90;
                        local_dc = local_8c;
                        fVar15 = local_a0;
                        fVar20 = local_9c;
                        fVar31 = local_d4;
                        fVar33 = local_d0;
                        fVar38 = local_c0;
                        fVar39 = local_c4;
                        fVar32 = local_bc;
                        fVar34 = local_b8;
                        fVar18 = local_98;
                        fVar21 = local_94;
                      }
                      else {
LAB_00519ef6:
                        local_dc = local_a4;
                        local_d8 = local_a8;
                        fVar15 = local_98;
                        fVar20 = local_94;
                        fVar31 = local_bc;
                        fVar33 = local_b8;
                        fVar38 = local_c8;
                        fVar39 = local_cc;
                        fVar32 = local_d4;
                        fVar34 = local_d0;
                        fVar18 = local_a0;
                        fVar21 = local_9c;
                      }
                      local_e4 = *DAT_0051a654;
                      local_e0 = DAT_0051a654[1];
                      local_fc = *DAT_0051a658;
                      local_f8 = DAT_0051a658[1];
                      iVar11 = FUN_00522f50(fVar18,fVar21,fVar15,fVar20,fVar32,fVar34,fVar31,fVar33,
                                            &local_e4,&local_e0);
                      iVar6 = FUN_00522f50(local_d8,local_dc,fVar18,fVar21,fVar32,fVar34,fVar39,
                                           fVar38,&local_fc,&local_f8);
                      fVar15 = (float)FUN_00524218((local_fc - local_e4) * (local_fc - local_e4) +
                                                   (local_f8 - local_e0) * (local_f8 - local_e0));
                      iVar7 = *piVar5;
                      if (((*(float *)(iVar7 + 0x2dc) * *(float *)(iVar7 + 0x2d8) < fVar15) ||
                          (iVar6 == 0)) || (iVar11 == 0)) {
                        fVar18 = fVar28;
                        fVar21 = fVar30;
                        fVar32 = fVar19;
                        fVar34 = fVar27;
                        if (-1 < (int)((uint)*(byte *)(iVar7 + 0x7d) << 0x1b)) {
                          uVar12 = FUN_0052266e(1,0,1,0);
                        }
                      }
                      else {
                        fVar22 = local_e4;
                        fVar23 = local_e0;
                        fVar24 = local_fc;
                        fVar25 = local_f8;
                        if (-1 < (int)((uint)*(byte *)(iVar7 + 0x7d) << 0x1b)) {
                          uVar12 = FUN_0052266e(0,1,1,0);
                          fVar22 = local_e4;
                          fVar23 = local_e0;
                          fVar24 = local_fc;
                          fVar25 = local_f8;
                        }
                      }
                      FUN_00516b34(fVar22,fVar23,fVar18,fVar21,fVar24,fVar25,fVar32,fVar34);
                      bVar2 = *(byte *)(*piVar5 + 0x7d);
                      goto joined_r0x00519bf4;
                    }
                  }
                }
              }
            }
            iVar11 = *piVar5;
            *(int *)(iVar11 + 0x128) = *(int *)(iVar11 + 0x128) + 1;
            uVar37 = (undefined4)((ulonglong)uVar36 >> 0x20);
            uVar12 = (undefined4)((ulonglong)uVar35 >> 0x20);
            if (*(float *)(iVar11 + 0x158) == 0.0) {
              *(int *)(iVar11 + 0x138) = (int)uVar36;
              *(undefined4 *)(iVar11 + 0x13c) = uVar37;
              iVar11 = *piVar5;
              *(float *)(iVar11 + 0x140) = local_ec;
              *(float *)(iVar11 + 0x144) = local_e8;
              iVar11 = *piVar5;
              *(float *)(iVar11 + 0x148) = local_f4;
              *(float *)(iVar11 + 0x14c) = local_f0;
              iVar11 = *piVar5;
              *(int *)(iVar11 + 0x150) = (int)uVar35;
              *(undefined4 *)(iVar11 + 0x154) = uVar12;
              iVar11 = *piVar5;
              *(float *)(iVar11 + 0x158) = fVar17;
              *(float *)(iVar11 + 0x15c) = fVar16;
              *(float *)(iVar11 + 0x160) = fVar14;
            }
            else {
              *(int *)(iVar11 + 0x164) = (int)uVar36;
              *(undefined4 *)(iVar11 + 0x168) = uVar37;
              iVar11 = *piVar5;
              *(float *)(iVar11 + 0x16c) = local_ec;
              *(float *)(iVar11 + 0x170) = local_e8;
              iVar11 = *piVar5;
              *(float *)(iVar11 + 0x174) = local_f4;
              *(float *)(iVar11 + 0x178) = local_f0;
              iVar11 = *piVar5;
              *(int *)(iVar11 + 0x17c) = (int)uVar35;
              *(undefined4 *)(iVar11 + 0x180) = uVar12;
              iVar11 = *piVar5;
              *(float *)(iVar11 + 0x184) = fVar17;
              *(float *)(iVar11 + 0x188) = fVar16;
              *(float *)(iVar11 + 0x18c) = fVar14;
            }
            goto LAB_0051a2d0;
          }
          *(float *)(iVar11 + 0x198) = local_108;
          *(float *)(iVar11 + 0x19c) = local_104 + *(float *)(iVar11 + 0x130) * -0.5;
          *(float *)(iVar11 + 0x1a0) = local_108;
LAB_005194b4:
          *(float *)(iVar11 + 0x1a4) = local_104 + *(float *)(iVar11 + 0x130) * 0.5;
          *(undefined4 *)(iVar11 + 400) = *(undefined4 *)(iVar11 + 0x198);
          *(undefined4 *)(iVar11 + 0x194) = *(undefined4 *)(iVar11 + 0x19c);
          iVar11 = *piVar5;
          *(undefined4 *)(iVar11 + 0x1a8) = *(undefined4 *)(iVar11 + 0x1a0);
          *(undefined4 *)(iVar11 + 0x1ac) = *(undefined4 *)(iVar11 + 0x1a4);
        }
        else {
          fVar14 = fVar29 - local_108;
          fVar16 = fVar26 - local_104;
          if ((int)((uint)(ABS(fVar14 * fVar14 + fVar16 * fVar16) < DAT_005194ec) << 0x1f) < 0) {
            *(float *)(iVar11 + 0x198) = local_108;
            *(float *)(iVar11 + 0x19c) = local_104 + *(float *)(iVar11 + 0x130) * -0.5;
            *(float *)(iVar11 + 0x1a0) = local_108;
            goto LAB_005194b4;
          }
          fVar17 = (float)FUN_004397a8();
          fVar14 = fVar14 * (1.0 / fVar17);
          fVar16 = fVar16 * (1.0 / fVar17);
          fVar19 = *(float *)(iVar11 + 0x130) * 0.5 * fVar16;
          fVar28 = local_108 - fVar19;
          fVar27 = *(float *)(iVar11 + 0x134) * 0.5 * fVar14;
          fVar30 = fVar27 + local_104;
          uVar36 = CONCAT44(fVar30,fVar28);
          *(float *)(iVar11 + 400) = fVar28;
          *(float *)(iVar11 + 0x194) = fVar30;
          iVar11 = *piVar5;
          fVar22 = fVar29 - fVar19;
          fVar23 = fVar27 + fVar26;
          *(float *)(iVar11 + 0x198) = fVar22;
          *(float *)(iVar11 + 0x19c) = fVar23;
          iVar11 = *piVar5;
          fVar24 = fVar19 + fVar29;
          fVar25 = fVar26 - fVar27;
          *(float *)(iVar11 + 0x1a0) = fVar24;
          *(float *)(iVar11 + 0x1a4) = fVar25;
          iVar11 = *piVar5;
          fVar19 = fVar19 + local_108;
          fVar27 = local_104 - fVar27;
          uVar35 = CONCAT44(fVar27,fVar19);
          *(float *)(iVar11 + 0x1a8) = fVar19;
          *(float *)(iVar11 + 0x1ac) = fVar27;
          iVar11 = *piVar5;
          if (*(int *)(iVar11 + 0x110) == 0) {
            uVar8 = FUN_005226b2(*(undefined4 *)(iVar11 + 0x8c));
            FUN_00516b34(fVar28,fVar30,fVar22,fVar23,fVar24,fVar25,fVar19,fVar27);
          }
          else {
            bVar13 = -1 < (int)((uint)*(byte *)(iVar11 + 0x7d) << 0x1b);
            uVar8 = FUN_0052266e(bVar13,0,bVar13,0);
            iVar11 = *piVar5;
            if (0.0 < *(float *)(iVar11 + 0x184)) {
              FUN_00516b34(*(undefined4 *)(iVar11 + 0x164),*(undefined4 *)(iVar11 + 0x168),
                           *(undefined4 *)(iVar11 + 0x16c),*(undefined4 *)(iVar11 + 0x170),
                           *(undefined4 *)(iVar11 + 0x174),*(undefined4 *)(iVar11 + 0x178),
                           *(undefined4 *)(iVar11 + 0x17c),*(undefined4 *)(iVar11 + 0x180));
              iVar11 = *piVar5;
              if ((int)((uint)(ABS(*(float *)(iVar11 + 0x188) * fVar16 -
                                   *(float *)(iVar11 + 0x18c) * fVar14) < DAT_0051a360) << 0x1f) < 0
                 ) {
                uVar36 = *(undefined8 *)(iVar11 + 0x16c);
                uVar35 = *(undefined8 *)(iVar11 + 0x174);
              }
              else {
                FUN_00516b34(*(undefined4 *)(iVar11 + 0x16c),*(undefined4 *)(iVar11 + 0x170),fVar28,
                             fVar30,*(undefined4 *)(iVar11 + 0x174),*(undefined4 *)(iVar11 + 0x178),
                             fVar19,fVar27);
              }
            }
            iVar11 = *piVar5;
            if ((0.0 < *(float *)(iVar11 + 0x158)) && (*(int *)(iVar11 + 0x128) == 1)) {
              if ((int)((uint)(ABS(*(float *)(iVar11 + 0x15c) * fVar16 -
                                   *(float *)(iVar11 + 0x160) * fVar14) < DAT_0051a360) << 0x1f) < 0
                 ) {
                uVar36 = *(undefined8 *)(iVar11 + 0x140);
                uVar35 = *(undefined8 *)(iVar11 + 0x148);
              }
              else {
                FUN_00516b34(*(undefined4 *)(iVar11 + 0x140),*(undefined4 *)(iVar11 + 0x144),
                             (int)uVar36,(int)((ulonglong)uVar36 >> 0x20),
                             *(undefined4 *)(iVar11 + 0x148),*(undefined4 *)(iVar11 + 0x14c),
                             (int)uVar35,(int)((ulonglong)uVar35 >> 0x20));
              }
            }
            iVar11 = *piVar5;
            *(int *)(iVar11 + 0x128) = *(int *)(iVar11 + 0x128) + 1;
            uVar37 = (undefined4)((ulonglong)uVar36 >> 0x20);
            uVar12 = (undefined4)((ulonglong)uVar35 >> 0x20);
            if (*(float *)(iVar11 + 0x158) == 0.0) {
              *(int *)(iVar11 + 0x138) = (int)uVar36;
              *(undefined4 *)(iVar11 + 0x13c) = uVar37;
              iVar11 = *piVar5;
              *(float *)(iVar11 + 0x140) = fVar22;
              *(float *)(iVar11 + 0x144) = fVar23;
              iVar11 = *piVar5;
              *(float *)(iVar11 + 0x148) = fVar24;
              *(float *)(iVar11 + 0x14c) = fVar25;
              iVar11 = *piVar5;
              *(int *)(iVar11 + 0x150) = (int)uVar35;
              *(undefined4 *)(iVar11 + 0x154) = uVar12;
              iVar11 = *piVar5;
              *(float *)(iVar11 + 0x158) = fVar17;
              *(float *)(iVar11 + 0x15c) = fVar14;
              *(float *)(iVar11 + 0x160) = fVar16;
            }
            else {
              *(int *)(iVar11 + 0x164) = (int)uVar36;
              *(undefined4 *)(iVar11 + 0x168) = uVar37;
              iVar11 = *piVar5;
              *(float *)(iVar11 + 0x16c) = fVar22;
              *(float *)(iVar11 + 0x170) = fVar23;
              iVar11 = *piVar5;
              *(float *)(iVar11 + 0x174) = fVar24;
              *(float *)(iVar11 + 0x178) = fVar25;
              iVar11 = *piVar5;
              *(int *)(iVar11 + 0x17c) = (int)uVar35;
              *(undefined4 *)(iVar11 + 0x180) = uVar12;
              iVar11 = *piVar5;
              *(float *)(iVar11 + 0x184) = fVar17;
              *(float *)(iVar11 + 0x188) = fVar14;
              *(float *)(iVar11 + 0x18c) = fVar16;
            }
          }
LAB_0051a2d0:
          FUN_005226b2(uVar8);
        }
        fVar14 = local_120 - fVar29;
        fVar16 = local_11c - fVar26;
        if ((int)((uint)(ABS(fVar14 * fVar14 + fVar16 * fVar16) < DAT_0051a650) << 0x1f) < 0) {
          iVar11 = *piVar5;
          *(float *)(iVar11 + 0x198) = fVar29;
          *(float *)(iVar11 + 0x19c) = fVar26 + *(float *)(iVar11 + 0x130) * -0.5;
          *(float *)(iVar11 + 0x1a0) = fVar29;
          *(float *)(iVar11 + 0x1a4) = fVar26 + *(float *)(iVar11 + 0x130) * 0.5;
          *(undefined4 *)(iVar11 + 400) = *(undefined4 *)(iVar11 + 0x198);
          *(undefined4 *)(iVar11 + 0x194) = *(undefined4 *)(iVar11 + 0x19c);
          iVar11 = *piVar5;
          *(undefined4 *)(iVar11 + 0x1a8) = *(undefined4 *)(iVar11 + 0x1a0);
          *(undefined4 *)(iVar11 + 0x1ac) = *(undefined4 *)(iVar11 + 0x1a4);
        }
        else {
          fVar17 = (float)FUN_004397a8();
          iVar11 = *piVar5;
          fVar14 = fVar14 * (1.0 / fVar17);
          fVar16 = fVar16 * (1.0 / fVar17);
          fVar19 = *(float *)(iVar11 + 0x130) * 0.5 * fVar16;
          fVar28 = fVar29 - fVar19;
          fVar27 = *(float *)(iVar11 + 0x134) * 0.5 * fVar14;
          fVar30 = fVar27 + fVar26;
          uVar36 = CONCAT44(fVar30,fVar28);
          *(float *)(iVar11 + 400) = fVar28;
          *(float *)(iVar11 + 0x194) = fVar30;
          iVar11 = *piVar5;
          fVar22 = local_120 - fVar19;
          fVar23 = fVar27 + local_11c;
          *(float *)(iVar11 + 0x198) = fVar22;
          *(float *)(iVar11 + 0x19c) = fVar23;
          iVar11 = *piVar5;
          fVar24 = fVar19 + local_120;
          fVar25 = local_11c - fVar27;
          *(float *)(iVar11 + 0x1a0) = fVar24;
          *(float *)(iVar11 + 0x1a4) = fVar25;
          iVar11 = *piVar5;
          fVar19 = fVar19 + fVar29;
          fVar26 = fVar26 - fVar27;
          uVar35 = CONCAT44(fVar26,fVar19);
          *(float *)(iVar11 + 0x1a8) = fVar19;
          *(float *)(iVar11 + 0x1ac) = fVar26;
          iVar11 = *piVar5;
          if (*(int *)(iVar11 + 0x110) == 0) {
            uVar8 = FUN_005226b2(*(undefined4 *)(iVar11 + 0x8c));
            FUN_00516b34(fVar28,fVar30,fVar22,fVar23,fVar24,fVar25,fVar19,fVar26);
          }
          else {
            bVar13 = -1 < (int)((uint)*(byte *)(iVar11 + 0x7d) << 0x1b);
            uVar8 = FUN_0052266e(bVar13,0,bVar13,0);
            iVar11 = *piVar5;
            if (0.0 < *(float *)(iVar11 + 0x184)) {
              FUN_00516b34(*(undefined4 *)(iVar11 + 0x164),*(undefined4 *)(iVar11 + 0x168),
                           *(undefined4 *)(iVar11 + 0x16c),*(undefined4 *)(iVar11 + 0x170),
                           *(undefined4 *)(iVar11 + 0x174),*(undefined4 *)(iVar11 + 0x178),
                           *(undefined4 *)(iVar11 + 0x17c),*(undefined4 *)(iVar11 + 0x180));
              iVar11 = *piVar5;
              if ((int)((uint)(ABS(*(float *)(iVar11 + 0x188) * fVar16 -
                                   *(float *)(iVar11 + 0x18c) * fVar14) < DAT_0051a65c) << 0x1f) < 0
                 ) {
                uVar36 = *(undefined8 *)(iVar11 + 0x16c);
                uVar35 = *(undefined8 *)(iVar11 + 0x174);
              }
              else {
                FUN_00516b34(*(undefined4 *)(iVar11 + 0x16c),*(undefined4 *)(iVar11 + 0x170),fVar28,
                             fVar30,*(undefined4 *)(iVar11 + 0x174),*(undefined4 *)(iVar11 + 0x178),
                             fVar19,fVar26);
              }
            }
            iVar11 = *piVar5;
            if ((0.0 < *(float *)(iVar11 + 0x158)) && (*(int *)(iVar11 + 0x128) == 1)) {
              if ((int)((uint)(ABS(*(float *)(iVar11 + 0x15c) * fVar16 -
                                   *(float *)(iVar11 + 0x160) * fVar14) < DAT_0051a65c) << 0x1f) < 0
                 ) {
                uVar36 = *(undefined8 *)(iVar11 + 0x140);
                uVar35 = *(undefined8 *)(iVar11 + 0x148);
              }
              else {
                FUN_00516b34(*(undefined4 *)(iVar11 + 0x140),*(undefined4 *)(iVar11 + 0x144),
                             (int)uVar36,(int)((ulonglong)uVar36 >> 0x20),
                             *(undefined4 *)(iVar11 + 0x148),*(undefined4 *)(iVar11 + 0x14c),
                             (int)uVar35,(int)((ulonglong)uVar35 >> 0x20));
              }
            }
            iVar11 = *piVar5;
            *(int *)(iVar11 + 0x128) = *(int *)(iVar11 + 0x128) + 1;
            uVar37 = (undefined4)((ulonglong)uVar36 >> 0x20);
            uVar12 = (undefined4)((ulonglong)uVar35 >> 0x20);
            if (*(float *)(iVar11 + 0x158) == 0.0) {
              *(int *)(iVar11 + 0x138) = (int)uVar36;
              *(undefined4 *)(iVar11 + 0x13c) = uVar37;
              iVar11 = *piVar5;
              *(float *)(iVar11 + 0x140) = fVar22;
              *(float *)(iVar11 + 0x144) = fVar23;
              iVar11 = *piVar5;
              *(float *)(iVar11 + 0x148) = fVar24;
              *(float *)(iVar11 + 0x14c) = fVar25;
              iVar11 = *piVar5;
              *(int *)(iVar11 + 0x150) = (int)uVar35;
              *(undefined4 *)(iVar11 + 0x154) = uVar12;
              iVar11 = *piVar5;
              *(float *)(iVar11 + 0x158) = fVar17;
              *(float *)(iVar11 + 0x15c) = fVar14;
              *(float *)(iVar11 + 0x160) = fVar16;
            }
            else {
              *(int *)(iVar11 + 0x164) = (int)uVar36;
              *(undefined4 *)(iVar11 + 0x168) = uVar37;
              iVar11 = *piVar5;
              *(float *)(iVar11 + 0x16c) = fVar22;
              *(float *)(iVar11 + 0x170) = fVar23;
              iVar11 = *piVar5;
              *(float *)(iVar11 + 0x174) = fVar24;
              *(float *)(iVar11 + 0x178) = fVar25;
              iVar11 = *piVar5;
              *(int *)(iVar11 + 0x17c) = (int)uVar35;
              *(undefined4 *)(iVar11 + 0x180) = uVar12;
              iVar11 = *piVar5;
              *(float *)(iVar11 + 0x184) = fVar17;
              *(float *)(iVar11 + 0x188) = fVar14;
              *(float *)(iVar11 + 0x18c) = fVar16;
            }
          }
          FUN_005226b2(uVar8);
        }
      }
      else {
        iVar11 = FUN_005639e8(local_108,local_104,fVar29,fVar26);
        if ((iVar11 != 0) || (iVar11 = FUN_005639e8(fVar29,fVar26,local_120,local_11c), iVar11 != 0)
           ) {
          iVar10 = *piVar5;
          *(undefined4 *)(iVar10 + 0x114) = 0;
          *(undefined4 *)(iVar10 + 0x118) = 0;
          FUN_0051565c(iVar11);
          return iVar11;
        }
      }
      iVar11 = *piVar5;
      if (*(int *)(iVar11 + 700) != 0) {
        iVar6 = *(int *)(iVar11 + 700) + -1;
        *(int *)(iVar11 + 700) = iVar6;
        iVar11 = iVar11 + iVar6 * 0x18;
        local_108 = *(float *)(iVar11 + 0x1cc);
        local_104 = *(float *)(iVar11 + 0x1d0);
        local_10c = *(float *)(iVar11 + 0x1d4);
        local_110 = *(float *)(iVar11 + 0x1d8);
        local_120 = *(float *)(iVar11 + 0x1dc);
        local_11c = *(float *)(iVar11 + 0x1e0);
      }
    }
    else {
      if (fVar30 <= fVar27 * 0.5) goto LAB_00519504;
LAB_00519384:
      if (*(int *)(iVar11 + 700) < 10) {
        *(float *)(iVar11 + *(int *)(iVar11 + 700) * 0x18 + 0x1cc) = fVar29;
        *(float *)(iVar11 + *(int *)(iVar11 + 700) * 0x18 + 0x1d0) = fVar26;
        *(float *)(iVar11 + *(int *)(iVar11 + 700) * 0x18 + 0x1d4) = fVar17;
        *(float *)(iVar11 + *(int *)(iVar11 + 700) * 0x18 + 0x1d8) = fVar19;
        *(float *)(iVar11 + *(int *)(iVar11 + 700) * 0x18 + 0x1dc) = local_120;
        *(float *)(iVar11 + *(int *)(iVar11 + 700) * 0x18 + 0x1e0) = local_11c;
        *(int *)(iVar11 + 700) = *(int *)(iVar11 + 700) + 1;
      }
      iVar10 = iVar10 + 1;
      local_120 = fVar29;
      local_11c = fVar26;
      local_110 = fVar16;
      local_10c = fVar14;
    }
    if (iVar10 == 0) {
      return 0;
    }
  } while( true );
}

