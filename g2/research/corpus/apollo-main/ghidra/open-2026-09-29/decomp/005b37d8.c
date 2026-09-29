
undefined8 FUN_005b37d8(void)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 unaff_r5;
  undefined4 unaff_r6;
  
  if (*(char *)(DAT_005b3e34 + 0x96) == '\x01') {
    FUN_005b3570(DAT_005b3e50,5000,DAT_005b3e4c);
  }
  else {
    iVar2 = FUN_0043d0ce();
    uVar1 = DAT_005b3e54;
    if (iVar2 << 0x1e < 0) {
      unaff_r5 = 0xc9;
      FUN_0043d574(4,DAT_005b3e18,DAT_005b3e14,DAT_005b3e58);
      unaff_r6 = uVar1;
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_005b3e5c);
    }
  }
  return CONCAT44(unaff_r6,unaff_r5);
}

