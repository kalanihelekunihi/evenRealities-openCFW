
void FUN_00584ee4(int param_1,char *param_2,int param_3,int param_4)

{
  int iVar1;
  int iVar2;
  char *pcVar3;
  
  pcVar3 = param_2;
  iVar2 = param_3;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    pcVar3 = PTR_s_system_monitor_common_data_handl_005850e4;
    iVar2 = param_1;
    param_4 = param_3;
    FUN_0043d574(3,PTR_s_system_monitor_005850f0,PTR_s_D__01_workspace_s200_ap510b_iar__005850ec,
                 PTR_s_system_monitor_common_data_handl_005850e8,0x30,
                 PTR_s_system_monitor_common_data_handl_005850e4,param_1,param_3);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0xc800000,PTR_s__system_monitor_system_monitor_c_005850f4,
                        PTR_s__system_monitor_system_monitor_c_005850f4,param_1,param_3,pcVar3,iVar2
                        ,param_4);
  }
  if (param_1 != 5) {
    return;
  }
  if (*param_2 != 'U') {
    return;
  }
  if (param_2[1] != '\x04') {
    return;
  }
  if (param_2[2] != '\x12') {
    return;
  }
  if (param_2[3] != '4') {
    return;
  }
  if (param_2[4] != 'V') {
    return;
  }
  if (param_2[5] != 'x') {
    return;
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    FUN_0043d574(4,PTR_s_system_monitor_005850f0,PTR_s_D__01_workspace_s200_ap510b_iar__005850ec,
                 PTR_s_system_monitor_common_data_handl_005850e8,0x34,
                 PTR_s_system_monitor_common_data_handl_005850f8);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x10000000,PTR_s__system_monitor_system_monitor_c_005850fc,
                        PTR_s__system_monitor_system_monitor_c_005850fc);
  }
  iVar2 = FUN_00443484();
  if (iVar2 == 1) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(4,PTR_s_system_monitor_005850f0,PTR_s_D__01_workspace_s200_ap510b_iar__005850ec,
                   PTR_s_system_monitor_common_data_handl_005850e8,0x36,
                   PTR_s_system_monitor_common_data_handl_00585100);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10000000,PTR_s__system_monitor_system_monitor_c_00585104,
                          PTR_s__system_monitor_system_monitor_c_00585104);
    }
    iVar2 = FUN_0044349c();
    if (iVar2 == 1) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(4,PTR_s_system_monitor_005850f0,PTR_s_D__01_workspace_s200_ap510b_iar__005850ec
                     ,PTR_s_system_monitor_common_data_handl_005850e8,0x38,
                     PTR_s_system_monitor_common_data_handl_00585108);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x10000000,PTR_s__system_monitor_system_monitor_c_0058510c,
                            PTR_s__system_monitor_system_monitor_c_0058510c);
      }
      FUN_004443cc(0,0,0);
    }
    iVar2 = FUN_004434b4();
    if (iVar2 == 1) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(3,PTR_s_system_monitor_005850f0,PTR_s_D__01_workspace_s200_ap510b_iar__005850ec
                     ,PTR_s_system_monitor_common_data_handl_005850e8,0x3d,
                     PTR_s_system_monitor_common_data_handl_00585110);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0xc000000,PTR_s__system_monitor_system_monitor_c_00585114,
                            PTR_s__system_monitor_system_monitor_c_00585114);
      }
      FUN_004443cc(0,0,0);
    }
  }
  iVar2 = 0;
  do {
    iVar1 = FUN_00443484();
    if (iVar1 != 1) break;
    FUN_00454b4c(100);
    iVar2 = iVar2 + 1;
  } while (iVar2 < 0xb);
  iVar2 = FUN_0045a568();
  if (iVar2 == 1) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(3,PTR_s_system_monitor_005850f0,PTR_s_D__01_workspace_s200_ap510b_iar__005850ec,
                   PTR_s_system_monitor_common_data_handl_005850e8,0x4c,
                   PTR_s_system_monitor_common_data_handl_00585118);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0xc000000,PTR_s__system_monitor_system_monitor_c_0058511c,
                          PTR_s__system_monitor_system_monitor_c_0058511c);
    }
    FUN_00465b10();
  }
  FUN_0049c0b0();
  func_0x004973f4(0);
  onboarding_saved_color_state_reset();
  td_state_reset();
  RPC_SyncRingStatusWithPeer();
  return;
}

