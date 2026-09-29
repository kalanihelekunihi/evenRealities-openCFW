
undefined4 FUN_0055bd2e(int param_1,uint param_2)

{
  if ((*(uint *)(DAT_0055c548 + param_1 * 0x1000 + 0x11c) & 0xf) >> 1 == param_2) {
    *(undefined4 *)(DAT_0055c548 + param_1 * 0x1000 + 0x11c) = 1;
  }
  else {
    if ((*(uint *)(DAT_0055c548 + param_1 * 0x1000 + 0x11c) & 0xff) >> 5 != param_2) {
      return 0;
    }
    *(undefined4 *)(DAT_0055c548 + param_1 * 0x1000 + 0x11c) = 0x10;
  }
  return 1;
}

