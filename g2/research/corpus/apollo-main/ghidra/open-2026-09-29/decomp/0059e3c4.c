
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4
translate_ui_0059e3c4(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined *puVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 uStack_10;
  undefined4 uStack_c;
  
  uStack_10 = param_3;
  uStack_c = param_4;
  iVar2 = UX_GetSystemBLEStatus();
  if (iVar2 == 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,DAT_0059e640,DAT_0059e63c,PTR_s_translate_ui_action_display_load_0059e6a0,0x275
                   ,PTR_s_BLE_disconnected__show_exit_prom_0059e69c);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__translate_ui_BLE_disconnected__s_0059e6a4,
                          PTR_s__translate_ui_BLE_disconnected__s_0059e6a4);
    }
    puVar1 = PTR_s_ID_GENERAL_BLUETOOTH_DISCONNECT_0059e664;
    uVar3 = FUN_00460084(PTR_s_ID_GENERAL_BLUETOOTH_DISCONNECT_0059e664);
    uVar3 = FUN_0045fffe(puVar1,uVar3);
    common_exit_prompt_show(*_DAT_0059e668,uVar3,5,0,5000);
    uVar3 = 0xffffffff;
  }
  else {
    uStack_10 = CONCAT22(uStack_10._2_2_,*(undefined2 *)PTR_DAT_0059e6a8);
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(3,DAT_0059e640,DAT_0059e63c,PTR_s_translate_ui_action_display_load_0059e6a0,0x27e
                   ,PTR_s_notify_app_to_start_0059e6ac);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0xc000000,PTR_s__translate_ui_notify_app_to_star_0059e6b0,
                          PTR_s__translate_ui_notify_app_to_star_0059e6b0);
    }
    APP_PbTranslateTxEncodeNotify(&uStack_10);
    uVar3 = 0;
  }
  return uVar3;
}

