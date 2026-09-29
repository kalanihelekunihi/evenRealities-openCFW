
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 hw_config_dispatch_42ec0c(uint *param_1,byte param_2,float *param_3)

{
  float *pfVar1;
  float *pfVar2;
  float *pfVar3;
  float fVar4;
  float fVar5;
  float fVar6;
  float fVar7;
  
  pfVar3 = _DAT_0042f198;
  pfVar2 = _DAT_0042f170;
  pfVar1 = _DAT_0042f160;
  if ((param_1 == (uint *)0x0) || ((*param_1 & 0x1ffffff) != _DAT_0042f17c)) {
    return 2;
  }
  if (param_2 == 0) {
    if ((0xfffff < (uint)param_3[1]) || (0xfffff < (uint)param_3[2])) {
      return 5;
    }
    *_DAT_0042f18c = (uint)param_3[1] & 0xfffff;
    *_DAT_0042f190 = (uint)param_3[2] & 0xfffff;
    *_DAT_0042f194 = (uint)*(byte *)param_3;
  }
  else if (param_2 == 2) {
    if (param_3 == (float *)0x0) {
      return 6;
    }
    if (param_3[3] != fRam0042edf8) {
      return 7;
    }
    *param_3 = *_DAT_0042f160;
    param_3[1] = pfVar1[1];
    param_3[2] = pfVar1[2];
    param_3[3] = (float)(uint)*(byte *)(pfVar1 + 3);
  }
  else if (param_2 < 2) {
    if (param_3 == (float *)0x0) {
      return 6;
    }
    if (param_3[2] != fRam0042edf8) {
      return 7;
    }
    fVar7 = *param_3;
    fVar4 = *_DAT_0042f160;
    fVar5 = _DAT_0042f160[1];
    fVar6 = _DAT_0042f160[2];
    if (*_DAT_0042f198 == 0.0) {
      *_DAT_0042f198 = _DAT_0042f19c;
      *pfVar3 = (fVar5 + fVar6) * *pfVar3;
      *pfVar3 = *pfVar3 + fVar4;
    }
    param_3[1] = fVar7 * fRam0042edfc + *pfVar3 + fRam0042ee6c;
  }
  else {
    if (param_2 != 3) {
      return 6;
    }
    if (param_3 == (float *)0x0) {
      return 6;
    }
    if (param_3[3] != fRam0042edf8) {
      return 7;
    }
    *param_3 = *_DAT_0042f170;
    param_3[1] = pfVar2[1];
    param_3[2] = 0.0;
    param_3[3] = 0.0;
  }
  return 0;
}

