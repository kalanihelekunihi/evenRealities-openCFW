
undefined8 AppBleMasterPeerMgrUnpairDev(undefined1 param_1,int param_2,int param_3,uint param_4)

{
  byte bVar1;
  int iVar2;
  int iVar3;
  int local_20;
  int local_1c;
  uint local_18;
  
  iVar2 = DAT_004d9128;
  local_20 = param_2;
  local_1c = param_3;
  if (param_2 == 0) goto LAB_004d9108;
  local_18 = param_4;
  FUN_00439be4(DAT_004d9128,param_2,6);
  *(undefined1 *)(iVar2 + 6) = param_1;
  bVar1 = auth_state_clear_wrapper();
  if (bVar1 == 0) {
    bVar1 = findConnIdByAddr(param_2);
  }
  if (bVar1 == 0) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      local_1c = DAT_004d913c;
      local_20 = 0x4b;
      FUN_0043d574(3,DAT_004d9120,DAT_004d911c,DAT_004d9130);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0xc000000,DAT_004d9140,DAT_004d9140);
    }
    auth_mode_set(0);
    APP_MasterResetRetryConnectCnt();
    fw_event_loop_remove_delayed(DAT_004d9138);
    fw_event_loop_remove_delayed(DAT_004d9144);
    local_20 = *DAT_004d9148;
    local_1c = DAT_004d9148[1];
    APP_MasterSetTargetAddrName(&local_20,&DAT_004d910c,0);
    APP_MasterUnpairDevEvent(iVar2);
    goto LAB_004d9108;
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    local_18 = (uint)bVar1;
    local_1c = DAT_004d912c;
    local_20 = 0x44;
    FUN_0043d574(3,DAT_004d9120,DAT_004d911c,DAT_004d9130);
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1f < 0) {
LAB_004d907a:
    compress_log_output(0xc400000,DAT_004d9134,DAT_004d9134,bVar1);
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1d < 0) goto LAB_004d907a;
  }
  APP_MasterResetRetryConnectCnt();
  fw_event_loop_remove_delayed(DAT_004d9138);
  APP_MasterUnpairConnIdEvent(bVar1);
LAB_004d9108:
  return CONCAT44(local_1c,local_20);
}

