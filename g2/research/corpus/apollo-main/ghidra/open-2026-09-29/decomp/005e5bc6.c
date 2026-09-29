
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

longlong FUN_005e5bc6(undefined4 param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uStack_10;
  
  iVar1 = DAT_005e5dd8;
  uStack_10 = param_4;
  td_counter_b_get();
  terminal_data_start_response_timer();
  td_record_status_write(1);
  FUN_005ec268();
  *(undefined1 *)(iVar1 + 0x28c) = 1;
  FUN_005e4c84(0);
  FUN_0043c0e4(&uStack_10,1,0);
  uStack_10 = CONCAT31(uStack_10._1_3_,4);
  APP_PbTerminalTxEncodeVoiceInput(&uStack_10);
  if ((((*(int *)(iVar1 + 0x1cc) != 0) && (*(int *)(iVar1 + 0x1d0) != 0)) &&
      (*(int *)(iVar1 + 0x1d4) != 0)) && (*(int *)(iVar1 + 0x1dc) != 0)) {
    FUN_0043dfa4(*(undefined4 *)(iVar1 + 0x1cc),1);
    FUN_005ea30c();
    FUN_005e482a(*(undefined4 *)(iVar1 + 0x1d0),DAT_005e625c,6,100);
    FUN_0049942e(*(undefined4 *)(iVar1 + 0x1d4),DAT_005e6260);
    FUN_0049942e(*(undefined4 *)(iVar1 + 0x1dc),PTR_s__Tap___hold_to_stop_response__005e6538);
    FUN_005e4902();
  }
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    param_2 = 0x4b1;
    FUN_0043d574(3,PTR_s_terminal_ui_005e6004,PTR_s_D__01_workspace_s200_ap510b_iar__005e6000,
                 PTR_s_terminal_ui_action_input_confirm_005e66c4,0x4b1,
                 PTR_s_input_confirmed__entering_agent_p_005e66c0);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0xc000000,_DAT_005e68d4,_DAT_005e68d4);
  }
  return (ulonglong)param_2 << 0x20;
}

