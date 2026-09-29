
undefined4 gx_audio_in_set_fftvad_curve_2(uint param_1,uint param_2)

{
  undefined4 uVar1;
  
  if ((param_1 < 0xc01) && (param_2 < 0x1e01)) {
    uRam00000188 = param_1 & 0xffff | param_2 << 0x10;
    uVar1 = 0;
  }
  else {
    uVar1 = 0xffffffff;
  }
  return uVar1;
}

