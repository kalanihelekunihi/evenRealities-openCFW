
uint FUN_0057dc54(uint param_1,uint param_2,uint param_3,uint param_4)

{
  longlong lVar1;
  bool bVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;
  int iVar9;
  uint uVar10;
  uint uVar11;
  bool bVar12;
  
  uVar3 = param_4 * 2;
  uVar6 = param_2 >> 0x14 & 0x7ff;
  uVar8 = (param_4 & 0x7fffffff) >> 0x14;
  if ((uVar8 == 0 || uVar6 == 0x7ff) || uVar8 == 0x7ff) {
    bVar12 = uVar3 == 0 && param_3 == 0;
    if (uVar3 != 0 || param_3 != 0) {
      bVar12 = uVar6 == 0x7ff;
    }
    if (!bVar12) {
      bVar12 = uVar8 == 0x7ff;
    }
    if (bVar12) {
      uVar8 = param_2 * 2;
      uVar6 = uVar3;
      if (0xffdfffff < uVar8) {
        param_2 = 0x7fffffff;
        uVar6 = uVar8;
      }
      if (uVar6 != 0xffe00000) {
        param_2 = 0x7fffffff;
      }
      if (0xffdfffff < uVar8 || 0xffdfffff < uVar3) {
        return param_1;
      }
      uVar3 = (*DAT_00577c38)(param_1,param_2);
      return uVar3;
    }
    uVar8 = param_2 * 2;
    bVar12 = uVar8 <= uVar3;
    if (uVar3 == uVar8) {
      bVar12 = param_1 <= param_3;
    }
    bVar2 = uVar3 == uVar8 && param_3 == param_1;
    if (bVar12) {
LAB_0057dd10:
      if (bVar2) {
        return 0;
      }
      return param_1;
    }
    param_4 = param_4 & 0x7fffffff;
    iVar9 = LZCOUNT(param_4);
    if (param_4 == 0) {
      iVar9 = LZCOUNT(param_3) + 0x20;
    }
    uVar8 = iVar9 - 0xb;
    if (uVar8 < 0x20) {
      uVar3 = param_4 << (uVar8 & 0xff) | param_3 >> (0x20 - uVar8 & 0xff);
    }
    else {
      uVar3 = param_3 << (iVar9 - 0x2bU & 0xff);
    }
    param_3 = param_3 << (uVar8 & 0xff);
    uVar8 = 1 - uVar8;
    if (uVar6 == 0) {
      param_2 = param_2 & 0x7fffffff;
      iVar9 = LZCOUNT(param_2);
      if (param_2 == 0) {
        iVar9 = LZCOUNT(param_1) + 0x20;
      }
      uVar6 = iVar9 - 0xb;
      if (uVar6 < 0x20) {
        uVar5 = param_2 << (uVar6 & 0xff) | param_1 >> (0x20 - uVar6 & 0xff);
      }
      else {
        uVar5 = param_1 << (iVar9 - 0x2bU & 0xff);
      }
      param_1 = param_1 << (uVar6 & 0xff);
      uVar6 = 1 - uVar6;
      goto LAB_0057dc88;
    }
  }
  else {
    uVar5 = param_2 * 2;
    bVar12 = uVar5 <= uVar3;
    if (uVar3 == uVar5) {
      bVar12 = param_1 <= param_3;
    }
    bVar2 = uVar3 == uVar5 && param_3 == param_1;
    if (bVar12) goto LAB_0057dd10;
    uVar3 = (uVar3 & 0x1fffff) >> 1 | 0x100000;
  }
  uVar5 = param_2 & 0xfffff | 0x100000;
LAB_0057dc88:
  uVar7 = (uVar6 - uVar8) - 0xb;
  if (10 < uVar6 - uVar8 && uVar7 != 0) {
    do {
      uVar4 = uVar5 << 0xb | param_1 >> 0x15;
      uVar6 = uVar4 / uVar3;
      uVar4 = uVar4 - uVar3 * uVar6;
      lVar1 = (ulonglong)param_3 * (ulonglong)uVar6;
      uVar11 = (uint)lVar1;
      uVar10 = (uint)((ulonglong)lVar1 >> 0x20);
      uVar6 = param_1 * 0x800;
      param_1 = uVar6 - uVar11;
      uVar5 = (uVar4 - uVar10) - (uint)(uVar11 > uVar6);
      if (uVar4 <= uVar10 && (uint)(uVar11 <= uVar6) <= uVar4 - uVar10) {
        bVar12 = CARRY4(param_1,param_3);
        param_1 = param_1 + param_3;
        uVar5 = uVar5 + uVar3 + (uint)bVar12;
      }
      if (param_1 == 0 && uVar5 == 0) {
        return 0;
      }
      bVar12 = 10 < uVar7;
      uVar7 = uVar7 - 0xb;
    } while (bVar12 && uVar7 != 0);
  }
  uVar7 = uVar7 + 0xb;
  uVar4 = param_1 << (uVar7 & 0xff);
  uVar7 = uVar5 << (uVar7 & 0xff) | param_1 >> (0x20 - uVar7 & 0xff);
  uVar6 = uVar7 / uVar3;
  uVar7 = uVar7 - uVar3 * uVar6;
  lVar1 = (ulonglong)param_3 * (ulonglong)uVar6;
  uVar11 = (uint)lVar1;
  uVar10 = (uint)((ulonglong)lVar1 >> 0x20);
  uVar5 = uVar4 - uVar11;
  uVar6 = (uVar7 - uVar10) - (uint)(uVar11 > uVar4);
  if (uVar7 <= uVar10 && (uint)(uVar11 <= uVar4) <= uVar7 - uVar10) {
    bVar12 = CARRY4(uVar5,param_3);
    uVar5 = uVar5 + param_3;
    uVar6 = uVar6 + uVar3 + (uint)bVar12;
  }
  uVar3 = uVar5;
  if (uVar6 == 0) {
    uVar8 = uVar8 - 0x20;
    uVar3 = 0;
    uVar6 = uVar5;
  }
  if (uVar6 != 0) {
    iVar9 = LZCOUNT(uVar6);
    uVar6 = uVar6 << iVar9 | uVar3 >> (0x20U - iVar9 & 0xff);
    uVar3 = uVar3 << iVar9;
    if (-0xb < (int)(uVar8 - iVar9)) {
      return uVar3 >> 0xb | uVar6 << 0x15;
    }
    iVar9 = -((uVar8 - iVar9) + 10);
    uVar5 = iVar9 + 0xb;
    uVar8 = iVar9 - 0x15;
    if ((int)uVar5 < 0x20) {
      uVar7 = uVar5 & 0xff;
      uVar4 = uVar5 & 0xff;
      uVar8 = 0x20 - uVar5 & 0xff;
      return (uVar3 >> (uVar5 & 0xff)) + (uVar6 << (0x20 - uVar5 & 0xff)) +
             (uint)(0x80000000 < uVar3 << uVar8 ||
                   (uVar3 << uVar8) + 0x80000000 <
                   (uint)(uVar8 == 0 &&
                          (uVar4 == 0 &&
                           (uVar7 == 0 && 0x1f < uVar5 ||
                           uVar7 != 0 && (uVar3 >> uVar7 - 1 & 1) != 0) ||
                          uVar4 != 0 && (uVar6 >> uVar4 - 1 & 1) != 0) ||
                         uVar8 != 0 && (uVar3 << uVar8 - 1 & 0x80000000) != 0));
    }
    if ((int)uVar5 < 0x41) {
      uVar5 = 0x20 - uVar8 & 0xff;
      uVar7 = uVar3 >> 1 | uVar6 << uVar5;
      return (uVar6 >> (uVar8 & 0xff)) + (uVar6 << uVar5) +
             (uint)(0x80000000 < uVar7 ||
                   uVar7 + 0x80000000 <
                   (uint)(uVar5 == 0 && (uVar3 & 1) != 0 ||
                         uVar5 != 0 && (uVar6 << uVar5 - 1 & 0x80000000) != 0));
    }
  }
  return 0;
}

