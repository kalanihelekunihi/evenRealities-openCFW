
undefined4 gx8002_audio_out_config_buffer(void)

{
  undefined4 uVar1;
  uint uVar2;
  
  if (*piRam1020540c == 0) {
    gx8002_printf(PTR_s__AOUT_ERROR___s__d_10205414,PTR_s_gx_audio_out_config_buffer_10205410,0xff);
    uVar1 = 0xffffffff;
  }
  else {
    uVar2 = *(uint *)(*piRam1020540c + 0x18);
    if (uVar2 == 0) {
      uVar1 = 0;
    }
    else {
      uVar1 = (*(code *)(uVar2 & 0xfffffffe))();
    }
  }
  return uVar1;
}

