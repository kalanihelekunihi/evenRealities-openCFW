
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4
APP_MasterTryReconnectRingByScene
          (char param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  char *pcVar1;
  byte *pbVar2;
  int iVar3;
  undefined4 uVar4;
  uint uVar5;
  undefined4 uVar6;
  char cStack_34;
  char cStack_33;
  char cStack_32;
  char cStack_31;
  char cStack_30;
  char cStack_2f;
  undefined1 auStack_2c [14];
  undefined1 uStack_1e;
  undefined4 uStack_1c;
  
  uStack_1c = param_4;
  iVar3 = central_is_ring_owner_side_004a2914();
  if (iVar3 == 0) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(3,PTR_s_ble_master_004a3558,PTR_s_D__01_workspace_s200_ap510b_iar__004a3554,
                   PTR_s_APP_MasterTryReconnectRingByScen_004a3550,0x60c,
                   PTR_s__Ring__TryReconnectByScene__not_r_004a354c);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0xc000000,PTR_s__ble_master__Ring__TryReconnectB_004a355c,
                          PTR_s__ble_master__Ring__TryReconnectB_004a355c);
    }
    uVar4 = 0;
  }
  else {
    iVar3 = FUN_00466010();
    FUN_00439be4(&cStack_34,iVar3 + 0xc,6);
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(3,PTR_s_ble_master_004a3558,PTR_s_D__01_workspace_s200_ap510b_iar__004a3554,
                   PTR_s_APP_MasterTryReconnectRingByScen_004a3550,0x613,
                   PTR_s__Ring__TryReconnectByScene__scen_004a3560,param_1);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0xc400000,PTR_s__ble_master__Ring__TryReconnectB_004a3564,
                          PTR_s__ble_master__Ring__TryReconnectB_004a3564,param_1);
    }
    if (((((cStack_2f == -1) && (cStack_30 == -1)) && (cStack_31 == -1)) &&
        ((cStack_32 == -1 && (cStack_33 == -1)))) && (cStack_34 == -1)) {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(3,PTR_s_ble_master_004a3558,PTR_s_D__01_workspace_s200_ap510b_iar__004a3554,
                     PTR_s_APP_MasterTryReconnectRingByScen_004a3550,0x617,
                     PTR_s__Ring__Scene__ringMac_not_set__s_004a3568);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0xc000000,PTR_s__ble_master__Ring__Scene__ringMa_004a356c,
                            PTR_s__ble_master__Ring__Scene__ringMa_004a356c);
      }
      uVar4 = 0;
    }
    else {
      iVar3 = master_conn_id_is_set_004a22c6();
      pbVar2 = _DAT_004a3584;
      pcVar1 = _DAT_004a3578;
      if (iVar3 == 0) {
        if (*_DAT_004a3578 == '\x03') {
          iVar3 = FUN_0043d0ce();
          if (iVar3 << 0x1e < 0) {
            FUN_0043d574(3,PTR_s_ble_master_004a3558,PTR_s_D__01_workspace_s200_ap510b_iar__004a3554
                         ,PTR_s_APP_MasterTryReconnectRingByScen_004a3550,0x621,_DAT_004a357c);
          }
          iVar3 = FUN_0043d0ce();
          if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
            compress_log_output(0xc000000,_DAT_004a3580,_DAT_004a3580);
          }
          uVar4 = 0;
        }
        else {
          uVar5 = (uint)*_DAT_004a3584;
          if (uVar5 != 0) {
            if (uVar5 == 1) {
              iVar3 = FUN_0043d0ce();
              if (iVar3 << 0x1e < 0) {
                FUN_0043d574(3,PTR_s_ble_master_004a3558,
                             PTR_s_D__01_workspace_s200_ap510b_iar__004a3554,
                             PTR_s_APP_MasterTryReconnectRingByScen_004a3550,0x62a,
                             PTR_s__Ring__Scene__OPENING_in_progres_004a3588);
              }
              iVar3 = FUN_0043d0ce();
              if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
                compress_log_output(0xc000000,PTR_s__ble_master__Ring__Scene__OPENIN_004a358c,
                                    PTR_s__ble_master__Ring__Scene__OPENIN_004a358c);
              }
              return 0;
            }
            if (uVar5 - 3 < 3) {
              iVar3 = FUN_0043d0ce();
              if (iVar3 << 0x1e < 0) {
                uVar4 = _ringLinkStateName(*pbVar2);
                FUN_0043d574(3,PTR_s_ble_master_004a3558,
                             PTR_s_D__01_workspace_s200_ap510b_iar__004a3554,
                             PTR_s_APP_MasterTryReconnectRingByScen_004a3550,0x632,
                             PTR_s__Ring__Scene__state__s__skip_004a3598,uVar4);
              }
              iVar3 = FUN_0043d0ce();
              if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
                uVar4 = _ringLinkStateName(*pbVar2);
                compress_log_output(0xc400000,PTR_s__ble_master__Ring__Scene__state__004a359c,
                                    PTR_s__ble_master__Ring__Scene__state__004a359c,uVar4);
              }
              return 0;
            }
            if (uVar5 == 6) {
              iVar3 = FUN_0043d0ce();
              if (iVar3 << 0x1e < 0) {
                FUN_0043d574(3,PTR_s_ble_master_004a3558,
                             PTR_s_D__01_workspace_s200_ap510b_iar__004a3554,
                             PTR_s_APP_MasterTryReconnectRingByScen_004a3550,0x62d,
                             PTR_s__Ring__Scene__UNPAIRING_in_progr_004a3590);
              }
              iVar3 = FUN_0043d0ce();
              if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
                compress_log_output(0xc000000,PTR_s__ble_master__Ring__Scene__UNPAIR_004a3594,
                                    PTR_s__ble_master__Ring__Scene__UNPAIR_004a3594);
              }
              return 0;
            }
          }
          if (param_1 == '\0') {
            uVar4 = 1000;
          }
          else {
            uVar4 = 500;
          }
          if (10 < *_DAT_004a35a0) {
            *_DAT_004a35a0 = 0;
          }
          central_cancel_connect_retry_work_004a17f4();
          FUN_00439be4(auStack_2c,DAT_004a34b8,0xe);
          uStack_1e = 0;
          APP_MasterSetTargetAddrName(&cStack_34,auStack_2c,0xf);
          auth_mode_set(1);
          *pcVar1 = '\x01';
          fw_event_loop_push_delayed(PTR_APP_MasterConnectEvent_1_004a35a4,1,uVar4);
          iVar3 = FUN_0043d0ce();
          if (iVar3 << 0x1e < 0) {
            uVar6 = _ringLinkStateName(*pbVar2);
            FUN_0043d574(3,PTR_s_ble_master_004a3558,PTR_s_D__01_workspace_s200_ap510b_iar__004a3554
                         ,PTR_s_APP_MasterTryReconnectRingByScen_004a3550,0x653,
                         PTR_s__Ring__Scene__d__connect_queued__004a35a8,param_1,uVar4,uVar6);
          }
          iVar3 = FUN_0043d0ce();
          if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
            uVar6 = _ringLinkStateName(*pbVar2);
            compress_log_output(0xcc00000,PTR_s__ble_master__Ring__Scene__d__con_004a35ac,
                                PTR_s__ble_master__Ring__Scene__d__con_004a35ac,param_1,uVar4,uVar6)
            ;
          }
          uVar4 = 1;
        }
      }
      else {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(3,PTR_s_ble_master_004a3558,PTR_s_D__01_workspace_s200_ap510b_iar__004a3554,
                       PTR_s_APP_MasterTryReconnectRingByScen_004a3550,0x61c,
                       PTR_s__Ring__Scene__already_connected__004a3570);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0xc000000,PTR_s__ble_master__Ring__Scene__alread_004a3574,
                              PTR_s__ble_master__Ring__Scene__alread_004a3574);
        }
        uVar4 = 0;
      }
    }
  }
  return uVar4;
}

