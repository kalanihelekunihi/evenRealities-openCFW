
undefined4 gx8002_audio_out_set_channel(void)

{
  undefined4 uVar1;
  uint uVar2;
  
  if (*piRam10205524 == 0) {
    gx8002_printf(PTR_s__AOUT_ERROR___s__d_1020552c,PTR_s_gx_audio_out_set_channel_10205528,0x16d);
    uVar1 = 0xffffffff;
  }
  else {
    uVar2 = *(uint *)(*piRam10205524 + 0x48);
    if (uVar2 == 0) {
      uVar1 = 0;
    }
    else {
      uVar1 = (*(code *)(uVar2 & 0xfffffffe))();
    }
  }
  return uVar1;
}

