
undefined4 gx_audio_in_set_i2sout_mode(uint param_1)

{
  uRam00000008 = uRam00000008 & 0xffffffef | (param_1 & 1) << 4;
  return 0;
}

