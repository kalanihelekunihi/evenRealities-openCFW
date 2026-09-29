
undefined4 gx_audio_in_set_i2s_clock(uint param_1)

{
  uRam00000000 = uRam00000000 & 0xf8ffffff | (param_1 & 7) << 0x18;
  return 0;
}

