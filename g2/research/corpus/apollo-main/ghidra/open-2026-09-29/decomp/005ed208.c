
undefined4 FUN_005ed208(char param_1,undefined4 param_2)

{
  int *piVar1;
  char cVar2;
  short sVar3;
  int iVar4;
  
  piVar1 = DAT_005ed744;
  sVar3 = FUN_005eca44(param_2);
  cVar2 = param_1;
  if (param_1 == '\f') {
    cVar2 = '\x02';
  }
  *(char *)((int)piVar1 + 0x276) = cVar2;
  if ((param_1 == '\f') && (iVar4 = td_flag_b_get(), iVar4 != 0)) {
    APP_PbTerminalTxEncodeNewSessionCancel();
    td_flag_set_with_reset(0);
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      FUN_0043d574(3,PTR_s_terminal_ui_005ed9dc,DAT_005ed9d8,
                   PTR_s_terminal_ui_action_session_list__005ed9d4,0x1c1,
                   PTR_s_new_session_pending_cancelled_be_005ed9d0);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0xc000000,PTR_s__terminal_ui_new_session_pending_005ed9e0);
    }
  }
  FUN_005ec268();
  FUN_005ebbc6();
  FUN_005ec9c0();
  if (param_1 != '\b') {
    FUN_005ec770();
  }
  if (*piVar1 != 0) {
    FUN_0043ded4(*piVar1,1);
  }
  FUN_005ed1fa();
  FUN_005ecef6((int)sVar3);
  iVar4 = FUN_0043d0ce();
  if (iVar4 << 0x1e < 0) {
    FUN_0043d574(3,PTR_s_terminal_ui_005ed9dc,DAT_005ed9d8,
                 PTR_s_terminal_ui_action_session_list__005ed9d4,0x1d0,
                 PTR_s_session_list_show__from__d_selec_005ed9e4,param_1,(int)sVar3);
  }
  iVar4 = FUN_0043d0ce();
  if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
    compress_log_output(0xc800000,PTR_s__terminal_ui_session_list_show__f_005ed9e8,
                        PTR_s__terminal_ui_session_list_show__f_005ed9e8,param_1,(int)sVar3);
  }
  return 0;
}

