
int FUN_00517e18(float param_1,float param_2,float param_3,float param_4,float param_5,float param_6
                ,float param_7,float param_8)

{
  char cVar1;
  byte bVar2;
  bool bVar3;
  undefined8 uVar4;
  int *piVar5;
  int iVar6;
  int iVar7;
  undefined4 uVar8;
  float *pfVar9;
  int iVar10;
  int iVar11;
  undefined4 uVar12;
  bool bVar13;
  bool bVar14;
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
  float fVar35;
  undefined8 uVar36;
  undefined8 uVar37;
  undefined4 uVar38;
  float fVar39;
  float fVar40;
  float local_120;
  float local_11c;
  float local_118;
  float local_114;
  float local_110;
  float local_10c;
  float local_104;
  float local_100;
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
  
  piVar5 = DAT_00518b14;
  iVar10 = 1;
  bVar3 = true;
  bVar13 = true;
  local_120 = param_7;
  local_11c = param_8;
  local_118 = param_6;
  local_114 = param_5;
  local_110 = param_4;
  local_10c = param_3;
  local_104 = param_1;
  local_100 = param_2;
  do {
    fVar15 = (local_104 + local_10c) * 0.5;
    fVar17 = (local_100 + local_110) * 0.5;
    fVar28 = (local_10c + local_114) * 0.5;
    fVar32 = (local_110 + local_118) * 0.5;
    fVar18 = (local_114 + local_120) * 0.5;
    fVar20 = (local_118 + local_11c) * 0.5;
    fVar26 = (fVar15 + fVar28) * 0.5;
    fVar27 = (fVar17 + fVar32) * 0.5;
    fVar29 = (fVar28 + fVar18) * 0.5;
    fVar32 = (fVar32 + fVar20) * 0.5;
    fVar35 = (fVar26 + fVar29) * 0.5;
    fVar28 = (fVar27 + fVar32) * 0.5;
    iVar11 = *piVar5;
    if ((((!bVar3) && (ABS((local_104 + local_120) * 0.5 - fVar35) < 0.5)) &&
        (ABS((local_100 + local_11c) * 0.5 - fVar28) < 0.5)) || (9 < *(int *)(iVar11 + 700))) {
      iVar10 = iVar10 + -1;
      if (*(char *)(iVar11 + 0x2e4) == '\0') {
        if ((bVar13) && (*(char *)(iVar11 + 0x1c0) == '\x01')) {
          fVar17 = fVar35 - local_104;
          fVar15 = fVar28 - local_100;
          if ((int)((uint)(ABS(fVar17 * fVar17 + fVar15 * fVar15) < DAT_005183f8) << 0x1f) < 0) {
            *(float *)(iVar11 + 0x198) = local_104;
            *(float *)(iVar11 + 0x19c) = local_100 + *(float *)(iVar11 + 0x130) * -0.5;
            *(float *)(iVar11 + 0x1a0) = local_104;
            *(float *)(iVar11 + 0x1a4) = local_100 + *(float *)(iVar11 + 0x130) * 0.5;
            *(undefined4 *)(iVar11 + 400) = *(undefined4 *)(iVar11 + 0x198);
            *(undefined4 *)(iVar11 + 0x194) = *(undefined4 *)(iVar11 + 0x19c);
            iVar11 = *piVar5;
            bVar13 = false;
            *(undefined4 *)(iVar11 + 0x1a8) = *(undefined4 *)(iVar11 + 0x1a0);
            *(undefined4 *)(iVar11 + 0x1ac) = *(undefined4 *)(iVar11 + 0x1a4);
          }
          else {
            fVar18 = (float)FUN_004397a8();
            fVar17 = fVar17 * (1.0 / fVar18);
            fVar15 = fVar15 * (1.0 / fVar18);
            fVar20 = *(float *)(iVar11 + 0x130) * 0.5 * fVar15;
            fVar27 = local_104 - fVar20;
            fVar26 = *(float *)(iVar11 + 0x134) * 0.5 * fVar17;
            fVar29 = fVar26 + local_100;
            uVar37 = CONCAT44(fVar29,fVar27);
            local_ec = fVar35 - fVar20;
            local_e8 = fVar26 + fVar28;
            local_f4 = fVar20 + fVar35;
            local_f0 = fVar28 - fVar26;
            *(float *)(iVar11 + 400) = fVar27;
            *(float *)(iVar11 + 0x194) = fVar29;
            fVar20 = fVar20 + local_104;
            iVar11 = *piVar5;
            fVar26 = local_100 - fVar26;
            uVar36 = CONCAT44(fVar26,fVar20);
            *(float *)(iVar11 + 0x198) = local_ec;
            *(float *)(iVar11 + 0x19c) = local_e8;
            iVar11 = *piVar5;
            *(float *)(iVar11 + 0x1a0) = local_f4;
            *(float *)(iVar11 + 0x1a4) = local_f0;
            iVar11 = *piVar5;
            *(float *)(iVar11 + 0x1a8) = fVar20;
            *(float *)(iVar11 + 0x1ac) = fVar26;
            iVar11 = *piVar5;
            if (*(int *)(iVar11 + 0x110) == 0) {
              uVar8 = FUN_005226b2(*(undefined4 *)(iVar11 + 0x8c));
              FUN_00516b34(fVar27,fVar29,local_ec,local_e8,local_f4,local_f0,fVar20,fVar26);
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
                if ((int)((uint)(ABS(*(float *)(iVar11 + 0x188) * fVar15 -
                                     *(float *)(iVar11 + 0x18c) * fVar17) < DAT_005184bc) << 0x1f) <
                    0) {
                  uVar37 = *(undefined8 *)(iVar11 + 0x16c);
                  uVar36 = *(undefined8 *)(iVar11 + 0x174);
                }
                else {
                  uVar4 = *(undefined8 *)(iVar11 + 0x16c);
                  local_cc = fVar27;
                  local_c8 = fVar29;
                  if (*(int *)(iVar11 + 0x110) != 0) {
                    cVar1 = *(char *)(iVar11 + 0x2e2);
                    uVar12 = 0;
                    fVar25 = (float)((ulonglong)*(undefined8 *)(iVar11 + 0x174) >> 0x20);
                    fVar23 = (float)((ulonglong)uVar4 >> 0x20);
                    fVar24 = (float)*(undefined8 *)(iVar11 + 0x174);
                    fVar32 = (float)uVar4;
                    if ((cVar1 == '\0') || (*(int *)(iVar11 + 0x118) != 0)) {
                      if (-1 < (int)((uint)*(byte *)(iVar11 + 0x7d) << 0x1b)) {
                        uVar12 = FUN_0052266e(1,0,1,0);
                      }
                      FUN_00516b34(fVar32,fVar23,local_cc,local_c8,fVar24,fVar25,fVar20,fVar26);
                      bVar2 = *(byte *)(*piVar5 + 0x7d);
joined_r0x005183a0:
                      if (-1 < (int)((uint)bVar2 << 0x1b)) {
                        FUN_005226b2(uVar12);
                      }
                    }
                    else if (cVar1 == '\x02') {
                      local_fc = *DAT_00519198;
                      local_f8 = DAT_00519198[1];
                      iVar11 = FUN_00522f50(fVar32,fVar23,fVar24,fVar25,fVar27,fVar29,fVar20,fVar26,
                                            &local_fc,&local_f8);
                      if (iVar11 != 0) {
                        iVar11 = *piVar5;
                        fVar20 = (float)FUN_004397a8(*(float *)(iVar11 + 0xec) *
                                                     *(float *)(iVar11 + 0xec) +
                                                     *(float *)(iVar11 + 0xf0) *
                                                     *(float *)(iVar11 + 0xf0));
                        fVar26 = (float)FUN_004397a8(*(float *)(iVar11 + 0xf8) *
                                                     *(float *)(iVar11 + 0xf8) +
                                                     *(float *)(iVar11 + 0xfc) *
                                                     *(float *)(iVar11 + 0xfc));
                        fVar20 = ABS(fVar20);
                        bVar13 = NAN(fVar20) || NAN(DAT_005184c0);
                        if (fVar20 < DAT_005184c0) {
                          bVar13 = NAN(ABS(fVar26)) || NAN(DAT_005184c0);
                        }
                        bVar13 = (fVar20 < DAT_005184c0 && ABS(fVar26) < DAT_005184c0) == bVar13;
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
                      if (cVar1 != '\x01') goto LAB_005184da;
                      if (*(char *)(iVar11 + 0x2e4) == '\0') {
                        if ((*(float *)(iVar11 + 0x158) <= 0.0) || (*(int *)(iVar11 + 0x128) != 1))
                        {
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
                      if ((((iVar11 != 1) ||
                           (iVar11 = FUN_005177a4(&local_bc,&local_90), iVar11 != 1)) ||
                          (iVar11 = FUN_005177a4(&local_b4,&local_88), iVar11 != 1)) ||
                         (iVar11 = FUN_005177a4(&local_ac,&local_80), iVar11 != 1)) {
                        iVar11 = FUN_0051785c(&local_c4,&local_90);
                        if ((iVar11 != 0) ||
                           (iVar11 = FUN_0051785c(&local_98,&local_c4), iVar11 != 0))
                        goto LAB_005185da;
                        iVar11 = FUN_0051785c(&local_c4,&local_88);
                        if ((iVar11 == 0) &&
                           (iVar11 = FUN_0051785c(&local_98,&local_ac), iVar11 == 0)) {
                          iVar11 = (uint)(local_84 < local_8c) << 0x1f;
                          if (local_c0 < local_8c) {
                            if (iVar11 < 0) goto LAB_005186ea;
                          }
                          else if (-1 < iVar11) goto LAB_005186ea;
LAB_005185da:
                          local_d0 = local_80;
                          local_d4 = local_7c;
                          local_d8 = local_b4;
                          local_dc = local_b0;
                          fVar29 = local_90;
                          fVar16 = local_8c;
                          fVar21 = local_c4;
                          fVar30 = local_c0;
                          fVar22 = local_ac;
                          fVar31 = local_a8;
                          fVar27 = local_88;
                          fVar19 = local_84;
                        }
                        else {
LAB_005186ea:
                          local_d4 = local_94;
                          local_d0 = local_98;
                          local_d8 = local_bc;
                          local_dc = local_b8;
                          fVar29 = local_88;
                          fVar16 = local_84;
                          fVar21 = local_ac;
                          fVar30 = local_a8;
                          fVar22 = local_c4;
                          fVar31 = local_c0;
                          fVar27 = local_90;
                          fVar19 = local_8c;
                        }
                        local_e4 = *DAT_00519284;
                        local_e0 = DAT_00519284[1];
                        local_fc = *DAT_00519288;
                        local_f8 = DAT_00519288[1];
                        iVar11 = FUN_00522f50(fVar27,fVar19,fVar29,fVar16,fVar22,fVar31,fVar21,
                                              fVar30,&local_e4,&local_e0);
                        iVar6 = FUN_00522f50(local_d0,local_d4,fVar27,fVar19,fVar22,fVar31,local_d8,
                                             local_dc,&local_fc,&local_f8);
                        fVar29 = (float)FUN_00524218((local_fc - local_e4) * (local_fc - local_e4) +
                                                     (local_f8 - local_e0) * (local_f8 - local_e0));
                        iVar7 = *piVar5;
                        if (((*(float *)(iVar7 + 0x2dc) * *(float *)(iVar7 + 0x2d8) < fVar29) ||
                            (iVar6 == 0)) || (iVar11 == 0)) {
                          fVar27 = local_cc;
                          fVar19 = local_c8;
                          fVar22 = fVar20;
                          fVar31 = fVar26;
                          if (-1 < (int)((uint)*(byte *)(iVar7 + 0x7d) << 0x1b)) {
                            uVar12 = FUN_0052266e(1,0,1,0);
                            fVar27 = local_cc;
                            fVar19 = local_c8;
                          }
                        }
                        else {
                          fVar32 = local_e4;
                          fVar23 = local_e0;
                          fVar24 = local_fc;
                          fVar25 = local_f8;
                          if (-1 < (int)((uint)*(byte *)(iVar7 + 0x7d) << 0x1b)) {
                            uVar12 = FUN_0052266e(0,1,1,0);
                            fVar32 = local_e4;
                            fVar23 = local_e0;
                            fVar24 = local_fc;
                            fVar25 = local_f8;
                          }
                        }
                        FUN_00516b34(fVar32,fVar23,fVar27,fVar19,fVar24,fVar25,fVar22,fVar31);
                        bVar2 = *(byte *)(*piVar5 + 0x7d);
                        goto joined_r0x005183a0;
                      }
                    }
                  }
                }
              }
              iVar11 = *piVar5;
              if ((0.0 < *(float *)(iVar11 + 0x158)) && (*(int *)(iVar11 + 0x128) == 1)) {
                if ((int)((uint)(ABS(*(float *)(iVar11 + 0x15c) * fVar15 -
                                     *(float *)(iVar11 + 0x160) * fVar17) < DAT_005184bc) << 0x1f) <
                    0) {
                  uVar37 = *(undefined8 *)(iVar11 + 0x140);
                  uVar36 = *(undefined8 *)(iVar11 + 0x148);
                }
                else {
                  uVar4 = *(undefined8 *)(iVar11 + 0x140);
                  fVar27 = (float)uVar37;
                  fVar29 = (float)((ulonglong)uVar37 >> 0x20);
                  fVar20 = (float)uVar36;
                  fVar26 = (float)((ulonglong)uVar36 >> 0x20);
                  if (*(int *)(iVar11 + 0x110) != 0) {
                    cVar1 = *(char *)(iVar11 + 0x2e2);
                    uVar12 = 0;
                    fVar25 = (float)((ulonglong)*(undefined8 *)(iVar11 + 0x148) >> 0x20);
                    fVar23 = (float)((ulonglong)uVar4 >> 0x20);
                    fVar24 = (float)*(undefined8 *)(iVar11 + 0x148);
                    fVar32 = (float)uVar4;
                    if ((cVar1 == '\0') || (*(int *)(iVar11 + 0x118) != 0)) {
                      if (-1 < (int)((uint)*(byte *)(iVar11 + 0x7d) << 0x1b)) {
                        uVar12 = FUN_0052266e(1,0,1,0);
                      }
                      FUN_00516b34(fVar32,fVar23,fVar27,fVar29,fVar24,fVar25,fVar20,fVar26);
                      bVar2 = *(byte *)(*piVar5 + 0x7d);
joined_r0x00518834:
                      if (-1 < (int)((uint)bVar2 << 0x1b)) {
                        FUN_005226b2(uVar12);
                      }
                    }
                    else if (cVar1 == '\x02') {
                      local_fc = *DAT_00519198;
                      local_f8 = DAT_00519198[1];
                      iVar11 = FUN_00522f50(fVar32,fVar23,fVar24,fVar25,fVar27,fVar29,fVar20,fVar26,
                                            &local_fc,&local_f8);
                      if (iVar11 != 0) {
                        iVar11 = *piVar5;
                        fVar20 = (float)FUN_004397a8(*(float *)(iVar11 + 0xec) *
                                                     *(float *)(iVar11 + 0xec) +
                                                     *(float *)(iVar11 + 0xf0) *
                                                     *(float *)(iVar11 + 0xf0));
                        fVar26 = (float)FUN_004397a8(*(float *)(iVar11 + 0xf8) *
                                                     *(float *)(iVar11 + 0xf8) +
                                                     *(float *)(iVar11 + 0xfc) *
                                                     *(float *)(iVar11 + 0xfc));
                        fVar20 = ABS(fVar20);
                        bVar13 = NAN(fVar20) || NAN(DAT_00518b18);
                        if (fVar20 < DAT_00518b18) {
                          bVar13 = NAN(ABS(fVar26)) || NAN(DAT_00518b18);
                        }
                        bVar13 = (fVar20 < DAT_00518b18 && ABS(fVar26) < DAT_00518b18) == bVar13;
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
LAB_005184da:
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
                      if ((((iVar11 != 1) ||
                           (iVar11 = FUN_005177a4(&local_cc,&local_a0), iVar11 != 1)) ||
                          (iVar11 = FUN_005177a4(&local_c4,&local_98), iVar11 != 1)) ||
                         (iVar11 = FUN_005177a4(&local_bc,&local_90), iVar11 != 1)) {
                        iVar11 = FUN_0051785c(&local_d4,&local_a0);
                        if ((iVar11 != 0) ||
                           (iVar11 = FUN_0051785c(&local_a8,&local_d4), iVar11 != 0))
                        goto LAB_00518a12;
                        iVar11 = FUN_0051785c(&local_d4,&local_98);
                        if ((iVar11 == 0) &&
                           (iVar11 = FUN_0051785c(&local_a8,&local_bc), iVar11 == 0)) {
                          iVar11 = (uint)(local_94 < local_9c) << 0x1f;
                          if (local_d0 < local_9c) {
                            if (iVar11 < 0) goto LAB_00518b36;
                          }
                          else if (-1 < iVar11) goto LAB_00518b36;
LAB_00518a12:
                          local_d8 = local_90;
                          local_dc = local_8c;
                          fVar16 = local_a0;
                          fVar21 = local_9c;
                          fVar30 = local_d4;
                          fVar33 = local_d0;
                          fVar39 = local_c0;
                          fVar40 = local_c4;
                          fVar31 = local_bc;
                          fVar34 = local_b8;
                          fVar19 = local_98;
                          fVar22 = local_94;
                        }
                        else {
LAB_00518b36:
                          local_dc = local_a4;
                          local_d8 = local_a8;
                          fVar16 = local_98;
                          fVar21 = local_94;
                          fVar30 = local_bc;
                          fVar33 = local_b8;
                          fVar39 = local_c8;
                          fVar40 = local_cc;
                          fVar31 = local_d4;
                          fVar34 = local_d0;
                          fVar19 = local_a0;
                          fVar22 = local_9c;
                        }
                        local_e4 = *DAT_00519284;
                        local_e0 = DAT_00519284[1];
                        local_fc = *DAT_00519288;
                        local_f8 = DAT_00519288[1];
                        iVar11 = FUN_00522f50(fVar19,fVar22,fVar16,fVar21,fVar31,fVar34,fVar30,
                                              fVar33,&local_e4,&local_e0);
                        iVar6 = FUN_00522f50(local_d8,local_dc,fVar19,fVar22,fVar31,fVar34,fVar40,
                                             fVar39,&local_fc,&local_f8);
                        fVar16 = (float)FUN_00524218((local_fc - local_e4) * (local_fc - local_e4) +
                                                     (local_f8 - local_e0) * (local_f8 - local_e0));
                        iVar7 = *piVar5;
                        if (((*(float *)(iVar7 + 0x2dc) * *(float *)(iVar7 + 0x2d8) < fVar16) ||
                            (iVar6 == 0)) || (iVar11 == 0)) {
                          fVar19 = fVar27;
                          fVar22 = fVar29;
                          fVar31 = fVar20;
                          fVar34 = fVar26;
                          if (-1 < (int)((uint)*(byte *)(iVar7 + 0x7d) << 0x1b)) {
                            uVar12 = FUN_0052266e(1,0,1,0);
                          }
                        }
                        else {
                          fVar32 = local_e4;
                          fVar23 = local_e0;
                          fVar24 = local_fc;
                          fVar25 = local_f8;
                          if (-1 < (int)((uint)*(byte *)(iVar7 + 0x7d) << 0x1b)) {
                            uVar12 = FUN_0052266e(0,1,1,0);
                            fVar32 = local_e4;
                            fVar23 = local_e0;
                            fVar24 = local_fc;
                            fVar25 = local_f8;
                          }
                        }
                        FUN_00516b34(fVar32,fVar23,fVar19,fVar22,fVar24,fVar25,fVar31,fVar34);
                        bVar2 = *(byte *)(*piVar5 + 0x7d);
                        goto joined_r0x00518834;
                      }
                    }
                  }
                }
              }
              iVar11 = *piVar5;
              *(int *)(iVar11 + 0x128) = *(int *)(iVar11 + 0x128) + 1;
              uVar38 = (undefined4)((ulonglong)uVar37 >> 0x20);
              uVar12 = (undefined4)((ulonglong)uVar36 >> 0x20);
              if (*(float *)(iVar11 + 0x158) == 0.0) {
                *(int *)(iVar11 + 0x138) = (int)uVar37;
                *(undefined4 *)(iVar11 + 0x13c) = uVar38;
                iVar11 = *piVar5;
                *(float *)(iVar11 + 0x140) = local_ec;
                *(float *)(iVar11 + 0x144) = local_e8;
                iVar11 = *piVar5;
                *(float *)(iVar11 + 0x148) = local_f4;
                *(float *)(iVar11 + 0x14c) = local_f0;
                iVar11 = *piVar5;
                *(int *)(iVar11 + 0x150) = (int)uVar36;
                *(undefined4 *)(iVar11 + 0x154) = uVar12;
                iVar11 = *piVar5;
                *(float *)(iVar11 + 0x158) = fVar18;
                *(float *)(iVar11 + 0x15c) = fVar17;
                *(float *)(iVar11 + 0x160) = fVar15;
              }
              else {
                *(int *)(iVar11 + 0x164) = (int)uVar37;
                *(undefined4 *)(iVar11 + 0x168) = uVar38;
                iVar11 = *piVar5;
                *(float *)(iVar11 + 0x16c) = local_ec;
                *(float *)(iVar11 + 0x170) = local_e8;
                iVar11 = *piVar5;
                *(float *)(iVar11 + 0x174) = local_f4;
                *(float *)(iVar11 + 0x178) = local_f0;
                iVar11 = *piVar5;
                *(int *)(iVar11 + 0x17c) = (int)uVar36;
                *(undefined4 *)(iVar11 + 0x180) = uVar12;
                iVar11 = *piVar5;
                *(float *)(iVar11 + 0x184) = fVar18;
                *(float *)(iVar11 + 0x188) = fVar17;
                *(float *)(iVar11 + 0x18c) = fVar15;
              }
            }
            FUN_005226b2(uVar8);
            bVar13 = false;
          }
        }
        else {
          fVar15 = fVar35 - local_104;
          fVar17 = fVar28 - local_100;
          if ((int)((uint)(ABS(fVar15 * fVar15 + fVar17 * fVar17) < DAT_005183f8) << 0x1f) < 0) {
            *(float *)(iVar11 + 0x198) = local_104;
            *(float *)(iVar11 + 0x19c) = local_100 + *(float *)(iVar11 + 0x130) * -0.5;
            *(float *)(iVar11 + 0x1a0) = local_104;
            *(float *)(iVar11 + 0x1a4) = local_100 + *(float *)(iVar11 + 0x130) * 0.5;
            *(undefined4 *)(iVar11 + 400) = *(undefined4 *)(iVar11 + 0x198);
            *(undefined4 *)(iVar11 + 0x194) = *(undefined4 *)(iVar11 + 0x19c);
            iVar11 = *piVar5;
            *(undefined4 *)(iVar11 + 0x1a8) = *(undefined4 *)(iVar11 + 0x1a0);
            *(undefined4 *)(iVar11 + 0x1ac) = *(undefined4 *)(iVar11 + 0x1a4);
          }
          else {
            fVar18 = (float)FUN_004397a8();
            fVar15 = fVar15 * (1.0 / fVar18);
            fVar17 = fVar17 * (1.0 / fVar18);
            fVar20 = *(float *)(iVar11 + 0x130) * 0.5 * fVar17;
            fVar27 = local_104 - fVar20;
            fVar26 = *(float *)(iVar11 + 0x134) * 0.5 * fVar15;
            fVar29 = fVar26 + local_100;
            uVar37 = CONCAT44(fVar29,fVar27);
            *(float *)(iVar11 + 400) = fVar27;
            *(float *)(iVar11 + 0x194) = fVar29;
            iVar11 = *piVar5;
            fVar32 = fVar35 - fVar20;
            fVar23 = fVar26 + fVar28;
            *(float *)(iVar11 + 0x198) = fVar32;
            *(float *)(iVar11 + 0x19c) = fVar23;
            iVar11 = *piVar5;
            fVar24 = fVar20 + fVar35;
            fVar25 = fVar28 - fVar26;
            *(float *)(iVar11 + 0x1a0) = fVar24;
            *(float *)(iVar11 + 0x1a4) = fVar25;
            iVar11 = *piVar5;
            fVar20 = fVar20 + local_104;
            fVar26 = local_100 - fVar26;
            uVar36 = CONCAT44(fVar26,fVar20);
            *(float *)(iVar11 + 0x1a8) = fVar20;
            *(float *)(iVar11 + 0x1ac) = fVar26;
            iVar11 = *piVar5;
            if (*(int *)(iVar11 + 0x110) == 0) {
              uVar8 = FUN_005226b2(*(undefined4 *)(iVar11 + 0x8c));
              FUN_00516b34(fVar27,fVar29,fVar32,fVar23,fVar24,fVar25,fVar20,fVar26);
            }
            else {
              bVar14 = -1 < (int)((uint)*(byte *)(iVar11 + 0x7d) << 0x1b);
              uVar8 = FUN_0052266e(bVar14,0,bVar14,0);
              iVar11 = *piVar5;
              if (0.0 < *(float *)(iVar11 + 0x184)) {
                FUN_00516b34(*(undefined4 *)(iVar11 + 0x164),*(undefined4 *)(iVar11 + 0x168),
                             *(undefined4 *)(iVar11 + 0x16c),*(undefined4 *)(iVar11 + 0x170),
                             *(undefined4 *)(iVar11 + 0x174),*(undefined4 *)(iVar11 + 0x178),
                             *(undefined4 *)(iVar11 + 0x17c),*(undefined4 *)(iVar11 + 0x180));
                iVar11 = *piVar5;
                if ((int)((uint)(ABS(*(float *)(iVar11 + 0x188) * fVar17 -
                                     *(float *)(iVar11 + 0x18c) * fVar15) < DAT_00519194) << 0x1f) <
                    0) {
                  uVar37 = *(undefined8 *)(iVar11 + 0x16c);
                  uVar36 = *(undefined8 *)(iVar11 + 0x174);
                }
                else {
                  FUN_00516b34(*(undefined4 *)(iVar11 + 0x16c),*(undefined4 *)(iVar11 + 0x170),
                               fVar27,fVar29,*(undefined4 *)(iVar11 + 0x174),
                               *(undefined4 *)(iVar11 + 0x178),fVar20,fVar26);
                }
              }
              iVar11 = *piVar5;
              if ((0.0 < *(float *)(iVar11 + 0x158)) && (*(int *)(iVar11 + 0x128) == 1)) {
                if ((int)((uint)(ABS(*(float *)(iVar11 + 0x15c) * fVar17 -
                                     *(float *)(iVar11 + 0x160) * fVar15) < DAT_00519194) << 0x1f) <
                    0) {
                  uVar37 = *(undefined8 *)(iVar11 + 0x140);
                  uVar36 = *(undefined8 *)(iVar11 + 0x148);
                }
                else {
                  FUN_00516b34(*(undefined4 *)(iVar11 + 0x140),*(undefined4 *)(iVar11 + 0x144),
                               (int)uVar37,(int)((ulonglong)uVar37 >> 0x20),
                               *(undefined4 *)(iVar11 + 0x148),*(undefined4 *)(iVar11 + 0x14c),
                               (int)uVar36,(int)((ulonglong)uVar36 >> 0x20));
                }
              }
              iVar11 = *piVar5;
              *(int *)(iVar11 + 0x128) = *(int *)(iVar11 + 0x128) + 1;
              uVar38 = (undefined4)((ulonglong)uVar37 >> 0x20);
              uVar12 = (undefined4)((ulonglong)uVar36 >> 0x20);
              if (*(float *)(iVar11 + 0x158) == 0.0) {
                *(int *)(iVar11 + 0x138) = (int)uVar37;
                *(undefined4 *)(iVar11 + 0x13c) = uVar38;
                iVar11 = *piVar5;
                *(float *)(iVar11 + 0x140) = fVar32;
                *(float *)(iVar11 + 0x144) = fVar23;
                iVar11 = *piVar5;
                *(float *)(iVar11 + 0x148) = fVar24;
                *(float *)(iVar11 + 0x14c) = fVar25;
                iVar11 = *piVar5;
                *(int *)(iVar11 + 0x150) = (int)uVar36;
                *(undefined4 *)(iVar11 + 0x154) = uVar12;
                iVar11 = *piVar5;
                *(float *)(iVar11 + 0x158) = fVar18;
                *(float *)(iVar11 + 0x15c) = fVar15;
                *(float *)(iVar11 + 0x160) = fVar17;
              }
              else {
                *(int *)(iVar11 + 0x164) = (int)uVar37;
                *(undefined4 *)(iVar11 + 0x168) = uVar38;
                iVar11 = *piVar5;
                *(float *)(iVar11 + 0x16c) = fVar32;
                *(float *)(iVar11 + 0x170) = fVar23;
                iVar11 = *piVar5;
                *(float *)(iVar11 + 0x174) = fVar24;
                *(float *)(iVar11 + 0x178) = fVar25;
                iVar11 = *piVar5;
                *(int *)(iVar11 + 0x17c) = (int)uVar36;
                *(undefined4 *)(iVar11 + 0x180) = uVar12;
                iVar11 = *piVar5;
                *(float *)(iVar11 + 0x184) = fVar18;
                *(float *)(iVar11 + 0x188) = fVar15;
                *(float *)(iVar11 + 0x18c) = fVar17;
              }
            }
            FUN_005226b2(uVar8);
          }
        }
        fVar15 = local_120 - fVar35;
        fVar17 = local_11c - fVar28;
        if ((int)((uint)(ABS(fVar15 * fVar15 + fVar17 * fVar17) < DAT_00519280) << 0x1f) < 0) {
          iVar11 = *piVar5;
          *(float *)(iVar11 + 0x198) = fVar35;
          *(float *)(iVar11 + 0x19c) = fVar28 + *(float *)(iVar11 + 0x130) * -0.5;
          *(float *)(iVar11 + 0x1a0) = fVar35;
          *(float *)(iVar11 + 0x1a4) = fVar28 + *(float *)(iVar11 + 0x130) * 0.5;
          *(undefined4 *)(iVar11 + 400) = *(undefined4 *)(iVar11 + 0x198);
          *(undefined4 *)(iVar11 + 0x194) = *(undefined4 *)(iVar11 + 0x19c);
          iVar11 = *piVar5;
          *(undefined4 *)(iVar11 + 0x1a8) = *(undefined4 *)(iVar11 + 0x1a0);
          *(undefined4 *)(iVar11 + 0x1ac) = *(undefined4 *)(iVar11 + 0x1a4);
        }
        else {
          fVar18 = (float)FUN_004397a8();
          iVar11 = *piVar5;
          fVar15 = fVar15 * (1.0 / fVar18);
          fVar17 = fVar17 * (1.0 / fVar18);
          fVar20 = *(float *)(iVar11 + 0x130) * 0.5 * fVar17;
          fVar27 = fVar35 - fVar20;
          fVar26 = *(float *)(iVar11 + 0x134) * 0.5 * fVar15;
          fVar29 = fVar26 + fVar28;
          uVar37 = CONCAT44(fVar29,fVar27);
          *(float *)(iVar11 + 400) = fVar27;
          *(float *)(iVar11 + 0x194) = fVar29;
          iVar11 = *piVar5;
          fVar32 = local_120 - fVar20;
          fVar23 = fVar26 + local_11c;
          *(float *)(iVar11 + 0x198) = fVar32;
          *(float *)(iVar11 + 0x19c) = fVar23;
          iVar11 = *piVar5;
          fVar24 = fVar20 + local_120;
          fVar25 = local_11c - fVar26;
          *(float *)(iVar11 + 0x1a0) = fVar24;
          *(float *)(iVar11 + 0x1a4) = fVar25;
          iVar11 = *piVar5;
          fVar20 = fVar20 + fVar35;
          fVar28 = fVar28 - fVar26;
          uVar36 = CONCAT44(fVar28,fVar20);
          *(float *)(iVar11 + 0x1a8) = fVar20;
          *(float *)(iVar11 + 0x1ac) = fVar28;
          iVar11 = *piVar5;
          if (*(int *)(iVar11 + 0x110) == 0) {
            uVar8 = FUN_005226b2(*(undefined4 *)(iVar11 + 0x8c));
            FUN_00516b34(fVar27,fVar29,fVar32,fVar23,fVar24,fVar25,fVar20,fVar28);
          }
          else {
            bVar14 = -1 < (int)((uint)*(byte *)(iVar11 + 0x7d) << 0x1b);
            uVar8 = FUN_0052266e(bVar14,0,bVar14,0);
            iVar11 = *piVar5;
            if (0.0 < *(float *)(iVar11 + 0x184)) {
              FUN_00516b34(*(undefined4 *)(iVar11 + 0x164),*(undefined4 *)(iVar11 + 0x168),
                           *(undefined4 *)(iVar11 + 0x16c),*(undefined4 *)(iVar11 + 0x170),
                           *(undefined4 *)(iVar11 + 0x174),*(undefined4 *)(iVar11 + 0x178),
                           *(undefined4 *)(iVar11 + 0x17c),*(undefined4 *)(iVar11 + 0x180));
              iVar11 = *piVar5;
              if ((int)((uint)(ABS(*(float *)(iVar11 + 0x188) * fVar17 -
                                   *(float *)(iVar11 + 0x18c) * fVar15) < DAT_00519194) << 0x1f) < 0
                 ) {
                uVar37 = *(undefined8 *)(iVar11 + 0x16c);
                uVar36 = *(undefined8 *)(iVar11 + 0x174);
              }
              else {
                FUN_00516b34(*(undefined4 *)(iVar11 + 0x16c),*(undefined4 *)(iVar11 + 0x170),fVar27,
                             fVar29,*(undefined4 *)(iVar11 + 0x174),*(undefined4 *)(iVar11 + 0x178),
                             fVar20,fVar28);
              }
            }
            iVar11 = *piVar5;
            if ((0.0 < *(float *)(iVar11 + 0x158)) && (*(int *)(iVar11 + 0x128) == 1)) {
              if ((int)((uint)(ABS(*(float *)(iVar11 + 0x15c) * fVar17 -
                                   *(float *)(iVar11 + 0x160) * fVar15) < DAT_0051928c) << 0x1f) < 0
                 ) {
                uVar37 = *(undefined8 *)(iVar11 + 0x140);
                uVar36 = *(undefined8 *)(iVar11 + 0x148);
              }
              else {
                FUN_00516b34(*(undefined4 *)(iVar11 + 0x140),*(undefined4 *)(iVar11 + 0x144),
                             (int)uVar37,(int)((ulonglong)uVar37 >> 0x20),
                             *(undefined4 *)(iVar11 + 0x148),*(undefined4 *)(iVar11 + 0x14c),
                             (int)uVar36,(int)((ulonglong)uVar36 >> 0x20));
              }
            }
            iVar11 = *piVar5;
            *(int *)(iVar11 + 0x128) = *(int *)(iVar11 + 0x128) + 1;
            uVar38 = (undefined4)((ulonglong)uVar37 >> 0x20);
            uVar12 = (undefined4)((ulonglong)uVar36 >> 0x20);
            if (*(float *)(iVar11 + 0x158) == 0.0) {
              *(int *)(iVar11 + 0x138) = (int)uVar37;
              *(undefined4 *)(iVar11 + 0x13c) = uVar38;
              iVar11 = *piVar5;
              *(float *)(iVar11 + 0x140) = fVar32;
              *(float *)(iVar11 + 0x144) = fVar23;
              iVar11 = *piVar5;
              *(float *)(iVar11 + 0x148) = fVar24;
              *(float *)(iVar11 + 0x14c) = fVar25;
              iVar11 = *piVar5;
              *(int *)(iVar11 + 0x150) = (int)uVar36;
              *(undefined4 *)(iVar11 + 0x154) = uVar12;
              iVar11 = *piVar5;
              *(float *)(iVar11 + 0x158) = fVar18;
              *(float *)(iVar11 + 0x15c) = fVar15;
              *(float *)(iVar11 + 0x160) = fVar17;
            }
            else {
              *(int *)(iVar11 + 0x164) = (int)uVar37;
              *(undefined4 *)(iVar11 + 0x168) = uVar38;
              iVar11 = *piVar5;
              *(float *)(iVar11 + 0x16c) = fVar32;
              *(float *)(iVar11 + 0x170) = fVar23;
              iVar11 = *piVar5;
              *(float *)(iVar11 + 0x174) = fVar24;
              *(float *)(iVar11 + 0x178) = fVar25;
              iVar11 = *piVar5;
              *(int *)(iVar11 + 0x17c) = (int)uVar36;
              *(undefined4 *)(iVar11 + 0x180) = uVar12;
              iVar11 = *piVar5;
              *(float *)(iVar11 + 0x184) = fVar18;
              *(float *)(iVar11 + 0x188) = fVar15;
              *(float *)(iVar11 + 0x18c) = fVar17;
            }
          }
          FUN_005226b2(uVar8);
        }
      }
      else {
        iVar11 = FUN_005639e8(local_104,local_100,fVar35,fVar28);
        if ((iVar11 != 0) || (iVar11 = FUN_005639e8(fVar35,fVar28,local_120,local_11c), iVar11 != 0)
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
        local_10c = *(float *)(iVar11 + 0x1cc);
        local_110 = *(float *)(iVar11 + 0x1d0);
        local_114 = *(float *)(iVar11 + 0x1d4);
        local_118 = *(float *)(iVar11 + 0x1d8);
        local_104 = local_120;
        local_100 = local_11c;
        local_120 = *(float *)(iVar11 + 0x1dc);
        local_11c = *(float *)(iVar11 + 0x1e0);
      }
    }
    else {
      bVar3 = false;
      *(float *)(iVar11 + *(int *)(iVar11 + 700) * 0x18 + 0x1cc) = fVar29;
      iVar10 = iVar10 + 1;
      *(float *)(iVar11 + *(int *)(iVar11 + 700) * 0x18 + 0x1d0) = fVar32;
      *(float *)(iVar11 + *(int *)(iVar11 + 700) * 0x18 + 0x1d4) = fVar18;
      *(float *)(iVar11 + *(int *)(iVar11 + 700) * 0x18 + 0x1d8) = fVar20;
      *(float *)(iVar11 + *(int *)(iVar11 + 700) * 0x18 + 0x1dc) = local_120;
      *(float *)(iVar11 + *(int *)(iVar11 + 700) * 0x18 + 0x1e0) = local_11c;
      *(int *)(iVar11 + 700) = *(int *)(iVar11 + 700) + 1;
      local_120 = fVar35;
      local_11c = fVar28;
      local_118 = fVar27;
      local_114 = fVar26;
      local_110 = fVar17;
      local_10c = fVar15;
    }
    if (iVar10 == 0) {
      return 0;
    }
  } while( true );
}

