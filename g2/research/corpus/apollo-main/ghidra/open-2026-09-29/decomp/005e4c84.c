
undefined4 FUN_005e4c84(char param_1)

{
  undefined4 unaff_r7;
  
  if (*(int *)(DAT_005e53b4 + 4) != 0) {
    if (param_1 == '\0') {
      if (*(char *)(DAT_005e53b4 + 0x27e) == '\0') {
        FUN_0043dfa4(*(undefined4 *)(DAT_005e53b4 + 4),1);
        FUN_005ea30c();
      }
    }
    else {
      FUN_0043ded4(*(undefined4 *)(DAT_005e53b4 + 4),1);
    }
  }
  return unaff_r7;
}

