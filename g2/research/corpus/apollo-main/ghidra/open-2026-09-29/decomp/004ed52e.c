
undefined8 FUN_004ed52e(void)

{
  int iVar1;
  undefined4 unaff_r5;
  undefined4 unaff_r6;
  
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    unaff_r5 = 0x7b8;
    unaff_r6 = DAT_004ed78c;
    FUN_0043d574(4,DAT_004ed6e4,DAT_004ed728,DAT_004ed790);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10000000,DAT_004ed794,DAT_004ed794);
  }
  if (*DAT_004ed798 != 0) {
    *DAT_004ed798 = 0;
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      unaff_r5 = 0x7bd;
      unaff_r6 = DAT_004ed79c;
      FUN_0043d574(4,DAT_004ed6e4,DAT_004ed728,DAT_004ed790);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_004ed7a0,DAT_004ed7a0);
    }
  }
  *DAT_004ed7a4 = 0;
  *DAT_004ed7a8 = 0;
  *DAT_004ed7ac = 0;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    unaff_r5 = 0x7c4;
    unaff_r6 = DAT_004ed7b0;
    FUN_0043d574(4,DAT_004ed6e4,DAT_004ed728,DAT_004ed790);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10000000,DAT_004ed7b4,DAT_004ed7b4);
  }
  if (*DAT_004ed7b8 == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      unaff_r5 = 0x7c8;
      unaff_r6 = DAT_004ed7bc;
      FUN_0043d574(2,DAT_004ed6e4,DAT_004ed728,DAT_004ed790);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_004ed7c0,DAT_004ed7c0);
    }
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      unaff_r5 = 0x7ca;
      unaff_r6 = DAT_004ed7c4;
      FUN_0043d574(4,DAT_004ed6e4,DAT_004ed728,DAT_004ed790);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_004ed7c8,DAT_004ed7c8);
    }
  }
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    unaff_r5 = 0x7ce;
    unaff_r6 = DAT_004ed7cc;
    FUN_0043d574(4,DAT_004ed6e4,DAT_004ed728,DAT_004ed790,0x7ce,DAT_004ed7cc,*DAT_004ed748);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_004ed7d0,DAT_004ed7d0,*DAT_004ed748);
  }
  return CONCAT44(unaff_r6,unaff_r5);
}

