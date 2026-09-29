
undefined4 gx_audio_in_set_fftvad_w(uint param_1)

{
  uRam00000158 = uRam00000158 & 0xfff000ff | (param_1 & 0xf) << 8 | (param_1 >> 8 & 0xf) << 0xc |
                 (param_1 >> 0x10 & 0xf) << 0x10;
  return 0;
}

