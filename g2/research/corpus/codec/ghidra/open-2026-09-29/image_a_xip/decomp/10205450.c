
undefined4 gx8002_audio_out_config_cb(void)

{
  undefined4 uVar1;
  uint uVar2;
  
  if (*piRam1020547c == 0) {
    gx8002_printf(PTR_s__AOUT_ERROR___s__d_10205484,PTR_s_gx_audio_out_config_cb_10205480,0x127);
    uVar1 = 0xffffffff;
  }
  else {
    uVar2 = *(uint *)(*piRam1020547c + 0x28);
    if (uVar2 == 0) {
      uVar1 = 0;
    }
    else {
      uVar1 = (*(code *)(uVar2 & 0xfffffffe))();
    }
  }
  return uVar1;
}

