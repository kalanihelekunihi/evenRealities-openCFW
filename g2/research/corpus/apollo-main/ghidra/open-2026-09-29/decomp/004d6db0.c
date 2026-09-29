
undefined4 PB_RxNotifCtrl(undefined4 param_1,byte *param_2)

{
  int iVar1;
  undefined4 uVar2;
  byte *pbVar3;
  uint local_20;
  uint local_1c;
  uint local_18;
  uint local_14;
  uint local_10;
  uint local_c;
  
  if (param_2 == (byte *)0x0) {
    FUN_00439c04(&local_20,DAT_004d76b8,0x14);
    local_1c = CONCAT22(local_1c._2_2_,1);
    APP_errorFaultHandler(&local_20);
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      local_1c = DAT_004d76bc;
      local_20 = 0x69;
      FUN_0043d574(1,DAT_004d7694,DAT_004d7690,DAT_004d76c0);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_004d76c4);
    }
    uVar2 = 2;
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      local_c = (uint)param_2[4];
      local_10 = (uint)param_2[2];
      local_14 = (uint)param_2[1];
      local_18 = (uint)*param_2;
      local_1c = DAT_004d76c8;
      local_20 = 0x6e;
      FUN_0043d574(3,DAT_004d7694,DAT_004d7690,DAT_004d76c0);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      local_18 = (uint)param_2[4];
      local_1c = (uint)param_2[2];
      local_20 = (uint)param_2[1];
      compress_log_output(0xd000000,DAT_004d78ec,DAT_004d78ec,*param_2);
    }
    pbVar3 = (byte *)service_ancc_state_get();
    *pbVar3 = *param_2;
    iVar1 = service_ancc_state_get();
    *(byte *)(iVar1 + 1) = param_2[1];
    iVar1 = service_ancc_state_get();
    *(byte *)(iVar1 + 2) = param_2[2];
    iVar1 = service_ancc_state_get();
    *(byte *)(iVar1 + 3) = param_2[4];
    uVar2 = 0;
  }
  return uVar2;
}

