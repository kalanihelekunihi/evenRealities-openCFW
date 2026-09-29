
undefined4
PB_RxDisconnectInfo(undefined4 param_1,byte *param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 local_20;
  undefined4 local_1c;
  uint local_18;
  undefined4 uStack_c;
  
  uStack_c = param_4;
  if (param_2 == (byte *)0x0) {
    FUN_00439c04(&local_20,DAT_004bcfa8,0x14);
    local_1c = CONCAT22(local_1c._2_2_,1);
    APP_errorFaultHandler(&local_20);
  }
  RING_ConnectPolicyResetRingConnectInfoThrottle();
  if (param_2 != (byte *)0x0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      local_18 = (uint)*param_2;
      local_1c = DAT_004bcfb0;
      local_20 = 0x256;
      FUN_0043d574(4,DAT_004bcfa4,DAT_004bcfa0,DAT_004bcfac);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_004bcfb4,DAT_004bcfb4,*param_2);
    }
    if (*param_2 == 2) {
      FUN_0043dacc(DAT_004bcfb8,0x10,param_2 + 4,*(undefined2 *)(param_2 + 2));
    }
    else if (*param_2 == 1) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        local_1c = DAT_004bcfbc;
        local_20 = 0x25a;
        FUN_0043d574(4,DAT_004bcfa4,DAT_004bcfa0,DAT_004bcfac);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_004bcfc0,DAT_004bcfc0);
      }
    }
    APP_MasterResetRetryConnectCnt();
    uVar1 = DAT_004bcfc4;
    fw_event_loop_remove_delayed(DAT_004bcfc4);
    fw_event_loop_push_delayed(uVar1,0x102,0);
    return 0;
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    local_1c = DAT_004bc914;
    local_20 = 0x253;
    FUN_0043d574(1,DAT_004bcfa4,DAT_004bcfa0,DAT_004bcfac);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x4000000,DAT_004bc91c);
  }
  return 2;
}

