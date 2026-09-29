
undefined4 AUDM_Init(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  char cVar1;
  int iVar2;
  
  FUN_0043c0e4(DAT_0054f978,8,0,param_4,param_1,param_2,param_3,param_4);
  cVar1 = FUN_0045a568();
  if (cVar1 == '\x02') {
    SVC_CodecCheckAndUpgrade(0);
    SVC_CodecDMICOpen();
    AUDM_SendSyncMsgToPeer(4);
  }
  else {
    FUN_00509024(6,1);
    AUDM_SendSyncMsgToPeer(1);
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    FUN_0043d574(3,DAT_0054f988,DAT_0054f984,PTR_s_AUDM_Init_0054fa10,0xbd,
                 PTR_s_audio_manager_initialized__role__0054fa0c,cVar1);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0xc400000,PTR_s__service_audio_manager_audio_man_0054fa14,
                        PTR_s__service_audio_manager_audio_man_0054fa14,cVar1);
  }
  return 0;
}

