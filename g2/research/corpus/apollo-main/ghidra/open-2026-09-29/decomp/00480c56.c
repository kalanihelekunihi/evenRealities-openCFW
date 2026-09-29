
undefined4 FUN_00480c56(undefined1 *param_1)

{
  if (*DAT_00480ec8 << 0x17 < 0) {
    *param_1 = 2;
  }
  else if (*DAT_00480ec8 << 0x1f < 0) {
    *param_1 = 1;
  }
  else {
    *param_1 = 0;
  }
  return 0;
}

