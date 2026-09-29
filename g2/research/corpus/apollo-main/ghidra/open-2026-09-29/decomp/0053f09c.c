
/* WARNING: Heritage AFTER dead removal. Example location: s1 : 0x0053f10e */
/* WARNING: Restarted to delay deadcode elimination for space: register */

undefined4 FUN_0053f09c(int param_1,int param_2,int *param_3,undefined4 param_4)

{
  float fVar1;
  char cVar2;
  int iVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  undefined4 uVar6;
  undefined4 uVar7;
  bool bVar8;
  uint uVar9;
  int iVar10;
  int iVar11;
  uint in_fpscr;
  uint uVar12;
  uint uVar13;
  float fVar14;
  float fVar15;
  float fVar16;
  undefined4 in_s3;
  float fVar17;
  float fVar18;
  float fVar19;
  float fVar20;
  undefined4 local_d8;
  uint local_d4;
  int local_d0;
  int local_cc;
  int local_c8;
  int local_c4;
  undefined1 auStack_c0 [16];
  undefined1 auStack_b0 [16];
  undefined1 auStack_a0 [44];
  int local_74;
  
  if (((2 < *(byte *)(param_2 + 0x3c)) && (*(int *)(param_2 + 0x20) != 0)) &&
     (uVar9 = in_fpscr & 0xfffffff |
              (uint)((float)*(undefined8 *)(param_2 + 0x24) ==
                    (float)((ulonglong)*(undefined8 *)(param_2 + 0x24) >> 0x20)) << 0x1e,
     (byte)(uVar9 >> 0x1e) == 0)) {
    local_d4 = *(uint *)(param_2 + 0x20);
    if ((int)(uint)*(ushort *)(param_2 + 0x34) < (int)local_d4) {
      local_d4 = (uint)*(ushort *)(param_2 + 0x34);
    }
    FUN_00439c04(auStack_b0,param_3,0x10);
    iVar3 = FUN_00450bcc(auStack_c0,auStack_b0,param_1 + 0x38);
    if (iVar3 != 0) {
      fVar14 = *(float *)(param_2 + 0x24);
      fVar17 = *(float *)(param_2 + 0x28);
      FUN_0057dc40(SUB84((double)fVar14,0),(int)((ulonglong)(double)fVar14 >> 0x20),
                   (int)DAT_0053f3dc);
      uVar9 = uVar9 & 0xfffffff | (uint)(fVar14 < 0.0) << 0x1f | (uint)(fVar14 == 0.0) << 0x1e |
              (uint)(0.0 <= fVar14) << 0x1d;
      if ((int)uVar9 < 0) {
        fVar14 = fVar14 + DAT_0053f3d8;
      }
      uVar7 = (undefined4)((ulonglong)(double)fVar17 >> 0x20);
      fVar15 = SUB84((double)fVar17,0);
      FUN_0057dc40(fVar15,uVar7,(int)DAT_0053f3dc);
      if ((int)(uVar9 & 0xfffffff | (uint)(fVar17 < 0.0) << 0x1f | (uint)(fVar17 == 0.0) << 0x1e |
               (uint)(0.0 <= fVar17) << 0x1d) < 0) {
        fVar17 = fVar17 + DAT_0053f3d8;
      }
      uVar9 = uVar9 & 0xfffffff | (uint)(fVar14 < fVar17) << 0x1f;
      uVar12 = uVar9 | (uint)(NAN(fVar14) || NAN(fVar17)) << 0x1c;
      if ((byte)(uVar9 >> 0x1f) == ((byte)(uVar12 >> 0x1c) & 1)) {
        fVar17 = fVar17 + DAT_0053f3d8;
      }
      iVar3 = *(int *)(param_1 + 0x48);
      FUN_00439be4(&local_d8,param_2 + 0x1c,3);
      uVar4 = FUN_004b06a8(local_d8,*(undefined1 *)(param_2 + 0x3c));
      bVar8 = false;
      uVar9 = uVar12 & 0xfffffff | (uint)(fVar17 - fVar14 < DAT_0053f3e4) << 0x1f;
      uVar13 = uVar9 | (uint)(NAN(fVar17 - fVar14) || NAN(DAT_0053f3e4)) << 0x1c;
      if ((byte)(uVar9 >> 0x1f) == ((byte)(uVar13 >> 0x1c) & 1)) {
        fVar16 = fVar17 - fVar14;
        uVar13 = uVar12 & 0xfffffff | (uint)(fVar16 < DAT_0053f3e8) << 0x1f |
                 (uint)(fVar16 == DAT_0053f3e8) << 0x1e | (uint)(DAT_0053f3e8 <= fVar16) << 0x1d;
        if ((int)uVar13 < 0) {
          bVar8 = true;
          uVar5 = FUN_004515a4(param_3);
          uVar6 = FUN_00451598(param_3);
          FUN_004b1516(*param_3 - *(int *)(iVar3 + 4),param_3[1] - *(int *)(iVar3 + 8),uVar6,uVar5);
        }
      }
      uVar9 = DAT_0053f3ec;
      if (*(char *)(iVar3 + 0x14) != '\x10') {
        uVar9 = 0x504;
      }
      iVar10 = *(int *)(param_2 + 0x2c) - *(int *)(iVar3 + 4);
      iVar11 = *(int *)(param_2 + 0x30) - *(int *)(iVar3 + 8);
      iVar3 = 0;
      if ((*(int *)(param_2 + 0x38) != 0) &&
         (cVar2 = FUN_004b0f50(*(undefined4 *)(param_2 + 0x38),0,auStack_a0,0), iVar3 = local_74,
         cVar2 != '\x01')) {
        local_d8 = DAT_0053f3f0;
        FUN_0044d25c(3,DAT_0053f3f8,0x6e,DAT_0053f3f4);
        iVar3 = 0;
      }
      if (iVar3 == 0) {
        FUN_004b0730(*(undefined4 *)(param_1 + 0x4c),uVar9);
        FUN_00522a16(uVar4);
      }
      else {
        uVar12 = FUN_004b0d38(iVar3,uVar4,8);
        FUN_004b0748(*(undefined4 *)(param_1 + 0x4c),uVar12 | uVar9);
        local_d0 = iVar10 - (*(uint *)(iVar3 + 4) & 0xffff) / 2;
        local_cc = iVar11 - *(uint *)(iVar3 + 4) / 0x20000;
        local_c8 = local_d0 + (*(uint *)(iVar3 + 4) & 0xffff) + -1;
        local_c4 = local_cc + (*(uint *)(iVar3 + 4) >> 0x10) + -1;
        VectorSignedToFloat(local_cc,(byte)(uVar13 >> 0x16) & 3);
        uVar4 = VectorSignedToFloat(local_d0,(byte)(uVar13 >> 0x16) & 3);
        FUN_005228b0(uVar4);
      }
      fVar16 = (float)VectorSignedToFloat(local_d4,(byte)(uVar13 >> 0x16) & 3);
      fVar18 = (float)VectorUnsignedToFloat
                                ((uint)*(ushort *)(param_2 + 0x34),(byte)(uVar13 >> 0x16) & 3);
      fVar18 = fVar18 + fVar16 * -0.5;
      if ((int)((uint)*(byte *)(param_2 + 0x3d) << 0x1f) < 0) {
        VectorSignedToFloat(iVar11,(byte)(uVar13 >> 0x16) & 3);
        uVar4 = VectorSignedToFloat(iVar10,(byte)(uVar13 >> 0x16) & 3);
        FUN_0052330c(uVar4,uVar7,fVar18,in_s3,fVar14,fVar17);
        fVar19 = (float)VectorSignedToFloat(iVar10,(byte)(uVar13 >> 0x16) & 3);
        FUN_00524130(fVar14);
        VectorSignedToFloat(iVar11,(byte)(uVar13 >> 0x16) & 3);
        FUN_0052405c(fVar14);
        fVar20 = (float)VectorSignedToFloat(iVar10,(byte)(uVar13 >> 0x16) & 3);
        FUN_00524130(fVar17);
        VectorSignedToFloat(iVar11,(byte)(uVar13 >> 0x16) & 3);
        FUN_0052405c(fVar17);
        fVar1 = DAT_0053f3fc;
        FUN_0052330c(fVar19 + fVar15 * fVar18,uVar7,fVar16 * 0.5 * 0.5,in_s3,fVar14 + DAT_0053f3fc,
                     fVar14 + DAT_0053f3d8);
        FUN_0052330c(fVar20 + fVar15 * fVar18,uVar7,fVar16 * 0.5 * 0.5,in_s3,fVar17,fVar17 + fVar1);
      }
      else {
        VectorSignedToFloat(iVar11,(byte)(uVar13 >> 0x16) & 3);
        uVar4 = VectorSignedToFloat(iVar10,(byte)(uVar13 >> 0x16) & 3);
        FUN_00523674(uVar4,uVar7,fVar18,in_s3,fVar14,fVar17,0x5000000);
      }
      if (iVar3 != 0) {
        uVar7 = FUN_005144fa();
        FUN_00514cf2(uVar7);
        FUN_00514d00(uVar7);
        FUN_00514384(uVar7);
        FUN_0048908c(auStack_a0);
      }
      if (bVar8) {
        FUN_004b1548();
      }
    }
  }
  return param_4;
}

