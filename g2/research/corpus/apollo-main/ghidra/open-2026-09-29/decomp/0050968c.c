
float FUN_0050968c(float param_1)

{
  int iVar1;
  float fVar2;
  uint uVar3;
  float fVar4;
  
  fVar2 = param_1 * DAT_0050964c;
  if ((int)((uint)(ABS(fVar2) < DAT_00509650) << 0x1f) < 0) {
    uVar3 = (uint)((float)((uint)fVar2 & 0x80000000 | 0x3f000000) + fVar2);
    if (uVar3 != 0) {
      fVar2 = (float)VectorSignedFixedToFloat(uVar3,0x20,0xe);
      param_1 = param_1 + fVar2 * DAT_00509654 + fVar2 * DAT_00509658 + fVar2 * DAT_0050965c +
                fVar2 * DAT_00509660 + fVar2 * DAT_00509664;
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
      return 1.0;
    }
    fVar2 = (float)((uint)fVar2 & 0x80000000 | 0x3f000000) + fVar2;
    if (ABS(fVar2) != 0.0) {
      uVar3 = 0x96 - ((uint)ABS(fVar2) >> 0x17);
      if ((int)uVar3 < 0x18) {
        if (0 < (int)uVar3) {
          fVar2 = (float)(((uint)fVar2 >> (uVar3 & 0xff)) << (uVar3 & 0xff));
        }
      }
      else {
        fVar2 = (float)((uint)fVar2 & 0x80000000);
      }
    }
    if (ABS(fVar2) != 0.0) {
      fVar4 = fVar2 * DAT_0050966c;
      param_1 = param_1 + fVar4 * DAT_00509654 + fVar4 * DAT_00509658 + fVar4 * DAT_0050965c +
                fVar4 * DAT_00509660 + fVar4 * DAT_00509664;
    }
    uVar3 = (uint)fVar2;
  }
  iVar1 = (uVar3 & 3) + 1;
  if ((int)((uint)(ABS(param_1) < DAT_00509670) << 0x1f) < 0) {
    if (iVar1 * -0x80000000 < 0) {
      param_1 = 1.0;
    }
  }
  else {
    fVar2 = param_1 * param_1;
    if (iVar1 * -0x80000000 < 0) {
      param_1 = (DAT_0050967c + (DAT_00509678 + fVar2 * DAT_00509674) * fVar2) * fVar2 + 1.0;
    }
    else {
      param_1 = param_1 + param_1 * fVar2 *
                          (DAT_00509688 + (DAT_00509684 + fVar2 * DAT_00509680) * fVar2);
    }
  }
  if (iVar1 * 0x40000000 < 0) {
    param_1 = -param_1;
  }
  return param_1;
}

