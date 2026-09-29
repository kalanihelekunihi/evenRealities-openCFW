
uint FT_Vector_NormLen(uint *param_1)

{
  uint uVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  int iVar7;
  int iVar8;
  uint uVar9;
  int iVar10;
  int iVar11;
  
  uVar1 = *param_1;
  uVar4 = param_1[1];
  iVar7 = 1;
  iVar8 = 1;
  if ((int)uVar1 < 0) {
    uVar1 = -uVar1;
    iVar7 = -1;
  }
  if ((int)uVar4 < 0) {
    uVar4 = -uVar4;
    iVar8 = -1;
  }
  if (uVar1 == 0) {
    if (uVar4 != 0) {
      param_1[1] = iVar8 << 0x10;
    }
  }
  else if (uVar4 == 0) {
    uVar4 = uVar1;
    if (uVar1 != 0) {
      *param_1 = iVar7 << 0x10;
    }
  }
  else {
    if (uVar4 < uVar1) {
      uVar9 = uVar1 + (uVar4 >> 1);
    }
    else {
      uVar9 = uVar4 + (uVar1 >> 1);
    }
    iVar2 = FT_MSB(uVar9);
    iVar2 = (0x1fU - iVar2) - (uint)(0xaaaaaaaaU >> (0x1fU - iVar2 & 0xff) <= uVar9);
    uVar3 = iVar2 - 0xf;
    if ((int)uVar3 < 1) {
      uVar1 = uVar1 >> (-uVar3 & 0xff);
      uVar4 = uVar4 >> (-uVar3 & 0xff);
      uVar9 = uVar9 >> (-uVar3 & 0xff);
    }
    else {
      uVar1 = uVar1 << (uVar3 & 0xff);
      uVar4 = uVar4 << (uVar3 & 0xff);
      if (uVar4 < uVar1) {
        uVar9 = uVar1 + (uVar4 >> 1);
      }
      else {
        uVar9 = uVar4 + (uVar1 >> 1);
      }
    }
    iVar10 = 0x10000 - uVar9;
    do {
      uVar9 = uVar1 + ((int)(iVar10 * uVar1) >> 0x10);
      uVar5 = uVar4 + ((int)(iVar10 * uVar4) >> 0x10);
      iVar11 = ((iVar10 + 0x10000 >> 8) * ((int)(uVar9 * uVar9 + uVar5 * uVar5) / DAT_00524f10)) /
               0x10000;
      iVar10 = iVar11 + iVar10;
    } while (0 < iVar11);
    uVar6 = uVar9;
    if (iVar7 < 0) {
      uVar6 = -uVar9;
    }
    *param_1 = uVar6;
    uVar6 = uVar5;
    if (iVar8 < 0) {
      uVar6 = -uVar5;
    }
    param_1[1] = uVar6;
    iVar7 = (int)(uVar1 * uVar9 + uVar4 * uVar5) / 0x10000 + 0x10000;
    if ((int)uVar3 < 1) {
      uVar4 = iVar7 << (-uVar3 & 0xff);
    }
    else {
      uVar4 = (uint)((1 << (iVar2 + 0xf0U & 0xff)) + iVar7) >> (uVar3 & 0xff);
    }
  }
  return uVar4;
}

