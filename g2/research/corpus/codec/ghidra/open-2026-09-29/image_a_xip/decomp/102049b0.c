
undefined4 gx8002_audio_channel_field(int param_1,uint param_2)

{
  *(uint *)((param_1 + 10) * 4) =
       *(uint *)((param_1 + 10) * 4) & 0xffff03ff | (param_2 & 0x3f) << 10;
  return 0;
}

