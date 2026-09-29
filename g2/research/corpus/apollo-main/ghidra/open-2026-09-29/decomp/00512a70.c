
undefined8 FUN_00512a70(void)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 unaff_r5;
  
  iVar1 = FUN_0055fc60(DAT_00512b14,0);
  if (iVar1 == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      unaff_r5 = 0x504;
      FUN_0043d574(1,PTR_s_npmx_driver_00512bc4,DAT_00512bc0,PTR_s_npmx_enter_ship_mode_00512c68,
                   0x504,PTR_s_p_ship_is_NULL_00512c64);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__npmx_driver_p_ship_is_NULL_00512c6c,
                          PTR_s__npmx_driver_p_ship_is_NULL_00512c6c);
    }
    uVar2 = 0xffffffff;
  }
  else {
    iVar1 = func_0x0055fc6a(iVar1,2);
    if (iVar1 == DAT_00512c1c) {
      uVar2 = 0;
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        unaff_r5 = 0x50a;
        FUN_0043d574(1,PTR_s_npmx_driver_00512bc4,DAT_00512bc0,PTR_s_npmx_enter_ship_mode_00512c68,
                     0x50a,PTR_s_npmx_ship_task_trigger_failed_00512c70);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x4000000,PTR_s__npmx_driver_npmx_ship_task_trig_00512c74,
                            PTR_s__npmx_driver_npmx_ship_task_trig_00512c74);
      }
      uVar2 = 0xfffffffe;
    }
  }
  return CONCAT44(unaff_r5,uVar2);
}

