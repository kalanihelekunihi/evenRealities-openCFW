
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 AUD_CodecAudioCheckTimerStart(void)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 unaff_r5;
  undefined4 unaff_r6;
  
  if ((*_DAT_0053ce74 != 0) && (iVar2 = osTimerStart(*_DAT_0053ce74,2000), iVar2 != 0)) {
    iVar2 = FUN_0043d0ce();
    uVar1 = _DAT_0053cd38;
    if (iVar2 << 0x1e < 0) {
      unaff_r5 = 0x92;
      FUN_0043d574(1,DAT_0053cd90,DAT_0053cd8c,_DAT_0053cd3c);
      unaff_r6 = uVar1;
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__thread_audio_codec_audio_check_t_0053ce78,
                          PTR_s__thread_audio_codec_audio_check_t_0053ce78);
    }
  }
  return CONCAT44(unaff_r6,unaff_r5);
}

