
undefined8 _flashDBMutexLock(void)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 unaff_r5;
  undefined4 unaff_r6;
  
  iVar2 = osMutexAcquire(*DAT_0054129c,0xffffffff);
  if (iVar2 != 0) {
    iVar2 = FUN_0043d0ce();
    uVar1 = DAT_005412b0;
    if (iVar2 << 0x1e < 0) {
      unaff_r5 = 0x94;
      FUN_0043d574(1,DAT_00541268,DAT_00541264,DAT_005412b4);
      unaff_r6 = uVar1;
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_005412b8,DAT_005412b8);
    }
  }
  return CONCAT44(unaff_r6,unaff_r5);
}

