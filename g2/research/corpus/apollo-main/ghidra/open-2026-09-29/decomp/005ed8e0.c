
longlong FUN_005ed8e0(char param_1,undefined4 param_2,uint param_3)

{
  undefined2 uVar1;
  int iVar2;
  
  iVar2 = DAT_005ed9c4;
  if (param_1 == '\v') {
    *(undefined1 *)(DAT_005ed9c4 + 0x27d) = 0;
    *(undefined1 *)(iVar2 + 0x27e) = 0;
    if (*(int *)(iVar2 + 4) != 0) {
      FUN_0043dfa4(*(undefined4 *)(iVar2 + 4),1);
    }
    FUN_005ecef6((int)*(short *)(iVar2 + 0x27a));
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_3 = 0x271;
      FUN_0043d574(2,PTR_s_terminal_ui_005ed9dc,DAT_005ed9d8,
                   PTR_s_terminal_ui_action_new_session_r_005eda54,0x271,
                   PTR_s_new_session_denied__keep_selecto_005eda50);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x8000000,PTR_s__terminal_ui_new_session_denied__005eda58,
                          PTR_s__terminal_ui_new_session_denied__005eda58);
    }
  }
  else {
    *(undefined1 *)(DAT_005ed9c4 + 0x27e) = 0;
    if (*(int *)(iVar2 + 4) != 0) {
      FUN_0043dfa4(*(undefined4 *)(iVar2 + 4),1);
    }
    FUN_005ec268();
    FUN_005ebbc6();
    FUN_005ec770();
    uVar1 = FUN_005ecaac();
    terminal_request_display(0x1b,uVar1);
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_3 = 0x27d;
      FUN_0043d574(2,PTR_s_terminal_ui_005ed9dc,DAT_005ed9d8,
                   PTR_s_terminal_ui_action_new_session_r_005eda54,0x27d,
                   PTR_s_new_session_failed_after_pending_005eda5c);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x8000000,PTR_s__terminal_ui_new_session_failed_a_005eda60,
                          PTR_s__terminal_ui_new_session_failed_a_005eda60);
    }
  }
  return (ulonglong)param_3 << 0x20;
}

