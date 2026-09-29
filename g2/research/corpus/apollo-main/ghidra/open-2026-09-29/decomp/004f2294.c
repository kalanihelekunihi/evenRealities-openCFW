
undefined8 FUN_004f2294(void)

{
  int iVar1;
  undefined4 unaff_r5;
  undefined4 unaff_r6;
  
  *DAT_004f2ba4 = 0;
  *DAT_004f2cd8 = 0;
  if (*DAT_004f27f8 != 0) {
    FUN_0043f142(*DAT_004f27f8,*DAT_004f2b9c);
  }
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    unaff_r5 = 0x4cd;
    unaff_r6 = DAT_004f2cdc;
    FUN_0043d574(4,DAT_004f23e0,DAT_004f23dc,DAT_004f2ce0,0x4cd,DAT_004f2cdc,*DAT_004f2b9c);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_004f2ce4,DAT_004f2ce4,*DAT_004f2b9c);
  }
  return CONCAT44(unaff_r6,unaff_r5);
}

