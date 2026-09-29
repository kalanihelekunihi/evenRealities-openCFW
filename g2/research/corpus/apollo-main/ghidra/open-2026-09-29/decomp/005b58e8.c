
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8
conversate_ui_ble_status_callback(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  undefined *puVar1;
  int iVar2;
  int iVar3;
  undefined4 uVar4;
  
  iVar2 = UX_GetSystemBLEStatus();
  iVar3 = DAT_005b5cc8;
  if (iVar2 == 0) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(1,DAT_005b5cd8,DAT_005b5cd4,PTR_s_conversate_ui_action_display_men_005b5cec,0x62,
                   PTR_s_BLE_disconnected__show_exit_prom_005b5ce8);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__conversate_ui_BLE_disconnected__005b5cf0,
                          PTR_s__conversate_ui_BLE_disconnected__005b5cf0);
    }
    puVar1 = PTR_s_ID_GENERAL_BLUETOOTH_DISCONNECT_005b5cf4;
    uVar4 = FUN_00460084(PTR_s_ID_GENERAL_BLUETOOTH_DISCONNECT_005b5cf4);
    uVar4 = FUN_0045fffe(puVar1,uVar4);
    param_3 = 5000;
    common_exit_prompt_show(*_DAT_005b5cf8,uVar4,0xb,0);
    uVar4 = 0xffffffff;
  }
  else {
    uVar4 = FUN_0043de82(*_DAT_005b5cf8);
    *(undefined4 *)(iVar3 + 4) = uVar4;
    FUN_0043f4c0(*(undefined4 *)(iVar3 + 4),0x240,0x120);
    FUN_0043f09a(*(undefined4 *)(iVar3 + 4),0,0);
    FUN_0044129e(*(undefined4 *)(iVar3 + 4),0,0);
    FUN_0044131c(*(undefined4 *)(iVar3 + 4),0,0);
    FUN_0044146a(*(undefined4 *)(iVar3 + 4),0,0);
    FUN_005b5720(*(undefined4 *)(iVar3 + 4),0,0);
    FUN_0043dfa4(*(undefined4 *)(iVar3 + 4),0x10);
    APP_PbConversateTxEncodePrepNoteListRequest();
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      param_3 = 0x71;
      FUN_0043d574(3,DAT_005b5cd8,DAT_005b5cd4,PTR_s_conversate_ui_action_display_men_005b5cec,0x71,
                   PTR_s_request_prep_note_list_005b5cfc);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0xc000000,PTR_s__conversate_ui_request_prep_note_005b5d00);
    }
    uVar4 = 0;
  }
  return CONCAT44(param_3,uVar4);
}

