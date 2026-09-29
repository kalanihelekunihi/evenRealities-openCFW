
void jdb4010_status_recovery(void)

{
  undefined4 uVar1;
  int iVar2;
  
  uVar1 = service_settings_auto_brightness();
  SVC_Settings_BrightnessLevelToLumAndCurrent(uVar1,&stack0xfffffff0,&stack0xfffffff4);
  jbd4010_power_on_sequence();
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    FUN_0043d574(3,DAT_00593900,DAT_005938fc,PTR_s_jdb4010_status_recovery_00593960,0x310,
                 PTR_s_jdb4010_power_down_done_0059395c);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0xc000000,PTR_s__driver_jbd4010_jdb4010_power_do_00593964,
                        PTR_s__driver_jbd4010_jdb4010_power_do_00593964);
  }
  FUN_004910f4(1);
  jbd4010_power_off_sequence();
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    FUN_0043d574(3,DAT_00593900,DAT_005938fc,PTR_s_jdb4010_status_recovery_00593960,0x314,
                 PTR_s_jdb4010_power_up_done_00593968);
  }
  iVar2 = FUN_0043d0ce();
  if (-1 < iVar2 << 0x1f) {
    iVar2 = FUN_0043d0ce();
    if (-1 < iVar2 << 0x1d) goto LAB_005935d4;
  }
  compress_log_output(0xc000000,PTR_s__driver_jbd4010_jdb4010_power_up_0059396c,
                      PTR_s__driver_jbd4010_jdb4010_power_up_0059396c);
LAB_005935d4:
  am_devices_mspi_jbd4010_configure();
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    FUN_0043d574(3,DAT_00593900,DAT_005938fc,PTR_s_jdb4010_status_recovery_00593960,0x316,
                 PTR_s_jdb4010_configure_done_00593970);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0xc000000,PTR_s__driver_jbd4010_jdb4010_configur_00593974,
                        PTR_s__driver_jbd4010_jdb4010_configur_00593974);
  }
  FUN_004910f4(1);
  am_devices_jbd4010_QSPI_PartialReflash_async(0,0,0,0,0x280,0x1e0);
  FUN_004910f4(1);
  am_devices_mspi_jbd4010_setBrightness(0,0,0);
  return;
}

