
undefined8 RING_ConnectPolicyNotifyConnectSuccessSoon(undefined4 param_1,undefined4 param_2)

{
  undefined4 uVar1;
  int iVar2;
  
  *DAT_0049f7d0 = 0;
  fw_event_loop_remove_delayed(DAT_0049f7ec);
  uVar1 = DAT_0049f7c0;
  fw_event_loop_remove_delayed(DAT_0049f7c0);
  iVar2 = central_is_ring_owner_side_004a2914();
  if (iVar2 != 0) {
    fw_event_loop_push_delayed(uVar1,0,200);
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_1 = 0xf1;
      param_2 = DAT_0049f804;
      FUN_0043d574(3,DAT_0049f754,DAT_0049f750,DAT_0049f808,0xf1,DAT_0049f804,200);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0xc400000,DAT_0049f80c,DAT_0049f80c,200);
    }
  }
  return CONCAT44(param_2,param_1);
}

