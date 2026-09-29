
undefined4 gx_audio_in_set_fftvad_curve_3(ushort param_1,short param_2)

{
  undefined4 uVar1;
  
  if ((param_1 < 0x1001) && ((ushort)(param_2 + 0x1400U) < 0x2801)) {
    uRam0000018c = CONCAT22(param_2,param_1);
    uVar1 = 0;
  }
  else {
    uVar1 = 0xffffffff;
  }
  return uVar1;
}

