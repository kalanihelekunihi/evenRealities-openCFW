
undefined4
terminal_action_host_status(char *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  char cVar1;
  byte bVar2;
  byte bVar3;
  undefined1 uVar4;
  int iVar5;
  undefined4 uVar6;
  int iVar7;
  
  if (param_1 == (char *)0x0) {
    return 0xffffffff;
  }
  iVar5 = FUN_0043d0ce();
  if (iVar5 << 0x1e < 0) {
    uVar6 = semantic_terminal_host_status_name(*param_1);
    FUN_0043d574(3,PTR_s_terminal_pb_005e9384,PTR_s_D__01_workspace_s200_ap510b_iar__005e9380,
                 PTR_s_terminal_action_host_status_005e937c,0x15f,
                 PTR_s_recv_terminal_host_status__host__005e9378,*param_1,uVar6,param_4);
  }
  iVar5 = FUN_0043d0ce();
  if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
    uVar6 = semantic_terminal_host_status_name(*param_1);
    compress_log_output(0xc800000,PTR_s__terminal_pb_recv_terminal_host_s_005e9388,
                        PTR_s__terminal_pb_recv_terminal_host_s_005e9388,*param_1,uVar6);
  }
  iVar5 = td_state_ptr_alias2();
  cVar1 = *(char *)(iVar5 + 0xa1d8);
  if (cVar1 != *param_1) {
    *(char *)(iVar5 + 0xa1d8) = *param_1;
    if ((cVar1 == '\x01') || (cVar1 == '\0')) {
      bVar2 = 1;
    }
    else {
      bVar2 = 0;
    }
    if ((*param_1 == '\x01') || (*param_1 == '\0')) {
      bVar3 = 1;
    }
    else {
      bVar3 = 0;
    }
    if ((bool)(bVar3 & (bVar2 ^ 1))) {
      td_notify_state_clear();
      td_session_struct_clear();
    }
    if (*param_1 == '\x02') {
      iVar5 = td_has_active_session();
      if (iVar5 == 0) {
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          FUN_0043d574(3,PTR_s_terminal_pb_005e9384,PTR_s_D__01_workspace_s200_ap510b_iar__005e9380,
                       PTR_s_terminal_action_host_status_005e937c,0x181,
                       PTR_s_host_streaming_without_host_id__k_005e98ec);
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          compress_log_output(0xc000000,PTR_s__terminal_pb_host_streaming_with_005e9aac,
                              PTR_s__terminal_pb_host_streaming_with_005e9aac);
        }
      }
      else {
        iVar5 = td_counter_b_get();
        iVar7 = semantic_terminal_state_is_processing(*(undefined1 *)(DAT_005e938c + 0x275));
        if (iVar7 != 0) {
          if (iVar5 == 0) {
            uVar6 = FUN_005ecafa();
            terminal_request_display(0x1b,uVar6);
            iVar5 = FUN_0043d0ce();
            if (iVar5 << 0x1e < 0) {
              FUN_0043d574(3,PTR_s_terminal_pb_005e9384,
                           PTR_s_D__01_workspace_s200_ap510b_iar__005e9380,
                           PTR_s_terminal_action_host_status_005e937c,0x17e,
                           PTR_s_host_streaming_with_host_id__sho_005e98e4);
            }
            iVar5 = FUN_0043d0ce();
            if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
              compress_log_output(0xc000000,PTR_s__terminal_pb_host_streaming_with_005e98e8,
                                  PTR_s__terminal_pb_host_streaming_with_005e98e8);
            }
          }
          else {
            terminal_apply_session_id_changed(iVar5,1);
            iVar7 = FUN_0043d0ce();
            if (iVar7 << 0x1e < 0) {
              FUN_0043d574(3,PTR_s_terminal_pb_005e9384,
                           PTR_s_D__01_workspace_s200_ap510b_iar__005e9380,
                           PTR_s_terminal_action_host_status_005e937c,0x17a,
                           PTR_s_host_streaming_with_current_sess_005e98dc,iVar5);
            }
            iVar7 = FUN_0043d0ce();
            if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
              compress_log_output(0xc400000,PTR_s__terminal_pb_host_streaming_with_005e98e0,
                                  PTR_s__terminal_pb_host_streaming_with_005e98e0,iVar5);
            }
          }
        }
      }
    }
    else {
      uVar4 = UX_GetSystemBLEStatus();
      terminal_request_runtime_event_if_allowed(uVar4);
    }
  }
  return 0;
}

