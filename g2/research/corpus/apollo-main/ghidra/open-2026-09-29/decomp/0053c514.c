
undefined4 aud_codec_mode_init(void)

{
  int iVar1;
  undefined4 unaff_r7;
  
  iVar1 = productModeGet();
  if (iVar1 == 1) {
    aud_codec_dfu_check();
  }
  else {
    AUDM_Init();
  }
  return unaff_r7;
}

