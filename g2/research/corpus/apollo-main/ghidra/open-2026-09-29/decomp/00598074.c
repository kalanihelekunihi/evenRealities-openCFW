
float FUN_00598074(float param_1)

{
  int iVar1;
  uint uVar2;
  bool bVar3;
  uint in_fpscr;
  float fVar4;
  float fVar5;
  float fVar6;
  float fVar7;
  
  bVar3 = param_1 < 0.0;
  if ((uint)((int)param_1 * 2) < 0xff000000) {
    if (param_1 != 0.0 && !bVar3) {
      if ((uint)param_1 >> 0x17 == 0) {
        uVar2 = (uint)(param_1 * DAT_00598130[3]) >> 0x17;
        param_1 = (float)((int)(param_1 * DAT_00598130[3]) + (uVar2 - 0x7e) * -0x800000);
        iVar1 = uVar2 - 0x95;
      }
      else {
        iVar1 = ((uint)param_1 >> 0x17) - 0x7e;
        param_1 = (float)((int)param_1 + iVar1 * -0x800000);
      }
      if (param_1 < *DAT_00598130) {
        iVar1 = iVar1 + -1;
        param_1 = param_1 * DAT_00598130[2];
      }
      fVar4 = (float)VectorSignedToFloat(iVar1,(byte)((in_fpscr & 0xfffffff) >> 0x16) & 3);
      fVar5 = param_1 - DAT_00598130[1];
      fVar6 = fVar5 / (param_1 + DAT_00598130[1]);
      fVar7 = fVar6 * fVar6;
      return (fVar5 - ((fVar5 - (DAT_00598130[6] +
                                (DAT_00598130[5] + DAT_00598130[4] * fVar7) * fVar7) * fVar7) *
                       fVar6 - DAT_00598130[8] * fVar4)) + DAT_00598130[7] * fVar4;
    }
    if (!bVar3) {
      return -INFINITY;
    }
  }
  else {
    if (0xff000000 < (uint)((int)param_1 * 2)) {
      return param_1;
    }
    bVar3 = (int)param_1 < 0;
  }
  if (!bVar3) {
    return param_1;
  }
  fVar4 = (float)(*DAT_00577c38)(0x7fffffff);
  return fVar4;
}

