
undefined8 FUN_004e7a10(void)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 unaff_r5;
  undefined4 unaff_r6;
  
  *DAT_004e83bc = 0;
  iVar2 = FUN_0043d0ce();
  uVar1 = DAT_004e843c;
  if (iVar2 << 0x1e < 0) {
    unaff_r5 = 0x1ce;
    FUN_0043d574(4,DAT_004e7fe8,DAT_004e7fe4,DAT_004e8440);
    unaff_r6 = uVar1;
  }
  iVar2 = FUN_0043d0ce();
  if (-1 < iVar2 << 0x1f) {
    iVar2 = FUN_0043d0ce();
    if (-1 < iVar2 << 0x1d) goto LAB_004e7a5e;
  }
  compress_log_output(0x10000000,DAT_004e8444,DAT_004e8444);
LAB_004e7a5e:
  iVar2 = FUN_0045a568();
  if (iVar2 == 1) {
    FUN_00464c36(1,0,0,0);
  }
  return CONCAT44(unaff_r6,unaff_r5);
}

