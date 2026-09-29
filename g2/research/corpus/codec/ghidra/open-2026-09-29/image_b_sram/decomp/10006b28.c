
undefined4 FUN_10006b28(void)

{
  undefined4 uVar1;
  uint uVar2;
  
  if (*DAT_10006b54 == 0) {
    FUN_10009934(PTR_s__AOUT_ERROR___s__d_10006b5c,PTR_s_gx_audio_out_config_cb_10006b58,0x127);
    return 0xffffffff;
  }
  uVar2 = *(uint *)(*DAT_10006b54 + 0x28);
  if (uVar2 != 0) {
    uVar1 = (*(code *)(uVar2 & 0xfffffffe))();
    return uVar1;
  }
  return 0;
}

