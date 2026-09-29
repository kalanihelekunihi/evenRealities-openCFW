
void terminal_log_session_list_items(int param_1)

{
  int iVar1;
  undefined4 uVar2;
  uint uVar3;
  uint uVar4;
  
  if (param_1 != 0) {
    uVar3 = (uint)*(ushort *)(param_1 + 8);
    if (10 < uVar3) {
      uVar3 = 10;
    }
    for (uVar4 = 0; uVar4 < uVar3; uVar4 = uVar4 + 1) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        uVar2 = semantic_terminal_session_status_name
                          (*(undefined1 *)(uVar4 * 0x88 + param_1 + 0x92));
        FUN_0043d574(3,PTR_s_terminal_pb_005e9f68,PTR_s_D__01_workspace_s200_ap510b_iar__005e9f64,
                     PTR_s_terminal_log_session_list_items_005ea1b4,0x2af,
                     PTR_s_session__lu__lu__status__d__s____005ea1b0,uVar4,
                     *(undefined4 *)(param_1 + uVar4 * 0x88 + 0xc),
                     *(undefined1 *)(uVar4 * 0x88 + param_1 + 0x92),uVar2,
                     uVar4 * 0x88 + param_1 + 0x12);
      }
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1f < 0) {
LAB_005e9c06:
        uVar2 = semantic_terminal_session_status_name
                          (*(undefined1 *)(uVar4 * 0x88 + param_1 + 0x92));
        compress_log_output(0xd400000,PTR_s__terminal_pb_session__lu__lu__st_005ea1b8,
                            PTR_s__terminal_pb_session__lu__lu__st_005ea1b8,uVar4,
                            *(undefined4 *)(param_1 + uVar4 * 0x88 + 0xc),
                            *(undefined1 *)(uVar4 * 0x88 + param_1 + 0x92),uVar2,
                            uVar4 * 0x88 + param_1 + 0x12);
      }
      else {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1d < 0) goto LAB_005e9c06;
      }
    }
  }
  return;
}

