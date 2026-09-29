
/* WARNING: Instruction at (ram,0x0051c276) overlaps instruction at (ram,0x0051c274)
    */

undefined4
FUN_0051bf7c(undefined4 param_1,float param_2,undefined4 param_3,float param_4,float param_5)

{
  uint uVar1;
  char cVar2;
  undefined8 uVar3;
  undefined8 uVar4;
  int *piVar5;
  undefined4 uVar6;
  float *pfVar7;
  int iVar8;
  uint extraout_r1;
  uint extraout_r1_00;
  uint uVar9;
  byte bVar10;
  bool bVar11;
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
  
  piVar5 = DAT_0051c5e8;
  iVar8 = *DAT_0051c5e8;
  bVar12 = *(int *)(iVar8 + 0x110) == 0;
  cVar2 = '\0';
  if (!bVar12) {
    cVar2 = *(char *)(iVar8 + 0x2e1);
  }
  if (bVar12 || cVar2 == '\0') {
    return 0;
  }
  if (cVar2 != '\x02') {
    if (cVar2 != '\x01') {
      return 0x800000;
    }
    fVar19 = *(float *)(iVar8 + 0x198);
    fVar18 = *(float *)(iVar8 + 400);
    uVar9 = in_fpscr & 0xfffffff | (uint)(fVar18 == fVar19) << 0x1e;
    fVar13 = *(float *)(iVar8 + 0x19c);
    bVar10 = 0;
    if ((byte)(uVar9 >> 0x1e) != 0) {
      param_4 = *(float *)(iVar8 + 0x194);
      uVar9 = in_fpscr & 0xfffffff | (uint)(param_4 == fVar13) << 0x1e;
      bVar10 = (byte)(uVar9 >> 0x1e);
    }
    if (bVar10 != 0) {
      fVar15 = *(float *)(iVar8 + 0x1a0);
      fVar16 = *(float *)(iVar8 + 0x1a8);
      uVar1 = uVar9 & 0xfffffff;
      uVar9 = uVar1 | (uint)(fVar15 == fVar16) << 0x1e;
      bVar10 = 0;
      if ((byte)(uVar9 >> 0x1e) != 0) {
        fVar16 = *(float *)(iVar8 + 0x1a4);
        uVar9 = uVar1 | (uint)(fVar16 == *(float *)(iVar8 + 0x1ac)) << 0x1e;
        bVar10 = (byte)(uVar9 >> 0x1e);
      }
      if (bVar10 != 0) {
        fVar13 = *(float *)(iVar8 + 0x2d8);
        fVar21 = (fVar18 - fVar15) / fVar13;
        fVar15 = (fVar18 + fVar15) * 0.5;
        fVar14 = fVar13 * 0.5;
        fVar13 = (param_4 - fVar16) / fVar13;
        fVar16 = (param_4 + fVar16) * 0.5;
        iVar8 = FUN_00522f1c(fVar14);
        iVar8 = iVar8 / 2;
        fVar19 = (float)VectorSignedToFloat(iVar8,(byte)(uVar9 >> 0x16) & 3);
        fVar19 = DAT_0051c394 / fVar19;
        fVar18 = (float)FUN_00524130(fVar19);
        fVar19 = (float)FUN_0052405c(fVar19);
        local_1e4 = fVar15 - fVar21 * fVar14;
        local_1e0 = fVar16 - fVar13 * fVar14;
        uVar9 = iVar8 - 1;
        if (1 < iVar8) {
          pfVar7 = local_1dc;
          if ((uVar9 & 3) != 0) {
            do {
              *pfVar7 = fVar15 + fVar14 * fVar21;
              pfVar7[1] = fVar16 + fVar14 * fVar13;
              fVar20 = fVar19 * fVar21;
              fVar21 = fVar18 * fVar21 - fVar19 * fVar13;
              loopEnd();
              pfVar7 = (float *)(extraout_r1 >> 9);
              fVar13 = fVar20 + fVar18 * fVar13;
            } while( true );
          }
          auStack_1f4[3] = uVar9;
          if (uVar9 >> 2 != 0) {
            do {
              *pfVar7 = fVar15 + fVar14 * fVar21;
              pfVar7[1] = fVar16 + fVar14 * fVar13;
              fVar20 = fVar18 * fVar21 - fVar19 * fVar13;
              pfVar7[2] = fVar15 + fVar14 * fVar20;
              fVar21 = fVar19 * fVar21 + fVar18 * fVar13;
              fVar17 = fVar19 * fVar20 + fVar18 * fVar21;
              fVar13 = fVar18 * fVar20 - fVar19 * fVar21;
              pfVar7[4] = fVar15 + fVar14 * fVar13;
              pfVar7[3] = fVar16 + fVar14 * fVar21;
              fVar20 = fVar19 * fVar13 + fVar18 * fVar17;
              fVar21 = fVar18 * fVar13 - fVar19 * fVar17;
              pfVar7[5] = fVar16 + fVar14 * fVar17;
              pfVar7[6] = fVar15 + fVar14 * fVar21;
              pfVar7[7] = fVar16 + fVar14 * fVar20;
              fVar13 = fVar19 * fVar21 + fVar18 * fVar20;
              fVar21 = fVar18 * fVar21 - fVar19 * fVar20;
              loopEnd();
              pfVar7 = (float *)(extraout_r1 >> 9);
            } while( true );
          }
        }
        uVar6 = FUN_0052266e(0,-(uint)((*(byte *)(*piVar5 + 0x7d) & 0x10) == 0) >> 0x1f,0,0);
        FUN_00523a34(&local_1e4,uVar9,2);
        bVar12 = -1 < (int)((uint)*(byte *)(*piVar5 + 0x7d) << 0x1b);
        FUN_0052266e(0,bVar12,bVar12,0);
        FUN_00522a24(local_1e4,local_1e0,auStack_1f4[iVar8 * 2],auStack_1f4[iVar8 * 2 + 1],
                     auStack_1f4[iVar8 * 2 + 2],auStack_1f4[iVar8 * 2 + 3]);
        goto LAB_0051c05e;
      }
    }
    fVar16 = *(float *)(iVar8 + 0x2d8);
    fVar15 = (*(float *)(iVar8 + 0x1a0) + fVar19) * 0.5;
    fVar21 = fVar16 * 0.5;
    fVar18 = (*(float *)(iVar8 + 0x1a4) - fVar13) / fVar16;
    fVar14 = (*(float *)(iVar8 + 0x1a4) + fVar13) * 0.5;
    fVar16 = (*(float *)(iVar8 + 0x1a0) - fVar19) / fVar16;
    iVar8 = FUN_00522f1c(fVar21);
    iVar8 = iVar8 / 2;
    fVar13 = (float)VectorSignedToFloat(iVar8,(byte)(uVar9 >> 0x16) & 3);
    fVar13 = DAT_0051c5e4 / fVar13;
    fVar19 = (float)FUN_00524130(fVar13);
    fVar13 = (float)FUN_0052405c(fVar13);
    local_1e4 = fVar15 - fVar16 * fVar21;
    local_1e0 = fVar14 - fVar18 * fVar21;
    uVar9 = iVar8 - 1;
    if (1 < iVar8) {
      pfVar7 = local_1dc;
      if ((uVar9 & 3) != 0) {
        do {
          *pfVar7 = fVar15 + fVar21 * fVar16;
          pfVar7[1] = fVar14 + fVar21 * fVar18;
          fVar20 = fVar13 * fVar16;
          fVar16 = fVar19 * fVar16 - fVar13 * fVar18;
          loopEnd();
          pfVar7 = (float *)(extraout_r1_00 >> 9);
          fVar18 = fVar20 + fVar19 * fVar18;
        } while( true );
      }
      auStack_1f4[3] = uVar9;
      if (uVar9 >> 2 != 0) {
        do {
          *pfVar7 = fVar15 + fVar21 * fVar16;
          pfVar7[1] = fVar14 + fVar21 * fVar18;
          fVar20 = fVar19 * fVar16 - fVar13 * fVar18;
          pfVar7[2] = fVar15 + fVar21 * fVar20;
          fVar16 = fVar13 * fVar16 + fVar19 * fVar18;
          fVar17 = fVar13 * fVar20 + fVar19 * fVar16;
          fVar18 = fVar19 * fVar20 - fVar13 * fVar16;
          pfVar7[4] = fVar15 + fVar21 * fVar18;
          pfVar7[3] = fVar14 + fVar21 * fVar16;
          fVar20 = fVar13 * fVar18 + fVar19 * fVar17;
          fVar16 = fVar19 * fVar18 - fVar13 * fVar17;
          pfVar7[5] = fVar14 + fVar21 * fVar17;
          pfVar7[6] = fVar15 + fVar21 * fVar16;
          pfVar7[7] = fVar14 + fVar21 * fVar20;
          fVar18 = fVar13 * fVar16 + fVar19 * fVar20;
          fVar16 = fVar19 * fVar16 - fVar13 * fVar20;
          loopEnd();
          pfVar7 = (float *)(extraout_r1_00 >> 9);
        } while( true );
      }
    }
    uVar6 = FUN_0052266e(0,-(uint)((*(byte *)(*piVar5 + 0x7d) & 0x10) == 0) >> 0x1f,0,0);
    FUN_00523a34(&local_1e4,uVar9,2);
    bVar12 = -1 < (int)((uint)*(byte *)(*piVar5 + 0x7d) << 0x1b);
    FUN_0052266e(0,bVar12,bVar12,0);
    FUN_00522a24(local_1e4,local_1e0,auStack_1f4[iVar8 * 2],auStack_1f4[iVar8 * 2 + 1],
                 auStack_1f4[iVar8 * 2 + 2],auStack_1f4[iVar8 * 2 + 3]);
    goto LAB_0051c05e;
  }
  fVar19 = *(float *)(iVar8 + 0x198);
  fVar13 = *(float *)(iVar8 + 400);
  bVar12 = fVar13 == fVar19;
  fVar18 = *(float *)(iVar8 + 0x19c);
  if (bVar12) {
    param_2 = *(float *)(iVar8 + 0x194);
  }
  if (bVar12 && (bVar12 && param_2 == fVar18)) {
    fVar15 = *(float *)(iVar8 + 0x1a0);
    fVar16 = *(float *)(iVar8 + 0x1a8);
    bVar12 = fVar15 == fVar16;
    if (bVar12) {
      fVar16 = *(float *)(iVar8 + 0x1a4);
      param_5 = *(float *)(iVar8 + 0x1ac);
    }
    if (bVar12 && (bVar12 && fVar16 == param_5)) {
      fVar19 = *(float *)(iVar8 + 300) * 0.5;
      bVar12 = -1 < (int)((uint)*(byte *)(iVar8 + 0x7d) << 0x1b);
      uVar6 = FUN_0052266e(bVar12,bVar12,bVar12,0);
      FUN_00516b34(fVar13,param_2,fVar19 + fVar13,param_2,fVar19 + fVar15,fVar16,fVar15,fVar16);
      goto LAB_0051c05e;
    }
  }
  bVar12 = fVar13 < fVar19;
  bVar11 = NAN(fVar13) || NAN(fVar19);
  uVar3 = *(undefined8 *)(iVar8 + 0x198);
  uVar4 = *(undefined8 *)(iVar8 + 0x1a0);
  fVar15 = *(float *)(iVar8 + 300) * 0.5;
  fVar13 = *(float *)(iVar8 + 0x1a0);
  fVar16 = *(float *)(iVar8 + 0x1a4);
  if (!bVar12) {
    bVar12 = *(float *)(iVar8 + 0x1a8) < fVar13;
    bVar11 = NAN(*(float *)(iVar8 + 0x1a8)) || NAN(fVar13);
  }
  fVar20 = fVar13 - fVar19;
  fVar21 = fVar16 - fVar18;
  fVar14 = (float)FUN_00524218(fVar20 * fVar20 + fVar21 * fVar21);
  fVar21 = -(fVar21 / fVar14);
  if (bVar12 == bVar11) {
    if (fVar21 <= 0.0) goto LAB_0051c0de;
LAB_0051c120:
    fVar13 = fVar13 - fVar15 * fVar21;
    fVar14 = fVar15 * (fVar20 / fVar14);
    fVar19 = fVar19 - fVar15 * fVar21;
    fVar16 = fVar16 - fVar14;
    fVar14 = fVar18 - fVar14;
  }
  else {
    if (fVar21 <= 0.0) goto LAB_0051c120;
LAB_0051c0de:
    fVar13 = fVar15 * fVar21 + fVar13;
    fVar14 = fVar15 * (fVar20 / fVar14);
    fVar19 = fVar15 * fVar21 + fVar19;
    fVar16 = fVar14 + fVar16;
    fVar14 = fVar14 + fVar18;
  }
  bVar12 = -1 < (int)((uint)*(byte *)(*piVar5 + 0x7d) << 0x1b);
  uVar6 = FUN_0052266e(0,bVar12,bVar12,bVar12);
  FUN_00516b34((int)uVar3,(int)((ulonglong)uVar3 >> 0x20),(int)uVar4,(int)((ulonglong)uVar4 >> 0x20)
               ,fVar13,fVar16,fVar19,fVar14);
  if ((int)((uint)*(byte *)(*piVar5 + 0x7d) << 0x1b) < 0) {
    return 0;
  }
LAB_0051c05e:
  FUN_005226b2(uVar6);
  return 0;
}

