
undefined8 quicklist_lock_storage(void)

{
  int iVar1;
  uint uVar2;
  undefined4 unaff_r5;
  
  if (*DAT_004ffba8 == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      unaff_r5 = 0x33;
      FUN_0043d574(2,DAT_004ffbb8,DAT_004ffbb4,DAT_004ffbc4,0x33,DAT_004ffbc0);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8000000,PTR_s__quicklist_page_mutex_is_NULL_004ffbc8,
                          PTR_s__quicklist_page_mutex_is_NULL_004ffbc8);
    }
    uVar2 = 0;
  }
  else {
    iVar1 = osMutexAcquire(*DAT_004ffba8,0xffffffff);
    uVar2 = (uint)(iVar1 == 0);
  }
  return CONCAT44(unaff_r5,uVar2);
}

