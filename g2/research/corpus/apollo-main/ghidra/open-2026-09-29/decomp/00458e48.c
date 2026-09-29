
undefined8 loggerSetting_cancel_ble_transmit(void)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 unaff_r5;
  undefined4 unaff_r6;
  
  iVar2 = loggerSetting_ble_transmit_enabled();
  if (iVar2 != 0) {
    iVar2 = FUN_0043d0ce();
    uVar1 = DAT_00459270;
    if (iVar2 << 0x1e < 0) {
      unaff_r5 = 0x53;
      FUN_0043d574(3,DAT_0045927c,DAT_00459278,DAT_00459274);
      unaff_r6 = uVar1;
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0xc000000,PTR_s__logger_setting_loggerSetting_ca_00459280,
                          PTR_s__logger_setting_loggerSetting_ca_00459280);
    }
    loggerSetting_set_ble_transmit(0);
  }
  return CONCAT44(unaff_r6,unaff_r5);
}

