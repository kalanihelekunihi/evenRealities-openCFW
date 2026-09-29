
undefined8 page_data_lock(void)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 unaff_r5;
  
  if (*DAT_0058b344 == 0) {
    uVar1 = 1;
  }
  else {
    iVar2 = osMutexAcquire(*DAT_0058b344,0xffffffff);
    if (iVar2 == 0) {
      uVar1 = 1;
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        unaff_r5 = 0x5a;
        FUN_0043d574(1,DAT_0058b354,DAT_0058b350,DAT_0058b34c,0x5a,DAT_0058b348);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_0058b528,DAT_0058b528);
      }
      uVar1 = 0;
    }
  }
  return CONCAT44(unaff_r5,uVar1);
}

