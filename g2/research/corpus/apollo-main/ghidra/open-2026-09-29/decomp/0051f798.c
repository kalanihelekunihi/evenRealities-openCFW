
int FUN_0051f798(uint *param_1)

{
  char cVar1;
  byte bVar2;
  undefined8 uVar3;
  undefined8 uVar4;
  undefined8 uVar5;
  int *piVar6;
  int iVar7;
  undefined4 uVar8;
  int iVar9;
  int iVar10;
  int iVar11;
  undefined4 *puVar12;
  byte bVar13;
  undefined4 uVar14;
  uint uVar15;
  undefined4 uVar16;
  undefined4 uVar17;
  undefined4 uVar18;
  bool bVar19;
  float fVar20;
  float fVar21;
  float extraout_s1;
  float extraout_s1_00;
  float extraout_s1_01;
  float fVar22;
  float extraout_s1_02;
  float extraout_s1_03;
  float extraout_s2;
  float extraout_s2_00;
  float extraout_s2_01;
  float fVar23;
  float fVar24;
  float extraout_s2_02;
  float extraout_s2_03;
  float extraout_s3;
  float extraout_s3_00;
  float extraout_s3_01;
  float extraout_s3_02;
  float extraout_s3_03;
  float extraout_s3_04;
  float extraout_s3_05;
  float extraout_s3_06;
  float extraout_s4;
  float extraout_s4_00;
  float extraout_s4_01;
  float fVar25;
  float extraout_s4_02;
  float extraout_s4_03;
  float fVar26;
  undefined4 uVar27;
  float fVar28;
  undefined4 uVar29;
  float fVar30;
  float fVar31;
  undefined4 uVar32;
  undefined4 uVar33;
  undefined4 uVar34;
  undefined4 uVar35;
  float local_118;
  float local_114;
  float local_110;
  float local_10c;
  undefined4 local_108;
  float local_104;
  undefined4 local_100;
  undefined4 local_fc;
  undefined4 local_f8;
  undefined4 local_f4;
  undefined4 local_f0;
  float local_ec;
  undefined4 uStack_e8;
  undefined4 uStack_e4;
  undefined4 uStack_e0;
  undefined4 local_dc;
  undefined4 local_d8;
  undefined4 local_d4;
  float local_d0;
  undefined4 local_cc;
  float local_c8;
  undefined4 local_c4;
  undefined4 local_c0;
  undefined4 uStack_bc;
  undefined4 uStack_b8;
  undefined4 uStack_b4;
  undefined1 local_b0;
  char local_af;
  char local_ae;
  undefined4 local_a4;
  undefined4 uStack_a0;
  undefined4 local_9c;
  undefined4 uStack_98;
  undefined4 local_94;
  undefined4 uStack_90;
  undefined4 local_8c;
  undefined4 uStack_88;
  
  piVar6 = DAT_005202e8;
  iVar11 = *DAT_005202e8;
  FUN_0048949c(&local_b0,0x48);
  local_b0 = 1;
  local_ae = '\x01';
  local_af = '\x01';
  uVar15 = 0;
  FUN_0056395c();
LAB_0051f7ee:
  do {
    do {
      do {
        while( true ) {
          if (*param_1 <= uVar15) {
            return 0;
          }
          bVar2 = *(byte *)(param_1[2] + uVar15);
          uVar15 = uVar15 + 1;
          iVar7 = FUN_005156b8(param_1,bVar2,&local_b0);
          bVar13 = bVar2 & 0x6f;
          if (iVar7 != 0) goto LAB_0051f812;
          if (uVar15 == *param_1) {
            *(undefined1 *)(*piVar6 + 0x1c1) = 1;
          }
          else {
            *(bool *)(*piVar6 + 0x1c1) = *(char *)(param_1[2] + uVar15) == '\x01';
          }
          *(byte *)(iVar11 + 0x2e9) = (byte)(-(uint)(local_af == '\0') >> 0x1f);
          if ((local_ae == '\0') && (-1 < (int)((uint)bVar2 << 0x18))) break;
          iVar7 = *piVar6;
          if (*(char *)(iVar7 + 0x2e7) != '\0') {
            *(undefined4 *)(iVar7 + 0x2f8) = 0;
            *(undefined4 *)(iVar7 + 0x304) = *(undefined4 *)(iVar7 + 0x300);
          }
          *(undefined1 *)(iVar11 + 0x2e8) = 0;
          *(undefined4 *)(iVar11 + 0x2fc) = 0;
          *(undefined1 *)(iVar11 + 0x2e5) = 1;
        }
        if ((bVar13 == 6) || (bVar13 == 8)) {
          *(undefined1 *)(iVar11 + 0x2ea) = 1;
          FUN_00517e18(local_a4,uStack_a0,local_94,uStack_90,local_8c,uStack_88,local_9c,uStack_98);
          fVar22 = extraout_s1_00;
          fVar23 = extraout_s2_00;
          fVar20 = extraout_s3_00;
          fVar25 = extraout_s4_00;
        }
        else if ((bVar13 == 5) || (bVar13 == 7)) {
          *(undefined1 *)(iVar11 + 0x2ea) = 1;
          FUN_00519290(local_a4,uStack_a0,local_94,uStack_90,local_9c,uStack_98);
          fVar22 = extraout_s1_01;
          fVar23 = extraout_s2_01;
          fVar20 = extraout_s3_01;
          fVar25 = extraout_s4_01;
        }
        else {
          if ((bVar2 & 0xf) == 9) {
            *(undefined1 *)(iVar11 + 0x2ea) = 1;
            iVar7 = FUN_0051a8ec(param_1,&local_b0);
            fVar22 = extraout_s1_02;
            fVar23 = extraout_s2_02;
            fVar20 = extraout_s3_02;
            fVar25 = extraout_s4_02;
          }
          else {
            fVar22 = extraout_s1;
            fVar23 = extraout_s2;
            fVar20 = extraout_s3;
            fVar25 = extraout_s4;
            if (bVar13 == 10 || bVar13 == 0xb) goto LAB_0051fa72;
            *(undefined1 *)(iVar11 + 0x2ea) = 0;
            iVar7 = FUN_005639e8(local_a4,uStack_a0,local_9c,uStack_98);
            fVar22 = extraout_s1_03;
            fVar23 = extraout_s2_03;
            fVar20 = extraout_s3_03;
            fVar25 = extraout_s4_03;
          }
          if (iVar7 != 0) {
LAB_0051f812:
            iVar11 = *piVar6;
            *(undefined4 *)(iVar11 + 0x114) = 0;
            *(undefined4 *)(iVar11 + 0x118) = 0;
            FUN_0051565c(iVar7);
            return iVar7;
          }
        }
LAB_0051fa72:
        iVar7 = *piVar6;
        if ((*(char *)(iVar7 + 0x1c1) != '\0') &&
           ((((bVar2 & 0x6f) != 0 && (*(int *)(iVar7 + 0x2f8) != 0)) ||
            (*(char *)(iVar7 + 0x1c2) != '\0')))) {
          bVar19 = *(int *)(iVar7 + 0x110) != 0;
          cVar1 = '\0';
          if (bVar19) {
            cVar1 = *(char *)(iVar7 + 0x2e1);
          }
          if (bVar19 && cVar1 != '\0') {
            if (cVar1 == '\x02') {
              fVar31 = *(float *)(iVar7 + 0x198);
              fVar20 = *(float *)(iVar7 + 400);
              bVar19 = fVar20 != fVar31;
              if (!bVar19) {
                fVar22 = *(float *)(iVar7 + 0x194);
                fVar23 = *(float *)(iVar7 + 0x19c);
              }
              if (bVar19 || (bVar19 || fVar22 != fVar23)) {
LAB_0051f93c:
                local_118 = *(float *)(iVar7 + 0x198);
                local_114 = *(float *)(iVar7 + 0x19c);
                bVar19 = fVar31 <= fVar20;
                uVar3 = *(undefined8 *)(iVar7 + 0x1a0);
                fVar25 = *(float *)(iVar7 + 300) * 0.5;
                fVar23 = *(float *)(iVar7 + 0x1a0);
                fVar24 = *(float *)(iVar7 + 0x19c);
                fVar22 = *(float *)(iVar7 + 0x1a4);
                if (bVar19) {
                  fVar20 = *(float *)(iVar7 + 0x1a8);
                }
                fVar26 = fVar23 - fVar31;
                fVar28 = fVar22 - fVar24;
                fVar21 = (float)FUN_00524218(fVar26 * fVar26 + fVar28 * fVar28);
                fVar28 = -(fVar28 / fVar21);
                if (!bVar19 || (!bVar19 || fVar20 < fVar23)) {
                  if (0.0 < fVar28) goto LAB_0051f9c0;
LAB_0051fc4c:
                  fVar23 = fVar23 - fVar25 * fVar28;
                  fVar20 = fVar25 * (fVar26 / fVar21);
                  fVar31 = fVar31 - fVar25 * fVar28;
                  fVar22 = fVar22 - fVar20;
                  fVar20 = fVar24 - fVar20;
                }
                else {
                  if (0.0 < fVar28) goto LAB_0051fc4c;
LAB_0051f9c0:
                  fVar23 = fVar25 * fVar28 + fVar23;
                  fVar20 = fVar25 * (fVar26 / fVar21);
                  fVar31 = fVar25 * fVar28 + fVar31;
                  fVar22 = fVar20 + fVar22;
                  fVar20 = fVar20 + fVar24;
                }
                bVar19 = -1 < (int)((uint)*(byte *)(*piVar6 + 0x7d) << 0x1b);
                uVar8 = FUN_0052266e(0,bVar19,bVar19,bVar19);
                FUN_00516b34(local_118,local_114,(int)uVar3,(int)((ulonglong)uVar3 >> 0x20),fVar23,
                             fVar22,fVar31,fVar20);
                fVar20 = extraout_s3_04;
                if ((int)((uint)*(byte *)(*piVar6 + 0x7d) << 0x1b) < 0) goto LAB_0051fcb0;
              }
              else {
                fVar24 = *(float *)(iVar7 + 0x1a0);
                fVar23 = *(float *)(iVar7 + 0x1a8);
                bVar19 = fVar24 == fVar23;
                if (bVar19) {
                  fVar23 = *(float *)(iVar7 + 0x1a4);
                  fVar25 = *(float *)(iVar7 + 0x1ac);
                }
                if (!bVar19 || (!bVar19 || fVar23 != fVar25)) goto LAB_0051f93c;
                fVar25 = *(float *)(iVar7 + 300) * 0.5;
                bVar19 = -1 < (int)((uint)*(byte *)(iVar7 + 0x7d) << 0x1b);
                uVar8 = FUN_0052266e(bVar19,bVar19,bVar19,0);
                FUN_00516b34(fVar20,fVar22,fVar25 + fVar20,fVar22,fVar25 + fVar24,fVar23,fVar24,
                             fVar23);
              }
              FUN_005226b2(uVar8);
              fVar20 = extraout_s3_05;
            }
            else {
              if (cVar1 != '\x01') goto LAB_0051fe02;
              FUN_0051b140();
              fVar20 = extraout_s3_06;
            }
          }
        }
LAB_0051fcb0:
        iVar7 = *piVar6;
      } while (*(char *)(iVar7 + 0x1c1) == '\0');
      if ((((bVar2 & 0x6f) != 0) || (*(char *)(iVar7 + 0x1c2) != '\0')) ||
         (*(char *)(iVar11 + 0x2e5) == '\0')) {
        uVar8 = *(undefined4 *)(iVar11 + 0x364);
        uVar14 = *(undefined4 *)(iVar11 + 0x368);
        uVar16 = *(undefined4 *)(iVar11 + 0x36c);
        uVar17 = *(undefined4 *)(iVar11 + 0x370);
        uVar18 = *(undefined4 *)(iVar11 + 0x374);
        *(undefined4 *)(iVar7 + 0x164) = *(undefined4 *)(iVar11 + 0x360);
        *(undefined4 *)(iVar7 + 0x168) = uVar8;
        *(undefined4 *)(iVar7 + 0x16c) = uVar14;
        *(undefined4 *)(iVar7 + 0x170) = uVar16;
        *(undefined4 *)(iVar7 + 0x174) = uVar17;
        *(undefined4 *)(iVar7 + 0x178) = uVar18;
        uVar8 = *(undefined4 *)(iVar11 + 0x37c);
        uVar14 = *(undefined4 *)(iVar11 + 0x380);
        uVar16 = *(undefined4 *)(iVar11 + 900);
        uVar17 = *(undefined4 *)(iVar11 + 0x388);
        *(undefined4 *)(iVar7 + 0x17c) = *(undefined4 *)(iVar11 + 0x378);
        *(undefined4 *)(iVar7 + 0x180) = uVar8;
        *(undefined4 *)(iVar7 + 0x184) = uVar14;
        *(undefined4 *)(iVar7 + 0x188) = uVar16;
        *(undefined4 *)(iVar7 + 0x18c) = uVar17;
        iVar7 = *piVar6;
        uVar8 = *(undefined4 *)(iVar11 + 0x364);
        uVar14 = *(undefined4 *)(iVar11 + 0x368);
        uVar16 = *(undefined4 *)(iVar11 + 0x36c);
        uVar17 = *(undefined4 *)(iVar11 + 0x370);
        uVar18 = *(undefined4 *)(iVar11 + 0x374);
        *(undefined4 *)(iVar7 + 400) = *(undefined4 *)(iVar11 + 0x360);
        *(undefined4 *)(iVar7 + 0x194) = uVar8;
        *(undefined4 *)(iVar7 + 0x198) = uVar14;
        *(undefined4 *)(iVar7 + 0x19c) = uVar16;
        *(undefined4 *)(iVar7 + 0x1a0) = uVar17;
        *(undefined4 *)(iVar7 + 0x1a4) = uVar18;
        uVar8 = *(undefined4 *)(iVar11 + 0x37c);
        uVar14 = *(undefined4 *)(iVar11 + 0x380);
        uVar16 = *(undefined4 *)(iVar11 + 900);
        uVar17 = *(undefined4 *)(iVar11 + 0x388);
        *(undefined4 *)(iVar7 + 0x1a8) = *(undefined4 *)(iVar11 + 0x378);
        *(undefined4 *)(iVar7 + 0x1ac) = uVar8;
        *(undefined4 *)(iVar7 + 0x1b0) = uVar14;
        *(undefined4 *)(iVar7 + 0x1b4) = uVar16;
        *(undefined4 *)(iVar7 + 0x1b8) = uVar17;
        iVar7 = *piVar6;
        uVar8 = *(undefined4 *)(iVar11 + 0x364);
        uVar14 = *(undefined4 *)(iVar11 + 0x368);
        uVar16 = *(undefined4 *)(iVar11 + 0x36c);
        uVar17 = *(undefined4 *)(iVar11 + 0x370);
        uVar18 = *(undefined4 *)(iVar11 + 0x374);
        *(undefined4 *)(iVar7 + 0x138) = *(undefined4 *)(iVar11 + 0x360);
        *(undefined4 *)(iVar7 + 0x13c) = uVar8;
        *(undefined4 *)(iVar7 + 0x140) = uVar14;
        *(undefined4 *)(iVar7 + 0x144) = uVar16;
        *(undefined4 *)(iVar7 + 0x148) = uVar17;
        *(undefined4 *)(iVar7 + 0x14c) = uVar18;
        uVar8 = *(undefined4 *)(iVar11 + 0x37c);
        uVar14 = *(undefined4 *)(iVar11 + 0x380);
        uVar16 = *(undefined4 *)(iVar11 + 900);
        uVar17 = *(undefined4 *)(iVar11 + 0x388);
        *(undefined4 *)(iVar7 + 0x150) = *(undefined4 *)(iVar11 + 0x378);
        *(undefined4 *)(iVar7 + 0x154) = uVar8;
        *(undefined4 *)(iVar7 + 0x158) = uVar14;
        *(undefined4 *)(iVar7 + 0x15c) = uVar16;
        *(undefined4 *)(iVar7 + 0x160) = uVar17;
        iVar7 = *piVar6;
        bVar19 = *(int *)(iVar7 + 0x110) != 0;
        cVar1 = '\0';
        if (bVar19) {
          cVar1 = *(char *)(iVar7 + 0x2e0);
        }
        if (bVar19 && cVar1 != '\0') {
          if (cVar1 == '\x02') {
            fVar23 = *(float *)(iVar7 + 400);
            if (fVar23 == *(float *)(iVar7 + 0x198)) {
              fVar25 = *(float *)(iVar7 + 0x194);
              fVar22 = *(float *)(iVar7 + 0x19c);
              bVar19 = fVar25 != fVar22;
              if (!bVar19) {
                fVar22 = *(float *)(iVar7 + 0x1a0);
                fVar20 = *(float *)(iVar7 + 0x1a8);
              }
              if ((bVar19 || (bVar19 || fVar22 != fVar20)) ||
                 (fVar20 = *(float *)(iVar7 + 0x1a4), fVar20 != *(float *)(iVar7 + 0x1ac)))
              goto LAB_0051fd40;
              fVar31 = *(float *)(iVar7 + 300) * -0.5;
              local_110 = fVar31 + fVar23;
              bVar19 = -1 < (int)((uint)*(byte *)(iVar7 + 0x7d) << 0x1b);
              local_118 = fVar23;
              local_114 = fVar25;
              local_10c = fVar25;
              uVar8 = FUN_0052266e(bVar19,0,bVar19,bVar19);
              FUN_00516b34(local_110,local_10c,local_118,local_114,fVar22,fVar20,fVar31 + fVar22,
                           fVar20);
            }
            else {
LAB_0051fd40:
              fVar25 = *(float *)(iVar7 + 300) * 0.5;
              bVar19 = false;
              uVar3 = *(undefined8 *)(iVar7 + 0x138);
              uVar4 = *(undefined8 *)(iVar7 + 0x150);
              fVar23 = *(float *)(iVar7 + 0x150);
              uVar5 = *(undefined8 *)(iVar7 + 0x138);
              fVar22 = *(float *)(iVar7 + 0x154);
              if ((*(float *)(iVar7 + 0x138) < *(float *)(iVar7 + 0x140)) &&
                 (fVar23 < *(float *)(iVar7 + 0x148))) {
                bVar19 = true;
              }
              fVar24 = (float)uVar5;
              fVar28 = fVar23 - fVar24;
              fVar21 = (float)((ulonglong)uVar5 >> 0x20);
              fVar31 = fVar22 - fVar21;
              fVar20 = (float)FUN_00524218(fVar28 * fVar28 + fVar31 * fVar31);
              fVar31 = -(fVar31 / fVar20);
              if (bVar19) {
                if (0.0 < fVar31) goto LAB_0051ff44;
LAB_0051fdb8:
                fVar23 = fVar25 * fVar31 + fVar23;
                fVar20 = fVar25 * (fVar28 / fVar20);
                fVar24 = fVar25 * fVar31 + fVar24;
                fVar22 = fVar20 + fVar22;
                fVar20 = fVar20 + fVar21;
              }
              else {
                if (0.0 < fVar31) goto LAB_0051fdb8;
LAB_0051ff44:
                fVar23 = fVar23 - fVar25 * fVar31;
                fVar20 = fVar25 * (fVar28 / fVar20);
                fVar24 = fVar24 - fVar25 * fVar31;
                fVar22 = fVar22 - fVar20;
                fVar20 = fVar21 - fVar20;
              }
              bVar19 = -1 < (int)((uint)*(byte *)(*piVar6 + 0x7d) << 0x1b);
              uVar8 = FUN_0052266e(0,bVar19,bVar19,bVar19);
              FUN_00516b34((int)uVar3,(int)((ulonglong)uVar3 >> 0x20),(int)uVar4,
                           (int)((ulonglong)uVar4 >> 0x20),fVar23,fVar22,fVar24,fVar20);
              if ((int)((uint)*(byte *)(*piVar6 + 0x7d) << 0x1b) < 0) goto LAB_0051faf0;
            }
            FUN_005226b2(uVar8);
          }
          else {
            if (cVar1 != '\x01') {
LAB_0051fe02:
              *(undefined4 *)(iVar7 + 0x114) = 0;
              *(undefined4 *)(iVar7 + 0x118) = 0;
              FUN_0051565c(0x800000);
              return 0x800000;
            }
            FUN_0051b140(0);
          }
        }
      }
LAB_0051faf0:
    } while (((*(char *)(*piVar6 + 0x1c1) == '\0') || (((bVar2 & 0x6f) != 0 && (bVar13 != 10)))) ||
            ((*(char *)(iVar11 + 0x2e5) == '\0' && (*(int *)(iVar11 + 0x2f8) != 0))));
    uVar3 = *(undefined8 *)(iVar11 + 0x310);
    uVar4 = *(undefined8 *)(iVar11 + 0x318);
    *(undefined4 *)(iVar11 + 0x334) = *(undefined4 *)(iVar11 + 0x308);
    *(undefined4 *)(iVar11 + 0x338) = *(undefined4 *)(iVar11 + 0x30c);
    *(undefined4 *)(iVar11 + 0x33c) = *(undefined4 *)(iVar11 + 0x310);
    *(undefined4 *)(iVar11 + 0x340) = *(undefined4 *)(iVar11 + 0x314);
    *(undefined4 *)(iVar11 + 0x344) = *(undefined4 *)(iVar11 + 0x318);
    *(undefined4 *)(iVar11 + 0x348) = *(undefined4 *)(iVar11 + 0x31c);
    *(undefined4 *)(iVar11 + 0x34c) = *(undefined4 *)(iVar11 + 800);
    *(undefined4 *)(iVar11 + 0x350) = *(undefined4 *)(iVar11 + 0x324);
    *(undefined4 *)(iVar11 + 0x354) = *(undefined4 *)(iVar11 + 0x328);
    *(undefined4 *)(iVar11 + 0x358) = *(undefined4 *)(iVar11 + 0x32c);
    *(undefined4 *)(iVar11 + 0x35c) = *(undefined4 *)(iVar11 + 0x330);
    *(undefined4 *)(iVar11 + 0x308) = *(undefined4 *)(iVar11 + 0x360);
    *(undefined4 *)(iVar11 + 0x30c) = *(undefined4 *)(iVar11 + 0x364);
    *(undefined4 *)(iVar11 + 0x310) = *(undefined4 *)(iVar11 + 0x368);
    *(undefined4 *)(iVar11 + 0x314) = *(undefined4 *)(iVar11 + 0x36c);
    *(undefined4 *)(iVar11 + 0x318) = *(undefined4 *)(iVar11 + 0x370);
    *(undefined4 *)(iVar11 + 0x31c) = *(undefined4 *)(iVar11 + 0x374);
    *(undefined4 *)(iVar11 + 800) = *(undefined4 *)(iVar11 + 0x378);
    *(undefined4 *)(iVar11 + 0x324) = *(undefined4 *)(iVar11 + 0x37c);
    *(undefined4 *)(iVar11 + 0x328) = *(undefined4 *)(iVar11 + 0x380);
    *(undefined4 *)(iVar11 + 0x32c) = *(undefined4 *)(iVar11 + 900);
    *(undefined4 *)(iVar11 + 0x330) = *(undefined4 *)(iVar11 + 0x388);
    iVar7 = *piVar6;
  } while (*(int *)(iVar7 + 0x110) == 0);
  cVar1 = *(char *)(iVar7 + 0x2e2);
  uVar16 = 0;
  fVar24 = (float)((ulonglong)*(undefined8 *)(iVar11 + 0x378) >> 0x20);
  fVar31 = (float)((ulonglong)uVar4 >> 0x20);
  fVar25 = (float)((ulonglong)*(undefined8 *)(iVar11 + 0x360) >> 0x20);
  fVar22 = (float)((ulonglong)uVar3 >> 0x20);
  uVar14 = (undefined4)*(undefined8 *)(iVar11 + 0x378);
  fVar20 = (float)uVar4;
  uVar8 = (undefined4)*(undefined8 *)(iVar11 + 0x360);
  fVar23 = (float)uVar3;
  if ((cVar1 == '\0') || (*(int *)(iVar7 + 0x118) != 0)) {
    if (-1 < (int)((uint)*(byte *)(iVar7 + 0x7d) << 0x1b)) {
      uVar16 = FUN_0052266e(1,0,1,0);
    }
    FUN_00516b34(fVar23,fVar22,uVar8,fVar25,fVar20,fVar31,uVar14,fVar24);
  }
  else {
    if (cVar1 == '\x02') {
      local_118 = DAT_005202d0;
      local_114 = DAT_005202d4;
      iVar7 = FUN_00522f50(fVar23,fVar22,fVar20,fVar31,uVar8,fVar25,uVar14,fVar24,&local_118,
                           &local_114);
      if (iVar7 != 0) {
        iVar7 = *piVar6;
        fVar23 = (float)FUN_004397a8(*(float *)(iVar7 + 0xec) * *(float *)(iVar7 + 0xec) +
                                     *(float *)(iVar7 + 0xf0) * *(float *)(iVar7 + 0xf0));
        fVar22 = (float)FUN_004397a8(*(float *)(iVar7 + 0xf8) * *(float *)(iVar7 + 0xf8) +
                                     *(float *)(iVar7 + 0xfc) * *(float *)(iVar7 + 0xfc));
        fVar23 = ABS(fVar23);
        bVar19 = NAN(fVar23) || NAN(DAT_0051ff24);
        if (fVar23 < DAT_0051ff24) {
          bVar19 = NAN(ABS(fVar22)) || NAN(DAT_0051ff24);
        }
        bVar19 = (fVar23 < DAT_0051ff24 && ABS(fVar22) < DAT_0051ff24) == bVar19;
        if (bVar19) {
          FUN_00522622(1);
        }
        if ((int)((uint)*(byte *)(*piVar6 + 0x7d) << 0x1b) < 0) {
          FUN_00522fb4(local_118,local_114,*(float *)(*piVar6 + 0x2d8) * 0.5);
        }
        else {
          FUN_00523284();
        }
        if (bVar19) {
          FUN_00522622(0);
        }
      }
      goto LAB_0051f7ee;
    }
    if (cVar1 != '\x01') {
      *(undefined4 *)(iVar7 + 0x114) = 0;
      *(undefined4 *)(iVar7 + 0x118) = 0;
      FUN_0051565c(0x1000000);
      return 0x1000000;
    }
    if (*(char *)(iVar7 + 0x2e4) == '\0') {
      if ((*(float *)(iVar7 + 0x158) <= 0.0) || (*(int *)(iVar7 + 0x128) != 1)) {
        local_dc = *(undefined4 *)(iVar7 + 0x164);
        local_d8 = *(undefined4 *)(iVar7 + 0x168);
        local_d4 = *(undefined4 *)(iVar7 + 0x16c);
        local_d0 = *(float *)(iVar7 + 0x170);
        local_cc = *(undefined4 *)(iVar7 + 0x174);
        local_c8 = *(float *)(iVar7 + 0x178);
        puVar12 = (undefined4 *)(iVar7 + 400);
        local_c4 = *(undefined4 *)(iVar7 + 0x17c);
        local_c0 = *(undefined4 *)(iVar7 + 0x180);
        uStack_bc = *(undefined4 *)(iVar7 + 0x184);
        uStack_b8 = *(undefined4 *)(iVar7 + 0x188);
        uStack_b4 = *(undefined4 *)(iVar7 + 0x18c);
      }
      else {
        local_dc = *(undefined4 *)(iVar7 + 0x138);
        local_d8 = *(undefined4 *)(iVar7 + 0x13c);
        local_d4 = *(undefined4 *)(iVar7 + 0x140);
        local_d0 = *(float *)(iVar7 + 0x144);
        local_cc = *(undefined4 *)(iVar7 + 0x148);
        local_c8 = *(float *)(iVar7 + 0x14c);
        puVar12 = (undefined4 *)(iVar7 + 400);
        local_c4 = *(undefined4 *)(iVar7 + 0x150);
        local_c0 = *(undefined4 *)(iVar7 + 0x154);
        uStack_bc = *(undefined4 *)(iVar7 + 0x158);
        uStack_b8 = *(undefined4 *)(iVar7 + 0x15c);
        uStack_b4 = *(undefined4 *)(iVar7 + 0x160);
      }
    }
    else {
      local_dc = *(undefined4 *)(iVar7 + 0x334);
      local_d8 = *(undefined4 *)(iVar7 + 0x338);
      local_d4 = *(undefined4 *)(iVar7 + 0x33c);
      local_d0 = *(float *)(iVar7 + 0x340);
      local_cc = *(undefined4 *)(iVar7 + 0x344);
      local_c8 = *(float *)(iVar7 + 0x348);
      puVar12 = (undefined4 *)(iVar7 + 0x308);
      local_c4 = *(undefined4 *)(iVar7 + 0x34c);
      local_c0 = *(undefined4 *)(iVar7 + 0x350);
      uStack_bc = *(undefined4 *)(iVar7 + 0x354);
      uStack_b8 = *(undefined4 *)(iVar7 + 0x358);
      uStack_b4 = *(undefined4 *)(iVar7 + 0x35c);
    }
    local_108 = *puVar12;
    local_104 = (float)puVar12[1];
    local_100 = puVar12[2];
    local_fc = puVar12[3];
    local_f8 = puVar12[4];
    local_f4 = puVar12[5];
    local_f0 = puVar12[6];
    local_ec = (float)puVar12[7];
    uStack_e8 = puVar12[8];
    uStack_e4 = puVar12[9];
    uStack_e0 = puVar12[10];
    iVar7 = FUN_005177a4(&local_108,&local_dc,puVar12 + 0xb);
    if ((((iVar7 == 1) && (iVar7 = FUN_005177a4(&local_100,&local_d4), iVar7 == 1)) &&
        (iVar7 = FUN_005177a4(&local_f8,&local_cc), iVar7 == 1)) &&
       (iVar7 = FUN_005177a4(&local_f0,&local_c4), iVar7 == 1)) goto LAB_0051f7ee;
    iVar7 = FUN_0051785c(&local_108,&local_d4);
    if ((iVar7 != 0) || (iVar7 = FUN_0051785c(&local_dc,&local_108), iVar7 != 0)) goto LAB_005200d8;
    iVar7 = FUN_0051785c(&local_108,&local_cc);
    uVar17 = local_cc;
    fVar21 = local_c8;
    uVar18 = local_f0;
    fVar28 = local_ec;
    uVar32 = local_fc;
    uVar33 = local_100;
    uVar34 = local_d8;
    uVar35 = local_dc;
    uVar27 = local_108;
    fVar26 = local_104;
    uVar29 = local_d4;
    fVar30 = local_d0;
    if ((iVar7 == 0) &&
       (iVar7 = FUN_0051785c(&local_dc,&local_f0), uVar17 = local_cc, fVar21 = local_c8,
       uVar18 = local_f0, fVar28 = local_ec, uVar32 = local_fc, uVar33 = local_100,
       uVar34 = local_d8, uVar35 = local_dc, uVar27 = local_108, fVar26 = local_104,
       uVar29 = local_d4, fVar30 = local_d0, iVar7 == 0)) {
      iVar7 = (uint)(local_c8 < local_d0) << 0x1f;
      if (local_104 < local_d0) {
        if (-1 < iVar7) goto LAB_005200d8;
      }
      else if (iVar7 < 0) {
LAB_005200d8:
        uVar17 = local_d4;
        fVar21 = local_d0;
        uVar18 = local_108;
        fVar28 = local_104;
        uVar32 = local_f4;
        uVar33 = local_f8;
        uVar34 = local_c0;
        uVar35 = local_c4;
        uVar27 = local_f0;
        fVar26 = local_ec;
        uVar29 = local_cc;
        fVar30 = local_c8;
      }
    }
    local_110 = DAT_005202d8;
    local_10c = DAT_005202dc;
    local_118 = DAT_005202e0;
    local_114 = DAT_005202e4;
    iVar7 = FUN_00522f50(uVar29,fVar30,uVar17,fVar21,uVar27,fVar26,uVar18,fVar28,&local_110,
                         &local_10c);
    iVar9 = FUN_00522f50(uVar35,uVar34,uVar29,fVar30,uVar27,fVar26,uVar33,uVar32,&local_118,
                         &local_114);
    fVar21 = (float)FUN_00524218((local_118 - local_110) * (local_118 - local_110) +
                                 (local_114 - local_10c) * (local_114 - local_10c));
    iVar10 = *piVar6;
    if ((*(float *)(iVar10 + 0x2dc) * *(float *)(iVar10 + 0x2d8) < fVar21) ||
       (iVar9 == 0 || iVar7 == 0)) {
      if (-1 < (int)((uint)*(byte *)(iVar10 + 0x7d) << 0x1b)) {
        uVar16 = FUN_0052266e(1,0,1,0);
      }
    }
    else {
      fVar23 = local_110;
      fVar22 = local_10c;
      uVar8 = uVar29;
      fVar25 = fVar30;
      fVar20 = local_118;
      fVar31 = local_114;
      uVar14 = uVar27;
      fVar24 = fVar26;
      if (-1 < (int)((uint)*(byte *)(iVar10 + 0x7d) << 0x1b)) {
        uVar16 = FUN_0052266e(0,1,1,0);
        fVar23 = local_110;
        fVar22 = local_10c;
        fVar20 = local_118;
        fVar31 = local_114;
      }
    }
    FUN_00516b34(fVar23,fVar22,uVar8,fVar25,fVar20,fVar31,uVar14,fVar24);
  }
  if (-1 < (int)((uint)*(byte *)(*piVar6 + 0x7d) << 0x1b)) {
    FUN_005226b2(uVar16);
  }
  goto LAB_0051f7ee;
}

