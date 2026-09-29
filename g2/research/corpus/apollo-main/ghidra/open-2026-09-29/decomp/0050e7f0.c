
undefined8 ui_onboarding_stock_sub_0050E7F0(void)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 unaff_r5;
  undefined4 unaff_r6;
  
  if (*DAT_0050e868 != 0) {
    *DAT_0050e868 = 0;
  }
  *DAT_0050e958 = 0;
  *DAT_0050e95c = 0;
  *DAT_0050e960 = 0;
  *DAT_0050e964 = 0;
  if (*DAT_0050e92c == 0) {
    iVar2 = FUN_0043d0ce();
    uVar1 = DAT_0050e96c;
    if (iVar2 << 0x1e < 0) {
      unaff_r5 = 0x978;
      FUN_0043d574(2,DAT_0050e978,DAT_0050e974,DAT_0050e970);
      unaff_r6 = uVar1;
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_0050e97c,DAT_0050e97c);
    }
  }
  return CONCAT44(unaff_r6,unaff_r5);
}

