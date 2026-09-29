
undefined4 FUN_10004078(int param_1,int *param_2,int param_3)

{
  if (param_3 == 0) {
    param_1 = *param_2;
  }
  if (param_1 == 0x40) {
    return 5;
  }
  if (param_1 < 0x41) {
    if (param_1 == 8) {
      return 2;
    }
    if (param_1 < 9) {
      if (param_1 == 4) {
        return 1;
      }
    }
    else {
      if (param_1 == 0x10) {
        return 3;
      }
      if (param_1 == 0x20) {
        return 4;
      }
    }
  }
  else {
    if (param_1 == 0x100) {
      return 7;
    }
    if (param_1 < 0x101) {
      if (param_1 == 0x80) {
        return 6;
      }
    }
    else {
      if (param_1 == 0x200) {
        return 8;
      }
      if (param_1 == 0x400) {
        return 9;
      }
    }
  }
  return 0;
}

