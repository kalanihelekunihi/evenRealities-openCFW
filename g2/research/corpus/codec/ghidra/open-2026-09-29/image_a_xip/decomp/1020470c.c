
undefined4 gx_audio_in_set_fftvad_curve_5(uint param_1)

{
  undefined4 uVar1;
  
  if (param_1 < 0x2001) {
    uRam00000194 = uRam00000194 & 0xffff0000 | param_1 & 0xffff;
    uVar1 = 0;
  }
  else {
    uVar1 = 0xffffffff;
  }
  return uVar1;
}

