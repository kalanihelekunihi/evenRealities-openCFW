
uint FUN_1001283c(uint *param_1)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  
  uVar1 = *param_1;
  uVar2 = param_1[3];
  if (uVar1 < 2) {
    return (uVar2 & 0xfffffff) >> 7 | 0x400000;
  }
  if (uVar1 != 4) {
    if (uVar1 == 2) {
      return 0;
    }
    if (uVar2 != 0) {
      uVar1 = param_1[2];
      if ((int)uVar1 < -0x7e) {
        uVar1 = -uVar1 - 0x7e;
        if (0x19 < (int)uVar1) {
          return 0;
        }
        uVar3 = uVar2 >> (uVar1 & 0x3f);
        uVar1 = (uint)((uVar2 & (1 << (uVar1 & 0x3f)) - 1U) != 0);
        uVar2 = uVar1 | uVar3;
        if ((uVar1 | uVar3 & 0x7f) == 0x40) {
          if ((uVar3 & 0x80) != 0) {
            uVar2 = uVar2 + 0x40;
          }
        }
        else {
          uVar2 = uVar2 + 0x3f;
        }
        return (uVar2 & 0x1fffffff) >> 7;
      }
      if ((int)uVar1 < 0x80) {
        if ((uVar2 & 0x7f) == 0x40) {
          if ((uVar2 & 0x80) != 0) {
            uVar2 = uVar2 + 0x40;
          }
        }
        else {
          uVar2 = uVar2 + 0x3f;
        }
        if ((int)uVar2 < 0) {
          uVar2 = uVar2 >> 1;
        }
        return (uVar2 & 0x1fffffff) >> 7;
      }
    }
  }
  return 0;
}

