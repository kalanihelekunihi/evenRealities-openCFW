
undefined8 FUN_004601ea(void)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 unaff_r5;
  undefined4 unaff_r6;
  
  if (*DAT_0046061c == 0) {
    iVar2 = FUN_0043d0ce();
    uVar1 = DAT_00460630;
    if (iVar2 << 0x1e < 0) {
      unaff_r5 = 0x56;
      FUN_0043d574(1,DAT_0046062c,DAT_00460628,DAT_00460634);
      unaff_r6 = uVar1;
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_00460e00,DAT_00460e00);
    }
  }
  else {
    osMutexRelease(*DAT_0046061c);
  }
  return CONCAT44(unaff_r6,unaff_r5);
}

