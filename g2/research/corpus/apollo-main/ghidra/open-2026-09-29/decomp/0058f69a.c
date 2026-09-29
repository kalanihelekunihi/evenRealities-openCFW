
longlong production_codec_mic_func_init(char param_1)

{
  int iVar1;
  uint unaff_r5;
  
  *DAT_0058f890 = 0;
  if (param_1 == '\0') {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      unaff_r5 = 0x6d;
      FUN_0043d574(4,DAT_0058f874,DAT_0058f870,DAT_0058f898,0x6d,DAT_0058f894);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_0058f89c,DAT_0058f89c);
    }
    SVC_PcmAppRegister(0x10b,0,DAT_0058f8a0);
  }
  else if (param_1 == '\x01') {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      unaff_r5 = 0x72;
      FUN_0043d574(4,DAT_0058f874,DAT_0058f870,DAT_0058f898,0x72,DAT_0058f8a4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_0058f8a8,DAT_0058f8a8);
    }
    SVC_PcmAppRegister(0x10b,0,DAT_0058f8ac);
  }
  aud_send_message_type0(1);
  service_audio_recording_start(0);
  return (ulonglong)unaff_r5 << 0x20;
}

