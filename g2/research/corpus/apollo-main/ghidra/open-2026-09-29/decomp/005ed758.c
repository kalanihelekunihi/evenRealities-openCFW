
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

longlong FUN_005ed758(char param_1,uint param_2)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  undefined1 uVar5;
  
  iVar4 = _DAT_005ed86c;
  if (param_1 == '\v') {
    if ((param_2 & 0xff) == 0) {
      uVar1 = td_counter_b_get();
      iVar2 = td_active_session();
      iVar4 = _DAT_005ed86c;
      uVar5 = 0;
      if ((iVar2 != 0) && (iVar3 = FUN_005eca64((int)*(short *)(_DAT_005ed86c + 0x27a)), iVar3 != 0)
         ) {
        uVar1 = *(undefined4 *)(*(short *)(iVar4 + 0x27a) * 0x90 + iVar2 + 0x9c);
        uVar5 = *(undefined1 *)(*(short *)(iVar4 + 0x27a) * 0x90 + iVar2 + 0x122);
      }
      FUN_005ed1ec(uVar1);
      FUN_005eceb2();
      FUN_005ed1d6();
      terminal_request_display(0x22,uVar5);
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        param_2 = 0x24e;
        FUN_0043d574(3,PTR_s_terminal_ui_005ed9dc,DAT_005ed9d8,
                     PTR_s_terminal_ui_action_session_switc_005eda34,0x24e,
                     PTR_s_session_switch_success__close_se_005eda30,uVar5);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0xc400000,PTR_s__terminal_ui_session_switch_succ_005eda38,
                            PTR_s__terminal_ui_session_switch_succ_005eda38,uVar5);
      }
    }
    else {
      *(undefined1 *)(_DAT_005ed86c + 0x27d) = 0;
      *(undefined1 *)(iVar4 + 0x27e) = 0;
      FUN_005ecef6((int)*(short *)(iVar4 + 0x27a));
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        param_2 = 0x255;
        FUN_0043d574(2,PTR_s_terminal_ui_005ed9dc,DAT_005ed9d8,
                     PTR_s_terminal_ui_action_session_switc_005eda34,0x255,
                     PTR_s_session_switch_failed__keep_sele_005eda3c);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x8000000,PTR_s__terminal_ui_session_switch_fail_005eda40,
                            PTR_s__terminal_ui_session_switch_fail_005eda40);
      }
    }
  }
  return (ulonglong)param_2 << 0x20;
}

