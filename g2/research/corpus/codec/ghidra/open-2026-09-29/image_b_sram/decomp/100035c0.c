
undefined4 FUN_100035c0(uint param_1,uint param_2)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  int local_28 [2];
  uint *puStack_20;
  uint *puStack_1c;
  int *piStack_18;
  int *piStack_14;
  
  if (0x19 < param_1) {
    return 0xffffffff;
  }
  if (param_2 == 2) {
    if (9 < param_1) {
      return 0xffffffff;
    }
    uVar4 = 1;
    if ((1 << (param_1 & 0x3f) & 0x247U) == 0) {
      return 0xffffffff;
    }
  }
  else if ((int)param_2 < 3) {
    uVar4 = 1;
  }
  else if (param_1 == 7) {
    param_2 = (int)param_2 >> 2;
    uVar4 = 1;
  }
  else {
    if (param_1 != 8) {
      return 0xffffffff;
    }
    param_2 = param_2 - 5;
    uVar4 = 3;
  }
  iVar1 = __module_get_info(param_1,local_28);
  if (iVar1 != 0) {
    return 0xffffffff;
  }
  uVar2 = (uint)*(char *)(local_28[0] + 6);
  if (uVar2 == 0xffffffff) {
    return 0xffffffff;
  }
  if (param_2 == 2) {
    if (param_1 != 8) {
      uVar2 = (uint)(char)(*(char *)(local_28[0] + 6) + '\x01');
      param_2 = 1;
      goto LAB_100035fa;
    }
    if ((*puStack_20 >> (uVar2 & 0x3f) & uVar4) == 2) {
      return 0;
    }
LAB_10003608:
    uVar3 = *puStack_1c >> ((int)*(char *)(local_28[0] + 5) & 0x3fU);
  }
  else {
LAB_100035fa:
    if ((*puStack_20 >> (uVar2 & 0x3f) & uVar4) == param_2) {
      return 0;
    }
    if ((0x16 < param_1) || ((0U >> (param_1 & 0x3f) & 1) == 0)) goto LAB_10003608;
    uVar3 = *puStack_1c >> ((int)*(char *)(DAT_10003784 + (param_1 + 1) * 0x10 + 5) & 0x3fU) &
            *puStack_1c >> ((int)*(char *)(DAT_10003784 + (param_1 + 2) * 0x10 + 5) & 0x3fU);
  }
  if ((~uVar3 & 1) != 0) {
    uVar3 = (uint)*(char *)(local_28[0] + 4);
    if (param_1 - 7 < 2) {
      *puStack_20 = param_2 << (uVar2 & 0x3f) | *puStack_20 & ~(uVar4 << (uVar2 & 0x3f));
      iVar1 = 1 << (uVar3 & 0x3f);
      *piStack_18 = iVar1;
      uVar2 = *puStack_1c;
      uVar4 = *puStack_20;
      if ((((uVar4 >> ((int)*(char *)(DAT_10003784 + 0x26) & 0x3fU) & 1) != 0) &&
          ((uVar2 >> ((int)*(char *)(DAT_10003784 + 0x25) & 0x3fU) & 1) != 0)) &&
         ((((uVar4 >> ((int)*(char *)(DAT_10003784 + 0x86) & 0x3fU) & 3) == 0 &&
           ((uVar2 >> ((int)*(char *)(DAT_10003784 + 0x85) & 0x3fU) & 1) == 0)) ||
          (((uVar4 >> ((int)*(char *)(DAT_10003784 + 0x76) & 0x3fU) |
            uVar2 >> ((int)*(char *)(DAT_10003784 + 0x75) & 0x3fU)) & 1) == 0)))) {
        *piStack_14 = iVar1;
      }
    }
    else {
      if (param_2 == 1) {
        *piStack_14 = 1 << (uVar3 & 0x3f);
        param_2 = 1;
        goto LAB_100036a4;
      }
      *puStack_20 = param_2 << (uVar2 & 0x3f) | *puStack_20 & ~(uVar4 << (uVar2 & 0x3f));
      *piStack_18 = 1 << (uVar3 & 0x3f);
    }
    return 0;
  }
LAB_100036a4:
  *puStack_20 = param_2 << (uVar2 & 0x3f) | *puStack_20 & ~(uVar4 << (uVar2 & 0x3f));
  return 0;
}

