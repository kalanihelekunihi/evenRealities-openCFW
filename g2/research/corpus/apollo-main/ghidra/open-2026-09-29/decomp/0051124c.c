
undefined8 FUN_0051124c(void)

{
  undefined *puVar1;
  int iVar2;
  undefined4 unaff_r5;
  undefined *unaff_r6;
  
  iVar2 = FUN_0043d0ce();
  puVar1 = PTR_s_Watchdog_triggered_00511bd4;
  if (iVar2 << 0x1e < 0) {
    unaff_r5 = 0x182;
    FUN_0043d574(3,DAT_00511958,DAT_00511954,PTR_s_watchdog_timer_callback_00511bd8);
    unaff_r6 = puVar1;
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0xc000000,PTR_s__npmx_driver_Watchdog_triggered_00511bdc,
                        PTR_s__npmx_driver_Watchdog_triggered_00511bdc);
  }
  return CONCAT44(unaff_r6,unaff_r5);
}

