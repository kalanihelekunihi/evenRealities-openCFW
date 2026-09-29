
float FUN_0050968c(float param_1,int param_2)

{
  float fVar1;
  uint uVar2;
  float fVar3;
  
  fVar1 = param_1 * DAT_0050964c;
  if ((int)((uint)(ABS(fVar1) < DAT_00509650) << 0x1f) < 0) {
    uVar2 = (uint)((float)((uint)fVar1 & 0x80000000 | 0x3f000000) + fVar1);
    if (uVar2 != 0) {
      fVar1 = (float)VectorSignedFixedToFloat(uVar2,0x20,0xe);
      param_1 = param_1 + fVar1 * DAT_00509654 + fVar1 * DAT_00509658 + fVar1 * DAT_0050965c +
                fVar1 * DAT_00509660 + fVar1 * DAT_00509664;
    }
  }
  else {
    if (((int)param_1 << 1) >> 0x18 == -1) {
      if ((((int)param_1 << 1) >> 0x18 == -1) && (((uint)param_1 & 0x7fffff) != 0)) {
        return param_1;
      }
      return DAT_00509668;
    }
    if (ABS(param_1) == 0.0) {
      if (param_2 == 0) {
        return param_1;
      }
      return 1.0;
    }
    fVar1 = (float)((uint)fVar1 & 0x80000000 | 0x3f000000) + fVar1;
    if (ABS(fVar1) != 0.0) {
      uVar2 = 0x96 - ((uint)ABS(fVar1) >> 0x17);
      if ((int)uVar2 < 0x18) {
        if (0 < (int)uVar2) {
          fVar1 = (float)(((uint)fVar1 >> (uVar2 & 0xff)) << (uVar2 & 0xff));
        }
      }
      else {
        fVar1 = (float)((uint)fVar1 & 0x80000000);
      }
    }
    if (ABS(fVar1) != 0.0) {
      fVar3 = fVar1 * DAT_0050966c;
      param_1 = param_1 + fVar3 * DAT_00509654 + fVar3 * DAT_00509658 + fVar3 * DAT_0050965c +
                fVar3 * DAT_00509660 + fVar3 * DAT_00509664;
    }
    uVar2 = (uint)fVar1;
  }
  param_2 = (uVar2 & 3) + param_2;
  if ((int)((uint)(ABS(param_1) < DAT_00509670) << 0x1f) < 0) {
    if (param_2 * -0x80000000 < 0) {
      param_1 = 1.0;
    }
  }
  else {
    fVar1 = param_1 * param_1;
    if (param_2 * -0x80000000 < 0) {
      param_1 = (DAT_0050967c + (DAT_00509678 + fVar1 * DAT_00509674) * fVar1) * fVar1 + 1.0;
    }
    else {
      param_1 = param_1 + param_1 * fVar1 *
                          (DAT_00509688 + (DAT_00509684 + fVar1 * DAT_00509680) * fVar1);
    }
  }
  if (param_2 * 0x40000000 < 0) {
    param_1 = -param_1;
  }
  return param_1;
}

