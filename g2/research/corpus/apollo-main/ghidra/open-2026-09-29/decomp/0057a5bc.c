
undefined8 DRV_Gx8002_PowerOff(void)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 unaff_r5;
  undefined4 unaff_r6;
  
  if (*DAT_0057a888 == '\0') {
    iVar2 = FUN_0043d0ce();
    uVar1 = DAT_0057a8a8;
    if (iVar2 << 0x1e < 0) {
      unaff_r5 = 0x67;
      FUN_0043d574(4,DAT_0057a898,DAT_0057a894,DAT_0057a8ac);
      unaff_r6 = uVar1;
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_0057a8b0,DAT_0057a8b0);
    }
  }
  else {
    *DAT_0057a888 = '\0';
    FUN_00509024(6,0);
    FUN_00509024(7,0);
    FUN_00509024(8,0);
    iVar2 = FUN_0043d0ce();
    uVar1 = DAT_0057a8b4;
    if (iVar2 << 0x1e < 0) {
      unaff_r5 = 0x6e;
      FUN_0043d574(4,DAT_0057a898,DAT_0057a894,DAT_0057a8ac);
      unaff_r6 = uVar1;
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_0057a8b8,DAT_0057a8b8);
    }
  }
  return CONCAT44(unaff_r6,unaff_r5);
}

