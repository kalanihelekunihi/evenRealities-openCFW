
undefined4 gx8002_audio_out_push_frame(void)

{
  undefined4 uVar1;
  uint uVar2;
  
  if (*DAT_102054b4 == 0) {
    gx8002_printf(PTR_s__AOUT_ERROR___s__d_102054bc,PTR_s_gx_audio_out_push_frame_102054b8,0x131);
    uVar1 = 0xffffffff;
  }
  else {
    uVar2 = *(uint *)(*DAT_102054b4 + 0x2c);
    if (uVar2 == 0) {
      uVar1 = 0;
    }
    else {
      uVar1 = (*(code *)(uVar2 & 0xfffffffe))();
    }
  }
  return uVar1;
}

