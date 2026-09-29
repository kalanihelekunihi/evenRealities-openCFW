
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 aud_codec_audio_check_timer_stop(void)

{
  undefined4 unaff_r7;
  
  if (*_DAT_0053ce74 != 0) {
    osTimerStop(*_DAT_0053ce74);
  }
  return unaff_r7;
}

