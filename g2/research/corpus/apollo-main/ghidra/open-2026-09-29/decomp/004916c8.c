
undefined8 FUN_004916c8(int param_1)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 unaff_r5;
  
  if (*(char *)(param_1 + 0x642e) == '\0') {
    *(undefined1 *)(param_1 + 0x642e) = 1;
    uVar2 = 1;
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      unaff_r5 = 0x23;
      FUN_0043d574(1,DAT_00491ee8,DAT_00491ee4,DAT_00491ee0,0x23,DAT_00491edc);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_00491eec,DAT_00491eec);
    }
    uVar2 = 0;
  }
  return CONCAT44(unaff_r5,uVar2);
}

