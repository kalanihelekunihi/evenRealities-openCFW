
undefined4 FUN_10005cbc(uint param_1,int param_2)

{
  if (param_2 == 0) {
    uRam00000100 = uRam00000100 & ~param_1;
    uRam00000104 = param_1;
    return 0;
  }
  uRam00000104 = param_1;
  uRam00000100 = param_1 | uRam00000100;
  return 0;
}

