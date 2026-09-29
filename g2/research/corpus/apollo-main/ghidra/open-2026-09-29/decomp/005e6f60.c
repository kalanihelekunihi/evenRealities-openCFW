
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_005e6f60(undefined4 param_1,undefined4 param_2)

{
  char cVar1;
  undefined1 uVar2;
  undefined1 uVar3;
  undefined4 uVar4;
  int iVar5;
  
  iVar5 = _DAT_005e7268;
  uVar4 = FUN_005e4cd4(param_2);
  if (*(int *)(iVar5 + 0x214) != 0) {
    cVar1 = FUN_005e4cd8(param_2);
    uVar2 = FUN_005e4cde(param_2);
    uVar3 = FUN_005e4ce6(param_2);
    if (cVar1 != '\0') {
      FUN_0044ea04(*(undefined4 *)(iVar5 + 0x214),uVar4,1);
    }
    *(undefined1 *)(iVar5 + 0x27c) = uVar2;
    *(undefined1 *)(iVar5 + 0x279) = uVar3;
    FUN_005ebb96();
    iVar5 = FUN_0043d0ce();
    if (iVar5 << 0x1e < 0) {
      FUN_0043d574(3,PTR_s_terminal_ui_005e72bc,PTR_s_D__01_workspace_s200_ap510b_iar__005e72b8,
                   PTR_s_terminal_ui_action_query_scroll__005e7b48,0x71e,
                   PTR_s_query_scroll_down_apply__browsin_005e7b44,uVar2,uVar3,uVar4,cVar1);
    }
    iVar5 = FUN_0043d0ce();
    if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
      compress_log_output(0xd000000,PTR_s__terminal_ui_query_scroll_down_a_005e7b4c,
                          PTR_s__terminal_ui_query_scroll_down_a_005e7b4c,uVar2,uVar3,uVar4,cVar1);
    }
  }
  return 0;
}

