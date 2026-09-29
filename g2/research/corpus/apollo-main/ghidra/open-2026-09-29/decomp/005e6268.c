
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

longlong FUN_005e6268(char param_1,uint param_2)

{
  int iVar1;
  
  iVar1 = _DAT_005e68d8;
  FUN_005e7f26();
  FUN_005e7fc0();
  FUN_005ec268();
  FUN_005ebbc6();
  FUN_005ec770();
  FUN_005ec9c0();
  FUN_005e65f8();
  *(undefined1 *)(iVar1 + 0x280) = 0;
  *(undefined4 *)(iVar1 + 0x284) = 0;
  if (param_1 == '\x03') {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      param_2 = 0x569;
      FUN_0043d574(3,PTR_s_terminal_ui_005e6b90,PTR_s_D__01_workspace_s200_ap510b_iar__005e6b8c,
                   PTR_s_terminal_ui_action_agent_done_005e6d50,0x569,
                   PTR_s_agent_done_while_blocked__keep_b_005e6d4c);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0xc000000,PTR_s__terminal_ui_agent_done_while_bl_005e6d54,
                          PTR_s__terminal_ui_agent_done_while_bl_005e6d54);
    }
  }
  else {
    if ((((*(int *)(iVar1 + 0x1cc) != 0) && (*(int *)(iVar1 + 0x1d0) != 0)) &&
        (*(int *)(iVar1 + 0x1d4) != 0)) && (*(int *)(iVar1 + 0x1dc) != 0)) {
      FUN_0043dfa4(*(undefined4 *)(iVar1 + 0x1cc),1);
      FUN_005ea30c();
      FUN_005e47fe(*(undefined4 *)(iVar1 + 0x1d0),_DAT_005e6dc8);
      FUN_0049942e(*(undefined4 *)(iVar1 + 0x1d4),_DAT_005e6dcc);
      FUN_0049942e(*(undefined4 *)(iVar1 + 0x1dc),DAT_005e6534);
      FUN_005e4894();
    }
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      param_2 = 0x574;
      FUN_0043d574(3,PTR_s_terminal_ui_005e6b90,PTR_s_D__01_workspace_s200_ap510b_iar__005e6b8c,
                   PTR_s_terminal_ui_action_agent_done_005e6d50,0x574,_DAT_005e6e2c,param_1);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0xc400000,PTR_s__terminal_ui_agent_done__back_to_005e7054,
                          PTR_s__terminal_ui_agent_done__back_to_005e7054,param_1);
    }
  }
  return (ulonglong)param_2 << 0x20;
}

