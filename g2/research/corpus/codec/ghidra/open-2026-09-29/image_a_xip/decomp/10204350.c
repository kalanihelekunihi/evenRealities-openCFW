
undefined4 gx_audio_in_set_dc_enable(int param_1,int param_2)

{
  if (param_1 == 1) {
    uRam0000000c = uRam0000000c & 0xfffffeff | ((byte)~(param_2 != 0) & 1) << 8;
  }
  else if (param_1 == 2) {
    uRam00000028 = uRam00000028 & 0xfffffeff | ((byte)~(param_2 != 0) & 1) << 8;
    uRam0000002c = uRam0000002c & 0xfffffeff | ((byte)~(param_2 != 0) & 1) << 8;
  }
  else if (param_1 == 4) {
    uRam00000048 = uRam00000048 & 0xfffffeff | ((byte)~(param_2 != 0) & 1) << 8;
    uRam0000004c = uRam0000004c & 0xfffffeff | ((byte)~(param_2 != 0) & 1) << 8;
  }
  return 0;
}

