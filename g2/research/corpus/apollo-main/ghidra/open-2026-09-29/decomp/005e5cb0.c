
undefined4 FUN_005e5cb0(char param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  undefined4 uStack_18;
  undefined4 uStack_14;
  
  iVar2 = DAT_005e5dd8;
  uStack_18 = param_3;
  uStack_14 = param_4;
  FUN_005e7f26();
  FUN_005e7fc0();
  if (param_1 == '\x04') {
    AUDM_appRelease(6);
    FUN_005e4878(*(undefined4 *)(iVar2 + 0x1f8));
  }
  FUN_005ec268();
  td_notify_state_clear();
  FUN_0043c0e4(&uStack_18,1,0);
  uStack_18 = CONCAT31(uStack_18._1_3_,5);
  APP_PbTerminalTxEncodeVoiceInput(&uStack_18);
  iVar1 = td_flag_b_get();
  if (iVar1 != 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(3,PTR_s_terminal_ui_005e6004,PTR_s_D__01_workspace_s200_ap510b_iar__005e6000,
                   PTR_s_terminal_ui_action_input_cancel_005e66cc,0x4ce,
                   PTR_s_new_session_first_prompt_input_c_005e66c8);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0xc000000,PTR_s__terminal_ui_new_session_first_p_005e66d0,
                          PTR_s__terminal_ui_new_session_first_p_005e66d0);
    }
  }
  if ((((*(int *)(iVar2 + 0x1cc) != 0) && (*(int *)(iVar2 + 0x1d0) != 0)) &&
      (*(int *)(iVar2 + 0x1d4) != 0)) && (*(int *)(iVar2 + 0x1dc) != 0)) {
    FUN_0043dfa4(*(undefined4 *)(iVar2 + 0x1cc),1);
    FUN_005ea30c();
    FUN_005e47fe(*(undefined4 *)(iVar2 + 0x1d0),DAT_005e6254);
    FUN_0049942e(*(undefined4 *)(iVar2 + 0x1d4),DAT_005e6258);
    FUN_0049942e(*(undefined4 *)(iVar2 + 0x1dc),DAT_005e6534);
    FUN_005e4894();
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    FUN_0043d574(3,PTR_s_terminal_ui_005e6004,PTR_s_D__01_workspace_s200_ap510b_iar__005e6000,
                 PTR_s_terminal_ui_action_input_cancel_005e66cc,0x4d9,
                 PTR_s_input_cancelled__back_to_idle_005e66d4);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0xc000000,PTR_s__terminal_ui_input_cancelled__ba_005e6984,
                        PTR_s__terminal_ui_input_cancelled__ba_005e6984);
  }
  return 0;
}

