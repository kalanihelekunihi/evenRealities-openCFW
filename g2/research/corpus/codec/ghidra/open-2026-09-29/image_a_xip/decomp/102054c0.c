
undefined4 gx8002_audio_out_set_db(void)

{
  undefined4 uVar1;
  uint uVar2;
  
  if (*piRam102054ec == 0) {
    gx8002_printf(PTR_s__AOUT_ERROR___s__d_102054f4,PTR_s_gx_audio_out_set_db_102054f0,0x145);
    uVar1 = 0xffffffff;
  }
  else {
    uVar2 = *(uint *)(*piRam102054ec + 0x38);
    if (uVar2 == 0) {
      uVar1 = 0;
    }
    else {
      uVar1 = (*(code *)(uVar2 & 0xfffffffe))();
    }
  }
  return uVar1;
}

