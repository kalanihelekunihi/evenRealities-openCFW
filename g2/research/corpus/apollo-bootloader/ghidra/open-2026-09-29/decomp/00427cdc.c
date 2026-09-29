
ulonglong fmod_bits_427cdc(uint param_1,uint param_2)

{
  uint uVar1;
  uint uVar2;
  int iVar3;
  uint uVar4;
  int iVar5;
  int iVar6;
  uint uVar7;
  uint uVar8;
  bool bVar9;
  
  uVar2 = param_2 * 2;
  uVar7 = (param_1 & 0x7fffffff) >> 0x17;
  uVar4 = (param_2 & 0x7fffffff) >> 0x17;
  if ((uVar4 == 0 || uVar7 == 0xff) || uVar4 == 0xff) {
    bVar9 = uVar2 == 0 || uVar7 == 0xff;
    if (uVar2 != 0 && uVar7 != 0xff) {
      bVar9 = uVar4 == 0xff;
    }
    if (bVar9) {
      uVar4 = param_1 * 2;
      uVar7 = uVar2;
      if (0xfeffffff < uVar4) {
        param_1 = 0x7fffffff;
        uVar7 = uVar4;
      }
      if (uVar7 != 0xff000000) {
        param_1 = 0x7fffffff;
      }
      if (0xfeffffff >= uVar4 && uVar2 < 0xff000000) {
        *DAT_004275e4 = 0x21;
        return CONCAT44(uVar2,param_1);
      }
      return CONCAT44(uVar2,param_1);
    }
    if (param_1 * 2 <= uVar2) {
LAB_00427d40:
      if (uVar2 + param_1 * -2 != 0) {
        return CONCAT44(uVar2,param_1);
      }
      goto LAB_00427d4e;
    }
    iVar6 = LZCOUNT(param_2 << 9);
    uVar2 = (param_2 << 9) << iVar6;
    uVar4 = -iVar6;
    if (uVar7 != 0) goto LAB_00427d00;
    iVar6 = LZCOUNT(param_1 << 9);
    uVar1 = (param_1 << 9) << iVar6;
    uVar7 = -iVar6;
  }
  else {
    if (param_1 * 2 <= uVar2) goto LAB_00427d40;
    uVar2 = param_2 << 8 | 0x80000000;
LAB_00427d00:
    uVar1 = param_1 << 8 | 0x80000000;
  }
  uVar2 = uVar2 >> 8;
  uVar8 = (uVar7 - uVar4) - 8;
  if (7 < uVar7 - uVar4 && uVar8 != 0) {
    do {
      uVar1 = (uVar1 - uVar2 * (uVar1 / uVar2)) * 0x100;
      if (uVar1 == 0) goto LAB_00427d4e;
      bVar9 = 7 < uVar8;
      uVar8 = uVar8 - 8;
    } while (bVar9 && uVar8 != 0);
  }
  uVar1 = uVar1 >> (-uVar8 & 0xff);
  iVar6 = uVar1 - uVar2 * (uVar1 / uVar2);
  if (iVar6 != 0) {
    iVar3 = LZCOUNT(iVar6);
    iVar5 = (uVar4 + 7) - iVar3;
    if ((int)(uVar4 + 7) < iVar3) {
      return CONCAT44(iVar3,(uint)(iVar6 << iVar3) >> (8U - iVar5 & 0xff) | param_1 & 0x80000000);
    }
    return CONCAT44(iVar3,(param_1 & 0x80000000 | (uint)(iVar6 << iVar3) >> 8) + iVar5 * 0x800000);
  }
LAB_00427d4e:
  return CONCAT44(uVar2,param_1) & 0xffffffff80000000;
}

