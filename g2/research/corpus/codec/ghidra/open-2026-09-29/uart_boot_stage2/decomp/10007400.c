
uint * FUN_10007400(uint *param_1,uint *param_2,uint *param_3)

{
  bool bVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;
  int iVar9;
  uint uVar10;
  uint local_2c;
  uint uStack_28;
  
  uVar2 = *param_1;
  if (uVar2 < 2) {
    return param_1;
  }
  uVar7 = *param_2;
  if (uVar7 < 2) {
    return param_2;
  }
  if (uVar2 == 4) {
    if (uVar7 != 4) {
      return param_1;
    }
    if (param_1[1] == param_2[1]) {
      return param_1;
    }
    return (uint *)PTR_DAT_1000772c;
  }
  if (uVar7 == 4) {
    return param_2;
  }
  if (uVar7 == 2) {
    if (uVar2 != 2) {
      return param_1;
    }
    *param_3 = 2;
    param_3[1] = param_1[1];
    param_3[2] = param_1[2];
    param_3[3] = param_1[3];
    uVar2 = param_2[1];
    param_3[4] = param_1[4];
    param_3[1] = param_1[1] & uVar2;
    return param_3;
  }
  if (uVar2 == 2) {
    return param_2;
  }
  uVar2 = param_1[2];
  uVar8 = param_2[2];
  uVar10 = uVar2 - uVar8;
  uVar7 = uVar10;
  if ((int)uVar10 < 0) {
    uVar7 = ~uVar10 + 1;
  }
  local_2c = param_1[3];
  uVar3 = param_1[4];
  uVar5 = param_2[3];
  uVar6 = param_2[4];
  uVar4 = uVar6;
  uStack_28 = uVar3;
  if ((int)uVar7 < 0x40) {
    if ((int)uVar10 < 1) {
      if (uVar10 != 0) {
        uVar10 = uVar7 - 0x20;
        bVar1 = (uVar10 & 0x80000000) == 0;
        uVar8 = local_2c >> (uVar7 & 0x3f) | (uVar3 << 1) << (0x1f - uVar7 & 0x3f);
        if (bVar1) {
          uVar8 = uVar3 >> (uVar10 & 0x3f);
        }
        uStack_28 = uVar3 >> (uVar7 & 0x3f);
        iVar9 = 1 << (uVar7 & 0x3f);
        uVar6 = 0;
        if (bVar1) {
          iVar9 = 0;
          uStack_28 = 0;
          uVar6 = 1 << (uVar10 & 0x3f);
        }
        uVar2 = uVar2 + uVar7;
        if (iVar9 == 0) {
          uVar6 = uVar6 - 1;
        }
        local_2c = uVar8 | ((local_2c & iVar9 - 1U) != 0 || (uVar3 & uVar6) != 0);
      }
      goto LAB_10007458;
    }
    uVar10 = uVar7 - 0x20;
    bVar1 = (uVar10 & 0x80000000) == 0;
    uVar8 = uVar5 >> (uVar7 & 0x3f) | (uVar6 << 1) << (0x1f - uVar7 & 0x3f);
    if (bVar1) {
      uVar8 = uVar6 >> (uVar10 & 0x3f);
    }
    iVar9 = 1 << (uVar7 & 0x3f);
    uVar4 = uVar6 >> (uVar7 & 0x3f);
    uVar7 = 0;
    if (bVar1) {
      iVar9 = 0;
      uVar4 = 0;
      uVar7 = 1 << (uVar10 & 0x3f);
    }
    if (iVar9 == 0) {
      uVar7 = uVar7 - 1;
    }
    uVar10 = param_1[1];
    uVar5 = ((iVar9 - 1U & uVar5) != 0 || (uVar7 & uVar6) != 0) | uVar8;
    if (uVar10 == param_2[1]) goto LAB_10007562;
  }
  else {
    if ((int)uVar8 < (int)uVar2) {
      uVar5 = 0;
      uVar4 = 0;
    }
    else {
      local_2c = 0;
      uStack_28 = 0;
      uVar2 = uVar8;
    }
LAB_10007458:
    uVar10 = param_1[1];
    if (uVar10 == param_2[1]) {
LAB_10007562:
      uVar7 = local_2c + uVar5;
      uVar8 = uStack_28 + uVar4 + (uint)CARRY4(local_2c,uVar5);
      param_3[1] = uVar10;
      param_3[2] = uVar2;
      param_3[3] = uVar7;
      param_3[4] = uVar8;
      goto LAB_1000757c;
    }
  }
  if (uVar10 == 0) {
    uVar7 = local_2c - uVar5;
    uVar8 = (uStack_28 - uVar4) - (uVar5 <= local_2c ^ 1);
  }
  else {
    uVar7 = uVar5 - local_2c;
    uVar8 = (uVar4 - uStack_28) - (local_2c <= uVar5 ^ 1);
  }
  if ((int)uVar8 < 0) {
    bVar1 = uVar7 == 0;
    uVar7 = -uVar7;
    uVar8 = -(bVar1 ^ 1) - uVar8;
    param_3[1] = 1;
    param_3[2] = uVar2;
    param_3[3] = uVar7;
    param_3[4] = uVar8;
  }
  else {
    param_3[1] = 0;
    param_3[2] = uVar2;
    param_3[3] = uVar7;
    param_3[4] = uVar8;
  }
  uVar2 = uVar8;
  if (uVar7 == 0) {
    uVar2 = uVar8 - 1;
  }
  if ((uVar2 < 0x10000000) && ((uVar2 != 0xfffffff || (uVar7 != 0)))) {
    uVar2 = param_3[2] - 1;
    do {
      uVar4 = uVar2;
      bVar1 = CARRY4(uVar7,uVar7);
      uVar7 = uVar7 * 2;
      uVar8 = uVar8 * 2 + (uint)bVar1;
      uVar10 = (uVar8 - 1) + (uint)(uVar7 != 0);
      uVar2 = uVar4 - 1;
      if (0xfffffff < uVar10) break;
    } while ((uVar10 != 0xfffffff) || (uVar7 != 0));
    param_3[3] = uVar7;
    param_3[4] = uVar8;
    param_3[2] = uVar4;
    *param_3 = 3;
    return param_3;
  }
LAB_1000757c:
  *param_3 = 3;
  if (0x1fffffff < uVar8) {
    param_3[3] = uVar7 >> 1 | uVar8 << 0x1f | uVar7 & 1;
    param_3[4] = uVar8 >> 1;
    param_3[2] = param_3[2] + 1;
  }
  return param_3;
}

