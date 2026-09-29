
undefined4 FUN_005ed4f8(undefined4 param_1,undefined4 param_2)

{
  byte bVar1;
  short sVar2;
  undefined4 *puVar3;
  undefined4 uVar4;
  int iVar5;
  
  bVar1 = func_0x005eca3e(param_2);
  sVar2 = FUN_005eca44(param_2);
  puVar3 = (undefined4 *)td_active_session();
  if (bVar1 == 1) {
    if (puVar3 == (undefined4 *)0x0) {
      return 0;
    }
    iVar5 = FUN_005eca64((int)sVar2);
    if (iVar5 == 0) {
      return 0;
    }
    FUN_005ed1ec(puVar3[sVar2 * 0x24 + 0x27]);
    FUN_005eceb2();
    FUN_005ed1d6();
    terminal_request_display(0x22,*(undefined1 *)((int)puVar3 + sVar2 * 0x90 + 0x122));
    iVar5 = FUN_0043d0ce();
    if (iVar5 << 0x1e < 0) {
      FUN_0043d574(3,PTR_s_terminal_ui_005ed9dc,DAT_005ed9d8,
                   PTR_s_terminal_ui_action_session_list__005eda10,0x20f,
                   PTR_s_session_select_current__idx__d_s_005eda0c,(int)sVar2,
                   *(undefined1 *)((int)puVar3 + sVar2 * 0x90 + 0x122));
    }
    iVar5 = FUN_0043d0ce();
    if ((-1 < iVar5 << 0x1f) && (iVar5 = FUN_0043d0ce(), -1 < iVar5 << 0x1d)) {
      return 0;
    }
    compress_log_output(0xc800000,PTR_s__terminal_ui_session_select_curr_005eda14,
                        PTR_s__terminal_ui_session_select_curr_005eda14,(int)sVar2,
                        *(undefined1 *)((int)puVar3 + sVar2 * 0x90 + 0x122));
    return 0;
  }
  if (bVar1 != 0) {
    if (bVar1 == 3) {
      iVar5 = td_has_active_session();
      if (iVar5 == 0) {
        return 0;
      }
      td_counter_a_get();
      APP_PbTerminalTxEncodeNewSessionRequest();
      iVar5 = DAT_005ed744;
      *(undefined1 *)(DAT_005ed744 + 0x27e) = 1;
      if (*(int *)(iVar5 + 4) != 0) {
        FUN_0043ded4(*(undefined4 *)(iVar5 + 4),1);
      }
      FUN_005ece4c(0x5ed85c);
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        uVar4 = td_counter_a_get();
        FUN_0043d574(3,PTR_s_terminal_ui_005ed9dc,DAT_005ed9d8,
                     PTR_s_terminal_ui_action_session_list__005eda10,0x227,
                     PTR_s_new_session_requested__host__lu_005eda20,uVar4);
      }
      iVar5 = FUN_0043d0ce();
      if ((-1 < iVar5 << 0x1f) && (iVar5 = FUN_0043d0ce(), -1 < iVar5 << 0x1d)) {
        return 0;
      }
      uVar4 = td_counter_a_get();
      compress_log_output(0xc400000,PTR_s__terminal_ui_new_session_request_005eda24,
                          PTR_s__terminal_ui_new_session_request_005eda24,uVar4);
      return 0;
    }
    if (bVar1 < 3) {
      if (puVar3 == (undefined4 *)0x0) {
        return 0;
      }
      iVar5 = FUN_005eca64((int)sVar2);
      if (iVar5 == 0) {
        return 0;
      }
      APP_PbTerminalTxEncodeSessionSwitchRequest(*puVar3,puVar3[sVar2 * 0x24 + 0x27]);
      iVar5 = DAT_005ed744;
      *(undefined1 *)(DAT_005ed744 + 0x27e) = 1;
      if (*(int *)(iVar5 + 4) != 0) {
        FUN_0043ded4(*(undefined4 *)(iVar5 + 4),1);
      }
      FUN_005ece4c(0x5ed85c);
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        FUN_0043d574(3,PTR_s_terminal_ui_005ed9dc,DAT_005ed9d8,
                     PTR_s_terminal_ui_action_session_list__005eda10,0x21b,
                     PTR_s_session_switch_requested__idx__d_005eda18,(int)sVar2,
                     puVar3[sVar2 * 0x24 + 0x27]);
      }
      iVar5 = FUN_0043d0ce();
      if ((-1 < iVar5 << 0x1f) && (iVar5 = FUN_0043d0ce(), -1 < iVar5 << 0x1d)) {
        return 0;
      }
      compress_log_output(0xc800000,PTR_s__terminal_ui_session_switch_requ_005eda1c,
                          PTR_s__terminal_ui_session_switch_requ_005eda1c,(int)sVar2,
                          puVar3[sVar2 * 0x24 + 0x27]);
      return 0;
    }
  }
  iVar5 = FUN_0043d0ce();
  if (iVar5 << 0x1e < 0) {
    FUN_0043d574(2,PTR_s_terminal_ui_005ed9dc,DAT_005ed9d8,
                 PTR_s_terminal_ui_action_session_list__005eda10,0x22c,
                 PTR_s_session_select_ignored__action___005eda28,bVar1,(int)sVar2);
  }
  iVar5 = FUN_0043d0ce();
  if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
    compress_log_output(0x8800000,PTR_s__terminal_ui_session_select_igno_005eda2c,
                        PTR_s__terminal_ui_session_select_igno_005eda2c,bVar1,(int)sVar2);
  }
  return 0;
}

