
undefined8
terminal_handle_session_await_user
          (int param_1,undefined *param_2,undefined4 param_3,undefined4 param_4)

{
  char cVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  iVar2 = DAT_005e8c04;
  cVar1 = *(char *)(DAT_005e8c04 + 0x275);
  if (param_1 == 0) {
    iVar2 = FUN_0043d0ce();
    iVar4 = param_1;
    if (iVar2 << 0x1e < 0) {
      iVar4 = 0xaa;
      param_2 = PTR_s_drop_await_user_notification_wit_005e8e5c;
      FUN_0043d574(2,DAT_005e8c18,DAT_005e8c14,PTR_s_terminal_handle_session_await_us_005e8e60,0xaa,
                   PTR_s_drop_await_user_notification_wit_005e8e5c,param_3,param_4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x8000000,PTR_s__terminal_pb_drop_await_user_not_005e8e64,
                          PTR_s__terminal_pb_drop_await_user_not_005e8e64);
    }
  }
  else {
    iVar4 = param_1;
    iVar3 = td_counter_b_get();
    if ((param_1 == iVar3) && (cVar1 == '\a')) {
      terminal_data_dismiss_query_notification(param_1);
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        iVar4 = 0xaf;
        param_2 = PTR_s_drop_current_session_await_user_w_005e8e68;
        FUN_0043d574(3,DAT_005e8c18,DAT_005e8c14,PTR_s_terminal_handle_session_await_us_005e8e60,
                     0xaf,PTR_s_drop_current_session_await_user_w_005e8e68,param_1);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0xc400000,PTR_s__terminal_pb_drop_current_sessio_005e9030,
                            PTR_s__terminal_pb_drop_current_sessio_005e9030,param_1);
      }
    }
    else if (cVar1 == '\v') {
      terminal_data_dismiss_query_notification(param_1);
      iVar2 = terminal_refresh_session_list_if_visible();
      if (iVar2 == 0) {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          iVar4 = 0xb7;
          param_2 = PTR_s_dismiss_await_user_in_session_li_005e903c;
          FUN_0043d574(3,DAT_005e8c18,DAT_005e8c14,PTR_s_terminal_handle_session_await_us_005e8e60,
                       0xb7,PTR_s_dismiss_await_user_in_session_li_005e903c,param_1);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0xc400000,PTR_s__terminal_pb_dismiss_await_user_i_005e9040,
                              PTR_s__terminal_pb_dismiss_await_user_i_005e9040,param_1);
        }
      }
      else {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          iVar4 = 0xb5;
          param_2 = PTR_s_dismiss_await_user_in_session_li_005e9034;
          FUN_0043d574(3,DAT_005e8c18,DAT_005e8c14,PTR_s_terminal_handle_session_await_us_005e8e60,
                       0xb5,PTR_s_dismiss_await_user_in_session_li_005e9034,param_1);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0xc400000,PTR_s__terminal_pb_dismiss_await_user_i_005e9038,
                              PTR_s__terminal_pb_dismiss_await_user_i_005e9038,param_1);
        }
      }
    }
    else {
      iVar3 = td_record_in_use_get(param_1);
      if (iVar3 == 0) {
        if ((cVar1 == '\0') || (*DAT_005e904c == 0)) {
          *(int *)(iVar2 + 0x288) = param_1;
          *(undefined1 *)(iVar2 + 0x277) = 0;
          *(undefined1 *)(iVar2 + 0x27f) = 0;
          iVar2 = FUN_0045a568();
          if (iVar2 == 1) {
            FUN_0045a8ee(0x30,0,0,0);
          }
          iVar2 = FUN_0043d0ce();
          if (iVar2 << 0x1e < 0) {
            iVar4 = 0xc6;
            param_2 = PTR_s_await_user_received_while_displa_005e9050;
            FUN_0043d574(3,DAT_005e8c18,DAT_005e8c14,PTR_s_terminal_handle_session_await_us_005e8e60
                         ,0xc6,PTR_s_await_user_received_while_displa_005e9050,param_1);
          }
          iVar2 = FUN_0043d0ce();
          if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
            compress_log_output(0xc400000,PTR_s__terminal_pb_await_user_received_005e9054,
                                PTR_s__terminal_pb_await_user_received_005e9054,param_1);
          }
        }
        else {
          iVar2 = semantic_terminal_state_allows_runtime_event(cVar1);
          if (iVar2 == 0) {
            terminal_data_dismiss_query_notification(param_1);
            iVar2 = FUN_0043d0ce();
            if (iVar2 << 0x1e < 0) {
              iVar4 = 0xd0;
              param_2 = PTR_s_drop_await_user_notification_in_s_005e9058;
              FUN_0043d574(2,DAT_005e8c18,DAT_005e8c14,
                           PTR_s_terminal_handle_session_await_us_005e8e60,0xd0,
                           PTR_s_drop_await_user_notification_in_s_005e9058,cVar1,param_1);
            }
            iVar2 = FUN_0043d0ce();
            if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
              compress_log_output(0x8800000,DAT_005e9314,DAT_005e9314,cVar1);
              iVar4 = param_1;
            }
          }
          else {
            terminal_request_display(0x16,param_1);
          }
        }
      }
      else {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          iVar4 = 0xbc;
          param_2 = PTR_s_drop_dismissed_await_user_notifi_005e9044;
          FUN_0043d574(3,DAT_005e8c18,DAT_005e8c14,PTR_s_terminal_handle_session_await_us_005e8e60,
                       0xbc,PTR_s_drop_dismissed_await_user_notifi_005e9044,param_1);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0xc400000,PTR_s__terminal_pb_drop_dismissed_awai_005e9048,
                              PTR_s__terminal_pb_drop_dismissed_awai_005e9048,param_1);
        }
      }
    }
  }
  return CONCAT44(param_2,iVar4);
}

