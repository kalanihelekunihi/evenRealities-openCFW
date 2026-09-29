
/* WARNING: Removing unreachable block (ram,0x0055ea00) */

float FUN_0058ecbc(float param_1)

{
  uint uVar1;
  float fVar2;
  float fVar3;
  
  uVar1 = 4;
  if (((uint)param_1 & 0x80000000) != 0 && ABS(param_1) != 0.0) {
    uVar1 = 8;
  }
  param_1 = ABS(param_1);
  if (0x3f800000 < (uint)param_1) {
    if (0xff000000 < (uint)((int)param_1 * 2)) {
      return param_1;
    }
    fVar3 = (float)(*DAT_00577c38)(0x7fffffff);
    return fVar3;
  }
  fVar3 = SQRT((param_1 + 1.0) * (1.0 - param_1));
  if ((uint)DAT_0058ed1c < (uint)param_1) {
    uVar1 = uVar1 ^ 4;
    fVar3 = fVar3 / param_1;
  }
  else {
    fVar3 = param_1 / fVar3;
  }
  if (0x3e8930a3 < (int)fVar3) {
    fVar3 = (DAT_0055ea1c + DAT_0055ea08 * fVar3) / (DAT_0055ea08 + fVar3);
    uVar1 = uVar1 | 2;
  }
  if (0x72ffffff < (uint)((int)fVar3 * 2)) {
    fVar2 = fVar3 * fVar3;
    fVar3 = (fVar3 + fVar3 * fVar2 * DAT_0055ea0c) /
            (DAT_0055ea18 + (DAT_0055ea14 + DAT_0055ea10 * fVar2) * fVar2);
  }
  if ((uVar1 >> 1 & 2) != 0) {
    fVar3 = -fVar3;
  }
  return fVar3 + *(float *)(&DAT_0055ea20 + (uVar1 >> 1) * 4);
}

