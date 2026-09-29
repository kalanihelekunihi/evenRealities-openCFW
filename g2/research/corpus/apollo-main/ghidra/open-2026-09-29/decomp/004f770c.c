
undefined8 FUN_004f770c(void)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 unaff_r5;
  undefined4 unaff_r6;
  
  *DAT_004f81d8 = 0;
  iVar2 = FUN_0043d0ce();
  uVar1 = DAT_004f8098;
  if (iVar2 << 0x1e < 0) {
    unaff_r5 = 0x94e;
    FUN_0043d574(4,DAT_004f81e0,DAT_004f81dc,DAT_004f809c);
    unaff_r6 = uVar1;
  }
  iVar2 = FUN_0043d0ce();
  if (-1 < iVar2 << 0x1f) {
    iVar2 = FUN_0043d0ce();
    if (-1 < iVar2 << 0x1d) goto LAB_004f775a;
  }
  compress_log_output(0x10000000,DAT_004f8328,DAT_004f8328);
LAB_004f775a:
  FUN_004faf20();
  return CONCAT44(unaff_r6,unaff_r5);
}

