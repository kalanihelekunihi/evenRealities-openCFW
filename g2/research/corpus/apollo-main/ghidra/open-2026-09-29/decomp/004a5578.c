
undefined4
semantic_quaternion_to_euler(float *param_1,float *param_2,undefined4 param_3,undefined4 param_4)

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
  
  fVar1 = DAT_004a56a0;
  fVar2 = param_1[1];
  fVar5 = param_1[2] * 2.0;
  fVar4 = param_1[3] * 2.0;
  fVar6 = *param_1;
  fVar7 = *param_1;
  fVar8 = param_1[1];
  fVar9 = param_1[1];
  fVar10 = param_1[2];
  fVar11 = param_1[2];
  fVar3 = (float)FUN_0050969c(-(fVar5 * param_1[1] + fVar4 * *param_1),
                              1.0 - (fVar5 * fVar10 + fVar4 * param_1[3]));
  *param_2 = fVar3 * fVar1;
  fVar2 = (float)FUN_0050969c(-(fVar4 * fVar11 + fVar2 * 2.0 * fVar6),
                              1.0 - (fVar2 * 2.0 * fVar8 + fVar5 * fVar10));
  param_2[1] = fVar2 * fVar1;
  fVar2 = (float)FUN_00509708(-(fVar4 * fVar9 - fVar5 * fVar7));
  param_2[2] = fVar2 * fVar1;
  return param_4;
}

