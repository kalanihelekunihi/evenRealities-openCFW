
/* WARNING: Type propagation algorithm not settling */

float FUN_005202ec(int *param_1,int param_2)

{
  char cVar1;
  char cVar2;
  int *piVar3;
  uint *puVar4;
  int *piVar5;
  undefined1 uVar6;
  int iVar7;
  uint uVar8;
  undefined4 *puVar9;
  float *pfVar10;
  float *pfVar11;
  uint uVar12;
  uint uVar13;
  undefined4 uVar14;
  int iVar15;
  undefined4 uVar16;
  float fVar17;
  float *pfVar18;
  uint uVar19;
  float *pfVar20;
  int iVar21;
  float *pfVar22;
  byte bVar23;
  bool bVar24;
  byte bVar25;
  bool bVar26;
  uint in_fpscr;
  uint uVar27;
  float fVar28;
  float fVar29;
  float fVar30;
  float fVar31;
  float fVar32;
  float fVar33;
  float fVar34;
  float fVar35;
  float fVar36;
  float fVar37;
  float fVar38;
  float fVar39;
  float fVar40;
  float fVar41;
  float fVar42;
  float local_d0 [8];
  uint local_b0;
  uint local_ac;
  float local_a8;
  int local_a4;
  float local_a0;
  undefined4 local_9c;
  uint local_98;
  undefined4 uStack_94;
  undefined4 uStack_90;
  undefined4 uStack_8c;
  undefined4 local_88;
  undefined4 uStack_84;
  undefined4 uStack_80;
  undefined4 uStack_7c;
  uint local_78;
  undefined4 uStack_74;
  undefined4 local_70;
  undefined4 uStack_6c;
  
  pfVar11 = local_d0;
  fVar17 = 0.0;
  iVar7 = FUN_005144fa();
  piVar5 = DAT_00520c78;
  puVar4 = DAT_00520c74;
  piVar3 = DAT_00520c70;
  if (iVar7 == 0) {
    fVar17 = 8.96831e-44;
  }
  if ((param_1 == (int *)0x0 || param_2 == 0) || (iVar7 = *DAT_00520c70, iVar7 == 0)) {
    fVar17 = (float)((uint)fVar17 | 1);
  }
  if (param_1[1] != 0) {
    iVar7 = *param_1;
  }
  if (param_1[1] == 0 || iVar7 == 0) {
    fVar17 = (float)((uint)fVar17 | 0x10);
  }
  fVar28 = (float)param_1[0x14];
  bVar26 = 0.0 <= fVar28;
  in_fpscr = in_fpscr & 0xfffffff;
  if (bVar26) {
    fVar28 = (float)param_1[0x15];
  }
  if (!bVar26 || (!bVar26 || fVar28 < 0.0)) {
    fVar17 = (float)((uint)fVar17 | 0x400);
  }
  uVar27 = in_fpscr | (uint)((float)param_1[6] < DAT_005205e4) << 0x1f;
  if ((((SUB41(uVar27 >> 0x1f,0) == (NAN((float)param_1[6]) || NAN(DAT_005205e4))) ||
       (uVar27 = in_fpscr, (float)param_1[4] < DAT_005205e8)) ||
      (uVar27 = in_fpscr | (uint)((float)param_1[7] < DAT_005205e4) << 0x1f,
      SUB41(uVar27 >> 0x1f,0) == (NAN((float)param_1[7]) || NAN(DAT_005205e4)))) ||
     (uVar27 = in_fpscr, (float)param_1[5] < DAT_005205e8)) {
    fVar17 = (float)((uint)fVar17 | 0x4000);
  }
  if ((*(char *)(*DAT_00520c70 + 0x7c) == '\0') &&
     (fVar28 = *(float *)(*DAT_00520c70 + 0x2d8),
     uVar27 = uVar27 & 0xfffffff | (uint)(fVar28 == 0.0) << 0x1e | (uint)(0.0 <= fVar28) << 0x1d,
     bVar23 = (byte)(uVar27 >> 0x18), !(bool)(bVar23 >> 5 & 1) || (bool)(bVar23 >> 6))) {
    fVar17 = (float)((uint)fVar17 | 0x200000);
  }
  uVar27 = uVar27 & 0xfffffff;
  if (*(float *)(param_2 + 0xd0) < 0.0) {
    fVar17 = (float)((uint)fVar17 | 0x400000);
  }
  uVar8 = *DAT_00520c74;
  uVar12 = *(uint *)(uVar8 + 0x10);
  iVar15 = *(int *)(*DAT_00520c78 + 0x3c);
  bVar26 = SBORROW4(uVar12,iVar15);
  iVar7 = uVar12 - iVar15;
  if (iVar15 <= (int)uVar12) {
    uVar8 = *(uint *)(uVar8 + 0x14);
    iVar7 = *(int *)(*DAT_00520c78 + 0x40);
    bVar26 = SBORROW4(uVar8,iVar7);
    iVar7 = uVar8 - iVar7;
  }
  if ((iVar7 < 0 != bVar26) || ((uVar12 & 3) != 0 || (uVar8 & 3) != 0)) {
    fVar17 = (float)((uint)fVar17 | 0x2000000);
  }
  FUN_0051565c(fVar17);
  iVar7 = *piVar3;
  if (fVar17 != 0.0) {
    *(undefined4 *)(iVar7 + 0x114) = 0;
    *(undefined4 *)(iVar7 + 0x118) = 0;
    goto LAB_00520d64;
  }
  uVar8 = *(int *)(iVar7 + 0x84) << 1;
  if ((int)uVar8 < 0) {
    uVar12 = (uint)*(byte *)(param_2 + 0xd5);
    bVar26 = uVar12 == 0;
    if (bVar26) {
      uVar12 = *(uint *)(*piVar5 + 0xfc);
      uVar8 = *(uint *)(param_2 + 0xd8);
    }
    if (bVar26 && uVar12 == uVar8) {
      return 0.0;
    }
  }
  bVar23 = *(byte *)(param_1 + 0x21);
  bVar25 = *(byte *)(iVar7 + 0x90);
  *(byte *)(iVar7 + 0x1bc) = bVar25 & 1 | bVar23 & 1;
  *(undefined1 *)(*piVar3 + 0x1be) = *(undefined1 *)(*piVar3 + 0x1bc);
  if ((bVar25 & 1) == 0) {
    if ((bVar23 & 1) == 0) {
      FUN_00561810(*piVar3 + 0xec);
    }
    else {
      FUN_00561830(*piVar3 + 0xec,param_1 + 0x18);
    }
  }
  else {
    FUN_00561830(*piVar3 + 0xec,*piVar3 + 0xa4);
    if ((bVar23 & 1) != 0) {
      FUN_005619f2(*piVar3 + 0xec,param_1 + 0x18);
    }
  }
  if (*(char *)(*piVar3 + 0x7e) != '\0') {
    *(undefined1 *)(*piVar3 + 0x1bc) = 0;
  }
  uVar8 = *(uint *)(param_2 + 0xd8);
  iVar7 = *piVar3;
  *(uint *)(iVar7 + 0x124) = uVar8;
  fVar17 = *(float *)(param_2 + 0xd0);
  uVar27 = uVar27 & 0xfffffff;
  if (fVar17 < 1.0) {
    uVar27 = uVar27 | (uint)(fVar17 == 0.0) << 0x1e | (uint)(0.0 <= fVar17) << 0x1d;
    bVar23 = (byte)(uVar27 >> 0x18);
    if (!(bool)(bVar23 >> 5 & 1) || (bool)(bVar23 >> 6)) {
      FUN_0051565c(0x400000);
      return 5.877472e-39;
    }
    fVar28 = (float)VectorSignedToFloat(uVar8 >> 0x18,(byte)(uVar27 >> 0x16) & 3);
    *(uint *)(iVar7 + 0x124) = uVar8 & 0xffffff | (int)(fVar28 * fVar17 + 0.5) << 0x18;
  }
  uVar8 = *(int *)(iVar7 + 0x84) << 5;
  if ((int)uVar8 < 0) {
    uVar12 = *(uint *)(iVar7 + 0x124);
    uVar8 = uVar12 >> 0x18;
    bVar23 = (byte)(uVar12 >> 0x18);
    *(uint *)(iVar7 + 0x124) =
         ((uint)((ulonglong)(uint)((int)(short)(ushort)bVar23 * (int)(short)((ushort)uVar12 & 0xff))
                 * (ulonglong)DAT_00520c7c >> 0x20) & 0x7fff) >> 7 |
         (((uint)((ulonglong)
                  (uint)((int)(short)(ushort)bVar23 * (int)(short)(ushort)(byte)(uVar12 >> 8)) *
                  (ulonglong)DAT_00520c7c >> 0x20) & 0x7fff) >> 7) << 8 |
         (((uint)((ulonglong)
                  (uint)((int)(short)(ushort)bVar23 * (int)(short)(ushort)(byte)(uVar12 >> 0x10)) *
                  (ulonglong)DAT_00520c7c >> 0x20) & 0x7fff) >> 7) << 0x10 | uVar8 << 0x18;
  }
  cVar1 = *(char *)(iVar7 + 0x7c);
  fVar17 = *(float *)(iVar7 + 0x2d8);
  *(float *)(iVar7 + 300) = fVar17;
  *(float *)(iVar7 + 0x130) = fVar17;
  *(float *)(iVar7 + 0x134) = fVar17;
  fVar28 = fVar17;
  fVar29 = fVar17;
  if (cVar1 == '\0') {
    cVar2 = *(char *)(iVar7 + 0x1bc);
    if (cVar2 == '\0') {
      uVar8 = (uint)*(byte *)(iVar7 + 0x1be);
    }
    if (cVar2 != '\0' || uVar8 != 0) {
      if ((int)((uint)*(byte *)(iVar7 + 0x90) << 0x1e) < 0) {
        if (cVar2 != '\0') {
          fVar30 = (float)FUN_004397a8(*(float *)(iVar7 + 0xec) * *(float *)(iVar7 + 0xec) +
                                       *(float *)(iVar7 + 0xf0) * *(float *)(iVar7 + 0xf0));
          fVar32 = (float)FUN_004397a8(*(float *)(iVar7 + 0xf8) * *(float *)(iVar7 + 0xf8) +
                                       *(float *)(iVar7 + 0xfc) * *(float *)(iVar7 + 0xfc));
          *(float *)(iVar7 + 0x130) = fVar17 * (1.0 / ABS(fVar30));
          *(float *)(iVar7 + 0x134) = (1.0 / ABS(fVar32)) * fVar17;
        }
      }
      else {
        fVar28 = (float)FUN_004397a8(*(float *)(iVar7 + 0xec) * *(float *)(iVar7 + 0xec) +
                                     *(float *)(iVar7 + 0xf0) * *(float *)(iVar7 + 0xf0));
        fVar29 = (float)FUN_004397a8(*(float *)(iVar7 + 0xf8) * *(float *)(iVar7 + 0xf8) +
                                     *(float *)(iVar7 + 0xfc) * *(float *)(iVar7 + 0xfc));
        fVar28 = fVar17 * ABS(fVar28);
        fVar29 = fVar17 * ABS(fVar29);
        uVar27 = uVar27 & 0xfffffff;
        fVar17 = fVar29;
        if (fVar29 < fVar28) {
          fVar17 = fVar28;
        }
      }
    }
    uVar8 = uVar27 & 0xfffffff;
    fVar30 = ABS(fVar28);
    if (ABS(fVar29) <= ABS(fVar28)) {
      fVar30 = ABS(fVar29);
    }
    fVar32 = fVar28 - fVar29;
    if (fVar32 < 0.0) {
      fVar32 = fVar29 - fVar28;
    }
    uVar12 = uVar8 | (uint)(fVar30 * DAT_00520754 < fVar32) << 0x1f;
    uVar27 = uVar12 | (uint)(NAN(fVar30 * DAT_00520754) || NAN(fVar32)) << 0x1c;
    if (((byte)(uVar12 >> 0x1f) == ((byte)(uVar27 >> 0x1c) & 1)) && (uVar27 = uVar8, fVar28 < 1.0))
    {
      uVar12 = *(uint *)(iVar7 + 0x124);
      fVar29 = (float)VectorUnsignedToFloat(uVar12 & 0xff,(byte)(uVar8 >> 0x16) & 3);
      fVar29 = fVar29 * fVar28;
      fVar30 = (float)VectorUnsignedToFloat((uVar12 & 0xffff) >> 8,(byte)(uVar8 >> 0x16) & 3);
      fVar30 = fVar30 * fVar28;
      fVar32 = (float)VectorUnsignedToFloat((uVar12 & 0xffffff) >> 0x10,(byte)(uVar8 >> 0x16) & 3);
      fVar32 = fVar32 * fVar28;
      fVar31 = (float)VectorUnsignedToFloat(uVar12 >> 0x18,(byte)(uVar8 >> 0x16) & 3);
      fVar31 = fVar31 * fVar28;
      fVar17 = 1.0;
      fVar28 = 1.0;
      *(uint *)(iVar7 + 0x124) =
           (uint)(0.0 < fVar29) * (int)fVar29 & 0xff |
           ((uint)(0.0 < fVar30) * (int)fVar30 & 0xff) << 8 |
           ((uint)(0.0 < fVar32) * (int)fVar32 & 0xff) << 0x10 |
           (uint)(0.0 < fVar31) * (int)fVar31 * 0x1000000;
      fVar29 = 1.0;
    }
  }
  if ((*(char *)(iVar7 + 0x1bc) == '\0') && (*(char *)(iVar7 + 0x1be) != '\0')) {
    *(float *)(iVar7 + 300) = fVar17;
    *(float *)(iVar7 + 0x130) = fVar28;
    *(float *)(iVar7 + 0x134) = fVar29;
  }
  if (cVar1 == '\0') {
    uVar8 = uVar27 & 0xfffffff;
    uVar12 = uVar8 | (uint)(fVar28 < DAT_00520758) << 0x1f;
    uVar27 = uVar12 | (uint)(NAN(fVar28) || NAN(DAT_00520758)) << 0x1c;
    bVar23 = (byte)(uVar12 >> 0x1f);
    bVar25 = (byte)(uVar27 >> 0x1c) & 1;
    if (bVar23 != bVar25) {
      uVar27 = uVar8 | (uint)(fVar29 < DAT_00520758) << 0x1f |
               (uint)(NAN(fVar29) || NAN(DAT_00520758)) << 0x1c;
      bVar25 = (byte)(uVar27 >> 0x18);
      bVar23 = bVar25 >> 7;
      bVar25 = bVar25 >> 4 & 1;
    }
    if (bVar23 != bVar25) goto LAB_0052075c;
    *(undefined4 *)(iVar7 + 0x110) = 1;
  }
  else {
LAB_0052075c:
    *(undefined4 *)(iVar7 + 0x110) = 0;
    *(undefined4 *)(iVar7 + 0x130) = 0x3f800000;
    *(undefined4 *)(iVar7 + 0x134) = 0x3f800000;
    *(undefined4 *)(iVar7 + 300) = 0x3f800000;
  }
  if (*(char *)(iVar7 + 0x2e0) == '\0') {
    *(byte *)(iVar7 + 0x1bf) = (byte)~(byte)(-(uint)(*(char *)(iVar7 + 0x2e1) == '\0') >> 0x18) >> 7
    ;
  }
  else {
    *(undefined1 *)(iVar7 + 0x1bf) = 1;
  }
  iVar7 = *piVar3;
  cVar1 = *(char *)(iVar7 + 0x7c);
  uVar8 = *(uint *)(iVar7 + 0x84);
  *(undefined4 *)(iVar7 + 0x114) = 0;
  bVar26 = cVar1 == '\0';
  if (bVar26) {
    cVar1 = *(char *)(param_2 + 0xd5);
  }
  if (bVar26 && cVar1 == '\0') {
    if (*(int *)(iVar7 + 0x110) != 0 && uVar8 != 1) {
      uVar12 = uVar8 & 0xffff;
      bVar26 = uVar12 != 0x501;
      if (!bVar26) {
        uVar12 = *(uint *)(iVar7 + 0x124) & 0xff000000;
      }
      if (bVar26 || uVar12 != 0xff000000) goto LAB_005207e4;
    }
    if (*(char *)(iVar7 + 0xa0) != '\x01') {
      *(undefined4 *)(iVar7 + 0x114) = 1;
    }
  }
LAB_005207e4:
  uVar12 = *(uint *)(iVar7 + 0x110);
  fVar17 = *(float *)(iVar7 + 300) * 0.5;
  bVar26 = uVar12 == 1;
  if (bVar26) {
    uVar12 = (uint)*(byte *)(iVar7 + 0x1bf);
  }
  if (bVar26 && uVar12 == 1) {
    fVar17 = *(float *)(iVar7 + 300) + 1.0 + fVar17;
  }
  fVar29 = 4.0;
  fVar28 = 1.0;
  *(undefined4 *)(iVar7 + 0x1c4) = 0;
  *(undefined4 *)(iVar7 + 0x1c8) = 0;
  if (*(char *)(iVar7 + 0x1bc) != '\0') {
    fVar31 = (float)FUN_004397a8(*(float *)(iVar7 + 0xec) * *(float *)(iVar7 + 0xec) +
                                 *(float *)(iVar7 + 0xf0) * *(float *)(iVar7 + 0xf0));
    fVar29 = 4.0;
    fVar32 = (float)FUN_004397a8(*(float *)(iVar7 + 0xf8) * *(float *)(iVar7 + 0xf8) +
                                 *(float *)(iVar7 + 0xfc) * *(float *)(iVar7 + 0xfc));
    fVar30 = DAT_00520bd8;
    fVar31 = ABS(fVar31);
    fVar32 = ABS(fVar32);
    bVar26 = NAN(DAT_00520bd8);
    *(float *)(iVar7 + 0x1c4) = fVar31;
    *(float *)(iVar7 + 0x1c8) = fVar32;
    if (!NAN(fVar31) && !bVar26) {
      fVar29 = 4.0 / fVar31;
    }
    uVar12 = uVar27 & 0xfffffff | (uint)(fVar32 < fVar30) << 0x1f;
    uVar27 = uVar12 | (uint)(NAN(fVar32) || NAN(fVar30)) << 0x1c;
    if ((byte)(uVar12 >> 0x1f) == ((byte)(uVar27 >> 0x1c) & 1)) {
      fVar28 = 4.0 / fVar32;
    }
  }
  uVar12 = *puVar4;
  fVar29 = fVar29 + fVar17;
  fVar35 = (float)param_1[4] - fVar29;
  *(float *)(uVar12 + 0x1c) = fVar35;
  fVar28 = fVar28 + fVar17;
  fVar32 = (float)param_1[5] - fVar28;
  *(float *)(uVar12 + 0x20) = fVar32;
  fVar31 = (float)param_1[4] + (float)param_1[0x14] + fVar29;
  *(float *)(uVar12 + 0x24) = fVar31;
  fVar33 = (float)param_1[5] - fVar28;
  *(float *)(uVar12 + 0x28) = fVar33;
  fVar34 = (float)param_1[4] + (float)param_1[0x14] + fVar29;
  *(float *)(uVar12 + 0x2c) = fVar34;
  fVar17 = (float)param_1[5] + (float)param_1[0x15] + fVar28;
  *(float *)(uVar12 + 0x30) = fVar17;
  fVar29 = (float)param_1[4] - fVar29;
  *(float *)(uVar12 + 0x34) = fVar29;
  fVar30 = (float)param_1[5];
  fVar28 = fVar30 + (float)param_1[0x15] + fVar28;
  *(float *)(uVar12 + 0x38) = fVar28;
  if (*(char *)(iVar7 + 0x1bc) != '\0') {
    *(float *)(uVar12 + 0x1c) =
         *(float *)(iVar7 + 0xec) * fVar35 + *(float *)(iVar7 + 0xf0) * fVar32 +
         *(float *)(iVar7 + 0xf4);
    *(float *)(uVar12 + 0x20) =
         *(float *)(iVar7 + 0xf8) * fVar35 + *(float *)(iVar7 + 0xfc) * fVar32 +
         *(float *)(iVar7 + 0x100);
    fVar30 = *(float *)(iVar7 + 0xf4);
    *(float *)(uVar12 + 0x24) =
         *(float *)(iVar7 + 0xec) * fVar31 + *(float *)(iVar7 + 0xf0) * fVar33 + fVar30;
    *(float *)(uVar12 + 0x28) =
         *(float *)(iVar7 + 0xf8) * fVar31 + *(float *)(iVar7 + 0xfc) * fVar33 +
         *(float *)(iVar7 + 0x100);
    *(float *)(uVar12 + 0x2c) =
         *(float *)(iVar7 + 0xec) * fVar34 + *(float *)(iVar7 + 0xf0) * fVar17 +
         *(float *)(iVar7 + 0xf4);
    *(float *)(uVar12 + 0x30) =
         *(float *)(iVar7 + 0xf8) * fVar34 + *(float *)(iVar7 + 0xfc) * fVar17 +
         *(float *)(iVar7 + 0x100);
    *(float *)(uVar12 + 0x34) =
         *(float *)(iVar7 + 0xec) * fVar29 + *(float *)(iVar7 + 0xf0) * fVar28 +
         *(float *)(iVar7 + 0xf4);
    *(float *)(uVar12 + 0x38) =
         *(float *)(iVar7 + 0xf8) * fVar29 + *(float *)(iVar7 + 0xfc) * fVar28 +
         *(float *)(iVar7 + 0x100);
  }
  fVar29 = *(float *)(uVar12 + 0x1c);
  uVar19 = uVar27 & 0xfffffff | (uint)(fVar29 == 0.0) << 0x1e | (uint)(0.0 <= fVar29) << 0x1d;
  bVar23 = (byte)(uVar19 >> 0x18);
  bVar26 = (bool)(bVar23 >> 6);
  bVar24 = (bool)(bVar23 >> 5 & 1);
  if (!bVar24 || bVar26) {
    uVar19 = uVar27 & 0xfffffff | (uint)(*(float *)(uVar12 + 0x24) == 0.0) << 0x1e |
             (uint)(0.0 <= *(float *)(uVar12 + 0x24)) << 0x1d;
    bVar23 = (byte)(uVar19 >> 0x18);
    bVar26 = (bool)(bVar23 >> 6);
    bVar24 = (bool)(bVar23 >> 5 & 1);
  }
  if (!bVar24 || bVar26) {
    uVar27 = uVar19 & 0xfffffff;
    uVar19 = uVar27 | (uint)(*(float *)(uVar12 + 0x2c) == 0.0) << 0x1e |
             (uint)(0.0 <= *(float *)(uVar12 + 0x2c)) << 0x1d;
    bVar23 = (byte)(uVar19 >> 0x18);
    bVar26 = (bool)(bVar23 >> 6);
    bVar24 = (bool)(bVar23 >> 5 & 1);
    if (!bVar24 || bVar26) {
      uVar19 = uVar27 | (uint)(*(float *)(uVar12 + 0x34) == 0.0) << 0x1e |
               (uint)(0.0 <= *(float *)(uVar12 + 0x34)) << 0x1d;
      bVar23 = (byte)(uVar19 >> 0x18);
      bVar26 = (bool)(bVar23 >> 6);
      bVar24 = (bool)(bVar23 >> 5 & 1);
    }
    if (!bVar24 || bVar26) {
      return 0.0;
    }
  }
  fVar32 = *(float *)(uVar12 + 0x20);
  uVar27 = uVar19 & 0xfffffff | (uint)(fVar32 == 0.0) << 0x1e | (uint)(0.0 <= fVar32) << 0x1d;
  bVar23 = (byte)(uVar27 >> 0x18);
  bVar26 = (bool)(bVar23 >> 6);
  bVar24 = (bool)(bVar23 >> 5 & 1);
  if (!bVar24 || bVar26) {
    uVar27 = uVar19 & 0xfffffff | (uint)(*(float *)(uVar12 + 0x28) == 0.0) << 0x1e |
             (uint)(0.0 <= *(float *)(uVar12 + 0x28)) << 0x1d;
    bVar23 = (byte)(uVar27 >> 0x18);
    bVar26 = (bool)(bVar23 >> 6);
    bVar24 = (bool)(bVar23 >> 5 & 1);
  }
  if (!bVar24 || bVar26) {
    uVar19 = uVar27 & 0xfffffff;
    uVar27 = uVar19 | (uint)(*(float *)(uVar12 + 0x30) == 0.0) << 0x1e |
             (uint)(0.0 <= *(float *)(uVar12 + 0x30)) << 0x1d;
    bVar23 = (byte)(uVar27 >> 0x18);
    bVar26 = (bool)(bVar23 >> 6);
    bVar24 = (bool)(bVar23 >> 5 & 1);
    if (!bVar24 || bVar26) {
      uVar27 = uVar19 | (uint)(*(float *)(uVar12 + 0x38) == 0.0) << 0x1e |
               (uint)(0.0 <= *(float *)(uVar12 + 0x38)) << 0x1d;
      bVar23 = (byte)(uVar27 >> 0x18);
      bVar26 = (bool)(bVar23 >> 6);
      bVar24 = (bool)(bVar23 >> 5 & 1);
    }
    if (!bVar24 || bVar26) {
      return 0.0;
    }
  }
  fVar31 = (float)VectorSignedToFloat(*(undefined4 *)(uVar12 + 0x10),(byte)(uVar27 >> 0x16) & 3);
  bVar26 = NAN(fVar29) || NAN(fVar31);
  uVar19 = uVar27 & 0xfffffff | (uint)(fVar29 < fVar31) << 0x1f;
  bVar24 = SUB41(uVar19 >> 0x1f,0);
  if (bVar24 == bVar26) {
    bVar26 = NAN(*(float *)(uVar12 + 0x24)) || NAN(fVar31);
    uVar19 = uVar27 & 0xfffffff | (uint)(*(float *)(uVar12 + 0x24) < fVar31) << 0x1f;
    bVar24 = SUB41(uVar19 >> 0x1f,0);
  }
  if (bVar24 == bVar26) {
    fVar17 = *(float *)(uVar12 + 0x2c);
    bVar26 = NAN(fVar17) || NAN(fVar31);
    uVar27 = uVar19 & 0xfffffff;
    uVar19 = uVar27 | (uint)(fVar17 < fVar31) << 0x1f;
    bVar24 = SUB41(uVar19 >> 0x1f,0);
    if (bVar24 == bVar26) {
      bVar26 = NAN(*(float *)(uVar12 + 0x34)) || NAN(fVar31);
      uVar19 = uVar27 | (uint)(*(float *)(uVar12 + 0x34) < fVar31) << 0x1f;
      bVar24 = SUB41(uVar19 >> 0x1f,0);
    }
    if (bVar24 == bVar26) {
      return 0.0;
    }
  }
  fVar31 = (float)VectorSignedToFloat(*(undefined4 *)(uVar12 + 0x14),(byte)(uVar19 >> 0x16) & 3);
  uVar13 = uVar19 & 0xfffffff | (uint)(fVar32 < fVar31) << 0x1f;
  uVar27 = uVar13 | (uint)(NAN(fVar32) || NAN(fVar31)) << 0x1c;
  bVar23 = (byte)(uVar13 >> 0x1f);
  bVar25 = (byte)(uVar27 >> 0x1c) & 1;
  if (bVar23 == bVar25) {
    uVar27 = uVar19 & 0xfffffff | (uint)(*(float *)(uVar12 + 0x28) < fVar31) << 0x1f |
             (uint)(NAN(*(float *)(uVar12 + 0x28)) || NAN(fVar31)) << 0x1c;
    bVar25 = (byte)(uVar27 >> 0x18);
    bVar23 = bVar25 >> 7;
    bVar25 = bVar25 >> 4 & 1;
  }
  if (bVar23 == bVar25) {
    fVar17 = *(float *)(uVar12 + 0x30);
    uVar19 = uVar27 & 0xfffffff;
    uVar13 = uVar19 | (uint)(fVar17 < fVar31) << 0x1f;
    uVar27 = uVar13 | (uint)(NAN(fVar17) || NAN(fVar31)) << 0x1c;
    bVar23 = (byte)(uVar13 >> 0x1f);
    bVar25 = (byte)(uVar27 >> 0x1c) & 1;
    if (bVar23 == bVar25) {
      uVar27 = uVar19 | (uint)(*(float *)(uVar12 + 0x38) < fVar31) << 0x1f |
               (uint)(NAN(*(float *)(uVar12 + 0x38)) || NAN(fVar31)) << 0x1c;
      bVar25 = (byte)(uVar27 >> 0x18);
      bVar23 = bVar25 >> 7;
      bVar25 = bVar25 >> 4 & 1;
    }
    if (bVar23 == bVar25) {
      return 0.0;
    }
  }
  if (*(char *)(iVar7 + 0x7e) == '\0') {
    bVar26 = NAN(fVar29) || NAN(DAT_00520c68);
    uVar19 = uVar27 & 0xfffffff | (uint)(fVar29 < DAT_00520c68) << 0x1f;
    bVar24 = SUB41(uVar19 >> 0x1f,0);
    if (bVar24 != bVar26) {
      bVar26 = NAN(fVar32) || NAN(DAT_00520c68);
      uVar19 = uVar27 & 0xfffffff | (uint)(fVar32 < DAT_00520c68) << 0x1f;
      bVar24 = SUB41(uVar19 >> 0x1f,0);
    }
    if (bVar24 != bVar26) {
      fVar31 = *(float *)(uVar12 + 0x24);
      bVar26 = NAN(fVar31) || NAN(DAT_00520c68);
      uVar27 = uVar19 & 0xfffffff | (uint)(fVar31 < DAT_00520c68) << 0x1f;
      bVar24 = SUB41(uVar27 >> 0x1f,0);
      if (bVar24 != bVar26) {
        fVar17 = *(float *)(uVar12 + 0x28);
        bVar26 = NAN(fVar17) || NAN(DAT_00520c68);
        uVar27 = uVar19 & 0xfffffff | (uint)(fVar17 < DAT_00520c68) << 0x1f;
        bVar24 = SUB41(uVar27 >> 0x1f,0);
      }
      if (bVar24 != bVar26) {
        fVar33 = *(float *)(uVar12 + 0x2c);
        bVar26 = NAN(fVar33) || NAN(DAT_00520c68);
        uVar19 = uVar27 & 0xfffffff | (uint)(fVar33 < DAT_00520c68) << 0x1f;
        bVar24 = SUB41(uVar19 >> 0x1f,0);
        if (bVar24 != bVar26) {
          fVar28 = *(float *)(uVar12 + 0x30);
          bVar26 = NAN(fVar28) || NAN(DAT_00520c68);
          uVar19 = uVar27 & 0xfffffff | (uint)(fVar28 < DAT_00520c68) << 0x1f;
          bVar24 = SUB41(uVar19 >> 0x1f,0);
        }
        if (bVar24 != bVar26) {
          fVar34 = *(float *)(uVar12 + 0x34);
          bVar26 = NAN(fVar34) || NAN(DAT_00520c68);
          uVar13 = uVar19 & 0xfffffff | (uint)(fVar34 < DAT_00520c68) << 0x1f;
          bVar24 = SUB41(uVar13 >> 0x1f,0);
          if (bVar24 != bVar26) {
            fVar30 = *(float *)(uVar12 + 0x38);
            bVar26 = NAN(fVar30) || NAN(DAT_00520c68);
            uVar13 = uVar19 & 0xfffffff | (uint)(fVar30 < DAT_00520c68) << 0x1f;
            bVar24 = SUB41(uVar13 >> 0x1f,0);
          }
          if ((((bVar24 != bVar26) &&
               (DAT_00520c6c <= fVar29 && (DAT_00520c6c <= fVar29 && DAT_00520c6c <= fVar32))) &&
              (DAT_00520c6c <= fVar31 && (DAT_00520c6c <= fVar31 && DAT_00520c6c <= fVar17))) &&
             (DAT_00520c6c <= fVar33 && (DAT_00520c6c <= fVar33 && DAT_00520c6c <= fVar28))) {
            uVar27 = uVar13 & 0xfffffff | (uint)(fVar34 < DAT_00520c6c) << 0x1f;
            bVar23 = -(char)((int)uVar27 >> 0x1f);
            if (bVar23 == 0) {
              uVar27 = uVar13 & 0xfffffff | (uint)(fVar30 < DAT_00520c6c) << 0x1f;
              bVar23 = (byte)(uVar27 >> 0x1f);
            }
            if (bVar23 == 0) goto LAB_00520bf4;
          }
        }
      }
    }
    if (-1 < (int)((uint)*(byte *)(iVar7 + 0x90) << 0x1d)) {
      FUN_0051565c(0x4000);
      return 2.29589e-41;
    }
    fVar17 = (float)FUN_00567230(param_1,param_2);
    if (fVar17 == 0.0) {
      return 0.0;
    }
LAB_00520c18:
    iVar7 = *piVar3;
    *(undefined4 *)(iVar7 + 0x114) = 0;
    *(undefined4 *)(iVar7 + 0x118) = 0;
    FUN_0051565c(fVar17);
    return fVar17;
  }
LAB_00520bf4:
  if (*(int *)(iVar7 + 0x114) == 1) {
    if ((DAT_00520c80 & uVar8) == 0x501) {
      puVar9 = (undefined4 *)FUN_00514aec(4);
      if (puVar9 == (undefined4 *)0x0) {
        fVar17 = 7.17465e-43;
        goto LAB_00520c18;
      }
      *puVar9 = 0x1d0;
      puVar9[1] = 1;
      uVar14 = DAT_00520c84;
      puVar9[2] = 0x11c;
      puVar9[3] = uVar14;
      puVar9[4] = 300;
      uVar14 = *(undefined4 *)(*piVar3 + 0x124);
      puVar9[6] = 0x118;
      puVar9[5] = uVar14;
      puVar9[7] = 0x90000000;
    }
    else {
      FUN_00513924(uVar8 | 0x1000000,0,0xffffffff);
      FUN_00522a16(*(undefined4 *)(*piVar3 + 0x124));
    }
    FUN_00516c82(*piVar3 + 0xec);
    if (*(char *)(*piVar3 + 0x2e4) == '\0') {
      if (*(int *)(*piVar3 + 0x110) == 0) {
        fVar17 = (float)FUN_005171f8(param_1);
      }
      else {
        fVar17 = (float)FUN_0051d2e0();
      }
    }
    else {
      fVar17 = (float)FUN_0051f798(param_1);
    }
    if (fVar17 != 0.0) {
      iVar7 = *piVar3;
      *(undefined4 *)(iVar7 + 0x114) = 0;
      *(undefined4 *)(iVar7 + 0x118) = 0;
      FUN_0051565c(fVar17);
      goto LAB_00520c18;
    }
    goto LAB_00520ce6;
  }
  iVar7 = *piVar5;
  if (*(char *)(iVar7 + 8) == '\x01') {
    iVar7 = *(int *)(iVar7 + 0xc);
    if (iVar7 == 0x40000000) {
      FUN_0052262e(0);
      uVar6 = 3;
    }
    else {
      if (iVar7 != -0x40000000) goto LAB_00520d48;
      FUN_0052264e(0);
      uVar6 = 4;
    }
    *(undefined1 *)(*piVar3 + 0x7f) = uVar6;
  }
LAB_00520d48:
  uVar8 = *puVar4;
  if (*(int *)(uVar8 + 8) == 0) {
    FUN_0051565c(2);
    fVar17 = 2.8026e-45;
  }
  else {
    local_d0[1] = *(float *)(uVar8 + 0x10);
    local_d0[2] = 0.0;
    local_d0[0] = 1.12104e-44;
    uVar14 = 0x80808080;
    FUN_004b1298(3,*(undefined4 *)(uVar8 + 0xc),local_d0[1],*(undefined4 *)(uVar8 + 0x14));
    local_ac = *(uint *)(*puVar4 + 0x10);
    local_b0 = *(uint *)(*puVar4 + 0x14);
    uVar8 = local_ac + 3 >> 2;
    if (*(char *)(*piVar3 + 0x7c) == '\0') {
      uVar14 = 0;
    }
    puVar9 = (undefined4 *)FUN_00514aec(8);
    if (puVar9 == (undefined4 *)0x0) {
      iVar7 = *piVar3;
      *(undefined4 *)(iVar7 + 0x114) = 0;
      *(undefined4 *)(iVar7 + 0x118) = 0;
      FUN_0051565c(0x200);
      fVar17 = 7.17465e-43;
    }
    else {
      *puVar9 = 0x34;
      puVar9[1] = (uVar8 & 0x3fff) << 2 | 0x1000000;
      puVar9[2] = 0x38;
      puVar9[6] = 0x11c;
      puVar9[3] = uVar8 | local_b0 << 0x10;
      puVar9[5] = 1;
      puVar9[7] = DAT_00521c18;
      puVar9[10] = 0x110;
      puVar9[4] = 0x1d0;
      puVar9[8] = 300;
      puVar9[9] = uVar14;
      puVar9[0xb] = 0;
      puVar9[0xc] = 0x114;
      puVar9[0xe] = 0x118;
      puVar9[0xd] = uVar8 & 0xffff | local_b0 << 0x10;
      puVar9[0xf] = 0x90000000;
      local_98 = FUN_005226b2(0);
      FUN_0043bb00(&local_a8,0,0x10);
      uVar8 = *puVar4;
      local_d0[0] = *(float *)(uVar8 + 0x1c);
      local_d0[1] = *(float *)(uVar8 + 0x20);
      local_d0[2] = *(float *)(uVar8 + 0x24);
      local_d0[3] = *(float *)(uVar8 + 0x28);
      local_d0[4] = *(float *)(uVar8 + 0x2c);
      local_d0[5] = *(float *)(uVar8 + 0x30);
      local_d0[6] = *(float *)(uVar8 + 0x34);
      iVar7 = 0;
      uVar27 = uVar27 & 0xfffffff;
      local_d0[7] = *(float *)(uVar8 + 0x38);
      if (local_d0[2] < local_d0[0]) {
LAB_00520ef2:
        pfVar10 = local_d0 + 2;
        iVar7 = 1;
        uVar12 = uVar27;
      }
      else {
        fVar17 = ABS(local_d0[0]);
        if (ABS(local_d0[2]) <= ABS(local_d0[0])) {
          fVar17 = ABS(local_d0[2]);
        }
        fVar28 = local_d0[0] - local_d0[2];
        if (fVar28 < 0.0) {
          fVar28 = local_d0[2] - local_d0[0];
        }
        uVar12 = uVar27 | (uint)(fVar17 * DAT_00520e58 < fVar28) << 0x1f;
        pfVar10 = local_d0;
        if ((SUB41(uVar12 >> 0x1f,0) == (NAN(fVar17 * DAT_00520e58) || NAN(fVar28))) &&
           (pfVar10 = local_d0, uVar12 = uVar27, *(float *)(uVar8 + 0x28) < *(float *)(uVar8 + 0x20)
           )) goto LAB_00520ef2;
      }
      fVar17 = *pfVar10;
      uVar12 = uVar12 & 0xfffffff;
      if (local_d0[4] < fVar17) {
LAB_00520f5a:
        pfVar10 = local_d0 + 4;
        iVar7 = 2;
        uVar27 = uVar12;
      }
      else {
        fVar28 = fVar17;
        if (fVar17 < 0.0) {
          fVar28 = -fVar17;
        }
        fVar29 = ABS(local_d0[4]);
        if (fVar28 < ABS(local_d0[4])) {
          fVar29 = fVar28;
        }
        fVar28 = fVar17 - local_d0[4];
        if (fVar28 < 0.0) {
          fVar28 = local_d0[4] - fVar17;
        }
        uVar27 = uVar12 | (uint)(fVar29 * DAT_00520e58 < fVar28) << 0x1f;
        if ((SUB41(uVar27 >> 0x1f,0) == (NAN(fVar29 * DAT_00520e58) || NAN(fVar28))) &&
           (uVar27 = uVar12, *(float *)(uVar8 + 0x30) < pfVar10[1])) goto LAB_00520f5a;
      }
      fVar17 = *pfVar10;
      uVar27 = uVar27 & 0xfffffff;
      if (local_d0[6] < fVar17) {
LAB_00520fc2:
        iVar7 = 3;
        uVar12 = uVar27;
      }
      else {
        fVar28 = fVar17;
        if (fVar17 < 0.0) {
          fVar28 = -fVar17;
        }
        if (ABS(local_d0[6]) <= fVar28) {
          fVar28 = ABS(local_d0[6]);
        }
        fVar29 = fVar17 - local_d0[6];
        if (fVar29 < 0.0) {
          fVar29 = local_d0[6] - fVar17;
        }
        uVar12 = uVar27 | (uint)(fVar28 * DAT_00520e58 < fVar29) << 0x1f;
        if ((SUB41(uVar12 >> 0x1f,0) == (NAN(fVar28 * DAT_00520e58) || NAN(fVar29))) &&
           (uVar12 = uVar27, *(float *)(uVar8 + 0x38) < pfVar10[1])) goto LAB_00520fc2;
      }
      iVar21 = (iVar7 + 1U) - (iVar7 + 1U & 0xfffffffc);
      iVar15 = (iVar7 + 3U) - (iVar7 + 3U & 0xfffffffc);
      uVar12 = uVar12 & 0xfffffff;
      if (0.0 < (local_d0[iVar15 * 2] - local_d0[iVar7 * 2]) *
                (local_d0[iVar21 * 2 + 1] - local_d0[iVar7 * 2 + 1]) +
                (local_d0[iVar7 * 2] - local_d0[iVar21 * 2]) *
                (local_d0[iVar15 * 2 + 1] - local_d0[iVar7 * 2 + 1])) {
        local_d0[0] = *(float *)(uVar8 + 0x34);
        local_d0[1] = *(float *)(uVar8 + 0x38);
        local_d0[2] = *(float *)(uVar8 + 0x2c);
        local_d0[3] = *(float *)(uVar8 + 0x30);
        local_d0[4] = *(float *)(uVar8 + 0x24);
        local_d0[5] = *(float *)(uVar8 + 0x28);
        local_d0[6] = *(float *)(uVar8 + 0x1c);
        local_d0[7] = *(float *)(uVar8 + 0x20);
      }
      if (local_d0[3] < local_d0[1]) {
LAB_005210f6:
        pfVar10 = local_d0 + 2;
        local_a8 = 1.4013e-45;
        uVar27 = uVar12;
      }
      else {
        fVar17 = ABS(local_d0[1]);
        if (ABS(local_d0[3]) <= ABS(local_d0[1])) {
          fVar17 = ABS(local_d0[3]);
        }
        fVar28 = local_d0[1] - local_d0[3];
        if (fVar28 < 0.0) {
          fVar28 = local_d0[3] - local_d0[1];
        }
        uVar27 = uVar12 | (uint)(fVar17 * DAT_00520e58 < fVar28) << 0x1f;
        pfVar10 = local_d0;
        if ((SUB41(uVar27 >> 0x1f,0) == (NAN(fVar17 * DAT_00520e58) || NAN(fVar28))) &&
           (pfVar10 = local_d0, uVar27 = uVar12, local_d0[0] < local_d0[2])) goto LAB_005210f6;
      }
      fVar17 = pfVar10[1];
      uVar27 = uVar27 & 0xfffffff;
      if (local_d0[5] < fVar17) {
LAB_0052115e:
        pfVar10 = local_d0 + 4;
        local_a8 = 2.8026e-45;
        uVar8 = uVar27;
      }
      else {
        fVar28 = ABS(local_d0[5]);
        if (ABS(pfVar10[1]) < ABS(local_d0[5])) {
          fVar28 = ABS(pfVar10[1]);
        }
        fVar29 = fVar17 - local_d0[5];
        if (fVar29 < 0.0) {
          fVar29 = local_d0[5] - fVar17;
        }
        uVar8 = uVar27 | (uint)(fVar28 * DAT_00520e58 < fVar29) << 0x1f;
        if ((SUB41(uVar8 >> 0x1f,0) == (NAN(fVar28 * DAT_00520e58) || NAN(fVar29))) &&
           (uVar8 = uVar27, *pfVar10 < local_d0[4])) goto LAB_0052115e;
      }
      fVar17 = pfVar10[1];
      uVar8 = uVar8 & 0xfffffff;
      if (local_d0[7] < fVar17) {
LAB_005211c6:
        pfVar10 = local_d0 + 6;
        local_a8 = 4.2039e-45;
        uVar27 = uVar8;
      }
      else {
        fVar28 = ABS(pfVar10[1]);
        if (ABS(local_d0[7]) <= ABS(pfVar10[1])) {
          fVar28 = ABS(local_d0[7]);
        }
        fVar29 = fVar17 - local_d0[7];
        if (fVar29 < 0.0) {
          fVar29 = local_d0[7] - fVar17;
        }
        uVar27 = uVar8 | (uint)(fVar28 * DAT_00520e58 < fVar29) << 0x1f;
        if ((SUB41(uVar27 >> 0x1f,0) == (NAN(fVar28 * DAT_00520e58) || NAN(fVar29))) &&
           (uVar27 = uVar8, *pfVar10 < local_d0[6])) goto LAB_005211c6;
      }
      uVar27 = uVar27 & 0xfffffff;
      if (local_d0[3] < local_d0[1]) {
LAB_0052122a:
        pfVar20 = local_d0 + 2;
        local_9c = 1;
        uVar8 = uVar27;
      }
      else {
        fVar17 = ABS(local_d0[1]);
        if (ABS(local_d0[3]) <= ABS(local_d0[1])) {
          fVar17 = ABS(local_d0[3]);
        }
        fVar28 = local_d0[1] - local_d0[3];
        if (fVar28 < 0.0) {
          fVar28 = local_d0[3] - local_d0[1];
        }
        uVar8 = uVar27 | (uint)(fVar17 * DAT_00520e58 < fVar28) << 0x1f;
        pfVar20 = local_d0;
        if ((SUB41(uVar8 >> 0x1f,0) == (NAN(fVar17 * DAT_00520e58) || NAN(fVar28))) &&
           (pfVar20 = local_d0, uVar8 = uVar27, local_d0[2] < local_d0[0])) goto LAB_0052122a;
      }
      fVar17 = pfVar20[1];
      uVar8 = uVar8 & 0xfffffff;
      if (local_d0[5] < fVar17) {
LAB_00521292:
        pfVar20 = local_d0 + 4;
        local_9c = 2;
        uVar27 = uVar8;
      }
      else {
        fVar28 = ABS(local_d0[5]);
        if (ABS(pfVar20[1]) < ABS(local_d0[5])) {
          fVar28 = ABS(pfVar20[1]);
        }
        fVar29 = fVar17 - local_d0[5];
        if (fVar29 < 0.0) {
          fVar29 = local_d0[5] - fVar17;
        }
        uVar27 = uVar8 | (uint)(fVar28 * DAT_00520e58 < fVar29) << 0x1f;
        if ((SUB41(uVar27 >> 0x1f,0) == (NAN(fVar28 * DAT_00520e58) || NAN(fVar29))) &&
           (uVar27 = uVar8, local_d0[4] < *pfVar20)) goto LAB_00521292;
      }
      fVar17 = pfVar20[1];
      uVar27 = uVar27 & 0xfffffff;
      if (local_d0[7] < fVar17) {
LAB_005212fa:
        pfVar20 = local_d0 + 6;
        local_9c = 3;
        uVar8 = uVar27;
      }
      else {
        fVar28 = ABS(pfVar20[1]);
        if (ABS(local_d0[7]) <= ABS(pfVar20[1])) {
          fVar28 = ABS(local_d0[7]);
        }
        fVar29 = fVar17 - local_d0[7];
        if (fVar29 < 0.0) {
          fVar29 = local_d0[7] - fVar17;
        }
        uVar8 = uVar27 | (uint)(fVar28 * DAT_00520e58 < fVar29) << 0x1f;
        if ((SUB41(uVar8 >> 0x1f,0) == (NAN(fVar28 * DAT_00520e58) || NAN(fVar29))) &&
           (uVar8 = uVar27, local_d0[6] < *pfVar20)) goto LAB_005212fa;
      }
      uVar8 = uVar8 & 0xfffffff;
      if (local_d0[1] < local_d0[3]) {
LAB_0052135e:
        pfVar22 = local_d0 + 2;
        local_a4 = 1;
        uVar27 = uVar8;
      }
      else {
        fVar17 = ABS(local_d0[1]);
        if (ABS(local_d0[3]) <= ABS(local_d0[1])) {
          fVar17 = ABS(local_d0[3]);
        }
        fVar28 = local_d0[1] - local_d0[3];
        if (fVar28 < 0.0) {
          fVar28 = local_d0[3] - local_d0[1];
        }
        uVar27 = uVar8 | (uint)(fVar17 * DAT_00520e58 < fVar28) << 0x1f;
        pfVar22 = local_d0;
        if ((SUB41(uVar27 >> 0x1f,0) == (NAN(fVar17 * DAT_00520e58) || NAN(fVar28))) &&
           (pfVar22 = local_d0, uVar27 = uVar8, local_d0[0] < local_d0[2])) goto LAB_0052135e;
      }
      fVar17 = pfVar22[1];
      uVar27 = uVar27 & 0xfffffff;
      if (fVar17 < local_d0[5]) {
LAB_005213c6:
        pfVar22 = local_d0 + 4;
        local_a4 = 2;
        uVar8 = uVar27;
      }
      else {
        fVar28 = ABS(local_d0[5]);
        if (ABS(pfVar22[1]) < ABS(local_d0[5])) {
          fVar28 = ABS(pfVar22[1]);
        }
        fVar29 = fVar17 - local_d0[5];
        if (fVar29 < 0.0) {
          fVar29 = local_d0[5] - fVar17;
        }
        uVar8 = uVar27 | (uint)(fVar28 * DAT_00520e58 < fVar29) << 0x1f;
        if ((SUB41(uVar8 >> 0x1f,0) == (NAN(fVar28 * DAT_00520e58) || NAN(fVar29))) &&
           (uVar8 = uVar27, *pfVar22 < local_d0[4])) goto LAB_005213c6;
      }
      fVar17 = pfVar22[1];
      uVar8 = uVar8 & 0xfffffff;
      if (fVar17 < local_d0[7]) {
LAB_0052142e:
        pfVar22 = local_d0 + 6;
        local_a4 = 3;
        uVar27 = uVar8;
      }
      else {
        fVar28 = ABS(pfVar22[1]);
        if (ABS(local_d0[7]) <= ABS(pfVar22[1])) {
          fVar28 = ABS(local_d0[7]);
        }
        fVar29 = fVar17 - local_d0[7];
        if (fVar29 < 0.0) {
          fVar29 = local_d0[7] - fVar17;
        }
        uVar27 = uVar8 | (uint)(fVar28 * DAT_00520e58 < fVar29) << 0x1f;
        if ((SUB41(uVar27 >> 0x1f,0) == (NAN(fVar28 * DAT_00520e58) || NAN(fVar29))) &&
           (uVar27 = uVar8, *pfVar22 < local_d0[6])) goto LAB_0052142e;
      }
      uVar27 = uVar27 & 0xfffffff;
      if (local_d0[1] < local_d0[3]) {
LAB_00521492:
        pfVar18 = local_d0 + 2;
        local_a0 = 1.4013e-45;
        uVar8 = uVar27;
      }
      else {
        fVar17 = ABS(local_d0[1]);
        if (ABS(local_d0[3]) <= ABS(local_d0[1])) {
          fVar17 = ABS(local_d0[3]);
        }
        fVar28 = local_d0[1] - local_d0[3];
        if (fVar28 < 0.0) {
          fVar28 = local_d0[3] - local_d0[1];
        }
        uVar8 = uVar27 | (uint)(fVar17 * DAT_00520e58 < fVar28) << 0x1f;
        pfVar18 = local_d0;
        if ((SUB41(uVar8 >> 0x1f,0) == (NAN(fVar17 * DAT_00520e58) || NAN(fVar28))) &&
           (pfVar18 = local_d0, uVar8 = uVar27, local_d0[2] < local_d0[0])) goto LAB_00521492;
      }
      fVar17 = pfVar18[1];
      uVar8 = uVar8 & 0xfffffff;
      if (fVar17 < local_d0[5]) {
LAB_005214fa:
        pfVar18 = local_d0 + 4;
        local_a0 = 2.8026e-45;
        uVar27 = uVar8;
      }
      else {
        fVar28 = ABS(local_d0[5]);
        if (ABS(pfVar18[1]) < ABS(local_d0[5])) {
          fVar28 = ABS(pfVar18[1]);
        }
        fVar29 = fVar17 - local_d0[5];
        if (fVar29 < 0.0) {
          fVar29 = local_d0[5] - fVar17;
        }
        uVar27 = uVar8 | (uint)(fVar28 * DAT_00520e58 < fVar29) << 0x1f;
        if ((SUB41(uVar27 >> 0x1f,0) == (NAN(fVar28 * DAT_00520e58) || NAN(fVar29))) &&
           (uVar27 = uVar8, local_d0[4] < *pfVar18)) goto LAB_005214fa;
      }
      fVar17 = pfVar18[1];
      uVar27 = uVar27 & 0xfffffff;
      if (fVar17 < local_d0[7]) {
LAB_00521562:
        pfVar18 = local_d0 + 6;
        local_a0 = 4.2039e-45;
        uVar12 = uVar27;
      }
      else {
        fVar28 = ABS(pfVar18[1]);
        if (ABS(local_d0[7]) <= ABS(pfVar18[1])) {
          fVar28 = ABS(local_d0[7]);
        }
        fVar29 = fVar17 - local_d0[7];
        if (fVar29 < 0.0) {
          fVar29 = local_d0[7] - fVar17;
        }
        uVar8 = uVar27 | (uint)(fVar28 * DAT_00520e58 < fVar29) << 0x1f;
        uVar12 = uVar8 | (uint)(NAN(fVar28 * DAT_00520e58) || NAN(fVar29)) << 0x1c;
        if (((byte)(uVar8 >> 0x1f) == ((byte)(uVar12 >> 0x1c) & 1)) &&
           (uVar12 = uVar27, local_d0[6] < *pfVar18)) goto LAB_00521562;
      }
      iVar7 = (int)local_a8 + 1;
      if (pfVar10 == pfVar20) {
        fVar30 = pfVar10[1];
        fVar17 = *pfVar10;
        iVar7 = iVar7 - (iVar7 + ((uint)(iVar7 >> 1) >> 0x1e) & 0xfffffffc);
        fVar32 = local_d0[iVar7 * 2];
        fVar31 = local_d0[iVar7 * 2 + 1];
        iVar7 = (int)local_a8 + 3;
        iVar7 = iVar7 - (iVar7 + ((uint)(iVar7 >> 1) >> 0x1e) & 0xfffffffc);
        fVar33 = local_d0[iVar7 * 2];
        fVar34 = local_d0[iVar7 * 2 + 1];
        fVar28 = fVar30;
        fVar29 = fVar17;
      }
      else {
        fVar17 = *pfVar10;
        fVar30 = pfVar10[1];
        iVar7 = iVar7 - (iVar7 + ((uint)(iVar7 >> 1) >> 0x1e) & 0xfffffffc);
        fVar32 = local_d0[iVar7 * 2];
        fVar31 = local_d0[iVar7 * 2 + 1];
        fVar29 = *pfVar20;
        iVar7 = (int)local_a8 + 2;
        iVar7 = iVar7 - (iVar7 + ((uint)(iVar7 >> 1) >> 0x1e) & 0xfffffffc);
        fVar33 = local_d0[iVar7 * 2];
        fVar34 = local_d0[iVar7 * 2 + 1];
        fVar28 = pfVar20[1];
      }
      fVar36 = *pfVar22;
      iVar7 = local_a4 + 3;
      fVar39 = fVar36 + 4.0;
      fVar35 = 1.0;
      if (pfVar22 == pfVar18) {
        iVar15 = local_a4 + 1;
        fVar40 = pfVar22[1];
        iVar15 = iVar15 - (iVar15 + ((uint)(iVar15 >> 1) >> 0x1e) & 0xfffffffc);
        local_a8 = fVar40;
        fVar37 = local_d0[iVar15 * 2];
      }
      else {
        iVar15 = local_a4 + 2;
        local_a8 = pfVar22[1];
        fVar36 = *pfVar18;
        iVar15 = iVar15 - (iVar15 + ((uint)(iVar15 >> 1) >> 0x1e) & 0xfffffffc);
        fVar40 = pfVar18[1];
        fVar37 = local_d0[iVar15 * 2];
      }
      fVar41 = local_d0[iVar15 * 2 + 1];
      iVar7 = iVar7 - (iVar7 + ((uint)(iVar7 >> 1) >> 0x1e) & 0xfffffffc);
      fVar38 = local_d0[iVar7 * 2];
      fVar42 = local_d0[iVar7 * 2 + 1];
      FUN_00516b34((fVar17 + 4.0) * 0.25,fVar30,(fVar32 + 4.0) * 0.25,fVar31,(fVar33 + -4.0) * 0.25,
                   fVar34,(fVar29 + -4.0) * 0.25,fVar28);
      FUN_00516b34(fVar39 * 0.25,local_a8,(fVar36 + -4.0) * 0.25,fVar40,(fVar37 + -4.0) * 0.25,
                   fVar41,(fVar38 + 4.0) * 0.25,fVar42);
      FUN_005226b2(local_98);
      FUN_004b1548();
      FUN_00514846(0x34,local_ac & 0xffff | 0x9000000);
      FUN_00514846(0x38,local_ac | local_b0 << 0x10);
      iVar7 = *piVar3;
      fVar28 = ((float)param_1[4] + (float)param_1[6]) * 0.5 + 0.5;
      fVar17 = ((float)param_1[5] + (float)param_1[7]) * 0.5 + 0.5;
      *(float *)(iVar7 + 0x2c4) = fVar17;
      *(int *)(iVar7 + 0x2cc) = (int)fVar17;
      *(float *)(iVar7 + 0x2c0) = fVar28;
      iVar15 = (int)fVar28;
      *(int *)(iVar7 + 0x2d0) = iVar15 << 0x10;
      *(int *)(iVar7 + 0x2c8) = iVar15;
      *(int *)(iVar7 + 0x2d4) = *(int *)(iVar7 + 0x2cc) << 0x10;
      FUN_00516c82(iVar7 + 0xec);
      iVar7 = *piVar3;
      uVar27 = *(uint *)(iVar7 + 0x110);
      fVar17 = *(float *)(iVar7 + 300) * 0.5;
      bVar26 = uVar27 == 1;
      if (bVar26) {
        uVar27 = (uint)*(byte *)(iVar7 + 0x1bf);
      }
      if (bVar26 && uVar27 == 1) {
        fVar17 = *(float *)(iVar7 + 300) + 1.0 + fVar17;
      }
      fVar28 = 1.0;
      if (!NAN(*(float *)(iVar7 + 0x1c4)) && !NAN(DAT_00521c14)) {
        fVar28 = 1.0 / *(float *)(iVar7 + 0x1c4);
      }
      fVar29 = *(float *)(iVar7 + 0x1c8);
      uVar8 = uVar12 & 0xfffffff | (uint)(fVar29 < DAT_00521c14) << 0x1f;
      uVar27 = uVar8 | (uint)(NAN(fVar29) || NAN(DAT_00521c14)) << 0x1c;
      if ((byte)(uVar8 >> 0x1f) == ((byte)(uVar27 >> 0x1c) & 1)) {
        fVar35 = 1.0 / fVar29;
      }
      fVar28 = fVar28 + fVar17;
      fVar35 = fVar35 + fVar17;
      param_1[8] = (int)((float)param_1[4] - fVar28);
      param_1[9] = (int)((float)param_1[5] - fVar35);
      param_1[10] = (int)((float)param_1[4] + (float)param_1[0x14] + fVar28);
      param_1[0xb] = (int)((float)param_1[5] - fVar35);
      param_1[0xc] = (int)((float)param_1[4] + (float)param_1[0x14] + fVar28);
      param_1[0xd] = (int)((float)param_1[5] + (float)param_1[0x15] + fVar35);
      param_1[0xe] = (int)((float)param_1[4] - fVar28);
      param_1[0xf] = (int)((float)param_1[5] + (float)param_1[0x15] + fVar35);
      param_1[0x10] = (int)((float)param_1[4] - fVar28);
      param_1[0x11] = (int)((float)param_1[5] - fVar35);
      param_1[0x12] = (int)((float)param_1[6] + fVar28);
      param_1[0x13] = (int)((float)param_1[7] + fVar35);
      param_1[0x16] = (int)((float)param_1[0x14] + fVar28 * 2.0);
      param_1[0x17] = (int)((float)param_1[0x15] + fVar35 * 2.0);
      if (*(char *)(iVar7 + 0x1bc) != '\0') {
        pfVar10 = (float *)(iVar7 + 0xec);
        fVar17 = (float)param_1[8];
        param_1[8] = (int)(*pfVar10 * fVar17 + *(float *)(iVar7 + 0xf0) * (float)param_1[9] +
                          *(float *)(iVar7 + 0xf4));
        param_1[9] = (int)(*(float *)(iVar7 + 0xf8) * fVar17 +
                           *(float *)(iVar7 + 0xfc) * (float)param_1[9] + *(float *)(iVar7 + 0x100))
        ;
        fVar17 = (float)param_1[10];
        param_1[10] = (int)(*pfVar10 * fVar17 + *(float *)(iVar7 + 0xf0) * (float)param_1[0xb] +
                           *(float *)(iVar7 + 0xf4));
        param_1[0xb] = (int)(*(float *)(iVar7 + 0xf8) * fVar17 +
                             *(float *)(iVar7 + 0xfc) * (float)param_1[0xb] +
                            *(float *)(iVar7 + 0x100));
        fVar17 = (float)param_1[0xc];
        param_1[0xc] = (int)(*pfVar10 * fVar17 + *(float *)(iVar7 + 0xf0) * (float)param_1[0xd] +
                            *(float *)(iVar7 + 0xf4));
        param_1[0xd] = (int)(*(float *)(iVar7 + 0xf8) * fVar17 +
                             *(float *)(iVar7 + 0xfc) * (float)param_1[0xd] +
                            *(float *)(iVar7 + 0x100));
        fVar17 = (float)param_1[0xe];
        param_1[0xe] = (int)(*pfVar10 * fVar17 + *(float *)(iVar7 + 0xf0) * (float)param_1[0xf] +
                            *(float *)(iVar7 + 0xf4));
        fVar28 = (float)param_1[10];
        fVar30 = (float)param_1[8];
        fVar17 = *(float *)(iVar7 + 0xf8) * fVar17 + *(float *)(iVar7 + 0xfc) * (float)param_1[0xf]
                 + *(float *)(iVar7 + 0x100);
        param_1[0xf] = (int)fVar17;
        fVar29 = fVar30;
        if (fVar28 <= fVar30) {
          fVar29 = fVar28;
        }
        fVar31 = (float)param_1[0xe];
        fVar33 = (float)param_1[0xc];
        fVar32 = fVar33;
        if (fVar31 <= fVar33) {
          fVar32 = fVar31;
        }
        if (fVar32 <= fVar29) {
          fVar29 = fVar32;
        }
        fVar32 = (float)param_1[0xb];
        fVar35 = (float)param_1[9];
        fVar34 = fVar35;
        if (fVar32 <= fVar35) {
          fVar34 = fVar32;
        }
        fVar39 = (float)param_1[0xd];
        fVar36 = fVar39;
        if (fVar17 <= fVar39) {
          fVar36 = fVar17;
        }
        if (fVar36 <= fVar34) {
          fVar34 = fVar36;
        }
        if (fVar28 < fVar30) {
          fVar28 = fVar30;
        }
        if (fVar31 < fVar33) {
          fVar31 = fVar33;
        }
        if (fVar28 <= fVar31) {
          fVar28 = fVar31;
        }
        if (fVar32 < fVar35) {
          fVar32 = fVar35;
        }
        if (fVar17 < fVar39) {
          fVar17 = fVar39;
        }
        if (fVar17 < fVar32) {
          fVar17 = fVar32;
        }
        param_1[0x13] = (int)fVar17;
        param_1[0x10] = (int)fVar29;
        param_1[0x11] = (int)fVar34;
        param_1[0x12] = (int)fVar28;
        param_1[0x16] = (int)(fVar28 - fVar29);
        param_1[0x17] = (int)(fVar17 - fVar34);
        uVar27 = uVar12 & 0xfffffff;
      }
      bVar23 = *(byte *)(iVar7 + 0x7c);
      fVar28 = 0.0;
      if (bVar23 == 0) {
        FUN_00513924(DAT_0052250c,3,0xffffffff);
        FUN_00522a16(0xffffffff);
        if (*(char *)(*piVar3 + 0x2e4) == '\0') {
          if (*(int *)(*piVar3 + 0x110) == 0) {
            fVar17 = (float)FUN_005171f8(param_1);
          }
          else {
            fVar17 = (float)FUN_0051d2e0();
          }
        }
        else {
          fVar17 = (float)FUN_0051f798(param_1);
        }
        if (fVar17 == 0.0) {
          uVar8 = *(uint *)(*puVar4 + 0x10) & 0xffff | 0x8000000;
          goto LAB_00521c52;
        }
LAB_00521c36:
        iVar7 = *piVar3;
        *(undefined4 *)(iVar7 + 0x114) = 0;
        *(undefined4 *)(iVar7 + 0x118) = 0;
        FUN_0051565c(fVar17);
      }
      else {
        if (bVar23 == 2) {
          FUN_00514846(0x11c,0xbc16);
          FUN_00514846(0x1e0,0xbc17);
          FUN_00522956(0x10001);
          fVar17 = (float)FUN_00516e0c(param_1);
          if (fVar17 != 0.0) goto LAB_00521c36;
          uVar8 = *(uint *)(*puVar4 + 0x10) & 0xffff | 0x2f000000;
LAB_00521c52:
          FUN_00514846(0x34,uVar8);
        }
        else {
          if (bVar23 < 2) {
            FUN_00514846(0x11c,0xbc16);
            FUN_00514846(0x1e0,0xbc17);
            FUN_00522956(0x10001);
            fVar17 = (float)FUN_00516e0c(param_1);
            if (fVar17 != 0.0) goto LAB_00521c36;
            uVar8 = *(uint *)(*puVar4 + 0x10) & 0xffff | 0x2e000000;
            goto LAB_00521c52;
          }
          fVar28 = 5.60519e-45;
          FUN_0051565c(4);
        }
        fVar17 = fVar28;
        if (fVar28 == 0.0) {
          iVar7 = *piVar3;
          if (*(char *)(iVar7 + 0xa0) != '\x01') {
LAB_00521d5a:
            if (*(char *)(param_2 + 0xd5) != '\0') {
              FUN_00515148(param_2);
              fVar17 = (float)FUN_0051520c(param_2);
              if (fVar17 != 0.0) {
                iVar7 = *piVar3;
                *(undefined4 *)(iVar7 + 0x114) = 0;
                *(undefined4 *)(iVar7 + 0x118) = 0;
                FUN_0051565c(fVar17);
                goto LAB_00521c6a;
              }
            }
            if ((*(byte *)(*piVar3 + 0x7f) & 7) == 3) {
              FUN_0052262e(1);
            }
            else if ((*(byte *)(*piVar3 + 0x7f) & 7) == 4) {
              FUN_0052264e(1);
            }
            uVar8 = *(uint *)(*piVar3 + 0x84);
            cVar1 = *(char *)(param_2 + 0xd5);
            if (cVar1 == '\0') {
              if ((DAT_00522548 & uVar8) == 0x501) {
                puVar9 = (undefined4 *)FUN_00514aec(3);
                if (puVar9 == (undefined4 *)0x0) {
                  iVar7 = *piVar3;
                  *(undefined4 *)(iVar7 + 0x114) = 0;
                  *(undefined4 *)(iVar7 + 0x118) = 0;
                  FUN_0051565c(0x200);
                  fVar17 = 7.17465e-43;
                  goto LAB_00521c6a;
                }
                *puVar9 = 0x1d0;
                uVar14 = DAT_0052254c;
                puVar9[1] = uVar8;
                puVar9[2] = 0x11c;
                puVar9[3] = uVar14;
                puVar9[4] = 300;
                puVar9[5] = *(undefined4 *)(*piVar3 + 0x124);
              }
              else {
                uVar12 = (uVar8 & 0xfff) >> 8;
                local_d0[2] = 1.102026e-39;
                if ((int)(uVar8 << 1) < 0) {
                  local_d0[2] = 2.571394e-39;
                }
                local_d0[0] = DAT_00522550;
                local_d0[1] = DAT_00522554;
                iVar7 = 2;
                local_d0[3] = (float)(DAT_00522558 | *(uint *)(DAT_0052252c + (uVar8 & 0xf) * 4));
                if (uVar12 != 0) {
                  local_d0[4] = 0.0;
                  iVar7 = 3;
                  local_d0[5] = (float)(*(uint *)(DAT_0052252c + uVar12 * 4) | DAT_00522534);
                }
                local_d0[iVar7 * 2] = DAT_00522538;
                local_d0[iVar7 * 2 + 1] = DAT_0052255c;
                local_d0[(iVar7 + 1) * 2] = DAT_00522540;
                local_d0[(iVar7 + 1) * 2 + 1] = DAT_00522560;
                FUN_0052294c(0xbc00);
                FUN_00522956(1);
                FUN_00522920(local_d0,iVar7 + 2,0);
                FUN_00522a16(*(undefined4 *)(*piVar3 + 0x124));
              }
            }
            else if ((uVar8 & 0xffff) == 0x501) {
              FUN_00514846(0x1d0,uVar8);
              uVar12 = 0;
              if ((int)(uVar8 << 1) < 0) {
                uVar12 = 0x100000;
              }
              local_a0 = DAT_0052256c;
              local_9c = DAT_00522570;
              local_98 = DAT_00522574;
              uStack_94 = DAT_00522578;
              uStack_90 = DAT_0052257c;
              uStack_8c = DAT_00522580;
              local_d0[6] = DAT_00522584;
              local_d0[7] = DAT_00522588;
              local_b0 = DAT_0052258c;
              local_ac = DAT_00522590;
              local_a8 = DAT_00522594;
              local_a4 = DAT_00522598;
              local_88 = DAT_0052259c;
              uStack_84 = DAT_005225a0;
              uStack_80 = DAT_005225a4;
              uStack_7c = DAT_005225a8;
              local_78 = DAT_005225ac;
              uStack_74 = DAT_005225b0;
              local_70 = DAT_005225b4;
              uStack_6c = DAT_005225b8;
              local_d0[0] = DAT_005225bc;
              local_d0[1] = DAT_005225c0;
              local_d0[2] = DAT_005225c4;
              local_d0[3] = DAT_005225c8;
              local_d0[4] = DAT_005225cc;
              local_d0[5] = DAT_005225d0;
              uVar19 = uVar27 & 0xfffffff | (uint)(*(float *)(param_2 + 0xd0) < 1.0) << 0x1f;
              uVar27 = uVar19 | (uint)NAN(*(float *)(param_2 + 0xd0)) << 0x1c;
              if ((byte)(uVar19 >> 0x1f) == ((byte)(uVar27 >> 0x1c) & 1)) {
                cVar1 = *(char *)(param_2 + 0xd5);
                iVar7 = 8;
                iVar15 = 2;
                bVar26 = cVar1 == '\x02';
                if (bVar26) {
                  cVar1 = *(char *)(param_2 + 0x2c);
                }
                uVar19 = DAT_00522510;
                if (bVar26 && cVar1 == '\x01') {
                  iVar7 = 0;
                  iVar15 = 3;
                  uVar19 = DAT_00522514;
                }
                if ((int)(uVar8 << 5) < 0) {
                  local_98 = uVar12 | DAT_00522574;
                  pfVar11 = &local_a0;
                }
                else {
                  local_b0 = uVar12 | DAT_0052258c;
                  pfVar11 = local_d0 + 6;
                }
                FUN_00522920((int)pfVar11 + iVar7,iVar15,0);
                FUN_0052294c(uVar19 | (0x20 - iVar15) * 0x10000);
              }
              else {
                cVar1 = *(char *)(param_2 + 0xd5);
                iVar7 = 8;
                iVar15 = 2;
                bVar26 = cVar1 == '\x02';
                if (bVar26) {
                  cVar1 = *(char *)(param_2 + 0x2c);
                }
                uVar19 = DAT_00522510;
                if (bVar26 && cVar1 == '\x01') {
                  iVar7 = 0;
                  iVar15 = 3;
                  uVar19 = DAT_00522514;
                }
                if ((int)(uVar8 << 5) < 0) {
                  iVar15 = iVar15 + 1;
                  local_78 = uVar12 | DAT_005225ac;
                  pfVar11 = (float *)&local_88;
                }
                else {
                  local_d0[2] = (float)(uVar12 | (uint)DAT_005225c4);
                }
                FUN_00522920((undefined1 *)((int)pfVar11 + iVar7),iVar15,0);
                FUN_0052294c(uVar19 | (0x20 - iVar15) * 0x10000);
                FUN_00513e2e((int)(*(float *)(param_2 + 0xd0) * DAT_00522120 + 0.5) << 0x18);
              }
            }
            else {
              bVar26 = cVar1 == '\x02';
              if (bVar26) {
                cVar1 = *(char *)(param_2 + 0x2c);
              }
              uVar12 = (uVar8 & 0xfff) >> 8;
              uVar19 = 0;
              if ((int)(uVar8 << 1) < 0) {
                uVar19 = 0x100000;
              }
              local_d0[0] = DAT_00522518;
              iVar7 = 1;
              if (bVar26 && cVar1 == '\x01') {
                local_d0[3] = 0.0;
                local_d0[2] = DAT_0052251c;
                iVar7 = 2;
              }
              if ((int)(uVar8 << 5) < 0) {
                local_d0[iVar7 * 2] = (float)(uVar19 | 0x4c0000);
                local_d0[iVar7 * 2 + 1] = DAT_00522520;
                iVar7 = iVar7 + 1;
              }
              uVar13 = DAT_00522524;
              if ((uVar8 & 0xf) - 6 < 4) {
                local_d0[iVar7 * 2] = (float)(DAT_00522524 | uVar19);
                local_d0[iVar7 * 2 + 1] = 0.0;
                iVar7 = iVar7 + 1;
                uVar13 = DAT_00522528;
              }
              local_d0[iVar7 * 2] = (float)(uVar19 | uVar13);
              local_d0[iVar7 * 2 + 1] =
                   (float)(DAT_00522530 | *(uint *)(DAT_0052252c + 0x40 + (uVar8 & 0xf) * 4));
              iVar15 = iVar7 + 1;
              if (uVar12 != 0) {
                local_d0[iVar15 * 2] = 0.0;
                local_d0[iVar15 * 2 + 1] =
                     (float)(*(uint *)(DAT_0052252c + 0x40 + uVar12 * 4) | DAT_00522534);
                iVar15 = iVar7 + 2;
              }
              local_d0[iVar15 * 2] = DAT_00522538;
              local_d0[iVar15 * 2 + 1] = DAT_0052253c;
              local_d0[(iVar15 + 1) * 2] = DAT_00522540;
              local_d0[(iVar15 + 1) * 2 + 1] = DAT_00522544;
              local_d0[1] = fVar28;
              FUN_0052294c(0x9c00);
              FUN_00522956(1);
              FUN_00522920(local_d0,iVar15 + 2,0);
            }
            if (*(char *)(param_2 + 0xd5) == '\x04') {
              iVar7 = FUN_004b14fe();
              uVar27 = uVar27 & 0xfffffff;
              fVar17 = *(float *)(param_2 + 0xc4);
              if (*(float *)(param_2 + 0xc4) < 0.0) {
                fVar17 = DAT_005223fc;
              }
              fVar28 = (float)VectorSignedToFloat(*(undefined4 *)(*puVar4 + 0x10),
                                                  (byte)(uVar27 >> 0x16) & 3);
              if (fVar28 < fVar17) {
                fVar17 = fVar28;
              }
              fVar29 = *(float *)(param_2 + 200);
              if (*(float *)(param_2 + 200) < 0.0) {
                fVar29 = DAT_005223fc;
              }
              fVar30 = (float)VectorSignedToFloat(*(undefined4 *)(*puVar4 + 0x14),
                                                  (byte)(uVar27 >> 0x16) & 3);
              if (fVar30 < fVar29) {
                fVar29 = fVar30;
              }
              fVar28 = (fVar28 - fVar17) + 0.5;
              uVar8 = uVar27 | (uint)(fVar28 < 0.0) << 0x1f | (uint)(fVar28 == 0.0) << 0x1e;
              uVar12 = uVar8 | (uint)NAN(fVar28) << 0x1c;
              fVar30 = (fVar30 - fVar29) + 0.5;
              bVar23 = (byte)(uVar8 >> 0x18);
              bVar25 = bVar23 >> 7;
              bVar26 = (bool)(bVar23 >> 6 & 1);
              bVar23 = (byte)(uVar12 >> 0x1c) & 1;
              if (!bVar26 && bVar25 == bVar23) {
                uVar12 = uVar27 | (uint)(fVar30 < 0.0) << 0x1f | (uint)(fVar30 == 0.0) << 0x1e |
                         (uint)NAN(fVar30) << 0x1c;
                bVar23 = (byte)(uVar12 >> 0x18);
                bVar25 = bVar23 >> 7;
                bVar26 = (bool)(bVar23 >> 6 & 1);
                bVar23 = bVar23 >> 4 & 1;
              }
              if (!bVar26 && bVar25 == bVar23) {
                FUN_005226e8(param_2 + 0x34);
                if (iVar7 == 0) {
                  FUN_004b1516((int)fVar17,(int)fVar29,(uint)(0.0 < fVar28) * (int)fVar28,
                               (uint)(0.0 < fVar30) * (int)fVar30);
                }
                else {
                  FUN_004b14ca();
                }
                FUN_00516b34(param_1[8],param_1[9],param_1[10],param_1[0xb],param_1[0xc],
                             param_1[0xd],param_1[0xe],param_1[0xf]);
              }
              fVar30 = fVar17 + 0.5;
              uVar27 = uVar12 & 0xfffffff | (uint)(fVar30 < 0.0) << 0x1f |
                       (uint)(fVar30 == 0.0) << 0x1e;
              uVar8 = uVar27 | (uint)NAN(fVar30) << 0x1c;
              fVar28 = (float)VectorSignedToFloat(*(undefined4 *)(*puVar4 + 0x14),
                                                  (byte)(uVar8 >> 0x16) & 3);
              fVar28 = (fVar28 - fVar29) + 0.5;
              bVar23 = (byte)(uVar27 >> 0x18);
              if (!(bool)(bVar23 >> 6 & 1) && bVar23 >> 7 == ((byte)(uVar8 >> 0x1c) & 1)) {
                uVar27 = uVar12 & 0xfffffff | (uint)(fVar28 < 0.0) << 0x1f |
                         (uint)(fVar28 == 0.0) << 0x1e;
                uVar8 = uVar27 | (uint)NAN(fVar28) << 0x1c;
                bVar23 = (byte)(uVar27 >> 0x18);
                if (!(bool)(bVar23 >> 6 & 1) && bVar23 >> 7 == ((byte)(uVar8 >> 0x1c) & 1)) {
                  FUN_005226e8(param_2 + 0x58);
                  if (iVar7 == 0) {
                    FUN_004b1516(0,(int)fVar29,(uint)(0.0 < fVar30) * (int)fVar30,
                                 (uint)(0.0 < fVar28) * (int)fVar28);
                  }
                  else {
                    FUN_004b14ca(0);
                  }
                  FUN_00516b34(param_1[8],param_1[9],param_1[10],param_1[0xb],param_1[0xc],
                               param_1[0xd],param_1[0xe],param_1[0xf]);
                }
                fVar28 = fVar29 + 0.5;
                uVar27 = uVar8 & 0xfffffff | (uint)(fVar28 < 0.0) << 0x1f |
                         (uint)(fVar28 == 0.0) << 0x1e;
                uVar8 = uVar27 | (uint)NAN(fVar28) << 0x1c;
                bVar23 = (byte)(uVar27 >> 0x18);
                if (!(bool)(bVar23 >> 6 & 1) && bVar23 >> 7 == ((byte)(uVar8 >> 0x1c) & 1)) {
                  FUN_005226e8(param_2 + 0x7c);
                  if (iVar7 == 0) {
                    FUN_004b1516(0,0,(uint)(0.0 < fVar30) * (int)fVar30,
                                 (uint)(0.0 < fVar28) * (int)fVar28);
                  }
                  else {
                    FUN_004b14ca(0,0);
                  }
                  FUN_00516b34(param_1[8],param_1[9],param_1[10],param_1[0xb],param_1[0xc],
                               param_1[0xd],param_1[0xe],param_1[0xf]);
                }
              }
              fVar29 = fVar29 + 0.5;
              fVar28 = (float)VectorSignedToFloat(*(undefined4 *)(*puVar4 + 0x10),
                                                  (byte)(uVar8 >> 0x16) & 3);
              fVar30 = (fVar28 - fVar17) + 0.5;
              bVar26 = fVar30 < 0.0;
              bVar24 = fVar30 == 0.0;
              fVar28 = fVar30;
              if (!bVar24 && !bVar26) {
                bVar26 = fVar29 < 0.0;
                bVar24 = fVar29 == 0.0;
                fVar28 = fVar29;
              }
              if (!bVar24 && bVar26 == NAN(fVar28)) {
                FUN_005226e8(param_2 + 0xa0);
                if (iVar7 == 0) {
                  FUN_004b1516((int)fVar17,0,(uint)(0.0 < fVar30) * (int)fVar30,
                               (uint)(0.0 < fVar29) * (int)fVar29);
                }
                else {
                  FUN_004b14ca((int)fVar17,0);
                }
                FUN_00516b34(param_1[8],param_1[9],param_1[10],param_1[0xb],param_1[0xc],
                             param_1[0xd],param_1[0xe],param_1[0xf]);
              }
              iVar7 = FUN_004b14fe();
              if (iVar7 == 0) {
                FUN_004b1548();
              }
              else {
                FUN_004b14ca(0,0,0x7fff);
              }
            }
            else {
              FUN_00516b34(param_1[8],param_1[9],param_1[10],param_1[0xb],param_1[0xc],param_1[0xd],
                           param_1[0xe],param_1[0xf]);
            }
LAB_00520ce6:
            if (*(char *)(*piVar3 + 0x1bd) != '\0') {
              FUN_00514846(0x388,1);
              *(undefined1 *)(*piVar3 + 0x1bc) = *(undefined1 *)(*piVar3 + 0x1bd);
              *(undefined1 *)(*piVar3 + 0x1bd) = 0;
            }
            return 0.0;
          }
          if (iVar7 == 0) {
            FUN_0051565c(1);
            fVar17 = 1.4013e-45;
          }
          else {
            if (*(int *)(iVar7 + 0x94) != 0) {
              FUN_004b146c(0);
              iVar7 = *(int *)(*piVar3 + 0x94);
              local_d0[2] = 1.12104e-44;
              local_d0[1] = *(float *)(iVar7 + 0x14);
              local_d0[0] = (float)(uint)*(byte *)(iVar7 + 0x1c);
              FUN_004b1298(2,*(undefined4 *)(iVar7 + 0xc),*(undefined2 *)(iVar7 + 0x10),
                           *(undefined2 *)(iVar7 + 0x12));
              bVar26 = *(char *)(*piVar3 + 0x7c) == '\x02' || *(char *)(*piVar3 + 0x7c) == '\x01';
              if (bVar26) {
                uVar8 = *puVar4;
                local_d0[1] = *(float *)(uVar8 + 0x10);
                local_d0[2] = 0.0;
                local_d0[0] = 1.12104e-44;
                FUN_004b1298(1,*(undefined4 *)(uVar8 + 0xc),local_d0[1],
                             *(undefined4 *)(uVar8 + 0x14));
                uVar16 = 3;
                uVar14 = 1;
              }
              else {
                uVar16 = 0xffffffff;
                uVar14 = 3;
              }
              FUN_00513924(0x400,uVar14,2,uVar16);
              FUN_005228b0(*(undefined4 *)(*piVar3 + 0x98),*(undefined4 *)(*piVar3 + 0x9c));
              FUN_00516b34(param_1[8],param_1[9],param_1[10],param_1[0xb],param_1[0xc],param_1[0xd],
                           param_1[0xe],param_1[0xf]);
              if (bVar26) {
                FUN_00514846(0x34,*(uint *)(*puVar4 + 0x10) & 0xffff | 0x8000000);
              }
              goto LAB_00521d5a;
            }
            FUN_0051565c(0x800);
            fVar17 = 2.86986e-42;
          }
        }
      }
LAB_00521c6a:
      iVar7 = *piVar3;
      *(undefined4 *)(iVar7 + 0x114) = 0;
      *(undefined4 *)(iVar7 + 0x118) = 0;
      FUN_0051565c(fVar17);
    }
  }
  iVar7 = *piVar3;
  *(undefined4 *)(iVar7 + 0x114) = 0;
  *(undefined4 *)(iVar7 + 0x118) = 0;
LAB_00520d64:
  FUN_0051565c(fVar17);
  return fVar17;
}

