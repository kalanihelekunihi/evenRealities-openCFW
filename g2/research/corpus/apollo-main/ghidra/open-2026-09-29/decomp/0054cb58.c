
undefined8 FUN_0054cb58(void)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 unaff_r5;
  undefined4 unaff_r6;
  
  iVar2 = FUN_0043d0ce();
  uVar1 = DAT_0054cfa0;
  if (iVar2 << 0x1e < 0) {
    unaff_r5 = 0xc4d;
    FUN_0043d574(4,PTR_s_navigation_ui_0054cf58,DAT_0054cf54,DAT_0054cfa4);
    unaff_r6 = uVar1;
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x10000000,DAT_0054cfa8,DAT_0054cfa8);
  }
  *DAT_0054cca0 = 0;
  FUN_0054c3f2();
  return CONCAT44(unaff_r6,unaff_r5);
}

