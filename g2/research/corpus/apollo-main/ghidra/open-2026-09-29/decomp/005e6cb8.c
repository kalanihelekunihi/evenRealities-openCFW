
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_005e6cb8(undefined1 param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  bool bVar2;
  
  if ((*(int *)(_DAT_005e7268 + 0x230) != 0) &&
     (bVar2 = param_2 == 1, (bool)*(char *)(_DAT_005e7268 + 0x278) != bVar2)) {
    *(bool *)(_DAT_005e7268 + 0x278) = bVar2;
    func_0x005ec73c();
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(3,PTR_s_terminal_ui_005e72bc,PTR_s_D__01_workspace_s200_ap510b_iar__005e72b8,
                   PTR_s_terminal_ui_action_interrupt_con_005e72d8,0x6ab,
                   PTR_s_interrupt_confirm_scroll__state__005e72d4,param_1,bVar2,param_4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0xc800000,PTR_s__terminal_ui_interrupt_confirm_s_005e72dc,
                          PTR_s__terminal_ui_interrupt_confirm_s_005e72dc,param_1,bVar2);
    }
  }
  return 0;
}

