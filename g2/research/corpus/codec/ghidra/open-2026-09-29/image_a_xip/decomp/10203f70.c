
undefined4 gx_audio_in_set_input_channel(int param_1,uint param_2,uint param_3)

{
  if (param_1 == 4) {
    uRam00000048 = uRam00000048 & 0xfffffff0 | param_2 & 0xf;
    uRam0000004c = uRam0000004c & 0xfffffff0 | param_3 & 0xf;
  }
  else if (param_1 == 2) {
    uRam00000028 = uRam00000028 & 0xfffffff0 | param_2 & 0xf;
    uRam0000002c = uRam0000002c & 0xfffffff0 | param_3 & 0xf;
  }
  return 0;
}

