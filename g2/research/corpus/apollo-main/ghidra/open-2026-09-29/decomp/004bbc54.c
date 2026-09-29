
longlong _PB_RxRingConnectInfoOwnerExecute
                   (undefined4 param_1,char *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  char *pcVar4;
  
  pcVar4 = param_2;
  APP_MasterSetTargetAddrName
            (param_2 + 4,param_2 + 0xc,(char)*(undefined2 *)(param_2 + 10),param_4,param_2,param_3,
             param_4);
  auth_mode_set(*param_2);
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    uVar2 = DAT_004bc5bc;
    if (*param_2 != '\0') {
      uVar2 = DAT_004bc5b8;
    }
    pcVar4 = (char *)0x10f;
    FUN_0043d574(4,DAT_004bbda8,DAT_004bbda4,DAT_004bc5c4,0x10f,DAT_004bc5c0,uVar2);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    uVar2 = DAT_004bc5bc;
    if (*param_2 != '\0') {
      uVar2 = DAT_004bc5b8;
    }
    compress_log_output(0x10400000,DAT_004bc788,DAT_004bc788,uVar2);
  }
  if ((*param_2 == '\0') ||
     (iVar1 = central_master_link_matches_target_004a2864(param_2 + 4), iVar1 == 0)) {
    uVar2 = DAT_004bc794;
    fw_event_loop_remove_delayed(DAT_004bc794);
    fw_event_loop_remove_delayed(DAT_004bc7b8);
    APP_MasterResetRetryConnectCnt();
    if (*param_2 == '\0') {
      APP_MasterClearRingConnectFailureNotifyAfterRetry();
    }
    else {
      APP_MasterBeginRingConnectFailureNotifyAfterRetry();
    }
    if (*param_2 == '\0') {
      uVar3 = 0x102;
    }
    else {
      uVar3 = 1;
    }
    fw_event_loop_push_delayed(uVar2,uVar3,0);
    RING_ConnectPolicyMarkRingConnectInfoProcessed(*param_2);
    if (*param_2 == '\0') {
      RING_ConnectPolicyCancelConnectTimeout();
    }
    else {
      RING_ConnectPolicyScheduleConnectTimeout();
    }
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      pcVar4 = (char *)0x115;
      FUN_0043d574(3,DAT_004bbda8,DAT_004bbda4,DAT_004bc5c4,0x115,DAT_004bc78c);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0xc000000,DAT_004bc790,DAT_004bc790);
    }
    RING_ConnectPolicyMarkRingConnectInfoProcessed(*param_2);
    APP_MasterClearRingConnectFailureNotifyAfterRetry();
    RING_ConnectPolicyNotifyConnectSuccessSoon();
    fw_event_loop_remove_delayed(DAT_004bc794);
    fw_event_loop_remove_delayed(DAT_004bc7b8);
  }
  return ZEXT48(pcVar4) << 0x20;
}

