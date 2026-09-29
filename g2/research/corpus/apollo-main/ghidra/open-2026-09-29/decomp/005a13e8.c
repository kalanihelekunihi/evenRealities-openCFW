
undefined4 FUN_005a13e8(uint *param_1,undefined4 *param_2,undefined4 *param_3)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  
  uVar3 = *DAT_005a1df4;
  uVar4 = ((byte)param_1[4] & 0xf) << 8;
  if (*(char *)((int)param_1 + 0x11) == '\x01') {
    uVar4 = uVar3 & 0xfffff0f0 | uVar4 | 1;
  }
  else if (*(char *)((int)param_1 + 0x11) == '\0') {
    uVar4 = uVar3 & 0xfffff0f0 | uVar4;
  }
  else if ((*DAT_005a1df8 & 3) == 2) {
    uVar4 = uVar3 & 0xfffff0f0 | uVar4 | 1;
  }
  else {
    uVar4 = uVar3 & 0xfffff0f0 | uVar4;
  }
  if ((((*(char *)((int)param_1 + 0x12) == '\x01') || (*(char *)((int)param_1 + 0x12) == '\x02')) ||
      ((*param_1 & 0x3fffffff) != 0)) || ((param_1[1] & 0x4c4) != 0)) {
    uVar4 = uVar4 & 0xffffff0f | 0x10;
  }
  else {
    uVar4 = uVar4 & 0xffffff0f;
  }
  if (*(char *)((int)param_1 + 0x12) == '\x02') {
    uVar4 = uVar4 & 0xffff0fff | 0x2000;
  }
  else if (*(char *)((int)param_1 + 0x12) == '\x01') {
    uVar4 = uVar4 & 0xffff0fff | 0x1000;
  }
  else {
    uVar4 = uVar4 & 0xffff0fff;
  }
  if (((*param_1 & 0x3fffffff) == 0) && ((param_1[1] & 0x4c4) == 0)) {
    uVar4 = uVar4 & 0xfff0ffff;
  }
  else {
    uVar4 = uVar4 & 0xfff0ffff | 0x10000;
  }
  if ((*param_1 & 0xc00000) == 0) {
    uVar4 = uVar4 & 0xff0fffff;
  }
  else {
    uVar4 = uVar4 & 0xff0fffff | 0x100000;
  }
  uVar3 = DAT_005a1e00 & uVar4;
  if (uVar3 == 0) {
    if ((int)((uint)*DAT_005a1e08 << 0x1f) < 0) {
      *param_2 = 7;
    }
    else {
      *param_2 = 3;
    }
  }
  else if (uVar3 == 1) {
    if ((int)((uint)*DAT_005a1e08 << 0x1f) < 0) {
      *param_2 = 0xf;
    }
    else {
      *param_2 = 0xb;
    }
  }
  else if (uVar3 == 0x10) {
    *param_2 = 7;
  }
  else if (uVar3 == 0x11) {
LAB_005a168a:
    *param_2 = 0xf;
  }
  else if (uVar3 == 0x100) {
    if ((int)((uint)*DAT_005a1e08 << 0x1f) < 0) {
      *param_2 = 6;
    }
    else {
      *param_2 = 2;
    }
  }
  else if (uVar3 == 0x101) {
    if ((int)((uint)*DAT_005a1e08 << 0x1f) < 0) {
      *param_2 = 0xe;
    }
    else {
      *param_2 = 10;
    }
  }
  else if (uVar3 == 0x110) {
    *param_2 = 6;
  }
  else if (uVar3 == 0x111) {
LAB_005a1684:
    *param_2 = 0xe;
  }
  else if (uVar3 == 0x200) {
    if ((int)((uint)*DAT_005a1e08 << 0x1f) < 0) {
      *param_2 = 5;
    }
    else {
      *param_2 = 1;
    }
  }
  else if (uVar3 == 0x201) {
    if ((int)((uint)*DAT_005a1e08 << 0x1f) < 0) {
      *param_2 = 0xd;
    }
    else {
      *param_2 = 9;
    }
  }
  else if (uVar3 == 0x210) {
    *param_2 = 5;
  }
  else if (uVar3 == 0x211) {
LAB_005a167e:
    *param_2 = 0xd;
  }
  else if (uVar3 == 0x300) {
    if ((int)((uint)*DAT_005a1e08 << 0x1f) < 0) {
      *param_2 = 4;
    }
    else {
      *param_2 = 0;
    }
  }
  else if (uVar3 == 0x301) {
    if ((int)((uint)*DAT_005a1e08 << 0x1f) < 0) {
      *param_2 = 0xc;
    }
    else {
      *param_2 = 8;
    }
  }
  else if (uVar3 == 0x310) {
    *param_2 = 4;
  }
  else {
    iVar1 = uVar3 - 0x311;
    if (iVar1 == 0) {
LAB_005a1678:
      *param_2 = 0xc;
    }
    else {
      iVar2 = iVar1 - DAT_005a1e04;
      if (iVar1 == DAT_005a1e04) {
        *param_2 = 0x13;
      }
      else {
        if (iVar2 == 1) goto LAB_005a168a;
        if (iVar2 == 0x100) {
          *param_2 = 0x12;
        }
        else {
          if (iVar2 == 0x101) goto LAB_005a1684;
          if (iVar2 == 0x200) {
            *param_2 = 0x11;
          }
          else {
            if (iVar2 == 0x201) goto LAB_005a167e;
            if (iVar2 != 0x300) {
              if (iVar2 != 0x301) {
                return 5;
              }
              goto LAB_005a1678;
            }
            *param_2 = 0x10;
          }
        }
      }
    }
  }
  uVar4 = uVar4 & DAT_005a1e0c;
  if (uVar4 == 0) {
    *param_3 = 0;
    return 0;
  }
  if (uVar4 == 1) {
    if ((int)((uint)*DAT_005a1e08 << 0x1f) < 0) {
      *param_3 = 7;
      return 0;
    }
    *param_3 = 1;
    return 0;
  }
  if (uVar4 == 0x1000) {
LAB_005a16c2:
    *param_3 = 2;
  }
  else {
    if (uVar4 == 0x1001) {
LAB_005a16ce:
      *param_3 = 4;
      return 0;
    }
    if (uVar4 == 0x2000) {
LAB_005a16c8:
      *param_3 = 3;
      return 0;
    }
    if (uVar4 != 0x2001) {
      if (uVar4 == 0x10000) {
        *param_3 = 6;
        return 0;
      }
      if (uVar4 == 0x10001) {
        *param_3 = 7;
        return 0;
      }
      if (uVar4 == 0x11000) goto LAB_005a16c2;
      if (uVar4 == DAT_005a1e10) goto LAB_005a16ce;
      if (uVar4 == 0x12000) goto LAB_005a16c8;
      if (uVar4 != DAT_005a1e14) {
        return 5;
      }
    }
    *param_3 = 5;
  }
  return 0;
}

