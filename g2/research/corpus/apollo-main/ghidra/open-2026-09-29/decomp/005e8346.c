
void terminal_apply_session_id_changed(int param_1,char param_2)

{
  undefined1 uVar1;
  int iVar2;
  undefined4 uVar3;
  
  td_session_bind_store(param_1);
  uVar1 = semantic_terminal_cached_session_status(param_1);
  td_flag_set_with_reset(0);
  semantic_terminal_reset_output_tracking();
  if (param_2 != '\0') {
    td_ring_reset_wrapper();
  }
  td_notify_state_clear();
  td_session_struct_clear();
  td_record_status_set(param_1,uVar1);
  if ((param_1 == 0) && (iVar2 = td_has_active_session(), iVar2 != 0)) {
    if (*(char *)(DAT_005e8c04 + 0x275) == '\v') {
      terminal_request_display(0x1c,0x40000000);
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(3,DAT_005e8c18,DAT_005e8c14,PTR_s_terminal_apply_session_id_change_005e8e48,
                     0x99,PTR_s_recv_terminal_session_id_changed_005e8e44);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0xc000000,PTR_s__terminal_pb_recv_terminal_sessi_005e8e4c);
      }
    }
    else {
      uVar3 = FUN_005ecafa();
      terminal_request_display(0x1b,uVar3);
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(3,DAT_005e8c18,DAT_005e8c14,PTR_s_terminal_apply_session_id_change_005e8e48,
                     0x9c,PTR_s_recv_terminal_session_id_changed_005e8e50);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0xc000000,PTR_s__terminal_pb_recv_terminal_sessi_005e8e54,
                            PTR_s__terminal_pb_recv_terminal_sessi_005e8e54);
      }
    }
  }
  else {
    terminal_request_display(0x23,param_1);
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      uVar3 = semantic_terminal_session_status_name(uVar1);
      FUN_0043d574(3,DAT_005e8c18,DAT_005e8c14,PTR_s_terminal_apply_session_id_change_005e8e48,0xa2,
                   PTR_s_recv_terminal_session_id_changed_005e8e58,param_1,uVar1,uVar3);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      uVar3 = semantic_terminal_session_status_name(uVar1);
      compress_log_output(0xcc00000,DAT_005e9028,DAT_005e9028,param_1,uVar1,uVar3);
    }
  }
  return;
}

