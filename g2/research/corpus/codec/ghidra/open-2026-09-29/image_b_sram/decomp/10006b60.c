
undefined4 FUN_10006b60(void)

{
  undefined4 uVar1;
  uint uVar2;
  
  if (*DAT_10006b8c == 0) {
    FUN_10009934(PTR_s__AOUT_ERROR___s__d_10006b94,PTR_s_gx_audio_out_push_frame_10006b90,0x131);
    return 0xffffffff;
  }
  uVar2 = *(uint *)(*DAT_10006b8c + 0x2c);
  if (uVar2 != 0) {
    uVar1 = (*(code *)(uVar2 & 0xfffffffe))();
    return uVar1;
  }
  return 0;
}

