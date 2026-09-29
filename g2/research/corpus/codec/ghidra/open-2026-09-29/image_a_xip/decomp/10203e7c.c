
undefined4 gx8002_audio_input_pdm(uint param_1)

{
  func_0x10025080(8,1);
  uRam00000028 = uRam00000028 & 0xffff03ff;
  uRam0000002c = uRam0000002c & 0xffff03ff;
  uRam00000000 = uRam00000000 & 0xffffbdff | (param_1 & 1) << 9 | 0x4000;
  *DAT_10203ec4 = *DAT_10203ec4 | 2;
  func_0x1002598c(10);
  return 0;
}

