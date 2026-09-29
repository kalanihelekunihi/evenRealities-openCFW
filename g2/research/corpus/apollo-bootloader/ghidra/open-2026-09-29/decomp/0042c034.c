
undefined4 hw_status_route_42c034(int param_1,uint param_2)

{
  if ((*(uint *)(DAT_0042c6e8 + param_1 * 0x1000 + 0x11c) & 0xf) >> 1 == param_2) {
    *(undefined4 *)(DAT_0042c6e8 + param_1 * 0x1000 + 0x11c) = 1;
  }
  else {
    if ((*(uint *)(DAT_0042c6e8 + param_1 * 0x1000 + 0x11c) & 0xff) >> 5 != param_2) {
      return 0;
    }
    *(undefined4 *)(DAT_0042c6e8 + param_1 * 0x1000 + 0x11c) = 0x10;
  }
  return 1;
}

