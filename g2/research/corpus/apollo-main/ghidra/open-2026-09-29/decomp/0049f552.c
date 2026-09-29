
undefined8
RING_ConnectPolicyScheduleReconnectTimeout
          (undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  
  if (*DAT_0049f7d0 == '\0') {
    *DAT_0049f7d0 = '\x01';
    uVar1 = DAT_0049f7ec;
    fw_event_loop_remove_delayed(DAT_0049f7ec);
    fw_event_loop_push_delayed(uVar1,0,20000);
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_2 = 0xd9;
      param_3 = DAT_0049f7f0;
      FUN_0043d574(3,DAT_0049f754,DAT_0049f750,DAT_0049f7e4,0xd9,DAT_0049f7f0,20000);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0xc400000,DAT_0049f7f4,DAT_0049f7f4,20000);
    }
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_4 = 20000;
      param_2 = 0xd3;
      param_3 = DAT_0049f7e0;
      FUN_0043d574(4,DAT_0049f754,DAT_0049f750,DAT_0049f7e4,0xd3,DAT_0049f7e0,20000);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_0049f7e8,DAT_0049f7e8,20000,param_2,param_3,param_4);
    }
  }
  return CONCAT44(param_3,param_2);
}

