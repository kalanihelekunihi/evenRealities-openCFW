
undefined1 system_get_brightness_level(uint param_1)

{
  if (0xc < param_1) {
    param_1 = 0xc;
  }
  return *(undefined1 *)(DAT_0046c738 + param_1);
}

