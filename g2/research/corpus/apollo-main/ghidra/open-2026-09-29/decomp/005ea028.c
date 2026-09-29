
undefined4 terminal_machine_handler(uint param_1,undefined *param_2,uint param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  uint uVar3;
  
  if ((param_1 & 0xff) < 0xd) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      uVar2 = semantic_terminal_event_name(param_1 & 0xff);
      FUN_0043d574(3,PTR_s_terminal_pb_005ea1f4,PTR_s_D__01_workspace_s200_ap510b_iar__005ea1f0,
                   PTR_s_terminal_machine_handler_005ea208,0x347,
                   PTR_s_recv_terminal_event__d__s__005ea210,param_1 & 0xff,uVar2);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      uVar2 = semantic_terminal_event_name(param_1 & 0xff);
      compress_log_output(0xc800000,PTR_s__terminal_pb_recv_terminal_event_005ea214,
                          PTR_s__terminal_pb_recv_terminal_event_005ea214,param_1 & 0xff,uVar2);
    }
    if (*(code **)(PTR_DAT_005ea218 + (param_1 & 0xff) * 4) == (code *)0x0) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        uVar2 = semantic_terminal_event_name(param_1 & 0xff);
        FUN_0043d574(2,PTR_s_terminal_pb_005ea1f4,PTR_s_D__01_workspace_s200_ap510b_iar__005ea1f0,
                     PTR_s_terminal_machine_handler_005ea208,0x34b,
                     PTR_s_unsupported_terminal_event__d__s_005ea21c,param_1 & 0xff,uVar2);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        uVar2 = semantic_terminal_event_name(param_1 & 0xff);
        compress_log_output(0x8800000,PTR_s__terminal_pb_unsupported_termina_005ea220,
                            PTR_s__terminal_pb_unsupported_termina_005ea220,param_1 & 0xff,uVar2);
      }
      uVar2 = 0xffffffff;
    }
    else {
      uVar2 = (**(code **)(PTR_DAT_005ea218 + (param_1 & 0xff) * 4))(param_2,param_3);
    }
  }
  else {
    uVar3 = param_1;
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      param_3 = param_1 & 0xff;
      uVar3 = 0x343;
      param_2 = PTR_s_invalid_terminal_event__d_005ea204;
      FUN_0043d574(2,PTR_s_terminal_pb_005ea1f4,PTR_s_D__01_workspace_s200_ap510b_iar__005ea1f0,
                   PTR_s_terminal_machine_handler_005ea208,0x343,
                   PTR_s_invalid_terminal_event__d_005ea204,param_3,param_4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8400000,PTR_s__terminal_pb_invalid_terminal_ev_005ea20c,
                          PTR_s__terminal_pb_invalid_terminal_ev_005ea20c,param_1 & 0xff,uVar3,
                          param_2,param_3);
    }
    uVar2 = 0xffffffff;
  }
  return uVar2;
}

