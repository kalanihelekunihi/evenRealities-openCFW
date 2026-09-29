
undefined8 AUD_PeerSyncMsg(int param_1,undefined *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  uint uVar2;
  
  if (param_1 == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      param_1 = 0x21b;
      param_2 = PTR_s_invalid_peer_sync_msg_0053cf48;
      FUN_0043d574(1,DAT_0053cd90,DAT_0053cd8c,PTR_s_AUD_PeerSyncMsg_0053cf4c,0x21b,
                   PTR_s_invalid_peer_sync_msg_0053cf48,param_3,param_4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__thread_audio_invalid_peer_sync_m_0053cf50,
                          PTR_s__thread_audio_invalid_peer_sync_m_0053cf50);
    }
  }
  else {
    uVar2 = *(uint *)(param_1 + 8);
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      param_1 = 0x222;
      param_2 = PTR_s_processing_peer_sync_msg_in_audi_0053cf54;
      FUN_0043d574(4,DAT_0053cd90,DAT_0053cd8c,PTR_s_AUD_PeerSyncMsg_0053cf4c,0x222,
                   PTR_s_processing_peer_sync_msg_in_audi_0053cf54,uVar2 & 0xff);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10400000,PTR_s__thread_audio_processing_peer_sy_0053cf58,
                          PTR_s__thread_audio_processing_peer_sy_0053cf58,uVar2 & 0xff);
    }
    AUDM_HandlePeerSyncMsg(uVar2 & 0xff);
  }
  return CONCAT44(param_2,param_1);
}

