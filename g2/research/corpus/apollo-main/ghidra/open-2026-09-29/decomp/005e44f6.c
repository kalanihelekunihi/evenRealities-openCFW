
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 Terminal_ui_event_handler(uint param_1,int param_2,uint param_3,undefined4 param_4)

{
  undefined4 *puVar1;
  int iVar2;
  uint uStack_20;
  undefined4 uStack_1c;
  
  uStack_20 = param_3;
  uStack_1c = param_4;
  FUN_0043c0e4(&uStack_20,8,0,param_4,param_1,param_2);
  terminal_action_lock();
  if (param_1 == 2) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(3,DAT_005e477c,DAT_005e4778,PTR_s_Terminal_ui_event_handler_005e47a0,0xb0,
                   PTR_s_terminal_display_startup_005e479c);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0xc000000,PTR_s__terminal_terminal_display_start_005e47a4,
                          PTR_s__terminal_terminal_display_start_005e47a4);
    }
    ble_state_skip_manual_start(0);
    CB_BLE_STATUS_RegisterCallback(PTR_semantic_terminal_runtime_event_callback_1_005e47a8);
    FUN_005e716c(param_4);
    FUN_005e7b74(1,0);
    puVar1 = DAT_005e4784;
    *(undefined4 *)(_DAT_005e47ac + 4) = *DAT_005e4784;
    FUN_0058c238(*puVar1,0xfa,0);
    terminal_display_exit_sync();
  }
  else if (1 < param_1) {
    if (param_1 == 4) {
      FUN_005e8008();
    }
    else if (param_1 < 4) {
      if ((param_2 != 0) && (7 < param_3)) {
        FUN_00439be4(&uStack_20,param_2,8);
        FUN_005e7b74(uStack_20 & 0xff,uStack_1c);
      }
    }
    else if (param_1 == 5) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(3,DAT_005e477c,DAT_005e4778,PTR_s_Terminal_ui_event_handler_005e47a0,0xc3,
                     PTR_s_terminal_display_exit_005e47b0);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0xc000000,PTR_s__terminal_terminal_display_exit_005e47b4,
                            PTR_s__terminal_terminal_display_exit_005e47b4);
      }
      terminal_display_exit_sync();
      FUN_005e720c();
    }
  }
  terminal_action_unlock();
  return 0;
}

