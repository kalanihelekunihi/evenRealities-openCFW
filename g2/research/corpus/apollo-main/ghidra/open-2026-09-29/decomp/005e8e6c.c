
undefined4
terminal_action_asr_result
          (undefined2 *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  bool bVar2;
  
  if (param_1 == (undefined2 *)0x0) {
    return 0xffffffff;
  }
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(3,PTR_s_terminal_pb_005e9384,PTR_s_D__01_workspace_s200_ap510b_iar__005e9380,
                 PTR_s_terminal_action_asr_result_005e98f4,0x191,
                 PTR_s_recv_terminal_asr_result_len___d_005e98f0,*param_1,
                 *(undefined1 *)(param_1 + 0x101),*(undefined1 *)((int)param_1 + 0x203),param_4);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0xcc00000,PTR_s__terminal_pb_recv_terminal_asr_r_005e98f8,
                        PTR_s__terminal_pb_recv_terminal_asr_r_005e98f8,*param_1,
                        *(undefined1 *)(param_1 + 0x101),*(undefined1 *)((int)param_1 + 0x203));
  }
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(3,PTR_s_terminal_pb_005e9384,PTR_s_D__01_workspace_s200_ap510b_iar__005e9380,
                 PTR_s_terminal_action_asr_result_005e98f4,0x192,&DAT_005e902c,param_1 + 1);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0xc400000,PTR_s__terminal_pb__s_005e98fc,PTR_s__terminal_pb__s_005e98fc,
                        param_1 + 1);
  }
  if ((*(char *)((int)param_1 + 0x203) != '\0') && (*(char *)(DAT_005e938c + 0x275) == '\x04')) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(1,PTR_s_terminal_pb_005e9384,PTR_s_D__01_workspace_s200_ap510b_iar__005e9380,
                   PTR_s_terminal_action_asr_result_005e98f4,0x195,
                   PTR_s_invalid_ASR_state__all_final_arr_005e9ab0);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__terminal_pb_invalid_ASR_state__a_005e9ab4,
                          PTR_s__terminal_pb_invalid_ASR_state__a_005e9ab4);
    }
    return 0;
  }
  td_ring_write(param_1);
  iVar1 = td_state_ptr();
  if (((*(char *)((int)param_1 + 0x203) == '\0') || (iVar1 == 0)) ||
     (*(short *)(iVar1 + 0x802) == 0)) {
    bVar2 = false;
  }
  else {
    bVar2 = true;
  }
  if ((*(char *)((int)param_1 + 0x203) == '\0') || (bVar2)) {
    if (bVar2) {
      terminal_request_display(0xb,0);
    }
    else {
      terminal_request_display(10,0);
    }
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(2,PTR_s_terminal_pb_005e9384,PTR_s_D__01_workspace_s200_ap510b_iar__005e9380,
                   PTR_s_terminal_action_asr_result_005e98f4,0x1a0,DAT_005e9b04);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8000000,PTR_s__terminal_pb_ASR_final_with_empt_005e9c54,
                          PTR_s__terminal_pb_ASR_final_with_empt_005e9c54);
    }
    td_notify_state_clear();
    terminal_request_display(0xc,0);
  }
  return 0;
}

