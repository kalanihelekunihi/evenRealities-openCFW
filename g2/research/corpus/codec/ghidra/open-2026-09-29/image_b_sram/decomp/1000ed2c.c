
undefined4 FUN_1000ed2c(float *param_1)

{
  float fVar1;
  float in_vr0;
  
  if (0.0 < in_vr0) {
    return 0xffffffff;
  }
  if (in_vr0 < 0.0) {
    *param_1 = 0.0;
    return 0;
  }
  fVar1 = 0.0;
  *param_1 = in_vr0;
  FUN_100100a4();
  *param_1 = fVar1;
  return 0;
}

