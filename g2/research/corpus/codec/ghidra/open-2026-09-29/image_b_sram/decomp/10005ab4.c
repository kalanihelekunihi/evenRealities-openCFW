
undefined4 gx_audio_in_set_logfbank_enable(uint param_1,uint param_2)

{
  uRam00000180 = uRam00000180 & 0xfffffff | (param_2 & 1) << 0x1c | (param_1 & 1) << 0x1d |
                 (param_1 & 1) << 0x1e | (uint)(byte)~(param_1 != 0) << 0x1f;
  return 0;
}

