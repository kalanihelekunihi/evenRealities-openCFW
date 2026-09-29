
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void AUD_CodecAudioCheck(void)

{
  int iVar1;
  undefined4 in_r3;
  uint uVar2;
  
  if (*_DAT_0053cefc != '\0') {
    uVar2 = *DAT_0053cedc;
    *DAT_0053cedc = 0;
    if (uVar2 < 0x14) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(2,DAT_0053cd90,DAT_0053cd8c,PTR_s_AUD_CodecAudioCheck_0053cf04,0x1ad,
                     PTR_s_codec_audio_check_fail__low_coun_0053cf00,uVar2,0x14,2000,in_r3);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x8c00000,PTR_s__thread_audio_codec_audio_check_f_0053cf08,
                            PTR_s__thread_audio_codec_audio_check_f_0053cf08,uVar2,0x14,2000);
      }
      aud_send_message_type0(2);
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(3,DAT_0053cd90,DAT_0053cd8c,PTR_s_AUD_CodecAudioCheck_0053cf04,0x1b0,
                     PTR_s_codec_audio_check_pass__cnt__u_0053cf0c,uVar2);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0xc400000,PTR_s__thread_audio_codec_audio_check_p_0053cf10,
                            PTR_s__thread_audio_codec_audio_check_p_0053cf10,uVar2);
      }
    }
  }
  return;
}

