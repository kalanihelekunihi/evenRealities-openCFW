
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

longlong FUN_005e7068(undefined4 param_1,undefined4 param_2,uint param_3)

{
  int iVar1;
  int iVar2;
  
  iVar2 = _DAT_005e7268;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    param_3 = 0x738;
    FUN_0043d574(3,PTR_s_terminal_ui_005e72bc,PTR_s_D__01_workspace_s200_ap510b_iar__005e72b8,
                 PTR_s_terminal_ui_action_agent_interru_005e7b54,0x738,
                 PTR_s_agent_interrupt_triggered_005e7b50);
  }
  iVar1 = FUN_0043d0ce();
  if (-1 < iVar1 << 0x1f) {
    iVar1 = FUN_0043d0ce();
    if (-1 < iVar1 << 0x1d) goto LAB_005e70ac;
  }
  compress_log_output(0xc000000,PTR_s__terminal_ui_agent_interrupt_tri_005e7b58,
                      PTR_s__terminal_ui_agent_interrupt_tri_005e7b58);
LAB_005e70ac:
  FUN_005ec770();
  *(undefined1 *)(iVar2 + 0x280) = 0;
  *(undefined4 *)(iVar2 + 0x284) = 0;
  APP_PbTerminalTxEncodeAgentInterrupt();
  td_counter_b_get();
  td_record_timer_clear();
  td_record_status_write(3);
  td_notify_state_clear();
  if ((((*(int *)(iVar2 + 0x1cc) != 0) && (*(int *)(iVar2 + 0x1d0) != 0)) &&
      (*(int *)(iVar2 + 0x1d4) != 0)) && (*(int *)(iVar2 + 0x1dc) != 0)) {
    FUN_0043dfa4(*(undefined4 *)(iVar2 + 0x1cc),1);
    FUN_005ea30c();
    FUN_005e47fe(*(undefined4 *)(iVar2 + 0x1d0),PTR_DAT_005e7b5c);
    FUN_0049942e(*(undefined4 *)(iVar2 + 0x1d4),PTR_s_Waiting_input_005e7b60);
    FUN_0049942e(*(undefined4 *)(iVar2 + 0x1dc),PTR_s__Tap___hold_to_input__005e7b64);
    FUN_005e4894();
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    param_3 = 0x748;
    FUN_0043d574(3,PTR_s_terminal_ui_005e72bc,PTR_s_D__01_workspace_s200_ap510b_iar__005e72b8,
                 PTR_s_terminal_ui_action_agent_interru_005e7b54,0x748,
                 PTR_s_agent_interrupted__back_to_idle_005e7b68);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0xc000000,PTR_s__terminal_ui_agent_interrupted__b_005e7b6c);
  }
  return (ulonglong)param_3 << 0x20;
}

