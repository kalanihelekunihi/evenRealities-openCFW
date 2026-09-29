
undefined4 gx8002_audio_out_exit(void)

{
  undefined4 uVar1;
  uint uVar2;
  
  if (*piRam1020559c == 0) {
    gx8002_printf(PTR_s__AOUT_ERROR___s__d_102055a4,PTR_s_gx_audio_out_exit_102055a0,0x183);
    uVar1 = 0xffffffff;
  }
  else {
    uVar2 = *(uint *)(*piRam1020559c + 8);
    uVar1 = 0;
    if (uVar2 != 0) {
      uVar1 = (*(code *)(uVar2 & 0xfffffffe))();
    }
  }
  return uVar1;
}

