
undefined4 gx8002_audio_out_init(void)

{
  int *piVar1;
  undefined4 uVar2;
  uint uVar3;
  
  piVar1 = piRam10205564;
  if (*piRam10205564 == 0) {
    *piRam10205564 = iRam10205568;
  }
  if (*piVar1 == 0) {
    gx8002_printf(PTR_s__AOUT_ERROR___s__d_10205570,PTR_s_gx_audio_out_init_1020556c,0x179);
    uVar2 = 0xffffffff;
  }
  else {
    uVar3 = *(uint *)(*piVar1 + 4);
    if (uVar3 == 0) {
      uVar2 = 0;
    }
    else {
      uVar2 = (*(code *)(uVar3 & 0xfffffffe))();
    }
  }
  return uVar2;
}

