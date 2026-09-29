
undefined4
terminal_action_error_msg(byte *param_1,undefined *param_2,uint param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  byte *pbVar3;
  
  if (param_1 == (byte *)0x0) {
    uVar1 = 0xffffffff;
  }
  else {
    pbVar3 = param_1;
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_3 = (uint)*param_1;
      pbVar3 = (byte *)0x295;
      param_2 = PTR_s_recv_terminal_error_msg__err_cod_005ea1a4;
      FUN_0043d574(1,PTR_s_terminal_pb_005e9f68,PTR_s_D__01_workspace_s200_ap510b_iar__005e9f64,
                   PTR_s_terminal_action_error_msg_005ea1a8,0x295,
                   PTR_s_recv_terminal_error_msg__err_cod_005ea1a4,param_3,param_4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4400000,PTR_s__terminal_pb_recv_terminal_error_005ea1ac,
                          PTR_s__terminal_pb_recv_terminal_error_005ea1ac,*param_1,pbVar3,param_2,
                          param_3);
    }
    if (*param_1 == 2) {
      td_notify_state_clear();
      terminal_request_display(0xc,0);
    }
    uVar1 = 0;
  }
  return uVar1;
}

