
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

uint FUN_00548f80(uint param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  undefined4 uVar2;
  int iVar3;
  undefined4 *puVar4;
  undefined1 uStack_64;
  undefined1 uStack_63;
  undefined1 uStack_58;
  undefined1 uStack_57;
  undefined1 uStack_56;
  undefined1 uStack_55;
  undefined1 uStack_54;
  undefined1 uStack_53;
  undefined1 uStack_4c;
  undefined1 uStack_4b;
  undefined1 uStack_4a;
  undefined1 uStack_49;
  undefined1 uStack_48;
  undefined1 uStack_47;
  undefined1 uStack_40;
  undefined1 uStack_3f;
  undefined1 uStack_3e;
  undefined1 uStack_3d;
  undefined1 uStack_3c;
  undefined1 uStack_3b;
  undefined1 uStack_34;
  undefined1 uStack_33;
  undefined1 uStack_32;
  undefined1 uStack_31;
  undefined1 uStack_30;
  undefined1 uStack_2f;
  undefined1 uStack_28;
  undefined1 uStack_27;
  undefined1 uStack_26;
  undefined1 uStack_25;
  undefined1 uStack_24;
  undefined1 uStack_23;
  undefined1 uStack_1c;
  undefined1 uStack_1b;
  undefined1 uStack_1a;
  undefined1 uStack_19;
  undefined1 uStack_18;
  undefined1 uStack_17;
  undefined4 uStack_10;
  
  uStack_10 = param_4;
  if (param_1 == 10) {
    bVar1 = FUN_0045a570();
    param_1 = (uint)bVar1;
    if (param_1 == 1) {
      FUN_0043c0e4(&uStack_1c,10,0);
      uStack_1c = 0xf2;
      uStack_1b = 10;
      uStack_1a = 0;
      uStack_19 = 0;
      uStack_18 = 0;
      uStack_17 = 0;
      uVar2 = FUN_00464bb2(8,&uStack_1c,6,0);
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(4,PTR_s_navigation_ui_005496f0,PTR_s_D__01_workspace_s200_ap510b_iar__005496ec,
                     PTR_s_NavigationInputEventHandler_00549b74,0x71e,
                     PTR_s_navigation_data_handler_send_inp_00549b70,uVar2);
      }
      iVar3 = FUN_0043d0ce();
      if (-1 < iVar3 << 0x1f) {
        iVar3 = FUN_0043d0ce();
        if (-1 < iVar3 << 0x1d) {
          return iVar3 << 0x1d;
        }
      }
      param_1 = compress_log_output(0x10400000,PTR_s__navigation_ui_navigation_data_h_00549b78,
                                    PTR_s__navigation_ui_navigation_data_h_00549b78,uVar2);
    }
  }
  else if (param_1 == 0x44) {
    if ((*_DAT_00549b7c == '\x02') && (*_DAT_00549b80 == '\x01')) {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(4,PTR_s_navigation_ui_005496f0,PTR_s_D__01_workspace_s200_ap510b_iar__005496ec,
                     PTR_s_NavigationInputEventHandler_00549b74,0x723,_DAT_00549b84);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x10000000,_DAT_00549b88,_DAT_00549b88);
      }
      param_1 = 0;
    }
    else if ((*_DAT_00549b7c == '\t') && (*_DAT_00549b8c == '\x01')) {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(4,PTR_s_navigation_ui_005496f0,PTR_s_D__01_workspace_s200_ap510b_iar__005496ec,
                     PTR_s_NavigationInputEventHandler_00549b74,0x728,
                     PTR_s_navigation_ui_state_is_NAVIGATIO_00549b90);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x10000000,PTR_s__navigation_ui_navigation_ui_sta_00549b94,
                            PTR_s__navigation_ui_navigation_ui_sta_00549b94);
      }
      param_1 = 0;
    }
    else {
      bVar1 = FUN_0045a570();
      param_1 = (uint)bVar1;
      if (param_1 == 1) {
        FUN_0043c0e4(&uStack_28,10,0);
        uStack_28 = 0xf2;
        uStack_27 = 0x44;
        uStack_26 = 0;
        uStack_25 = 0;
        uStack_24 = 0;
        uStack_23 = 0;
        uVar2 = FUN_00464bb2(8,&uStack_28,6,0);
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(4,PTR_s_navigation_ui_005496f0,
                       PTR_s_D__01_workspace_s200_ap510b_iar__005496ec,
                       PTR_s_NavigationInputEventHandler_00549b74,0x737,
                       PTR_s_navigation_data_handler_send_inp_00549b70,uVar2);
        }
        iVar3 = FUN_0043d0ce();
        if (-1 < iVar3 << 0x1f) {
          iVar3 = FUN_0043d0ce();
          if (-1 < iVar3 << 0x1d) {
            return iVar3 << 0x1d;
          }
        }
        param_1 = compress_log_output(0x10400000,PTR_s__navigation_ui_navigation_data_h_00549b78,
                                      PTR_s__navigation_ui_navigation_data_h_00549b78,uVar2);
      }
    }
  }
  else if (param_1 == 0x45) {
    if ((*_DAT_00549b7c == '\x02') && (*_DAT_00549b80 == '\x01')) {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(4,PTR_s_navigation_ui_005496f0,PTR_s_D__01_workspace_s200_ap510b_iar__005496ec,
                     PTR_s_NavigationInputEventHandler_00549b74,0x73c,_DAT_00549b84);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x10000000,_DAT_00549b88,_DAT_00549b88);
      }
      param_1 = 0;
    }
    else if ((*_DAT_00549b7c == '\t') && (*_DAT_00549b8c == '\x01')) {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(4,PTR_s_navigation_ui_005496f0,PTR_s_D__01_workspace_s200_ap510b_iar__005496ec,
                     PTR_s_NavigationInputEventHandler_00549b74,0x741,
                     PTR_s_navigation_ui_state_is_NAVIGATIO_00549b90);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x10000000,PTR_s__navigation_ui_navigation_ui_sta_00549b94,
                            PTR_s__navigation_ui_navigation_ui_sta_00549b94);
      }
      param_1 = 0;
    }
    else {
      bVar1 = FUN_0045a570();
      param_1 = (uint)bVar1;
      if (param_1 == 1) {
        FUN_0043c0e4(&uStack_34,10,0);
        uStack_34 = 0xf2;
        uStack_33 = 0x45;
        uStack_32 = 0;
        uStack_31 = 0;
        uStack_30 = 0;
        uStack_2f = 0;
        uVar2 = FUN_00464bb2(8,&uStack_34,6,0);
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(4,PTR_s_navigation_ui_005496f0,
                       PTR_s_D__01_workspace_s200_ap510b_iar__005496ec,
                       PTR_s_NavigationInputEventHandler_00549b74,0x750,
                       PTR_s_navigation_data_handler_send_inp_00549b70,uVar2);
        }
        iVar3 = FUN_0043d0ce();
        if (-1 < iVar3 << 0x1f) {
          iVar3 = FUN_0043d0ce();
          if (-1 < iVar3 << 0x1d) {
            return iVar3 << 0x1d;
          }
        }
        param_1 = compress_log_output(0x10400000,PTR_s__navigation_ui_navigation_data_h_00549b78,
                                      PTR_s__navigation_ui_navigation_data_h_00549b78,uVar2);
      }
    }
  }
  else if (param_1 == 0x48) {
    bVar1 = FUN_0045a570();
    param_1 = (uint)bVar1;
    if (param_1 == 1) {
      FUN_0043c0e4(&uStack_40,10,0);
      uStack_40 = 0xf2;
      uStack_3f = 0x48;
      uStack_3e = 0;
      uStack_3d = 0;
      uStack_3c = 0;
      uStack_3b = 0;
      uVar2 = FUN_00464bb2(8,&uStack_40,6,0);
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(4,PTR_s_navigation_ui_005496f0,PTR_s_D__01_workspace_s200_ap510b_iar__005496ec,
                     PTR_s_NavigationInputEventHandler_00549b74,0x75e,
                     PTR_s_navigation_data_handler_send_inp_00549b70,uVar2);
      }
      iVar3 = FUN_0043d0ce();
      if (-1 < iVar3 << 0x1f) {
        iVar3 = FUN_0043d0ce();
        if (-1 < iVar3 << 0x1d) {
          return iVar3 << 0x1d;
        }
      }
      param_1 = compress_log_output(0x10400000,PTR_s__navigation_ui_navigation_data_h_00549b78,
                                    PTR_s__navigation_ui_navigation_data_h_00549b78,uVar2);
    }
  }
  else if (param_1 == 0x41) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(4,PTR_s_navigation_ui_005496f0,PTR_s_D__01_workspace_s200_ap510b_iar__005496ec,
                   PTR_s_NavigationInputEventHandler_00549b74,0x761,
                   PTR_s_IMU_compass_Event__00549b98);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x10000000,PTR_s__navigation_ui_IMU_compass_Event_00549b9c,
                          PTR_s__navigation_ui_IMU_compass_Event_00549b9c);
    }
    bVar1 = FUN_0045a570();
    param_1 = (uint)bVar1;
    if (param_1 == 1) {
      FUN_0043c0e4(&uStack_4c,10,0);
      puVar4 = *(undefined4 **)(param_2 + 0x10);
      uStack_4c = 0xf2;
      uStack_4b = 0x41;
      uStack_4a = (undefined1)*puVar4;
      uStack_49 = (undefined1)((uint)*puVar4 >> 8);
      uStack_48 = (undefined1)((uint)*puVar4 >> 0x10);
      uStack_47 = (undefined1)((uint)*puVar4 >> 0x18);
      uVar2 = FUN_00464bb2(8,&uStack_4c,6,0);
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(4,PTR_s_navigation_ui_005496f0,PTR_s_D__01_workspace_s200_ap510b_iar__005496ec,
                     PTR_s_NavigationInputEventHandler_00549b74,0x774,
                     PTR_s_navigation_data_handler_send_inp_00549b70,uVar2);
      }
      iVar3 = FUN_0043d0ce();
      if (-1 < iVar3 << 0x1f) {
        iVar3 = FUN_0043d0ce();
        if (-1 < iVar3 << 0x1d) {
          return iVar3 << 0x1d;
        }
      }
      param_1 = compress_log_output(0x10400000,PTR_s__navigation_ui_navigation_data_h_00549b78,
                                    PTR_s__navigation_ui_navigation_data_h_00549b78,uVar2);
    }
  }
  else if (param_1 == 0x50) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(4,PTR_s_navigation_ui_005496f0,PTR_s_D__01_workspace_s200_ap510b_iar__005496ec,
                   PTR_s_NavigationInputEventHandler_00549b74,0x777,
                   PTR_s_IMU_compass_Event__00549b98);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x10000000,PTR_s__navigation_ui_IMU_compass_Event_00549b9c,
                          PTR_s__navigation_ui_IMU_compass_Event_00549b9c);
    }
    bVar1 = FUN_0045a570();
    param_1 = (uint)bVar1;
    if (param_1 == 1) {
      FUN_0043c0e4(&uStack_58,10,0);
      uStack_58 = 0xf7;
      uStack_57 = 0;
      uStack_56 = 0;
      uStack_55 = 0;
      uStack_54 = 0;
      uStack_53 = 0;
      uVar2 = FUN_00464bb2(8,&uStack_58,6,0);
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(4,PTR_s_navigation_ui_005496f0,PTR_s_D__01_workspace_s200_ap510b_iar__005496ec,
                     PTR_s_NavigationInputEventHandler_00549b74,0x783,
                     PTR_s_navigation_data_handler_send_inp_00549b70,uVar2);
      }
      iVar3 = FUN_0043d0ce();
      if (-1 < iVar3 << 0x1f) {
        iVar3 = FUN_0043d0ce();
        if (-1 < iVar3 << 0x1d) {
          return iVar3 << 0x1d;
        }
      }
      param_1 = compress_log_output(0x10400000,PTR_s__navigation_ui_navigation_data_h_00549b78,
                                    PTR_s__navigation_ui_navigation_data_h_00549b78,uVar2);
    }
  }
  else if (param_1 == 0x4f) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(4,PTR_s_navigation_ui_005496f0,PTR_s_D__01_workspace_s200_ap510b_iar__005496ec,
                   PTR_s_NavigationInputEventHandler_00549b74,0x786,
                   PTR_s_PAGE_EVENT_SYSTEM_EXIT_NOTIFY_Ev_00549ba0);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x10000000,PTR_s__navigation_ui_PAGE_EVENT_SYSTEM_00549ba4,
                          PTR_s__navigation_ui_PAGE_EVENT_SYSTEM_00549ba4);
    }
    bVar1 = FUN_0045a570();
    param_1 = (uint)bVar1;
    if (param_1 == 1) {
      FUN_0043c0e4(&uStack_64,10,0);
      uStack_64 = 0xf4;
      uStack_63 = 0;
      uVar2 = FUN_00464bb2(8,&uStack_64,6,0);
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(4,PTR_s_navigation_ui_005496f0,PTR_s_D__01_workspace_s200_ap510b_iar__005496ec,
                     PTR_s_NavigationInputEventHandler_00549b74,0x78e,
                     PTR_s_systemClose_application_send_exi_00549ba8,uVar2);
      }
      iVar3 = FUN_0043d0ce();
      if (-1 < iVar3 << 0x1f) {
        iVar3 = FUN_0043d0ce();
        if (-1 < iVar3 << 0x1d) {
          return iVar3 << 0x1d;
        }
      }
      param_1 = compress_log_output(0x10400000,PTR_s__navigation_ui_systemClose_appli_00549bac,
                                    PTR_s__navigation_ui_systemClose_appli_00549bac,uVar2);
    }
  }
  return param_1;
}

