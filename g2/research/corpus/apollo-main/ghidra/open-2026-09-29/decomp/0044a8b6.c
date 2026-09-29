
undefined8 compress_log_export_timeout_callback(void)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 unaff_r5;
  undefined4 unaff_r6;
  
  iVar2 = FUN_0043d0ce();
  uVar1 = DAT_0044aa00;
  if (iVar2 << 0x1e < 0) {
    unaff_r5 = 0x157;
    FUN_0043d574(2,DAT_0044a9e4,DAT_0044a9e0,DAT_0044aa04);
    unaff_r6 = uVar1;
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x8000000,DAT_0044aa08,DAT_0044aa08);
  }
  *DAT_0044aa0c = 0;
  return CONCAT44(unaff_r6,unaff_r5);
}

