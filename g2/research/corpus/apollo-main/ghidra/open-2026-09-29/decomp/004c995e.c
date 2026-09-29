
undefined8 FUN_004c995e(int param_1,undefined4 param_2,undefined4 param_3,undefined *param_4)

{
  int iVar1;
  undefined4 local_10;
  undefined4 local_c;
  
  local_10 = param_3;
  local_c = param_4;
  if (param_1 << 0x1a < 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      local_c = PTR_s__sys__enter_mode__ota_004c9ce8;
      local_10 = 0x13c;
      FUN_0043d574(3,DAT_004c9ca4,DAT_004c9ca0,PTR_s__thread_notify_event_handler_004c9cec);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0xc000000,PTR_s__task_manager__sys__enter_mode__o_004c9cf0,
                          PTR_s__task_manager__sys__enter_mode__o_004c9cf0);
    }
    if (*DAT_004c9cf4 == '\0') {
      *DAT_004c9cf4 = '\x01';
      FUN_004c9778(param_1);
    }
  }
  if (param_1 << 0x1f < 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      local_c = PTR_s__sys__enter_mode__poweroff_004c9cf8;
      local_10 = 0x146;
      FUN_0043d574(4,DAT_004c9ca4,DAT_004c9ca0,PTR_s__thread_notify_event_handler_004c9cec);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10000000,PTR_s__task_manager__sys__enter_mode__p_004c9cfc);
    }
    FUN_004c9778(param_1);
  }
  if (param_1 << 0x1e < 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      local_c = PTR_s__sys__enter_mode__reboot_004c9d00;
      local_10 = 0x14e;
      FUN_0043d574(4,DAT_004c9ca4,DAT_004c9ca0,PTR_s__thread_notify_event_handler_004c9cec);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10000000,PTR_s__task_manager__sys__enter_mode__r_004c9d04,
                          PTR_s__task_manager__sys__enter_mode__r_004c9d04);
    }
    FUN_004c9778(param_1);
  }
  if (param_1 << 0x1d < 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      local_c = PTR_s__sys__enter_mode__shipmode_004c9d08;
      local_10 = 0x156;
      FUN_0043d574(4,DAT_004c9ca4,DAT_004c9ca0,PTR_s__thread_notify_event_handler_004c9cec);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10000000,PTR_s__task_manager__sys__enter_mode__s_004c9d0c,
                          PTR_s__task_manager__sys__enter_mode__s_004c9d0c);
    }
    FUN_004c9778(param_1);
  }
  if (param_1 << 0x1c < 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      local_c = PTR_s__sys__enter_mode__lowpower_004c9d10;
      local_10 = 0x15d;
      FUN_0043d574(4,DAT_004c9ca4,DAT_004c9ca0,PTR_s__thread_notify_event_handler_004c9cec);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10000000,PTR_s__task_manager__sys__enter_mode__l_004c9d14,
                          PTR_s__task_manager__sys__enter_mode__l_004c9d14);
    }
    FUN_004c9778(param_1);
  }
  if (param_1 << 0x1b < 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      local_c = PTR_s__sys__enter_mode__temp_abnormal_004c9d18;
      local_10 = 0x164;
      FUN_0043d574(4,DAT_004c9ca4,DAT_004c9ca0,PTR_s__thread_notify_event_handler_004c9cec);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10000000,PTR_s__task_manager__sys__enter_mode__t_004c9d1c,
                          PTR_s__task_manager__sys__enter_mode__t_004c9d1c);
    }
    FUN_004c9778(param_1);
  }
  return CONCAT44(local_c,local_10);
}

