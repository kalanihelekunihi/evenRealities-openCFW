
/* WARNING: Instruction at (ram,0x0051f3ee) overlaps instruction at (ram,0x0051f3ec)
    */

int FUN_0051d2e0(uint *param_1)

{
  uint uVar1;
  char cVar2;
  undefined8 uVar3;
  int *piVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  uint uVar10;
  uint extraout_r1;
  uint extraout_r1_00;
  uint extraout_r1_01;
  uint extraout_r1_02;
  float *pfVar11;
  uint uVar12;
  uint uVar13;
  undefined4 uVar14;
  undefined4 uVar15;
  byte bVar16;
  byte bVar17;
  bool bVar18;
  bool bVar19;
  uint in_fpscr;
  float fVar20;
  float fVar21;
  float fVar22;
  float fVar23;
  float fVar24;
  float *extraout_s1;
  float *extraout_s1_00;
  float *pfVar25;
  float *extraout_s1_01;
  float fVar26;
  float extraout_s2;
  float fVar27;
  float extraout_s2_00;
  float extraout_s2_01;
  float fVar28;
  float fVar29;
  float fVar30;
  float fVar31;
  float extraout_s4;
  float extraout_s4_00;
  float extraout_s4_01;
  float fVar32;
  float fVar33;
  float fVar34;
  float fVar35;
  undefined8 uVar36;
  undefined8 uVar37;
  undefined4 uVar38;
  float fVar39;
  float fVar40;
  float fVar41;
  float fVar42;
  float local_2d0;
  float *local_2cc;
  float local_2c8;
  float *local_2c4;
  float local_2c0;
  float local_2bc;
  float local_2b8;
  float local_2b4;
  float local_2b0;
  float local_2ac;
  float local_2a8;
  float local_2a4;
  float local_2a0;
  float local_29c;
  float local_298;
  float local_294;
  float local_290;
  float local_28c;
  float local_288;
  float local_284;
  float local_280;
  float local_27c;
  float local_278;
  float local_274;
  float local_270;
  float local_26c;
  float local_268;
  float local_264;
  float local_260;
  float local_25c;
  float local_258;
  float local_254;
  float local_250;
  float local_24c;
  float local_248;
  undefined4 uStack_244;
  undefined4 uStack_240;
  undefined4 uStack_23c;
  undefined1 local_238;
  char local_237;
  char local_236;
  float local_22c;
  float local_228;
  float local_224;
  float local_220;
  undefined4 local_21c;
  undefined4 uStack_218;
  undefined4 local_214;
  undefined4 uStack_210;
  undefined4 auStack_200 [4];
  float local_1f0;
  float local_1ec;
  float local_1e8 [96];
  
  FUN_0048949c(&local_238,0x48);
  piVar4 = DAT_0051dd2c;
  uVar13 = 0;
  local_238 = 1;
  local_236 = '\x01';
  local_237 = '\x01';
  local_2cc = DAT_0051dd28;
LAB_0051d332:
  do {
    if (*param_1 <= uVar13) {
      uVar14 = 0;
      iVar5 = -(uint)(local_237 == '\0');
      iVar7 = -(iVar5 >> 0x1f);
      if ((int)((uint)*(byte *)(*piVar4 + 0x7d) << 0x1b) < 0) {
        uVar14 = FUN_0052266e(0,0,0,0);
      }
      if (iVar5 < 0) {
        iVar6 = *piVar4;
        fVar22 = *(float *)(iVar6 + 0x158);
        uVar13 = in_fpscr & 0xfffffff;
        uVar10 = uVar13 | (uint)(fVar22 < 0.0) << 0x1f | (uint)(fVar22 == 0.0) << 0x1e;
        in_fpscr = uVar10 | (uint)NAN(fVar22) << 0x1c;
        bVar16 = (byte)(uVar10 >> 0x18);
        bVar17 = bVar16 >> 7;
        bVar19 = (bool)(bVar16 >> 6 & 1);
        bVar16 = (byte)(in_fpscr >> 0x1c) & 1;
        if (!bVar19 && bVar17 == bVar16) {
          fVar22 = *(float *)(iVar6 + 0x184);
          in_fpscr = uVar13 | (uint)(fVar22 < 0.0) << 0x1f | (uint)(fVar22 == 0.0) << 0x1e |
                     (uint)NAN(fVar22) << 0x1c;
          bVar16 = (byte)(in_fpscr >> 0x18);
          bVar17 = bVar16 >> 7;
          bVar19 = (bool)(bVar16 >> 6 & 1);
          bVar16 = bVar16 >> 4 & 1;
        }
        if (bVar19 || bVar17 != bVar16) goto LAB_0051e59c;
        if (*(int *)(iVar6 + 0x110) == 0) goto LAB_0051e59c;
        cVar2 = *(char *)(iVar6 + 0x2e2);
        uVar15 = 0;
        fVar27 = (float)*(undefined8 *)(iVar6 + 0x150);
        fVar39 = (float)((ulonglong)*(undefined8 *)(iVar6 + 0x150) >> 0x20);
        fVar31 = (float)*(undefined8 *)(iVar6 + 0x174);
        pfVar25 = (float *)((ulonglong)*(undefined8 *)(iVar6 + 0x174) >> 0x20);
        fVar40 = (float)*(undefined8 *)(iVar6 + 0x138);
        fVar20 = (float)((ulonglong)*(undefined8 *)(iVar6 + 0x138) >> 0x20);
        fVar22 = (float)*(undefined8 *)(iVar6 + 0x16c);
        fVar21 = (float)((ulonglong)*(undefined8 *)(iVar6 + 0x16c) >> 0x20);
        if ((cVar2 == '\0') || (*(int *)(iVar6 + 0x118) != 0)) {
          if (-1 < (int)((uint)*(byte *)(iVar6 + 0x7d) << 0x1b)) {
            uVar15 = FUN_0052266e(1,0,1,0);
          }
          FUN_00516b34(fVar22,fVar21,fVar40,fVar20,fVar31,pfVar25,fVar27,fVar39);
LAB_0051e58c:
          if (-1 < (int)((uint)*(byte *)(*piVar4 + 0x7d) << 0x1b)) {
            FUN_005226b2(uVar15);
          }
          goto LAB_0051e59c;
        }
        if (cVar2 == '\x02') {
          local_2c8 = *DAT_0051e4a8;
          local_2c4 = (float *)DAT_0051e4a8[1];
          iVar6 = FUN_00522f50(fVar22,fVar21,fVar31,pfVar25,fVar40,fVar20,fVar27,fVar39,&local_2c8,
                               &local_2c4);
          if (iVar6 != 0) {
            iVar6 = *piVar4;
            fVar22 = (float)FUN_004397a8(*(float *)(iVar6 + 0xec) * *(float *)(iVar6 + 0xec) +
                                         *(float *)(iVar6 + 0xf0) * *(float *)(iVar6 + 0xf0));
            fVar21 = (float)FUN_004397a8(*(float *)(iVar6 + 0xf8) * *(float *)(iVar6 + 0xf8) +
                                         *(float *)(iVar6 + 0xfc) * *(float *)(iVar6 + 0xfc));
            uVar13 = in_fpscr & 0xfffffff;
            uVar10 = uVar13 | (uint)(ABS(fVar22) < DAT_0051e4a4) << 0x1f;
            in_fpscr = uVar10 | (uint)(NAN(ABS(fVar22)) || NAN(DAT_0051e4a4)) << 0x1c;
            bVar16 = (byte)(uVar10 >> 0x1f);
            bVar17 = (byte)(in_fpscr >> 0x1c) & 1;
            if (bVar16 != bVar17) {
              in_fpscr = uVar13 | (uint)(ABS(fVar21) < DAT_0051e4a4) << 0x1f |
                         (uint)(NAN(ABS(fVar21)) || NAN(DAT_0051e4a4)) << 0x1c;
              bVar17 = (byte)(in_fpscr >> 0x18);
              bVar16 = bVar17 >> 7;
              bVar17 = bVar17 >> 4 & 1;
            }
            if (bVar16 == bVar17) {
              FUN_00522622(1);
            }
            if ((int)((uint)*(byte *)(*piVar4 + 0x7d) << 0x1b) < 0) {
              FUN_00522fb4(local_2c8,local_2c4,*(float *)(*piVar4 + 0x2d8) * 0.5);
            }
            else {
              FUN_00523284();
            }
            if (bVar16 == bVar17) {
              FUN_00522622(0);
            }
          }
          goto LAB_0051e59c;
        }
        if (cVar2 == '\x01') {
          if (*(char *)(iVar6 + 0x2e4) == '\0') {
            if (*(int *)(iVar6 + 0x128) == 1) {
              local_28c = *(float *)(iVar6 + 0x138);
              local_288 = *(float *)(iVar6 + 0x13c);
              local_284 = *(float *)(iVar6 + 0x140);
              local_280 = *(float *)(iVar6 + 0x144);
              local_27c = *(float *)(iVar6 + 0x148);
              local_278 = *(float *)(iVar6 + 0x14c);
              local_274 = *(float *)(iVar6 + 0x150);
              local_270 = *(float *)(iVar6 + 0x154);
              local_26c = *(float *)(iVar6 + 0x158);
              local_268 = *(float *)(iVar6 + 0x15c);
              local_264 = *(float *)(iVar6 + 0x160);
              local_2b8 = *(float *)(iVar6 + 400);
              local_2b4 = *(float *)(iVar6 + 0x194);
              local_2b0 = *(float *)(iVar6 + 0x198);
              local_2ac = *(float *)(iVar6 + 0x19c);
              local_2a8 = *(float *)(iVar6 + 0x1a0);
              local_2a4 = *(float *)(iVar6 + 0x1a4);
              local_2a0 = *(float *)(iVar6 + 0x1a8);
              local_29c = *(float *)(iVar6 + 0x1ac);
              local_298 = *(float *)(iVar6 + 0x1b0);
              local_294 = *(float *)(iVar6 + 0x1b4);
              local_290 = *(float *)(iVar6 + 0x1b8);
              iVar6 = iVar6 + 0x1bc;
            }
            else {
              local_2b8 = *(float *)(iVar6 + 0x138);
              local_2b4 = *(float *)(iVar6 + 0x13c);
              local_2b0 = *(float *)(iVar6 + 0x140);
              local_2ac = *(float *)(iVar6 + 0x144);
              local_2a8 = *(float *)(iVar6 + 0x148);
              local_2a4 = *(float *)(iVar6 + 0x14c);
              local_2a0 = *(float *)(iVar6 + 0x150);
              local_29c = *(float *)(iVar6 + 0x154);
              local_298 = *(float *)(iVar6 + 0x158);
              local_294 = *(float *)(iVar6 + 0x15c);
              local_290 = *(float *)(iVar6 + 0x160);
              local_28c = *(float *)(iVar6 + 0x164);
              local_288 = *(float *)(iVar6 + 0x168);
              local_284 = *(float *)(iVar6 + 0x16c);
              local_280 = *(float *)(iVar6 + 0x170);
              local_27c = *(float *)(iVar6 + 0x174);
              local_278 = *(float *)(iVar6 + 0x178);
              local_274 = *(float *)(iVar6 + 0x17c);
              local_270 = *(float *)(iVar6 + 0x180);
              local_26c = *(float *)(iVar6 + 0x184);
              local_268 = *(float *)(iVar6 + 0x188);
              local_264 = *(float *)(iVar6 + 0x18c);
              iVar6 = iVar6 + 400;
            }
          }
          else {
            local_28c = *(float *)(iVar6 + 0x334);
            local_288 = *(float *)(iVar6 + 0x338);
            local_284 = *(float *)(iVar6 + 0x33c);
            local_280 = *(float *)(iVar6 + 0x340);
            local_27c = *(float *)(iVar6 + 0x344);
            local_278 = *(float *)(iVar6 + 0x348);
            local_274 = *(float *)(iVar6 + 0x34c);
            local_270 = *(float *)(iVar6 + 0x350);
            local_26c = *(float *)(iVar6 + 0x354);
            local_268 = *(float *)(iVar6 + 0x358);
            local_264 = *(float *)(iVar6 + 0x35c);
            local_2b8 = *(float *)(iVar6 + 0x308);
            local_2b4 = *(float *)(iVar6 + 0x30c);
            local_2b0 = *(float *)(iVar6 + 0x310);
            local_2ac = *(float *)(iVar6 + 0x314);
            local_2a8 = *(float *)(iVar6 + 0x318);
            local_2a4 = *(float *)(iVar6 + 0x31c);
            local_2a0 = *(float *)(iVar6 + 800);
            local_29c = *(float *)(iVar6 + 0x324);
            local_298 = *(float *)(iVar6 + 0x328);
            local_294 = *(float *)(iVar6 + 0x32c);
            local_290 = *(float *)(iVar6 + 0x330);
            iVar6 = iVar6 + 0x334;
          }
          iVar6 = FUN_005177a4(&local_2b8,&local_28c,iVar6);
          if ((((iVar6 != 1) || (iVar6 = FUN_005177a4(&local_2b0,&local_284), iVar6 != 1)) ||
              (iVar6 = FUN_005177a4(&local_2a8,&local_27c), iVar6 != 1)) ||
             (iVar6 = FUN_005177a4(&local_2a0,&local_274), iVar6 != 1)) {
            iVar6 = FUN_0051785c(&local_2b8,&local_284);
            if ((iVar6 != 0) || (iVar6 = FUN_0051785c(&local_28c,&local_2b8), iVar6 != 0))
            goto LAB_0051e3a0;
            iVar6 = FUN_0051785c(&local_2b8,&local_27c);
            fVar28 = local_27c;
            fVar23 = local_278;
            fVar26 = local_2a0;
            fVar32 = local_29c;
            fVar35 = local_2ac;
            fVar34 = local_2b0;
            fVar41 = local_288;
            fVar42 = local_28c;
            fVar30 = local_2b8;
            fVar33 = local_2b4;
            fVar24 = local_284;
            fVar29 = local_280;
            if ((iVar6 == 0) &&
               (iVar6 = FUN_0051785c(&local_28c,&local_2a0), fVar28 = local_27c, fVar23 = local_278,
               fVar26 = local_2a0, fVar32 = local_29c, fVar35 = local_2ac, fVar34 = local_2b0,
               fVar41 = local_288, fVar42 = local_28c, fVar30 = local_2b8, fVar33 = local_2b4,
               fVar24 = local_284, fVar29 = local_280, iVar6 == 0)) {
              in_fpscr = in_fpscr & 0xfffffff;
              if (local_280 <= local_2b4) {
                if (local_280 > local_278) goto LAB_0051e3a0;
              }
              else if (local_280 <= local_278) {
LAB_0051e3a0:
                fVar28 = local_284;
                fVar23 = local_280;
                fVar26 = local_2b8;
                fVar32 = local_2b4;
                fVar35 = local_2a4;
                fVar34 = local_2a8;
                fVar41 = local_270;
                fVar42 = local_274;
                fVar30 = local_2a0;
                fVar33 = local_29c;
                fVar24 = local_27c;
                fVar29 = local_278;
              }
            }
            local_2c0 = *local_2cc;
            local_2bc = local_2cc[1];
            local_2c8 = *DAT_0051e7bc;
            local_2c4 = (float *)DAT_0051e7bc[1];
            iVar6 = FUN_00522f50(fVar24,fVar29,fVar28,fVar23,fVar30,fVar33,fVar26,fVar32,&local_2c0,
                                 &local_2bc);
            iVar8 = FUN_00522f50(fVar42,fVar41,fVar24,fVar29,fVar30,fVar33,fVar34,fVar35,&local_2c8,
                                 &local_2c4);
            fVar28 = (float)FUN_00524218((local_2c8 - local_2c0) * (local_2c8 - local_2c0) +
                                         ((float)local_2c4 - local_2bc) *
                                         ((float)local_2c4 - local_2bc));
            iVar9 = *piVar4;
            in_fpscr = in_fpscr & 0xfffffff;
            if ((*(float *)(iVar9 + 0x2dc) * *(float *)(iVar9 + 0x2d8) < fVar28) ||
               (iVar8 == 0 || iVar6 == 0)) {
              fVar24 = fVar40;
              fVar29 = fVar20;
              fVar30 = fVar27;
              fVar33 = fVar39;
              if (-1 < (int)((uint)*(byte *)(iVar9 + 0x7d) << 0x1b)) {
                uVar15 = FUN_0052266e(1,0,1,0);
              }
            }
            else {
              fVar22 = local_2c0;
              fVar21 = local_2bc;
              fVar31 = local_2c8;
              pfVar25 = local_2c4;
              if (-1 < (int)((uint)*(byte *)(iVar9 + 0x7d) << 0x1b)) {
                uVar15 = FUN_0052266e(0,1,1,0);
                fVar22 = local_2c0;
                fVar21 = local_2bc;
                fVar31 = local_2c8;
                pfVar25 = local_2c4;
              }
            }
            FUN_00516b34(fVar22,fVar21,fVar24,fVar29,fVar31,pfVar25,fVar30,fVar33);
            goto LAB_0051e58c;
          }
          goto LAB_0051e59c;
        }
LAB_0051e51e:
        *(undefined4 *)(iVar6 + 0x114) = 0;
        *(undefined4 *)(iVar6 + 0x118) = 0;
        FUN_0051565c(0x1000000);
        iVar5 = *piVar4;
        *(undefined4 *)(iVar5 + 0x114) = 0;
        *(undefined4 *)(iVar5 + 0x118) = 0;
LAB_0051e538:
        FUN_0051565c(0x1000000);
        return 0x1000000;
      }
LAB_0051e59c:
      iVar6 = *piVar4;
      fVar22 = *(float *)(iVar6 + 0x184);
      uVar13 = in_fpscr & 0xfffffff | (uint)(fVar22 < 0.0) << 0x1f | (uint)(fVar22 == 0.0) << 0x1e;
      uVar10 = uVar13 | (uint)NAN(fVar22) << 0x1c;
      bVar16 = (byte)(uVar13 >> 0x18);
      if (!(bool)(bVar16 >> 6 & 1) && bVar16 >> 7 == ((byte)(uVar10 >> 0x1c) & 1)) {
        if (-1 < (int)((uint)*(byte *)(iVar6 + 0x7d) << 0x1b)) {
          if (iVar7 == 0) {
            uVar13 = -(uint)(*(char *)(iVar6 + 0x1bf) == '\0') >> 0x1f;
          }
          else {
            uVar13 = 0;
          }
          uVar14 = FUN_0052266e(1,uVar13,1,0);
        }
        iVar6 = *piVar4;
        FUN_00516b34(*(undefined4 *)(iVar6 + 0x164),*(undefined4 *)(iVar6 + 0x168),
                     *(undefined4 *)(iVar6 + 0x16c),*(undefined4 *)(iVar6 + 0x170),
                     *(undefined4 *)(iVar6 + 0x174),*(undefined4 *)(iVar6 + 0x178),
                     *(undefined4 *)(iVar6 + 0x17c),*(undefined4 *)(iVar6 + 0x180));
        iVar6 = *piVar4;
        *(undefined4 *)(iVar6 + 0x184) = 0;
        if (-1 < (int)((uint)*(byte *)(iVar6 + 0x7d) << 0x1b)) {
          FUN_005226b2(uVar14);
        }
      }
      iVar6 = *piVar4;
      fVar22 = *(float *)(iVar6 + 0x158);
      uVar10 = uVar10 & 0xfffffff | (uint)(fVar22 < 0.0) << 0x1f | (uint)(fVar22 == 0.0) << 0x1e;
      uVar13 = uVar10 | (uint)NAN(fVar22) << 0x1c;
      bVar16 = (byte)(uVar10 >> 0x18);
      if (!(bool)(bVar16 >> 6 & 1) && bVar16 >> 7 == ((byte)(uVar13 >> 0x1c) & 1)) {
        if (-1 < (int)((uint)*(byte *)(iVar6 + 0x7d) << 0x1b)) {
          if (iVar7 == 0) {
            if (*(int *)(iVar6 + 0x128) == 1) {
              if (*(char *)(iVar6 + 0x1bf) == '\0') {
                uVar12 = 1;
                uVar10 = 1;
              }
              else {
                uVar12 = -(uint)(*(char *)(iVar6 + 0x2e0) == '\0') >> 0x1f;
                uVar10 = -(uint)(*(char *)(iVar6 + 0x2e1) == '\0') >> 0x1f;
              }
            }
            else {
              uVar12 = -(uint)(*(char *)(iVar6 + 0x1bf) == '\0') >> 0x1f;
              uVar10 = 0;
            }
          }
          else {
            uVar12 = 0;
            uVar10 = 0;
          }
          uVar14 = FUN_0052266e(1,uVar10,1,uVar12);
        }
        iVar6 = *piVar4;
        FUN_00516b34(*(undefined4 *)(iVar6 + 0x138),*(undefined4 *)(iVar6 + 0x13c),
                     *(undefined4 *)(iVar6 + 0x140),*(undefined4 *)(iVar6 + 0x144),
                     *(undefined4 *)(iVar6 + 0x148),*(undefined4 *)(iVar6 + 0x14c),
                     *(undefined4 *)(iVar6 + 0x150),*(undefined4 *)(iVar6 + 0x154));
        iVar6 = *piVar4;
        *(undefined4 *)(iVar6 + 0x158) = 0;
        if (-1 < (int)((uint)*(byte *)(iVar6 + 0x7d) << 0x1b)) {
          FUN_005226b2(uVar14);
        }
      }
      iVar6 = *piVar4;
      if (*(int *)(iVar6 + 0x128) == 2) {
        if (*(int *)(iVar6 + 0x110) != 0) {
          cVar2 = *(char *)(iVar6 + 0x2e2);
          uVar15 = 0;
          fVar31 = (float)*(undefined8 *)(iVar6 + 0x17c);
          fVar27 = (float)((ulonglong)*(undefined8 *)(iVar6 + 0x17c) >> 0x20);
          fVar21 = (float)*(undefined8 *)(iVar6 + 0x148);
          pfVar11 = (float *)((ulonglong)*(undefined8 *)(iVar6 + 0x148) >> 0x20);
          fVar39 = (float)*(undefined8 *)(iVar6 + 0x164);
          fVar40 = (float)((ulonglong)*(undefined8 *)(iVar6 + 0x164) >> 0x20);
          fVar22 = (float)*(undefined8 *)(iVar6 + 0x140);
          pfVar25 = (float *)((ulonglong)*(undefined8 *)(iVar6 + 0x140) >> 0x20);
          if ((cVar2 == '\0') || (*(int *)(iVar6 + 0x118) != 0)) {
            if (-1 < (int)((uint)*(byte *)(iVar6 + 0x7d) << 0x1b)) {
              uVar15 = FUN_0052266e(1,0,1,0);
            }
            FUN_00516b34(fVar22,pfVar25,fVar39,fVar40,fVar21,pfVar11,fVar31,fVar27);
LAB_0051ea72:
            if (-1 < (int)((uint)*(byte *)(*piVar4 + 0x7d) << 0x1b)) {
              FUN_005226b2(uVar15);
            }
          }
          else if (cVar2 == '\x02') {
            local_2d0 = *DAT_0051f50c;
            local_2cc = (float *)DAT_0051f50c[1];
            iVar6 = FUN_00522f50(fVar22,pfVar25,fVar21,pfVar11,fVar39,fVar40,fVar31,fVar27,
                                 &local_2d0,&local_2cc);
            if (iVar6 != 0) {
              iVar6 = *piVar4;
              fVar22 = (float)FUN_004397a8(*(float *)(iVar6 + 0xec) * *(float *)(iVar6 + 0xec) +
                                           *(float *)(iVar6 + 0xf0) * *(float *)(iVar6 + 0xf0));
              fVar21 = (float)FUN_004397a8(*(float *)(iVar6 + 0xf8) * *(float *)(iVar6 + 0xf8) +
                                           *(float *)(iVar6 + 0xfc) * *(float *)(iVar6 + 0xfc));
              uVar10 = uVar13 & 0xfffffff;
              uVar12 = uVar10 | (uint)(ABS(fVar22) < DAT_0051e7c0) << 0x1f;
              uVar13 = uVar12 | (uint)(NAN(ABS(fVar22)) || NAN(DAT_0051e7c0)) << 0x1c;
              bVar16 = (byte)(uVar12 >> 0x1f);
              bVar17 = (byte)(uVar13 >> 0x1c) & 1;
              if (bVar16 != bVar17) {
                uVar13 = uVar10 | (uint)(ABS(fVar21) < DAT_0051e7c0) << 0x1f |
                         (uint)(NAN(ABS(fVar21)) || NAN(DAT_0051e7c0)) << 0x1c;
                bVar17 = (byte)(uVar13 >> 0x18);
                bVar16 = bVar17 >> 7;
                bVar17 = bVar17 >> 4 & 1;
              }
              if (bVar16 == bVar17) {
                FUN_00522622(1);
              }
              if ((int)((uint)*(byte *)(*piVar4 + 0x7d) << 0x1b) < 0) {
                FUN_00522fb4(local_2d0,local_2cc,*(float *)(*piVar4 + 0x2d8) * 0.5);
              }
              else {
                FUN_00523284();
              }
              if (bVar16 == bVar17) {
                FUN_00522622(0);
              }
            }
          }
          else {
            if (cVar2 != '\x01') goto LAB_0051e51e;
            if (*(char *)(iVar6 + 0x2e4) == '\0') {
              local_294 = *(float *)(iVar6 + 0x164);
              local_290 = *(float *)(iVar6 + 0x168);
              local_28c = *(float *)(iVar6 + 0x16c);
              local_288 = *(float *)(iVar6 + 0x170);
              local_284 = *(float *)(iVar6 + 0x174);
              local_280 = *(float *)(iVar6 + 0x178);
              local_27c = *(float *)(iVar6 + 0x17c);
              local_278 = *(float *)(iVar6 + 0x180);
              local_274 = *(float *)(iVar6 + 0x184);
              local_270 = *(float *)(iVar6 + 0x188);
              local_26c = *(float *)(iVar6 + 0x18c);
              local_2c0 = *(float *)(iVar6 + 400);
              local_2bc = *(float *)(iVar6 + 0x194);
              local_2b8 = *(float *)(iVar6 + 0x198);
              local_2b4 = *(float *)(iVar6 + 0x19c);
              local_2b0 = *(float *)(iVar6 + 0x1a0);
              local_2ac = *(float *)(iVar6 + 0x1a4);
              local_2a8 = *(float *)(iVar6 + 0x1a8);
              local_2a4 = *(float *)(iVar6 + 0x1ac);
              local_2a0 = *(float *)(iVar6 + 0x1b0);
              local_29c = *(float *)(iVar6 + 0x1b4);
              local_298 = *(float *)(iVar6 + 0x1b8);
              iVar6 = iVar6 + 0x1bc;
            }
            else {
              local_294 = *(float *)(iVar6 + 0x334);
              local_290 = *(float *)(iVar6 + 0x338);
              local_28c = *(float *)(iVar6 + 0x33c);
              local_288 = *(float *)(iVar6 + 0x340);
              local_284 = *(float *)(iVar6 + 0x344);
              local_280 = *(float *)(iVar6 + 0x348);
              local_27c = *(float *)(iVar6 + 0x34c);
              local_278 = *(float *)(iVar6 + 0x350);
              local_274 = *(float *)(iVar6 + 0x354);
              local_270 = *(float *)(iVar6 + 0x358);
              local_26c = *(float *)(iVar6 + 0x35c);
              local_2c0 = *(float *)(iVar6 + 0x308);
              local_2bc = *(float *)(iVar6 + 0x30c);
              local_2b8 = *(float *)(iVar6 + 0x310);
              local_2b4 = *(float *)(iVar6 + 0x314);
              local_2b0 = *(float *)(iVar6 + 0x318);
              local_2ac = *(float *)(iVar6 + 0x31c);
              local_2a8 = *(float *)(iVar6 + 800);
              local_2a4 = *(float *)(iVar6 + 0x324);
              local_2a0 = *(float *)(iVar6 + 0x328);
              local_29c = *(float *)(iVar6 + 0x32c);
              local_298 = *(float *)(iVar6 + 0x330);
              iVar6 = iVar6 + 0x334;
            }
            iVar6 = FUN_005177a4(&local_2c0,&local_294,iVar6);
            if ((((iVar6 != 1) || (iVar6 = FUN_005177a4(&local_2b8,&local_28c), iVar6 != 1)) ||
                (iVar6 = FUN_005177a4(&local_2b0,&local_284), iVar6 != 1)) ||
               (iVar6 = FUN_005177a4(&local_2a8,&local_27c), iVar6 != 1)) {
              iVar6 = FUN_0051785c(&local_2c0,&local_28c);
              if ((iVar6 != 0) || (iVar6 = FUN_0051785c(&local_294,&local_2c0), iVar6 != 0))
              goto LAB_0051e8c4;
              iVar6 = FUN_0051785c(&local_2c0,&local_284);
              fVar24 = local_284;
              fVar29 = local_280;
              fVar30 = local_2a8;
              fVar33 = local_2a4;
              fVar32 = local_2b4;
              fVar35 = local_2b8;
              fVar34 = local_290;
              fVar41 = local_294;
              fVar23 = local_2c0;
              fVar26 = local_2bc;
              fVar20 = local_28c;
              fVar28 = local_288;
              if ((iVar6 == 0) &&
                 (iVar6 = FUN_0051785c(&local_294,&local_2a8), fVar24 = local_284,
                 fVar29 = local_280, fVar30 = local_2a8, fVar33 = local_2a4, fVar32 = local_2b4,
                 fVar35 = local_2b8, fVar34 = local_290, fVar41 = local_294, fVar23 = local_2c0,
                 fVar26 = local_2bc, fVar20 = local_28c, fVar28 = local_288, iVar6 == 0)) {
                uVar13 = uVar13 & 0xfffffff;
                if (local_288 <= local_2bc) {
                  if (local_288 > local_280) goto LAB_0051e8c4;
                }
                else if (local_288 <= local_280) {
LAB_0051e8c4:
                  fVar24 = local_28c;
                  fVar29 = local_288;
                  fVar30 = local_2c0;
                  fVar33 = local_2bc;
                  fVar32 = local_2ac;
                  fVar35 = local_2b0;
                  fVar34 = local_278;
                  fVar41 = local_27c;
                  fVar23 = local_2a8;
                  fVar26 = local_2a4;
                  fVar20 = local_284;
                  fVar28 = local_280;
                }
              }
              local_2c8 = *local_2cc;
              local_2c4 = (float *)local_2cc[1];
              local_2d0 = *DAT_0051f790;
              local_2cc = (float *)DAT_0051f790[1];
              iVar6 = FUN_00522f50(fVar20,fVar28,fVar24,fVar29,fVar23,fVar26,fVar30,fVar33,
                                   &local_2c8,&local_2c4);
              iVar8 = FUN_00522f50(fVar41,fVar34,fVar20,fVar28,fVar23,fVar26,fVar35,fVar32,
                                   &local_2d0,&local_2cc);
              fVar24 = (float)FUN_00524218((local_2d0 - local_2c8) * (local_2d0 - local_2c8) +
                                           ((float)local_2cc - (float)local_2c4) *
                                           ((float)local_2cc - (float)local_2c4));
              iVar9 = *piVar4;
              uVar13 = uVar13 & 0xfffffff;
              if ((*(float *)(iVar9 + 0x2dc) * *(float *)(iVar9 + 0x2d8) < fVar24) ||
                 (iVar8 == 0 || iVar6 == 0)) {
                fVar20 = fVar39;
                fVar28 = fVar40;
                fVar23 = fVar31;
                fVar26 = fVar27;
                if (-1 < (int)((uint)*(byte *)(iVar9 + 0x7d) << 0x1b)) {
                  uVar15 = FUN_0052266e(1,0,1,0);
                }
              }
              else {
                fVar22 = local_2c8;
                pfVar25 = local_2c4;
                fVar21 = local_2d0;
                pfVar11 = local_2cc;
                if (-1 < (int)((uint)*(byte *)(iVar9 + 0x7d) << 0x1b)) {
                  uVar15 = FUN_0052266e(0,1,1,0);
                  fVar22 = local_2c8;
                  pfVar25 = local_2c4;
                  fVar21 = local_2d0;
                  pfVar11 = local_2cc;
                }
              }
              FUN_00516b34(fVar22,pfVar25,fVar20,fVar28,fVar21,pfVar11,fVar23,fVar26);
              goto LAB_0051ea72;
            }
          }
        }
      }
      FUN_005226b2(uVar14);
      iVar6 = *piVar4;
      *(undefined4 *)(iVar6 + 0x128) = 0;
      if (iVar5 < 0) {
        return 0;
      }
      bVar19 = *(int *)(iVar6 + 0x110) != 0;
      cVar2 = '\0';
      if (bVar19) {
        cVar2 = *(char *)(iVar6 + 0x2e0);
      }
      pfVar25 = extraout_s1;
      fVar22 = extraout_s2;
      fVar21 = extraout_s4;
      if (bVar19 && cVar2 != '\0') {
        if (cVar2 == '\x02') {
          fVar21 = *(float *)(iVar6 + 400);
          fVar22 = *(float *)(iVar6 + 0x198);
          uVar10 = uVar13 & 0xfffffff;
          uVar13 = uVar10 | (uint)(fVar21 == fVar22) << 0x1e;
          bVar16 = 0;
          if ((byte)(uVar13 >> 0x1e) != 0) {
            fVar22 = *(float *)(iVar6 + 0x194);
            uVar13 = uVar10 | (uint)(fVar22 == *(float *)(iVar6 + 0x19c)) << 0x1e;
            bVar16 = (byte)(uVar13 >> 0x1e);
          }
          if (bVar16 != 0) {
            fVar27 = *(float *)(iVar6 + 0x1a0);
            fVar31 = *(float *)(iVar6 + 0x1a8);
            uVar10 = uVar13 & 0xfffffff;
            uVar13 = uVar10 | (uint)(fVar27 == fVar31) << 0x1e;
            bVar16 = 0;
            if ((byte)(uVar13 >> 0x1e) != 0) {
              fVar31 = *(float *)(iVar6 + 0x1a4);
              uVar13 = uVar10 | (uint)(fVar31 == *(float *)(iVar6 + 0x1ac)) << 0x1e;
              bVar16 = (byte)(uVar13 >> 0x1e);
            }
            if (bVar16 != 0) {
              fVar39 = *(float *)(iVar6 + 300) * -0.5;
              bVar19 = -1 < (int)((uint)*(byte *)(iVar6 + 0x7d) << 0x1b);
              uVar14 = FUN_0052266e(bVar19,0,bVar19,bVar19);
              FUN_00516b34(fVar39 + fVar21,fVar22,fVar21,fVar22,fVar27,fVar31,fVar39 + fVar27,fVar31
                          );
              goto LAB_0051eb72;
            }
          }
          local_2c8 = *(float *)(iVar6 + 0x138);
          local_2c4 = *(float **)(iVar6 + 0x13c);
          local_2d0 = *(float *)(iVar6 + 0x150);
          local_2cc = *(float **)(iVar6 + 0x154);
          fVar31 = *(float *)(iVar6 + 300) * 0.5;
          uVar13 = uVar13 & 0xfffffff;
          fVar22 = *(float *)(iVar6 + 0x150);
          uVar37 = *(undefined8 *)(iVar6 + 0x138);
          fVar21 = *(float *)(iVar6 + 0x154);
          bVar16 = 0;
          if (*(float *)(iVar6 + 0x138) < *(float *)(iVar6 + 0x140)) {
            uVar13 = uVar13 | (uint)(fVar22 < *(float *)(iVar6 + 0x148)) << 0x1f;
            bVar16 = (byte)(uVar13 >> 0x1f);
          }
          if (bVar16 != 0) {
            iVar7 = 1;
          }
          fVar40 = (float)uVar37;
          fVar24 = fVar22 - fVar40;
          fVar20 = (float)((ulonglong)uVar37 >> 0x20);
          fVar39 = fVar21 - fVar20;
          fVar27 = (float)FUN_00524218(fVar24 * fVar24 + fVar39 * fVar39);
          fVar39 = -(fVar39 / fVar27);
          uVar10 = uVar13 & 0xfffffff | (uint)(fVar39 < 0.0) << 0x1f | (uint)(fVar39 == 0.0) << 0x1e
                   | (uint)(0.0 <= fVar39) << 0x1d;
          uVar13 = uVar10 | (uint)NAN(fVar39) << 0x1c;
          bVar16 = (byte)(uVar10 >> 0x18);
          if (iVar7 == 0) {
            if ((bool)(bVar16 >> 5 & 1) && !(bool)(bVar16 >> 6 & 1)) goto LAB_0051eca8;
LAB_0051ecea:
            fVar22 = fVar22 - fVar31 * fVar39;
            fVar27 = fVar31 * (fVar24 / fVar27);
            fVar40 = fVar40 - fVar31 * fVar39;
            fVar21 = fVar21 - fVar27;
            fVar27 = fVar20 - fVar27;
          }
          else {
            if (!(bool)(bVar16 >> 6 & 1) && bVar16 >> 7 == ((byte)(uVar13 >> 0x1c) & 1))
            goto LAB_0051ecea;
LAB_0051eca8:
            fVar22 = fVar31 * fVar39 + fVar22;
            fVar27 = fVar31 * (fVar24 / fVar27);
            fVar40 = fVar31 * fVar39 + fVar40;
            fVar21 = fVar27 + fVar21;
            fVar27 = fVar27 + fVar20;
          }
          bVar19 = -1 < (int)((uint)*(byte *)(*piVar4 + 0x7d) << 0x1b);
          uVar14 = FUN_0052266e(0,bVar19,bVar19,bVar19);
          FUN_00516b34(local_2c8,local_2c4,local_2d0,local_2cc,fVar22,fVar21,fVar40,fVar27);
          pfVar25 = extraout_s1_01;
          fVar22 = extraout_s2_01;
          fVar21 = extraout_s4_01;
          if ((int)((uint)*(byte *)(*piVar4 + 0x7d) << 0x1b) < 0) goto LAB_0051eb76;
        }
        else {
          if (cVar2 != '\x01') goto LAB_0051f756;
          fVar21 = *(float *)(iVar6 + 400);
          fVar22 = *(float *)(iVar6 + 0x198);
          uVar10 = uVar13 & 0xfffffff;
          uVar13 = uVar10 | (uint)(fVar21 == fVar22) << 0x1e;
          bVar16 = 0;
          if ((byte)(uVar13 >> 0x1e) != 0) {
            fVar22 = *(float *)(iVar6 + 0x194);
            uVar13 = uVar10 | (uint)(fVar22 == *(float *)(iVar6 + 0x19c)) << 0x1e;
            bVar16 = (byte)(uVar13 >> 0x1e);
          }
          if (bVar16 != 0) {
            fVar27 = *(float *)(iVar6 + 0x1a0);
            fVar31 = *(float *)(iVar6 + 0x1a8);
            uVar10 = uVar13 & 0xfffffff;
            uVar13 = uVar10 | (uint)(fVar27 == fVar31) << 0x1e;
            bVar16 = 0;
            if ((byte)(uVar13 >> 0x1e) != 0) {
              fVar31 = *(float *)(iVar6 + 0x1a4);
              uVar13 = uVar10 | (uint)(fVar31 == *(float *)(iVar6 + 0x1ac)) << 0x1e;
              bVar16 = (byte)(uVar13 >> 0x1e);
            }
            if (bVar16 != 0) {
              fVar39 = *(float *)(iVar6 + 0x2d8);
              fVar24 = (fVar21 - fVar27) / fVar39;
              fVar27 = (fVar21 + fVar27) * 0.5;
              fVar20 = fVar39 * 0.5;
              fVar39 = (fVar22 - fVar31) / fVar39;
              fVar40 = (fVar22 + fVar31) * 0.5;
              iVar5 = FUN_00522f1c(fVar20);
              iVar5 = iVar5 / 2;
              fVar22 = (float)VectorSignedToFloat(iVar5,(byte)(uVar13 >> 0x16) & 3);
              fVar22 = DAT_0051f160 / fVar22;
              fVar21 = (float)FUN_00524130(fVar22);
              fVar31 = (float)FUN_0052405c(fVar22);
              fVar31 = -fVar31;
              local_1f0 = fVar27 - fVar24 * fVar20;
              local_1ec = fVar40 - fVar39 * fVar20;
              fVar22 = (float)(iVar5 - 1);
              if (fVar22 != 0.0 && 0 < iVar5) {
                pfVar25 = (float *)(auStack_200 + 6);
                if (((uint)fVar22 & 3) != 0) {
                  do {
                    *pfVar25 = fVar27 + fVar20 * fVar24;
                    pfVar25[1] = fVar40 + fVar20 * fVar39;
                    fVar22 = fVar31 * fVar24;
                    fVar24 = fVar21 * fVar24 - fVar31 * fVar39;
                    loopEnd();
                    pfVar25 = (float *)(extraout_r1 >> 9);
                    fVar39 = fVar22 + fVar21 * fVar39;
                  } while( true );
                }
                local_2d0 = fVar22;
                if ((uint)fVar22 >> 2 != 0) {
                  do {
                    *pfVar25 = fVar27 + fVar20 * fVar24;
                    pfVar25[1] = fVar40 + fVar20 * fVar39;
                    fVar22 = fVar21 * fVar24 - fVar31 * fVar39;
                    pfVar25[2] = fVar27 + fVar20 * fVar22;
                    fVar39 = fVar31 * fVar24 + fVar21 * fVar39;
                    fVar28 = fVar31 * fVar22 + fVar21 * fVar39;
                    fVar22 = fVar21 * fVar22 - fVar31 * fVar39;
                    pfVar25[4] = fVar27 + fVar20 * fVar22;
                    pfVar25[3] = fVar40 + fVar20 * fVar39;
                    fVar24 = fVar31 * fVar22 + fVar21 * fVar28;
                    fVar22 = fVar21 * fVar22 - fVar31 * fVar28;
                    pfVar25[5] = fVar40 + fVar20 * fVar28;
                    pfVar25[6] = fVar27 + fVar20 * fVar22;
                    pfVar25[7] = fVar40 + fVar20 * fVar24;
                    fVar39 = fVar31 * fVar22 + fVar21 * fVar24;
                    fVar24 = fVar21 * fVar22 - fVar31 * fVar24;
                    loopEnd();
                    pfVar25 = (float *)(extraout_r1 >> 9);
                  } while( true );
                }
              }
              uVar14 = FUN_0052266e(0,-(uint)((*(byte *)(*piVar4 + 0x7d) & 0x10) == 0) >> 0x1f,0,0);
              FUN_00523a34(auStack_200 + 4,fVar22,2);
              bVar19 = -1 < (int)((uint)*(byte *)(*piVar4 + 0x7d) << 0x1b);
              FUN_0052266e(0,bVar19,bVar19,0);
              FUN_00522a24(local_1f0,local_1ec,auStack_200[iVar5 * 2],auStack_200[iVar5 * 2 + 1],
                           auStack_200[iVar5 * 2 + 2],auStack_200[iVar5 * 2 + 3]);
              goto LAB_0051eb72;
            }
          }
          fVar22 = *(float *)(iVar6 + 0x2d8);
          fVar24 = (*(float *)(iVar6 + 0x150) - *(float *)(iVar6 + 0x138)) / fVar22;
          fVar39 = (*(float *)(iVar6 + 0x150) + *(float *)(iVar6 + 0x138)) * 0.5;
          fVar20 = fVar22 * 0.5;
          fVar22 = (*(float *)(iVar6 + 0x154) - *(float *)(iVar6 + 0x13c)) / fVar22;
          fVar40 = (*(float *)(iVar6 + 0x154) + *(float *)(iVar6 + 0x13c)) * 0.5;
          iVar5 = FUN_00522f1c(fVar20);
          iVar5 = iVar5 / 2;
          fVar21 = (float)VectorSignedToFloat(iVar5,(byte)(uVar13 >> 0x16) & 3);
          fVar21 = DAT_0051f160 / fVar21;
          fVar31 = (float)FUN_00524130(fVar21);
          fVar27 = (float)FUN_0052405c(fVar21);
          fVar27 = -fVar27;
          local_1f0 = fVar39 - fVar24 * fVar20;
          local_1ec = fVar40 - fVar22 * fVar20;
          fVar21 = (float)(iVar5 - 1);
          if (fVar21 != 0.0 && 0 < iVar5) {
            pfVar25 = (float *)(auStack_200 + 6);
            if (((uint)fVar21 & 3) != 0) {
              do {
                *pfVar25 = fVar39 + fVar20 * fVar24;
                pfVar25[1] = fVar40 + fVar20 * fVar22;
                fVar21 = fVar27 * fVar24;
                fVar24 = fVar31 * fVar24 - fVar27 * fVar22;
                loopEnd();
                pfVar25 = (float *)(extraout_r1_00 >> 9);
                fVar22 = fVar21 + fVar31 * fVar22;
              } while( true );
            }
            local_2d0 = fVar21;
            if ((uint)fVar21 >> 2 != 0) {
              do {
                *pfVar25 = fVar39 + fVar20 * fVar24;
                pfVar25[1] = fVar40 + fVar20 * fVar22;
                fVar21 = fVar31 * fVar24 - fVar27 * fVar22;
                pfVar25[2] = fVar39 + fVar20 * fVar21;
                fVar24 = fVar27 * fVar24 + fVar31 * fVar22;
                fVar28 = fVar27 * fVar21 + fVar31 * fVar24;
                fVar22 = fVar31 * fVar21 - fVar27 * fVar24;
                pfVar25[4] = fVar39 + fVar20 * fVar22;
                pfVar25[3] = fVar40 + fVar20 * fVar24;
                fVar24 = fVar27 * fVar22 + fVar31 * fVar28;
                fVar21 = fVar31 * fVar22 - fVar27 * fVar28;
                pfVar25[5] = fVar40 + fVar20 * fVar28;
                pfVar25[6] = fVar39 + fVar20 * fVar21;
                pfVar25[7] = fVar40 + fVar20 * fVar24;
                fVar22 = fVar27 * fVar21 + fVar31 * fVar24;
                fVar24 = fVar31 * fVar21 - fVar27 * fVar24;
                loopEnd();
                pfVar25 = (float *)(extraout_r1_00 >> 9);
              } while( true );
            }
          }
          uVar14 = FUN_0052266e(0,-(uint)((*(byte *)(*piVar4 + 0x7d) & 0x10) == 0) >> 0x1f,0,0);
          FUN_00523a34(auStack_200 + 4,fVar21,2);
          bVar19 = -1 < (int)((uint)*(byte *)(*piVar4 + 0x7d) << 0x1b);
          FUN_0052266e(0,bVar19,bVar19,0);
          FUN_00522a24(local_1f0,local_1ec,auStack_200[iVar5 * 2],auStack_200[iVar5 * 2 + 1],
                       auStack_200[iVar5 * 2 + 2],auStack_200[iVar5 * 2 + 3]);
        }
LAB_0051eb72:
        FUN_005226b2(uVar14);
        pfVar25 = extraout_s1_00;
        fVar22 = extraout_s2_00;
        fVar21 = extraout_s4_00;
      }
LAB_0051eb76:
      iVar6 = *piVar4;
      bVar19 = *(int *)(iVar6 + 0x110) == 0;
      cVar2 = '\0';
      if (!bVar19) {
        cVar2 = *(char *)(iVar6 + 0x2e1);
      }
      if (bVar19 || cVar2 == '\0') {
        return 0;
      }
      if (cVar2 != '\x02') {
        if (cVar2 != '\x01') {
LAB_0051f756:
          *(undefined4 *)(iVar6 + 0x114) = 0;
          *(undefined4 *)(iVar6 + 0x118) = 0;
          FUN_0051565c(0x800000);
          iVar5 = *piVar4;
          *(undefined4 *)(iVar5 + 0x114) = 0;
          *(undefined4 *)(iVar5 + 0x118) = 0;
          FUN_0051565c(0x800000);
          return 0x800000;
        }
        fVar21 = *(float *)(iVar6 + 0x198);
        fVar31 = *(float *)(iVar6 + 400);
        uVar10 = uVar13 & 0xfffffff | (uint)(fVar31 == fVar21) << 0x1e;
        bVar16 = 0;
        if ((byte)(uVar10 >> 0x1e) != 0) {
          fVar22 = *(float *)(iVar6 + 0x194);
          uVar10 = uVar13 & 0xfffffff | (uint)(fVar22 == *(float *)(iVar6 + 0x19c)) << 0x1e;
          bVar16 = (byte)(uVar10 >> 0x1e);
        }
        if (bVar16 != 0) {
          fVar39 = *(float *)(iVar6 + 0x1a0);
          fVar27 = *(float *)(iVar6 + 0x1a8);
          uVar13 = uVar10 & 0xfffffff;
          uVar10 = uVar13 | (uint)(fVar39 == fVar27) << 0x1e;
          bVar16 = 0;
          if ((byte)(uVar10 >> 0x1e) != 0) {
            fVar27 = *(float *)(iVar6 + 0x1a4);
            uVar10 = uVar13 | (uint)(fVar27 == *(float *)(iVar6 + 0x1ac)) << 0x1e;
            bVar16 = (byte)(uVar10 >> 0x1e);
          }
          if (bVar16 != 0) {
            fVar21 = *(float *)(iVar6 + 0x2d8);
            fVar24 = (fVar31 - fVar39) / fVar21;
            fVar39 = (fVar31 + fVar39) * 0.5;
            fVar20 = fVar21 * 0.5;
            fVar21 = (fVar22 - fVar27) / fVar21;
            fVar40 = (fVar22 + fVar27) * 0.5;
            iVar5 = FUN_00522f1c(fVar20);
            iVar5 = iVar5 / 2;
            fVar22 = (float)VectorSignedToFloat(iVar5,(byte)(uVar10 >> 0x16) & 3);
            fVar22 = DAT_0051f510 / fVar22;
            fVar31 = (float)FUN_00524130(fVar22);
            fVar27 = (float)FUN_0052405c(fVar22);
            local_1f0 = fVar39 - fVar24 * fVar20;
            local_1ec = fVar40 - fVar21 * fVar20;
            fVar22 = (float)(iVar5 - 1);
            if (fVar22 != 0.0 && 0 < iVar5) {
              pfVar25 = (float *)(auStack_200 + 6);
              if (((uint)fVar22 & 3) != 0) {
                do {
                  *pfVar25 = fVar39 + fVar20 * fVar24;
                  pfVar25[1] = fVar40 + fVar20 * fVar21;
                  fVar22 = fVar27 * fVar24;
                  fVar24 = fVar31 * fVar24 - fVar27 * fVar21;
                  loopEnd();
                  pfVar25 = (float *)(extraout_r1_01 >> 9);
                  fVar21 = fVar22 + fVar31 * fVar21;
                } while( true );
              }
              local_2d0 = fVar22;
              if ((uint)fVar22 >> 2 != 0) {
                do {
                  *pfVar25 = fVar39 + fVar20 * fVar24;
                  pfVar25[1] = fVar40 + fVar20 * fVar21;
                  fVar22 = fVar31 * fVar24 - fVar27 * fVar21;
                  pfVar25[2] = fVar39 + fVar20 * fVar22;
                  fVar21 = fVar27 * fVar24 + fVar31 * fVar21;
                  fVar28 = fVar27 * fVar22 + fVar31 * fVar21;
                  fVar22 = fVar31 * fVar22 - fVar27 * fVar21;
                  pfVar25[4] = fVar39 + fVar20 * fVar22;
                  pfVar25[3] = fVar40 + fVar20 * fVar21;
                  fVar24 = fVar27 * fVar22 + fVar31 * fVar28;
                  fVar22 = fVar31 * fVar22 - fVar27 * fVar28;
                  pfVar25[5] = fVar40 + fVar20 * fVar28;
                  pfVar25[6] = fVar39 + fVar20 * fVar22;
                  pfVar25[7] = fVar40 + fVar20 * fVar24;
                  fVar21 = fVar27 * fVar22 + fVar31 * fVar24;
                  fVar24 = fVar31 * fVar22 - fVar27 * fVar24;
                  loopEnd();
                  pfVar25 = (float *)(extraout_r1_01 >> 9);
                } while( true );
              }
            }
            uVar14 = FUN_0052266e(0,-(uint)((*(byte *)(*piVar4 + 0x7d) & 0x10) == 0) >> 0x1f,0,0);
            FUN_00523a34(auStack_200 + 4,fVar22,2);
            bVar19 = -1 < (int)((uint)*(byte *)(*piVar4 + 0x7d) << 0x1b);
            FUN_0052266e(0,bVar19,bVar19,0);
            FUN_00522a24(local_1f0,local_1ec,auStack_200[iVar5 * 2],auStack_200[iVar5 * 2 + 1],
                         auStack_200[iVar5 * 2 + 2],auStack_200[iVar5 * 2 + 3]);
            goto LAB_0051f1ce;
          }
        }
        fVar22 = *(float *)(iVar6 + 0x2d8);
        fVar24 = (*(float *)(iVar6 + 0x1a0) - fVar21) / fVar22;
        fVar39 = (*(float *)(iVar6 + 0x1a0) + fVar21) * 0.5;
        fVar20 = fVar22 * 0.5;
        fVar22 = (*(float *)(iVar6 + 0x1a4) - *(float *)(iVar6 + 0x19c)) / fVar22;
        fVar40 = (*(float *)(iVar6 + 0x1a4) + *(float *)(iVar6 + 0x19c)) * 0.5;
        iVar5 = FUN_00522f1c(fVar20);
        iVar5 = iVar5 / 2;
        fVar21 = (float)VectorSignedToFloat(iVar5,(byte)(uVar10 >> 0x16) & 3);
        fVar21 = DAT_0051f794 / fVar21;
        fVar31 = (float)FUN_00524130(fVar21);
        fVar27 = (float)FUN_0052405c(fVar21);
        local_1f0 = fVar39 - fVar24 * fVar20;
        local_1ec = fVar40 - fVar22 * fVar20;
        fVar21 = (float)(iVar5 - 1);
        if (fVar21 != 0.0 && 0 < iVar5) {
          pfVar25 = (float *)(auStack_200 + 6);
          if (((uint)fVar21 & 3) != 0) {
            do {
              *pfVar25 = fVar39 + fVar20 * fVar24;
              pfVar25[1] = fVar40 + fVar20 * fVar22;
              fVar21 = fVar27 * fVar24;
              fVar24 = fVar31 * fVar24 - fVar27 * fVar22;
              loopEnd();
              pfVar25 = (float *)(extraout_r1_02 >> 9);
              fVar22 = fVar21 + fVar31 * fVar22;
            } while( true );
          }
          local_2d0 = fVar21;
          if ((uint)fVar21 >> 2 != 0) {
            do {
              *pfVar25 = fVar39 + fVar20 * fVar24;
              pfVar25[1] = fVar40 + fVar20 * fVar22;
              fVar21 = fVar31 * fVar24 - fVar27 * fVar22;
              pfVar25[2] = fVar39 + fVar20 * fVar21;
              fVar24 = fVar27 * fVar24 + fVar31 * fVar22;
              fVar28 = fVar27 * fVar21 + fVar31 * fVar24;
              fVar22 = fVar31 * fVar21 - fVar27 * fVar24;
              pfVar25[4] = fVar39 + fVar20 * fVar22;
              pfVar25[3] = fVar40 + fVar20 * fVar24;
              fVar24 = fVar27 * fVar22 + fVar31 * fVar28;
              fVar21 = fVar31 * fVar22 - fVar27 * fVar28;
              pfVar25[5] = fVar40 + fVar20 * fVar28;
              pfVar25[6] = fVar39 + fVar20 * fVar21;
              pfVar25[7] = fVar40 + fVar20 * fVar24;
              fVar22 = fVar27 * fVar21 + fVar31 * fVar24;
              fVar24 = fVar31 * fVar21 - fVar27 * fVar24;
              loopEnd();
              pfVar25 = (float *)(extraout_r1_02 >> 9);
            } while( true );
          }
        }
        uVar14 = FUN_0052266e(0,-(uint)((*(byte *)(*piVar4 + 0x7d) & 0x10) == 0) >> 0x1f,0,0);
        FUN_00523a34(auStack_200 + 4,fVar21,2);
        bVar19 = -1 < (int)((uint)*(byte *)(*piVar4 + 0x7d) << 0x1b);
        FUN_0052266e(0,bVar19,bVar19,0);
        FUN_00522a24(local_1f0,local_1ec,auStack_200[iVar5 * 2],auStack_200[iVar5 * 2 + 1],
                     auStack_200[iVar5 * 2 + 2],auStack_200[iVar5 * 2 + 3]);
        goto LAB_0051f1ce;
      }
      fVar27 = *(float *)(iVar6 + 0x198);
      fVar31 = *(float *)(iVar6 + 400);
      bVar19 = fVar31 == fVar27;
      if (bVar19) {
        pfVar25 = *(float **)(iVar6 + 0x194);
        fVar22 = *(float *)(iVar6 + 0x19c);
      }
      if (bVar19 && (bVar19 && (float)pfVar25 == fVar22)) {
        fVar39 = *(float *)(iVar6 + 0x1a0);
        fVar22 = *(float *)(iVar6 + 0x1a8);
        bVar19 = fVar39 == fVar22;
        if (bVar19) {
          fVar22 = *(float *)(iVar6 + 0x1a4);
          fVar21 = *(float *)(iVar6 + 0x1ac);
        }
        if (bVar19 && (bVar19 && fVar22 == fVar21)) {
          fVar21 = *(float *)(iVar6 + 300) * 0.5;
          local_2d0 = fVar21 + fVar31;
          bVar19 = -1 < (int)((uint)*(byte *)(iVar6 + 0x7d) << 0x1b);
          local_2cc = pfVar25;
          local_2c8 = fVar31;
          local_2c4 = pfVar25;
          uVar14 = FUN_0052266e(bVar19,bVar19,bVar19,0);
          FUN_00516b34(local_2c8,local_2c4,local_2d0,local_2cc,fVar21 + fVar39,fVar22,fVar39,fVar22)
          ;
          goto LAB_0051f1ce;
        }
      }
      bVar19 = fVar31 < fVar27;
      bVar18 = NAN(fVar31) || NAN(fVar27);
      uVar37 = *(undefined8 *)(iVar6 + 0x198);
      uVar36 = *(undefined8 *)(iVar6 + 0x1a0);
      fVar31 = *(float *)(iVar6 + 300) * 0.5;
      fVar22 = *(float *)(iVar6 + 0x1a0);
      fVar39 = *(float *)(iVar6 + 0x19c);
      fVar21 = *(float *)(iVar6 + 0x1a4);
      if (!bVar19) {
        bVar19 = *(float *)(iVar6 + 0x1a8) < fVar22;
        bVar18 = NAN(*(float *)(iVar6 + 0x1a8)) || NAN(fVar22);
      }
      fVar24 = fVar22 - fVar27;
      fVar20 = fVar21 - fVar39;
      fVar40 = (float)FUN_00524218(fVar24 * fVar24 + fVar20 * fVar20);
      fVar20 = -(fVar20 / fVar40);
      if (bVar19 == bVar18) {
        if (0.0 < fVar20) goto LAB_0051f298;
LAB_0051f256:
        fVar22 = fVar31 * fVar20 + fVar22;
        fVar40 = fVar31 * (fVar24 / fVar40);
        fVar27 = fVar31 * fVar20 + fVar27;
        fVar21 = fVar40 + fVar21;
        fVar40 = fVar40 + fVar39;
      }
      else {
        if (0.0 < fVar20) goto LAB_0051f256;
LAB_0051f298:
        fVar22 = fVar22 - fVar31 * fVar20;
        fVar40 = fVar31 * (fVar24 / fVar40);
        fVar27 = fVar27 - fVar31 * fVar20;
        fVar21 = fVar21 - fVar40;
        fVar40 = fVar39 - fVar40;
      }
      bVar19 = -1 < (int)((uint)*(byte *)(*piVar4 + 0x7d) << 0x1b);
      uVar14 = FUN_0052266e(0,bVar19,bVar19,bVar19);
      FUN_00516b34((int)uVar37,(int)((ulonglong)uVar37 >> 0x20),(int)uVar36,
                   (int)((ulonglong)uVar36 >> 0x20),fVar22,fVar21,fVar27,fVar40);
      if ((int)((uint)*(byte *)(*piVar4 + 0x7d) << 0x1b) < 0) {
        return 0;
      }
LAB_0051f1ce:
      FUN_005226b2(uVar14);
      return 0;
    }
    bVar16 = *(byte *)(param_1[2] + uVar13);
    uVar13 = uVar13 + 1;
    iVar5 = FUN_005156b8(param_1,bVar16,&local_238);
    fVar27 = local_220;
    fVar31 = local_224;
    fVar21 = local_228;
    fVar22 = local_22c;
    bVar17 = bVar16 & 0x6f;
    if (iVar5 != 0) goto LAB_0051e0fc;
    if ((local_236 == '\0') && (-1 < (int)((uint)bVar16 << 0x18))) {
      if (bVar17 == 6 || bVar17 == 8) {
        FUN_00517e18(local_22c,local_228,local_21c,uStack_218,local_214,uStack_210,local_224,
                     local_220);
      }
      else if ((bVar17 == 5) || (bVar17 == 7)) {
        FUN_00519290(local_22c,local_228,local_21c,uStack_218,local_224,local_220);
      }
      else if ((bVar16 & 0xf) == 9) {
        iVar5 = FUN_0051a8ec(param_1,&local_238);
        if (iVar5 != 0) goto LAB_0051e0fc;
      }
      else if (bVar17 != 10 && bVar17 != 0xb) {
        fVar40 = local_224 - local_22c;
        fVar39 = local_220 - local_228;
        in_fpscr = in_fpscr & 0xfffffff;
        if (DAT_0051d8a4 <= ABS(fVar40 * fVar40 + fVar39 * fVar39)) {
          local_2d0 = (float)FUN_004397a8();
          iVar5 = *piVar4;
          fVar40 = fVar40 * (1.0 / local_2d0);
          fVar39 = fVar39 * (1.0 / local_2d0);
          fVar20 = *(float *)(iVar5 + 0x130) * 0.5 * fVar39;
          fVar28 = fVar22 - fVar20;
          fVar24 = *(float *)(iVar5 + 0x134) * 0.5 * fVar40;
          fVar29 = fVar24 + fVar21;
          uVar37 = CONCAT44(fVar29,fVar28);
          local_2b8 = fVar31 - fVar20;
          local_2b4 = fVar24 + fVar27;
          local_2c0 = fVar20 + fVar31;
          local_2bc = fVar27 - fVar24;
          *(float *)(iVar5 + 400) = fVar28;
          *(float *)(iVar5 + 0x194) = fVar29;
          fVar20 = fVar20 + fVar22;
          iVar5 = *piVar4;
          fVar21 = fVar21 - fVar24;
          uVar36 = CONCAT44(fVar21,fVar20);
          *(float *)(iVar5 + 0x198) = local_2b8;
          *(float *)(iVar5 + 0x19c) = local_2b4;
          iVar5 = *piVar4;
          *(float *)(iVar5 + 0x1a0) = local_2c0;
          *(float *)(iVar5 + 0x1a4) = local_2bc;
          iVar5 = *piVar4;
          *(float *)(iVar5 + 0x1a8) = fVar20;
          *(float *)(iVar5 + 0x1ac) = fVar21;
          iVar5 = *piVar4;
          if (*(int *)(iVar5 + 0x110) == 0) {
            uVar14 = FUN_005226b2(*(undefined4 *)(iVar5 + 0x8c));
            FUN_00516b34(fVar28,fVar29,local_2b8,local_2b4,local_2c0,local_2bc,fVar20,fVar21);
          }
          else {
            bVar19 = -1 < (int)((uint)*(byte *)(iVar5 + 0x7d) << 0x1b);
            uVar14 = FUN_0052266e(bVar19,0,bVar19,0);
            iVar5 = *piVar4;
            uVar10 = in_fpscr & 0xfffffff | (uint)(*(float *)(iVar5 + 0x184) == 0.0) << 0x1e |
                     (uint)(0.0 <= *(float *)(iVar5 + 0x184)) << 0x1d;
            bVar16 = (byte)(uVar10 >> 0x18);
            if ((bool)(bVar16 >> 5 & 1) && !(bool)(bVar16 >> 6)) {
              FUN_00516b34(*(undefined4 *)(iVar5 + 0x164),*(undefined4 *)(iVar5 + 0x168),
                           *(undefined4 *)(iVar5 + 0x16c),*(undefined4 *)(iVar5 + 0x170),
                           *(undefined4 *)(iVar5 + 0x174),*(undefined4 *)(iVar5 + 0x178),
                           *(undefined4 *)(iVar5 + 0x17c),*(undefined4 *)(iVar5 + 0x180));
              iVar5 = *piVar4;
              uVar10 = uVar10 & 0xfffffff;
              if (ABS(*(float *)(iVar5 + 0x188) * fVar39 - *(float *)(iVar5 + 0x18c) * fVar40) <
                  DAT_0051d8a8) {
                uVar37 = *(undefined8 *)(iVar5 + 0x16c);
                uVar36 = *(undefined8 *)(iVar5 + 0x174);
                goto LAB_0051d794;
              }
              uVar3 = *(undefined8 *)(iVar5 + 0x16c);
              local_298 = fVar28;
              local_294 = fVar29;
              if (*(int *)(iVar5 + 0x110) == 0) goto LAB_0051d794;
              cVar2 = *(char *)(iVar5 + 0x2e2);
              uVar15 = 0;
              pfVar25 = (float *)((ulonglong)*(undefined8 *)(iVar5 + 0x174) >> 0x20);
              fVar31 = (float)((ulonglong)uVar3 >> 0x20);
              fVar27 = (float)*(undefined8 *)(iVar5 + 0x174);
              fVar22 = (float)uVar3;
              if ((cVar2 == '\0') || (*(int *)(iVar5 + 0x118) != 0)) {
                if (-1 < (int)((uint)*(byte *)(iVar5 + 0x7d) << 0x1b)) {
                  uVar15 = FUN_0052266e(1,0,1,0);
                }
                FUN_00516b34(fVar22,fVar31,local_298,local_294,fVar27,pfVar25,fVar20,fVar21);
                bVar16 = *(byte *)(*piVar4 + 0x7d);
joined_r0x0051d790:
                if (-1 < (int)((uint)bVar16 << 0x1b)) {
                  FUN_005226b2(uVar15);
                }
                goto LAB_0051d794;
              }
              if (cVar2 == '\x02') {
                local_2c8 = *DAT_0051e4a8;
                local_2c4 = (float *)DAT_0051e4a8[1];
                iVar5 = FUN_00522f50(fVar22,fVar31,fVar27,pfVar25,fVar28,fVar29,fVar20,fVar21,
                                     &local_2c8,&local_2c4);
                if (iVar5 != 0) {
                  iVar5 = *piVar4;
                  fVar22 = (float)FUN_004397a8(*(float *)(iVar5 + 0xec) * *(float *)(iVar5 + 0xec) +
                                               *(float *)(iVar5 + 0xf0) * *(float *)(iVar5 + 0xf0));
                  fVar21 = (float)FUN_004397a8(*(float *)(iVar5 + 0xf8) * *(float *)(iVar5 + 0xf8) +
                                               *(float *)(iVar5 + 0xfc) * *(float *)(iVar5 + 0xfc));
                  uVar12 = uVar10 & 0xfffffff;
                  uVar1 = uVar12 | (uint)(ABS(fVar22) < DAT_0051d8ac) << 0x1f;
                  uVar10 = uVar1 | (uint)(NAN(ABS(fVar22)) || NAN(DAT_0051d8ac)) << 0x1c;
                  bVar16 = (byte)(uVar1 >> 0x1f);
                  bVar17 = (byte)(uVar10 >> 0x1c) & 1;
                  if (bVar16 != bVar17) {
                    uVar10 = uVar12 | (uint)(ABS(fVar21) < DAT_0051d8ac) << 0x1f |
                             (uint)(NAN(ABS(fVar21)) || NAN(DAT_0051d8ac)) << 0x1c;
                    bVar17 = (byte)(uVar10 >> 0x18);
                    bVar16 = bVar17 >> 7;
                    bVar17 = bVar17 >> 4 & 1;
                  }
                  if (bVar16 == bVar17) {
                    FUN_00522622(1);
                  }
                  if ((int)((uint)*(byte *)(*piVar4 + 0x7d) << 0x1b) < 0) {
                    FUN_00522fb4(local_2c8,local_2c4,*(float *)(*piVar4 + 0x2d8) * 0.5);
                  }
                  else {
                    FUN_00523284();
                  }
                  if (bVar16 == bVar17) {
                    FUN_00522622(0);
                  }
                }
                goto LAB_0051d794;
              }
              if (cVar2 == '\x01') {
                if (*(char *)(iVar5 + 0x2e4) == '\0') {
                  fVar24 = *(float *)(iVar5 + 0x158);
                  uVar12 = uVar10 | (uint)(fVar24 < 0.0) << 0x1f | (uint)(fVar24 == 0.0) << 0x1e;
                  uVar10 = uVar12 | (uint)NAN(fVar24) << 0x1c;
                  bVar16 = (byte)(uVar12 >> 0x18);
                  if (((bool)(bVar16 >> 6 & 1) || bVar16 >> 7 != ((byte)(uVar10 >> 0x1c) & 1)) ||
                     (*(int *)(iVar5 + 0x128) != 1)) {
                    local_264 = *(float *)(iVar5 + 0x164);
                    local_260 = *(float *)(iVar5 + 0x168);
                    local_25c = *(float *)(iVar5 + 0x16c);
                    local_258 = *(float *)(iVar5 + 0x170);
                    local_254 = *(float *)(iVar5 + 0x174);
                    local_250 = *(float *)(iVar5 + 0x178);
                    pfVar11 = (float *)(iVar5 + 400);
                    local_24c = *(float *)(iVar5 + 0x17c);
                    local_248 = *(float *)(iVar5 + 0x180);
                    uStack_244 = *(undefined4 *)(iVar5 + 0x184);
                    uStack_240 = *(undefined4 *)(iVar5 + 0x188);
                    uStack_23c = *(undefined4 *)(iVar5 + 0x18c);
                  }
                  else {
                    local_264 = *(float *)(iVar5 + 0x138);
                    local_260 = *(float *)(iVar5 + 0x13c);
                    local_25c = *(float *)(iVar5 + 0x140);
                    local_258 = *(float *)(iVar5 + 0x144);
                    local_254 = *(float *)(iVar5 + 0x148);
                    local_250 = *(float *)(iVar5 + 0x14c);
                    pfVar11 = (float *)(iVar5 + 400);
                    local_24c = *(float *)(iVar5 + 0x150);
                    local_248 = *(float *)(iVar5 + 0x154);
                    uStack_244 = *(undefined4 *)(iVar5 + 0x158);
                    uStack_240 = *(undefined4 *)(iVar5 + 0x15c);
                    uStack_23c = *(undefined4 *)(iVar5 + 0x160);
                  }
                }
                else {
                  local_264 = *(float *)(iVar5 + 0x334);
                  local_260 = *(float *)(iVar5 + 0x338);
                  local_25c = *(float *)(iVar5 + 0x33c);
                  local_258 = *(float *)(iVar5 + 0x340);
                  local_254 = *(float *)(iVar5 + 0x344);
                  local_250 = *(float *)(iVar5 + 0x348);
                  pfVar11 = (float *)(iVar5 + 0x308);
                  local_24c = *(float *)(iVar5 + 0x34c);
                  local_248 = *(float *)(iVar5 + 0x350);
                  uStack_244 = *(undefined4 *)(iVar5 + 0x354);
                  uStack_240 = *(undefined4 *)(iVar5 + 0x358);
                  uStack_23c = *(undefined4 *)(iVar5 + 0x35c);
                }
                local_290 = *pfVar11;
                local_28c = pfVar11[1];
                local_288 = pfVar11[2];
                local_284 = pfVar11[3];
                local_280 = pfVar11[4];
                local_27c = pfVar11[5];
                local_278 = pfVar11[6];
                local_274 = pfVar11[7];
                local_270 = pfVar11[8];
                local_26c = pfVar11[9];
                local_268 = pfVar11[10];
                iVar5 = FUN_005177a4(&local_290,&local_264,pfVar11 + 0xb);
                if ((((iVar5 != 1) || (iVar5 = FUN_005177a4(&local_288,&local_25c), iVar5 != 1)) ||
                    (iVar5 = FUN_005177a4(&local_280,&local_254), iVar5 != 1)) ||
                   (iVar5 = FUN_005177a4(&local_278,&local_24c), iVar5 != 1)) {
                  iVar5 = FUN_0051785c(&local_290,&local_25c);
                  if ((iVar5 != 0) || (iVar5 = FUN_0051785c(&local_264,&local_290), iVar5 != 0))
                  goto LAB_0051d9ae;
                  iVar5 = FUN_0051785c(&local_290,&local_254);
                  if ((iVar5 == 0) && (iVar5 = FUN_0051785c(&local_264,&local_278), iVar5 == 0)) {
                    uVar10 = uVar10 & 0xfffffff;
                    if (NAN(local_28c) || NAN(local_258)) {
                      if (local_250 < local_258) goto LAB_0051daba;
                    }
                    else if (local_250 >= local_258) goto LAB_0051daba;
LAB_0051d9ae:
                    local_29c = local_24c;
                    local_2a0 = local_248;
                    local_2a4 = local_280;
                    local_2a8 = local_27c;
                    fVar28 = local_25c;
                    fVar23 = local_258;
                    fVar26 = local_290;
                    fVar32 = local_28c;
                    fVar30 = local_278;
                    fVar33 = local_274;
                    fVar24 = local_254;
                    fVar29 = local_250;
                  }
                  else {
LAB_0051daba:
                    local_2a0 = local_260;
                    local_29c = local_264;
                    local_2a4 = local_288;
                    local_2a8 = local_284;
                    fVar28 = local_254;
                    fVar23 = local_250;
                    fVar26 = local_278;
                    fVar32 = local_274;
                    fVar30 = local_290;
                    fVar33 = local_28c;
                    fVar24 = local_25c;
                    fVar29 = local_258;
                  }
                  local_2b0 = *local_2cc;
                  local_2ac = local_2cc[1];
                  local_2c8 = *DAT_0051e7bc;
                  local_2c4 = (float *)DAT_0051e7bc[1];
                  iVar5 = FUN_00522f50(fVar24,fVar29,fVar28,fVar23,fVar30,fVar33,fVar26,fVar32,
                                       &local_2b0,&local_2ac);
                  iVar7 = FUN_00522f50(local_29c,local_2a0,fVar24,fVar29,fVar30,fVar33,local_2a4,
                                       local_2a8,&local_2c8,&local_2c4);
                  fVar28 = (float)FUN_00524218((local_2c8 - local_2b0) * (local_2c8 - local_2b0) +
                                               ((float)local_2c4 - local_2ac) *
                                               ((float)local_2c4 - local_2ac));
                  iVar6 = *piVar4;
                  fVar23 = *(float *)(iVar6 + 0x2dc) * *(float *)(iVar6 + 0x2d8);
                  uVar12 = uVar10 & 0xfffffff | (uint)(fVar23 < fVar28) << 0x1f;
                  uVar10 = uVar12 | (uint)(NAN(fVar23) || NAN(fVar28)) << 0x1c;
                  if ((((byte)(uVar12 >> 0x1f) == ((byte)(uVar10 >> 0x1c) & 1)) && (iVar7 != 0)) &&
                     (iVar5 != 0)) {
                    fVar22 = local_2b0;
                    fVar31 = local_2ac;
                    fVar27 = local_2c8;
                    pfVar25 = local_2c4;
                    if (-1 < (int)((uint)*(byte *)(iVar6 + 0x7d) << 0x1b)) {
                      uVar15 = FUN_0052266e(0,1,1,0);
                      fVar22 = local_2b0;
                      fVar31 = local_2ac;
                      fVar27 = local_2c8;
                      pfVar25 = local_2c4;
                    }
                  }
                  else {
                    fVar24 = local_298;
                    fVar29 = local_294;
                    fVar30 = fVar20;
                    fVar33 = fVar21;
                    if (-1 < (int)((uint)*(byte *)(iVar6 + 0x7d) << 0x1b)) {
                      uVar15 = FUN_0052266e(1,0,1,0);
                      fVar24 = local_298;
                      fVar29 = local_294;
                    }
                  }
                  FUN_00516b34(fVar22,fVar31,fVar24,fVar29,fVar27,pfVar25,fVar30,fVar33);
                  bVar16 = *(byte *)(*piVar4 + 0x7d);
                  goto joined_r0x0051d790;
                }
                goto LAB_0051d794;
              }
LAB_0051d8c6:
              *(undefined4 *)(iVar5 + 0x114) = 0;
              *(undefined4 *)(iVar5 + 0x118) = 0;
              FUN_0051565c(0x1000000);
              iVar5 = *piVar4;
              *(undefined4 *)(iVar5 + 0x114) = 0;
              *(undefined4 *)(iVar5 + 0x118) = 0;
              goto LAB_0051e538;
            }
LAB_0051d794:
            iVar5 = *piVar4;
            uVar10 = uVar10 & 0xfffffff;
            uVar12 = uVar10 | (uint)(*(float *)(iVar5 + 0x158) == 0.0) << 0x1e |
                     (uint)(0.0 <= *(float *)(iVar5 + 0x158)) << 0x1d;
            bVar16 = (byte)(uVar12 >> 0x18);
            if (((bool)(bVar16 >> 5 & 1) && !(bool)(bVar16 >> 6)) && (*(int *)(iVar5 + 0x128) == 1))
            {
              uVar12 = uVar10;
              if (DAT_0051d8a8 <=
                  ABS(*(float *)(iVar5 + 0x15c) * fVar39 - *(float *)(iVar5 + 0x160) * fVar40)) {
                uVar3 = *(undefined8 *)(iVar5 + 0x140);
                fVar31 = (float)uVar37;
                fVar27 = (float)((ulonglong)uVar37 >> 0x20);
                fVar22 = (float)uVar36;
                fVar21 = (float)((ulonglong)uVar36 >> 0x20);
                if (*(int *)(iVar5 + 0x110) != 0) {
                  cVar2 = *(char *)(iVar5 + 0x2e2);
                  uVar15 = 0;
                  pfVar25 = (float *)((ulonglong)*(undefined8 *)(iVar5 + 0x148) >> 0x20);
                  fVar24 = (float)((ulonglong)uVar3 >> 0x20);
                  fVar28 = (float)*(undefined8 *)(iVar5 + 0x148);
                  fVar20 = (float)uVar3;
                  if ((cVar2 == '\0') || (*(int *)(iVar5 + 0x118) != 0)) {
                    if (-1 < (int)((uint)*(byte *)(iVar5 + 0x7d) << 0x1b)) {
                      uVar15 = FUN_0052266e(1,0,1,0);
                    }
                    FUN_00516b34(fVar20,fVar24,fVar31,fVar27,fVar28,pfVar25,fVar22,fVar21);
                    bVar16 = *(byte *)(*piVar4 + 0x7d);
joined_r0x0051dbfc:
                    uVar12 = uVar10;
                    if (-1 < (int)((uint)bVar16 << 0x1b)) {
                      FUN_005226b2(uVar15);
                      uVar12 = uVar10;
                    }
                  }
                  else if (cVar2 == '\x02') {
                    local_2c8 = *DAT_0051e4a8;
                    local_2c4 = (float *)DAT_0051e4a8[1];
                    iVar5 = FUN_00522f50(fVar20,fVar24,fVar28,pfVar25,fVar31,fVar27,fVar22,fVar21,
                                         &local_2c8,&local_2c4);
                    uVar12 = uVar10;
                    if (iVar5 != 0) {
                      iVar5 = *piVar4;
                      fVar22 = (float)FUN_004397a8(*(float *)(iVar5 + 0xec) *
                                                   *(float *)(iVar5 + 0xec) +
                                                   *(float *)(iVar5 + 0xf0) *
                                                   *(float *)(iVar5 + 0xf0));
                      fVar21 = (float)FUN_004397a8(*(float *)(iVar5 + 0xf8) *
                                                   *(float *)(iVar5 + 0xf8) +
                                                   *(float *)(iVar5 + 0xfc) *
                                                   *(float *)(iVar5 + 0xfc));
                      uVar1 = uVar10 & 0xfffffff | (uint)(ABS(fVar22) < DAT_0051dd24) << 0x1f;
                      uVar12 = uVar1 | (uint)(NAN(ABS(fVar22)) || NAN(DAT_0051dd24)) << 0x1c;
                      bVar16 = (byte)(uVar1 >> 0x1f);
                      bVar17 = (byte)(uVar12 >> 0x1c) & 1;
                      if (bVar16 != bVar17) {
                        uVar12 = uVar10 & 0xfffffff | (uint)(ABS(fVar21) < DAT_0051dd24) << 0x1f |
                                 (uint)(NAN(ABS(fVar21)) || NAN(DAT_0051dd24)) << 0x1c;
                        bVar17 = (byte)(uVar12 >> 0x18);
                        bVar16 = bVar17 >> 7;
                        bVar17 = bVar17 >> 4 & 1;
                      }
                      if (bVar16 == bVar17) {
                        FUN_00522622(1);
                      }
                      if ((int)((uint)*(byte *)(*piVar4 + 0x7d) << 0x1b) < 0) {
                        FUN_00522fb4(local_2c8,local_2c4,*(float *)(*piVar4 + 0x2d8) * 0.5);
                      }
                      else {
                        FUN_00523284();
                      }
                      if (bVar16 == bVar17) {
                        FUN_00522622(0);
                      }
                    }
                  }
                  else {
                    if (cVar2 != '\x01') goto LAB_0051d8c6;
                    if (*(char *)(iVar5 + 0x2e4) == '\0') {
                      local_274 = *(float *)(iVar5 + 0x138);
                      local_270 = *(float *)(iVar5 + 0x13c);
                      local_26c = *(float *)(iVar5 + 0x140);
                      local_268 = *(float *)(iVar5 + 0x144);
                      local_264 = *(float *)(iVar5 + 0x148);
                      local_260 = *(float *)(iVar5 + 0x14c);
                      pfVar11 = (float *)(iVar5 + 400);
                      local_25c = *(float *)(iVar5 + 0x150);
                      local_258 = *(float *)(iVar5 + 0x154);
                      local_254 = *(float *)(iVar5 + 0x158);
                      local_250 = *(float *)(iVar5 + 0x15c);
                      local_24c = *(float *)(iVar5 + 0x160);
                    }
                    else {
                      local_274 = *(float *)(iVar5 + 0x334);
                      local_270 = *(float *)(iVar5 + 0x338);
                      local_26c = *(float *)(iVar5 + 0x33c);
                      local_268 = *(float *)(iVar5 + 0x340);
                      local_264 = *(float *)(iVar5 + 0x344);
                      local_260 = *(float *)(iVar5 + 0x348);
                      pfVar11 = (float *)(iVar5 + 0x308);
                      local_25c = *(float *)(iVar5 + 0x34c);
                      local_258 = *(float *)(iVar5 + 0x350);
                      local_254 = *(float *)(iVar5 + 0x354);
                      local_250 = *(float *)(iVar5 + 0x358);
                      local_24c = *(float *)(iVar5 + 0x35c);
                    }
                    local_2a0 = *pfVar11;
                    local_29c = pfVar11[1];
                    local_298 = pfVar11[2];
                    local_294 = pfVar11[3];
                    local_290 = pfVar11[4];
                    local_28c = pfVar11[5];
                    local_288 = pfVar11[6];
                    local_284 = pfVar11[7];
                    local_280 = pfVar11[8];
                    local_27c = pfVar11[9];
                    local_278 = pfVar11[10];
                    iVar5 = FUN_005177a4(&local_2a0,&local_274,pfVar11 + 0xb);
                    if ((((iVar5 != 1) || (iVar5 = FUN_005177a4(&local_298,&local_26c), iVar5 != 1))
                        || (iVar5 = FUN_005177a4(&local_290,&local_264), iVar5 != 1)) ||
                       (iVar5 = FUN_005177a4(&local_288,&local_25c), uVar12 = uVar10, iVar5 != 1)) {
                      iVar5 = FUN_0051785c(&local_2a0,&local_26c);
                      if ((iVar5 != 0) || (iVar5 = FUN_0051785c(&local_274,&local_2a0), iVar5 != 0))
                      goto LAB_0051ddda;
                      iVar5 = FUN_0051785c(&local_2a0,&local_264);
                      if ((iVar5 == 0) && (iVar5 = FUN_0051785c(&local_274,&local_288), iVar5 == 0))
                      {
                        uVar10 = uVar10 & 0xfffffff;
                        if (NAN(local_29c) || NAN(local_268)) {
                          if (local_260 < local_268) goto LAB_0051deec;
                        }
                        else if (local_260 >= local_268) goto LAB_0051deec;
LAB_0051ddda:
                        local_2a4 = local_25c;
                        local_2a8 = local_258;
                        fVar23 = local_26c;
                        fVar26 = local_268;
                        fVar32 = local_2a0;
                        fVar34 = local_29c;
                        fVar41 = local_28c;
                        fVar42 = local_290;
                        fVar33 = local_288;
                        fVar35 = local_284;
                        fVar29 = local_264;
                        fVar30 = local_260;
                      }
                      else {
LAB_0051deec:
                        local_2a8 = local_270;
                        local_2a4 = local_274;
                        fVar23 = local_264;
                        fVar26 = local_260;
                        fVar32 = local_288;
                        fVar34 = local_284;
                        fVar41 = local_294;
                        fVar42 = local_298;
                        fVar33 = local_2a0;
                        fVar35 = local_29c;
                        fVar29 = local_26c;
                        fVar30 = local_268;
                      }
                      local_2b0 = *local_2cc;
                      local_2ac = local_2cc[1];
                      local_2c8 = *DAT_0051e7bc;
                      local_2c4 = (float *)DAT_0051e7bc[1];
                      iVar5 = FUN_00522f50(fVar29,fVar30,fVar23,fVar26,fVar33,fVar35,fVar32,fVar34,
                                           &local_2b0,&local_2ac);
                      iVar7 = FUN_00522f50(local_2a4,local_2a8,fVar29,fVar30,fVar33,fVar35,fVar42,
                                           fVar41,&local_2c8,&local_2c4);
                      fVar23 = (float)FUN_00524218((local_2c8 - local_2b0) * (local_2c8 - local_2b0)
                                                   + ((float)local_2c4 - local_2ac) *
                                                     ((float)local_2c4 - local_2ac));
                      iVar6 = *piVar4;
                      fVar26 = *(float *)(iVar6 + 0x2dc) * *(float *)(iVar6 + 0x2d8);
                      uVar12 = uVar10 & 0xfffffff | (uint)(fVar26 < fVar23) << 0x1f;
                      uVar10 = uVar12 | (uint)(NAN(fVar26) || NAN(fVar23)) << 0x1c;
                      if ((((byte)(uVar12 >> 0x1f) == ((byte)(uVar10 >> 0x1c) & 1)) && (iVar7 != 0))
                         && (iVar5 != 0)) {
                        fVar20 = local_2b0;
                        fVar24 = local_2ac;
                        fVar28 = local_2c8;
                        pfVar25 = local_2c4;
                        if (-1 < (int)((uint)*(byte *)(iVar6 + 0x7d) << 0x1b)) {
                          uVar15 = FUN_0052266e(0,1,1,0);
                          fVar20 = local_2b0;
                          fVar24 = local_2ac;
                          fVar28 = local_2c8;
                          pfVar25 = local_2c4;
                        }
                      }
                      else {
                        fVar29 = fVar31;
                        fVar30 = fVar27;
                        fVar33 = fVar22;
                        fVar35 = fVar21;
                        if (-1 < (int)((uint)*(byte *)(iVar6 + 0x7d) << 0x1b)) {
                          uVar15 = FUN_0052266e(1,0,1,0);
                        }
                      }
                      FUN_00516b34(fVar20,fVar24,fVar29,fVar30,fVar28,pfVar25,fVar33,fVar35);
                      bVar16 = *(byte *)(*piVar4 + 0x7d);
                      goto joined_r0x0051dbfc;
                    }
                  }
                }
              }
              else {
                uVar37 = *(undefined8 *)(iVar5 + 0x140);
                uVar36 = *(undefined8 *)(iVar5 + 0x148);
              }
            }
            iVar5 = *piVar4;
            in_fpscr = uVar12 & 0xfffffff | (uint)(*(float *)(iVar5 + 0x158) == 0.0) << 0x1e;
            *(int *)(iVar5 + 0x128) = *(int *)(iVar5 + 0x128) + 1;
            uVar38 = (undefined4)((ulonglong)uVar37 >> 0x20);
            uVar15 = (undefined4)((ulonglong)uVar36 >> 0x20);
            if ((byte)(in_fpscr >> 0x1e) == 0) {
              *(int *)(iVar5 + 0x164) = (int)uVar37;
              *(undefined4 *)(iVar5 + 0x168) = uVar38;
              iVar5 = *piVar4;
              *(float *)(iVar5 + 0x16c) = local_2b8;
              *(float *)(iVar5 + 0x170) = local_2b4;
              iVar5 = *piVar4;
              *(float *)(iVar5 + 0x174) = local_2c0;
              *(float *)(iVar5 + 0x178) = local_2bc;
              iVar5 = *piVar4;
              *(int *)(iVar5 + 0x17c) = (int)uVar36;
              *(undefined4 *)(iVar5 + 0x180) = uVar15;
              iVar5 = *piVar4;
              *(float *)(iVar5 + 0x184) = local_2d0;
              *(float *)(iVar5 + 0x188) = fVar40;
              *(float *)(iVar5 + 0x18c) = fVar39;
            }
            else {
              *(int *)(iVar5 + 0x138) = (int)uVar37;
              *(undefined4 *)(iVar5 + 0x13c) = uVar38;
              iVar5 = *piVar4;
              *(float *)(iVar5 + 0x140) = local_2b8;
              *(float *)(iVar5 + 0x144) = local_2b4;
              iVar5 = *piVar4;
              *(float *)(iVar5 + 0x148) = local_2c0;
              *(float *)(iVar5 + 0x14c) = local_2bc;
              iVar5 = *piVar4;
              *(int *)(iVar5 + 0x150) = (int)uVar36;
              *(undefined4 *)(iVar5 + 0x154) = uVar15;
              iVar5 = *piVar4;
              *(float *)(iVar5 + 0x158) = local_2d0;
              *(float *)(iVar5 + 0x15c) = fVar40;
              *(float *)(iVar5 + 0x160) = fVar39;
            }
          }
          FUN_005226b2(uVar14);
        }
        else {
          iVar5 = *piVar4;
          *(float *)(iVar5 + 0x198) = local_22c;
          *(float *)(iVar5 + 0x19c) = local_228 + *(float *)(iVar5 + 0x130) * -0.5;
          *(float *)(iVar5 + 0x1a0) = local_22c;
          *(float *)(iVar5 + 0x1a4) = local_228 + *(float *)(iVar5 + 0x130) * 0.5;
          *(undefined4 *)(iVar5 + 400) = *(undefined4 *)(iVar5 + 0x198);
          *(undefined4 *)(iVar5 + 0x194) = *(undefined4 *)(iVar5 + 0x19c);
          iVar5 = *piVar4;
          *(undefined4 *)(iVar5 + 0x1a8) = *(undefined4 *)(iVar5 + 0x1a0);
          *(undefined4 *)(iVar5 + 0x1ac) = *(undefined4 *)(iVar5 + 0x1a4);
        }
      }
      goto LAB_0051d332;
    }
    uVar14 = 0;
    if ((int)((uint)*(byte *)(*piVar4 + 0x7d) << 0x1b) < 0) {
      uVar14 = FUN_0052266e(0,0,0,0);
    }
    iVar5 = *piVar4;
    uVar10 = in_fpscr & 0xfffffff | (uint)(*(float *)(iVar5 + 0x184) == 0.0) << 0x1e |
             (uint)(0.0 <= *(float *)(iVar5 + 0x184)) << 0x1d;
    bVar17 = (byte)(uVar10 >> 0x18);
    if ((bool)(bVar17 >> 5 & 1) && !(bool)(bVar17 >> 6)) {
      if (-1 < (int)((uint)*(byte *)(iVar5 + 0x7d) << 0x1b)) {
        uVar14 = FUN_0052266e(1,-(uint)(*(char *)(iVar5 + 0x1bf) == '\0') >> 0x1f,1,0);
      }
      iVar5 = *piVar4;
      local_2b0 = *(float *)(iVar5 + 0x164);
      local_2ac = *(float *)(iVar5 + 0x168);
      local_2b8 = *(float *)(iVar5 + 0x16c);
      local_2b4 = *(float *)(iVar5 + 0x170);
      local_2c0 = *(float *)(iVar5 + 0x174);
      local_2bc = *(float *)(iVar5 + 0x178);
      local_2c8 = *(float *)(iVar5 + 0x17c);
      local_2c4 = *(float **)(iVar5 + 0x180);
      FUN_00516b34(local_2b0,local_2ac,local_2b8,local_2b4,local_2c0,local_2bc,local_2c8,local_2c4);
      iVar5 = *piVar4;
      *(undefined4 *)(iVar5 + 0x184) = 0;
      if (-1 < (int)((uint)*(byte *)(iVar5 + 0x7d) << 0x1b)) {
        FUN_005226b2(uVar14);
      }
    }
    iVar5 = *piVar4;
    in_fpscr = uVar10 & 0xfffffff | (uint)(*(float *)(iVar5 + 0x158) == 0.0) << 0x1e |
               (uint)(0.0 <= *(float *)(iVar5 + 0x158)) << 0x1d;
    bVar17 = (byte)(in_fpscr >> 0x18);
    if (((bool)(bVar17 >> 5 & 1) && !(bool)(bVar17 >> 6)) && (-1 < (int)((uint)bVar16 << 0x18))) {
      if (-1 < (int)((uint)*(byte *)(iVar5 + 0x7d) << 0x1b)) {
        if (*(int *)(iVar5 + 0x128) == 1) {
          if (*(char *)(iVar5 + 0x1bf) == '\0') {
            uVar12 = 1;
            uVar10 = 1;
          }
          else {
            uVar12 = -(uint)(*(char *)(iVar5 + 0x2e0) == '\0') >> 0x1f;
            uVar10 = -(uint)(*(char *)(iVar5 + 0x2e1) == '\0') >> 0x1f;
          }
        }
        else {
          uVar12 = -(uint)(*(char *)(iVar5 + 0x1bf) == '\0') >> 0x1f;
          uVar10 = 0;
        }
        uVar14 = FUN_0052266e(1,uVar10,1,uVar12);
      }
      iVar5 = *piVar4;
      local_2b0 = *(float *)(iVar5 + 0x138);
      local_2ac = *(float *)(iVar5 + 0x13c);
      local_2b8 = *(float *)(iVar5 + 0x140);
      local_2b4 = *(float *)(iVar5 + 0x144);
      local_2c0 = *(float *)(iVar5 + 0x148);
      local_2bc = *(float *)(iVar5 + 0x14c);
      local_2c8 = *(float *)(iVar5 + 0x150);
      local_2c4 = *(float **)(iVar5 + 0x154);
      FUN_00516b34(local_2b0,local_2ac,local_2b8,local_2b4,local_2c0,local_2bc,local_2c8,local_2c4);
      iVar5 = *piVar4;
      *(undefined4 *)(iVar5 + 0x158) = 0;
      if (-1 < (int)((uint)*(byte *)(iVar5 + 0x7d) << 0x1b)) {
        FUN_005226b2(uVar14);
      }
    }
    iVar5 = *piVar4;
    if (*(int *)(iVar5 + 0x128) == 2) {
      local_2b0 = *(float *)(iVar5 + 0x140);
      local_2ac = *(float *)(iVar5 + 0x144);
      local_2b8 = *(float *)(iVar5 + 0x164);
      local_2b4 = *(float *)(iVar5 + 0x168);
      local_2c0 = *(float *)(iVar5 + 0x148);
      local_2bc = *(float *)(iVar5 + 0x14c);
      local_2c8 = *(float *)(iVar5 + 0x17c);
      local_2c4 = *(float **)(iVar5 + 0x180);
      local_2d0 = 0.0;
      iVar5 = FUN_005179d0(&local_2b0,&local_2b8,&local_2c0,&local_2c8);
      if (iVar5 != 0) {
        iVar7 = *piVar4;
        *(undefined4 *)(iVar7 + 0x114) = 0;
        *(undefined4 *)(iVar7 + 0x118) = 0;
        FUN_0051565c(iVar5);
        goto LAB_0051e0fc;
      }
    }
    FUN_005226b2(uVar14);
    *(undefined4 *)(*piVar4 + 0x128) = 0;
    if ((local_237 != '\0' && uVar13 != 1) &&
       ((iVar5 = FUN_0051b8f0(), iVar5 != 0 || (iVar5 = FUN_0051bf7c(), iVar5 != 0)))) {
      iVar7 = *piVar4;
      *(undefined4 *)(iVar7 + 0x114) = 0;
      *(undefined4 *)(iVar7 + 0x118) = 0;
      FUN_0051565c(iVar5);
LAB_0051e0fc:
      iVar7 = *piVar4;
      *(undefined4 *)(iVar7 + 0x114) = 0;
      *(undefined4 *)(iVar7 + 0x118) = 0;
      FUN_0051565c(iVar5);
      return iVar5;
    }
  } while( true );
}

