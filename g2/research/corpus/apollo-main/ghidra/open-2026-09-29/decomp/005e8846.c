
/* WARNING: Removing unreachable block (ram,0x005e8b18) */

undefined4 terminal_action_mode_sync(char *param_1)

{
  longlong lVar1;
  int iVar2;
  undefined4 uVar3;
  uint uVar4;
  undefined *puVar5;
  uint uVar6;
  uint uVar7;
  uint local_38;
  undefined *local_34;
  uint local_30;
  uint local_2c;
  char local_28 [4];
  uint local_24;
  uint local_20;
  undefined4 local_1c;
  undefined4 uStack_18;
  
  FUN_0043c0e4(local_28,2,0);
  uVar6 = 0;
  if (param_1 == (char *)0x0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      local_34 = PTR_s_terminal_mode_sync_is_null_005e931c;
      local_38 = 0x107;
      FUN_0043d574(1,DAT_005e8c18,DAT_005e8c14,PTR_s_terminal_action_mode_sync_005e9320);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__terminal_pb_terminal_mode_sync_i_005e9324,
                          PTR_s__terminal_pb_terminal_mode_sync_i_005e9324);
    }
    uVar3 = 0xffffffff;
  }
  else {
    uVar7 = (uint)(*param_1 == '\x02');
    uVar4 = settings_get_terminal_mode();
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      local_34 = PTR_s_mode_sync_recv__current_mode_ena_005e9328;
      local_38 = 0x10d;
      local_30 = uVar4;
      local_2c = uVar7;
      FUN_0043d574(3,DAT_005e8c18,DAT_005e8c14,PTR_s_terminal_action_mode_sync_005e9320);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      local_38 = uVar7;
      compress_log_output(0xc800000,PTR_s__terminal_pb_mode_sync_recv__cur_005e932c,
                          PTR_s__terminal_pb_mode_sync_recv__cur_005e932c,uVar4);
    }
    local_28[0] = *param_1;
    local_28[1] = 0;
    if (uVar7 == uVar4) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        local_34 = PTR_s_mode_sync_no_state_change__send_s_005e9330;
        local_38 = 0x113;
        FUN_0043d574(3,DAT_005e8c18,DAT_005e8c14,PTR_s_terminal_action_mode_sync_005e9320);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0xc000000,PTR_s__terminal_pb_mode_sync_no_state_c_005e9334,
                            PTR_s__terminal_pb_mode_sync_no_state_c_005e9334);
      }
      APP_PbTerminalTxEncodeStatusReply(local_28);
      uVar3 = 0;
    }
    else {
      input_msg_send_id4(uVar7);
      if (uVar7 == 1) {
        local_20 = 0;
        local_24 = 0;
        iVar2 = FUN_00443504(&local_20,&local_24);
        if (iVar2 == 0) {
          iVar2 = FUN_0043d0ce();
          if (iVar2 << 0x1e < 0) {
            local_2c = local_20;
            local_30 = local_24;
            local_34 = PTR_s_terminal_enter_running_apps__for_005e9338;
            local_38 = 0x11f;
            FUN_0043d574(3,DAT_005e8c18,DAT_005e8c14,PTR_s_terminal_action_mode_sync_005e9320);
          }
          iVar2 = FUN_0043d0ce();
          if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
            local_38 = local_20;
            compress_log_output(0xc800000,PTR_s__terminal_pb_terminal_enter_runn_005e933c,
                                PTR_s__terminal_pb_terminal_enter_runn_005e933c,local_24);
          }
          if (local_24 != 0) {
            iVar2 = FUN_0045a568();
            if (iVar2 == 1) {
              FUN_00464c36(local_24 & 0xffff,0,0,0);
            }
            uVar6 = 500;
          }
          if (local_20 != 0) {
            iVar2 = FUN_0045a568();
            if (iVar2 == 1) {
              FUN_00464c36(local_20 & 0xffff,0,0,0);
            }
            uVar6 = uVar6 + 500;
          }
        }
        else {
          iVar2 = FUN_0043d0ce();
          if (iVar2 << 0x1e < 0) {
            local_34 = PTR_s_terminal_mode_enter__getRunningA_005e9340;
            local_38 = 0x12d;
            FUN_0043d574(2,DAT_005e8c18,DAT_005e8c14,PTR_s_terminal_action_mode_sync_005e9320);
          }
          iVar2 = FUN_0043d0ce();
          if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
            compress_log_output(0x8000000,PTR_s__terminal_pb_terminal_mode_enter_005e9344,
                                PTR_s__terminal_pb_terminal_mode_enter_005e9344);
          }
        }
        td_state_reset();
        semantic_terminal_reset_output_tracking();
        CB_BLE_STATUS_RegisterCallback(PTR_semantic_terminal_runtime_event_callback_1_005e9348);
        *(undefined1 *)(DAT_005e8c04 + 0x274) = 1;
        if (uVar6 == 0) {
          uVar6 = 300;
        }
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          local_34 = PTR_s_terminal_mode_enter__startup_req_005e934c;
          local_38 = 0x135;
          local_30 = uVar6;
          FUN_0043d574(3,DAT_005e8c18,DAT_005e8c14,PTR_s_terminal_action_mode_sync_005e9320);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0xc400000,PTR_s__terminal_pb_terminal_mode_enter_005e9350,
                              PTR_s__terminal_pb_terminal_mode_enter_005e9350,uVar6);
        }
        osDelay(uVar6);
        settings_set_terminal_mode(1);
        iVar2 = FUN_0045a568();
        if (iVar2 == 1) {
          local_1c = *(undefined4 *)PTR_DAT_005e9354;
          uStack_18 = *(undefined4 *)(PTR_DAT_005e9354 + 4);
          FUN_0048eb32(DAT_005e9358,2,&local_1c);
        }
        iVar2 = FUN_0045a568();
        if (iVar2 == 1) {
          FUN_0045a8ee(0x30,0,0,0);
          iVar2 = osKernelGetTickCount();
          *DAT_005e935c = iVar2;
        }
      }
      else {
        iVar2 = osKernelGetTickCount();
        lVar1 = (ulonglong)(uint)(iVar2 - *DAT_005e935c) * 1000;
        puVar5 = (undefined *)FUN_0047cc60((int)lVar1,(int)((ulonglong)lVar1 >> 0x20),1000,0);
        iVar2 = FUN_0045a568();
        if (iVar2 == 1) {
          local_38 = *DAT_005e9360;
          local_34 = puVar5;
          FUN_0048eb32(DAT_005e9364,2,&local_38);
        }
        iVar2 = FUN_0045a568();
        if (iVar2 == 1) {
          local_30 = *DAT_005e9368;
          local_2c = DAT_005e9368[1];
          FUN_0048eb32(DAT_005e936c,2,&local_30);
        }
        settings_set_terminal_mode(uVar7);
        td_state_reset();
        semantic_terminal_reset_output_tracking();
        ble_param_reset_delayed_event(10000);
        CB_BLE_STATUS_UnregisterCallback(PTR_semantic_terminal_runtime_event_callback_1_005e9348);
        if (*(char *)(DAT_005e8c04 + 0x275) == '\0') {
          iVar2 = FUN_0043d0ce();
          if (iVar2 << 0x1e < 0) {
            local_34 = PTR_s_terminal_mode_exit__ui_already_c_005e9370;
            local_38 = 0x14f;
            FUN_0043d574(3,DAT_005e8c18,DAT_005e8c14,PTR_s_terminal_action_mode_sync_005e9320);
          }
          iVar2 = FUN_0043d0ce();
          if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
            compress_log_output(0xc000000,PTR_s__terminal_pb_terminal_mode_exit__005e9374,
                                PTR_s__terminal_pb_terminal_mode_exit__005e9374);
          }
          APP_PbTerminalTxEncodeStatusReply(local_28);
        }
        else {
          *(undefined1 *)(DAT_005e8c04 + 0x274) = 1;
          iVar2 = FUN_0045a568();
          if (iVar2 == 1) {
            FUN_00464c36(0x30,0,0,0);
          }
        }
      }
      uVar3 = 0;
    }
  }
  return uVar3;
}

