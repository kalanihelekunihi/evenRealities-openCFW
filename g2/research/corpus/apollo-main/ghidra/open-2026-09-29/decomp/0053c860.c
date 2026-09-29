
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 AUD_CodecCtr(int param_1,undefined *param_2,uint param_3,undefined4 param_4)

{
  int iVar1;
  uint uVar2;
  
  uVar2 = *(uint *)(param_1 + 8);
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    param_3 = uVar2 & 0xff;
    param_1 = 0x17e;
    param_2 = PTR_s_codec_ctr___d_0053cef0;
    FUN_0043d574(3,DAT_0053cd90,DAT_0053cd8c,PTR_s_AUD_CodecCtr_0053cef4,0x17e,
                 PTR_s_codec_ctr___d_0053cef0,param_3,param_4);
  }
  iVar1 = FUN_0043d0ce();
  if (-1 < iVar1 << 0x1f) {
    iVar1 = FUN_0043d0ce();
    if (-1 < iVar1 << 0x1d) goto LAB_0053c8b2;
  }
  compress_log_output(0xc400000,PTR_s__thread_audio_codec_ctr___d_0053cef8,
                      PTR_s__thread_audio_codec_ctr___d_0053cef8,uVar2 & 0xff,param_1,param_2,
                      param_3);
LAB_0053c8b2:
  iVar1 = productModeGet();
  if (iVar1 == 1) {
    aud_codec_route_control(uVar2 & 0xff);
  }
  else {
    if ((uVar2 & 0xff) == 2) {
      DRV_Gx8002_Reboot(0);
    }
    if ((uVar2 & 0xff) == 0) {
      *_DAT_0053cefc = 0;
      *DAT_0053cedc = 0;
      aud_codec_audio_check_timer_stop();
      DRV_Gx8002_I2SDeinit();
      osDelay(0x32);
      SVC_I2SOutputCtrl(0);
    }
    else {
      *_DAT_0053cefc = 1;
      *DAT_0053cedc = 0;
      SVC_CodecDMICOpen();
      osDelay(0x32);
      SVC_I2SOutputCtrl(1);
      osDelay(0x32);
      DRV_Gx8002_I2SInit();
      AUD_CodecAudioCheckTimerStart();
    }
  }
  return CONCAT44(param_2,param_1);
}

