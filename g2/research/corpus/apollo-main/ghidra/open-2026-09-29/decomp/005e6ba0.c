
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_005e6ba0(void)

{
  char cVar1;
  int iVar2;
  undefined4 uVar3;
  
  iVar2 = _DAT_005e7268;
  cVar1 = *(char *)(_DAT_005e7268 + 0x280);
  uVar3 = *(undefined4 *)(_DAT_005e7268 + 0x284);
  FUN_005ec770();
  *(undefined1 *)(iVar2 + 0x280) = 0;
  *(undefined4 *)(iVar2 + 0x284) = 0;
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    FUN_0043d574(3,PTR_s_terminal_ui_005e72bc,PTR_s_D__01_workspace_s200_ap510b_iar__005e72b8,
                 PTR_s_terminal_ui_action_interrupt_con_005e72b4,0x693,
                 PTR_s_interrupt_confirm_cancel__deferr_005e72b0,cVar1,uVar3);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0xc800000,PTR_s__terminal_ui_interrupt_confirm_c_005e72c0,
                        PTR_s__terminal_ui_interrupt_confirm_c_005e72c0,cVar1,uVar3);
  }
  if (cVar1 == '\0') {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(3,PTR_s_terminal_ui_005e72bc,PTR_s_D__01_workspace_s200_ap510b_iar__005e72b8,
                   PTR_s_terminal_ui_action_interrupt_con_005e72b4,0x698,
                   PTR_s_interrupt_confirm_cancelled__bac_005e72cc);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0xc000000,PTR_s__terminal_ui_interrupt_confirm_c_005e72d0,
                          PTR_s__terminal_ui_interrupt_confirm_c_005e72d0);
    }
  }
  else {
    terminal_request_display(0x15,uVar3);
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(3,PTR_s_terminal_ui_005e72bc,PTR_s_D__01_workspace_s200_ap510b_iar__005e72b8,
                   PTR_s_terminal_ui_action_interrupt_con_005e72b4,0x696,
                   PTR_s_interrupt_confirm_cancel__>_repl_005e72c4,uVar3);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0xc400000,PTR_s__terminal_ui_interrupt_confirm_c_005e72c8,
                          PTR_s__terminal_ui_interrupt_confirm_c_005e72c8,uVar3);
    }
  }
  return 0;
}

