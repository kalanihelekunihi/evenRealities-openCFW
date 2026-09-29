
undefined4 gx8002_audio_out_config_pcm(void)

{
  undefined4 uVar1;
  uint uVar2;
  
  if (*piRam10205444 == 0) {
    gx8002_printf(PTR_s__AOUT_ERROR___s__d_1020544c,PTR_s_gx_audio_out_config_pcm_10205448,0x109);
    uVar1 = 0xffffffff;
  }
  else {
    uVar2 = *(uint *)(*piRam10205444 + 0x1c);
    if (uVar2 == 0) {
      uVar1 = 0;
    }
    else {
      uVar1 = (*(code *)(uVar2 & 0xfffffffe))();
    }
  }
  return uVar1;
}

