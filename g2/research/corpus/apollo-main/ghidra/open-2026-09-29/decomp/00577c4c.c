
uint FUN_00577c4c(uint param_1,uint param_2)

{
  uint uVar1;
  uint uVar2;
  int iVar3;
  uint uVar4;
  int iVar5;
  int iVar6;
  uint uVar7;
  uint uVar8;
  uint uVar9;
  bool bVar10;
  
  uVar7 = param_1 & 0x80000000;
  uVar2 = param_2 * 2;
  uVar8 = (param_1 & 0x7fffffff) >> 0x17;
  uVar4 = (param_2 & 0x7fffffff) >> 0x17;
  if ((uVar4 == 0 || uVar8 == 0xff) || uVar4 == 0xff) {
    bVar10 = uVar2 == 0 || uVar8 == 0xff;
    if (uVar2 != 0 && uVar8 != 0xff) {
      bVar10 = uVar4 == 0xff;
    }
    if (bVar10) {
      uVar4 = param_1 * 2;
      uVar8 = uVar2;
      if (0xfeffffff < uVar4) {
        param_1 = 0x7fffffff;
        uVar8 = uVar4;
      }
      if (uVar8 != 0xff000000) {
        param_1 = 0x7fffffff;
      }
      if (0xfeffffff < uVar4 || 0xfeffffff < uVar2) {
        return param_1;
      }
      uVar4 = (*DAT_00577c38)(param_1);
      return uVar4;
    }
    if (param_1 * 2 <= uVar2) {
LAB_00577cb0:
      if (uVar2 + param_1 * -2 == 0) {
        return uVar7;
      }
      return param_1;
    }
    iVar6 = LZCOUNT(param_2 << 9);
    uVar2 = (param_2 << 9) << iVar6;
    uVar4 = -iVar6;
    if (uVar8 == 0) {
      iVar6 = LZCOUNT(param_1 << 9);
      uVar1 = (param_1 << 9) << iVar6;
      uVar8 = -iVar6;
      goto LAB_00577c74;
    }
  }
  else {
    if (param_1 * 2 <= uVar2) goto LAB_00577cb0;
    uVar2 = param_2 << 8 | 0x80000000;
  }
  uVar1 = param_1 << 8 | 0x80000000;
LAB_00577c74:
  uVar2 = uVar2 >> 8;
  uVar9 = (uVar8 - uVar4) - 8;
  if (7 < uVar8 - uVar4 && uVar9 != 0) {
    do {
      uVar1 = (uVar1 - uVar2 * (uVar1 / uVar2)) * 0x100;
      if (uVar1 == 0) {
        return uVar7;
      }
      bVar10 = 7 < uVar9;
      uVar9 = uVar9 - 8;
    } while (bVar10 && uVar9 != 0);
  }
  uVar1 = uVar1 >> (-uVar9 & 0xff);
  iVar6 = uVar1 - uVar2 * (uVar1 / uVar2);
  if (iVar6 == 0) {
    return uVar7;
  }
  iVar3 = LZCOUNT(iVar6);
  iVar5 = (uVar4 + 7) - iVar3;
  if (iVar3 <= (int)(uVar4 + 7)) {
    return (uVar7 | (uint)(iVar6 << iVar3) >> 8) + iVar5 * 0x800000;
  }
  return (uint)(iVar6 << iVar3) >> (8U - iVar5 & 0xff) | uVar7;
}

