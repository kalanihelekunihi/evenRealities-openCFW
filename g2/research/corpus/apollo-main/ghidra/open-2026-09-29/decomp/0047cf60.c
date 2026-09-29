
undefined4
UX_LocalSystemStatusSyncHandler
          (undefined4 param_1,ushort *param_2,undefined4 param_3,undefined4 param_4)

{
  ushort uVar1;
  bool bVar2;
  bool bVar3;
  byte *pbVar4;
  undefined1 uVar5;
  char cVar6;
  int iVar7;
  uint uVar8;
  undefined *puVar9;
  uint uVar10;
  
  bVar3 = false;
  bVar2 = false;
  iVar7 = FUN_0043d0ce();
  if (iVar7 << 0x1e < 0) {
    FUN_0043d574(4,PTR_s_ux_setting_0047d918,PTR_s_D__01_workspace_s200_ap510b_iar__0047d914,
                 PTR_s_UX_LocalSystemStatusSyncHandler_0047d910,0x50,
                 PTR_s_raw_data___0x_x_len____d_0047d90c,param_2,param_3,param_4);
  }
  iVar7 = FUN_0043d0ce();
  if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
    compress_log_output(0x10800000,PTR_s__ux_setting_raw_data___0x_x_len___0047d91c,
                        PTR_s__ux_setting_raw_data___0x_x_len___0047d91c,param_2,param_3);
  }
  iVar7 = FUN_0043d0ce();
  if (iVar7 << 0x1e < 0) {
    uVar5 = FUN_0045a568();
    FUN_0043d574(4,PTR_s_ux_setting_0047d918,PTR_s_D__01_workspace_s200_ap510b_iar__0047d914,
                 PTR_s_UX_LocalSystemStatusSyncHandler_0047d910,0x51,
                 PTR_s_pHeadMsg_>msgSelfRole____d__d_R___0047d920,(char)param_2[2],uVar5);
  }
  iVar7 = FUN_0043d0ce();
  if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
    uVar5 = FUN_0045a568();
    compress_log_output(0x10800000,PTR_s__ux_setting_pHeadMsg_>msgSelfRol_0047d924,
                        PTR_s__ux_setting_pHeadMsg_>msgSelfRol_0047d924,(char)param_2[2],uVar5);
  }
  iVar7 = FUN_0043d0ce();
  if (iVar7 << 0x1e < 0) {
    uVar5 = FUN_0045a568();
    FUN_0043d574(4,PTR_s_ux_setting_0047d918,PTR_s_D__01_workspace_s200_ap510b_iar__0047d914,
                 PTR_s_UX_LocalSystemStatusSyncHandler_0047d910,0x52,
                 PTR_s_pHeadMsg_>msgPeerRole____d__d_0047d928,*(undefined1 *)((int)param_2 + 5),
                 uVar5);
  }
  iVar7 = FUN_0043d0ce();
  if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
    uVar5 = FUN_0045a568();
    compress_log_output(0x10800000,PTR_s__ux_setting_pHeadMsg_>msgPeerRol_0047d92c,
                        PTR_s__ux_setting_pHeadMsg_>msgPeerRol_0047d92c,
                        *(undefined1 *)((int)param_2 + 5),uVar5);
  }
  uVar1 = *param_2;
  if (uVar1 == 1) {
    iVar7 = FUN_0043d0ce();
    if (iVar7 << 0x1e < 0) {
      FUN_0043d574(4,PTR_s_ux_setting_0047d918,PTR_s_D__01_workspace_s200_ap510b_iar__0047d914,
                   PTR_s_UX_LocalSystemStatusSyncHandler_0047d910,0x57,
                   PTR_s_SYSTEM_OTA_STATUS_ID_0047d930);
    }
    iVar7 = FUN_0043d0ce();
    if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
      compress_log_output(0x10000000,PTR_s__ux_setting_SYSTEM_OTA_STATUS_ID_0047d934,
                          PTR_s__ux_setting_SYSTEM_OTA_STATUS_ID_0047d934);
    }
    cVar6 = FUN_0045a568();
    if ((char)param_2[2] == cVar6) {
      iVar7 = FUN_0043d0ce();
      if (iVar7 << 0x1e < 0) {
        FUN_0043d574(4,PTR_s_ux_setting_0047d918,PTR_s_D__01_workspace_s200_ap510b_iar__0047d914,
                     PTR_s_UX_LocalSystemStatusSyncHandler_0047d910,0x59,
                     PTR_s_SYSTEM_OTA_STATUS_ID_state_come_f_0047d938,(char)param_2[3]);
      }
      iVar7 = FUN_0043d0ce();
      if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
        compress_log_output(0x10400000,PTR_s__ux_setting_SYSTEM_OTA_STATUS_ID_0047d93c,
                            PTR_s__ux_setting_SYSTEM_OTA_STATUS_ID_0047d93c,(char)param_2[3]);
      }
      if ((char)param_2[3] == '\x01') {
        *DAT_0047d900 = *DAT_0047d900 | 1;
        puVar9 = PTR_APP_MasterConnectEvent_1_0047d940;
        fw_event_loop_remove_delayed(PTR_APP_MasterConnectEvent_1_0047d940);
        fw_event_loop_push_delayed(puVar9,0x102,0);
      }
      else {
        *DAT_0047d900 = *DAT_0047d900 & 0xfe;
      }
    }
    else {
      cVar6 = FUN_0045a568();
      if (*(char *)((int)param_2 + 5) == cVar6) {
        iVar7 = FUN_0043d0ce();
        if (iVar7 << 0x1e < 0) {
          FUN_0043d574(4,PTR_s_ux_setting_0047d918,PTR_s_D__01_workspace_s200_ap510b_iar__0047d914,
                       PTR_s_UX_LocalSystemStatusSyncHandler_0047d910,0x62,
                       PTR_s_SYSTEM_OTA_STATUS_ID_state_come_f_0047d944,(char)param_2[3]);
        }
        iVar7 = FUN_0043d0ce();
        if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
          compress_log_output(0x10400000,PTR_s__ux_setting_SYSTEM_OTA_STATUS_ID_0047d948,
                              PTR_s__ux_setting_SYSTEM_OTA_STATUS_ID_0047d948,(char)param_2[3]);
        }
        if ((char)param_2[3] == '\x01') {
          *DAT_0047d900 = *DAT_0047d900 | 2;
          puVar9 = PTR_APP_MasterConnectEvent_1_0047d940;
          fw_event_loop_remove_delayed(PTR_APP_MasterConnectEvent_1_0047d940);
          fw_event_loop_push_delayed(puVar9,0x102,0);
        }
        else {
          *DAT_0047d900 = *DAT_0047d900 & 0xfd;
        }
      }
    }
    if ((*DAT_0047d900 & 0xc) == 0xc) {
      FUN_0047432c();
    }
    else if (((*DAT_0047d900 & 0xc) == 0) && (iVar7 = SVC_Settings_InputEventCheck(), iVar7 == 1)) {
      FUN_00474100();
    }
  }
  else if (uVar1 != 0) {
    if (uVar1 == 3) {
      uVar8 = UX_GetSystemBLEStatus();
      cVar6 = FUN_0045a568();
      bVar2 = bVar3;
      if (*(char *)((int)param_2 + 5) == cVar6) {
        iVar7 = FUN_0043d0ce();
        if (iVar7 << 0x1e < 0) {
          FUN_0043d574(4,PTR_s_ux_setting_0047d918,PTR_s_D__01_workspace_s200_ap510b_iar__0047d914,
                       PTR_s_UX_LocalSystemStatusSyncHandler_0047d910,0xb3,
                       PTR_s_SYSTEM_BLE_STATUS_REPLY_ID_state_0047d97c,(char)param_2[3]);
        }
        iVar7 = FUN_0043d0ce();
        if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
          compress_log_output(0x10400000,PTR_s__ux_setting_SYSTEM_BLE_STATUS_RE_0047d980,
                              PTR_s__ux_setting_SYSTEM_BLE_STATUS_RE_0047d980,(char)param_2[3]);
        }
        if ((char)param_2[3] == '\x01') {
          *DAT_0047d900 = *DAT_0047d900 | 8;
          uVar10 = UX_GetSystemBLEStatus();
          if ((uVar8 & 0xff) == uVar10) {
            bVar2 = false;
          }
          else {
            bVar2 = true;
          }
        }
        else if ((char)param_2[3] == '\0') {
          *DAT_0047d900 = *DAT_0047d900 & 0xf7;
          uVar10 = UX_GetSystemBLEStatus();
          if ((uVar8 & 0xff) == uVar10) {
            bVar2 = false;
          }
          else {
            bVar2 = true;
          }
        }
      }
    }
    else if (uVar1 < 3) {
      uVar8 = UX_GetSystemBLEStatus();
      iVar7 = FUN_0043d0ce();
      if (iVar7 << 0x1e < 0) {
        iVar7 = FUN_0045a568();
        puVar9 = PTR_DAT_0047d950;
        if (iVar7 == 1) {
          puVar9 = PTR_s_RIGHT_0047d94c;
        }
        FUN_0043d574(4,PTR_s_ux_setting_0047d918,PTR_s_D__01_workspace_s200_ap510b_iar__0047d914,
                     PTR_s_UX_LocalSystemStatusSyncHandler_0047d910,0x7a,
                     PTR_s_SYSTEM_BLE_STATUS_ID_ROLE____s_0047d954,puVar9);
      }
      iVar7 = FUN_0043d0ce();
      if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
        iVar7 = FUN_0045a568();
        puVar9 = PTR_DAT_0047d950;
        if (iVar7 == 1) {
          puVar9 = PTR_s_RIGHT_0047d94c;
        }
        compress_log_output(0x10400000,PTR_s__ux_setting_SYSTEM_BLE_STATUS_ID_0047d958,
                            PTR_s__ux_setting_SYSTEM_BLE_STATUS_ID_0047d958,puVar9);
      }
      iVar7 = FUN_0043d0ce();
      if (iVar7 << 0x1e < 0) {
        FUN_0043d574(4,PTR_s_ux_setting_0047d918,PTR_s_D__01_workspace_s200_ap510b_iar__0047d914,
                     PTR_s_UX_LocalSystemStatusSyncHandler_0047d910,0x7b,
                     PTR_s_SYSTEM_BLE_STATUS_ID_selfBleStat_0047d95c,(*DAT_0047d900 & 7) >> 2,
                     (*DAT_0047d900 & 0xf) >> 3);
      }
      iVar7 = FUN_0043d0ce();
      if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
        compress_log_output(0x10800000,PTR_s__ux_setting_SYSTEM_BLE_STATUS_ID_0047d960,
                            PTR_s__ux_setting_SYSTEM_BLE_STATUS_ID_0047d960,(*DAT_0047d900 & 7) >> 2
                            ,(*DAT_0047d900 & 0xf) >> 3);
      }
      iVar7 = FUN_0043d0ce();
      if (iVar7 << 0x1e < 0) {
        FUN_0043d574(4,PTR_s_ux_setting_0047d918,PTR_s_D__01_workspace_s200_ap510b_iar__0047d914,
                     PTR_s_UX_LocalSystemStatusSyncHandler_0047d910,0x7c,
                     PTR_s_SYSTEM_BLE_STATUS_ID_selfBleRing_0047d964,(*DAT_0047d900 & 0x1f) >> 4,
                     (*DAT_0047d900 & 0x3f) >> 5);
      }
      iVar7 = FUN_0043d0ce();
      if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
        compress_log_output(0x10800000,PTR_s__ux_setting_SYSTEM_BLE_STATUS_ID_0047d968,
                            PTR_s__ux_setting_SYSTEM_BLE_STATUS_ID_0047d968,
                            (*DAT_0047d900 & 0x1f) >> 4,(*DAT_0047d900 & 0x3f) >> 5);
      }
      cVar6 = FUN_0045a568();
      if ((char)param_2[2] == cVar6) {
        iVar7 = FUN_0043d0ce();
        if (iVar7 << 0x1e < 0) {
          FUN_0043d574(4,PTR_s_ux_setting_0047d918,PTR_s_D__01_workspace_s200_ap510b_iar__0047d914,
                       PTR_s_UX_LocalSystemStatusSyncHandler_0047d910,0x7e,
                       PTR_s_SYSTEM_BLE_STATUS_ID_state_come_f_0047d96c,(char)param_2[3]);
        }
        iVar7 = FUN_0043d0ce();
        if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
          compress_log_output(0x10400000,PTR_s__ux_setting_SYSTEM_BLE_STATUS_ID_0047d970,
                              PTR_s__ux_setting_SYSTEM_BLE_STATUS_ID_0047d970,(char)param_2[3]);
        }
        if ((char)param_2[3] == '\x01') {
          *DAT_0047d900 = *DAT_0047d900 | 4;
          uVar10 = UX_GetSystemBLEStatus();
          if ((uVar8 & 0xff) == uVar10) {
            bVar2 = false;
          }
          else {
            bVar2 = true;
          }
        }
        else if ((char)param_2[3] == '\0') {
          *DAT_0047d900 = *DAT_0047d900 & 0xfb;
          uVar10 = UX_GetSystemBLEStatus();
          if ((uVar8 & 0xff) == uVar10) {
            bVar2 = false;
          }
          else {
            bVar2 = true;
          }
        }
        else if ((char)param_2[3] == '\x03') {
          *DAT_0047d900 = *DAT_0047d900 | 0x10;
          FUN_004d306c(2);
          FUN_0049e448(3,0);
          bVar2 = bVar3;
        }
        else {
          bVar2 = bVar3;
          if ((char)param_2[3] == '\x02') {
            *DAT_0047d900 = *DAT_0047d900 & 0xef;
            FUN_004d306c(1);
            FUN_0049e448(2,0);
          }
        }
      }
      else {
        cVar6 = FUN_0045a568();
        bVar2 = bVar3;
        if (*(char *)((int)param_2 + 5) == cVar6) {
          iVar7 = FUN_0043d0ce();
          if (iVar7 << 0x1e < 0) {
            FUN_0043d574(4,PTR_s_ux_setting_0047d918,PTR_s_D__01_workspace_s200_ap510b_iar__0047d914
                         ,PTR_s_UX_LocalSystemStatusSyncHandler_0047d910,0x93,
                         PTR_s_SYSTEM_BLE_STATUS_ID_state_come_f_0047d974,(char)param_2[3]);
          }
          iVar7 = FUN_0043d0ce();
          if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
            compress_log_output(0x10400000,PTR_s__ux_setting_SYSTEM_BLE_STATUS_ID_0047d978,
                                PTR_s__ux_setting_SYSTEM_BLE_STATUS_ID_0047d978,(char)param_2[3]);
          }
          if ((char)param_2[3] == '\x01') {
            *DAT_0047d900 = *DAT_0047d900 | 8;
            uVar10 = UX_GetSystemBLEStatus();
            UX_SendBLEStatusToPeer();
            bVar2 = (uVar8 & 0xff) != uVar10;
          }
          else if ((char)param_2[3] == '\0') {
            *DAT_0047d900 = *DAT_0047d900 & 0xf7;
            uVar10 = UX_GetSystemBLEStatus();
            UX_SendBLEStatusToPeer();
            bVar2 = (uVar8 & 0xff) != uVar10;
          }
          else if ((char)param_2[3] == '\x03') {
            *DAT_0047d900 = *DAT_0047d900 | 0x20;
            iVar7 = central_is_ring_owner_side_004a2914();
            if (iVar7 == 0) {
              APP_MasterCancelRingConnectRetry(1);
            }
          }
          else if ((char)param_2[3] == '\x02') {
            *DAT_0047d900 = *DAT_0047d900 & 0xdf;
          }
        }
      }
    }
    else if (uVar1 == 5) {
      iVar7 = FUN_0043d0ce();
      if (iVar7 << 0x1e < 0) {
        FUN_0043d574(3,PTR_s_ux_setting_0047d918,PTR_s_D__01_workspace_s200_ap510b_iar__0047d914,
                     PTR_s_UX_LocalSystemStatusSyncHandler_0047d910,0xe5,
                     PTR_s_SYSTEM_BLE_STATUS_RING_QUERY_ID_0047d99c);
      }
      iVar7 = FUN_0043d0ce();
      if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
        compress_log_output(0xc000000,PTR_s__ux_setting_SYSTEM_BLE_STATUS_RI_0047d9a0,
                            PTR_s__ux_setting_SYSTEM_BLE_STATUS_RI_0047d9a0);
      }
      cVar6 = FUN_0045a568();
      if (*(char *)((int)param_2 + 5) == cVar6) {
        iVar7 = FUN_0043d0ce();
        if (iVar7 << 0x1e < 0) {
          uVar5 = central_is_ring_owner_side_004a2914();
          FUN_0043d574(4,PTR_s_ux_setting_0047d918,PTR_s_D__01_workspace_s200_ap510b_iar__0047d914,
                       PTR_s_UX_LocalSystemStatusSyncHandler_0047d910,0xe7,
                       PTR_s_SYSTEM_BLE_STATUS_RING_QUERY_ID_f_0047d9a4,uVar5);
        }
        iVar7 = FUN_0043d0ce();
        if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
          uVar5 = central_is_ring_owner_side_004a2914();
          compress_log_output(0x10400000,PTR_s__ux_setting_SYSTEM_BLE_STATUS_RI_0047d9a8,
                              PTR_s__ux_setting_SYSTEM_BLE_STATUS_RI_0047d9a8,uVar5);
        }
        iVar7 = central_is_ring_owner_side_004a2914();
        if (iVar7 != 0) {
          UX_SendRingStatusToPeer();
        }
      }
    }
    else if (uVar1 < 5) {
      iVar7 = FUN_0043d0ce();
      if (iVar7 << 0x1e < 0) {
        FUN_0043d574(3,PTR_s_ux_setting_0047d918,PTR_s_D__01_workspace_s200_ap510b_iar__0047d914,
                     PTR_s_UX_LocalSystemStatusSyncHandler_0047d910,0xc1,
                     PTR_s_SYSTEM_BLE_STATUS_RING_MAC_SET_I_0047d984,(char)param_2[3]);
      }
      iVar7 = FUN_0043d0ce();
      if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
        compress_log_output(0xc400000,PTR_s__ux_setting_SYSTEM_BLE_STATUS_RI_0047d988,
                            PTR_s__ux_setting_SYSTEM_BLE_STATUS_RI_0047d988,(char)param_2[3]);
      }
      pbVar4 = DAT_0047d900;
      *DAT_0047d900 = *DAT_0047d900 & 0xbf | ((byte)param_2[3] & 1) << 6;
      if ((*pbVar4 & 0x7f) >> 6 == 0) {
        *pbVar4 = *pbVar4 & 0xef;
        *pbVar4 = *pbVar4 & 0xdf;
      }
      iVar7 = FUN_0045a568();
      if (iVar7 == 1) {
        CB_BLE_STATUS_Notify(1,(*pbVar4 & 0x7f) >> 6);
      }
    }
    else if (uVar1 == 6) {
      iVar7 = FUN_0043d0ce();
      if (iVar7 << 0x1e < 0) {
        FUN_0043d574(3,PTR_s_ux_setting_0047d918,PTR_s_D__01_workspace_s200_ap510b_iar__0047d914,
                     PTR_s_UX_LocalSystemStatusSyncHandler_0047d910,0xd0,
                     PTR_s_SYSTEM_BLE_STATUS_RING_REPLY_ID_s_0047d98c,(char)param_2[3]);
      }
      iVar7 = FUN_0043d0ce();
      if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
        compress_log_output(0xc400000,PTR_s__ux_setting_SYSTEM_BLE_STATUS_RI_0047d990,
                            PTR_s__ux_setting_SYSTEM_BLE_STATUS_RI_0047d990,(char)param_2[3]);
      }
      cVar6 = FUN_0045a568();
      if (*(char *)((int)param_2 + 5) == cVar6) {
        iVar7 = FUN_0043d0ce();
        if (iVar7 << 0x1e < 0) {
          FUN_0043d574(4,PTR_s_ux_setting_0047d918,PTR_s_D__01_workspace_s200_ap510b_iar__0047d914,
                       PTR_s_UX_LocalSystemStatusSyncHandler_0047d910,0xd2,
                       PTR_s_SYSTEM_BLE_STATUS_RING_REPLY_ID_s_0047d994,(char)param_2[3]);
        }
        iVar7 = FUN_0043d0ce();
        if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
          compress_log_output(0x10400000,PTR_s__ux_setting_SYSTEM_BLE_STATUS_RI_0047d998,
                              PTR_s__ux_setting_SYSTEM_BLE_STATUS_RI_0047d998,(char)param_2[3]);
        }
        if ((char)param_2[3] == '\x03') {
          *DAT_0047d900 = *DAT_0047d900 | 0x20;
          FUN_004d306c(2);
          FUN_0049e448(3,0);
          iVar7 = central_is_ring_owner_side_004a2914();
          if (iVar7 == 0) {
            APP_MasterCancelRingConnectRetry(1);
          }
        }
        else if ((char)param_2[3] == '\x02') {
          *DAT_0047d900 = *DAT_0047d900 & 0xdf;
          FUN_004d306c(1);
          FUN_0049e448(2,0);
        }
      }
    }
  }
  if (bVar2) {
    iVar7 = FUN_0043d0ce();
    if (iVar7 << 0x1e < 0) {
      uVar5 = UX_GetSystemBLEStatus();
      FUN_0043d574(4,PTR_s_ux_setting_0047d918,PTR_s_D__01_workspace_s200_ap510b_iar__0047d914,
                   PTR_s_UX_LocalSystemStatusSyncHandler_0047d910,0xf4,
                   PTR_s_CB_EVENT_BLE_STATUS_CHANGE_UX_Ge_0047d9ac,uVar5);
    }
    iVar7 = FUN_0043d0ce();
    if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
      uVar5 = UX_GetSystemBLEStatus();
      compress_log_output(0x10400000,PTR_s__ux_setting_CB_EVENT_BLE_STATUS__0047d9b0,
                          PTR_s__ux_setting_CB_EVENT_BLE_STATUS__0047d9b0,uVar5);
    }
    uVar5 = UX_GetSystemBLEStatus();
    CB_BLE_STATUS_Notify(0,uVar5);
  }
  return 0;
}

