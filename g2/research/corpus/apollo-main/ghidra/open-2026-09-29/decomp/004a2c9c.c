
void APP_MasterCleanupRingUnpair(int param_1)

{
  int *piVar1;
  char *pcVar2;
  int iVar3;
  undefined4 uVar4;
  undefined4 local_14;
  undefined4 uStack_10;
  
  local_14 = *DAT_004a34e8;
  uStack_10 = DAT_004a34e8[1];
  iVar3 = FUN_0043d0ce();
  if (iVar3 << 0x1e < 0) {
    uVar4 = _ringLinkStateName(*DAT_004a3120);
    FUN_0043d574(2,DAT_004a315c,DAT_004a3158,DAT_004a34f0,0x5b8,DAT_004a34ec,uVar4);
  }
  iVar3 = FUN_0043d0ce();
  if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
    uVar4 = _ringLinkStateName(*DAT_004a3120);
    compress_log_output(0x8400000,DAT_004a34f4,DAT_004a34f4,uVar4);
  }
  auth_mode_set(0);
  *DAT_004a2fcc = 0;
  *DAT_004a3144 = 0;
  *DAT_004a3124 = 0;
  fw_event_loop_remove_delayed(DAT_004a311c);
  fw_event_loop_remove_delayed(DAT_004a34c8);
  fw_event_loop_remove_delayed(DAT_004a34f8);
  fw_event_loop_remove_delayed(DAT_004a34fc);
  fw_event_loop_remove_delayed(DAT_004a3500);
  APP_MasterResetRetryConnectCnt();
  APP_MasterClearRingConnectFailureNotifyAfterRetry();
  RING_ConnectPolicyReset();
  APP_MasterSetTargetAddrName(&local_14,&DAT_004a2fb8,0);
  iVar3 = FUN_00466010();
  FUN_0043c0e4(iVar3 + 0xc,6,0xff);
  FUN_004661a6();
  FUN_00466016();
  iVar3 = FUN_0045a568();
  if (iVar3 == 1) {
    UX_SendBLEStatusReply(0);
  }
  if (param_1 != 0) {
    FUN_0047b59c(1,param_1);
  }
  AppMasterSecClearAddr();
  pcVar2 = DAT_004a34cc;
  piVar1 = DAT_004a3134;
  if ((*DAT_004a3120 == '\x01') && (*DAT_004a34cc != '\0')) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(3,DAT_004a315c,DAT_004a3158,DAT_004a34f0,0x5d3,DAT_004a3504,*pcVar2);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0xc400000,DAT_004a3508,DAT_004a3508,*pcVar2);
    }
    _masterConnectCancel(*pcVar2);
    return;
  }
  if ((*DAT_004a3134 == 0) || (*(char *)(*DAT_004a3134 + 0x55) == '\0')) {
    _SetRingLinkState(0,PTR_s_ring_unpair_cleanup_idle_004a3518);
  }
  else {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(3,DAT_004a315c,DAT_004a3158,DAT_004a34f0,0x5d9,DAT_004a350c,
                   *(undefined1 *)(*piVar1 + 0x55));
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0xc400000,DAT_004a3510,DAT_004a3510,*(undefined1 *)(*piVar1 + 0x55));
    }
    _SetRingLinkState(4,DAT_004a3514);
    FUN_004bb04a(*(undefined1 *)(*piVar1 + 0x55));
  }
  return;
}

