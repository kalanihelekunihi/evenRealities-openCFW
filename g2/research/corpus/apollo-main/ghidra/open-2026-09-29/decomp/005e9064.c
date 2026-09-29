
undefined4
terminal_action_session_status
          (char *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  char cVar1;
  undefined4 uVar2;
  int iVar3;
  
  if (param_1 == (char *)0x0) {
    uVar2 = 0xffffffff;
  }
  else {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      uVar2 = semantic_terminal_session_status_name(*param_1);
      FUN_0043d574(3,PTR_s_terminal_pb_005e9384,PTR_s_D__01_workspace_s200_ap510b_iar__005e9380,
                   PTR_s_terminal_action_session_status_005e9b7c,0x1b4,
                   PTR_s_recv_terminal_session_status_id__005e9b78,*(undefined4 *)(param_1 + 4),
                   *param_1,uVar2,param_4);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      uVar2 = semantic_terminal_session_status_name(*param_1);
      compress_log_output(0xcc00000,PTR_s__terminal_pb_recv_terminal_sessi_005e9b80,
                          PTR_s__terminal_pb_recv_terminal_sessi_005e9b80,
                          *(undefined4 *)(param_1 + 4),*param_1,uVar2);
    }
    if (*param_1 == '\x05') {
      iVar3 = terminal_message_session_matches
                        (*(undefined4 *)(param_1 + 4),PTR_s_session_sync_end_005e9c58);
      if (iVar3 != 0) {
        *(undefined4 *)(DAT_005e938c + 0x29c) = 0;
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(3,PTR_s_terminal_pb_005e9384,PTR_s_D__01_workspace_s200_ap510b_iar__005e9380,
                       PTR_s_terminal_action_session_status_005e9b7c,0x1ba,
                       PTR_s_session_history_sync_end__unbloc_005e9c5c,*(undefined4 *)(param_1 + 4))
          ;
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0xc400000,PTR_s__terminal_pb_session_history_syn_005e9c60,
                              PTR_s__terminal_pb_session_history_syn_005e9c60,
                              *(undefined4 *)(param_1 + 4));
        }
      }
      uVar2 = 0;
    }
    else {
      td_record_status_set(*(undefined4 *)(param_1 + 4),*param_1);
      if (*param_1 == '\x02') {
        terminal_handle_session_await_user(*(undefined4 *)(param_1 + 4));
        uVar2 = 0;
      }
      else {
        if (((*param_1 == '\x01') && (*(char *)(DAT_005e938c + 0x275) == '\n')) &&
           (*(int *)(DAT_005e938c + 0x288) == *(int *)(param_1 + 4))) {
          terminal_request_display(0x18,1);
          iVar3 = FUN_0043d0ce();
          if (iVar3 << 0x1e < 0) {
            FUN_0043d574(3,PTR_s_terminal_pb_005e9384,
                         PTR_s_D__01_workspace_s200_ap510b_iar__005e9380,
                         PTR_s_terminal_action_session_status_005e9b7c,0x1c9,
                         PTR_s_dismiss_query_notification_by_th_005e9c64,
                         *(undefined4 *)(param_1 + 4));
          }
          iVar3 = FUN_0043d0ce();
          if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
            compress_log_output(0xc400000,PTR_s__terminal_pb_dismiss_query_notif_005e9c68,
                                PTR_s__terminal_pb_dismiss_query_notif_005e9c68,
                                *(undefined4 *)(param_1 + 4));
          }
        }
        iVar3 = td_counter_b_get();
        if (*(int *)(param_1 + 4) == iVar3) {
          cVar1 = *param_1;
          if (cVar1 == '\x01') {
            if (*(char *)(DAT_005e938c + 0x294) != '\0') {
              iVar3 = FUN_0043d0ce();
              if (iVar3 << 0x1e < 0) {
                uVar2 = semantic_terminal_session_status_name(*param_1);
                FUN_0043d574(4,PTR_s_terminal_pb_005e9384,
                             PTR_s_D__01_workspace_s200_ap510b_iar__005e9380,
                             PTR_s_terminal_action_session_status_005e9b7c,0x1ec,
                             PTR_s_skip_session_status_ui_refresh_d_005e9c74,*param_1,uVar2);
              }
              iVar3 = FUN_0043d0ce();
              if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
                uVar2 = semantic_terminal_session_status_name(*param_1);
                compress_log_output(0x10800000,PTR_s__terminal_pb_skip_session_status_005e9f58,
                                    PTR_s__terminal_pb_skip_session_status_005e9f58,*param_1,uVar2);
              }
              return 0;
            }
          }
          else {
            if (cVar1 == '\x03') {
              semantic_terminal_reset_output_tracking();
              td_record_timer_clear(*(undefined4 *)(param_1 + 4));
              td_notify_state_clear();
              td_session_struct_clear();
              iVar3 = terminal_refresh_session_list_if_visible();
              if (iVar3 == 0) {
                terminal_request_display(0x10,0);
              }
              return 0;
            }
            if (cVar1 == '\x04') {
              semantic_terminal_reset_output_tracking();
              td_record_timer_clear(*(undefined4 *)(param_1 + 4));
              td_ring_reset_wrapper();
              td_notify_state_clear();
              td_session_struct_clear();
              iVar3 = terminal_refresh_session_list_if_visible();
              if (iVar3 == 0) {
                terminal_request_display(0x11,0);
              }
              return 0;
            }
          }
          iVar3 = terminal_refresh_session_list_if_visible();
          if (iVar3 == 0) {
            terminal_request_display(0xf,*(undefined4 *)(param_1 + 4));
            uVar2 = 0;
          }
          else {
            uVar2 = 0;
          }
        }
        else {
          terminal_refresh_session_list_if_visible();
          iVar3 = FUN_0043d0ce();
          if (iVar3 << 0x1e < 0) {
            uVar2 = semantic_terminal_session_status_name(*param_1);
            FUN_0043d574(2,PTR_s_terminal_pb_005e9384,
                         PTR_s_D__01_workspace_s200_ap510b_iar__005e9380,
                         PTR_s_terminal_action_session_status_005e9b7c,0x1d0,
                         PTR_s_session_status_cached_for_inacti_005e9c6c,
                         *(undefined4 *)(param_1 + 4),*param_1,uVar2);
          }
          iVar3 = FUN_0043d0ce();
          if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
            uVar2 = semantic_terminal_session_status_name(*param_1);
            compress_log_output(0x8c00000,PTR_s__terminal_pb_session_status_cach_005e9c70,
                                PTR_s__terminal_pb_session_status_cach_005e9c70,
                                *(undefined4 *)(param_1 + 4),*param_1,uVar2);
          }
          uVar2 = 0;
        }
      }
    }
  }
  return uVar2;
}

