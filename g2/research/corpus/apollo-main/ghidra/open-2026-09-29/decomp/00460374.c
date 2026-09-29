
undefined8 FUN_00460374(void)

{
  int iVar1;
  undefined4 unaff_r5;
  undefined4 unaff_r6;
  
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    unaff_r5 = 0x117;
    unaff_r6 = DAT_00460d60;
    FUN_0043d574(3,DAT_0046062c,DAT_00460628,DAT_00460d64,0x117,DAT_00460d60,0xfa);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0xc400000,DAT_00460d68,DAT_00460d68,0xfa);
  }
  *(undefined4 *)(DAT_00460e08 + 0xc) = 0xfa;
  if ((*DAT_00460e0c != 0) && (iVar1 = FUN_0045f840(*DAT_00460e0c,3), iVar1 != 0)) {
    *(undefined4 *)(iVar1 + 0xc) = 0xfa;
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      unaff_r5 = 0x11f;
      unaff_r6 = DAT_00460e10;
      FUN_0043d574(4,DAT_0046062c,DAT_00460628,DAT_00460d64);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_00461028,DAT_00461028);
    }
  }
  return CONCAT44(unaff_r6,unaff_r5);
}

