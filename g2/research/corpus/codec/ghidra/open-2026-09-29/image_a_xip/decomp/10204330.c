
undefined4 gx_audio_in_set_i2sin_mode(uint param_1)

{
  uRam00000004 = uRam00000004 & 0xfffeffff | (param_1 & 1) << 0x10;
  return 0;
}

