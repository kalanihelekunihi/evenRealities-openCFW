
undefined8 FUN_004c59aa(void)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 unaff_r5;
  undefined4 unaff_r6;
  
  iVar2 = osKernelGetTickCount();
  if (((uint)(iVar2 - *DAT_004c618c) < 1000) || ((uint)(iVar2 - *DAT_004c6190) < 1000)) {
    iVar2 = FUN_0043d0ce();
    uVar1 = DAT_004c6194;
    if (iVar2 << 0x1e < 0) {
      unaff_r5 = 0x71;
      FUN_0043d574(2,DAT_004c6184,DAT_004c6180,DAT_004c6198);
      unaff_r6 = uVar1;
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_004c619c,DAT_004c619c);
    }
  }
  else {
    iVar2 = FUN_0043d0ce();
    uVar1 = DAT_004c61a0;
    if (iVar2 << 0x1e < 0) {
      unaff_r5 = 0x76;
      FUN_0043d574(2,DAT_004c6184,DAT_004c6180,DAT_004c6198);
      unaff_r6 = uVar1;
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_004c61a4,DAT_004c61a4);
    }
    SilentMode_ToggleByLocalLongPress();
  }
  return CONCAT44(unaff_r6,unaff_r5);
}

