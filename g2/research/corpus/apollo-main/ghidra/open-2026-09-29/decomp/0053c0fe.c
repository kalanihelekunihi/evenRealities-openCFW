
undefined8 DRV_Bq27427HwInit(void)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 unaff_r5;
  
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    unaff_r5 = 0x2f0;
    FUN_0043d574(4,DAT_0053c238,DAT_0053c234,DAT_0053c28c,0x2f0,DAT_0053c288);
  }
  iVar1 = FUN_0043d0ce();
  if (-1 < iVar1 << 0x1f) {
    iVar1 = FUN_0043d0ce();
    if (-1 < iVar1 << 0x1d) goto LAB_0053c13a;
  }
  compress_log_output(0x10000000,DAT_0053c290,DAT_0053c290);
LAB_0053c13a:
  bq27427_settings();
  iVar1 = bq27427_status_update();
  if (iVar1 == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      unaff_r5 = 0x2f7;
      FUN_0043d574(4,DAT_0053c238,DAT_0053c234,DAT_0053c28c,0x2f7,DAT_0053c29c);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_0053c2a0,DAT_0053c2a0);
    }
    uVar2 = 0;
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      unaff_r5 = 0x2f3;
      FUN_0043d574(4,DAT_0053c238,DAT_0053c234,DAT_0053c28c,0x2f3,DAT_0053c294);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_0053c298,DAT_0053c298);
    }
    uVar2 = 0xffffffff;
  }
  return CONCAT44(unaff_r5,uVar2);
}

