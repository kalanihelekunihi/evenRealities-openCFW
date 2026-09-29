
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_005e69a0(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  byte bVar2;
  char cVar3;
  byte bVar4;
  undefined4 *puVar5;
  int iVar6;
  undefined4 uStack_2c;
  undefined4 uStack_28;
  undefined4 uStack_24;
  
  iVar1 = _DAT_005e7268;
  uStack_24 = param_4;
  puVar5 = (undefined4 *)td_session_struct_ptr();
  *(undefined1 *)(iVar1 + 0x28c) = 1;
  FUN_005e4c84(0);
  bVar2 = FUN_005e4d00(param_2);
  cVar3 = FUN_005e4d04(param_2);
  bVar4 = FUN_005e4d0a(param_2);
  if (puVar5 != (undefined4 *)0x0) {
    if ((ushort)bVar2 < *(ushort *)((int)puVar5 + 0x406)) {
      FUN_0043c0e4(&uStack_2c,8,0);
      uStack_2c = *puVar5;
      uStack_28 = puVar5[(uint)bVar2 * 0x22 + 0x102];
      APP_PbTerminalTxEncodeQueryReply(&uStack_2c);
      iVar6 = FUN_0043d0ce();
      if (iVar6 << 0x1e < 0) {
        FUN_0043d574(3,PTR_s_terminal_ui_005e6b90,PTR_s_D__01_workspace_s200_ap510b_iar__005e6b8c,
                     PTR_s_terminal_ui_action_query_reply_005e7284,0x662,
                     PTR_s_query_reply__query_id__d__option_005e7280,uStack_2c,uStack_28,bVar2);
      }
      iVar6 = FUN_0043d0ce();
      if (-1 < iVar6 << 0x1f) {
        iVar6 = FUN_0043d0ce();
        if (-1 < iVar6 << 0x1d) goto LAB_005e6a72;
      }
      compress_log_output(0xcc00000,PTR_s__terminal_ui_query_reply__query__005e7288,
                          PTR_s__terminal_ui_query_reply__query__005e7288,uStack_2c,uStack_28,bVar2)
      ;
    }
  }
LAB_005e6a72:
  FUN_005ebbc6();
  td_session_struct_clear();
  if ((((*(int *)(iVar1 + 0x1cc) != 0) && (*(int *)(iVar1 + 0x1d0) != 0)) &&
      (*(int *)(iVar1 + 0x1d4) != 0)) && (*(int *)(iVar1 + 0x1dc) != 0)) {
    FUN_0043dfa4(*(undefined4 *)(iVar1 + 0x1cc),1);
    FUN_005ea30c();
    FUN_005e482a(*(undefined4 *)(iVar1 + 0x1d0),_DAT_005e728c,6,100);
    if (cVar3 == '\0') {
      FUN_0049942e(*(undefined4 *)(iVar1 + 0x1d4),PTR_s_Thinking____005e729c);
      *_DAT_005e7298 = 0;
    }
    else {
      FUN_005ea2a8(bVar4);
      *_DAT_005e7290 = bVar4;
      *_DAT_005e7294 = (uint)bVar4;
      *_DAT_005e7298 = 1;
    }
    FUN_0049942e(*(undefined4 *)(iVar1 + 0x1dc),PTR_s__Tap___hold_to_stop_response__005e72a0);
    FUN_005e4902();
  }
  return 0;
}

