
undefined8 FUN_005b3c2a(void)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 unaff_r5;
  undefined4 unaff_r6;
  
  *(undefined4 *)(DAT_005b3e48 + 0x18) = 0xffffffff;
  iVar2 = FUN_0043d0ce();
  uVar1 = DAT_005b3ebc;
  if (iVar2 << 0x1e < 0) {
    unaff_r5 = 0x158;
    FUN_0043d574(4,DAT_005b3e18,DAT_005b3e14,DAT_005b3ec0);
    unaff_r6 = uVar1;
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x10000000,DAT_005b3ec4,DAT_005b3ec4);
  }
  return CONCAT44(unaff_r6,unaff_r5);
}

