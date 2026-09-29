
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_005e5de0(char param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uStack_14;
  
  iVar1 = _DAT_005e68d8;
  uStack_14 = param_4;
  FUN_005e7f26();
  FUN_005e7fc0();
  if (param_1 == '\x04') {
    AUDM_appRelease(6);
    FUN_005e4878(*(undefined4 *)(iVar1 + 0x1f8));
  }
  FUN_005ec268();
  FUN_0043c0e4(&uStack_14,1,0);
  uStack_14 = CONCAT31(uStack_14._1_3_,5);
  APP_PbTerminalTxEncodeVoiceInput(&uStack_14);
  if ((((*(int *)(iVar1 + 0x1cc) != 0) && (*(int *)(iVar1 + 0x1d0) != 0)) &&
      (*(int *)(iVar1 + 0x1d4) != 0)) && (*(int *)(iVar1 + 0x1dc) != 0)) {
    FUN_0043dfa4(*(undefined4 *)(iVar1 + 0x1cc),1);
    FUN_005ea30c();
    FUN_005e47fe(*(undefined4 *)(iVar1 + 0x1d0),DAT_005e6254);
    FUN_0049942e(*(undefined4 *)(iVar1 + 0x1d4),DAT_005e6258);
    FUN_0049942e(*(undefined4 *)(iVar1 + 0x1dc),DAT_005e6534);
    FUN_005e4894();
  }
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(2,PTR_s_terminal_ui_005e6004,PTR_s_D__01_workspace_s200_ap510b_iar__005e6000,
                 PTR_s_terminal_ui_action_asr_fail_005e698c,0x4fe,
                 PTR_s_asr_failed_timeout__back_to_idle_005e6988,param_1);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x8400000,PTR_s__terminal_ui_asr_failed_timeout__005e6b88,
                        PTR_s__terminal_ui_asr_failed_timeout__005e6b88,param_1);
  }
  return 0;
}

