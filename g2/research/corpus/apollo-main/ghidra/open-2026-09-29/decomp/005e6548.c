
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_005e6548(char param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  int iVar2;
  
  piVar1 = _DAT_005e68d8;
  if (param_2 == 0) {
    param_2 = _DAT_005e68d8[0xa2];
  }
  if (param_2 == 0) {
    param_2 = td_counter_b_get();
  }
  piVar1[0xa2] = param_2;
  if (param_1 == '\x01') {
    param_1 = '\0';
  }
  *(char *)((int)piVar1 + 0x277) = param_1;
  *(undefined1 *)((int)piVar1 + 0x27f) = 0;
  if ((*(char *)((int)piVar1 + 0x277) == '\0') && (*piVar1 != 0)) {
    FUN_0043ded4(*piVar1,1);
  }
  func_0x005ec82a();
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    FUN_0043d574(3,PTR_s_terminal_ui_005e6b90,PTR_s_D__01_workspace_s200_ap510b_iar__005e6b8c,
                 PTR_s_terminal_ui_action_query_notific_005e705c,0x5d9,
                 PTR_s_query_notification_shown__sessio_005e7058,piVar1[0xa2],
                 *(undefined1 *)((int)piVar1 + 0x277),param_4);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0xc800000,PTR_s__terminal_ui_query_notification_s_005e7244,
                        PTR_s__terminal_ui_query_notification_s_005e7244,piVar1[0xa2],
                        *(undefined1 *)((int)piVar1 + 0x277));
  }
  return 0;
}

