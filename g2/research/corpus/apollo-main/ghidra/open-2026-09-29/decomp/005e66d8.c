
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_005e66d8(undefined1 param_1)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  undefined4 uVar5;
  uint uVar6;
  int iVar7;
  char cVar8;
  
  iVar4 = _DAT_005e68d8;
  iVar7 = *(int *)(_DAT_005e68d8 + 0x288);
  iVar1 = td_counter_b_get();
  iVar2 = td_active_session();
  iVar3 = td_counter_a_get();
  cVar8 = '\0';
  if (iVar7 == 0) {
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      FUN_0043d574(2,PTR_s_terminal_ui_005e6b90,PTR_s_D__01_workspace_s200_ap510b_iar__005e6b8c,
                   PTR_s_terminal_ui_action_query_notific_005e7208,0x60f,
                   PTR_s_query_notification_activate_igno_005e7204);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x8000000,PTR_s__terminal_ui_query_notification_a_005e724c,
                          PTR_s__terminal_ui_query_notification_a_005e724c);
    }
    uVar5 = FUN_005e6620(param_1);
  }
  else {
    terminal_data_dismiss_query_notification(iVar7);
    if (iVar7 == iVar1) {
      FUN_005ec9c0();
      FUN_005e583c(param_1,0);
      FUN_005e5484(4,iVar7,0);
      FUN_005e65f8();
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        FUN_0043d574(3,PTR_s_terminal_ui_005e6b90,PTR_s_D__01_workspace_s200_ap510b_iar__005e6b8c,
                     PTR_s_terminal_ui_action_query_notific_005e7208,0x619,
                     PTR_s_query_notification_activate_curr_005e7250,iVar7);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0xc400000,PTR_s__terminal_ui_query_notification_a_005e7254,
                            PTR_s__terminal_ui_query_notification_a_005e7254,iVar7);
      }
      uVar5 = 8;
    }
    else {
      if (iVar2 != 0) {
        for (uVar6 = 0; uVar6 < *(uint *)(iVar2 + 8); uVar6 = uVar6 + 1) {
          if (*(int *)(uVar6 * 0x90 + iVar2 + 0x9c) == iVar7) {
            cVar8 = '\x01';
            break;
          }
        }
      }
      if ((cVar8 == '\0') || (iVar3 == 0)) {
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          FUN_0043d574(2,PTR_s_terminal_ui_005e6b90,PTR_s_D__01_workspace_s200_ap510b_iar__005e6b8c,
                       PTR_s_terminal_ui_action_query_notific_005e7208,0x627,
                       PTR_s_query_notification_activate_fail_005e7258,iVar7,cVar8,iVar3);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0x8c00000,PTR_s__terminal_ui_query_notification_a_005e725c,
                              PTR_s__terminal_ui_query_notification_a_005e725c,iVar7,cVar8,iVar3);
        }
        uVar5 = FUN_005e6620(param_1);
      }
      else {
        *(undefined1 *)(iVar4 + 0x27f) = 1;
        APP_PbTerminalTxEncodeSessionSwitchRequest(iVar3,iVar7);
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          FUN_0043d574(3,PTR_s_terminal_ui_005e6b90,PTR_s_D__01_workspace_s200_ap510b_iar__005e6b8c,
                       PTR_s_terminal_ui_action_query_notific_005e7208,0x62d,
                       PTR_s_query_notification_switch_reques_005e7260,iVar7);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0xc400000,PTR_s__terminal_ui_query_notification_s_005e7264,
                              PTR_s__terminal_ui_query_notification_s_005e7264,iVar7);
        }
        uVar5 = 0;
      }
    }
  }
  return uVar5;
}

