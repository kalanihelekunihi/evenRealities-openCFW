
undefined8 FUN_0047b4d4(void)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 unaff_r5;
  undefined4 unaff_r6;
  
  iVar2 = FUN_0043d0ce();
  uVar1 = DAT_0047bc18;
  if (iVar2 << 0x1e < 0) {
    unaff_r5 = 0x706;
    FUN_0043d574(4,DAT_0047bc24,DAT_0047bc20,DAT_0047bc1c);
    unaff_r6 = uVar1;
  }
  iVar2 = FUN_0043d0ce();
  if (-1 < iVar2 << 0x1f) {
    iVar2 = FUN_0043d0ce();
    if (-1 < iVar2 << 0x1d) goto LAB_0047b51a;
  }
  compress_log_output(0x10000000,DAT_0047bc28,DAT_0047bc28);
LAB_0047b51a:
  DmPrivClearResList();
  FUN_00479418();
  iVar2 = FUN_0043d0ce();
  uVar1 = DAT_0047bc2c;
  if (iVar2 << 0x1e < 0) {
    unaff_r5 = 0x70e;
    FUN_0043d574(4,DAT_0047bc24,DAT_0047bc20,DAT_0047bc1c);
    unaff_r6 = uVar1;
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x10000000,DAT_0047c06c,DAT_0047c06c);
  }
  return CONCAT44(unaff_r6,unaff_r5);
}

