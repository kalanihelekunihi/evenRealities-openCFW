
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_005e58ba(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uStack_10;
  undefined4 uStack_c;
  
  iVar1 = DAT_005e5dd8;
  uStack_10 = param_3;
  uStack_c = param_4;
  td_notify_state_clear();
  FUN_005ebd0e();
  FUN_005e7ed4();
  AUDM_appAcquire(6);
  if ((((*(int *)(iVar1 + 0x1cc) != 0) && (*(int *)(iVar1 + 0x1d0) != 0)) &&
      (*(int *)(iVar1 + 0x1d4) != 0)) && (*(int *)(iVar1 + 0x1dc) != 0)) {
    FUN_0043dfa4(*(undefined4 *)(iVar1 + 0x1cc),1);
    FUN_005ea30c();
    FUN_005e47fe(*(undefined4 *)(iVar1 + 0x1d0),_DAT_005e6264);
    FUN_0049942e(*(undefined4 *)(iVar1 + 0x1d4),PTR_s_Recording____005e6394);
    FUN_0049942e(*(undefined4 *)(iVar1 + 0x1dc),PTR_s__Release_to_stop__005e6398);
    FUN_005e4894();
  }
  FUN_0043c0e4(&uStack_10,1,0);
  uStack_10 = CONCAT31(uStack_10._1_3_,1);
  APP_PbTerminalTxEncodeVoiceInput(&uStack_10);
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(3,PTR_s_terminal_ui_005e6004,PTR_s_D__01_workspace_s200_ap510b_iar__005e6000,
                 PTR_s_terminal_ui_action_voice_start_005e63a0,0x430,
                 PTR_s_voice_start__timer_armed_005e639c);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0xc000000,PTR_s__terminal_ui_voice_start__timer_a_005e6610,
                        PTR_s__terminal_ui_voice_start__timer_a_005e6610);
  }
  return 0;
}

