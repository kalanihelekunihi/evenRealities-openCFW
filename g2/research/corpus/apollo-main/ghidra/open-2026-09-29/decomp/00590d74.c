
undefined4 FUN_00590d74(int param_1,int param_2)

{
  if (param_2 == 0) {
    if (param_1 == 8000) {
      return 0;
    }
    if (param_1 == 16000) {
      return 1;
    }
    if (param_1 == 24000) {
      return 2;
    }
    if (param_1 == 32000) {
      return 3;
    }
    if (param_1 == 48000) {
      return 4;
    }
  }
  else {
    if (param_1 == 48000) {
      return 5;
    }
    if (param_1 == DAT_005915a4) {
      return 6;
    }
  }
  return 7;
}

