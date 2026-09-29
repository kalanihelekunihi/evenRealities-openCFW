
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_00555758(undefined4 param_1,undefined *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  undefined4 uStack_18;
  undefined *puStack_14;
  undefined4 uStack_10;
  undefined4 uStack_c;
  
  uStack_18 = param_1;
  puStack_14 = param_2;
  uStack_10 = param_3;
  uStack_c = param_4;
  iVar1 = UX_GetSystemBLEStatus();
  iVar2 = _DAT_00556260;
  if (iVar1 == 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      puStack_14 = PTR_s_BLE_disconnected__show_exit_prom_00556264;
      uStack_18 = 0x4bf;
      FUN_0043d574(1,DAT_005558cc,DAT_005558c8,PTR_s_teleprompt_ui_action_display_men_00556268);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__teleprompt_ui_BLE_disconnected__0055626c,
                          PTR_s__teleprompt_ui_BLE_disconnected__0055626c);
    }
    *(undefined4 *)(_DAT_00556260 + 0x24) = 0;
    iVar2 = FUN_0045a568();
    if (iVar2 == 1) {
      uStack_18 = *(undefined4 *)PTR_DAT_00556270;
      puStack_14 = *(undefined **)(PTR_DAT_00556270 + 4);
      FUN_0048eb32(_DAT_00556274,2,&uStack_18);
    }
    uVar4 = _DAT_00556278;
    uVar3 = FUN_00460084(_DAT_00556278);
    uVar4 = FUN_0045fffe(uVar4,uVar3);
    uStack_18 = 5000;
    common_exit_prompt_show(*_DAT_0055627c,uVar4,6,0);
    uVar4 = 0xffffffff;
  }
  else {
    *(undefined4 *)(_DAT_00556260 + 0xc) = 0xffffffff;
    *(undefined4 *)(iVar2 + 8) = 0;
    *(undefined4 *)(iVar2 + 4) = 0;
    FUN_0058c238(*_DAT_0055627c,0xfa,0);
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      puStack_14 = _DAT_00556280;
      uStack_18 = 0x4cc;
      FUN_0043d574(4,DAT_005558cc,DAT_005558c8,PTR_s_teleprompt_ui_action_display_men_00556268);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10000000,_DAT_005563b8,_DAT_005563b8);
    }
    FUN_0043c0e4(&uStack_10,1,0);
    iVar2 = FUN_0045a568();
    if (iVar2 == 1) {
      APP_PbTxEncodeFileListRequest(&uStack_10);
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        puStack_14 = _DAT_005563bc;
        uStack_18 = 0x4d2;
        FUN_0043d574(3,DAT_005558cc,DAT_005558c8,PTR_s_teleprompt_ui_action_display_men_00556268);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0xc000000,PTR_s__teleprompt_ui_Request_file_list_00556484,
                            PTR_s__teleprompt_ui_Request_file_list_00556484);
      }
    }
    uVar4 = 0;
  }
  return uVar4;
}

