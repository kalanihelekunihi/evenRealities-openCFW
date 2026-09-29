
undefined4 terminal_action_query(undefined4 *param_1)

{
  int *piVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  
  piVar1 = DAT_005ea174;
  if (param_1 == (undefined4 *)0x0) {
    uVar2 = 0xffffffff;
  }
  else if ((*DAT_005ea174 == 0) || (*(char *)(DAT_005ea01c + 0x275) != '\a')) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(2,PTR_s_terminal_pb_005e9f68,PTR_s_D__01_workspace_s200_ap510b_iar__005e9f64,
                   PTR_s_terminal_action_query_005ea17c,0x274,
                   PTR_s_ignore_terminal_query_outside_ma_005ea178,*piVar1 != 0,
                   *(undefined1 *)(DAT_005ea01c + 0x275),param_1[0x212]);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x8c00000,PTR_s__terminal_pb_ignore_terminal_que_005ea180,
                          PTR_s__terminal_pb_ignore_terminal_que_005ea180,*piVar1 != 0,
                          *(undefined1 *)(DAT_005ea01c + 0x275),param_1[0x212]);
    }
    uVar2 = 0;
  }
  else {
    iVar3 = terminal_message_session_matches(param_1[0x212],PTR_s_query_005ea184);
    if (iVar3 == 0) {
      uVar2 = 0;
    }
    else {
      td_session_struct_copy_out(param_1);
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(3,PTR_s_terminal_pb_005e9f68,PTR_s_D__01_workspace_s200_ap510b_iar__005e9f64,
                     PTR_s_terminal_action_query_005ea17c,0x27c,
                     PTR_s_recv_terminal_query_id__d__quest_005ea188,*param_1,(int)param_1 + 6);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0xc800000,PTR_s__terminal_pb_recv_terminal_query_005ea18c,
                            PTR_s__terminal_pb_recv_terminal_query_005ea18c,*param_1,
                            (int)param_1 + 6);
      }
      for (iVar3 = 0; iVar3 < (int)(uint)*(ushort *)((int)param_1 + 0x406); iVar3 = iVar3 + 1) {
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          FUN_0043d574(3,PTR_s_terminal_pb_005e9f68,PTR_s_D__01_workspace_s200_ap510b_iar__005e9f64,
                       PTR_s_terminal_action_query_005ea17c,0x27e,
                       PTR_s_option__d_id__u____s_005ea190,iVar3,param_1[iVar3 * 0x22 + 0x102],
                       (int)param_1 + iVar3 * 0x88 + 0x40e);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0xcc00000,PTR_s__terminal_pb_option__d_id__u_____005ea194,
                              PTR_s__terminal_pb_option__d_id__u_____005ea194,iVar3,
                              param_1[iVar3 * 0x22 + 0x102],(int)param_1 + iVar3 * 0x88 + 0x40e);
        }
      }
      terminal_request_display(0x15,0);
      uVar2 = 0;
    }
  }
  return uVar2;
}

