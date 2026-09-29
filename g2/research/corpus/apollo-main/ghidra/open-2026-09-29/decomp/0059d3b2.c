
undefined8 translate_ui_0059d3b2(void)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 unaff_r5;
  undefined4 unaff_r6;
  
  FUN_0059ec28(9,0);
  iVar2 = FUN_0043d0ce();
  uVar1 = DAT_0059de84;
  if (iVar2 << 0x1e < 0) {
    unaff_r5 = 0x55;
    FUN_0043d574(4,DAT_0059defc,DAT_0059def8,DAT_0059def4);
    unaff_r6 = uVar1;
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x10000000,DAT_0059e110,DAT_0059e110);
  }
  return CONCAT44(unaff_r6,unaff_r5);
}

