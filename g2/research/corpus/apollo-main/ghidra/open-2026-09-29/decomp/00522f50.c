
undefined4
FUN_00522f50(float param_1,float param_2,float param_3,float param_4,float param_5,float param_6,
            float param_7,float param_8,float *param_9,float *param_10)

{
  float fVar1;
  float fVar2;
  float fVar3;
  
  param_4 = param_4 - param_2;
  param_3 = param_1 - param_3;
  fVar1 = param_4 * param_1 + param_3 * param_2;
  param_8 = param_8 - param_6;
  param_7 = param_5 - param_7;
  fVar2 = param_8 * param_5 + param_7 * param_6;
  fVar3 = param_4 * param_7 - param_8 * param_3;
  if (-1 < (int)((uint)(ABS(fVar3) < DAT_005232c4) << 0x1f)) {
    *param_9 = (param_7 * fVar1 - param_3 * fVar2) / fVar3;
    *param_10 = (param_4 * fVar2 - param_8 * fVar1) / fVar3;
    return 1;
  }
  return 0;
}

