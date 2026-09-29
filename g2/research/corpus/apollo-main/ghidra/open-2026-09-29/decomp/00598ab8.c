
void FUN_00598ab8(int param_1,int param_2,int param_3,float *param_4,float *param_5,float *param_6)

{
  float *pfVar1;
  float *pfVar2;
  float *pfVar3;
  float *pfVar4;
  float *pfVar5;
  float *pfVar6;
  int iVar7;
  int *piVar8;
  int iVar9;
  float *pfVar10;
  float *pfVar11;
  int iVar12;
  float *pfVar13;
  float *pfVar14;
  int iVar15;
  float *pfVar16;
  uint in_fpscr;
  float fVar17;
  float fVar18;
  float fVar19;
  float fVar20;
  float fVar21;
  float fVar22;
  float fVar23;
  float fVar24;
  float local_f28 [961];
  
  iVar12 = *(int *)(DAT_00598ddc + param_2 * 4);
  iVar15 = (param_1 + 1) * *(int *)(DAT_00598ddc + param_3 * 4);
  iVar9 = iVar12 * (param_1 + 1);
  piVar8 = *(int **)(DAT_00598de0 + param_1 * 0x1c + param_2 * 4);
  pfVar5 = local_f28;
  if (param_1 == 2) {
    iVar12 = *(int *)(DAT_00598de4 + param_2 * 4);
  }
  pfVar11 = *(float **)(DAT_00598de8 + param_1 * 0x1c + param_2 * 4);
  pfVar4 = pfVar11 + iVar9;
  iVar12 = iVar12 + iVar9 >> 1;
  pfVar6 = pfVar4 + iVar12;
  pfVar2 = param_4 + (iVar9 - iVar12);
  pfVar14 = param_5 + iVar12;
  pfVar1 = pfVar5 + iVar9 / 2;
  pfVar13 = pfVar4;
  pfVar3 = pfVar2;
  pfVar16 = pfVar1;
  while (param_4 < pfVar2) {
    pfVar1[-1] = *param_5 * *pfVar11 - pfVar2[-1] * pfVar4[-1];
    fVar17 = *pfVar3;
    *param_5 = fVar17;
    *pfVar16 = fVar17 * *pfVar13;
    pfVar2 = pfVar2 + -2;
    pfVar4 = pfVar4 + -2;
    pfVar1 = pfVar1 + -2;
    *pfVar1 = param_5[1] * pfVar11[1] - *pfVar2 * *pfVar4;
    pfVar11 = pfVar11 + 2;
    fVar17 = pfVar3[1];
    param_5[1] = fVar17;
    pfVar16[1] = fVar17 * pfVar13[1];
    pfVar3 = pfVar3 + 2;
    param_5 = param_5 + 2;
    pfVar13 = pfVar13 + 2;
    pfVar16 = pfVar16 + 2;
  }
  pfVar2 = pfVar2 + iVar9;
  if (pfVar3 < pfVar2) {
    do {
      pfVar1[-1] = *param_5 * *pfVar11 - pfVar14[-1] * pfVar4[-1];
      fVar18 = *pfVar3;
      *param_5 = fVar18;
      fVar17 = pfVar2[-1];
      pfVar2 = pfVar2 + -2;
      pfVar4 = pfVar4 + -2;
      pfVar10 = pfVar14 + -1;
      pfVar14 = pfVar14 + -2;
      *pfVar10 = fVar17;
      *pfVar16 = fVar18 * *pfVar13 + fVar17 * pfVar6[-1];
      pfVar1 = pfVar1 + -2;
      pfVar6 = pfVar6 + -2;
      *pfVar1 = param_5[1] * pfVar11[1] - *pfVar14 * *pfVar4;
      fVar17 = pfVar3[1];
      pfVar11 = pfVar11 + 2;
      pfVar3 = pfVar3 + 2;
      param_5[1] = fVar17;
      fVar18 = *pfVar2;
      *pfVar14 = fVar18;
      pfVar16[1] = fVar17 * pfVar13[1] + fVar18 * *pfVar6;
      param_5 = param_5 + 2;
      pfVar13 = pfVar13 + 2;
      pfVar16 = pfVar16 + 2;
    } while (pfVar3 < pfVar2);
  }
  iVar12 = *piVar8;
  pfVar3 = (float *)piVar8[1];
  pfVar2 = pfVar5 + iVar12 * 2;
  pfVar11 = local_f28;
  pfVar4 = pfVar3 + iVar12 * 2;
  pfVar13 = local_f28 + iVar12 * 2;
  if (pfVar5 < pfVar2) {
    do {
      fVar17 = pfVar2[-1];
      fVar22 = *pfVar5;
      pfVar2 = pfVar2 + -2;
      fVar24 = pfVar5[1];
      fVar18 = *pfVar3;
      fVar19 = pfVar3[1];
      fVar20 = pfVar4[-2];
      fVar21 = pfVar4[-1];
      fVar23 = *pfVar2;
      *pfVar11 = fVar22 * fVar19 - fVar17 * fVar18;
      pfVar11[1] = fVar22 * fVar18 + fVar17 * fVar19;
      pfVar3 = pfVar3 + 2;
      pfVar5 = pfVar5 + 2;
      pfVar11 = pfVar11 + 2;
      pfVar13[-2] = fVar24 * fVar20 - fVar23 * fVar21;
      pfVar13[-1] = -(fVar24 * fVar21) - fVar23 * fVar20;
      pfVar4 = pfVar4 + -2;
      pfVar13 = pfVar13 + -2;
    } while (pfVar5 < pfVar2);
  }
  iVar12 = FUN_0059845c(local_f28,iVar9 / 2,local_f28,param_6);
  iVar7 = *piVar8 >> 1;
  pfVar5 = param_6 + *piVar8;
  pfVar4 = (float *)(piVar8[1] + iVar7 * 8);
  pfVar2 = (float *)(iVar12 + iVar7 * 8);
  pfVar11 = pfVar5;
  pfVar13 = pfVar4;
  pfVar3 = pfVar2;
  while (param_6 < pfVar5) {
    fVar18 = pfVar13[-1];
    fVar20 = pfVar3[-2];
    fVar17 = pfVar3[-1];
    fVar19 = pfVar13[-2];
    fVar22 = pfVar4[1];
    fVar24 = *pfVar2;
    fVar21 = pfVar2[1];
    fVar23 = *pfVar4;
    pfVar1 = pfVar5 + -1;
    *pfVar11 = fVar21 * fVar22 + fVar24 * fVar23;
    pfVar11[1] = fVar20 * fVar18 - fVar17 * fVar19;
    pfVar5 = pfVar5 + -2;
    pfVar11 = pfVar11 + 2;
    *pfVar1 = fVar24 * fVar22 - fVar21 * fVar23;
    pfVar2 = pfVar2 + 2;
    pfVar4 = pfVar4 + 2;
    *pfVar5 = fVar17 * fVar18 + fVar20 * fVar19;
    pfVar13 = pfVar13 + -2;
    pfVar3 = pfVar3 + -2;
  }
  if (iVar9 != iVar15) {
    fVar17 = (float)VectorSignedToFloat(iVar15,(byte)(in_fpscr >> 0x16) & 3);
    fVar18 = (float)VectorSignedToFloat(iVar9,(byte)(in_fpscr >> 0x16) & 3);
    FUN_004397a8(fVar17 / fVar18);
    FUN_0059898c(param_6,iVar15);
  }
  return;
}

