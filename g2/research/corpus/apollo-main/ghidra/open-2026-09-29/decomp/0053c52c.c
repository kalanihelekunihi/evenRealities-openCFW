
void AUD_ThreadHandler(void)

{
  uint uVar1;
  int iVar2;
  
  aud_pdm_counter_reset_callback();
  aud_codec_mode_init();
  AUD_ResourceInit();
  aud_codec_counter_reset_callback();
  do {
    do {
      while ((uVar1 = osThreadFlagsWait(0xffffff,0,0xffffffff), uVar1 != 0 && (uVar1 < 0x80000000)))
      {
        aud_thread_flag_dispatch();
      }
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(1,DAT_0053cd90,DAT_0053cd8c,PTR_s_AUD_ThreadHandler_0053ceac);
      }
      iVar2 = FUN_0043d0ce();
    } while ((-1 < iVar2 << 0x1f) && (iVar2 = FUN_0043d0ce(), -1 < iVar2 << 0x1d));
    compress_log_output(0x4000000,PTR_s__thread_audio_Notify_error__0053ceb0,
                        PTR_s__thread_audio_Notify_error__0053ceb0);
  } while( true );
}

