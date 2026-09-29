
undefined8 _ringReconnectTimeoutFire(void)

{
  int iVar1;
  undefined4 unaff_r5;
  undefined4 unaff_r6;
  
  *DAT_0049f7d0 = 0;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    unaff_r5 = 0xcb;
    unaff_r6 = DAT_0049f7d4;
    FUN_0043d574(2,DAT_0049f754,DAT_0049f750,DAT_0049f7d8,0xcb,DAT_0049f7d4,20000);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x8400000,DAT_0049f7dc,DAT_0049f7dc,20000);
  }
  PB_TxEncodeNotifyRingConnectInfo(0x5a);
  return CONCAT44(unaff_r6,unaff_r5);
}

