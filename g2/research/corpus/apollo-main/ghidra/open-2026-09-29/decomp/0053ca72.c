
void AUD_CodecIntNotify(void)

{
  int iVar1;
  int iVar2;
  undefined4 in_r3;
  char acStack_14 [4];
  char acStack_10 [2];
  short sStack_e;
  undefined4 uStack_c;
  
  uStack_c = in_r3;
  iVar1 = gx8002_power_state_get();
  if (iVar1 == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(2,DAT_0053cd90,DAT_0053cd8c,PTR_s_AUD_CodecIntNotify_0053cf18,0x1d6,
                   PTR_s_codec_is_not_power_on__no_need_t_0053cf14);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8000000,PTR_s__thread_audio_codec_is_not_power_0053cf1c,
                          PTR_s__thread_audio_codec_is_not_power_0053cf1c);
    }
  }
  else {
    FUN_0053a590(0x1d,acStack_14);
    if (acStack_14[0] == '\0') {
      gx8002_host_init();
      FUN_0043c0e4(acStack_10,4,0);
      iVar1 = GX8002_GetVoiceEvent(acStack_10);
      if (iVar1 == 0) {
        semantic_gx8002_uart_cleanup();
        iVar1 = SVC_Settings_InputEventCheck();
        if (iVar1 == 0) {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            FUN_0043d574(2,DAT_0053cd90,DAT_0053cd8c,PTR_s_AUD_CodecIntNotify_0053cf18,0x1ee,
                         PTR_s_input_event_check_failed__no_nee_0053cf30);
          }
          iVar1 = FUN_0043d0ce();
          if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
            compress_log_output(0x8000000,PTR_s__thread_audio_input_event_check_f_0053cf34,
                                PTR_s__thread_audio_input_event_check_f_0053cf34);
          }
        }
        else {
          iVar1 = settings_get_terminal_mode();
          if (iVar1 == 0) {
            if (acStack_10[0] == '\f') {
              service_even_ai_fn_0049832e(1,0);
            }
            else if (acStack_10[0] == '\r') {
              if (sStack_e == 1) {
                service_even_ai_fn_00498528(1);
              }
              else if (sStack_e == 0) {
                service_even_ai_fn_00498528(2);
              }
              iVar1 = FUN_0043d0ce();
              if (iVar1 << 0x1e < 0) {
                FUN_0043d574(2,DAT_0053cd90,DAT_0053cd8c,PTR_s_AUD_CodecIntNotify_0053cf18,0x204,
                             PTR_s_vad_report___d_0053cf40,sStack_e);
              }
              iVar1 = FUN_0043d0ce();
              if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
                compress_log_output(0x8400000,PTR_s__thread_audio_vad_report___d_0053cf44,
                                    PTR_s__thread_audio_vad_report___d_0053cf44,sStack_e);
              }
            }
          }
          else {
            iVar1 = FUN_0043d0ce();
            if (iVar1 << 0x1e < 0) {
              FUN_0043d574(3,DAT_0053cd90,DAT_0053cd8c,PTR_s_AUD_CodecIntNotify_0053cf18,499,
                           PTR_s_terminal_mode_is_enabled__no_nee_0053cf38);
            }
            iVar1 = FUN_0043d0ce();
            if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
              compress_log_output(0xc000000,PTR_s__thread_audio_terminal_mode_is_e_0053cf3c,
                                  PTR_s__thread_audio_terminal_mode_is_e_0053cf3c);
            }
          }
        }
      }
      else {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(1,DAT_0053cd90,DAT_0053cd8c,PTR_s_AUD_CodecIntNotify_0053cf18,0x1e7,
                       PTR_s_parse_voice_event_failed___d_0053cf28,iVar1);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0x4400000,PTR_s__thread_audio_parse_voice_event_f_0053cf2c,
                              PTR_s__thread_audio_parse_voice_event_f_0053cf2c,iVar1);
        }
      }
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(2,DAT_0053cd90,DAT_0053cd8c,PTR_s_AUD_CodecIntNotify_0053cf18,0x1dd,
                     PTR_s_codec_int_gpio_level_is_not_low__0053cf20);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x8000000,PTR_s__thread_audio_codec_int_gpio_lev_0053cf24);
      }
    }
  }
  return;
}

