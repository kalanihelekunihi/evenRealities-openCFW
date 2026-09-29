
undefined4 FUN_10006af0(void)

{
  undefined4 uVar1;
  uint uVar2;
  
  if (*DAT_10006b1c == 0) {
    FUN_10009934(PTR_s__AOUT_ERROR___s__d_10006b24,PTR_s_gx_audio_out_config_pcm_10006b20,0x109);
    return 0xffffffff;
  }
  uVar2 = *(uint *)(*DAT_10006b1c + 0x1c);
  if (uVar2 != 0) {
    uVar1 = (*(code *)(uVar2 & 0xfffffffe))();
    return uVar1;
  }
  return 0;
}

