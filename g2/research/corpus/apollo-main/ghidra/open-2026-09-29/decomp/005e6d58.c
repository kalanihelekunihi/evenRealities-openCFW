
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_005e6d58(undefined1 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  iVar1 = _DAT_005e7268;
  *(undefined1 *)(_DAT_005e7268 + 0x280) = 1;
  *(undefined4 *)(iVar1 + 0x284) = param_2;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(3,PTR_s_terminal_ui_005e72bc,PTR_s_D__01_workspace_s200_ap510b_iar__005e72b8,
                 PTR_s_terminal_ui_action_interrupt_con_005e72e4,0x6b7,
                 PTR_s_defer_query_while_interrupt_conf_005e72e0,param_1,param_2,param_4);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0xc800000,PTR_s__terminal_ui_defer_query_while_i_005e72e8,
                        PTR_s__terminal_ui_defer_query_while_i_005e72e8,param_1,param_2);
  }
  return 0;
}

