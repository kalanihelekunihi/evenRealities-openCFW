
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 AUDM_HandlePeerSyncMsg(uint param_1,undefined *param_2,uint param_3,undefined4 param_4)

{
  uint uVar1;
  int iVar2;
  
  uVar1 = param_1 & 0xff;
  if (uVar1 == 1) {
    iVar2 = FUN_0045a568();
    uVar1 = param_1;
    if (iVar2 == 2) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        param_1 = 0x80;
        param_2 = PTR_s_slave__received_request_from_mas_0054f9dc;
        FUN_0043d574(3,DAT_0054f988,DAT_0054f984,PTR_s_AUDM_HandlePeerSyncMsg_0054f9e0);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0xc000000,PTR_s__service_audio_manager_slave__re_0054f9e4,
                            PTR_s__service_audio_manager_slave__re_0054f9e4);
      }
      SVC_CodecDMICClose();
      AUDM_SendSyncMsgToPeer(2);
      uVar1 = param_1;
    }
    goto LAB_0054f88c;
  }
  if (uVar1 != 0) {
    if (uVar1 == 3) {
      iVar2 = FUN_0045a568();
      uVar1 = param_1;
      if (iVar2 == 2) {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          param_1 = 0x91;
          param_2 = PTR_s_slave__received_low_power_respon_0054f9f4;
          FUN_0043d574(3,DAT_0054f988,DAT_0054f984,PTR_s_AUDM_HandlePeerSyncMsg_0054f9e0);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0xc000000,PTR_s__service_audio_manager_slave__re_0054f9f8,
                              PTR_s__service_audio_manager_slave__re_0054f9f8);
        }
        SVC_CodecDMICOpen();
        uVar1 = param_1;
      }
      goto LAB_0054f88c;
    }
    if (uVar1 < 3) {
      iVar2 = FUN_0045a568();
      uVar1 = param_1;
      if (iVar2 == 1) {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          param_1 = 0x88;
          param_2 = PTR_s_master__received_DMIC_closed_res_0054f9e8;
          FUN_0043d574(3,DAT_0054f988,DAT_0054f984,PTR_s_AUDM_HandlePeerSyncMsg_0054f9e0);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0xc000000,PTR_s__service_audio_manager_master__r_0054f9ec);
        }
        SVC_CodecCheckAndUpgrade(0);
        AUDM_SendSyncMsgToPeer(3);
        *_DAT_0054f9f0 = '\x01';
        uVar1 = param_1;
      }
      goto LAB_0054f88c;
    }
    if (uVar1 == 4) {
      iVar2 = FUN_0045a568();
      uVar1 = param_1;
      if ((iVar2 == 1) && (*_DAT_0054f9f0 == '\0')) {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          param_1 = 0x9c;
          param_2 = PTR_s_master__not_initialized__sending_0054f9fc;
          FUN_0043d574(3,DAT_0054f988,DAT_0054f984,PTR_s_AUDM_HandlePeerSyncMsg_0054f9e0);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0xc000000,PTR_s__service_audio_manager_master__n_0054fa00,
                              PTR_s__service_audio_manager_master__n_0054fa00);
        }
        AUDM_SendSyncMsgToPeer(1);
        uVar1 = param_1;
      }
      goto LAB_0054f88c;
    }
  }
  uVar1 = param_1;
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    param_3 = param_1 & 0xff;
    uVar1 = 0xa2;
    param_2 = PTR_s_unknown_audio_sync_msg_id___d_0054fa04;
    FUN_0043d574(2,DAT_0054f988,DAT_0054f984,PTR_s_AUDM_HandlePeerSyncMsg_0054f9e0,0xa2,
                 PTR_s_unknown_audio_sync_msg_id___d_0054fa04,param_3,param_4);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x8400000,PTR_s__service_audio_manager_unknown_a_0054fa08,
                        PTR_s__service_audio_manager_unknown_a_0054fa08,param_1 & 0xff,uVar1,param_2
                        ,param_3);
  }
LAB_0054f88c:
  return CONCAT44(param_2,uVar1);
}

