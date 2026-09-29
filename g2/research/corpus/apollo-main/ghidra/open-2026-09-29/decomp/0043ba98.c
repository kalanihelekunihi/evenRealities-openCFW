
float FUN_0043ba98(float param_1)

{
  uint uVar1;
  uint in_fpscr;
  float fVar2;
  float fVar3;
  uint uVar4;
  float fVar5;
  float fVar6;
  
  fVar2 = *DAT_0043bac4;
  fVar3 = DAT_0043bac4[1];
  if ((uint)DAT_0043bac4[0xf] < (uint)((int)param_1 << 1)) {
    if (0xfeffffff < (uint)((int)param_1 * 2)) {
      if (((uint)((int)param_1 * 2) < 0xff000001) && (CARRY4((uint)param_1,(uint)param_1))) {
        param_1 = 0.0;
      }
      return param_1;
    }
    if ((int)param_1 < 0) {
      return param_1;
    }
    goto FUN_00439cb2;
  }
  if (param_1 == 0.0) {
    return param_1;
  }
  if ((int)param_1 < 0) {
    fVar3 = -fVar3;
  }
  uVar4 = (uint)(fVar3 + param_1 * DAT_0043bac4[2]);
  fVar3 = (float)VectorSignedToFloat(uVar4,(byte)((in_fpscr & 0xfffffff) >> 0x16) & 3);
  fVar3 = (param_1 - fVar3 * DAT_0043bac4[4]) - fVar3 * DAT_0043bac4[5];
  uVar1 = uVar4 + 0x7f;
  if (-1 < (int)((uint)(ABS(fVar3) < DAT_0043bac4[6]) << 0x1f)) {
    fVar5 = fVar3 * fVar3 * DAT_0043bac4[7];
    fVar6 = DAT_0043bac4[9] + fVar3 * fVar3 * DAT_0043bac4[8];
    fVar2 = fVar2 * ((fVar5 + fVar3 * fVar6 + DAT_0043bac4[10]) /
                    ((fVar5 - fVar3 * fVar6) + DAT_0043bac4[10]));
  }
  if (uVar1 == 0) {
LAB_0043c076:
    if ((int)(uVar4 + 0xfd) < 1) {
      param_1 = fVar2 - fVar2;
    }
    else {
      fVar2 = fVar2 * DAT_0043bac4[0xc];
      param_1 = (float)((uVar4 + 0xfd) * 0x800000);
    }
  }
  else {
    param_1 = (float)(uVar1 * 0x800000);
    if (0xfe < uVar1) {
      if ((int)uVar1 < 1) goto LAB_0043c076;
      param_1 = DAT_0043bac4[3];
      if (uVar4 < 0xff) {
        fVar2 = fVar2 * DAT_0043bac4[0xb];
        param_1 = (float)(uVar4 * 0x800000);
      }
    }
  }
  param_1 = param_1 * fVar2;
  if (param_1 != 0.0 && ABS(param_1) != INFINITY) {
    return param_1;
  }
FUN_00439cb2:
  *DAT_00439cd4 = 0x22;
  return param_1;
}

