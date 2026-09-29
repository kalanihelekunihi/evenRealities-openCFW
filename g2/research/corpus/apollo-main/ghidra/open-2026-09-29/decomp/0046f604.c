
undefined8 FUN_0046f604(void)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 unaff_r5;
  undefined4 unaff_r6;
  
  if ((*DAT_0047001c != 0) && (iVar2 = osMutexRelease(*DAT_0047001c), iVar2 != 0)) {
    iVar2 = FUN_0043d0ce();
    uVar1 = DAT_00470160;
    if (iVar2 << 0x1e < 0) {
      unaff_r5 = 0xcc;
      FUN_0043d574(1,DAT_004700a8,DAT_004700a4,DAT_00470164);
      unaff_r6 = uVar1;
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_004702d0,DAT_004702d0);
    }
  }
  return CONCAT44(unaff_r6,unaff_r5);
}

