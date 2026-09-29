
undefined4 aud_codec_dfu_check(void)

{
  undefined4 unaff_r7;
  
  SVC_CodecCheckAndUpgrade(0);
  return unaff_r7;
}

