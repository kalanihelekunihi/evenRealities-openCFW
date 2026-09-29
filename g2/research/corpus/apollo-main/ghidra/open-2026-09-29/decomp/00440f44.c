
undefined4 FUN_00440f44(byte param_1)

{
  uint uVar1;
  undefined4 uVar2;
  
  uVar1 = (uint)param_1;
  if (uVar1 == 6) {
    return 8;
  }
  if (uVar1 == 7) {
    return 1;
  }
  if (uVar1 == 8) {
    return 2;
  }
  if (uVar1 == 9) {
    return 4;
  }
  if (uVar1 == 10) {
    return 8;
  }
  if (uVar1 == 0xb) {
    return 1;
  }
  if (uVar1 == 0xc) {
    return 2;
  }
  if (uVar1 == 0xd) {
    return 4;
  }
  if (uVar1 == 0xe) {
    return 8;
  }
  if (uVar1 == 0xf) {
LAB_00440fb8:
    uVar2 = 0x18;
  }
  else {
    if (uVar1 - 0x10 < 2) {
      return 0x20;
    }
    if (uVar1 != 0x12) {
      if (uVar1 == 0x13) goto LAB_00440fb8;
      if (3 < uVar1 - 0x14) {
        if (uVar1 == 0x18) {
          return 8;
        }
        if (uVar1 != 0x26) {
          if (uVar1 == 0x30) {
            return 4;
          }
          if (2 < uVar1 - 0x31) {
            if (uVar1 - 0x34 < 2) {
              return 0xc;
            }
            return 0;
          }
          return 6;
        }
      }
    }
    uVar2 = 0x10;
  }
  return uVar2;
}

