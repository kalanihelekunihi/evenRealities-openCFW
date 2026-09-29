
void FUN_005b1724(byte param_1,undefined4 param_2)

{
  byte bVar1;
  byte *pbVar2;
  int iVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  byte *pbVar6;
  
  if (param_1 < 0x15) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      uVar4 = FUN_005b16fc(param_1);
      FUN_0043d574(3,DAT_005b1ae0,DAT_005b1adc,PTR_s_conversate_ui_fsm_handler_005b1b08,0x24e,
                   PTR_s_UI_event___d__s__005b1b10,param_1,uVar4);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      uVar4 = FUN_005b16fc(param_1);
      compress_log_output(0xc800000,PTR_s__conversate_ui_UI_event___d__s__005b1b14,
                          PTR_s__conversate_ui_UI_event___d__s__005b1b14,param_1,uVar4);
    }
    pbVar2 = DAT_005b1ae8;
    if (*DAT_005b1ae8 < 7) {
      pbVar6 = PTR_DAT_005b1b20 + (uint)param_1 * 8 + (uint)*DAT_005b1ae8 * 0xa8;
      if (*(int *)(pbVar6 + 4) == 0) {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          uVar4 = FUN_005b16fc(param_1);
          uVar5 = FUN_005b16dc(*pbVar2);
          FUN_0043d574(2,DAT_005b1ae0,DAT_005b1adc,PTR_s_conversate_ui_fsm_handler_005b1b08,0x259,
                       PTR_s_UI_current_state__d__s__no_match_005b1b24,*pbVar2,uVar5,param_1,uVar4);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          uVar4 = FUN_005b16fc(param_1);
          uVar5 = FUN_005b16dc(*pbVar2);
          compress_log_output(0x9000000,PTR_s__conversate_ui_UI_current_state__005b1b28,
                              PTR_s__conversate_ui_UI_current_state__005b1b28,*pbVar2,uVar5,param_1,
                              uVar4);
        }
      }
      else {
        iVar3 = (**(code **)(pbVar6 + 4))(*DAT_005b1ae8,param_2);
        if (iVar3 == 0) {
          bVar1 = *pbVar2;
          if (bVar1 != *pbVar6) {
            iVar3 = FUN_0043d0ce();
            if (iVar3 << 0x1e < 0) {
              uVar4 = FUN_005b16dc(*pbVar6);
              uVar5 = FUN_005b16dc(*pbVar2);
              FUN_0043d574(3,DAT_005b1ae0,DAT_005b1adc,PTR_s_conversate_ui_fsm_handler_005b1b08,
                           0x263,PTR_s_UI_state___d__s___>___d__s__005b1b2c,*pbVar2,uVar5,*pbVar6,
                           uVar4);
            }
            iVar3 = FUN_0043d0ce();
            if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
              uVar4 = FUN_005b16dc(*pbVar6);
              uVar5 = FUN_005b16dc(*pbVar2);
              compress_log_output(0xd000000,PTR_s__conversate_ui_UI_state___d__s____005b1b30,
                                  PTR_s__conversate_ui_UI_state___d__s____005b1b30,*pbVar2,uVar5,
                                  *pbVar6,uVar4);
            }
          }
          *pbVar2 = *pbVar6;
          FUN_005b3d86(bVar1,*pbVar6);
        }
        else {
          iVar3 = FUN_0043d0ce();
          if (iVar3 << 0x1e < 0) {
            FUN_0043d574(1,DAT_005b1ae0,DAT_005b1adc,PTR_s_conversate_ui_fsm_handler_005b1b08,0x268,
                         PTR_s_UI_transition_action_failed_005b1b34);
          }
          iVar3 = FUN_0043d0ce();
          if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
            compress_log_output(0x4000000,PTR_s__conversate_ui_UI_transition_act_005b1b38,
                                PTR_s__conversate_ui_UI_transition_act_005b1b38);
          }
        }
      }
    }
    else {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(1,DAT_005b1ae0,DAT_005b1adc,PTR_s_conversate_ui_fsm_handler_005b1b08,0x251,
                     PTR_s_UI_current_state_is_invalid___d_005b1b18,*pbVar2);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x4400000,PTR_s__conversate_ui_UI_current_state_i_005b1b1c,
                            PTR_s__conversate_ui_UI_current_state_i_005b1b1c,*pbVar2);
      }
    }
  }
  else {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(1,DAT_005b1ae0,DAT_005b1adc,PTR_s_conversate_ui_fsm_handler_005b1b08,0x24a,
                   PTR_s_UI_event_is_invalid___d_005b1b04,param_1);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x4400000,PTR_s__conversate_ui_UI_event_is_inval_005b1b0c,
                          PTR_s__conversate_ui_UI_event_is_inval_005b1b0c,param_1);
    }
  }
  return;
}

