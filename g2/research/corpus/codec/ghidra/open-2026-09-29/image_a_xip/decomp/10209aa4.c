
uint gx8002_udivdi3(uint param_1,uint param_2,uint param_3,uint param_4)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  int iVar4;
  uint uVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;
  uint uVar9;
  uint uVar10;
  
  if (param_4 == 0) {
    if (param_2 < param_3) {
      if (param_3 < 0x10000) {
        iVar4 = 0;
        if (0xff < param_3) {
          iVar4 = 8;
        }
      }
      else {
        iVar4 = 0x18;
        if (param_3 < 0x1000000) {
          iVar4 = 0x10;
        }
      }
      uVar5 = iVar4 + (uint)*(byte *)(iRam10209dd4 + (param_3 >> iVar4));
      uVar3 = 0x20 - uVar5;
      if (uVar3 != 0) {
        param_3 = param_3 << (uVar3 & 0x3f);
        param_2 = param_1 >> (uVar5 & 0x3f) | param_2 << (uVar3 & 0x3f);
        param_1 = param_1 << (uVar3 & 0x3f);
      }
      uVar1 = param_3 >> 0x10;
      uVar2 = param_2 / uVar1;
      uVar5 = (param_3 & 0x7fff) * uVar2;
      uVar9 = param_1 >> 0x10 | (param_2 - uVar2 * uVar1) * 0x10000;
      uVar3 = uVar2;
      if (uVar9 < uVar5) {
        uVar9 = uVar9 + param_3;
        uVar3 = uVar2 - 1;
        if ((param_3 <= uVar9) && (uVar9 < uVar5)) {
          uVar3 = uVar2 - 2;
          uVar9 = uVar9 + param_3;
        }
      }
      uVar2 = (uVar9 - uVar5) / uVar1;
      uVar6 = uVar2 * (param_3 & 0x7fff);
      uVar1 = param_1 & 0x7fff | ((uVar9 - uVar5) - uVar2 * uVar1) * 0x10000;
      uVar5 = uVar2;
      if (uVar1 < uVar6) {
        uVar1 = uVar1 + param_3;
        uVar5 = uVar2 - 1;
        if ((param_3 <= uVar1) && (uVar1 < uVar6)) {
          uVar5 = uVar2 - 2;
        }
      }
      return uVar3 << 0x10 | uVar5;
    }
    if (param_3 == 0) {
      param_3 = 1 / 0;
    }
    if (param_3 < 0x10000) {
      iVar4 = 0;
      if (0xff < param_3) {
        iVar4 = 8;
      }
    }
    else {
      iVar4 = 0x18;
      if (param_3 < 0x1000000) {
        iVar4 = 0x10;
      }
    }
    uVar3 = iVar4 + (uint)*(byte *)(iRam10209dd4 + (param_3 >> iVar4));
    uVar5 = 0x20 - uVar3;
    if (uVar5 == 0) {
      param_2 = param_2 - param_3;
      uVar7 = param_3 >> 0x10;
      uVar3 = param_3 & 0x7fff;
      uVar1 = param_1;
    }
    else {
      param_3 = param_3 << (uVar5 & 0x3f);
      uVar10 = param_2 >> (uVar3 & 0x3f);
      uVar1 = param_1 << (uVar5 & 0x3f);
      uVar7 = param_3 >> 0x10;
      uVar2 = uVar10 / uVar7;
      uVar6 = param_1 >> (uVar3 & 0x3f) | param_2 << (uVar5 & 0x3f);
      uVar3 = param_3 & 0x7fff;
      uVar9 = uVar3 * uVar2;
      uVar5 = uVar6 >> 0x10 | (uVar10 - uVar2 * uVar7) * 0x10000;
      if (((uVar5 < uVar9) && (uVar5 = uVar5 + param_3, param_3 <= uVar5)) && (uVar5 < uVar9)) {
        uVar5 = uVar5 + param_3;
      }
      uVar10 = (uVar5 - uVar9) / uVar7;
      uVar2 = uVar3 * uVar10;
      param_2 = ((uVar5 - uVar9) - uVar10 * uVar7) * 0x10000 | uVar6 & 0x7fff;
      if (((param_2 < uVar2) && (param_2 = param_2 + param_3, param_3 <= param_2)) &&
         (param_2 < uVar2)) {
        param_2 = param_2 + param_3;
      }
      param_2 = param_2 - uVar2;
    }
    uVar6 = param_2 / uVar7;
    uVar2 = uVar6 * uVar3;
    uVar9 = uVar1 >> 0x10 | (param_2 - uVar6 * uVar7) * 0x10000;
    uVar5 = uVar6;
    if (uVar9 < uVar2) {
      uVar9 = uVar9 + param_3;
      uVar5 = uVar6 - 1;
      if ((param_3 <= uVar9) && (uVar9 < uVar2)) {
        uVar5 = uVar6 - 2;
        uVar9 = uVar9 + param_3;
      }
    }
    uVar6 = (uVar9 - uVar2) / uVar7;
    uVar2 = ((uVar9 - uVar2) - uVar6 * uVar7) * 0x10000 | uVar1 & 0x7fff;
    uVar1 = uVar6;
    if (uVar2 < uVar6 * uVar3) {
      uVar2 = uVar2 + param_3;
      uVar1 = uVar6 - 1;
      if ((param_3 <= uVar2) && (uVar2 < uVar6 * uVar3)) {
        uVar1 = uVar6 - 2;
      }
    }
    return uVar5 << 0x10 | uVar1;
  }
  if (param_2 < param_4) {
    return 0;
  }
  if (param_4 < 0x10000) {
    iVar4 = (uint)(0xff < param_4) << 3;
  }
  else {
    iVar4 = 0x10;
    if (0xffffff < param_4) {
      iVar4 = 0x18;
    }
  }
  uVar5 = (uint)*(byte *)(iRam10209dd4 + (param_4 >> iVar4)) + iVar4;
  uVar3 = 0x20 - uVar5;
  if (uVar3 == 0) {
    if (param_2 <= param_4) {
      return (uint)(param_3 <= param_1);
    }
    return 1;
  }
  uVar6 = param_3 >> (uVar5 & 0x3f) | param_4 << (uVar3 & 0x3f);
  uVar9 = param_2 >> (uVar5 & 0x3f);
  uVar7 = uVar6 >> 0x10;
  uVar2 = uVar9 / uVar7;
  uVar1 = param_1 >> (uVar5 & 0x3f) | param_2 << (uVar3 & 0x3f);
  uVar10 = (uVar6 & 0x7fff) * uVar2;
  uVar9 = uVar1 >> 0x10 | (uVar9 - uVar2 * uVar7) * 0x10000;
  param_3 = param_3 << (uVar3 & 0x3f);
  uVar5 = uVar2;
  if (uVar9 < uVar10) {
    uVar9 = uVar9 + uVar6;
    uVar5 = uVar2 - 1;
    if ((uVar6 <= uVar9) && (uVar9 < uVar10)) {
      uVar5 = uVar2 - 2;
      uVar9 = uVar9 + uVar6;
    }
  }
  uVar2 = (uVar9 - uVar10) / uVar7;
  uVar8 = (uVar6 & 0x7fff) * uVar2;
  uVar9 = uVar1 & 0x7fff | ((uVar9 - uVar10) - uVar2 * uVar7) * 0x10000;
  uVar1 = uVar2;
  if (uVar9 < uVar8) {
    uVar9 = uVar9 + uVar6;
    uVar1 = uVar2 - 1;
    if ((uVar6 <= uVar9) && (uVar9 < uVar8)) {
      uVar1 = uVar2 - 2;
      uVar9 = uVar9 + uVar6;
    }
  }
  uVar2 = uVar5 << 0x10 | uVar1;
  uVar5 = param_3 & 0x7fff;
  param_3 = param_3 >> 0x10;
  uVar6 = (uVar1 & 0x7fff) * uVar5;
  uVar5 = (uVar6 >> 0x10) + param_3 * (uVar1 & 0x7fff) + (uVar2 >> 0x10) * uVar5;
  uVar1 = param_3 * (uVar2 >> 0x10) + (uVar5 >> 0x10);
  if ((uVar1 <= uVar9 - uVar8) &&
     ((uVar9 - uVar8 != uVar1 || (uVar5 * 0x10000 + (uVar6 & 0x7fff) <= param_1 << (uVar3 & 0x3f))))
     ) {
    return uVar2;
  }
  return uVar2 - 1;
}

