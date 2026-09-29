
void FUN_00561902(float param_1,float param_2,float *param_3)

{
  float fVar1;
  float fVar2;
  float fVar3;
  
  fVar1 = *param_3;
  fVar2 = param_3[1];
  fVar3 = param_3[2];
  *param_3 = fVar1 + param_3[3] * param_1;
  param_3[1] = param_3[1] + param_3[4] * param_1;
  param_3[3] = param_3[3] + fVar1 * param_2;
  param_3[2] = param_3[2] + param_3[5] * param_1;
  param_3[4] = param_3[4] + fVar2 * param_2;
  param_3[5] = param_3[5] + fVar3 * param_2;
  return;
}

