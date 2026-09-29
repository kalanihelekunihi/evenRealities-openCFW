
void FUN_00561ad4(float *param_1,float *param_2,float *param_3)

{
  float fVar1;
  float fVar2;
  float fVar3;
  
  fVar1 = *param_2;
  fVar2 = *param_3;
  fVar3 = param_1[6] * fVar1 + param_1[7] * fVar2 + param_1[8];
  *param_2 = (*param_1 * fVar1 + param_1[1] * fVar2 + param_1[2]) / fVar3;
  *param_3 = (param_1[3] * fVar1 + param_1[4] * fVar2 + param_1[5]) / fVar3;
  return;
}

