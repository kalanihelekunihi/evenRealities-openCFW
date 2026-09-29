
void onboarding_ble_status_callback
               (undefined4 param_1,char *param_2,undefined4 param_3,undefined4 param_4)

{
  char cVar1;
  undefined1 *puVar2;
  undefined1 *puVar3;
  int iVar4;
  undefined1 auStack_10 [4];
  undefined4 uStack_c;
  
  uStack_c = param_4;
  if (param_2 == (char *)0x0) {
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      FUN_0043d574(1,PTR_s_onboarding_004690e0,PTR_s_D__01_workspace_s200_ap510b_iar__004690dc,
                   PTR_s_onboarding_ble_status_callback_004690d8,0x197,
                   PTR_s_Onboarding__invalid_ble_status_d_004690d4);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__onboarding_Onboarding__invalid_b_004690e4);
    }
  }
  else {
    cVar1 = *param_2;
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      FUN_0043d574(3,PTR_s_onboarding_004690e0,PTR_s_D__01_workspace_s200_ap510b_iar__004690dc,
                   PTR_s_onboarding_ble_status_callback_004690d8,0x19c,
                   PTR_s_Onboarding__ble_status_changed_t_004690e8,cVar1);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0xc400000,PTR_s__onboarding_Onboarding__ble_stat_004690ec,
                          PTR_s__onboarding_Onboarding__ble_stat_004690ec,cVar1);
    }
    iVar4 = FUN_004434d0(0x10);
    puVar2 = DAT_00469100;
    if (iVar4 == 1) {
      if (cVar1 == '\0') {
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          FUN_0043d574(3,PTR_s_onboarding_004690e0,PTR_s_D__01_workspace_s200_ap510b_iar__004690dc,
                       PTR_s_onboarding_ble_status_callback_004690d8,0x1a9,
                       PTR_s_Onboarding__BLE_disconnected__sa_004690f8,*DAT_00468c24,DAT_00468c24[1]
                      );
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0xc800000,PTR_s__onboarding_Onboarding__BLE_disc_004690fc,
                              PTR_s__onboarding_Onboarding__BLE_disc_004690fc,*DAT_00468c24,
                              DAT_00468c24[1]);
        }
        puVar3 = DAT_00469100;
        puVar2 = DAT_00468c24;
        *DAT_00469100 = *DAT_00468c24;
        puVar3[1] = puVar2[1];
        puVar3[2] = 1;
        auStack_10[0] = 0xf;
        FUN_00465480(0x10,auStack_10,1,0,5);
      }
      else if ((cVar1 == '\x01') && (DAT_00469100[2] != '\0')) {
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          FUN_0043d574(3,PTR_s_onboarding_004690e0,PTR_s_D__01_workspace_s200_ap510b_iar__004690dc,
                       PTR_s_onboarding_ble_status_callback_004690d8,0x1b8,
                       PTR_s_Onboarding__BLE_reconnected__res_00469104,*puVar2,puVar2[1]);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0xc800000,PTR_s__onboarding_Onboarding__BLE_reco_00469108,
                              PTR_s__onboarding_Onboarding__BLE_reco_00469108,*puVar2,puVar2[1]);
        }
        puVar2[2] = 0;
        RPC_OnboardingProcessSyncToPeer();
      }
    }
    else {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        FUN_0043d574(4,PTR_s_onboarding_004690e0,PTR_s_D__01_workspace_s200_ap510b_iar__004690dc,
                     PTR_s_onboarding_ble_status_callback_004690d8,0x1a0,
                     PTR_s_Onboarding__app_not_running__ign_004690f0);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x10000000,PTR_s__onboarding_Onboarding__app_not_r_004690f4,
                            PTR_s__onboarding_Onboarding__app_not_r_004690f4);
      }
    }
  }
  return;
}

