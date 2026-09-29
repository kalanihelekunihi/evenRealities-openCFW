
uint FUN_0047cc1c(uint param_1,uint param_2,uint param_3,uint param_4)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  int iVar6;
  uint uVar7;
  uint uVar8;
  uint uVar9;
  uint uVar10;
  uint uVar11;
  uint uVar12;
  bool bVar13;
  
  uVar11 = param_4 & 0x80000000;
  if ((int)uVar11 < 0) {
    bVar13 = param_3 != 0;
    param_3 = -param_3;
    param_4 = -(uint)bVar13 - param_4;
  }
  uVar11 = uVar11 ^ (int)param_2 >> 0x20;
  if (uVar11 != 0) {
    if ((int)param_2 < 0) {
      bVar13 = param_1 != 0;
      param_1 = -param_1;
      param_2 = -(uint)bVar13 - param_2;
    }
    uVar1 = FUN_0047cc60(param_1,param_2);
    if ((uVar11 & 0x80000000) != 0) {
      uVar1 = -uVar1;
    }
    return uVar1;
  }
  if (param_4 == 0) {
    if (param_2 == 0) {
      if (2 < param_3) {
        return param_1 / param_3;
      }
    }
    else {
      if (0xffff < param_3) {
        if (param_3 < 0x1000000) {
          uVar1 = (param_2 - param_3 * (param_2 / param_3)) * 0x100 | param_1 >> 0x18;
          uVar7 = uVar1 / param_3;
          uVar11 = uVar7 | param_1 << 8;
          uVar1 = (uVar1 - param_3 * uVar7) * 0x100 | uVar11 >> 0x18;
          uVar7 = uVar1 / param_3;
          uVar11 = uVar7 | uVar11 << 8;
          uVar1 = (uVar1 - param_3 * uVar7) * 0x100 | uVar11 >> 0x18;
          uVar7 = uVar1 / param_3;
          uVar11 = uVar7 | uVar11 << 8;
          return ((uVar1 - param_3 * uVar7) * 0x100 | uVar11 >> 0x18) / param_3 | uVar11 << 8;
        }
        uVar1 = 0xf - LZCOUNT(param_3);
        iVar6 = LZCOUNT(param_3) - LZCOUNT(param_2);
        uVar11 = param_3 >> (uVar1 & 0xff);
        uVar1 = uVar1 & 0x1f;
        uVar7 = iVar6 + 0x20;
        uVar1 = (param_3 >> uVar1 | param_3 << 0x20 - uVar1) ^ uVar11;
        uVar10 = iVar6 + 0x11;
        if (uVar7 < 0xf || uVar10 == 0) goto LAB_0047cd04;
        goto LAB_0047cd92;
      }
      if (2 < param_3) {
        uVar11 = (param_2 - param_3 * (param_2 / param_3)) * 0x10000 | param_1 >> 0x10;
        uVar1 = uVar11 / param_3;
        return (param_1 & 0xffff | (uVar11 - param_3 * uVar1) * 0x10000) / param_3 | uVar1 << 0x10;
      }
    }
    if (param_3 == 0) {
      return param_1;
    }
    if (param_3 == 2) {
      return (uint)((param_2 & 1) != 0) << 0x1f | param_1 >> 1;
    }
    return param_1;
  }
  if (param_2 <= param_4 && (uint)(param_3 <= param_1) <= param_2 - param_4) {
    return 0;
  }
  if (0xffff < param_4) {
    uVar1 = param_2 / param_4;
    param_2 = param_2 - param_4 * uVar1;
    uVar11 = (uint)((ulonglong)param_3 * (ulonglong)uVar1 >> 0x20);
    if (param_2 <= uVar11 &&
        (uint)((uint)((ulonglong)param_3 * (ulonglong)uVar1) <= param_1) <= param_2 - uVar11) {
      uVar1 = uVar1 - 1;
    }
    return uVar1;
  }
  uVar11 = LZCOUNT(param_4) - 0xf;
  uVar7 = LZCOUNT(param_4) - LZCOUNT(param_2);
  uVar1 = param_3 << (uVar11 & 0xff);
  uVar11 = 0x20 - uVar11 & 0x1f;
  uVar11 = ((param_4 ^ param_3) >> uVar11 | (param_4 ^ param_3) << 0x20 - uVar11) ^ uVar1;
  uVar10 = uVar7 - 0xf;
  if (uVar7 < 0xf || uVar10 == 0) {
LAB_0047cd04:
    uVar7 = LZCOUNT(param_2) + -0xf + uVar7;
    uVar10 = param_1 << (uVar7 & 0xff);
    uVar7 = 0x20 - uVar7 & 0x1f;
    uVar7 = ((param_2 ^ param_1) >> uVar7 | (param_2 ^ param_1) << 0x20 - uVar7) ^ uVar10;
    uVar2 = uVar7 / uVar11;
    uVar7 = uVar7 - uVar11 * uVar2;
    uVar11 = (uint)((ulonglong)uVar1 * (ulonglong)uVar2 >> 0x20);
    if (uVar7 <= uVar11 &&
        (uint)((uint)((ulonglong)uVar1 * (ulonglong)uVar2) <= uVar10) <= uVar7 - uVar11) {
      uVar2 = uVar2 - 1;
    }
    return uVar2;
  }
