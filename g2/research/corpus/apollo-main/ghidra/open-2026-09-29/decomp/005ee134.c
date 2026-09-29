
void tracepoint_reply_result(undefined1 *param_1)

{
  int iVar1;
  
  iVar1 = FUN_0045a568();
  if (iVar1 == 2) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,DAT_005ee79c,DAT_005ee798,DAT_005eeb68,0x11a,DAT_005eeb64,*param_1,param_1[4]);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10800000,DAT_005eeb6c,DAT_005eeb6c,*param_1,param_1[4]);
    }
    tracepoint_send_to_master(0xc,param_1);
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,DAT_005ee79c,DAT_005ee798,DAT_005eeb68,0x11f,DAT_005eeb70,*param_1,param_1[4]);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10800000,DAT_005eeb74,DAT_005eeb74,*param_1,param_1[4]);
    }
    tracepoint_send_to_phone(param_1);
  }
  return;
}

