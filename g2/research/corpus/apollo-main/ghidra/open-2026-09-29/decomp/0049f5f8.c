
undefined8 RING_ConnectPolicyCancelConnectTimeout(void)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 unaff_r5;
  undefined4 unaff_r6;
  
  *DAT_0049f7d0 = 0;
  fw_event_loop_remove_delayed(DAT_0049f7ec);
  fw_event_loop_remove_delayed(DAT_0049f7c0);
  iVar2 = FUN_0043d0ce();
  uVar1 = DAT_0049f7f8;
  if (iVar2 << 0x1e < 0) {
    unaff_r5 = 0xe1;
    FUN_0043d574(3,DAT_0049f754,DAT_0049f750,DAT_0049f7fc);
    unaff_r6 = uVar1;
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0xc000000,DAT_0049f800,DAT_0049f800);
  }
  return CONCAT44(unaff_r6,unaff_r5);
}

