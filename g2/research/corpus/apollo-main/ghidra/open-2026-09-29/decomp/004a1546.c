
undefined8 APP_MasterBeginRingConnectFailureNotifyAfterRetry(void)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 unaff_r5;
  undefined4 unaff_r6;
  
  *DAT_004a1fac = 1;
  *DAT_004a1fb0 = 0;
  iVar2 = FUN_0043d0ce();
  uVar1 = DAT_004a1fb4;
  if (iVar2 << 0x1e < 0) {
    unaff_r5 = 0x374;
    FUN_0043d574(3,DAT_004a1af4,DAT_004a1af0,DAT_004a1fb8);
    unaff_r6 = uVar1;
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0xc000000,DAT_004a224c,DAT_004a224c);
  }
  return CONCAT44(unaff_r6,unaff_r5);
}

