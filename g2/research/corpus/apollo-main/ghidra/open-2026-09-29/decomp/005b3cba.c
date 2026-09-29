
undefined8 FUN_005b3cba(void)

{
  undefined *puVar1;
  int iVar2;
  undefined4 unaff_r5;
  undefined *unaff_r6;
  
  iVar2 = FUN_0045a568();
  if (iVar2 == 1) {
    FUN_005b38cc();
    iVar2 = FUN_0043d0ce();
    puVar1 = PTR_s_Timer_manager_initialized_005b3ed4;
    if (iVar2 << 0x1e < 0) {
      unaff_r5 = 0x175;
      FUN_0043d574(4,DAT_005b3e18,DAT_005b3e14,PTR_s_conversate_timer_mgr_init_005b3ed8);
      unaff_r6 = puVar1;
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10000000,PTR_s__conversate_timer_Timer_manager_i_005b3edc,
                          PTR_s__conversate_timer_Timer_manager_i_005b3edc);
    }
  }
  return CONCAT44(unaff_r6,unaff_r5);
}

