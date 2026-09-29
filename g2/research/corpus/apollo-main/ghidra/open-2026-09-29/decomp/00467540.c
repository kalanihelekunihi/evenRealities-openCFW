
void FUN_00467540(uint *param_1)

{
  undefined1 uVar1;
  byte bVar2;
  int iVar3;
  int iVar4;
  undefined *puVar5;
  uint uVar6;
  undefined4 uVar7;
  bool bVar8;
  
  if (param_1 == (uint *)0x0) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(2,PTR_s_setting_00467f14,PTR_s_D__01_workspace_s200_ap510b_iar__00467f10,
                   PTR_s_setting_handle_dominant_hand_00467f2c,0x233,
                   PTR_s_dominant_hand_data_is_NULL_00467f28);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x8000000,PTR_s__setting_dominant_hand_data_is_N_00467f30,
                          PTR_s__setting_dominant_hand_data_is_N_00467f30);
    }
  }
  else {
    iVar3 = FUN_00466010();
    uVar6 = *param_1;
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      FUN_0043d574(3,PTR_s_setting_00467f14,PTR_s_D__01_workspace_s200_ap510b_iar__00467f10,
                   PTR_s_setting_handle_dominant_hand_00467f2c,0x23c,
                   PTR_s_Received_dominant_hand_setting__d_00467f34,uVar6 & 0xff,(short)param_1[1]);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0xc800000,PTR_s__setting_Received_dominant_hand_s_00467f38,
                          PTR_s__setting_Received_dominant_hand_s_00467f38,uVar6 & 0xff,
                          (short)param_1[1]);
    }
    uVar1 = *(undefined1 *)(iVar3 + 0xb);
    bVar8 = false;
    if ((short)param_1[1] == 6) {
      iVar4 = FUN_004751c8(iVar3 + 0xc,(int)param_1 + 6,6);
      bVar8 = iVar4 != 0;
      if (bVar8) {
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          FUN_0043d574(3,PTR_s_setting_00467f14,PTR_s_D__01_workspace_s200_ap510b_iar__00467f10,
                       PTR_s_setting_handle_dominant_hand_00467f2c,0x265,
                       PTR_s_dominant_hand_ring_mac_changed__r_00467f3c,
                       *(undefined1 *)(iVar3 + 0x11),*(undefined1 *)(iVar3 + 0x10),
                       *(undefined1 *)(iVar3 + 0xf));
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0xcc00000,PTR_s__setting_dominant_hand_ring_mac_c_00467f40,
                              PTR_s__setting_dominant_hand_ring_mac_c_00467f40,
                              *(undefined1 *)(iVar3 + 0x11),*(undefined1 *)(iVar3 + 0x10),
                              *(undefined1 *)(iVar3 + 0xf));
        }
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          FUN_0043d574(3,PTR_s_setting_00467f14,PTR_s_D__01_workspace_s200_ap510b_iar__00467f10,
                       PTR_s_setting_handle_dominant_hand_00467f2c,0x269,
                       PTR_s_dominant_hand_ring_mac_changed__r_00467f44,*(undefined1 *)(iVar3 + 0xe)
                       ,*(undefined1 *)(iVar3 + 0xd),*(undefined1 *)(iVar3 + 0xc));
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0xcc00000,PTR_s__setting_dominant_hand_ring_mac_c_00467f48,
                              PTR_s__setting_dominant_hand_ring_mac_c_00467f48,
                              *(undefined1 *)(iVar3 + 0xe),*(undefined1 *)(iVar3 + 0xd),
                              *(undefined1 *)(iVar3 + 0xc));
        }
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          FUN_0043d574(3,PTR_s_setting_00467f14,PTR_s_D__01_workspace_s200_ap510b_iar__00467f10,
                       PTR_s_setting_handle_dominant_hand_00467f2c,0x26d,
                       PTR_s_dominant_hand_ring_mac_changed__r_00467f4c,
                       *(undefined1 *)((int)param_1 + 0xb),*(undefined1 *)((int)param_1 + 10),
                       *(undefined1 *)((int)param_1 + 9));
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0xcc00000,PTR_s__setting_dominant_hand_ring_mac_c_00467f50,
                              PTR_s__setting_dominant_hand_ring_mac_c_00467f50,
                              *(undefined1 *)((int)param_1 + 0xb),*(undefined1 *)((int)param_1 + 10)
                              ,*(undefined1 *)((int)param_1 + 9));
        }
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          FUN_0043d574(3,PTR_s_setting_00467f14,PTR_s_D__01_workspace_s200_ap510b_iar__00467f10,
                       PTR_s_setting_handle_dominant_hand_00467f2c,0x271,
                       PTR_s_dominant_hand_ring_mac_changed__r_00467f54,(char)param_1[2],
                       *(undefined1 *)((int)param_1 + 7),*(undefined1 *)((int)param_1 + 6));
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0xcc00000,PTR_s__setting_dominant_hand_ring_mac_c_00467f58,
                              PTR_s__setting_dominant_hand_ring_mac_c_00467f58,(char)param_1[2],
                              *(undefined1 *)((int)param_1 + 7),*(undefined1 *)((int)param_1 + 6));
        }
      }
    }
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      iVar4 = FUN_0045a568();
      puVar5 = PTR_DAT_00467f60;
      if (iVar4 == 1) {
        puVar5 = PTR_s_RIGHT_00467f5c;
      }
      FUN_0043d574(3,PTR_s_setting_00467f14,PTR_s_D__01_workspace_s200_ap510b_iar__00467f10,
                   PTR_s_setting_handle_dominant_hand_00467f2c,0x277,
                   PTR_s_dominant_hand_policy__cur__u_new_00467f64,uVar1,uVar6 & 0xff,puVar5);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      iVar4 = FUN_0045a568();
      puVar5 = PTR_DAT_00467f60;
      if (iVar4 == 1) {
        puVar5 = PTR_s_RIGHT_00467f5c;
      }
      compress_log_output(0xcc00000,PTR_s__setting_dominant_hand_policy__c_00467f68,
                          PTR_s__setting_dominant_hand_policy__c_00467f68,uVar1,uVar6 & 0xff,puVar5)
      ;
    }
    bVar2 = RING_ConnectPolicyOnDominantHand(uVar1,uVar6 & 0xff);
    uVar7 = 4000;
    if ((bVar8 != false) && (iVar4 = ring_address_is_unset_004a26e8(iVar3 + 0xc), iVar4 != 0)) {
      uVar7 = 8000;
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        FUN_0043d574(3,PTR_s_setting_00467f14,PTR_s_D__01_workspace_s200_ap510b_iar__00467f10,
                     PTR_s_setting_handle_dominant_hand_00467f2c,0x281,
                     PTR_s_dominant_hand__ring_mac_recovere_00467f6c,8000);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0xc400000,PTR_s__setting_dominant_hand__ring_mac_00467f70,
                            PTR_s__setting_dominant_hand__ring_mac_00467f70,8000);
      }
    }
    if (bVar2 == 0) {
      *(char *)(iVar3 + 0xb) = (char)uVar6;
      if ((short)param_1[1] == 6) {
        FUN_00439be4(iVar3 + 0xc,(int)param_1 + 6,6);
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          FUN_0043d574(3,PTR_s_setting_00467f14,PTR_s_D__01_workspace_s200_ap510b_iar__00467f10,
                       PTR_s_setting_handle_dominant_hand_00467f2c,0x286,
                       PTR_s_Updated_ring_mac__02X__02X__02X__00467f74,*(undefined1 *)(iVar3 + 0x11)
                       ,*(undefined1 *)(iVar3 + 0x10),*(undefined1 *)(iVar3 + 0xf),
                       *(undefined1 *)(iVar3 + 0xe),*(undefined1 *)(iVar3 + 0xd),
                       *(undefined1 *)(iVar3 + 0xc));
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0xd800000,PTR_s__setting_Updated_ring_mac__02X___00467f78,
                              PTR_s__setting_Updated_ring_mac__02X___00467f78,
                              *(undefined1 *)(iVar3 + 0x11),*(undefined1 *)(iVar3 + 0x10),
                              *(undefined1 *)(iVar3 + 0xf),*(undefined1 *)(iVar3 + 0xe),
                              *(undefined1 *)(iVar3 + 0xd),*(undefined1 *)(iVar3 + 0xc));
        }
      }
      else if ((short)param_1[1] == 0) {
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          FUN_0043d574(4,PTR_s_setting_00467f14,PTR_s_D__01_workspace_s200_ap510b_iar__00467f10,
                       PTR_s_setting_handle_dominant_hand_00467f2c,0x286,
                       PTR_s_ring_mac_not_provided_by_APP__ke_00467f7c);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0x10000000,PTR_s__setting_ring_mac_not_provided_b_00467f80,
                              PTR_s__setting_ring_mac_not_provided_b_00467f80);
        }
      }
      else {
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          FUN_0043d574(2,PTR_s_setting_00467f14,PTR_s_D__01_workspace_s200_ap510b_iar__00467f10,
                       PTR_s_setting_handle_dominant_hand_00467f2c,0x286,
                       PTR_s_Unexpected_ring_mac_size__d__ign_00467f84,(short)param_1[1]);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0x8400000,PTR_s__setting_Unexpected_ring_mac_siz_00467f88,
                              PTR_s__setting_Unexpected_ring_mac_siz_00467f88,(short)param_1[1]);
        }
      }
      APP_MasterSetTargetAddrName(iVar3 + 0xc,0,0);
      FUN_004661a6();
      if (bVar8 != false) {
        FUN_00466016();
      }
      APP_MasterOnDominantHandChangedEx(uVar6 & 0xff,uVar7,0);
      iVar3 = FUN_0045a568();
      if (iVar3 == 1) {
        UX_SendBLEStatusReply(1);
      }
    }
    else if (bVar2 == 2) {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(2,PTR_s_setting_00467f14,PTR_s_D__01_workspace_s200_ap510b_iar__00467f10,
                     PTR_s_setting_handle_dominant_hand_00467f2c,0x2a6,
                     PTR_s_setting_handle_dominant_hand__re_00467f9c,uVar1);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x8400000,PTR_s__setting_setting_handle_dominant_00467fa0,
                            PTR_s__setting_setting_handle_dominant_00467fa0,uVar1);
      }
    }
    else if (bVar2 < 2) {
      *(char *)(iVar3 + 0xb) = (char)uVar6;
      if ((short)param_1[1] == 6) {
        FUN_00439be4(iVar3 + 0xc,(int)param_1 + 6,6);
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          FUN_0043d574(3,PTR_s_setting_00467f14,PTR_s_D__01_workspace_s200_ap510b_iar__00467f10,
                       PTR_s_setting_handle_dominant_hand_00467f2c,0x293,
                       PTR_s_Updated_ring_mac__02X__02X__02X__00467f74,*(undefined1 *)(iVar3 + 0x11)
                       ,*(undefined1 *)(iVar3 + 0x10),*(undefined1 *)(iVar3 + 0xf),
                       *(undefined1 *)(iVar3 + 0xe),*(undefined1 *)(iVar3 + 0xd),
                       *(undefined1 *)(iVar3 + 0xc));
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0xd800000,PTR_s__setting_Updated_ring_mac__02X___00467f78,
                              PTR_s__setting_Updated_ring_mac__02X___00467f78,
                              *(undefined1 *)(iVar3 + 0x11),*(undefined1 *)(iVar3 + 0x10),
                              *(undefined1 *)(iVar3 + 0xf),*(undefined1 *)(iVar3 + 0xe),
                              *(undefined1 *)(iVar3 + 0xd),*(undefined1 *)(iVar3 + 0xc));
        }
      }
      else if ((short)param_1[1] == 0) {
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          FUN_0043d574(4,PTR_s_setting_00467f14,PTR_s_D__01_workspace_s200_ap510b_iar__00467f10,
                       PTR_s_setting_handle_dominant_hand_00467f2c,0x293,
                       PTR_s_ring_mac_not_provided_by_APP__ke_00467f7c);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0x10000000,PTR_s__setting_ring_mac_not_provided_b_00467f80,
                              PTR_s__setting_ring_mac_not_provided_b_00467f80);
        }
      }
      else {
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          FUN_0043d574(2,PTR_s_setting_00467f14,PTR_s_D__01_workspace_s200_ap510b_iar__00467f10,
                       PTR_s_setting_handle_dominant_hand_00467f2c,0x293,
                       PTR_s_Unexpected_ring_mac_size__d__ign_00467f84,(short)param_1[1]);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0x8400000,PTR_s__setting_Unexpected_ring_mac_siz_00467f88,
                              PTR_s__setting_Unexpected_ring_mac_siz_00467f88,(short)param_1[1]);
        }
      }
      APP_MasterSetTargetAddrName(iVar3 + 0xc,0,0);
      FUN_004661a6();
      if (bVar8 != false) {
        FUN_00466016();
      }
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        puVar5 = PTR_s_only_00467f90;
        if (bVar8 != false) {
          puVar5 = PTR_s___ring_mac_changed_00467f8c;
        }
        FUN_0043d574(3,PTR_s_setting_00467f14,PTR_s_D__01_workspace_s200_ap510b_iar__00467f10,
                     PTR_s_setting_handle_dominant_hand_00467f2c,0x29a,
                     PTR_s_setting_handle_dominant_hand__un_00467f94,puVar5);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        puVar5 = PTR_s_only_00467f90;
        if (bVar8 != false) {
          puVar5 = PTR_s___ring_mac_changed_00467f8c;
        }
        compress_log_output(0xc400000,PTR_s__setting_setting_handle_dominant_00467f98,
                            PTR_s__setting_setting_handle_dominant_00467f98,puVar5);
      }
      APP_MasterOnDominantHandChangedEx(uVar6 & 0xff,0,bVar8 ^ 1);
      if ((bVar8 != false) && (iVar3 = FUN_0045a568(), iVar3 == 1)) {
        UX_SendBLEStatusReply(1);
      }
    }
  }
  return;
}

