
undefined4
terminal_action_new_session_result
          (char *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined1 uVar1;
  undefined4 uVar2;
  int iVar3;
  
  if (param_1 == (char *)0x0) {
    uVar2 = 0xffffffff;
  }
  else {
    if (*param_1 == '\0') {
      semantic_terminal_reset_output_tracking();
      td_record_flags_clear_all();
      td_ring_reset_wrapper();
      td_notify_state_clear();
      td_session_struct_clear();
      td_flag_set_with_reset(1);
    }
    else {
      td_flag_set_with_reset(0);
    }
    if (*param_1 == '\0') {
      uVar1 = 0x20;
    }
    else {
      uVar1 = 0x21;
    }
    terminal_request_display(uVar1,0);
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(3,PTR_s_terminal_pb_005e9f68,PTR_s_D__01_workspace_s200_ap510b_iar__005e9f64,
                   PTR_s_terminal_action_new_session_resu_005ea1e0,0x30a,
                   PTR_s_recv_terminal_new_session_result_005ea1dc,*param_1,param_4);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0xc400000,PTR_s__terminal_pb_recv_terminal_new_s_005ea1e4,
                          PTR_s__terminal_pb_recv_terminal_new_s_005ea1e4,*param_1);
    }
    uVar2 = 0;
  }
  return uVar2;
}

