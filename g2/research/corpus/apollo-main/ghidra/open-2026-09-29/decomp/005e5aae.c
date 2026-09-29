
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

longlong FUN_005e5aae(char param_1,uint param_2)

{
  int iVar1;
  int iVar2;
  
  iVar2 = DAT_005e5dd8;
  FUN_005e7f26();
  FUN_005e7fc0();
  if (param_1 == '\x04') {
    AUDM_appRelease(6);
    FUN_005e4878(*(undefined4 *)(iVar2 + 0x1f8));
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      param_2 = 0x481;
      FUN_0043d574(2,PTR_s_terminal_ui_005e6004,PTR_s_D__01_workspace_s200_ap510b_iar__005e6000,
                   PTR_s_terminal_ui_action_asr_final_005e6540,0x481,
                   PTR_s_ASR_final_received_while_capturi_005e653c);
    }
    iVar1 = FUN_0043d0ce();
    if (-1 < iVar1 << 0x1f) {
      iVar1 = FUN_0043d0ce();
      if (-1 < iVar1 << 0x1d) goto LAB_005e5b14;
    }
    compress_log_output(0x8000000,PTR_s__terminal_ui_ASR_final_received_w_005e6544,
                        PTR_s__terminal_ui_ASR_final_received_w_005e6544);
  }
LAB_005e5b14:
  iVar1 = td_state_ptr();
  if (*(short *)(iVar1 + 0x802) != 0) {
    func_0x005ebfae();
  }
  func_0x005ebff8();
  if ((((*(int *)(iVar2 + 0x1cc) != 0) && (*(int *)(iVar2 + 0x1d0) != 0)) &&
      (*(int *)(iVar2 + 0x1d4) != 0)) && (*(int *)(iVar2 + 0x1dc) != 0)) {
    FUN_0043dfa4(*(undefined4 *)(iVar2 + 0x1cc),1);
    FUN_005ea30c();
    FUN_005e47fe(*(undefined4 *)(iVar2 + 0x1d0),DAT_005e6254);
    FUN_0049942e(*(undefined4 *)(iVar2 + 0x1d4),PTR_s_Confirm_input__005e6614);
    FUN_0049942e(*(undefined4 *)(iVar2 + 0x1dc),PTR_s__Swipe_to_select__005e6618);
    FUN_005e4894();
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    param_2 = 0x492;
    FUN_0043d574(3,PTR_s_terminal_ui_005e6004,PTR_s_D__01_workspace_s200_ap510b_iar__005e6000,
                 PTR_s_terminal_ui_action_asr_final_005e6540,0x492,
                 PTR_s_ASR_final_received__showing_conf_005e661c);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0xc000000,_DAT_005e68b0);
  }
  return (ulonglong)param_2 << 0x20;
}

