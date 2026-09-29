
undefined4
terminal_action_session_switch_result
          (undefined1 *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  
  if (param_1 == (undefined1 *)0x0) {
    uVar1 = 0xffffffff;
  }
  else {
    terminal_request_display(0x1f,*param_1,param_3,param_4,param_1,param_2,param_3,param_4);
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(3,PTR_s_terminal_pb_005e9f68,PTR_s_D__01_workspace_s200_ap510b_iar__005e9f64,
                   PTR_s_terminal_action_session_switch_r_005ea1d4,0x2ef,
                   PTR_s_recv_terminal_session_switch_res_005ea1d0,*param_1);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0xc400000,PTR_s__terminal_pb_recv_terminal_sessi_005ea1d8,
                          PTR_s__terminal_pb_recv_terminal_sessi_005ea1d8,*param_1);
    }
    uVar1 = 0;
  }
  return uVar1;
}

