
undefined4 FUN_005b89f0(byte param_1)

{
  if (param_1 == 1) {
    return 0;
  }
  if (param_1 != 0) {
    if (param_1 == 3) {
      if (*(int *)(DAT_005b8d78 + 0x58) != 1) {
        return DAT_005b8d80;
      }
      return DAT_005b8d7c;
    }
    if (param_1 < 3) {
      if (*(int *)(DAT_005b8d78 + 0x7c) != 0) {
        return DAT_005b8d74;
      }
      return DAT_005b8d70;
    }
    if (param_1 == 5) {
      return DAT_005b8d64;
    }
    if (param_1 < 5) {
      return DAT_005b8d60;
    }
    if (param_1 == 7) {
      return DAT_005b8d68;
    }
    if (param_1 < 7) {
      return DAT_005b8d84;
    }
    if (param_1 == 9) {
      return DAT_005b8d6c;
    }
    if (param_1 < 9) {
      return DAT_005b8dc8;
    }
  }
  return 0;
}

