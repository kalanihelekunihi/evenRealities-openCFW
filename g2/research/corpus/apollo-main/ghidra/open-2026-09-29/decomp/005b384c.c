
undefined8 FUN_005b384c(void)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 unaff_r5;
  undefined4 unaff_r6;
  
  if ((*DAT_005b3e34 == '\x04') && (DAT_005b3e34[0x96] == '\0')) {
    FUN_005b3570(DAT_005b3e70,1000,DAT_005b3e6c);
  }
  else {
    iVar2 = FUN_0043d0ce();
    uVar1 = DAT_005b3e60;
    if (iVar2 << 0x1e < 0) {
      unaff_r5 = 0xd5;
      FUN_0043d574(4,DAT_005b3e18,DAT_005b3e14,DAT_005b3e64);
      unaff_r6 = uVar1;
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_005b3e68,DAT_005b3e68);
    }
  }
  return CONCAT44(unaff_r6,unaff_r5);
}

