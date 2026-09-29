
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8
Onboarding_ui_event_handler(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  
  if (param_1 == 2) {
    uVar3 = param_4;
    iVar1 = FUN_0043d0ce(param_2,param_3);
    uVar2 = param_2;
    if (iVar1 << 0x1e < 0) {
      uVar2 = 0x23b;
      FUN_0043d574(4,PTR_s_onboarding_004690e0,PTR_s_D__01_workspace_s200_ap510b_iar__004690dc,
                   PTR_s_Onboarding_ui_event_handler_00469144,0x23b,
                   PTR_s_Onboarding_ui_event_handler_UI_E_00469140,uVar3);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10000000,PTR_s__onboarding_Onboarding_ui_event__00469148,
                          PTR_s__onboarding_Onboarding_ui_event__00469148);
    }
    *_DAT_00469124 = 0;
    onboarding_process_mutex_init();
    func_0x004aba58(param_4);
    *(undefined4 *)(_DAT_0046914c + 4) = *_DAT_00469118;
    iVar1 = FUN_0045a568();
    if (iVar1 == 1) {
      FUN_0043c0e4(DAT_00469100,3,0);
      iVar1 = CB_BLE_STATUS_RegisterCallback(PTR_onboarding_ble_status_callback_1_00469150);
      if (iVar1 == 0) {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          uVar2 = 0x247;
          FUN_0043d574(1,PTR_s_onboarding_004690e0,PTR_s_D__01_workspace_s200_ap510b_iar__004690dc,
                       PTR_s_Onboarding_ui_event_handler_00469144,0x247,
                       PTR_s_Onboarding__failed_to_register_B_0046915c);
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0x4000000,PTR_s__onboarding_Onboarding__failed_t_00469160,
                              PTR_s__onboarding_Onboarding__failed_t_00469160);
        }
      }
      else {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          uVar2 = 0x245;
          FUN_0043d574(4,PTR_s_onboarding_004690e0,PTR_s_D__01_workspace_s200_ap510b_iar__004690dc,
                       PTR_s_Onboarding_ui_event_handler_00469144,0x245,
                       PTR_s_Onboarding__BLE_status_callback_r_00469154);
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0x10000000,PTR_s__onboarding_Onboarding__BLE_stat_00469158,
                              PTR_s__onboarding_Onboarding__BLE_stat_00469158);
        }
      }
    }
    param_2 = 0;
  }
  else {
    uVar2 = param_2;
    if (param_1 == 3) {
      param_2 = ui_onboarding_main_sub_004A99D0();
    }
    else if (param_1 == 4) {
      ui_onboarding_main_sub_004A9C0C();
      param_2 = 0;
    }
    else if (param_1 == 5) {
      iVar1 = FUN_0043d0ce(param_2,param_3);
      uVar2 = param_2;
      if (iVar1 << 0x1e < 0) {
        uVar2 = 0x252;
        FUN_0043d574(3,PTR_s_onboarding_004690e0,PTR_s_D__01_workspace_s200_ap510b_iar__004690dc,
                     PTR_s_Onboarding_ui_event_handler_00469144,0x252,
                     PTR_s_Onboarding_ui_event_handler_UI_E_00469164);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0xc000000,PTR_s__onboarding_Onboarding_ui_event__00469168,
                            PTR_s__onboarding_Onboarding_ui_event__00469168);
      }
      iVar1 = FUN_0045a568();
      if (iVar1 == 1) {
        CB_BLE_STATUS_UnregisterCallback(PTR_onboarding_ble_status_callback_1_00469150);
      }
      func_0x004abba4();
      *_DAT_00469124 = 0;
      param_2 = 0;
    }
  }
  return CONCAT44(uVar2,param_2);
}

