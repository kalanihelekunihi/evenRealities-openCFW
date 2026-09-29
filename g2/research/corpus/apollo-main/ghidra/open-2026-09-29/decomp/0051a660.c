
void FUN_0051a660(float param_1,float param_2,float param_3,float param_4,float param_5,
                 float param_6,float *param_7)

{
  float fVar1;
  
  fVar1 = *param_7;
  *param_7 = (fVar1 * param_3 * param_1 - param_7[1] * param_4 * param_2) + param_5;
  param_7[1] = fVar1 * param_3 * param_2 + param_7[1] * param_4 * param_1 + param_6;
  return;
}

