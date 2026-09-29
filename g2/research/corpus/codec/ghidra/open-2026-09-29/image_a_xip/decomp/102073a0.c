
undefined4 gx8002_audio_input_update_read(int param_1)

{
  undefined4 uVar1;
  
  if (puRam102073b8[1] < param_1 + *puRam102073b8) {
    uVar1 = 0xffffffff;
  }
  else {
    *puRam102073b8 = param_1 + *puRam102073b8;
    uVar1 = 0;
  }
  return uVar1;
}

