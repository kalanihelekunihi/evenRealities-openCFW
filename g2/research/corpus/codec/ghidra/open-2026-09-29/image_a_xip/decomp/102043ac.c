
undefined4 gx_audio_in_set_rough_gain(int param_1,uint param_2)

{
  if (param_1 == 1) {
    uRam0000000c = uRam0000000c & 0xffffff0f | (param_2 & 0xf) << 4;
  }
  else if (param_1 == 2) {
    uRam00000028 = uRam00000028 & 0xffffff0f | (param_2 & 0xf) << 4;
    uRam0000002c = uRam0000002c & 0xffffff0f | (param_2 & 0xf) << 4;
  }
  else if (param_1 == 4) {
    uRam00000048 = uRam00000048 & 0xffffff0f | (param_2 & 0xf) << 4;
    uRam0000004c = uRam0000004c & 0xffffff0f | (param_2 & 0xf) << 4;
  }
  return 0;
}

