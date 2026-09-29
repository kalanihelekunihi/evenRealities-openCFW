
undefined4 FUN_10006a88(void)

{
  undefined4 uVar1;
  uint uVar2;
  
  if ((uint *)*DAT_10006ab0 == (uint *)0x0) {
    FUN_10009934(PTR_s__AOUT_ERROR___s__d_10006ab8,PTR_s_gx_audio_out_alloc_playback_10006ab4,0xea);
    return 0xffffffff;
  }
  uVar2 = *(uint *)*DAT_10006ab0;
  if (uVar2 != 0) {
    uVar1 = (*(code *)(uVar2 & 0xfffffffe))();
    return uVar1;
  }
  return 0;
}

