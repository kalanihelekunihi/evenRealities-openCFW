
void SVC_Settings_SyncHandler(char *param_1,uint param_2)

{
  int iVar1;
  uint uVar2;
  undefined4 uVar3;
  
  if ((param_1 == (char *)0x0) || (param_2 < 0x30)) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(2,PTR_s_service_settings_0046c664,DAT_0046c660,
                   PTR_s_SVC_Settings_SyncHandler_0046c65c,0x10d,
                   PTR_s_invalid_sync_data__len__u_0046c658,param_2);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8400000,PTR_s__service_settings_invalid_sync_d_0046c668,
                          PTR_s__service_settings_invalid_sync_d_0046c668,param_2);
    }
  }
  else if ((*param_1 == '\0') && (iVar1 = FUN_0045a568(), iVar1 == 2)) {
    FUN_00439c04(DAT_0046bee8,param_1 + 4,0x1c);
    uVar2 = settings_get_terminal_mode();
    if (uVar2 != (byte)param_1[0x21]) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        uVar3 = settings_get_terminal_mode();
        FUN_0043d574(3,PTR_s_service_settings_0046c664,DAT_0046c660,
                     PTR_s_SVC_Settings_SyncHandler_0046c65c,0x114,
                     PTR_s_terminal_mode_changed___d__>__d__0046c66c,uVar3,param_1[0x21]);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        uVar3 = settings_get_terminal_mode();
        compress_log_output(0xc800000,PTR_s__service_settings_terminal_mode_c_0046c670,
                            PTR_s__service_settings_terminal_mode_c_0046c670,uVar3,param_1[0x21]);
      }
      settings_set_terminal_mode(param_1[0x21]);
    }
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(3,PTR_s_service_settings_0046c664,DAT_0046c660,
                   PTR_s_SVC_Settings_SyncHandler_0046c65c,0x118,
                   PTR_s_recv_master_settings_sync__0046c674);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0xc000000,PTR_s__service_settings_recv_master_se_0046c678,
                          PTR_s__service_settings_recv_master_se_0046c678);
    }
    SVC_Settings_DumpSettingConfig();
    settings_apply_display_levels();
    SVC_Settings_SyncVersionOnlySend();
  }
  else if ((*param_1 == '\x01') && (iVar1 = FUN_0045a568(), iVar1 == 1)) {
    SVC_Settings_UpdateLeftVersion(param_1 + 0x24);
    if (*(short *)(param_1 + 0x1c) == *(short *)(DAT_0046bee8 + 0x18)) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(3,PTR_s_service_settings_0046c664,DAT_0046c660,
                     PTR_s_SVC_Settings_SyncHandler_0046c65c,0x125,
                     PTR_s_crc_value_match__not_send_0046c67c);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0xc000000,PTR_s__service_settings_crc_value_matc_0046c680,
                            PTR_s__service_settings_crc_value_matc_0046c680);
      }
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(3,PTR_s_service_settings_0046c664,DAT_0046c660,
                     PTR_s_SVC_Settings_SyncHandler_0046c65c,0x128,
                     PTR_s_recv_slave_settings_sync__crc_va_0046c684);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0xc000000,PTR_s__service_settings_recv_slave_set_0046c688,
                            PTR_s__service_settings_recv_slave_set_0046c688);
      }
      settings_send_config_to_peer();
    }
  }
  else if ((*param_1 == '\x02') && (iVar1 = FUN_0045a568(), iVar1 == 1)) {
    SVC_Settings_UpdateLeftVersion(param_1 + 0x24);
  }
  else if ((*param_1 == '\x03') && (iVar1 = FUN_0045a568(), iVar1 == 2)) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(3,PTR_s_service_settings_0046c664,DAT_0046c660,
                   PTR_s_SVC_Settings_SyncHandler_0046c65c,0x12f,
                   PTR_s_recv_master_version_request__rep_0046c68c);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0xc000000,PTR_s__service_settings_recv_master_ve_0046c690,
                          PTR_s__service_settings_recv_master_ve_0046c690);
    }
    SVC_Settings_SyncVersionOnlySend();
  }
  return;
}

