
/* WARNING: Removing unreachable block (ram,0x0050955a) */

float FUN_00509690(float param_1)

{
  uint uVar1;
  float fVar2;
  int iVar3;
  float fVar4;
  
  fVar2 = param_1 * DAT_0050964c;
  if ((int)((uint)(ABS(fVar2) < DAT_00509650) << 0x1f) < 0) {
    iVar3 = (int)((float)((uint)fVar2 & 0x80000000 | 0x3f000000) + fVar2);
    if (iVar3 != 0) {
      fVar2 = (float)VectorSignedFixedToFloat(iVar3,0x20,0xe);
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
      return param_1;
    }
    fVar2 = (float)((uint)fVar2 & 0x80000000 | 0x3f000000) + fVar2;
    if (ABS(fVar2) != 0.0) {
      uVar1 = 0x96 - ((uint)ABS(fVar2) >> 0x17);
      if ((int)uVar1 < 0x18) {
        if (0 < (int)uVar1) {
          fVar2 = (float)(((uint)fVar2 >> (uVar1 & 0xff)) << (uVar1 & 0xff));
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
    iVar3 = (int)fVar2;
  }
  if ((int)((uint)(ABS(param_1) < DAT_00509670) << 0x1f) < 0) {
    if (iVar3 << 0x1f < 0) {
      param_1 = 1.0;
    }
  }
  else {
    fVar2 = param_1 * param_1;
    if (iVar3 << 0x1f < 0) {
      param_1 = (DAT_0050967c + (DAT_00509678 + fVar2 * DAT_00509674) * fVar2) * fVar2 + 1.0;
    }
    else {
      param_1 = param_1 + param_1 * fVar2 *
                          (DAT_00509688 + (DAT_00509684 + fVar2 * DAT_00509680) * fVar2);
    }
  }
  if (iVar3 << 0x1e < 0) {
    param_1 = -param_1;
  }
  return param_1;
}

