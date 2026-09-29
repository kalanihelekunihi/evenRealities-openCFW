
undefined4 FUN_10006abc(void)

{
  undefined4 uVar1;
  uint uVar2;
  
  if (*DAT_10006ae4 == 0) {
    FUN_10009934(PTR_s__AOUT_ERROR___s__d_10006aec,PTR_s_gx_audio_out_config_buffer_10006ae8,0xff);
    return 0xffffffff;
  }
  uVar2 = *(uint *)(*DAT_10006ae4 + 0x18);
  if (uVar2 != 0) {
    uVar1 = (*(code *)(uVar2 & 0xfffffffe))();
    return uVar1;
  }
  return 0;
}

