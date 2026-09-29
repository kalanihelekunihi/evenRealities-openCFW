
uint FUN_100117d0(uint param_1,uint param_2,uint param_3,uint param_4)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  uint uVar7;
  int iVar8;
  uint uVar9;
  uint uVar10;
  uint uVar11;
  
  if (param_4 != 0) {
    if (param_2 < param_4) {
      return param_1;
    }
    if (param_4 < 0x10000) {
      iVar8 = (uint)(0xff < param_4) << 3;
    }
    else {
      iVar8 = 0x10;
      if (0xffffff < param_4) {
        iVar8 = 0x18;
      }
    }
    uVar2 = (uint)(byte)PTR_LAB_10011af0[param_4 >> iVar8] + iVar8;
    uVar6 = 0x20 - uVar2;
    if (uVar6 == 0) {
      if ((param_4 < param_2) || (param_3 <= param_1)) {
        param_1 = param_1 - param_3;
      }
      return param_1;
    }
    uVar4 = param_3 >> (uVar2 & 0x3f) | param_4 << (uVar6 & 0x3f);
    uVar1 = param_2 >> (uVar2 & 0x3f);
    uVar3 = param_1 >> (uVar2 & 0x3f) | param_2 << (uVar6 & 0x3f);
    uVar7 = uVar4 >> 0x10;
    uVar11 = uVar1 / uVar7;
    param_3 = param_3 << (uVar6 & 0x3f);
    uVar5 = (uVar4 & 0x7fff) * uVar11;
    uVar9 = uVar3 >> 0x10 | (uVar1 - uVar11 * uVar7) * 0x10000;
    param_1 = param_1 << (uVar6 & 0x3f);
    uVar1 = uVar11;
    if (uVar9 < uVar5) {
      uVar9 = uVar9 + uVar4;
      uVar1 = uVar11 - 1;
      if ((uVar4 <= uVar9) && (uVar9 < uVar5)) {
        uVar1 = uVar11 - 2;
        uVar9 = uVar9 + uVar4;
      }
    }
    uVar11 = (uVar9 - uVar5) / uVar7;
    uVar10 = uVar11 * (uVar4 & 0x7fff);
    uVar9 = uVar3 & 0x7fff | ((uVar9 - uVar5) - uVar11 * uVar7) * 0x10000;
    uVar3 = uVar11;
    if (uVar9 < uVar10) {
      uVar9 = uVar9 + uVar4;
      uVar3 = uVar11 - 1;
      if ((uVar4 <= uVar9) && (uVar9 < uVar10)) {
        uVar3 = uVar11 - 2;
        uVar9 = uVar9 + uVar4;
      }
    }
    uVar1 = (uVar1 << 0x10 | uVar3) >> 0x10;
    uVar9 = uVar9 - uVar10;
    uVar11 = (uVar3 & 0x7fff) * (param_3 & 0x7fff);
    uVar3 = (uVar11 >> 0x10) + (param_3 >> 0x10) * (uVar3 & 0x7fff) + uVar1 * (param_3 & 0x7fff);
    uVar1 = (uVar3 >> 0x10) + (param_3 >> 0x10) * uVar1;
    uVar3 = uVar3 * 0x10000 + (uVar11 & 0x7fff);
    if (uVar1 <= uVar9) {
      uVar11 = uVar3;
      if (uVar9 != uVar1) {
        iVar8 = uVar9 - uVar1;
        goto LAB_10011a2e;
      }
      if (uVar3 <= param_1) {
        iVar8 = 0;
        goto LAB_10011a2e;
      }
    }
    uVar11 = uVar3 - param_3;
    iVar8 = uVar9 - ((uVar1 - uVar4) - (uint)(byte)~(uVar11 <= uVar3));
LAB_10011a2e:
    return param_1 - uVar11 >> (uVar6 & 0x3f) |
           iVar8 - (uint)(byte)~(param_1 - uVar11 <= param_1) << (uVar2 & 0x3f);
  }
  if (param_2 < param_3) {
    if (param_3 < 0x10000) {
      iVar8 = 0;
      if (0xff < param_3) {
        iVar8 = 8;
      }
    }
    else {
      iVar8 = 0x18;
      if (param_3 < 0x1000000) {
        iVar8 = 0x10;
      }
    }
    uVar2 = param_3 >> iVar8;
    uVar6 = 0x20 - (iVar8 + (uint)(byte)PTR_LAB_10011af0[uVar2]);
    if (uVar6 != 0) {
      param_3 = param_3 << (uVar6 & 0x3f);
      param_2 = param_1 >> (iVar8 + (uint)(byte)PTR_LAB_10011af0[uVar2] & 0x3f) |
                param_2 << (uVar6 & 0x3f);
      param_1 = param_1 << (uVar6 & 0x3f);
    }
    uVar9 = param_3 >> 0x10;
    uVar3 = (param_3 & 0x7fff) * (param_2 / uVar9);
    uVar1 = param_1 >> 0x10 | (param_2 - (param_2 / uVar9) * uVar9) * 0x10000;
    if (((uVar1 < uVar3) && (uVar1 = uVar1 + param_3, param_3 <= uVar1)) && (uVar1 < uVar3)) {
      uVar1 = uVar1 + param_3;
    }
    uVar4 = (uVar1 - uVar3) / uVar9;
    uVar2 = uVar4 * (param_3 & 0x7fff);
    uVar1 = param_1 & 0x7fff | ((uVar1 - uVar3) - uVar4 * uVar9) * 0x10000;
    if (uVar2 <= uVar1) {
      return uVar1 - uVar2 >> (uVar6 & 0x3f);
    }
  }
  else {
    if (param_3 == 0) {
      param_3 = 1 / 0;
    }
    if (param_3 < 0x10000) {
      iVar8 = 0;
      if (0xff < param_3) {
        iVar8 = 8;
      }
    }
    else {
      iVar8 = 0x18;
      if (param_3 < 0x1000000) {
        iVar8 = 0x10;
      }
    }
    uVar2 = iVar8 + (uint)(byte)PTR_LAB_10011af0[param_3 >> iVar8];
    uVar6 = 0x20 - uVar2;
    if (uVar6 == 0) {
      param_2 = param_2 - param_3;
      uVar9 = param_3 >> 0x10;
      uVar2 = param_3 & 0x7fff;
    }
    else {
      param_3 = param_3 << (uVar6 & 0x3f);
      uVar1 = param_2 >> (uVar2 & 0x3f);
      uVar9 = param_3 >> 0x10;
      uVar3 = param_2 << (uVar6 & 0x3f) | param_1 >> (uVar2 & 0x3f);
      uVar11 = uVar1 / uVar9;
      uVar2 = param_3 & 0x7fff;
      uVar4 = uVar2 * uVar11;
      uVar1 = uVar3 >> 0x10 | (uVar1 - uVar11 * uVar9) * 0x10000;
      param_1 = param_1 << (uVar6 & 0x3f);
      if (((uVar1 < uVar4) && (uVar1 = uVar1 + param_3, param_3 <= uVar1)) && (uVar1 < uVar4)) {
        uVar1 = uVar1 + param_3;
      }
      uVar11 = (uVar1 - uVar4) / uVar9;
      uVar5 = uVar2 * uVar11;
      param_2 = ((uVar1 - uVar4) - uVar11 * uVar9) * 0x10000 | uVar3 & 0x7fff;
      if (((param_2 < uVar5) && (param_2 = param_2 + param_3, param_3 <= param_2)) &&
         (param_2 < uVar5)) {
        param_2 = param_2 + param_3;
      }
      param_2 = param_2 - uVar5;
    }
    uVar3 = (param_2 / uVar9) * uVar2;
    uVar1 = param_1 >> 0x10 | (param_2 - (param_2 / uVar9) * uVar9) * 0x10000;
    if (((uVar1 < uVar3) && (uVar1 = uVar1 + param_3, param_3 <= uVar1)) && (uVar1 < uVar3)) {
      uVar1 = uVar1 + param_3;
    }
    uVar4 = (uVar1 - uVar3) / uVar9;
    uVar2 = uVar2 * uVar4;
    uVar1 = ((uVar1 - uVar3) - uVar4 * uVar9) * 0x10000 | param_1 & 0x7fff;
    if (uVar2 <= uVar1) goto LAB_10011944;
  }
  uVar1 = uVar1 + param_3;
  if ((param_3 <= uVar1) && (uVar1 < uVar2)) {
    uVar1 = param_3 + uVar1;
  }
LAB_10011944:
  return uVar1 - uVar2 >> (uVar6 & 0x3f);
}

