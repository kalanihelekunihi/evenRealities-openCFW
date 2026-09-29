
void FUN_005619f2(float *param_1,float *param_2)

{
  float fVar1;
  float fVar2;
  float fVar3;
  float fVar4;
  float fVar5;
  float fVar6;
  float fVar7;
  float fVar8;
  float fVar9;
  float fVar10;
  float fVar11;
  float fVar12;
  float fVar13;
  float fVar14;
  float fVar15;
  float fVar16;
  float fVar17;
  float fVar18;
  
  fVar5 = param_2[1];
  fVar6 = *param_1;
  fVar3 = param_2[4];
  fVar4 = param_1[1];
  fVar16 = param_1[3];
  fVar17 = *param_2;
  fVar1 = param_2[7];
  fVar2 = param_1[2];
  fVar13 = param_2[3];
  fVar14 = param_1[4];
  fVar9 = param_2[2];
  fVar10 = param_2[6];
  fVar11 = param_1[5];
  fVar18 = param_1[6];
  fVar8 = param_2[5];
  fVar15 = param_1[7];
  fVar7 = param_2[8];
  fVar12 = param_1[8];
  *param_1 = fVar6 * fVar17 + fVar4 * fVar13 + fVar2 * fVar10;
  param_1[1] = fVar6 * fVar5 + fVar4 * fVar3 + fVar2 * fVar1;
  param_1[2] = fVar6 * fVar9 + fVar4 * fVar8 + fVar2 * fVar7;
  param_1[3] = fVar16 * fVar17 + fVar14 * fVar13 + fVar11 * fVar10;
  param_1[4] = fVar16 * fVar5 + fVar14 * fVar3 + fVar11 * fVar1;
  param_1[5] = fVar16 * fVar9 + fVar14 * fVar8 + fVar11 * fVar7;
  param_1[6] = fVar18 * fVar17 + fVar15 * fVar13 + fVar12 * fVar10;
  param_1[7] = fVar18 * fVar5 + fVar15 * fVar3 + fVar12 * fVar1;
  param_1[8] = fVar18 * fVar9 + fVar15 * fVar8 + fVar12 * fVar7;
  return;
}

