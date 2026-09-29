
undefined8 APP_MasterResetRetryConnectCnt(void)

{
  int iVar1;
  undefined4 unaff_r5;
  undefined4 unaff_r6;
  
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    unaff_r5 = 0x4d0;
    unaff_r6 = DAT_004a2c84;
    FUN_0043d574(3,DAT_004a28f0,DAT_004a28ec,DAT_004a2c88,0x4d0,DAT_004a2c84,*DAT_004a2fb4);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0xc400000,DAT_004a2c8c,DAT_004a2c8c,*DAT_004a2fb4);
  }
  *DAT_004a2fb4 = 0;
  return CONCAT44(unaff_r6,unaff_r5);
}

