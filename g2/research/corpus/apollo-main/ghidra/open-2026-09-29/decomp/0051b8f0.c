
/* WARNING: Instruction at (ram,0x0051bbfe) overlaps instruction at (ram,0x0051bbfc)
    */

undefined4
FUN_0051b8f0(undefined4 param_1,undefined4 param_2,float param_3,undefined4 param_4,float param_5)

{
  uint uVar1;
  char cVar2;
  undefined8 uVar3;
  undefined8 uVar4;
  undefined8 uVar5;
  int *piVar6;
  undefined4 uVar7;
  float *pfVar8;
  int iVar9;
  uint extraout_r1;
  uint extraout_r1_00;
  uint uVar10;
  byte bVar11;
  bool bVar12;
  uint in_fpscr;
  float fVar13;
  float fVar14;
  float fVar15;
  float fVar16;
  float fVar17;
  float fVar18;
  float fVar19;
  float fVar20;
  float fVar21;
  uint auStack_1f4 [4];
  float local_1e4;
  float local_1e0;
  float local_1dc [97];
  
  piVar6 = DAT_0051bf74;
  iVar9 = *DAT_0051bf74;
  bVar12 = *(int *)(iVar9 + 0x110) == 0;
  cVar2 = '\0';
  if (!bVar12) {
    cVar2 = *(char *)(iVar9 + 0x2e0);
  }
  if (bVar12 || cVar2 == '\0') {
    return 0;
  }
  if (cVar2 != '\x02') {
    if (cVar2 != '\x01') {
      return 0x800000;
    }
    fVar13 = *(float *)(iVar9 + 400);
    fVar16 = *(float *)(iVar9 + 0x198);
    uVar10 = in_fpscr & 0xfffffff | (uint)(fVar13 == fVar16) << 0x1e;
    bVar11 = 0;
    if ((byte)(uVar10 >> 0x1e) != 0) {
      fVar16 = *(float *)(iVar9 + 0x194);
      uVar10 = in_fpscr & 0xfffffff | (uint)(fVar16 == *(float *)(iVar9 + 0x19c)) << 0x1e;
      bVar11 = (byte)(uVar10 >> 0x1e);
    }
    if (bVar11 != 0) {
      fVar17 = *(float *)(iVar9 + 0x1a0);
      fVar18 = *(float *)(iVar9 + 0x1a8);
      uVar1 = uVar10 & 0xfffffff;
      uVar10 = uVar1 | (uint)(fVar17 == fVar18) << 0x1e;
      bVar11 = 0;
      if ((byte)(uVar10 >> 0x1e) != 0) {
        fVar18 = *(float *)(iVar9 + 0x1a4);
        uVar10 = uVar1 | (uint)(fVar18 == *(float *)(iVar9 + 0x1ac)) << 0x1e;
        bVar11 = (byte)(uVar10 >> 0x1e);
      }
      if (bVar11 != 0) {
        fVar19 = *(float *)(iVar9 + 0x2d8);
        fVar14 = (fVar13 - fVar17) / fVar19;
        fVar17 = (fVar13 + fVar17) * 0.5;
        fVar21 = fVar19 * 0.5;
        fVar19 = (fVar16 - fVar18) / fVar19;
        fVar18 = (fVar16 + fVar18) * 0.5;
        iVar9 = FUN_00522f1c(fVar21);
        iVar9 = iVar9 / 2;
        fVar16 = (float)VectorSignedToFloat(iVar9,(byte)(uVar10 >> 0x16) & 3);
        fVar16 = DAT_0051bd1c / fVar16;
        fVar13 = (float)FUN_00524130(fVar16);
        fVar16 = (float)FUN_0052405c(fVar16);
        fVar16 = -fVar16;
        local_1e4 = fVar17 - fVar14 * fVar21;
        local_1e0 = fVar18 - fVar19 * fVar21;
        uVar10 = iVar9 - 1;
        if (1 < iVar9) {
          pfVar8 = local_1dc;
          if ((uVar10 & 3) != 0) {
            do {
              *pfVar8 = fVar17 + fVar21 * fVar14;
              pfVar8[1] = fVar18 + fVar21 * fVar19;
              fVar15 = fVar16 * fVar14;
              fVar14 = fVar13 * fVar14 - fVar16 * fVar19;
              loopEnd();
              pfVar8 = (float *)(extraout_r1 >> 9);
              fVar19 = fVar15 + fVar13 * fVar19;
            } while( true );
          }
          auStack_1f4[3] = uVar10;
          if (uVar10 >> 2 != 0) {
            do {
              *pfVar8 = fVar17 + fVar21 * fVar14;
              pfVar8[1] = fVar18 + fVar21 * fVar19;
              fVar15 = fVar13 * fVar14 - fVar16 * fVar19;
              pfVar8[2] = fVar17 + fVar21 * fVar15;
              fVar14 = fVar16 * fVar14 + fVar13 * fVar19;
              fVar20 = fVar16 * fVar15 + fVar13 * fVar14;
              fVar19 = fVar13 * fVar15 - fVar16 * fVar14;
              pfVar8[4] = fVar17 + fVar21 * fVar19;
              pfVar8[3] = fVar18 + fVar21 * fVar14;
              fVar15 = fVar16 * fVar19 + fVar13 * fVar20;
              fVar14 = fVar13 * fVar19 - fVar16 * fVar20;
              pfVar8[5] = fVar18 + fVar21 * fVar20;
              pfVar8[6] = fVar17 + fVar21 * fVar14;
              pfVar8[7] = fVar18 + fVar21 * fVar15;
              fVar19 = fVar16 * fVar14 + fVar13 * fVar15;
              fVar14 = fVar13 * fVar14 - fVar16 * fVar15;
              loopEnd();
              pfVar8 = (float *)(extraout_r1 >> 9);
            } while( true );
          }
        }
        uVar7 = FUN_0052266e(0,-(uint)((*(byte *)(*piVar6 + 0x7d) & 0x10) == 0) >> 0x1f,0,0);
        FUN_00523a34(&local_1e4,uVar10,2);
        bVar12 = -1 < (int)((uint)*(byte *)(*piVar6 + 0x7d) << 0x1b);
        FUN_0052266e(0,bVar12,bVar12,0);
        FUN_00522a24(local_1e4,local_1e0,auStack_1f4[iVar9 * 2],auStack_1f4[iVar9 * 2 + 1],
                     auStack_1f4[iVar9 * 2 + 2],auStack_1f4[iVar9 * 2 + 3]);
        goto LAB_0051b9d8;
      }
    }
    fVar16 = *(float *)(iVar9 + 0x2d8);
    fVar14 = (*(float *)(iVar9 + 0x150) - *(float *)(iVar9 + 0x138)) / fVar16;
    fVar17 = (*(float *)(iVar9 + 0x150) + *(float *)(iVar9 + 0x138)) * 0.5;
    fVar21 = fVar16 * 0.5;
    fVar16 = (*(float *)(iVar9 + 0x154) - *(float *)(iVar9 + 0x13c)) / fVar16;
    fVar19 = (*(float *)(iVar9 + 0x154) + *(float *)(iVar9 + 0x13c)) * 0.5;
    iVar9 = FUN_00522f1c(fVar21);
    iVar9 = iVar9 / 2;
    fVar13 = (float)VectorSignedToFloat(iVar9,(byte)(uVar10 >> 0x16) & 3);
    fVar13 = DAT_0051bf78 / fVar13;
    fVar18 = (float)FUN_00524130(fVar13);
    fVar13 = (float)FUN_0052405c(fVar13);
    fVar13 = -fVar13;
    local_1e4 = fVar17 - fVar14 * fVar21;
    local_1e0 = fVar19 - fVar16 * fVar21;
    uVar10 = iVar9 - 1;
    if (1 < iVar9) {
      pfVar8 = local_1dc;
      if ((uVar10 & 3) != 0) {
        do {
          *pfVar8 = fVar17 + fVar21 * fVar14;
          pfVar8[1] = fVar19 + fVar21 * fVar16;
          fVar15 = fVar13 * fVar14;
          fVar14 = fVar18 * fVar14 - fVar13 * fVar16;
          loopEnd();
          pfVar8 = (float *)(extraout_r1_00 >> 9);
          fVar16 = fVar15 + fVar18 * fVar16;
        } while( true );
      }
      auStack_1f4[3] = uVar10;
      if (uVar10 >> 2 != 0) {
        do {
          *pfVar8 = fVar17 + fVar21 * fVar14;
          pfVar8[1] = fVar19 + fVar21 * fVar16;
          fVar15 = fVar18 * fVar14 - fVar13 * fVar16;
          pfVar8[2] = fVar17 + fVar21 * fVar15;
          fVar14 = fVar13 * fVar14 + fVar18 * fVar16;
          fVar20 = fVar13 * fVar15 + fVar18 * fVar14;
          fVar16 = fVar18 * fVar15 - fVar13 * fVar14;
          pfVar8[4] = fVar17 + fVar21 * fVar16;
          pfVar8[3] = fVar19 + fVar21 * fVar14;
          fVar15 = fVar13 * fVar16 + fVar18 * fVar20;
          fVar14 = fVar18 * fVar16 - fVar13 * fVar20;
          pfVar8[5] = fVar19 + fVar21 * fVar20;
          pfVar8[6] = fVar17 + fVar21 * fVar14;
          pfVar8[7] = fVar19 + fVar21 * fVar15;
          fVar16 = fVar13 * fVar14 + fVar18 * fVar15;
          fVar14 = fVar18 * fVar14 - fVar13 * fVar15;
          loopEnd();
          pfVar8 = (float *)(extraout_r1_00 >> 9);
        } while( true );
      }
    }
    uVar7 = FUN_0052266e(0,-(uint)((*(byte *)(*piVar6 + 0x7d) & 0x10) == 0) >> 0x1f,0,0);
    FUN_00523a34(&local_1e4,uVar10,2);
    bVar12 = -1 < (int)((uint)*(byte *)(*piVar6 + 0x7d) << 0x1b);
    FUN_0052266e(0,bVar12,bVar12,0);
    FUN_00522a24(local_1e4,local_1e0,auStack_1f4[iVar9 * 2],auStack_1f4[iVar9 * 2 + 1],
                 auStack_1f4[iVar9 * 2 + 2],auStack_1f4[iVar9 * 2 + 3]);
    goto LAB_0051b9d8;
  }
  fVar13 = *(float *)(iVar9 + 400);
  fVar16 = *(float *)(iVar9 + 0x198);
  bVar12 = fVar13 == fVar16;
  if (bVar12) {
    fVar16 = *(float *)(iVar9 + 0x194);
    param_3 = *(float *)(iVar9 + 0x19c);
  }
  if (bVar12 && (bVar12 && fVar16 == param_3)) {
    fVar17 = *(float *)(iVar9 + 0x1a0);
    fVar18 = *(float *)(iVar9 + 0x1a8);
    bVar12 = fVar17 == fVar18;
    if (bVar12) {
      fVar18 = *(float *)(iVar9 + 0x1a4);
      param_5 = *(float *)(iVar9 + 0x1ac);
    }
    if (bVar12 && (bVar12 && fVar18 == param_5)) {
      fVar19 = *(float *)(iVar9 + 300) * -0.5;
      bVar12 = -1 < (int)((uint)*(byte *)(iVar9 + 0x7d) << 0x1b);
      uVar7 = FUN_0052266e(bVar12,0,bVar12,bVar12);
      FUN_00516b34(fVar19 + fVar13,fVar16,fVar13,fVar16,fVar17,fVar18,fVar19 + fVar17,fVar18);
      goto LAB_0051b9d8;
    }
  }
  fVar16 = 0.5;
  fVar17 = *(float *)(iVar9 + 300) * 0.5;
  bVar12 = *(float *)(iVar9 + 0x140) <= *(float *)(iVar9 + 0x138);
  uVar3 = *(undefined8 *)(iVar9 + 0x138);
  uVar4 = *(undefined8 *)(iVar9 + 0x150);
  fVar13 = *(float *)(iVar9 + 0x150);
  uVar5 = *(undefined8 *)(iVar9 + 0x138);
  fVar18 = *(float *)(iVar9 + 0x154);
  if (!bVar12) {
    fVar16 = *(float *)(iVar9 + 0x148);
  }
  fVar14 = (float)uVar5;
  fVar20 = fVar13 - fVar14;
  fVar15 = (float)((ulonglong)uVar5 >> 0x20);
  fVar21 = fVar18 - fVar15;
  fVar19 = (float)FUN_00524218(fVar20 * fVar20 + fVar21 * fVar21);
  fVar21 = -(fVar21 / fVar19);
  if (bVar12 || (bVar12 || fVar16 <= fVar13)) {
    if (fVar21 <= 0.0) goto LAB_0051baa6;
LAB_0051ba64:
    fVar13 = fVar17 * fVar21 + fVar13;
    fVar16 = fVar17 * (fVar20 / fVar19);
    fVar14 = fVar17 * fVar21 + fVar14;
    fVar18 = fVar16 + fVar18;
    fVar16 = fVar16 + fVar15;
  }
  else {
    if (fVar21 <= 0.0) goto LAB_0051ba64;
LAB_0051baa6:
    fVar13 = fVar13 - fVar17 * fVar21;
    fVar16 = fVar17 * (fVar20 / fVar19);
    fVar14 = fVar14 - fVar17 * fVar21;
    fVar18 = fVar18 - fVar16;
    fVar16 = fVar15 - fVar16;
  }
  bVar12 = -1 < (int)((uint)*(byte *)(*piVar6 + 0x7d) << 0x1b);
  uVar7 = FUN_0052266e(0,bVar12,bVar12,bVar12);
  FUN_00516b34((int)uVar3,(int)((ulonglong)uVar3 >> 0x20),(int)uVar4,(int)((ulonglong)uVar4 >> 0x20)
               ,fVar13,fVar18,fVar14,fVar16);
  if ((int)((uint)*(byte *)(*piVar6 + 0x7d) << 0x1b) < 0) {
    return 0;
  }
LAB_0051b9d8:
  FUN_005226b2(uVar7);
  return 0;
}

