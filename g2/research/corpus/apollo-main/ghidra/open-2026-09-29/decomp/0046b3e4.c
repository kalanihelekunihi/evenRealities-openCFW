
undefined8
SVC_Settings_BatteryCallback(int param_1,int param_2,undefined4 param_3,undefined *param_4)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 uStack_10;
  undefined4 uStack_c;
  
  iVar1 = DAT_0046bee8;
  uStack_10 = param_3;
  uStack_c = param_4;
  if (param_2 == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      uStack_c = PTR_s_battery_callback__data_is_NULL_0046be70;
      uStack_10 = 0x74;
      FUN_0043d574(4,DAT_0046bb74,DAT_0046bb70,PTR_s_SVC_Settings_BatteryCallback_0046be74);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10000000,PTR_s__service_settings_battery_callba_0046be78,
                          PTR_s__service_settings_battery_callba_0046be78);
    }
  }
  else if ((param_1 == 0) || (param_1 == 1)) {
    uVar2 = CHG_GetSoc();
    *(undefined4 *)(iVar1 + 0x38) = uVar2;
    uVar2 = CHG_GetIsCharging();
    *(undefined4 *)(iVar1 + 0x3c) = uVar2;
    setting_notify_device_status_to_app();
  }
  return CONCAT44(uStack_c,uStack_10);
}

