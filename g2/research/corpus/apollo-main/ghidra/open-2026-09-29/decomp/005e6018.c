
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int FUN_005e6018(byte param_1,int param_2)

{
  char cVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = _DAT_005e68d8;
  iVar2 = td_counter_b_get();
  if ((param_2 == 0) || (param_2 != iVar2)) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(2,PTR_s_terminal_ui_005e6b90,PTR_s_D__01_workspace_s200_ap510b_iar__005e6b8c,
                   PTR_s_terminal_ui_action_session_statu_005e6b10,0x532,
                   PTR_s_ignore_stale_session_status_ui_u_005e6b0c,param_2,iVar2,param_1);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x8c00000,PTR_s__terminal_ui_ignore_stale_sessio_005e6b14,
                          PTR_s__terminal_ui_ignore_stale_sessio_005e6b14,param_2,iVar2,param_1);
    }
    iVar3 = param_1 + 1;
  }
  else {
    cVar1 = td_record_status_get(param_2);
    if (param_1 == 9) {
      if (cVar1 == '\x01') {
        FUN_005ebbc6();
        td_session_struct_clear();
        if ((((*(int *)(iVar3 + 0x1cc) != 0) && (*(int *)(iVar3 + 0x1d0) != 0)) &&
            (*(int *)(iVar3 + 0x1d4) != 0)) && (*(int *)(iVar3 + 0x1dc) != 0)) {
          FUN_0043dfa4(*(undefined4 *)(iVar3 + 0x1cc),1);
          FUN_005ea30c();
          FUN_005e482a(*(undefined4 *)(iVar3 + 0x1d0),DAT_005e625c,6,100);
          FUN_0049942e(*(undefined4 *)(iVar3 + 0x1d4),DAT_005e6260);
          FUN_0049942e(*(undefined4 *)(iVar3 + 0x1dc),PTR_s__Tap___hold_to_stop_response__005e6538);
          FUN_005e4902();
        }
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(3,PTR_s_terminal_ui_005e6b90,PTR_s_D__01_workspace_s200_ap510b_iar__005e6b8c,
                       PTR_s_terminal_ui_action_session_statu_005e6b10,0x544,
                       PTR_s_session_status___d_005e6b94,1);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0xc400000,_DAT_005e6e28,_DAT_005e6e28,1);
        }
        iVar3 = 8;
      }
      else {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(2,PTR_s_terminal_ui_005e6b90,PTR_s_D__01_workspace_s200_ap510b_iar__005e6b8c,
                       PTR_s_terminal_ui_action_session_statu_005e6b10,0x547,
                       PTR_s_ignore_session_status_in_query_p_005e6b98,cVar1);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x8400000,PTR_s__terminal_ui_ignore_session_stat_005e6b9c,
                              PTR_s__terminal_ui_ignore_session_stat_005e6b9c,cVar1);
        }
        iVar3 = 10;
      }
    }
    else {
      if ((((*(int *)(iVar3 + 0x1cc) != 0) && (*(int *)(iVar3 + 0x1d0) != 0)) &&
          (*(int *)(iVar3 + 0x1d4) != 0)) && (*(int *)(iVar3 + 0x1dc) != 0)) {
        FUN_0043dfa4(*(undefined4 *)(iVar3 + 0x1cc),1);
        FUN_005ea30c();
        FUN_005e482a(*(undefined4 *)(iVar3 + 0x1d0),DAT_005e625c,6,100);
        FUN_0049942e(*(undefined4 *)(iVar3 + 0x1d4),DAT_005e6260);
        FUN_0049942e(*(undefined4 *)(iVar3 + 0x1dc),PTR_s__Tap___hold_to_stop_response__005e6538);
        FUN_005e4902();
      }
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(3,PTR_s_terminal_ui_005e6b90,PTR_s_D__01_workspace_s200_ap510b_iar__005e6b8c,
                     PTR_s_terminal_ui_action_session_statu_005e6b10,0x553,
                     PTR_s_session_status___d_005e6b94,cVar1);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0xc400000,_DAT_005e6e28,_DAT_005e6e28,cVar1);
      }
      iVar3 = 0;
    }
  }
  return iVar3;
}

