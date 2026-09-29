
undefined4 gx8002_audio_output_pcm(uint param_1)

{
  int iVar1;
  uint in_stack_00000004;
  uint in_stack_00000008;
  
  if (param_1 == 1) {
    iVar1 = _pcm_channel_setting_isra_0(0);
    if (iVar1 == 0) {
      uRam00000108 = uRam00000108 & 0xffffff10 | in_stack_00000008 & 3 |
                     (in_stack_00000004 & 3) << 2 | 0x60;
LAB_1020401c:
      *(uint *)(DAT_1020407c + 4) = param_1 | *(uint *)(DAT_1020407c + 4);
      return 0;
    }
  }
  else if ((param_1 == 2) && (iVar1 = _pcm_channel_setting_isra_0(1), iVar1 == 0)) {
    uRam00000108 = uRam00000108 & 0xffff10ff | (in_stack_00000008 & 3) << 8 |
                   (in_stack_00000004 & 3) << 10 | 0x6000;
    goto LAB_1020401c;
  }
  return 0xffffffff;
}

