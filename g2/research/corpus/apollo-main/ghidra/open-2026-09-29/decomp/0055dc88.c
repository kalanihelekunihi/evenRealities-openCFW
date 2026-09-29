
undefined4 FUN_0055dc88(uint *param_1,byte param_2,float *param_3)

{
  float *pfVar1;
  float *pfVar2;
  float *pfVar3;
  float fVar4;
  float fVar5;
  float fVar6;
  float fVar7;
  
  pfVar3 = DAT_0055e214;
  pfVar2 = DAT_0055e1ec;
  pfVar1 = DAT_0055e1dc;
  if ((param_1 == (uint *)0x0) || ((*param_1 & 0x1ffffff) != DAT_0055e1f8)) {
    return 2;
  }
  if (param_2 == 0) {
    if ((0xfffff < (uint)param_3[1]) || (0xfffff < (uint)param_3[2])) {
      return 5;
    }
    *DAT_0055e208 = (uint)param_3[1] & 0xfffff;
    *DAT_0055e20c = (uint)param_3[2] & 0xfffff;
    *DAT_0055e210 = (uint)*(byte *)param_3;
  }
  else if (param_2 == 2) {
    if (param_3 == (float *)0x0) {
      return 6;
    }
    if (param_3[3] != DAT_0055de74) {
      return 7;
    }
    *param_3 = *DAT_0055e1dc;
    param_3[1] = pfVar1[1];
    param_3[2] = pfVar1[2];
    param_3[3] = (float)(uint)*(byte *)(pfVar1 + 3);
  }
  else if (param_2 < 2) {
    if (param_3 == (float *)0x0) {
      return 6;
    }
    if (param_3[2] != DAT_0055de74) {
      return 7;
    }
    fVar7 = *param_3;
    fVar4 = *DAT_0055e1dc;
    fVar5 = DAT_0055e1dc[1];
    fVar6 = DAT_0055e1dc[2];
    if (*DAT_0055e214 == 0.0) {
      *DAT_0055e214 = DAT_0055e218;
      *pfVar3 = (fVar5 + fVar6) * *pfVar3;
      *pfVar3 = *pfVar3 + fVar4;
    }
    param_3[1] = fVar7 * DAT_0055de78 + *pfVar3 + DAT_0055dee8;
  }
  else {
    if (param_2 != 3) {
      return 6;
    }
    if (param_3 == (float *)0x0) {
      return 6;
    }
    if (param_3[3] != DAT_0055de74) {
      return 7;
    }
    *param_3 = *DAT_0055e1ec;
    param_3[1] = pfVar2[1];
    param_3[2] = 0.0;
    param_3[3] = 0.0;
  }
  return 0;
}

