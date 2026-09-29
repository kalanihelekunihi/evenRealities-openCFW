
undefined4 gx_audio_in_set_fftvad_curve_4(uint param_1,uint param_2)

{
  undefined4 uVar1;
  
  if ((param_1 < 0x1401) && (param_2 < 0x1401)) {
    uRam00000190 = param_1 & 0xffff | param_2 << 0x10;
    uVar1 = 0;
  }
  else {
    uVar1 = 0xffffffff;
  }
  return uVar1;
}

