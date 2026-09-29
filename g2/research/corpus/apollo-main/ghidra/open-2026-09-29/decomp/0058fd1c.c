
undefined4 FUN_0058fd1c(int param_1)

{
  undefined4 uVar1;
  
  if ((param_1 == 0) || (param_1 == 0x100)) {
    return 6;
  }
  if (param_1 - 0x200U < 8) {
LAB_0058fd54:
    uVar1 = 5;
  }
  else {
    if (6 < param_1 - 0x208U) {
      if (param_1 - 0x20fU < 7) {
        if (*DAT_00590810 << 1 < 0) {
          return 3;
        }
        return 2;
      }
      if ((param_1 != 0x216) && (1 < param_1 - 0x10200U)) {
        if (param_1 == 0x10202) {
          return 2;
        }
        if (param_1 - 0x10200U != 3) {
          return 7;
        }
        goto LAB_0058fd54;
      }
    }
    uVar1 = 4;
  }
  return uVar1;
}

