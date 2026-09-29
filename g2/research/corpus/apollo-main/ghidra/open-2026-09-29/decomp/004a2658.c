
undefined8
APP_MasterResetSceneConnectPending
          (undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  char *pcVar1;
  int iVar2;
  undefined4 local_10;
  undefined4 local_c;
  
  pcVar1 = DAT_004a2fcc;
  local_10 = param_3;
  local_c = param_4;
  if (*DAT_004a2fcc == '\x01') {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      local_c = DAT_004a2fd0;
      local_10 = 0x503;
      FUN_0043d574(2,DAT_004a28f0,DAT_004a28ec,DAT_004a2fd4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_004a2fd8,DAT_004a2fd8);
    }
    *pcVar1 = '\0';
    fw_event_loop_remove_delayed(DAT_004a311c);
  }
  return CONCAT44(local_c,local_10);
}

