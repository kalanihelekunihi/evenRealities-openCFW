
undefined8 _flashDBMutexUnlock(void)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 unaff_r5;
  undefined4 unaff_r6;
  
  iVar2 = osMutexRelease(*DAT_0054129c);
  if (iVar2 != 0) {
    iVar2 = FUN_0043d0ce();
    uVar1 = DAT_005412bc;
    if (iVar2 << 0x1e < 0) {
      unaff_r5 = 0x9b;
      FUN_0043d574(1,DAT_00541268,DAT_00541264,DAT_005412c0);
      unaff_r6 = uVar1;
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_005412c4,DAT_005412c4);
    }
  }
  return CONCAT44(unaff_r6,unaff_r5);
}

