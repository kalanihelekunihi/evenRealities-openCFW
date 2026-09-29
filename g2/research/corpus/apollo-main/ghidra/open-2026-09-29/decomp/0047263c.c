
undefined8 FUN_0047263c(int param_1)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 unaff_r5;
  
  if (param_1 == 0) {
    uVar1 = 0xffffffff;
  }
  else {
    if ((*(char *)(param_1 + 3) == '\x01') && (*(char *)(param_1 + 4) == '\x01')) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        unaff_r5 = 0x1d5;
        FUN_0043d574(4,DAT_00472bbc,DAT_00472bb8,DAT_00472bf0,0x1d5,DAT_00472bec);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_00472bf4,DAT_00472bf4);
      }
    }
    uVar1 = 0;
  }
  return CONCAT44(unaff_r5,uVar1);
}

