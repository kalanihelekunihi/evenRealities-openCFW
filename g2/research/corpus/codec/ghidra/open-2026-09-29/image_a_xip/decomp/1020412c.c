
undefined4
gx8002_audio_output_spectrum
          (uint param_1,uint param_2,uint param_3,int param_4,uint param_5,uint param_6)

{
  undefined4 uVar1;
  
  uRam00000108 = uRam00000108 & 0xfff8ffff | (param_6 & 7) << 0x10;
  if (((param_3 & 0x7f) == 0) && ((param_2 & 7) == 0)) {
    if (param_1 == 1) {
      _pcm_channel_setting_isra_0(0,param_2,0,param_3,param_4 * 2);
      uRam00000108 = uRam00000108 & 0xffffff10 | 3 | (param_5 & 3) << 2 | 0x40 | (param_2 & 1) << 7
                     | 0x20;
    }
    else {
      if (param_1 != 2) goto LAB_1020421c;
      _pcm_channel_setting_isra_0(1,param_2,0,param_3,param_4 * 2);
      uRam00000108 = uRam00000108 & 0xffff10ff | 0x300 | (param_5 & 3) << 10 | 0x4000 |
                     (param_2 & 1) << 0xf | 0x2000;
    }
    uVar1 = 0;
    *(uint *)(DAT_10204224 + 4) = param_1 | *(uint *)(DAT_10204224 + 4);
  }
  else {
LAB_1020421c:
    uVar1 = 0xffffffff;
  }
  return uVar1;
}

