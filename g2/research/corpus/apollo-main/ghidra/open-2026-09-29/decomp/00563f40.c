
float FUN_00563f40(float param_1)

{
  uint uVar1;
  float fVar2;
  int iVar3;
  float fVar4;
  
  fVar2 = param_1 * DAT_005640b0;
  if ((int)((uint)(ABS(fVar2) < DAT_005640b4) << 0x1f) < 0) {
    iVar3 = (int)((float)((uint)fVar2 & 0x80000000 | 0x3f000000) + fVar2);
    if (iVar3 != 0) {
      fVar2 = (float)VectorSignedFixedToFloat(iVar3,0x20,0xe);
      param_1 = param_1 + fVar2 * DAT_005640b8 + fVar2 * DAT_005640bc + fVar2 * DAT_005640c0 +
                fVar2 * DAT_005640c4 + fVar2 * DAT_005640c8;
    }
  }
  else {
    if (((int)param_1 << 1) >> 0x18 == -1) {
      if ((((int)param_1 << 1) >> 0x18 == -1) && (((uint)param_1 & 0x7fffff) != 0)) {
        return param_1;
      }
      return DAT_005640cc;
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
      fVar4 = fVar2 * DAT_005640d0;
      param_1 = param_1 + fVar4 * DAT_005640b8 + fVar4 * DAT_005640bc + fVar4 * DAT_005640c0 +
                fVar4 * DAT_005640c4 + fVar4 * DAT_005640c8;
    }
    iVar3 = (int)fVar2;
  }
  if ((int)((uint)(ABS(param_1) < DAT_005640d4) << 0x1f) < 0) {
    if (iVar3 << 0x1f < 0) {
      return -1.0 / param_1;
    }
  }
  else {
    fVar4 = param_1 * param_1;
    fVar2 = (DAT_005640dc + fVar4 * DAT_005640d8) * fVar4 + 1.0;
    param_1 = param_1 + param_1 * fVar4 * DAT_005640e0;
    if (iVar3 << 0x1f < 0) {
      return -(fVar2 / param_1);
    }
    param_1 = param_1 / fVar2;
  }
  return param_1;
}

