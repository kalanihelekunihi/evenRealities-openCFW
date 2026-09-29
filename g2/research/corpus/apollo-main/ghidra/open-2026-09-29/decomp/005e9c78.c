
undefined4 terminal_action_session_list(undefined4 *param_1)

{
  char cVar1;
  bool bVar2;
  char cVar3;
  undefined4 uVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  bool bVar9;
  
  if (param_1 == (undefined4 *)0x0) {
    uVar4 = 0xffffffff;
  }
  else {
    iVar5 = td_counter_b_get();
    cVar1 = td_flag_b_get();
    td_state_sync(param_1);
    iVar6 = td_counter_b_get();
    iVar7 = td_state_ptr_alias1();
    iVar8 = UX_GetSystemBLEStatus();
    if (((iVar8 == 0) || (iVar7 == 0)) || (*(char *)(iVar7 + 0xa1d8) != '\x02')) {
      bVar2 = false;
    }
    else {
      bVar2 = true;
    }
    bVar9 = iVar6 != 0;
    if ((iVar5 == iVar6) || (cVar1 == '\0')) {
      cVar1 = '\0';
    }
    else {
      cVar1 = '\x01';
    }
    if (((bVar2) && (iVar7 = td_has_active_session(), iVar7 != 0)) &&
       (iVar7 = semantic_terminal_state_is_processing(*(undefined1 *)(DAT_005ea01c + 0x275)),
       iVar7 != 0)) {
      bVar2 = true;
    }
    else {
      bVar2 = false;
    }
    cVar3 = '\0';
    if (!bVar9 || iVar5 == iVar6) {
      if (!bVar2 || bVar9) {
        cVar3 = terminal_refresh_session_list_if_visible();
      }
      else {
        uVar4 = FUN_005ecafa();
        terminal_request_display(0x1b,uVar4);
      }
      bVar2 = bVar2 && !bVar9;
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        FUN_0043d574(3,PTR_s_terminal_pb_005e9f68,PTR_s_D__01_workspace_s200_ap510b_iar__005e9f64,
                     PTR_s_terminal_action_session_list_005ea1c0,0x2e0,
                     PTR_s_recv_terminal_session_list__host_005ea1c8,*param_1,param_1[1],
                     *(undefined2 *)(param_1 + 2),bVar2,cVar3 != '\0');
      }
      iVar5 = FUN_0043d0ce();
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        compress_log_output(0xd400000,PTR_s__terminal_pb_recv_terminal_sessi_005ea1cc,
                            PTR_s__terminal_pb_recv_terminal_sessi_005ea1cc,*param_1,param_1[1],
                            *(undefined2 *)(param_1 + 2),bVar2,cVar3 != '\0');
      }
      terminal_log_session_list_items(param_1);
      uVar4 = 0;
    }
    else {
      if (cVar1 != '\0') {
        terminal_data_bind_temp_session_response_timer(iVar6);
      }
      terminal_apply_session_id_changed(iVar6,1);
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        FUN_0043d574(3,PTR_s_terminal_pb_005e9f68,PTR_s_D__01_workspace_s200_ap510b_iar__005e9f64,
                     PTR_s_terminal_action_session_list_005ea1c0,0x2d2,
                     PTR_s_recv_terminal_session_list__host_005ea1bc,*param_1,param_1[1],
                     *(undefined2 *)(param_1 + 2),cVar1);
      }
      iVar5 = FUN_0043d0ce();
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        compress_log_output(0xd000000,PTR_s__terminal_pb_recv_terminal_sessi_005ea1c4,
                            PTR_s__terminal_pb_recv_terminal_sessi_005ea1c4,*param_1,param_1[1],
                            *(undefined2 *)(param_1 + 2),cVar1);
      }
      terminal_log_session_list_items(param_1);
      uVar4 = 0;
    }
  }
  return uVar4;
}

