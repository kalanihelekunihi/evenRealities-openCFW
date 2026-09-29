
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

longlong FUN_00467e68(uint param_1,undefined4 param_2,uint param_3,undefined4 param_4)

{
  int iVar1;
  
  if (param_1 == 2) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      param_3 = 0x305;
      FUN_0043d574(4,PTR_s_setting_00467f14,PTR_s_D__01_workspace_s200_ap510b_iar__00467f10,
                   PTR_s_Setting_ui_event_handler_00467fdc,0x305,
                   PTR_s_setting_DISPLAY_STARTUP_00467fd8);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10000000,PTR_s__setting_setting_DISPLAY_STARTUP_00467fe0,
                          PTR_s__setting_setting_DISPLAY_STARTUP_00467fe0);
    }
    hub_calibration_display_update(param_4);
    *(undefined4 *)(_DAT_00467fe8 + 4) = *_DAT_00467fe4;
  }
  else if ((1 < param_1) && (param_1 != 4)) {
    if (param_1 < 4) {
      hub_calibration_success_display();
      iVar1 = settings_get_config();
      *(undefined4 *)(iVar1 + 0x40) = 1;
      setting_notify_device_status_to_app();
    }
    else if (param_1 == 5) {
      iVar1 = settings_get_config();
      *(undefined4 *)(iVar1 + 0x40) = 0;
      *DAT_00467fec = 0;
      setting_notify_recalibration_status_to_app(1);
      setting_notify_device_status_to_app();
    }
  }
  return (ulonglong)param_3 << 0x20;
}

