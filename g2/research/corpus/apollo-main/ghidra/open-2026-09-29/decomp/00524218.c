
float FUN_00524218(float param_1)

{
  float fVar1;
  
  fVar1 = (float)(DAT_005242f8 - ((uint)param_1 >> 1));
  return param_1 * fVar1 * (1.5 - param_1 * 0.5 * fVar1 * fVar1);
}

