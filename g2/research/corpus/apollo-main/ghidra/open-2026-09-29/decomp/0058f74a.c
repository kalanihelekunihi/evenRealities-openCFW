
undefined8
production_codec_mic_func_deinit(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  int iVar1;
  int iVar2;
  
  aud_send_message_type0(0);
  iVar1 = SVC_PcmAppUnregister(0x10b,0);
  if (iVar1 == 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_3 = 0x82;
      FUN_0043d574(3,DAT_0058f874,DAT_0058f870,DAT_0058f8b4,0x82,DAT_0058f8b0);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0xc000000,DAT_0058f8b8,DAT_0058f8b8);
    }
    service_audio_recording_stop(0);
    service_audio_lc3_encoder_setup(DAT_0058f880);
    service_audio_lc3_encoder_setup(DAT_0058f884);
  }
  return CONCAT44(param_3,iVar1);
}

