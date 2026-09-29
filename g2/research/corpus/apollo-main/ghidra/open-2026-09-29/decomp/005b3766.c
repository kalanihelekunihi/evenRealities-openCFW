
undefined8 FUN_005b3766(void)

{
  undefined *puVar1;
  int iVar2;
  undefined4 unaff_r5;
  undefined *unaff_r6;
  
  if (*DAT_005b3e34 == '\x01') {
    FUN_005b3570(DAT_005b3e48,2000,PTR_s_Loading_timeout_005b3e44);
  }
  else {
    iVar2 = FUN_0043d0ce();
    puVar1 = PTR_s_Loading_timeout_start_skipped__s_005b3e38;
    if (iVar2 << 0x1e < 0) {
      unaff_r5 = 0xb7;
      FUN_0043d574(4,DAT_005b3e18,DAT_005b3e14,PTR_s_conversate_timer_loading_timeout_005b3e3c);
      unaff_r6 = puVar1;
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10000000,PTR_s__conversate_timer_Loading_timeou_005b3e40,
                          PTR_s__conversate_timer_Loading_timeou_005b3e40);
    }
  }
  return CONCAT44(unaff_r6,unaff_r5);
}

