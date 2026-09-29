
longlong FUN_005ed870(undefined1 param_1,undefined4 param_2,uint param_3,undefined4 param_4)

{
  int iVar1;
  
  FUN_005e5484(3,0,0,param_4,param_3,param_4);
  FUN_005eae2c(4);
  *(undefined1 *)(DAT_005ed9c4 + 0x27e) = 0;
  FUN_005eceb2();
  FUN_005e57c6(param_1,0);
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    param_3 = 0x262;
    FUN_0043d574(3,PTR_s_terminal_ui_005ed9dc,DAT_005ed9d8,
                 PTR_s_terminal_ui_action_new_session_r_005eda48,0x262,
                 PTR_s_new_session_allowed__waiting_fir_005eda44);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0xc000000,PTR_s__terminal_ui_new_session_allowed_005eda4c);
  }
  return (ulonglong)param_3 << 0x20;
}

