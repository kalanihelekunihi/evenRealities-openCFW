
undefined4 PB_RxTimeSyncInfo(undefined4 param_1,undefined4 *param_2)

{
  undefined4 *puVar1;
  int iVar2;
  undefined4 uVar3;
  int local_20;
  undefined4 local_1c;
  undefined4 local_18;
  int local_14;
  
  fw_event_loop_remove_delayed(DAT_00543bc4);
  puVar1 = DAT_00543bd0;
  if (param_2 == (undefined4 *)0x0) {
    FUN_00439c04(&local_20,DAT_00543bc8,0x14);
    local_1c = CONCAT22(local_1c._2_2_,1);
    APP_errorFaultHandler(&local_20);
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      local_1c = DAT_005436d4;
      local_20 = 0x116;
      FUN_0043d574(1,DAT_005436e0,DAT_005436dc,DAT_00543bcc);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_005436e4);
    }
    uVar3 = 2;
  }
  else {
    *DAT_00543bd0 = *param_2;
    *(undefined1 *)(puVar1 + 1) = *(undefined1 *)(param_2 + 1);
    SVC_SystemTimeSync(*param_2,(int)*(char *)(param_2 + 1));
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      local_14 = (int)*(char *)(puVar1 + 1);
      local_18 = *puVar1;
      local_1c = DAT_00543bd4;
      local_20 = 0x11d;
      FUN_0043d574(4,DAT_005436e0,DAT_005436dc,DAT_00543bcc);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      local_20 = (int)*(char *)(puVar1 + 1);
      compress_log_output(0x10800000,DAT_00543bd8,DAT_00543bd8,*puVar1);
    }
    fw_event_loop_remove_delayed(DAT_00543bdc);
    RPC_SystemTimeSync(0);
    FUN_004b82e8(1);
    uVar3 = 0;
  }
  return uVar3;
}

