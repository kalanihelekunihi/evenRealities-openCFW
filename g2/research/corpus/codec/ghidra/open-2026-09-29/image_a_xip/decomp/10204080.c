
undefined4
gx8002_audio_output_logfbank(uint param_1,uint param_2,uint param_3,uint param_4,uint param_5)

{
  undefined4 uVar1;
  uint uVar2;
  
  if ((((param_1 & 7) == 0) && (uVar2 = (param_2 / 0x50) * 0x50, param_2 == uVar2)) &&
     (param_2 == param_3 * (param_2 / param_3))) {
    uRam00000160 = param_1 & 0xfffffff8;
    uRam00000104 = 0x2000;
    uRam00000108 = uRam00000108 & 0xff00ffff | (param_4 & 3) << 0x13 | (param_5 & 7) << 0x10 |
                   0x600000;
    uRam0000015c = param_3;
    uRam00000164 = uVar2;
    *(uint *)(DAT_10204128 + 4) = *(uint *)(DAT_10204128 + 4) | 4;
    uVar1 = 0;
  }
  else {
    uVar1 = 0xffffffff;
  }
  return uVar1;
}

