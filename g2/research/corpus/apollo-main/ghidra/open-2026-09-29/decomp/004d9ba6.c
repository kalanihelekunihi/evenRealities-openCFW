
undefined8 FUN_004d9ba6(void)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 unaff_r5;
  undefined4 unaff_r6;
  
  if (*DAT_004da5f0 == 0) {
    iVar2 = FUN_0043d0ce();
    uVar1 = DAT_004da604;
    if (iVar2 << 0x1e < 0) {
      unaff_r5 = 0x51;
      FUN_0043d574(1,DAT_004da600,DAT_004da5fc,DAT_004da608);
      unaff_r6 = uVar1;
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_004da7c4,DAT_004da7c4);
    }
  }
  else {
    osMutexRelease(*DAT_004da5f0);
  }
  return CONCAT44(unaff_r6,unaff_r5);
}

