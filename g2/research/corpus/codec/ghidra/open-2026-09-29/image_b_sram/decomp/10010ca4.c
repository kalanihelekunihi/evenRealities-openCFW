
uint FUN_10010ca4(uint param_1,uint param_2,uint param_3,uint param_4)

{
  uint uVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  int iVar5;
  int iVar6;
  
  uVar3 = param_4 & 0x3fffffff;
  if (((param_3 == 0 && uVar3 == 0) || (uVar4 = param_2 & 0x3fffffff, -1 < (int)uVar4)) ||
     ((int)(-param_3 | param_3) < 0 || uVar3 != 0)) {
    FUN_10011e50(param_1,param_2,param_3,param_4);
    uVar3 = FUN_10012050();
    return uVar3;
  }
  if (uVar4 <= uVar3) {
    if (uVar4 < uVar3) {
      return param_1;
    }
    if (param_1 < param_3) {
      return param_1;
    }
    if (param_1 == param_3) goto LAB_10010dcc;
  }
  if (uVar4 < 0x100000) {
    if (uVar4 == 0) {
      iVar6 = -0x413;
      for (uVar1 = param_1; 0 < (int)uVar1; uVar1 = uVar1 * 2) {
        iVar6 = iVar6 + -1;
      }
    }
    else {
      iVar2 = param_2 << 0xb;
      iVar6 = -0x3fe;
      do {
        iVar2 = iVar2 * 2;
        iVar6 = iVar6 + -1;
      } while (0 < iVar2);
    }
  }
  else {
    iVar6 = ((int)uVar4 >> 0x14) + -0x3ff;
  }
  if (uVar3 < 0x100000) {
    if (uVar3 == 0) {
      iVar2 = -0x413;
      for (uVar1 = param_3; 0 < (int)uVar1; uVar1 = uVar1 * 2) {
        iVar2 = iVar2 + -1;
      }
    }
    else {
      iVar5 = param_4 << 0xb;
      iVar2 = -0x3fe;
      do {
        iVar5 = iVar5 * 2;
        iVar2 = iVar2 + -1;
      } while (0 < iVar5);
    }
  }
  else {
    iVar2 = ((int)uVar3 >> 0x14) + -0x3ff;
  }
  if (iVar6 < -0x3fe) {
    uVar1 = -iVar6 - 0x3fe;
    if ((int)uVar1 < 0x20) {
      uVar4 = param_1 >> (0x20 - uVar1 & 0x3f) | uVar4 << (uVar1 & 0x3f);
      param_1 = param_1 << (uVar1 & 0x3f);
    }
    else {
      uVar4 = param_1 << (-iVar6 - 0x41eU & 0x3f);
      param_1 = 0;
    }
  }
  else {
    uVar4 = param_2 & 0x7ffff | 0x100000;
  }
  if (iVar2 < -0x3fe) {
    uVar1 = -iVar2 - 0x3fe;
    if ((int)uVar1 < 0x20) {
      uVar3 = uVar3 << (uVar1 & 0x3f) | param_3 >> (0x20 - uVar1 & 0x3f);
      param_3 = param_3 << (uVar1 & 0x3f);
    }
    else {
      uVar3 = param_3 << (-iVar2 - 0x41eU & 0x3f);
      param_3 = 0;
    }
  }
  else {
    uVar3 = param_4 & 0x7ffff | 0x100000;
  }
  iVar6 = iVar6 - iVar2;
  while( true ) {
    uVar1 = uVar4 - uVar3;
    if (param_1 < param_3) {
      uVar1 = uVar1 - 1;
    }
    if (iVar6 == 0) break;
    if ((int)uVar1 < 0) {
      uVar4 = uVar4 * 2 - ((int)param_1 >> 0x1f);
    }
    else {
      param_1 = param_1 - param_3;
      if (uVar1 == 0 && param_1 == 0) goto LAB_10010dcc;
      uVar4 = uVar1 * 2 - ((int)param_1 >> 0x1f);
    }
    param_1 = param_1 * 2;
    iVar6 = iVar6 + -1;
  }
  if (-1 < (int)uVar1) {
    param_1 = param_1 - param_3;
    uVar4 = uVar1;
  }
  if (uVar4 != 0 || param_1 != 0) {
    for (; (int)uVar4 < 0x100000; uVar4 = uVar4 * 2 - iVar6) {
      iVar6 = (int)param_1 >> 0x1f;
      param_1 = param_1 * 2;
      iVar2 = iVar2 + -1;
    }
    if (-0x3ff < iVar2) {
      return param_1;
    }
    uVar3 = -iVar2 - 0x3fe;
    if ((int)uVar3 < 0x15) {
      uVar4 = uVar4 << (0x20 - uVar3 & 0x3f) | param_1 >> (uVar3 & 0x3f);
    }
    else if ((int)uVar3 < 0x20) {
      uVar4 = uVar4 << (0x20 - uVar3 & 0x3f) | param_1 >> (uVar3 & 0x3f);
    }
    else {
      uVar4 = (int)uVar4 >> (-iVar2 - 0x41eU & 0x3f);
    }
    return uVar4;
  }
LAB_10010dcc:
  return *(uint *)PTR_DAT_10010ee4;
}

