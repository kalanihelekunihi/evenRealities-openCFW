
undefined8 RING_ConnectPolicyResetRingConnectInfoThrottle(void)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 unaff_r5;
  undefined4 unaff_r6;
  
  iVar2 = FUN_0043d0ce();
  uVar1 = DAT_0049f81c;
  if (iVar2 << 0x1e < 0) {
    unaff_r5 = 0xff;
    FUN_0043d574(3,DAT_0049f754,DAT_0049f750,DAT_0049f820);
    unaff_r6 = uVar1;
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0xc000000,DAT_0049f824,DAT_0049f824);
  }
  *DAT_0049f7a8 = 0;
  return CONCAT44(unaff_r6,unaff_r5);
}

