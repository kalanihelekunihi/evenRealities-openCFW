
undefined8
RING_ConnectPolicyScheduleConnectTimeout(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  undefined4 uVar1;
  int iVar2;
  
  uVar1 = DAT_0049f7c0;
  fw_event_loop_remove_delayed(DAT_0049f7c0);
  fw_event_loop_push_delayed(uVar1,0x5a,20000);
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    param_2 = 0xbc;
    param_3 = DAT_0049f7c4;
    FUN_0043d574(3,DAT_0049f754,DAT_0049f750,DAT_0049f7c8,0xbc,DAT_0049f7c4,20000);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0xc400000,DAT_0049f7cc,DAT_0049f7cc,20000);
  }
  return CONCAT44(param_3,param_2);
}

