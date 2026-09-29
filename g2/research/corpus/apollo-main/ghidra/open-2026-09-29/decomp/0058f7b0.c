
longlong production_pdm_mic_func_init(void)

{
  int iVar1;
  uint unaff_r5;
  
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    unaff_r5 = 0x92;
    FUN_0043d574(4,DAT_0058f874,DAT_0058f870,DAT_0058f8c0,0x92,DAT_0058f8bc);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10000000,DAT_0058f8c4,DAT_0058f8c4);
  }
  SVC_PcmAppRegister(0x10b,1,DAT_0058f8a0);
  aud_send_message_type1(1);
  service_audio_recording_start(1);
  return (ulonglong)unaff_r5 << 0x20;
}

