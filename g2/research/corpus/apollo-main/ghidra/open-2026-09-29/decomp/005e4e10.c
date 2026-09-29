
undefined1 FUN_005e4e10(int param_1,undefined1 param_2)

{
  if (param_1 << 3 < 0) {
    param_2 = 2;
  }
  else if (param_1 << 2 < 0) {
    param_2 = 1;
  }
  else if (param_1 << 1 < 0) {
    param_2 = 0;
  }
  return param_2;
}

