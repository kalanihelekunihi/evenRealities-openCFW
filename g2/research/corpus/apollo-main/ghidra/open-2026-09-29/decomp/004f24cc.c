
undefined8 FUN_004f24cc(void)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 unaff_r5;
  undefined4 unaff_r6;
  
  *DAT_004f2cd8 = 0;
  iVar2 = FUN_0043d0ce();
  uVar1 = DAT_004f2eb8;
  if (iVar2 << 0x1e < 0) {
    unaff_r5 = 0x502;
    FUN_0043d574(4,DAT_004f2eb4,DAT_004f2eb0,DAT_004f2ebc);
    unaff_r6 = uVar1;
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x10000000,DAT_004f31b8,DAT_004f31b8);
  }
  return CONCAT44(unaff_r6,unaff_r5);
}

