
undefined4 FUN_005ed492(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  short sVar1;
  int iVar2;
  
  sVar1 = FUN_005eca44(param_2);
  FUN_005ecc1a((int)sVar1);
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    FUN_0043d574(3,PTR_s_terminal_ui_005ed9dc,DAT_005ed9d8,DAT_005eda04,0x1fd,DAT_005eda00,
                 (int)sVar1,param_4);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0xc400000,PTR_s__terminal_ui_session_list_scroll_005eda08,
                        PTR_s__terminal_ui_session_list_scroll_005eda08,(int)sVar1);
  }
  return 0;
}

