
undefined4
tracepoint_setting_common_data_handler(int param_1,int param_2,uint param_3,undefined4 param_4)

{
  undefined1 uVar1;
  int iVar2;
  undefined4 uVar3;
  
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    uVar1 = tracepoint_role_char();
    FUN_0043d574(4,DAT_005ef018,DAT_005ef014,PTR_s_tracepoint_setting_common_data_h_005ef0a0,0x21e,
                 PTR_s_tracepoint_handler_event__d_len__005ef09c,param_1,param_3,uVar1,param_4);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    uVar1 = tracepoint_role_char();
    compress_log_output(0x10c00000,PTR_s__tp_setting_tracepoint_handler_e_005ef0a4,
                        PTR_s__tp_setting_tracepoint_handler_e_005ef0a4,param_1,param_3,uVar1);
  }
  if (param_1 == 0) {
    uVar3 = tracepoint_handle_ble_data(param_2,param_3);
  }
  else if (param_1 == 0xb) {
    uVar3 = tracepoint_handle_slave_file_list(param_2,param_3);
  }
  else if (param_1 == 0xc) {
    if ((param_2 == 0) || (param_3 == 0)) {
      uVar3 = 0xffffffff;
    }
    else {
      uVar3 = Thread_MsgPbTxByBle(1,0x11,param_2,param_3 & 0xffff);
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(4,DAT_005ef018,DAT_005ef014,PTR_s_tracepoint_setting_common_data_h_005ef0a0,
                     0x22a,PTR_s_tracepoint_forward_slave_delete_r_005ef0a8,param_3,uVar3);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x10800000,PTR_s__tp_setting_tracepoint_forward_s_005ef0ac,
                            PTR_s__tp_setting_tracepoint_forward_s_005ef0ac,param_3,uVar3);
      }
    }
  }
  else {
    uVar3 = 0;
  }
  return uVar3;
}

