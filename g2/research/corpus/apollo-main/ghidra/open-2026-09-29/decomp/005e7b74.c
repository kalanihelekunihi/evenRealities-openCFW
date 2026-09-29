
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_005e7b74(byte param_1)

{
  char cVar1;
  int iVar2;
  int iVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  undefined1 *puVar6;
  
  iVar2 = _DAT_005e7e0c;
  if (param_1 < 0x28) {
    if (*(byte *)(_DAT_005e7e0c + 0x275) < 0xd) {
      puVar6 = PTR_DAT_005e7e80 + (uint)param_1 * 8 + (uint)*(byte *)(_DAT_005e7e0c + 0x275) * 0x140
      ;
      if (*(int *)(puVar6 + 4) == 0) {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          uVar4 = FUN_005e7b2a(param_1);
          uVar5 = FUN_005e7b10(*(undefined1 *)(iVar2 + 0x275));
          FUN_0043d574(2,PTR_s_terminal_ui_005e7e1c,PTR_s_D__01_workspace_s200_ap510b_iar__005e7e18,
                       PTR_s_terminal_ui_fsm_handler_005e7e70,0x981,
                       PTR_s_terminal_ui_no_action__state__d__005e7e84,
                       *(undefined1 *)(iVar2 + 0x275),uVar5,param_1,uVar4);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          uVar4 = FUN_005e7b2a(param_1);
          uVar5 = FUN_005e7b10(*(undefined1 *)(iVar2 + 0x275));
          compress_log_output(0x9000000,PTR_s__terminal_ui_terminal_ui_no_acti_005e7e88,
                              PTR_s__terminal_ui_terminal_ui_no_acti_005e7e88,
                              *(undefined1 *)(iVar2 + 0x275),uVar5,param_1,uVar4);
        }
      }
      else {
        cVar1 = *(char *)(_DAT_005e7e0c + 0x275);
        iVar3 = (**(code **)(puVar6 + 4))(*(undefined1 *)(_DAT_005e7e0c + 0x275));
        if (iVar3 == -1) {
          iVar2 = FUN_0043d0ce();
          if (iVar2 << 0x1e < 0) {
            FUN_0043d574(1,PTR_s_terminal_ui_005e7e1c,
                         PTR_s_D__01_workspace_s200_ap510b_iar__005e7e18,
                         PTR_s_terminal_ui_fsm_handler_005e7e70,0x988,
                         PTR_s_terminal_ui_action_failed__event_005e7e8c,param_1);
          }
          iVar2 = FUN_0043d0ce();
          if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
            compress_log_output(0x4400000,PTR_s__terminal_ui_terminal_ui_action_f_005e7e90,
                                PTR_s__terminal_ui_terminal_ui_action_f_005e7e90,param_1);
          }
        }
        else {
          if (iVar3 == 0) {
            *(undefined1 *)(iVar2 + 0x275) = *puVar6;
          }
          else {
            if ((iVar3 < 1) || (0xc < (iVar3 + 0xffU & 0xff))) {
              iVar2 = FUN_0043d0ce();
              if (iVar2 << 0x1e < 0) {
                FUN_0043d574(1,PTR_s_terminal_ui_005e7e1c,
                             PTR_s_D__01_workspace_s200_ap510b_iar__005e7e18,
                             PTR_s_terminal_ui_fsm_handler_005e7e70,0x991,
                             PTR_s_terminal_ui_action_result_invali_005e7e9c,param_1,iVar3);
              }
              iVar2 = FUN_0043d0ce();
              if ((-1 < iVar2 << 0x1f) && (iVar2 = FUN_0043d0ce(), -1 < iVar2 << 0x1d)) {
                return;
              }
              compress_log_output(0x4800000,PTR_s__terminal_ui_terminal_ui_action_r_005e7ea0,
                                  PTR_s__terminal_ui_terminal_ui_action_r_005e7ea0,param_1,iVar3);
              return;
            }
            *(char *)(iVar2 + 0x275) = (char)iVar3 + -1;
          }
          if (cVar1 != *(char *)(iVar2 + 0x275)) {
            iVar3 = FUN_0043d0ce();
            if (iVar3 << 0x1e < 0) {
              uVar4 = FUN_005e7b10(*(undefined1 *)(iVar2 + 0x275));
              uVar5 = FUN_005e7b10(cVar1);
              FUN_0043d574(3,PTR_s_terminal_ui_005e7e1c,
                           PTR_s_D__01_workspace_s200_ap510b_iar__005e7e18,
                           PTR_s_terminal_ui_fsm_handler_005e7e70,0x997,
                           PTR_s_terminal_ui_state___d__s___>__d__005e7e94,cVar1,uVar5,
                           *(undefined1 *)(iVar2 + 0x275),uVar4);
            }
            iVar3 = FUN_0043d0ce();
            if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
              uVar4 = FUN_005e7b10(*(undefined1 *)(iVar2 + 0x275));
              uVar5 = FUN_005e7b10(cVar1);
              compress_log_output(0xd000000,PTR_s__terminal_ui_terminal_ui_state____005e7e98,
                                  PTR_s__terminal_ui_terminal_ui_state____005e7e98,cVar1,uVar5,
                                  *(undefined1 *)(iVar2 + 0x275),uVar4);
            }
          }
        }
      }
    }
    else {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(1,PTR_s_terminal_ui_005e7e1c,PTR_s_D__01_workspace_s200_ap510b_iar__005e7e18,
                     PTR_s_terminal_ui_fsm_handler_005e7e70,0x97a,
                     PTR_s_terminal_ui_state_invalid___d_005e7e78,*(undefined1 *)(iVar2 + 0x275));
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x4400000,PTR_s__terminal_ui_terminal_ui_state_i_005e7e7c,
                            PTR_s__terminal_ui_terminal_ui_state_i_005e7e7c,
                            *(undefined1 *)(iVar2 + 0x275));
      }
    }
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,PTR_s_terminal_ui_005e7e1c,PTR_s_D__01_workspace_s200_ap510b_iar__005e7e18,
                   PTR_s_terminal_ui_fsm_handler_005e7e70,0x975,
                   PTR_s_terminal_ui_event_invalid___d_005e7e6c,param_1);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4400000,PTR_s__terminal_ui_terminal_ui_event_i_005e7e74,
                          PTR_s__terminal_ui_terminal_ui_event_i_005e7e74,param_1);
    }
  }
  return;
}

