
undefined8 get_silent_mode_ui_showing(void)

{
  int iVar1;
  undefined4 unaff_r5;
  
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    unaff_r5 = 0x18b;
    FUN_0043d574(4,DAT_00469b3c,DAT_00469b38,DAT_00469bec,0x18b,DAT_00469be8,*DAT_00469b44);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_00469bf0,DAT_00469bf0,*DAT_00469b44);
  }
  return CONCAT44(unaff_r5,(uint)*DAT_00469b44);
}

