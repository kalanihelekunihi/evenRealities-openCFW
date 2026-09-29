
undefined8 FUN_0045e024(undefined4 param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  char cVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  iVar4 = param_2;
  if (*(int *)(param_2 + 8) == 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      iVar4 = 0x55f;
      FUN_0043d574(4,PTR_s_sync_module_framework_0045e8c0,
                   PTR_s_D__01_workspace_s200_ap510b_iar__0045e8bc,
                   PTR_s__MasterDisplayCmd_Listener_0045e8b8,0x55f,
                   PTR_s_msg_data_is_null_timeout_resourc_0045e8b4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10000000,PTR_s__sync_module_framework_msg_data_i_0045e8c4);
    }
    if (*(int *)(param_2 + 0x10) != 0) {
      iVar3 = *(int *)(param_2 + 0x10);
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        iVar4 = 0x562;
        FUN_0043d574(4,PTR_s_sync_module_framework_0045e8c0,
                     PTR_s_D__01_workspace_s200_ap510b_iar__0045e8bc,
                     PTR_s__MasterDisplayCmd_Listener_0045e8b8,0x562,
                     PTR_s_SyncEventType____d_0045e8c8,*(undefined2 *)(iVar3 + 4));
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x10400000,PTR_s__sync_module_framework_SyncEvent_0045e8cc,
                            PTR_s__sync_module_framework_SyncEvent_0045e8cc,
                            *(undefined2 *)(iVar3 + 4));
      }
      file_heap_free(*(undefined4 *)(iVar3 + 8));
      file_heap_free(iVar3);
    }
  }
  else {
    cVar1 = **(char **)(param_2 + 8);
    if (cVar1 == '\x02') {
      if (*(int *)(param_2 + 0x10) == 0) {
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          param_2 = 0x56d;
          FUN_0043d574(2,PTR_s_sync_module_framework_0045e8c0,
                       PTR_s_D__01_workspace_s200_ap510b_iar__0045e8bc,
                       PTR_s__MasterDisplayCmd_Listener_0045e8b8,0x56d,
                       PTR_s_userdata_is_null_0045eb78);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar4 = param_2, iVar2 << 0x1d < 0)) {
          compress_log_output(0x8000000,PTR_s__sync_module_framework_userdata_i_0045eb7c,
                              PTR_s__sync_module_framework_userdata_i_0045eb7c);
          iVar4 = param_2;
        }
      }
      else {
        iVar3 = *(int *)(param_2 + 0x10);
        iVar2 = *(int *)(iVar3 + 8);
        FUN_004441ec(*(undefined2 *)(iVar2 + 2),iVar2 + 8,*(undefined2 *)(iVar2 + 6),param_4,param_2
                     ,param_3,param_4);
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          iVar4 = 0x574;
          FUN_0043d574(4,PTR_s_sync_module_framework_0045e8c0,
                       PTR_s_D__01_workspace_s200_ap510b_iar__0045e8bc,
                       PTR_s__MasterDisplayCmd_Listener_0045e8b8,0x574,
                       PTR_s_received_display_start_response_0045eb80);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0x10000000,PTR_s__sync_module_framework_received_d_0045eb84,
                              PTR_s__sync_module_framework_received_d_0045eb84);
        }
        if (*(int *)(param_2 + 0x14) != 0) {
          iVar4 = 0;
          iVar2 = FUN_00491184(PTR_FUN_0045ade8_1_0045eb88,0,*(undefined4 *)(param_2 + 0x14),0);
          if (iVar2 != 0) {
            iVar2 = FUN_0043d0ce();
            if (iVar2 << 0x1e < 0) {
              iVar4 = 0x577;
              FUN_0043d574(1,PTR_s_sync_module_framework_0045e8c0,
                           PTR_s_D__01_workspace_s200_ap510b_iar__0045e8bc,
                           PTR_s__MasterDisplayCmd_Listener_0045e8b8,0x577,
                           PTR_s_submit_work_failed__0045eb8c);
            }
            iVar2 = FUN_0043d0ce();
            if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
              compress_log_output(0x4000000,PTR_s__sync_module_framework_submit_wo_0045e654,
                                  PTR_s__sync_module_framework_submit_wo_0045e654);
            }
            (**(code **)(param_2 + 0x14))(0);
          }
        }
        file_heap_free(*(undefined4 *)(iVar3 + 8));
        file_heap_free(iVar3);
      }
    }
    else if (cVar1 == '\x04') {
      if (*(int *)(param_2 + 0x10) == 0) {
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          param_2 = 0x582;
          FUN_0043d574(2,PTR_s_sync_module_framework_0045e8c0,
                       PTR_s_D__01_workspace_s200_ap510b_iar__0045e8bc,
                       PTR_s__MasterDisplayCmd_Listener_0045e8b8,0x582,
                       PTR_s_userdata_is_null_0045eb78);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar4 = param_2, iVar2 << 0x1d < 0)) {
          compress_log_output(0x8000000,PTR_s__sync_module_framework_userdata_i_0045eb7c,
                              PTR_s__sync_module_framework_userdata_i_0045eb7c);
          iVar4 = param_2;
        }
      }
      else {
        iVar3 = *(int *)(param_2 + 0x10);
        iVar2 = *(int *)(iVar3 + 8);
        FUN_004442d0(*(undefined2 *)(iVar2 + 2),iVar2 + 8,*(undefined2 *)(iVar2 + 6));
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          iVar4 = 0x589;
          FUN_0043d574(4,PTR_s_sync_module_framework_0045e8c0,
                       PTR_s_D__01_workspace_s200_ap510b_iar__0045e8bc,
                       PTR_s__MasterDisplayCmd_Listener_0045e8b8,0x589,
                       PTR_s_received_display_refresh_respons_0045eb90);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0x10000000,PTR_s__sync_module_framework_received_d_0045eb94,
                              PTR_s__sync_module_framework_received_d_0045eb94);
        }
        if (*(int *)(param_2 + 0x14) != 0) {
          iVar4 = 0;
          iVar2 = FUN_00491184(PTR_FUN_0045ade8_1_0045eb88,0,*(undefined4 *)(param_2 + 0x14),0);
          if (iVar2 != 0) {
            iVar2 = FUN_0043d0ce();
            if (iVar2 << 0x1e < 0) {
              iVar4 = 0x58c;
              FUN_0043d574(1,PTR_s_sync_module_framework_0045e8c0,
                           PTR_s_D__01_workspace_s200_ap510b_iar__0045e8bc,
                           PTR_s__MasterDisplayCmd_Listener_0045e8b8,0x58c,
                           PTR_s_submit_work_failed__0045eb8c);
            }
            iVar2 = FUN_0043d0ce();
            if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
              compress_log_output(0x4000000,PTR_s__sync_module_framework_submit_wo_0045e654,
                                  PTR_s__sync_module_framework_submit_wo_0045e654);
            }
            (**(code **)(param_2 + 0x14))(0);
          }
        }
        file_heap_free(*(undefined4 *)(iVar3 + 8));
        file_heap_free(iVar3);
      }
    }
    else if (cVar1 == '\x06') {
      if (*(int *)(param_2 + 0x10) == 0) {
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          param_2 = 0x597;
          FUN_0043d574(2,PTR_s_sync_module_framework_0045e8c0,
                       PTR_s_D__01_workspace_s200_ap510b_iar__0045e8bc,
                       PTR_s__MasterDisplayCmd_Listener_0045e8b8,0x597,
                       PTR_s_userdata_is_null_0045eb78);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar4 = param_2, iVar2 << 0x1d < 0)) {
          compress_log_output(0x8000000,PTR_s__sync_module_framework_userdata_i_0045eb7c,
                              PTR_s__sync_module_framework_userdata_i_0045eb7c);
          iVar4 = param_2;
        }
      }
      else {
        iVar3 = *(int *)(param_2 + 0x10);
        iVar2 = *(int *)(iVar3 + 8);
        FUN_004443cc(*(undefined2 *)(iVar2 + 2),iVar2 + 8,*(undefined2 *)(iVar2 + 6));
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          iVar4 = 0x59e;
          FUN_0043d574(4,PTR_s_sync_module_framework_0045e8c0,
                       PTR_s_D__01_workspace_s200_ap510b_iar__0045e8bc,
                       PTR_s__MasterDisplayCmd_Listener_0045e8b8,0x59e,
                       PTR_s_received_display_stop_response_0045eb98);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0x10000000,PTR_s__sync_module_framework_received_d_0045eb9c,
                              PTR_s__sync_module_framework_received_d_0045eb9c);
        }
        if (*(int *)(param_2 + 0x14) != 0) {
          iVar4 = 0;
          iVar2 = FUN_00491184(PTR_FUN_0045ade8_1_0045eb88,0,*(undefined4 *)(param_2 + 0x14),0);
          if (iVar2 != 0) {
            iVar2 = FUN_0043d0ce();
            if (iVar2 << 0x1e < 0) {
              iVar4 = 0x5a1;
              FUN_0043d574(1,PTR_s_sync_module_framework_0045e8c0,
                           PTR_s_D__01_workspace_s200_ap510b_iar__0045e8bc,
                           PTR_s__MasterDisplayCmd_Listener_0045e8b8,0x5a1,
                           PTR_s_submit_work_failed__0045eb8c);
            }
            iVar2 = FUN_0043d0ce();
            if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
              compress_log_output(0x4000000,PTR_s__sync_module_framework_submit_wo_0045e654,
                                  PTR_s__sync_module_framework_submit_wo_0045e654);
            }
            (**(code **)(param_2 + 0x14))(0);
          }
        }
        file_heap_free(*(undefined4 *)(iVar3 + 8));
        file_heap_free(iVar3);
      }
    }
    else if (cVar1 == '\x11') {
      if (*(int *)(param_2 + 0x10) == 0) {
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          param_2 = 0x5ac;
          FUN_0043d574(2,PTR_s_sync_module_framework_0045e8c0,
                       PTR_s_D__01_workspace_s200_ap510b_iar__0045e8bc,
                       PTR_s__MasterDisplayCmd_Listener_0045e8b8,0x5ac,
                       PTR_s_userdata_is_null_0045eb78);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar4 = param_2, iVar2 << 0x1d < 0)) {
          compress_log_output(0x8000000,PTR_s__sync_module_framework_userdata_i_0045eb7c,
                              PTR_s__sync_module_framework_userdata_i_0045eb7c);
          iVar4 = param_2;
        }
      }
      else {
        iVar3 = *(int *)(param_2 + 0x10);
        FUN_004444b8(*(int *)(iVar3 + 8) + 8,*(undefined2 *)(*(int *)(iVar3 + 8) + 6));
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          iVar4 = 0x5b3;
          FUN_0043d574(4,PTR_s_sync_module_framework_0045e8c0,
                       PTR_s_D__01_workspace_s200_ap510b_iar__0045e8bc,
                       PTR_s__MasterDisplayCmd_Listener_0045e8b8,0x5b3,
                       PTR_s_received_display_all_page_exit_r_0045eba0);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0x10000000,PTR_s__sync_module_framework_received_d_0045eba4,
                              PTR_s__sync_module_framework_received_d_0045eba4);
        }
        if (*(int *)(param_2 + 0x14) != 0) {
          iVar4 = 0;
          iVar2 = FUN_00491184(PTR_FUN_0045ade8_1_0045eb88,0,*(undefined4 *)(param_2 + 0x14),0);
          if (iVar2 != 0) {
            iVar2 = FUN_0043d0ce();
            if (iVar2 << 0x1e < 0) {
              iVar4 = 0x5b6;
              FUN_0043d574(1,PTR_s_sync_module_framework_0045e8c0,
                           PTR_s_D__01_workspace_s200_ap510b_iar__0045e8bc,
                           PTR_s__MasterDisplayCmd_Listener_0045e8b8,0x5b6,
                           PTR_s_submit_work_failed__0045eb8c);
            }
            iVar2 = FUN_0043d0ce();
            if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
              compress_log_output(0x4000000,PTR_s__sync_module_framework_submit_wo_0045e654,
                                  PTR_s__sync_module_framework_submit_wo_0045e654);
            }
            (**(code **)(param_2 + 0x14))(0);
          }
        }
        file_heap_free(*(undefined4 *)(iVar3 + 8));
        file_heap_free(iVar3);
      }
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        iVar4 = 0x5c0;
        FUN_0043d574(2,PTR_s_sync_module_framework_0045e8c0,
                     PTR_s_D__01_workspace_s200_ap510b_iar__0045e8bc,
                     PTR_s__MasterDisplayCmd_Listener_0045e8b8,0x5c0,
                     PTR_s_unknown_command_cmd____d_0045eba8,**(undefined1 **)(param_2 + 8));
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x8400000,PTR_s__sync_module_framework_unknown_c_0045ebac,
                            PTR_s__sync_module_framework_unknown_c_0045ebac,
                            **(undefined1 **)(param_2 + 8));
      }
      if (*(int *)(param_2 + 0x10) != 0) {
        iVar2 = *(int *)(param_2 + 0x10);
        file_heap_free(*(undefined4 *)(iVar2 + 8));
        file_heap_free(iVar2);
      }
    }
  }
  return CONCAT44(iVar4,3);
}

