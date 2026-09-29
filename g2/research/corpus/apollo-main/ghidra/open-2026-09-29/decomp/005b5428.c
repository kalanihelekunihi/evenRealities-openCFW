
undefined4 FUN_005b5428(char *param_1,undefined2 *param_2,undefined4 param_3,undefined4 param_4)

{
  char cVar1;
  int iVar2;
  
  if (param_2 == (undefined2 *)0x0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,PTR_s_conversate_005b56d4,PTR_s_D__01_workspace_s200_ap510b_iar__005b56d0,
                   PTR_s_conversate_action_transcribe_dat_005b56f0,0x176,
                   PTR_s_conversate_transcribe_data_is_NU_005b56ec,param_3,param_4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__conversate_conversate_transcrib_005b56f4);
    }
    return 0xffffffff;
  }
  if (*param_1 == '\x01') {
    cVar1 = FUN_005b16d0();
    if ((cVar1 != '\0') && (cVar1 != '\x06')) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(3,PTR_s_conversate_005b56d4,PTR_s_D__01_workspace_s200_ap510b_iar__005b56d0,
                     PTR_s_conversate_action_transcribe_dat_005b56f0,0x185,
                     PTR_s_transcribe_data_received__len__d_005b5708,*param_2,
                     *(undefined4 *)(param_2 + 0x202));
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0xc800000,PTR_s__conversate_transcribe_data_rece_005b570c,
                            PTR_s__conversate_transcribe_data_rece_005b570c,*param_2,
                            *(undefined4 *)(param_2 + 0x202));
      }
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(3,PTR_s_conversate_005b56d4,PTR_s_D__01_workspace_s200_ap510b_iar__005b56d0,
                     PTR_s_conversate_action_transcribe_dat_005b56f0,0x186,&DAT_005b5634,param_2 + 1
                    );
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0xc400000,PTR_s__conversate__s_005b5710,PTR_s__conversate__s_005b5710,
                            param_2 + 1);
      }
      FUN_005b41be(param_2);
      FUN_005b02e4(0xb,0);
      return 0;
    }
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(2,PTR_s_conversate_005b56d4,PTR_s_D__01_workspace_s200_ap510b_iar__005b56d0,
                   PTR_s_conversate_action_transcribe_dat_005b56f0,0x181,
                   PTR_s_conversate_ui_state_is_invalid__n_005b5700);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x8000000,PTR_s__conversate_conversate_ui_state_i_005b5704,
                          PTR_s__conversate_conversate_ui_state_i_005b5704);
    }
    return 0xffffffff;
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    FUN_0043d574(2,PTR_s_conversate_005b56d4,PTR_s_D__01_workspace_s200_ap510b_iar__005b56d0,
                 PTR_s_conversate_action_transcribe_dat_005b56f0,0x17b,
                 PTR_s_conversate_state_is_not_running__005b56f8);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x8000000,PTR_s__conversate_conversate_state_is_n_005b56fc,
                        PTR_s__conversate_conversate_state_is_n_005b56fc);
  }
  return 0xffffffff;
}

