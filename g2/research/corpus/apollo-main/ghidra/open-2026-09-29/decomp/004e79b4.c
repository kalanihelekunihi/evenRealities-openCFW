
undefined8 FUN_004e79b4(void)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 unaff_r5;
  undefined4 unaff_r6;
  
  *DAT_004e83bc = 0;
  iVar2 = FUN_0043d0ce();
  uVar1 = DAT_004e83c0;
  if (iVar2 << 0x1e < 0) {
    unaff_r5 = 0x1be;
    FUN_0043d574(4,DAT_004e7fe8,DAT_004e7fe4,DAT_004e83c4);
    unaff_r6 = uVar1;
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x10000000,DAT_004e8438,DAT_004e8438);
  }
  return CONCAT44(unaff_r6,unaff_r5);
}