LAB_0047cd92:
  uVar2 = param_1 << LZCOUNT(param_2);
  uVar7 = 0x20U - LZCOUNT(param_2) & 0x1f;
  uVar3 = ((param_2 ^ param_1) >> uVar7 | (param_2 ^ param_1) << 0x20 - uVar7) ^ uVar2;
  uVar12 = uVar3 / uVar11;
  uVar3 = uVar3 - uVar11 * uVar12;
  uVar5 = (uint)((ulonglong)uVar1 * (ulonglong)uVar12);
  uVar8 = (uint)((ulonglong)uVar1 * (ulonglong)uVar12 >> 0x20);
  uVar7 = uVar2 - uVar5;
  uVar4 = (uVar3 - uVar8) - (uint)(uVar5 > uVar2);
  if (uVar3 <= uVar8 && (uint)(uVar5 <= uVar2) <= uVar3 - uVar8) {
    uVar12 = uVar12 - 1;
    bVar13 = CARRY4(uVar7,uVar1);
    uVar7 = uVar7 + uVar1;
    uVar4 = uVar4 + uVar11 + (uint)bVar13;
  }
  if (0xe < uVar10) {
    uVar10 = uVar10 - 0xf;
    uVar3 = uVar4 << 0xf | uVar7 >> 0x11;
    uVar9 = uVar3 / uVar11;
    uVar3 = uVar3 - uVar11 * uVar9;
    uVar5 = (uint)((ulonglong)uVar1 * (ulonglong)uVar9);
    uVar8 = (uint)((ulonglong)uVar1 * (ulonglong)uVar9 >> 0x20);
    uVar2 = uVar7 * 0x8000;
    uVar7 = uVar2 - uVar5;
    uVar4 = (uVar3 - uVar8) - (uint)(uVar5 > uVar2);
    if (uVar3 <= uVar8 && (uint)(uVar5 <= uVar2) <= uVar3 - uVar8) {
      uVar9 = uVar9 - 1;
      bVar13 = CARRY4(uVar7,uVar1);
      uVar7 = uVar7 + uVar1;
      uVar4 = uVar4 + uVar11 + (uint)bVar13;
    }
    uVar12 = uVar9 | uVar12 << 0xf;
  }
  if (uVar10 != 0) {
    uVar3 = uVar7 << (uVar10 & 0xff);
    uVar2 = 0x20 - uVar10 & 0x1f;
    uVar7 = ((uVar4 ^ uVar7) >> uVar2 | (uVar4 ^ uVar7) << 0x20 - uVar2) ^ uVar3;
    uVar2 = uVar7 / uVar11;
    uVar7 = uVar7 - uVar11 * uVar2;
    uVar11 = (uint)((ulonglong)uVar1 * (ulonglong)uVar2 >> 0x20);
    if (uVar7 <= uVar11 &&
        (uint)((uint)((ulonglong)uVar1 * (ulonglong)uVar2) <= uVar3) <= uVar7 - uVar11) {
      uVar2 = uVar2 - 1;
    }
    return uVar12 << (uVar10 & 0xff) | uVar2;
  }
  return uVar12;
}

