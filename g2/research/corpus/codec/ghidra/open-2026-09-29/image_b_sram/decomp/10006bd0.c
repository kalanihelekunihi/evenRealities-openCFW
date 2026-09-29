
undefined4 FUN_10006bd0(void)

{
  undefined4 uVar1;
  uint uVar2;
  
  if (*DAT_10006bfc == 0) {
    FUN_10009934(PTR_s__AOUT_ERROR___s__d_10006c04,PTR_s_gx_audio_out_set_channel_10006c00,0x16d);
    return 0xffffffff;
  }
  uVar2 = *(uint *)(*DAT_10006bfc + 0x48);
  if (uVar2 != 0) {
    uVar1 = (*(code *)(uVar2 & 0xfffffffe))();
    return uVar1;
  }
  return 0;
}

