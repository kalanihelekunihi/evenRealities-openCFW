
undefined4 gx8002_audio_out_alloc_playback(void)

{
  undefined4 uVar1;
  uint uVar2;
  
  if ((uint *)*piRam102053a4 == (uint *)0x0) {
    gx8002_printf(PTR_s__AOUT_ERROR___s__d_102053ac,PTR_s_gx_audio_out_alloc_playback_102053a8,0xea)
    ;
    uVar1 = 0xffffffff;
  }
  else {
    uVar2 = *(uint *)*piRam102053a4;
    if (uVar2 == 0) {
      uVar1 = 0;
    }
    else {
      uVar1 = (*(code *)(uVar2 & 0xfffffffe))();
    }
  }
  return uVar1;
}

