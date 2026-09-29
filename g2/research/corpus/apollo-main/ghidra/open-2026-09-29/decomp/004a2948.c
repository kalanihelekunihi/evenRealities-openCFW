
void APP_MasterOnDominantHandChangedEx
               (undefined1 param_1,undefined4 param_2,char param_3,undefined4 param_4)

{
  char *pcVar1;
  char cVar2;
  undefined1 uVar3;
  int iVar4;
  undefined4 uVar5;
  undefined *puVar6;
  undefined1 auStack_34 [8];
  undefined1 auStack_2c [14];
  undefined1 local_1e;
  undefined4 uStack_1c;
  
  uStack_1c = param_4;
  cVar2 = central_is_ring_owner_side_004a2914();
  iVar4 = FUN_0043d0ce();
  if (iVar4 << 0x1e < 0) {
    uVar3 = UX_GetPeerRingStatus();
    uVar5 = _ringLinkStateName(*DAT_004a3120);
    FUN_0043d574(3,DAT_004a315c,DAT_004a3158,DAT_004a3154,0x574,DAT_004a3150,param_1,cVar2,uVar5,
                 uVar3,param_2);
  }
  iVar4 = FUN_0043d0ce();
  if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
    uVar3 = UX_GetPeerRingStatus();
    uVar5 = _ringLinkStateName(*DAT_004a3120);
    compress_log_output(0xd400000,DAT_004a3160,DAT_004a3160,param_1,cVar2,uVar5,uVar3,param_2);
  }
  if (cVar2 == '\0') {
    auth_mode_set(0);
    uVar5 = DAT_004a311c;
    fw_event_loop_remove_delayed(DAT_004a311c);
    fw_event_loop_remove_delayed(DAT_004a34c8);
    APP_MasterResetRetryConnectCnt();
    APP_MasterClearRingConnectFailureNotifyAfterRetry();
    APP_MasterResetSceneConnectPending();
    RING_ConnectPolicyCancelConnectTimeout();
    pcVar1 = DAT_004a34cc;
    if ((*DAT_004a3120 == '\x01') && (*DAT_004a34cc != '\0')) {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        FUN_0043d574(3,DAT_004a315c,DAT_004a3158,DAT_004a3154,0x5a4,DAT_004a34d0,*pcVar1);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0xc400000,DAT_004a34d4,DAT_004a34d4,*pcVar1);
      }
      _masterConnectCancel(*pcVar1);
    }
    else if ((*DAT_004a3134 == 0) || (*(char *)(*DAT_004a3134 + 0x55) == '\0')) {
      _SetRingLinkState(0,DAT_004a34e4);
    }
    else {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        FUN_0043d574(3,DAT_004a315c,DAT_004a3158,DAT_004a3154,0x5a7,DAT_004a34d8);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0xc000000,DAT_004a34dc,DAT_004a34dc);
      }
      _SetRingLinkState(4,DAT_004a34e0);
      fw_event_loop_push_delayed(uVar5,0x102,0);
    }
  }
  else {
    iVar4 = FUN_00466010();
    FUN_00439be4(auStack_34,iVar4 + 0xc,6);
    iVar4 = ring_address_is_unset_004a26e8(auStack_34);
    if (iVar4 == 0) {
      iVar4 = central_master_link_matches_target_004a2864(auStack_34);
      if (iVar4 == 0) {
        FUN_00439be4(auStack_2c,DAT_004a34b8,0xe);
        local_1e = 0;
        APP_MasterSetTargetAddrName(auStack_34,auStack_2c,0xf);
        auth_mode_set(1);
        APP_MasterResetRetryConnectCnt();
        if (param_3 == '\0') {
          APP_MasterBeginRingConnectFailureNotifyAfterRetry();
          RING_ConnectPolicyScheduleConnectTimeout();
        }
        else {
          RING_ConnectPolicyScheduleReconnectTimeout();
        }
        central_schedule_master_connect_004a2618(param_2,param_3);
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          puVar6 = DAT_004a34bc;
          if (param_3 == '\0') {
            puVar6 = &DAT_004a2c70;
          }
          FUN_0043d574(3,DAT_004a315c,DAT_004a3158,DAT_004a3154,0x596,DAT_004a34c0,puVar6);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          puVar6 = DAT_004a34bc;
          if (param_3 == '\0') {
            puVar6 = &DAT_004a2c70;
          }
          compress_log_output(0xc400000,DAT_004a34c4,DAT_004a34c4,puVar6);
        }
      }
      else {
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          FUN_0043d574(3,DAT_004a315c,DAT_004a3158,DAT_004a3154,0x57e,DAT_004a34b0);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0xc000000,DAT_004a34b4,DAT_004a34b4);
        }
        APP_MasterClearRingConnectFailureNotifyAfterRetry();
        RING_ConnectPolicyNotifyConnectSuccessSoon();
      }
    }
    else {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        FUN_0043d574(2,DAT_004a315c,DAT_004a3158,DAT_004a3154,0x579,DAT_004a3164);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x8000000,DAT_004a3168,DAT_004a3168);
      }
    }
  }
  return;
}

