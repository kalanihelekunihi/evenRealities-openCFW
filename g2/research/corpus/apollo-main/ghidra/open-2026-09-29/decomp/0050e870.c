
undefined8 ui_onboarding_stock_sub_0050E870(void)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 unaff_r5;
  undefined4 unaff_r6;
  
  if (*DAT_0050e92c != 0) {
    *DAT_0050e92c = 0;
  }
  *DAT_0050e930 = 0;
  *DAT_0050e934 = 0;
  *DAT_0050e938 = 0;
  *DAT_0050e93c = 0;
  if (*DAT_0050e980 == 0) {
    iVar2 = FUN_0043d0ce();
    uVar1 = DAT_0050e984;
    if (iVar2 << 0x1e < 0) {
      unaff_r5 = 0x994;
      FUN_0043d574(2,DAT_0050e978,DAT_0050e974,DAT_0050e988);
      unaff_r6 = uVar1;
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_0050e98c,DAT_0050e98c);
    }
  }
  return CONCAT44(unaff_r6,unaff_r5);
}

