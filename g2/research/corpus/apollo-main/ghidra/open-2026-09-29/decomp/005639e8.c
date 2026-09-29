
int FUN_005639e8(float param_1,float param_2,float param_3,float param_4)

{
  char cVar1;
  undefined8 uVar2;
  undefined8 uVar3;
  undefined8 uVar4;
  undefined8 uVar5;
  float fVar6;
  int *piVar7;
  undefined4 uVar8;
  int iVar9;
  int iVar10;
  int iVar11;
  uint uVar12;
  undefined4 uVar13;
  uint uVar14;
  uint uVar15;
  uint uVar16;
  uint uVar17;
  undefined4 uVar18;
  undefined4 uVar19;
  undefined4 uVar20;
  undefined4 uVar21;
  byte bVar22;
  bool bVar23;
  uint in_fpscr;
  float fVar24;
  float fVar25;
  float fVar26;
  float fVar27;
  float fVar28;
  float fVar29;
  undefined4 local_8c;
  undefined4 uStack_88;
  undefined4 local_84;
  undefined4 uStack_80;
  undefined4 local_7c;
  undefined4 uStack_78;
  undefined4 local_74;
  undefined4 uStack_70;
  
  iVar10 = *DAT_00563f3c;
  param_3 = param_3 - param_1;
  param_4 = param_4 - param_2;
  fVar24 = (float)FUN_00524218(param_3 * param_3 + param_4 * param_4);
  fVar6 = DAT_00563adc;
  fVar24 = (float)VectorSignedToFloat((int)(fVar24 + 0.5),(byte)(in_fpscr >> 0x16) & 3);
  param_4 = param_4 / fVar24;
  param_3 = param_3 / fVar24;
  do {
    fVar25 = DAT_00563ae0;
    uVar16 = in_fpscr & 0xfffffff;
    uVar17 = uVar16 | (uint)(fVar24 == 0.0) << 0x1e;
    if ((byte)(uVar17 >> 0x1e) != 0) {
      return 0;
    }
    if (*(int *)(iVar10 + 0x2f8) == 0) {
      uVar17 = 1;
      fVar29 = *(float *)(*(int *)(iVar10 + 0x2ec) + *(int *)(iVar10 + 0x2fc) * 4);
    }
    else {
      fVar29 = (float)VectorUnsignedToFloat(*(int *)(iVar10 + 0x2f8),(byte)(uVar17 >> 0x16) & 3);
      uVar17 = -(uint)(*(char *)(iVar10 + 0x2e8) == '\0') >> 0x1f;
    }
    if (0.0 <= fVar24 - fVar29) {
      uVar15 = 1;
      uVar12 = *(int *)(iVar10 + 0x2fc) + 1;
      if (uVar12 < *(uint *)(iVar10 + 0x2f0)) {
        *(uint *)(iVar10 + 0x2fc) = uVar12;
      }
      else {
        *(undefined4 *)(iVar10 + 0x2fc) = 0;
      }
    }
    else {
      fVar25 = (float)((uint)(0.0 < fVar29 - fVar24) * (int)(fVar29 - fVar24));
      uVar15 = 0;
      fVar29 = fVar24;
    }
    *(float *)(iVar10 + 0x2f8) = fVar25;
    fVar26 = *(float *)(iVar10 + 0x304);
    uVar12 = uVar16 | (uint)(fVar26 < 0.0) << 0x1f;
    in_fpscr = uVar12 | (uint)NAN(fVar26) << 0x1c;
    fVar25 = DAT_00563aec;
    fVar27 = fVar29;
    if ((byte)(uVar12 >> 0x1f) == ((byte)(in_fpscr >> 0x1c) & 1)) {
      fVar27 = fVar29 - fVar26;
      uVar16 = uVar16 | (uint)(fVar27 < 0.0) << 0x1f | (uint)(fVar27 == 0.0) << 0x1e;
      in_fpscr = uVar16 | (uint)NAN(fVar27) << 0x1c;
      bVar22 = (byte)(uVar16 >> 0x18);
      if ((bool)(bVar22 >> 6 & 1) || bVar22 >> 7 != ((byte)(in_fpscr >> 0x1c) & 1)) {
        fVar25 = fVar26 - fVar29;
        fVar27 = DAT_00563ae0;
      }
    }
    *(float *)(iVar10 + 0x304) = fVar25;
    piVar7 = DAT_00563f3c;
    iVar11 = *DAT_00563f3c;
    fVar24 = fVar24 - fVar27;
    fVar29 = param_1 + param_3 * fVar27;
    fVar26 = param_2 + param_4 * fVar27;
    bVar23 = *(char *)(iVar11 + 0x1c1) != '\0';
    cVar1 = '\0';
    if (bVar23) {
      cVar1 = *(char *)(iVar10 + 0x2e9);
    }
    if (((bVar23 && cVar1 != '\0') &&
        (in_fpscr = in_fpscr & 0xfffffff | (uint)(fVar24 == 0.0) << 0x1e,
        (byte)(in_fpscr >> 0x1e) != 0)) && (uVar15 != 0)) {
      uVar15 = 0;
    }
    bVar22 = 0;
    if (*(char *)(iVar10 + 0x2e5) == '\x01') {
      in_fpscr = in_fpscr & 0xfffffff | (uint)(fVar25 == 0.0) << 0x1e;
      bVar22 = (byte)(in_fpscr >> 0x1e);
    }
    if (bVar22 != 0) {
      if (((*(char *)(iVar10 + 0x2e8) == '\0') && (*(char *)(iVar10 + 0x2eb) == '\0')) ||
         (*(char *)(iVar10 + 0x2ea) == '\0')) {
        uVar16 = 0;
      }
      else {
        uVar16 = (uint)(*(char *)(iVar10 + 0x2e6) == '\x01') & (uVar17 ^ 1);
      }
      if ((int)((uint)*(byte *)(iVar11 + 0x7d) << 0x1b) < 0) {
        uVar14 = 0;
        uVar13 = 0;
        uVar12 = 0;
        uVar8 = 0;
      }
      else {
        uVar14 = -(uint)(*(char *)(iVar11 + 0x2e0) == '\0') >> 0x1f;
        uVar12 = -(uint)(*(char *)(iVar11 + 0x2e1) == '\0') >> 0x1f;
        if ((uVar17 & uVar15) == 0) {
          if (uVar15 == 1 && uVar17 == 0) {
            uVar14 = 0;
          }
          else if (uVar17 == 1 && uVar15 == 0) {
            uVar12 = 0;
          }
          else {
            uVar14 = 0;
            uVar12 = 0;
          }
        }
        uVar13 = 1;
        uVar8 = 1;
      }
      uVar8 = FUN_0052266e(uVar8,uVar12,uVar13,uVar14);
      in_fpscr = in_fpscr & 0xfffffff | (uint)(fVar27 == 0.0) << 0x1e;
      if ((byte)(in_fpscr >> 0x1e) == 0) {
        iVar11 = *piVar7;
        if (*(int *)(iVar11 + 0x110) == 0) {
          FUN_00516bde(param_1,param_2,fVar29,fVar26,1,*(undefined4 *)(iVar11 + 0x88));
        }
        else {
          fVar28 = fVar29 - param_1;
          fVar27 = fVar26 - param_2;
          fVar25 = (float)FUN_004397a8(fVar28 * fVar28 + fVar27 * fVar27);
          fVar27 = *(float *)(iVar11 + 0x130) * 0.5 * fVar27 * (1.0 / fVar25);
          fVar25 = *(float *)(iVar11 + 0x134) * 0.5 * fVar28 * (1.0 / fVar25);
          *(float *)(iVar11 + 0x308) = param_1 - fVar27;
          *(float *)(iVar11 + 0x30c) = fVar25 + param_2;
          *(float *)(iVar11 + 0x310) = fVar29 - fVar27;
          *(float *)(iVar11 + 0x314) = fVar25 + fVar26;
          *(float *)(iVar11 + 0x318) = fVar27 + fVar29;
          *(float *)(iVar11 + 0x31c) = fVar26 - fVar25;
          *(float *)(iVar11 + 800) = fVar27 + param_1;
          *(float *)(iVar11 + 0x324) = param_2 - fVar25;
          FUN_00516b34(*(undefined4 *)(iVar11 + 0x308),*(undefined4 *)(iVar11 + 0x30c),
                       *(undefined4 *)(iVar11 + 0x310),*(undefined4 *)(iVar11 + 0x314),
                       *(undefined4 *)(iVar11 + 0x318),*(undefined4 *)(iVar11 + 0x31c),
                       *(undefined4 *)(iVar11 + 800),*(undefined4 *)(iVar11 + 0x324));
          iVar9 = *piVar7;
          uVar13 = *(undefined4 *)(iVar11 + 0x30c);
          uVar18 = *(undefined4 *)(iVar11 + 0x310);
          uVar19 = *(undefined4 *)(iVar11 + 0x314);
          uVar21 = *(undefined4 *)(iVar11 + 0x318);
          *(undefined4 *)(iVar9 + 400) = *(undefined4 *)(iVar11 + 0x308);
          *(undefined4 *)(iVar9 + 0x194) = uVar13;
          *(undefined4 *)(iVar9 + 0x198) = uVar18;
          *(undefined4 *)(iVar9 + 0x19c) = uVar19;
          *(undefined4 *)(iVar9 + 0x1a0) = uVar21;
          uVar13 = *(undefined4 *)(iVar11 + 800);
          uVar18 = *(undefined4 *)(iVar11 + 0x324);
          uVar19 = *(undefined4 *)(iVar11 + 0x328);
          uVar21 = *(undefined4 *)(iVar11 + 0x32c);
          *(undefined4 *)(iVar9 + 0x1a4) = *(undefined4 *)(iVar11 + 0x31c);
          *(undefined4 *)(iVar9 + 0x1a8) = uVar13;
          *(undefined4 *)(iVar9 + 0x1ac) = uVar18;
          *(undefined4 *)(iVar9 + 0x1b0) = uVar19;
          *(undefined4 *)(iVar9 + 0x1b4) = uVar21;
          *(undefined4 *)(iVar9 + 0x1b8) = *(undefined4 *)(iVar11 + 0x330);
          iVar9 = *piVar7;
          uVar13 = *(undefined4 *)(iVar11 + 0x30c);
          uVar18 = *(undefined4 *)(iVar11 + 0x310);
          uVar19 = *(undefined4 *)(iVar11 + 0x314);
          uVar21 = *(undefined4 *)(iVar11 + 0x318);
          uVar20 = *(undefined4 *)(iVar11 + 0x31c);
          *(undefined4 *)(iVar9 + 0x138) = *(undefined4 *)(iVar11 + 0x308);
          *(undefined4 *)(iVar9 + 0x13c) = uVar13;
          *(undefined4 *)(iVar9 + 0x140) = uVar18;
          *(undefined4 *)(iVar9 + 0x144) = uVar19;
          *(undefined4 *)(iVar9 + 0x148) = uVar21;
          *(undefined4 *)(iVar9 + 0x14c) = uVar20;
          uVar13 = *(undefined4 *)(iVar11 + 0x324);
          uVar18 = *(undefined4 *)(iVar11 + 0x328);
          uVar19 = *(undefined4 *)(iVar11 + 0x32c);
          uVar21 = *(undefined4 *)(iVar11 + 0x330);
          *(undefined4 *)(iVar9 + 0x150) = *(undefined4 *)(iVar11 + 800);
          *(undefined4 *)(iVar9 + 0x154) = uVar13;
          *(undefined4 *)(iVar9 + 0x158) = uVar18;
          *(undefined4 *)(iVar9 + 0x15c) = uVar19;
          *(undefined4 *)(iVar9 + 0x160) = uVar21;
          if (uVar16 != 0) {
            iVar11 = *piVar7;
            fVar25 = ABS(*(float *)(iVar11 + 0x358) * *(float *)(iVar11 + 0x330) -
                         *(float *)(iVar11 + 0x35c) * *(float *)(iVar11 + 0x32c));
            uVar16 = in_fpscr & 0xfffffff | (uint)(fVar25 < fVar6) << 0x1f;
            in_fpscr = uVar16 | (uint)(NAN(fVar25) || NAN(fVar6)) << 0x1c;
            if ((byte)(uVar16 >> 0x1f) != ((byte)(in_fpscr >> 0x1c) & 1)) {
              uVar2 = *(undefined8 *)(iVar11 + 0x33c);
              uVar3 = *(undefined8 *)(iVar11 + 0x308);
              uVar4 = *(undefined8 *)(iVar11 + 0x344);
              uVar5 = *(undefined8 *)(iVar11 + 800);
              bVar23 = -1 < (int)((uint)*(byte *)(iVar11 + 0x7d) << 0x1b);
              uVar13 = FUN_0052266e(bVar23,0,bVar23,0);
              FUN_00516b34((int)uVar2,(int)((ulonglong)uVar2 >> 0x20),(int)uVar3,
                           (int)((ulonglong)uVar3 >> 0x20),(int)uVar4,
                           (int)((ulonglong)uVar4 >> 0x20),(int)uVar5,
                           (int)((ulonglong)uVar5 >> 0x20));
              FUN_005226b2(uVar13);
            }
          }
        }
      }
      else {
        *(float *)(iVar10 + 0x310) = param_1;
        iVar11 = *piVar7;
        *(float *)(iVar10 + 0x314) = param_2 + *(float *)(iVar11 + 0x130) * -0.5;
        *(float *)(iVar10 + 0x318) = param_1;
        *(float *)(iVar10 + 0x31c) = param_2 + *(float *)(iVar11 + 0x130) * 0.5;
        *(undefined4 *)(iVar10 + 0x308) = *(undefined4 *)(iVar10 + 0x310);
        *(undefined4 *)(iVar10 + 0x30c) = *(undefined4 *)(iVar10 + 0x314);
        *(undefined4 *)(iVar10 + 800) = *(undefined4 *)(iVar10 + 0x318);
        *(undefined4 *)(iVar10 + 0x324) = *(undefined4 *)(iVar10 + 0x31c);
      }
      FUN_005226b2(uVar8);
      iVar11 = *piVar7;
      uVar8 = *(undefined4 *)(iVar10 + 0x30c);
      uVar13 = *(undefined4 *)(iVar10 + 0x310);
      uVar18 = *(undefined4 *)(iVar10 + 0x314);
      uVar19 = *(undefined4 *)(iVar10 + 0x318);
      uVar21 = *(undefined4 *)(iVar10 + 0x31c);
      *(undefined4 *)(iVar11 + 0x164) = *(undefined4 *)(iVar10 + 0x308);
      *(undefined4 *)(iVar11 + 0x168) = uVar8;
      *(undefined4 *)(iVar11 + 0x16c) = uVar13;
      *(undefined4 *)(iVar11 + 0x170) = uVar18;
      *(undefined4 *)(iVar11 + 0x174) = uVar19;
      *(undefined4 *)(iVar11 + 0x178) = uVar21;
      uVar8 = *(undefined4 *)(iVar10 + 0x324);
      uVar13 = *(undefined4 *)(iVar10 + 0x328);
      uVar18 = *(undefined4 *)(iVar10 + 0x32c);
      uVar19 = *(undefined4 *)(iVar10 + 0x330);
      *(undefined4 *)(iVar11 + 0x17c) = *(undefined4 *)(iVar10 + 800);
      *(undefined4 *)(iVar11 + 0x180) = uVar8;
      *(undefined4 *)(iVar11 + 0x184) = uVar13;
      *(undefined4 *)(iVar11 + 0x188) = uVar18;
      *(undefined4 *)(iVar11 + 0x18c) = uVar19;
      iVar11 = *piVar7;
      uVar8 = *(undefined4 *)(iVar10 + 0x30c);
      uVar13 = *(undefined4 *)(iVar10 + 0x310);
      uVar18 = *(undefined4 *)(iVar10 + 0x314);
      uVar19 = *(undefined4 *)(iVar10 + 0x318);
      uVar21 = *(undefined4 *)(iVar10 + 0x31c);
      *(undefined4 *)(iVar11 + 400) = *(undefined4 *)(iVar10 + 0x308);
      *(undefined4 *)(iVar11 + 0x194) = uVar8;
      *(undefined4 *)(iVar11 + 0x198) = uVar13;
      *(undefined4 *)(iVar11 + 0x19c) = uVar18;
      *(undefined4 *)(iVar11 + 0x1a0) = uVar19;
      *(undefined4 *)(iVar11 + 0x1a4) = uVar21;
      uVar8 = *(undefined4 *)(iVar10 + 0x324);
      uVar13 = *(undefined4 *)(iVar10 + 0x328);
      uVar18 = *(undefined4 *)(iVar10 + 0x32c);
      uVar19 = *(undefined4 *)(iVar10 + 0x330);
      *(undefined4 *)(iVar11 + 0x1a8) = *(undefined4 *)(iVar10 + 800);
      *(undefined4 *)(iVar11 + 0x1ac) = uVar8;
      *(undefined4 *)(iVar11 + 0x1b0) = uVar13;
      *(undefined4 *)(iVar11 + 0x1b4) = uVar18;
      *(undefined4 *)(iVar11 + 0x1b8) = uVar19;
      if ((uVar17 & uVar15) == 0) {
        if (uVar15 == 1 && uVar17 == 0) {
          local_74 = *(undefined4 *)(iVar10 + 0x33c);
          uStack_70 = *(undefined4 *)(iVar10 + 0x340);
          local_7c = *(undefined4 *)(iVar10 + 0x308);
          uStack_78 = *(undefined4 *)(iVar10 + 0x30c);
          local_84 = *(undefined4 *)(iVar10 + 0x344);
          uStack_80 = *(undefined4 *)(iVar10 + 0x348);
          local_8c = *(undefined4 *)(iVar10 + 800);
          uStack_88 = *(undefined4 *)(iVar10 + 0x324);
          if ((*(char *)(iVar10 + 0x2ea) == '\0') &&
             (iVar11 = FUN_005179d0(&local_74,&local_7c,&local_84,&local_8c,0), iVar11 != 0))
          goto LAB_00563ea2;
          iVar11 = FUN_0051bf7c();
          goto joined_r0x00563f0e;
        }
        if ((uVar17 == 1 && uVar15 == 0) && (*(char *)(iVar10 + 0x2e8) != '\0')) {
          iVar11 = FUN_0051b8f0();
          goto joined_r0x00563f0e;
        }
      }
      else {
        if (*(char *)(iVar10 + 0x2e8) == '\0') {
          iVar11 = FUN_0051bf7c(0,iVar10 + 0x334);
        }
        else {
          iVar11 = FUN_0051c5ec();
        }
joined_r0x00563f0e:
        if (iVar11 != 0) {
LAB_00563ea2:
          FUN_0051778c(0);
          FUN_00517796(0);
          FUN_0051565c(iVar11);
          return iVar11;
        }
      }
      *(undefined4 *)(iVar10 + 0x334) = *(undefined4 *)(iVar10 + 0x308);
      *(undefined4 *)(iVar10 + 0x338) = *(undefined4 *)(iVar10 + 0x30c);
      *(undefined4 *)(iVar10 + 0x33c) = *(undefined4 *)(iVar10 + 0x310);
      *(undefined4 *)(iVar10 + 0x340) = *(undefined4 *)(iVar10 + 0x314);
      *(undefined4 *)(iVar10 + 0x344) = *(undefined4 *)(iVar10 + 0x318);
      *(undefined4 *)(iVar10 + 0x348) = *(undefined4 *)(iVar10 + 0x31c);
      *(undefined4 *)(iVar10 + 0x34c) = *(undefined4 *)(iVar10 + 800);
      *(undefined4 *)(iVar10 + 0x350) = *(undefined4 *)(iVar10 + 0x324);
      *(undefined4 *)(iVar10 + 0x354) = *(undefined4 *)(iVar10 + 0x328);
      *(undefined4 *)(iVar10 + 0x358) = *(undefined4 *)(iVar10 + 0x32c);
      *(undefined4 *)(iVar10 + 0x35c) = *(undefined4 *)(iVar10 + 0x330);
      if (*(char *)(iVar10 + 0x2e8) == '\0') {
        *(undefined4 *)(iVar10 + 0x360) = *(undefined4 *)(iVar10 + 0x308);
        *(undefined4 *)(iVar10 + 0x364) = *(undefined4 *)(iVar10 + 0x30c);
        *(undefined4 *)(iVar10 + 0x368) = *(undefined4 *)(iVar10 + 0x310);
        *(undefined4 *)(iVar10 + 0x36c) = *(undefined4 *)(iVar10 + 0x314);
        *(undefined4 *)(iVar10 + 0x370) = *(undefined4 *)(iVar10 + 0x318);
        *(undefined4 *)(iVar10 + 0x374) = *(undefined4 *)(iVar10 + 0x31c);
        *(undefined4 *)(iVar10 + 0x378) = *(undefined4 *)(iVar10 + 800);
        *(undefined4 *)(iVar10 + 0x37c) = *(undefined4 *)(iVar10 + 0x324);
        *(undefined4 *)(iVar10 + 0x380) = *(undefined4 *)(iVar10 + 0x328);
        *(undefined4 *)(iVar10 + 900) = *(undefined4 *)(iVar10 + 0x32c);
        *(undefined4 *)(iVar10 + 0x388) = *(undefined4 *)(iVar10 + 0x330);
        *(undefined1 *)(iVar10 + 0x2e8) = 1;
      }
    }
    *(byte *)(iVar10 + 0x2e6) = *(byte *)(iVar10 + 0x2e5);
    param_2 = fVar26;
    param_1 = fVar29;
    if (*(int *)(iVar10 + 0x2f8) == 0) {
      *(byte *)(iVar10 + 0x2e5) = *(byte *)(iVar10 + 0x2e5) ^ 1;
    }
  } while( true );
}

