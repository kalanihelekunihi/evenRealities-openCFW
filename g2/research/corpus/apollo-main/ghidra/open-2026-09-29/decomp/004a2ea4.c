
void APP_MasterCancelRingConnectRetry
               (char param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    uVar2 = _ringLinkStateName(*DAT_004a3120);
    FUN_0043d574(3,DAT_004a315c,DAT_004a3158,PTR_s_APP_MasterCancelRingConnectRetry_004a3520,0x5e7,
                 PTR_s_APP_MasterCancelRingConnectRetry_004a351c,param_1,*DAT_004a2fb4,
                 *(undefined1 *)(*DAT_004a3134 + 0x55),uVar2,param_4);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    uVar2 = _ringLinkStateName(*DAT_004a3120);
    compress_log_output(0xd000000,PTR_s__ble_master_APP_MasterCancelRing_004a3524,
                        PTR_s__ble_master_APP_MasterCancelRing_004a3524,param_1,*DAT_004a2fb4,
                        *(undefined1 *)(*DAT_004a3134 + 0x55),uVar2);
  }
  uVar2 = DAT_004a311c;
  fw_event_loop_remove_delayed(DAT_004a311c);
  fw_event_loop_remove_delayed(DAT_004a34c8);
  APP_MasterResetRetryConnectCnt();
  APP_MasterClearRingConnectFailureNotifyAfterRetry();
  APP_MasterResetSceneConnectPending();
  if (((param_1 != '\0') && (*DAT_004a3134 != 0)) && (*(char *)(*DAT_004a3134 + 0x55) != '\0')) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(3,DAT_004a315c,DAT_004a3158,PTR_s_APP_MasterCancelRingConnectRetry_004a3520,0x5ee
                   ,PTR_s_APP_MasterCancelRingConnectRetry_004a3528);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0xc000000,PTR_s__ble_master_APP_MasterCancelRing_004a352c);
    }
    auth_mode_set(0);
    fw_event_loop_push_delayed(uVar2,0x102,0);
  }
  return;
}

