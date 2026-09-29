
/* WARNING: Instruction at (ram,0x0051b23e) overlaps instruction at (ram,0x0051b23c)
    */

void FUN_0051b140(undefined4 param_1,undefined4 param_2,float param_3,int param_4)

{
  uint uVar1;
  int *piVar2;
  float *pfVar3;
  undefined4 uVar4;
  int iVar5;
  uint extraout_r1;
  uint extraout_r1_00;
  uint extraout_r1_01;
  uint extraout_r1_02;
  uint uVar6;
  byte bVar7;
  bool bVar8;
  uint in_fpscr;
  float fVar9;
  float fVar10;
  float fVar11;
  float fVar12;
  float fVar13;
  float fVar14;
  float fVar15;
  float fVar16;
  float fVar17;
  uint auStack_1d4 [4];
  float local_1c4;
  float local_1c0;
  float local_1bc [97];
  
  piVar2 = DAT_0051bf74;
  iVar5 = *DAT_0051bf74;
  fVar9 = *(float *)(iVar5 + 0x198);
  fVar13 = *(float *)(iVar5 + 400);
  uVar6 = in_fpscr & 0xfffffff | (uint)(fVar13 == fVar9) << 0x1e;
  bVar7 = 0;
  if ((byte)(uVar6 >> 0x1e) != 0) {
    param_3 = *(float *)(iVar5 + 0x194);
    uVar6 = in_fpscr & 0xfffffff | (uint)(param_3 == *(float *)(iVar5 + 0x19c)) << 0x1e;
    bVar7 = (byte)(uVar6 >> 0x1e);
  }
  if (bVar7 != 0) {
    fVar14 = *(float *)(iVar5 + 0x1a0);
    fVar16 = *(float *)(iVar5 + 0x1a8);
    uVar1 = uVar6 & 0xfffffff;
    uVar6 = uVar1 | (uint)(fVar14 == fVar16) << 0x1e;
    bVar7 = 0;
    if ((byte)(uVar6 >> 0x1e) != 0) {
      fVar16 = *(float *)(iVar5 + 0x1a4);
      uVar6 = uVar1 | (uint)(fVar16 == *(float *)(iVar5 + 0x1ac)) << 0x1e;
      bVar7 = (byte)(uVar6 >> 0x1e);
    }
    if (bVar7 != 0) {
      fVar10 = *(float *)(iVar5 + 0x2d8);
      fVar17 = (fVar13 - fVar14) / fVar10;
      fVar13 = (fVar13 + fVar14) * 0.5;
      fVar9 = (param_3 - fVar16) / fVar10;
      fVar10 = fVar10 * 0.5;
      fVar16 = (param_3 + fVar16) * 0.5;
      if (param_4 == 1) {
        iVar5 = FUN_00522f1c(fVar10);
        iVar5 = iVar5 / 2;
        fVar14 = (float)VectorSignedToFloat(iVar5,(byte)(uVar6 >> 0x16) & 3);
        fVar14 = DAT_0051b4ec / fVar14;
        fVar11 = (float)FUN_00524130(fVar14);
        fVar14 = (float)FUN_0052405c(fVar14);
        local_1c4 = fVar13 - fVar17 * fVar10;
        local_1c0 = fVar16 - fVar9 * fVar10;
        uVar6 = iVar5 - 1;
        if (1 < iVar5) {
          pfVar3 = local_1bc;
          if ((uVar6 & 3) != 0) {
            do {
              *pfVar3 = fVar13 + fVar10 * fVar17;
              pfVar3[1] = fVar16 + fVar10 * fVar9;
              fVar12 = fVar14 * fVar17;
              fVar17 = fVar11 * fVar17 - fVar14 * fVar9;
              loopEnd();
              pfVar3 = (float *)(extraout_r1 >> 9);
              fVar9 = fVar12 + fVar11 * fVar9;
            } while( true );
          }
          auStack_1d4[3] = uVar6;
          if (uVar6 >> 2 != 0) {
            do {
              *pfVar3 = fVar13 + fVar10 * fVar17;
              pfVar3[1] = fVar16 + fVar10 * fVar9;
              fVar12 = fVar11 * fVar17 - fVar14 * fVar9;
              pfVar3[2] = fVar13 + fVar10 * fVar12;
              fVar17 = fVar14 * fVar17 + fVar11 * fVar9;
              fVar15 = fVar14 * fVar12 + fVar11 * fVar17;
              fVar9 = fVar11 * fVar12 - fVar14 * fVar17;
              pfVar3[4] = fVar13 + fVar10 * fVar9;
              pfVar3[3] = fVar16 + fVar10 * fVar17;
              fVar12 = fVar14 * fVar9 + fVar11 * fVar15;
              fVar17 = fVar11 * fVar9 - fVar14 * fVar15;
              pfVar3[5] = fVar16 + fVar10 * fVar15;
              pfVar3[6] = fVar13 + fVar10 * fVar17;
              pfVar3[7] = fVar16 + fVar10 * fVar12;
              fVar9 = fVar14 * fVar17 + fVar11 * fVar12;
              fVar17 = fVar11 * fVar17 - fVar14 * fVar12;
              loopEnd();
              pfVar3 = (float *)(extraout_r1 >> 9);
            } while( true );
          }
        }
        uVar4 = FUN_0052266e(0,-(uint)((*(byte *)(*piVar2 + 0x7d) & 0x10) == 0) >> 0x1f,0,0);
        FUN_00523a34(&local_1c4,uVar6,2);
        bVar8 = -1 < (int)((uint)*(byte *)(*piVar2 + 0x7d) << 0x1b);
        FUN_0052266e(0,bVar8,bVar8,0);
      }
      else {
        iVar5 = FUN_00522f1c(fVar10);
        iVar5 = iVar5 / 2;
        fVar14 = (float)VectorSignedToFloat(iVar5,(byte)(uVar6 >> 0x16) & 3);
        fVar14 = DAT_0051b4ec / fVar14;
        fVar11 = (float)FUN_00524130(fVar14);
        fVar14 = (float)FUN_0052405c(fVar14);
        fVar14 = -fVar14;
        local_1c4 = fVar13 - fVar17 * fVar10;
        local_1c0 = fVar16 - fVar9 * fVar10;
        uVar6 = iVar5 - 1;
        if (1 < iVar5) {
          pfVar3 = local_1bc;
          if ((uVar6 & 3) != 0) {
            do {
              *pfVar3 = fVar13 + fVar10 * fVar17;
              pfVar3[1] = fVar16 + fVar10 * fVar9;
              fVar12 = fVar14 * fVar17;
              fVar17 = fVar11 * fVar17 - fVar14 * fVar9;
              loopEnd();
              pfVar3 = (float *)(extraout_r1_00 >> 9);
              fVar9 = fVar12 + fVar11 * fVar9;
            } while( true );
          }
          auStack_1d4[3] = uVar6;
          if (uVar6 >> 2 != 0) {
            do {
              *pfVar3 = fVar13 + fVar10 * fVar17;
              pfVar3[1] = fVar16 + fVar10 * fVar9;
              fVar12 = fVar11 * fVar17 - fVar14 * fVar9;
              pfVar3[2] = fVar13 + fVar10 * fVar12;
              fVar17 = fVar14 * fVar17 + fVar11 * fVar9;
              fVar15 = fVar14 * fVar12 + fVar11 * fVar17;
              fVar9 = fVar11 * fVar12 - fVar14 * fVar17;
              pfVar3[4] = fVar13 + fVar10 * fVar9;
              pfVar3[3] = fVar16 + fVar10 * fVar17;
              fVar12 = fVar14 * fVar9 + fVar11 * fVar15;
              fVar17 = fVar11 * fVar9 - fVar14 * fVar15;
              pfVar3[5] = fVar16 + fVar10 * fVar15;
              pfVar3[6] = fVar13 + fVar10 * fVar17;
              pfVar3[7] = fVar16 + fVar10 * fVar12;
              fVar9 = fVar14 * fVar17 + fVar11 * fVar12;
              fVar17 = fVar11 * fVar17 - fVar14 * fVar12;
              loopEnd();
              pfVar3 = (float *)(extraout_r1_00 >> 9);
            } while( true );
          }
        }
        uVar4 = FUN_0052266e(0,-(uint)((*(byte *)(*piVar2 + 0x7d) & 0x10) == 0) >> 0x1f,0,0);
        FUN_00523a34(&local_1c4,uVar6,2);
        bVar8 = -1 < (int)((uint)*(byte *)(*piVar2 + 0x7d) << 0x1b);
        FUN_0052266e(0,bVar8,bVar8,0);
      }
      goto LAB_0051b8ac;
    }
  }
  fVar13 = *(float *)(iVar5 + 0x2d8);
  if (param_4 == 1) {
    fVar11 = (*(float *)(iVar5 + 0x1a0) - fVar9) / fVar13;
    fVar14 = (*(float *)(iVar5 + 0x1a0) + fVar9) * 0.5;
    fVar17 = fVar13 * 0.5;
    fVar13 = (*(float *)(iVar5 + 0x1a4) - *(float *)(iVar5 + 0x19c)) / fVar13;
    fVar10 = (*(float *)(iVar5 + 0x1a4) + *(float *)(iVar5 + 0x19c)) * 0.5;
    iVar5 = FUN_00522f1c(fVar17);
    iVar5 = iVar5 / 2;
    fVar9 = (float)VectorSignedToFloat(iVar5,(byte)(uVar6 >> 0x16) & 3);
    fVar9 = DAT_0051b8ec / fVar9;
    fVar16 = (float)FUN_00524130(fVar9);
    fVar9 = (float)FUN_0052405c(fVar9);
    local_1c4 = fVar14 - fVar11 * fVar17;
    local_1c0 = fVar10 - fVar13 * fVar17;
    uVar6 = iVar5 - 1;
    if (1 < iVar5) {
      pfVar3 = local_1bc;
      if ((uVar6 & 3) != 0) {
        do {
          *pfVar3 = fVar14 + fVar17 * fVar11;
          pfVar3[1] = fVar10 + fVar17 * fVar13;
          fVar12 = fVar9 * fVar11;
          fVar11 = fVar16 * fVar11 - fVar9 * fVar13;
          loopEnd();
          pfVar3 = (float *)(extraout_r1_01 >> 9);
          fVar13 = fVar12 + fVar16 * fVar13;
        } while( true );
      }
      auStack_1d4[3] = uVar6;
      if (uVar6 >> 2 != 0) {
        do {
          *pfVar3 = fVar14 + fVar17 * fVar11;
          pfVar3[1] = fVar10 + fVar17 * fVar13;
          fVar12 = fVar16 * fVar11 - fVar9 * fVar13;
          pfVar3[2] = fVar14 + fVar17 * fVar12;
          fVar11 = fVar9 * fVar11 + fVar16 * fVar13;
          fVar15 = fVar9 * fVar12 + fVar16 * fVar11;
          fVar13 = fVar16 * fVar12 - fVar9 * fVar11;
          pfVar3[4] = fVar14 + fVar17 * fVar13;
          pfVar3[3] = fVar10 + fVar17 * fVar11;
          fVar12 = fVar9 * fVar13 + fVar16 * fVar15;
          fVar11 = fVar16 * fVar13 - fVar9 * fVar15;
          pfVar3[5] = fVar10 + fVar17 * fVar15;
          pfVar3[6] = fVar14 + fVar17 * fVar11;
          pfVar3[7] = fVar10 + fVar17 * fVar12;
          fVar13 = fVar9 * fVar11 + fVar16 * fVar12;
          fVar11 = fVar16 * fVar11 - fVar9 * fVar12;
          loopEnd();
          pfVar3 = (float *)(extraout_r1_01 >> 9);
        } while( true );
      }
    }
    uVar4 = FUN_0052266e(0,-(uint)((*(byte *)(*piVar2 + 0x7d) & 0x10) == 0) >> 0x1f,0,0);
    FUN_00523a34(&local_1c4,uVar6,2);
    bVar8 = -1 < (int)((uint)*(byte *)(*piVar2 + 0x7d) << 0x1b);
    FUN_0052266e(0,bVar8,bVar8,0);
  }
  else {
    fVar11 = (*(float *)(iVar5 + 0x150) - *(float *)(iVar5 + 0x138)) / fVar13;
    fVar14 = (*(float *)(iVar5 + 0x150) + *(float *)(iVar5 + 0x138)) * 0.5;
    fVar17 = fVar13 * 0.5;
    fVar13 = (*(float *)(iVar5 + 0x154) - *(float *)(iVar5 + 0x13c)) / fVar13;
    fVar10 = (*(float *)(iVar5 + 0x154) + *(float *)(iVar5 + 0x13c)) * 0.5;
    iVar5 = FUN_00522f1c(fVar17);
    iVar5 = iVar5 / 2;
    fVar9 = (float)VectorSignedToFloat(iVar5,(byte)(uVar6 >> 0x16) & 3);
    fVar9 = DAT_0051b8ec / fVar9;
    fVar16 = (float)FUN_00524130(fVar9);
    fVar9 = (float)FUN_0052405c(fVar9);
    fVar9 = -fVar9;
    local_1c4 = fVar14 - fVar11 * fVar17;
    local_1c0 = fVar10 - fVar13 * fVar17;
    uVar6 = iVar5 - 1;
    if (1 < iVar5) {
      pfVar3 = local_1bc;
      if ((uVar6 & 3) != 0) {
        do {
          *pfVar3 = fVar14 + fVar17 * fVar11;
          pfVar3[1] = fVar10 + fVar17 * fVar13;
          fVar12 = fVar9 * fVar11;
          fVar11 = fVar16 * fVar11 - fVar9 * fVar13;
          loopEnd();
          pfVar3 = (float *)(extraout_r1_02 >> 9);
          fVar13 = fVar12 + fVar16 * fVar13;
        } while( true );
      }
      auStack_1d4[3] = uVar6;
      if (uVar6 >> 2 != 0) {
        do {
          *pfVar3 = fVar14 + fVar17 * fVar11;
          pfVar3[1] = fVar10 + fVar17 * fVar13;
          fVar12 = fVar16 * fVar11 - fVar9 * fVar13;
          pfVar3[2] = fVar14 + fVar17 * fVar12;
          fVar11 = fVar9 * fVar11 + fVar16 * fVar13;
          fVar15 = fVar9 * fVar12 + fVar16 * fVar11;
          fVar13 = fVar16 * fVar12 - fVar9 * fVar11;
          pfVar3[4] = fVar14 + fVar17 * fVar13;
          pfVar3[3] = fVar10 + fVar17 * fVar11;
          fVar12 = fVar9 * fVar13 + fVar16 * fVar15;
          fVar11 = fVar16 * fVar13 - fVar9 * fVar15;
          pfVar3[5] = fVar10 + fVar17 * fVar15;
          pfVar3[6] = fVar14 + fVar17 * fVar11;
          pfVar3[7] = fVar10 + fVar17 * fVar12;
          fVar13 = fVar9 * fVar11 + fVar16 * fVar12;
          fVar11 = fVar16 * fVar11 - fVar9 * fVar12;
          loopEnd();
          pfVar3 = (float *)(extraout_r1_02 >> 9);
        } while( true );
      }
    }
    uVar4 = FUN_0052266e(0,-(uint)((*(byte *)(*piVar2 + 0x7d) & 0x10) == 0) >> 0x1f,0,0);
    FUN_00523a34(&local_1c4,uVar6,2);
    bVar8 = -1 < (int)((uint)*(byte *)(*piVar2 + 0x7d) << 0x1b);
    FUN_0052266e(0,bVar8,bVar8,0);
  }
LAB_0051b8ac:
  FUN_00522a24(local_1c4,local_1c0,auStack_1d4[iVar5 * 2],auStack_1d4[iVar5 * 2 + 1],
               auStack_1d4[iVar5 * 2 + 2],auStack_1d4[iVar5 * 2 + 3]);
  FUN_005226b2(uVar4);
  return;
}

