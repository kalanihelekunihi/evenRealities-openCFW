
undefined4 am_devices_hongshi_status_check_and_recovery(void)

{
  char cVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  undefined1 auStack_24 [24];
  undefined4 local_c;
  
  FUN_00439be4(DAT_005bd350,PTR_DAT_005bd34c,8);
  FUN_00439c04(auStack_24,PTR_DAT_005bd354,0x1c);
  local_c = *DAT_005bd304;
  iVar2 = am_devices_mspi_write(auStack_24);
  if (iVar2 != 0) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(1,DAT_005bd2f4,DAT_005bd2f0,PTR_s_am_devices_hongshi_status_check__005bd35c,0x413
                   ,PTR_s_status_check_and_recovery_spi_wr_005bd358,iVar2);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x4400000,PTR_s__driver_a6n_g_status_check_and_r_005bd360,
                          PTR_s__driver_a6n_g_status_check_and_r_005bd360,iVar2);
    }
    return 0;
  }
  cVar1 = am_devices_mspi_hongshi_read_bank(0xbe,0);
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    FUN_0043d574(3,DAT_005bd2f4,DAT_005bd2f0,PTR_s_am_devices_hongshi_status_check__005bd35c,0x41a,
                 PTR_s_status_check_bank0_0xBE___0x_02X_005bd364,cVar1);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0xc400000,PTR_s__driver_a6n_g_status_check_bank0_005bd368,
                        PTR_s__driver_a6n_g_status_check_bank0_005bd368,cVar1);
  }
  if (cVar1 != -0x7c) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,DAT_005bd2f4,DAT_005bd2f0,PTR_s_am_devices_hongshi_status_check__005bd35c,0x41c
                   ,PTR_s_hongshi_ASIC_abnormal__bank0_0xB_005bd36c,cVar1);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4400000,PTR_s__driver_a6n_g_hongshi_ASIC_abnor_005bd370,
                          PTR_s__driver_a6n_g_hongshi_ASIC_abnor_005bd370,cVar1);
    }
    am_devices_hongshi_status_recovery();
    return 0;
  }
  cVar1 = am_devices_mspi_hongshi_read_bank(0x62,0);
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    FUN_0043d574(3,DAT_005bd2f4,DAT_005bd2f0,PTR_s_am_devices_hongshi_status_check__005bd35c,0x423,
                 PTR_s_status_check_bank0_0x62___0x_02X_005bd374,cVar1);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0xc400000,PTR_s__driver_a6n_g_status_check_bank0_005bd378,
                        PTR_s__driver_a6n_g_status_check_bank0_005bd378,cVar1);
  }
  if ((cVar1 != 'w') && (cVar1 != 'W')) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,DAT_005bd2f4,DAT_005bd2f0,PTR_s_am_devices_hongshi_status_check__005bd35c,0x425
                   ,PTR_s_hongshi_panel_abnormal__bank0_0x_005bd37c,cVar1);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4400000,PTR_s__driver_a6n_g_hongshi_panel_abno_005bd380,
                          PTR_s__driver_a6n_g_hongshi_panel_abno_005bd380,cVar1);
    }
    am_devices_hongshi_status_recovery();
    return 0;
  }
  uVar4 = hongshi_read_panel_mirror();
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    FUN_0043d574(3,DAT_005bd2f4,DAT_005bd2f0,PTR_s_am_devices_hongshi_status_check__005bd35c,0x42f,
                 PTR_s_status_check_panel_mirror_reg___0_005bd384,uVar4 & 0xff);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0xc400000,PTR_s__driver_a6n_g_status_check_panel_005bd388,
                        PTR_s__driver_a6n_g_status_check_panel_005bd388,uVar4 & 0xff);
  }
  if (-1 < (int)(uVar4 << 0x1a)) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,DAT_005bd2f4,DAT_005bd2f0,PTR_s_am_devices_hongshi_status_check__005bd35c,0x432
                   ,PTR_s_hongshi_panel_abnormal__mirror___005bd38c,uVar4 & 0xff);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4400000,PTR_s__driver_a6n_g_hongshi_panel_abno_005bd390,
                          PTR_s__driver_a6n_g_hongshi_panel_abno_005bd390,uVar4 & 0xff);
    }
    am_devices_hongshi_status_recovery();
    return 0;
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    FUN_0043d574(3,DAT_005bd2f4,DAT_005bd2f0,PTR_s_am_devices_hongshi_status_check__005bd35c,0x436,
                 PTR_s_hongshi_panel_normal__mirror___0_005bd394,uVar4 & 0xff);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0xc400000,PTR_s__driver_a6n_g_hongshi_panel_norm_005bd398,
                        PTR_s__driver_a6n_g_hongshi_panel_norm_005bd398,uVar4 & 0xff);
  }
  return 1;
}

