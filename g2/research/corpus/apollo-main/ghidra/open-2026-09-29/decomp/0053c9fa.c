
undefined4 aud_codec_check_trigger(int param_1)

{
  undefined4 unaff_r7;
  
  SVC_CodecCheckAndUpgrade(*(int *)(param_1 + 8) != 0);
  return unaff_r7;
}

