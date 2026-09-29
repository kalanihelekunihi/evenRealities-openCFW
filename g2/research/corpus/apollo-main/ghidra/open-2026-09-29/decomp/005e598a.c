
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

longlong FUN_005e598a(undefined4 param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  undefined4 uStack_10;
  
  iVar2 = DAT_005e5dd8;
  uVar3 = param_2;
  uStack_10 = param_4;
  FUN_005e7f26();
  FUN_005e7f6e();
  if (param_2 == 0) {
    FUN_0043c0e4(&uStack_10,1,0);
    uStack_10 = CONCAT31(uStack_10._1_3_,2);
    APP_PbTerminalTxEncodeVoiceInput(&uStack_10);
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      uVar3 = 0x443;
      FUN_0043d574(3,PTR_s_terminal_ui_005e6004,PTR_s_D__01_workspace_s200_ap510b_iar__005e6000,
                   PTR_s_terminal_ui_action_voice_stop_005e63a8,0x443,
                   PTR_s_voice_stop_manual_005e63a4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0xc000000,PTR_s__terminal_ui_voice_stop_manual_005e63ac,
                          PTR_s__terminal_ui_voice_stop_manual_005e63ac);
    }
  }
  AUDM_appRelease(6);
  FUN_005e4878(*(undefined4 *)(iVar2 + 0x1f8));
  if ((((*(int *)(iVar2 + 0x1cc) != 0) && (*(int *)(iVar2 + 0x1d0) != 0)) &&
      (*(int *)(iVar2 + 0x1d4) != 0)) && (*(int *)(iVar2 + 0x1dc) != 0)) {
    FUN_0043dfa4(*(undefined4 *)(iVar2 + 0x1cc),1);
    FUN_005ea30c();
    FUN_005e47fe(*(undefined4 *)(iVar2 + 0x1d0),_DAT_005e6264);
    FUN_0049942e(*(undefined4 *)(iVar2 + 0x1d4),PTR_s_Recognizing____005e63b0);
    FUN_0049942e(*(undefined4 *)(iVar2 + 0x1dc),0x5e5ca4);
    FUN_005e4894();
  }
  iVar2 = td_state_ptr();
  if (*(short *)(iVar2 + 0x802) == 0) {
    func_0x005ebfae(PTR_s_Waiting_for_result____005e66bc);
  }
  else {
    func_0x005ebfae();
  }
  func_0x005ebfe0();
  return (ulonglong)uVar3 << 0x20;
}

