
undefined4
PB_RxBleConnectParams(undefined4 param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 local_20;
  undefined4 local_1c;
  undefined4 local_18;
  undefined4 uStack_c;
  
  uStack_c = param_4;
  if (param_2 == 0) {
    FUN_00439c04(&local_20,DAT_004bcb20,0x14);
    local_1c = CONCAT22(local_1c._2_2_,1);
    APP_errorFaultHandler(&local_20);
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      local_1c = DAT_004bc914;
      local_20 = 0x1e7;
      FUN_0043d574(1,DAT_004bc7a4,DAT_004bc7a0,DAT_004bcb24);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_004bc91c);
    }
    uVar2 = 2;
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      local_18 = DAT_004bcde4;
      if (*(char *)(param_2 + 4) != '\0') {
        local_18 = DAT_004bcde0;
      }
      local_1c = DAT_004bcde8;
      local_20 = 0x1eb;
      FUN_0043d574(4,DAT_004bc7a4,DAT_004bc7a0,DAT_004bcb24);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      uVar2 = DAT_004bcde4;
      if (*(char *)(param_2 + 4) != '\0') {
        uVar2 = DAT_004bcde0;
      }
      compress_log_output(0x10400000,DAT_004bcf9c,DAT_004bcf9c,uVar2);
    }
    if (*(char *)(param_2 + 4) == '\0') {
      ble_param_reset_delayed_event(0);
    }
    else {
      ble_state_skip_manual_start(0);
    }
    uVar2 = 0;
  }
  return uVar2;
}

