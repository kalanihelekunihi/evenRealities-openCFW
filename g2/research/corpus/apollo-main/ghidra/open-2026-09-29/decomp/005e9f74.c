
undefined4 terminal_action_session_id_changed(int *param_1)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  
  if (param_1 == (int *)0x0) {
    uVar2 = 0xffffffff;
  }
  else {
    if (*param_1 == 0) {
      *(undefined4 *)(DAT_005ea01c + 0x29c) = 0;
    }
    else {
      iVar3 = osKernelGetTickCount();
      iVar1 = DAT_005ea01c;
      if (iVar3 == 0) {
        iVar3 = 1;
      }
      *(int *)(DAT_005ea01c + 0x29c) = iVar3;
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(3,PTR_s_terminal_pb_005ea1f4,PTR_s_D__01_workspace_s200_ap510b_iar__005ea1f0,
                     PTR_s_terminal_action_session_id_chang_005ea1ec,0x31b,
                     PTR_s_block_input_during_session_switc_005ea1e8,*param_1,
                     *(undefined4 *)(iVar1 + 0x29c));
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0xc800000,PTR_s__terminal_pb_block_input_during_s_005ea1f8,
                            PTR_s__terminal_pb_block_input_during_s_005ea1f8,*param_1,
                            *(undefined4 *)(iVar1 + 0x29c));
      }
    }
    terminal_apply_session_id_changed(*param_1,1);
    uVar2 = 0;
  }
  return uVar2;
}

