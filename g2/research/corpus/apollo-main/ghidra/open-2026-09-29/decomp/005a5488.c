
undefined4 _atAudioCtrl(undefined4 param_1,undefined *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  
  uVar2 = param_1;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    uVar2 = 0xe;
    param_2 = PTR_s_set_audio__s_005a5508;
    param_3 = param_1;
    FUN_0043d574(3,PTR_s_at_codec_005a5514,PTR_s_D__01_workspace_s200_ap510b_iar__005a5510,
                 PTR_s__atAudioCtrl_005a550c,0xe,PTR_s_set_audio__s_005a5508,param_1,param_4);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0xc400000,PTR_s__at_codec_set_audio__s_005a5518,
                        PTR_s__at_codec_set_audio__s_005a5518,param_1,uVar2,param_2,param_3);
  }
  iVar1 = FUN_0044b610(param_1,0x5a5500,1);
  if (iVar1 == 0) {
    AUDM_appAcquire(7);
  }
  else {
    iVar1 = FUN_0044b610(param_1,0x5a5504,1);
    if (iVar1 == 0) {
      AUDM_appRelease(7);
    }
  }
  at_core_output(PTR_s_AUD_AUDIO_OK_005a551c);
  return 1;
}

