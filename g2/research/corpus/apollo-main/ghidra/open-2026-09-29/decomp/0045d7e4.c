
undefined8 FUN_0045d7e4(undefined4 param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = param_2;
  if (*(int *)(param_2 + 8) == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      iVar3 = 0x4bb;
      FUN_0043d574(4,PTR_s_sync_module_framework_0045e014,
                   PTR_s_D__01_workspace_s200_ap510b_iar__0045e010,
                   PTR_s__UserDataCmd_Listener_0045e00c,0x4bb,
                   PTR_s_msg_data_is_null_timeout_resourc_0045df20);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10000000,PTR_s__sync_module_framework_msg_data_i_0045dfd8);
    }
    if (*(int *)(param_2 + 0x10) != 0) {
      iVar2 = *(int *)(param_2 + 0x10);
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        iVar3 = 0x4be;
        FUN_0043d574(4,PTR_s_sync_module_framework_0045e014,
                     PTR_s_D__01_workspace_s200_ap510b_iar__0045e010,
                     PTR_s__UserDataCmd_Listener_0045e00c,0x4be,PTR_s_SyncEventType____d_0045dfdc,
                     *(undefined2 *)(iVar2 + 4));
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x10400000,PTR_s__sync_module_framework_SyncEvent_0045dfe0,
                            PTR_s__sync_module_framework_SyncEvent_0045dfe0,
                            *(undefined2 *)(iVar2 + 4));
      }
      file_heap_free(*(undefined4 *)(iVar2 + 8));
      file_heap_free(iVar2);
    }
  }
  else if (**(char **)(param_2 + 8) == '\n') {
    if (*(int *)(param_2 + 0x10) == 0) {
      iVar1 = FUN_0043d0ce();
      iVar3 = param_2;
      if (iVar1 << 0x1e < 0) {
        iVar3 = 0x4c9;
        FUN_0043d574(2,PTR_s_sync_module_framework_0045e014,
                     PTR_s_D__01_workspace_s200_ap510b_iar__0045e010,
                     PTR_s__UserDataCmd_Listener_0045e00c,0x4c9,PTR_s_userdata_is_null_0045dfe4);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x8000000,PTR_s__sync_module_framework_userdata_i_0045dfe8,
                            PTR_s__sync_module_framework_userdata_i_0045dfe8);
      }
    }
    else {
      iVar2 = *(int *)(param_2 + 0x10);
      iVar1 = *(int *)(iVar2 + 8);
      FUN_0045a72c(*(undefined2 *)(iVar1 + 2),iVar1 + 8,*(undefined2 *)(iVar1 + 6),
                   *(undefined2 *)(iVar1 + 4),param_2,param_3,param_4);
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        iVar3 = 0x4d0;
        FUN_0043d574(4,PTR_s_sync_module_framework_0045e014,
                     PTR_s_D__01_workspace_s200_ap510b_iar__0045e010,
                     PTR_s__UserDataCmd_Listener_0045e00c,0x4d0,
                     PTR_s_received_user_data_response_0045e018);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x10000000,PTR_s__sync_module_framework_received_u_0045e01c,
                            PTR_s__sync_module_framework_received_u_0045e01c);
      }
      if (*(int *)(param_2 + 0x14) != 0) {
        iVar3 = 0;
        iVar1 = FUN_00491184(PTR_FUN_0045ade8_1_0045dff4,0,*(undefined4 *)(param_2 + 0x14),0);
        if (iVar1 != 0) {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            iVar3 = 0x4d3;
            FUN_0043d574(1,PTR_s_sync_module_framework_0045e014,
                         PTR_s_D__01_workspace_s200_ap510b_iar__0045e010,
                         PTR_s__UserDataCmd_Listener_0045e00c,0x4d3,
                         PTR_s_submit_work_failed__0045dff8);
          }
          iVar1 = FUN_0043d0ce();
          if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
            compress_log_output(0x4000000,PTR_s__sync_module_framework_submit_wo_0045e654,
                                PTR_s__sync_module_framework_submit_wo_0045e654);
          }
          (**(code **)(param_2 + 0x14))(0);
        }
      }
      file_heap_free(*(undefined4 *)(iVar2 + 8));
      file_heap_free(iVar2);
    }
  }
  return CONCAT44(iVar3,3);
}

