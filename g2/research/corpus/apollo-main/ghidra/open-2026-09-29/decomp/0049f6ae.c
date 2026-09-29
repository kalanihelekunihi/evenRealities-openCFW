
undefined8 RING_ConnectPolicyReset(void)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 unaff_r5;
  undefined4 unaff_r6;
  
  iVar2 = FUN_0043d0ce();
  uVar1 = DAT_0049f810;
  if (iVar2 << 0x1e < 0) {
    unaff_r5 = 0xf6;
    FUN_0043d574(2,DAT_0049f754,DAT_0049f750,DAT_0049f814);
    unaff_r6 = uVar1;
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x8000000,DAT_0049f818,DAT_0049f818);
  }
  _EnterState(0);
  *DAT_0049f7a8 = 0;
  *DAT_0049f7d0 = 0;
  fw_event_loop_remove_delayed(DAT_0049f7ec);
  return CONCAT44(unaff_r6,unaff_r5);
}

