
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_005e6b18(undefined1 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  iVar1 = _DAT_005e7268;
  *(undefined1 *)(_DAT_005e7268 + 0x278) = 0;
  *(undefined1 *)(iVar1 + 0x280) = 0;
  *(undefined4 *)(iVar1 + 0x284) = 0;
  func_0x005ec446();
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(3,PTR_s_terminal_ui_005e6b90,PTR_s_D__01_workspace_s200_ap510b_iar__005e6b8c,
                 PTR_s_terminal_ui_action_interrupt_con_005e72a8,0x684,
                 PTR_s_interrupt_confirm_shown__from_st_005e72a4,param_1,param_4);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0xc400000,PTR_s__terminal_ui_interrupt_confirm_s_005e72ac,
                        PTR_s__terminal_ui_interrupt_confirm_s_005e72ac,param_1);
  }
  return 0;
}

