
undefined4 FUN_00561b38(float *param_1)

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
  
  fVar6 = param_1[5];
  fVar1 = param_1[3];
  fVar3 = param_1[7];
  fVar7 = param_1[8];
  fVar12 = *param_1;
  fVar2 = param_1[6];
  fVar4 = param_1[4];
  fVar9 = fVar7 * fVar4 - fVar6 * fVar3;
  fVar8 = fVar6 * fVar2 - fVar7 * fVar1;
  fVar11 = param_1[1];
  fVar5 = fVar3 * fVar1 - fVar4 * fVar2;
  fVar10 = param_1[2];
  fVar13 = fVar9 * fVar12 + fVar8 * fVar11 + fVar5 * fVar10;
  if ((int)((uint)(ABS(fVar13) < DAT_00561c64) << 0x1f) < 0) {
    return 0xffffffff;
  }
  *param_1 = fVar9;
  param_1[1] = fVar3 * fVar10 - fVar11 * fVar7;
  param_1[2] = fVar11 * fVar6 - fVar4 * fVar10;
  param_1[3] = fVar8;
  param_1[4] = fVar12 * fVar7 - fVar2 * fVar10;
  param_1[5] = fVar1 * fVar10 - fVar12 * fVar6;
  param_1[6] = fVar5;
  param_1[7] = fVar2 * fVar11 - fVar12 * fVar3;
  param_1[8] = fVar12 * fVar4 - fVar1 * fVar11;
  fVar13 = 1.0 / fVar13;
  *param_1 = *param_1 * fVar13;
  param_1[1] = param_1[1] * fVar13;
  param_1[2] = param_1[2] * fVar13;
  param_1[3] = param_1[3] * fVar13;
  param_1[4] = param_1[4] * fVar13;
  param_1[5] = param_1[5] * fVar13;
  param_1[6] = param_1[6] * fVar13;
  param_1[7] = param_1[7] * fVar13;
  param_1[8] = param_1[8] * fVar13;
  return 0;
}

