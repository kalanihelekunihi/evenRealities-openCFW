
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 FUN_005e68dc(undefined1 param_1,char param_2,undefined4 param_3)

{
  undefined4 uVar1;
  int iVar2;
  
  if (*(char *)(_DAT_005e7268 + 0x27f) == '\0') {
    uVar1 = 0;
  }
  else if (param_2 == '\0') {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_3 = 0x644;
      FUN_0043d574(3,PTR_s_terminal_ui_005e6b90,PTR_s_D__01_workspace_s200_ap510b_iar__005e6b8c,
                   PTR_s_terminal_ui_action_query_notific_005e7270,0x644,
                   PTR_s_query_notification_switch_succes_005e726c);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0xc000000,PTR_s__terminal_ui_query_notification_s_005e7274);
    }
    uVar1 = 0;
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_3 = 0x648;
      FUN_0043d574(2,PTR_s_terminal_ui_005e6b90,PTR_s_D__01_workspace_s200_ap510b_iar__005e6b8c,
                   PTR_s_terminal_ui_action_query_notific_005e7270,0x648,
                   PTR_s_query_notification_switch_failed_005e7278);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x8000000,PTR_s__terminal_ui_query_notification_s_005e727c,
                          PTR_s__terminal_ui_query_notification_s_005e727c);
    }
    uVar1 = FUN_005e6620(param_1);
  }
  return CONCAT44(param_3,uVar1);
}

