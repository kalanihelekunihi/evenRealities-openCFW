
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int FUN_0049e68c(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  undefined1 uVar2;
  int iVar3;
  uint uVar4;
  int iVar5;
  undefined4 uStack_70;
  undefined4 uStack_6c;
  undefined1 auStack_68 [3];
  char cStack_65;
  undefined1 auStack_64 [4];
  int iStack_60;
  int iStack_54;
  int iStack_50;
  int iStack_4c;
  int iStack_48;
  undefined1 auStack_3c [40];
  
  if (param_1 == 2) {
    *_DAT_0049ea3c = 0;
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      uStack_6c = PTR_s_Dashboard_ui_event_handler_UI_EV_0049ea80;
      uStack_70 = 0x443;
      FUN_0043d574(4,PTR_s_dashboard_0049ea68,PTR_s_D__01_workspace_s200_ap510b_iar__0049ea64,
                   PTR_s_Dashboard_ui_event_handler_0049ea84);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x10000000,PTR_s__dashboard_Dashboard_ui_event_ha_0049ea88,
                          PTR_s__dashboard_Dashboard_ui_event_ha_0049ea88);
    }
    iVar3 = settings_get_config();
    *(undefined4 *)(iVar3 + 0x34) = 1;
    setting_notify_device_status_to_app();
    FUN_0049c09a();
    quicklist_data_mutex_init();
    health_data_mutex_init();
    FUN_004ffe14();
    cb_ring_battery_forwarder(param_4);
    *(undefined4 *)(_DAT_0049ea8c + 4) = *_DAT_0049ea30;
    iVar3 = FUN_0045a568();
    if (iVar3 == 1) {
      CB_BLE_STATUS_RegisterCallback(PTR_FUN_0049e486_1_0049ea90);
      CB_ANCC_RegisterMsgCountCallback(PTR_FUN_0049c2b0_1_0049ea94);
      CB_CHG_RegisterBatInfoCallback(PTR_FUN_0049c3d8_1_0049ea98);
      CB_RING_BAT_RegisterCallback(PTR_FUN_0049c5c4_1_0049ea9c);
      FUN_0049c25a();
      service_time_current_calendar_get(auStack_3c);
      uVar4 = service_time_current_epoch_get();
      FUN_0043c0e4(auStack_68,4,0);
      FUN_0043c0e4(auStack_68,4,0);
      auStack_68[0] = 7;
      cStack_65 = (char)(uVar4 / 0xe10) + (char)((uVar4 / 0xe10) / 0x18) * -0x18;
      FUN_0045aaca(1,auStack_68,4,400);
      iVar3 = FUN_0047121c();
      if (iVar3 == 0xff55) {
        *_DAT_0049eaa0 = 0;
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          uStack_6c = _DAT_0049eaa4;
          uStack_70 = 0x46e;
          FUN_0043d574(3,PTR_s_dashboard_0049ea68,PTR_s_D__01_workspace_s200_ap510b_iar__0049ea64,
                       PTR_s_Dashboard_ui_event_handler_0049ea84);
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          compress_log_output(0xc000000,_DAT_0049eaa8,_DAT_0049eaa8);
        }
      }
      else {
        *_DAT_0049eaa0 = 1;
      }
      piVar1 = _DAT_0049ea48;
      *_DAT_0049ea48 = iVar3 * 0x41;
      *_DAT_0049ea44 = *piVar1;
      *_DAT_0049eaac = '\0';
      *_DAT_0049ea40 = '\0';
    }
    return 0;
  }
  if (param_1 == 3) {
    iVar3 = FUN_004e8dec(param_2,param_3);
    return iVar3;
  }
  if (param_1 == 4) {
    service_time_current_calendar_get(auStack_64);
    iVar3 = FUN_0045a568();
    piVar1 = _DAT_0049ea48;
    if (iVar3 == 1) {
      if ((((*_DAT_0049ea40 == '\0') && (*_DAT_0049eab0 == 0)) &&
          (*_DAT_0049ea48 = *_DAT_0049ea48 + -1, *piVar1 < 1)) &&
         ((*_DAT_0049eaac == '\0' && (*_DAT_0049eaa0 == 1)))) {
        *_DAT_0049eaac = '\x01';
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          uStack_6c = _DAT_0049eab4;
          uStack_70 = 0x484;
          FUN_0043d574(3,PTR_s_dashboard_0049ea68,PTR_s_D__01_workspace_s200_ap510b_iar__0049ea64,
                       PTR_s_Dashboard_ui_event_handler_0049ea84);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0xc000000,_DAT_0049eab8,_DAT_0049eab8);
        }
        FUN_0043c0e4(&uStack_70,2,0);
        FUN_0043c0e4(&uStack_70,2,0);
        uStack_70 = CONCAT31(uStack_70._1_3_,8);
        FUN_00464bb2(1,&uStack_70,2,0);
      }
      if ((*_DAT_0049eabc != iStack_4c) || (*_DAT_0049eac0 != iStack_48)) {
        *_DAT_0049eabc = iStack_4c;
        *_DAT_0049eac0 = iStack_48;
        iVar3 = FUN_0045a568();
        if (iVar3 == 1) {
          uVar4 = service_time_current_epoch_get();
          FUN_0043c0e4(&uStack_6c,4,0);
          FUN_0043c0e4(&uStack_6c,4,0);
          uStack_6c = (undefined *)
                      CONCAT13((char)(uVar4 / 0xe10) + (char)((uVar4 / 0xe10) / 0x18) * -0x18,
                               CONCAT12((undefined1)iStack_48,CONCAT11((undefined1)iStack_4c,7)));
          FUN_00464bb2(1,&uStack_6c,4,0);
        }
      }
      FUN_004efa78();
    }
    if (((*_DAT_0049eac4 != iStack_54) || (*_DAT_0049eac8 != iStack_50)) ||
       (*_DAT_0049eacc != iStack_60)) {
      *_DAT_0049eac4 = iStack_54;
      *_DAT_0049eac8 = iStack_50;
      *_DAT_0049eacc = iStack_60;
      uVar2 = FUN_00466500();
      dashboard_watchface_manager_call_10(iStack_60,iStack_54,iStack_50,uVar2);
    }
    FUN_004e923c(param_2,param_3);
    return 0;
  }
  if (param_1 == 5) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      uStack_6c = _DAT_0049ead0;
      uStack_70 = 0x4af;
      FUN_0043d574(4,PTR_s_dashboard_0049ea68,PTR_s_D__01_workspace_s200_ap510b_iar__0049ea64,
                   PTR_s_Dashboard_ui_event_handler_0049ea84);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x10000000,_DAT_0049ead4,_DAT_0049ead4);
    }
    iVar3 = FUN_0045a568();
    if (iVar3 == 1) {
      CB_BLE_STATUS_UnregisterCallback(PTR_FUN_0049e486_1_0049ea90);
      CB_ANCC_UnregisterMsgCountCallback(PTR_FUN_0049c2b0_1_0049ea94);
      CB_CHG_UnregisterBatInfoCallback(PTR_FUN_0049c3d8_1_0049ea98);
      iVar3 = settings_get_config();
      *(undefined4 *)(iVar3 + 0x34) = 0;
      setting_notify_device_status_to_app();
    }
    FUN_00501066(0);
    FUN_004e8000();
    *_DAT_0049ea3c = 0;
    return 0;
  }
  return param_1;
}

