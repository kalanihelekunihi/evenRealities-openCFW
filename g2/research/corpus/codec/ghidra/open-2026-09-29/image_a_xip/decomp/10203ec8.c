
void gx8002_audio_input_i2s
               (uint param_1,uint param_2,uint param_3,uint param_4,uint param_5,uint param_6)

{
  func_0x10025080(2,1);
  uRam00000004 = uRam00000004 & 0xbf80f003 | (param_1 & 0xf) << 4 | (param_2 & 7) << 8 |
                 (param_3 & 1) << 0x10 | (param_4 & 3) << 0x12 | (param_5 & 3) << 0x15 |
                 (uint)(2 < param_2) << 0x11 | (param_6 & 1) << 0xb | 0x40000000;
  *DAT_10203f6c = *DAT_10203f6c | 4;
  return;
}

