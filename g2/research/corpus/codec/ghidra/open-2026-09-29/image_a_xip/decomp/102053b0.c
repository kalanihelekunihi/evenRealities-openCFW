
undefined4 gx8002_audio_out_free(void)

{
  undefined4 uVar1;
  uint uVar2;
  
  if (*piRam102053d8 == 0) {
    gx8002_printf(PTR_s__AOUT_ERROR___s__d_102053e0,PTR_s_gx_audio_out_free_102053dc,0xf5);
    uVar1 = 0xffffffff;
  }
  else {
    uVar2 = *(uint *)(*piRam102053d8 + 0x14);
    if (uVar2 == 0) {
      uVar1 = 0;
    }
    else {
      uVar1 = (*(code *)(uVar2 & 0xfffffffe))();
    }
  }
  return uVar1;
}

