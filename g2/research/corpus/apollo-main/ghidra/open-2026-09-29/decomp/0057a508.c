
undefined8 DRV_Gx8002_PowerOn(void)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 unaff_r5;
  undefined4 unaff_r6;
  
  if (*DAT_0057a888 == '\0') {
    *DAT_0057a888 = '\x01';
    FUN_00509024(6,1);
    osDelay(5);
    FUN_00509024(7,1);
    osDelay(0x14);
    FUN_00509024(8,1);
    iVar2 = FUN_0043d0ce();
    uVar1 = DAT_0057a8a0;
    if (iVar2 << 0x1e < 0) {
      unaff_r5 = 0x61;
      FUN_0043d574(4,DAT_0057a898,DAT_0057a894,DAT_0057a890);
      unaff_r6 = uVar1;
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_0057a8a4,DAT_0057a8a4);
    }
  }
  else {
    iVar2 = FUN_0043d0ce();
    uVar1 = DAT_0057a88c;
    if (iVar2 << 0x1e < 0) {
      unaff_r5 = 0x57;
      FUN_0043d574(4,DAT_0057a898,DAT_0057a894,DAT_0057a890);
      unaff_r6 = uVar1;
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_0057a89c,DAT_0057a89c);
    }
  }
  return CONCAT44(unaff_r6,unaff_r5);
}

