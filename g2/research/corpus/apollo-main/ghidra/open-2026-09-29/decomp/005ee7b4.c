
void tracepoint_handle_delete_all
               (undefined1 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined1 uVar1;
  int iVar2;
  int iVar3;
  
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    uVar1 = tracepoint_role_char();
    FUN_0043d574(3,PTR_s_tp_setting_005ee8b8,PTR_s_D__01_workspace_s200_ap510b_iar__005ee8b4,
                 PTR_s_tracepoint_handle_delete_all_005eeffc,0x19c,
                 PTR_s_tracepoint_delete_all_request_ma_005eeff8,param_1,uVar1,param_4);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    uVar1 = tracepoint_role_char();
    compress_log_output(0xc800000,PTR_s__tp_setting_tracepoint_delete_al_005ef000,
                        PTR_s__tp_setting_tracepoint_delete_al_005ef000,param_1,uVar1);
  }
  iVar2 = tracepoint_delete_all_files();
  iVar3 = FUN_0043d0ce();
  if (iVar3 << 0x1e < 0) {
    FUN_0043d574(3,PTR_s_tp_setting_005ee8b8,PTR_s_D__01_workspace_s200_ap510b_iar__005ee8b4,
                 PTR_s_tracepoint_handle_delete_all_005eeffc,0x1a0,
                 PTR_s_tracepoint_delete_all_result__d_005ef004,iVar2);
  }
  iVar3 = FUN_0043d0ce();
  if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
    compress_log_output(0xc400000,PTR_s__tp_setting_tracepoint_delete_al_005ef008,
                        PTR_s__tp_setting_tracepoint_delete_al_005ef008,iVar2);
  }
  tracepoint_make_result_message(3,param_1,iVar2 < 0);
  tracepoint_reply_result(DAT_005eeb60);
  return;
}

