
uint FUN_00509708(float param_1)

{
  uint uVar1;
  float fVar2;
  
  uVar1 = (uint)param_1 >> 0x1f;
  param_1 = ABS(param_1);
  if (param_1 != 0.0) {
    if ((uint)param_1 < 0x3f800001) {
      fVar2 = SQRT((param_1 + 1.0) * (1.0 - param_1));
      if ((uint)DAT_00509760 < (uint)param_1) {
        uVar1 = 4;
        fVar2 = fVar2 / param_1;
      }
      else {
        fVar2 = param_1 / fVar2;
      }
      if (0x3e8930a3 < (int)fVar2) {
        uVar1 = uVar1 | 2;
      }
      return uVar1 >> 1;
    }
    if ((uint)((int)param_1 * 2) < 0xff000001) {
      *DAT_00439cd4 = 0x21;
      return uVar1;
    }
  }
  return uVar1;
}

