
float FUN_0058ec74(float param_1)

{
  uint uVar1;
  float fVar2;
  
  uVar1 = (uint)ABS(param_1) >> 0x17;
  if (uVar1 != 0) {
    if (uVar1 < 0x99) {
      uVar1 = -((int)param_1 >> 0x1f);
      param_1 = ABS(param_1);
      if (0x3f800000 < (int)param_1) {
        param_1 = 1.0 / param_1;
        uVar1 = uVar1 + 4;
      }
      if (0x3e8930a3 < (int)param_1) {
        param_1 = (DAT_0055ea1c + DAT_0055ea08 * param_1) / (DAT_0055ea08 + param_1);
        uVar1 = uVar1 | 2;
      }
      if (0x72ffffff < (uint)((int)param_1 * 2)) {
        fVar2 = param_1 * param_1;
        param_1 = (param_1 + param_1 * fVar2 * DAT_0055ea0c) /
                  (DAT_0055ea18 + (DAT_0055ea14 + DAT_0055ea10 * fVar2) * fVar2);
      }
      if ((uVar1 >> 1 & 2) != 0) {
        param_1 = -param_1;
      }
      param_1 = param_1 + *(float *)(&DAT_0055ea20 + (uVar1 >> 1) * 4);
      if ((uVar1 & 1) != 0) {
        param_1 = -param_1;
      }
      return param_1;
    }
    if ((uVar1 != 0xff) || (((uint)param_1 & 0x7fffff) == 0)) {
      param_1 = (float)(DAT_0058ecb8 | (uint)param_1 & 0x80000000);
    }
  }
  return param_1;
}

