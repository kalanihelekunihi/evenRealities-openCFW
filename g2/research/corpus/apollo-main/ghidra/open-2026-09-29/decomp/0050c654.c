
undefined8 FUN_0050c654(void)

{
  int iVar1;
  uint uVar2;
  undefined4 unaff_r5;
  
  iVar1 = FUN_0050c476(DAT_0050c864);
  if (iVar1 == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      unaff_r5 = 0x948;
      FUN_0043d574(2,DAT_0050c9c8,DAT_0050c9c4,DAT_0050c9fc,0x948,DAT_0050c9f8);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_0050ca00,DAT_0050ca00);
    }
    uVar2 = 0;
  }
  else {
    uVar2 = (uint)*(byte *)(iVar1 + 0x29);
  }
  return CONCAT44(unaff_r5,uVar2);
}

