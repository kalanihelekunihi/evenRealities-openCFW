
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int loggerSetting_common_data_handler(int param_1,undefined4 param_2,byte *param_3)

{
  byte bVar1;
  byte bVar2;
  undefined *puVar3;
  undefined1 *puVar4;
  undefined4 uVar5;
  int *piVar6;
  char cVar7;
  int iVar8;
  int iVar9;
  byte *pbVar10;
  undefined1 uVar11;
  uint uVar12;
  uint uStack_138;
  undefined *puStack_134;
  byte *pbStack_130;
  uint uStack_12c;
  undefined4 uStack_128;
  uint uStack_124;
  byte *pbStack_11c;
  undefined1 auStack_118 [12];
  byte *pbStack_10c;
  undefined1 auStack_108 [12];
  uint uStack_fc;
  undefined1 auStack_f4 [12];
  uint uStack_e8;
  undefined1 auStack_e0 [12];
  uint uStack_d4;
  byte abStack_cc [2];
  byte abStack_ca [62];
  byte abStack_8c [31];
  undefined1 uStack_6d;
  undefined1 auStack_6c [12];
  uint uStack_60;
  undefined1 auStack_58 [12];
  uint uStack_4c;
  undefined1 auStack_44 [12];
  uint uStack_38;
  undefined1 auStack_30 [20];
  
  iVar8 = FUN_0043d0ce();
  if (iVar8 << 0x1e < 0) {
    puStack_134 = PTR_s_loggerSetting_common_data_handle_00459f8c;
    uStack_138 = 0xde;
    pbStack_130 = param_3;
    FUN_0043d574(4,PTR_s_logger_setting_00459f98,PTR_s_D__01_workspace_s200_ap510b_iar__00459f94,
                 PTR_s_loggerSetting_common_data_handle_00459f90);
  }
  iVar8 = FUN_0043d0ce();
  if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
    compress_log_output(0x10400000,PTR_s__logger_setting_loggerSetting_co_00459f9c,
                        PTR_s__logger_setting_loggerSetting_co_00459f9c,param_3);
  }
  pbVar10 = _DAT_00459fa0;
  if (param_1 == 0) {
    FUN_0043c0e4(_DAT_00459fa0,0x508,0);
    FUN_0048f49c(&uStack_138,param_2,param_3);
    FUN_00439c04(auStack_118,&uStack_138,0x10);
    puVar3 = PTR_DAT_0045a05c;
    cVar7 = FUN_00490120(auStack_118,PTR_DAT_0045a05c,pbVar10);
    if (cVar7 == '\0') {
      iVar8 = FUN_0043d0ce();
      if (iVar8 << 0x1e < 0) {
        pbStack_130 = PTR_s__none__0045a060;
        if (pbStack_10c != (byte *)0x0) {
          pbStack_130 = pbStack_10c;
        }
        puStack_134 = PTR_s_loggerSetting_common_data_handle_0045a064;
        uStack_138 = 0xe4;
        FUN_0043d574(1,PTR_s_logger_setting_00459f98,PTR_s_D__01_workspace_s200_ap510b_iar__00459f94
                     ,PTR_s_loggerSetting_common_data_handle_00459f90);
      }
      iVar8 = FUN_0043d0ce();
      if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
        pbVar10 = PTR_s__none__0045a060;
        if (pbStack_10c != (byte *)0x0) {
          pbVar10 = pbStack_10c;
        }
        compress_log_output(0x4400000,PTR_s__logger_setting_loggerSetting_co_0045a068,
                            PTR_s__logger_setting_loggerSetting_co_0045a068,pbVar10);
      }
      return 0;
    }
    bVar2 = *pbVar10;
    bVar1 = pbVar10[1];
    iVar8 = FUN_0043d0ce();
    if (iVar8 << 0x1e < 0) {
      uStack_12c = (uint)bVar1;
      pbStack_130 = (byte *)(uint)bVar2;
      puStack_134 = PTR_s_loggerSetting_common_data_handle_0045a06c;
      uStack_138 = 0xea;
      FUN_0043d574(4,PTR_s_logger_setting_00459f98,PTR_s_D__01_workspace_s200_ap510b_iar__00459f94,
                   PTR_s_loggerSetting_common_data_handle_00459f90);
    }
    iVar8 = FUN_0043d0ce();
    if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
      uStack_138 = (uint)bVar1;
      compress_log_output(0x10800000,PTR_s__logger_setting_loggerSetting_co_0045a070,
                          PTR_s__logger_setting_loggerSetting_co_0045a070,bVar2);
    }
    if (bVar2 == 0) {
      iVar8 = FUN_0043d0ce();
      if (iVar8 << 0x1e < 0) {
        puStack_134 = _DAT_0045a164;
        uStack_138 = 0xed;
        FUN_0043d574(4,PTR_s_logger_setting_00459f98,PTR_s_D__01_workspace_s200_ap510b_iar__00459f94
                     ,PTR_s_loggerSetting_common_data_handle_00459f90);
      }
      iVar8 = FUN_0043d0ce();
      if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
        compress_log_output(0x10000000,_DAT_0045a168,_DAT_0045a168);
      }
    }
    else {
      if (bVar2 == 1) {
        iVar8 = FUN_0043d0ce();
        if (iVar8 << 0x1e < 0) {
          puStack_134 = _DAT_0045a1c8;
          uStack_138 = 0xf1;
          FUN_0043d574(4,PTR_s_logger_setting_00459f98,
                       PTR_s_D__01_workspace_s200_ap510b_iar__00459f94,
                       PTR_s_loggerSetting_common_data_handle_00459f90);
        }
        iVar8 = FUN_0043d0ce();
        if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
          compress_log_output(0x10000000,_DAT_0045a1cc,_DAT_0045a1cc);
        }
        if (*(short *)(pbVar10 + 2) != 3) {
          return 0;
        }
        if (*(int *)(pbVar10 + 4) == 1) {
          loggerSetting_set_ble_transmit(1);
          iVar8 = FUN_0043d0ce();
          if (iVar8 << 0x1e < 0) {
            puStack_134 = _DAT_0045a1c8;
            uStack_138 = 0xf5;
            FUN_0043d574(4,PTR_s_logger_setting_00459f98,
                         PTR_s_D__01_workspace_s200_ap510b_iar__00459f94,
                         PTR_s_loggerSetting_common_data_handle_00459f90);
          }
          iVar8 = FUN_0043d0ce();
          if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
            compress_log_output(0x10000000,_DAT_0045a1cc,_DAT_0045a1cc);
          }
        }
        else {
          loggerSetting_set_ble_transmit(0);
          iVar8 = FUN_0043d0ce();
          if (iVar8 << 0x1e < 0) {
            puStack_134 = _DAT_0045a1c8;
            uStack_138 = 0xf8;
            FUN_0043d574(4,PTR_s_logger_setting_00459f98,
                         PTR_s_D__01_workspace_s200_ap510b_iar__00459f94,
                         PTR_s_loggerSetting_common_data_handle_00459f90);
          }
          iVar8 = FUN_0043d0ce();
          if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
            compress_log_output(0x10000000,_DAT_0045a1cc,_DAT_0045a1cc);
          }
        }
        puVar4 = _DAT_0045a258;
        FUN_0043c0e4(_DAT_0045a258,0x508,0);
        uVar5 = _DAT_0045a25c;
        FUN_0043c0e4(_DAT_0045a25c,0x578,0);
        *puVar4 = 1;
        puVar4[1] = bVar1;
        *(undefined2 *)(puVar4 + 2) = 3;
        FUN_004905f4(auStack_30,uVar5,0x578);
        FUN_00439c04(auStack_44,auStack_30,0x14);
        iVar8 = FUN_00490c32(auStack_44,puVar3,puVar4);
        if (iVar8 == 0) {
          return 0;
        }
        iVar8 = Thread_MsgPbTxByBle(1,0xf,uVar5,uStack_38 & 0xffff);
      }
      else if (bVar2 == 2) {
        iVar8 = FUN_0043d0ce();
        if (iVar8 << 0x1e < 0) {
          puStack_134 = _DAT_0045a2a8;
          uStack_138 = 0x113;
          FUN_0043d574(4,PTR_s_logger_setting_00459f98,
                       PTR_s_D__01_workspace_s200_ap510b_iar__00459f94,
                       PTR_s_loggerSetting_common_data_handle_00459f90);
        }
        iVar8 = FUN_0043d0ce();
        if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
          compress_log_output(0x10000000,_DAT_0045a2ac,_DAT_0045a2ac);
        }
        if (*(short *)(pbVar10 + 2) != 4) {
          return 0;
        }
        iVar8 = FUN_0043d0ce();
        if (iVar8 << 0x1e < 0) {
          puStack_134 = _DAT_0045a2a8;
          uStack_138 = 0x115;
          FUN_0043d574(4,PTR_s_logger_setting_00459f98,
                       PTR_s_D__01_workspace_s200_ap510b_iar__00459f94,
                       PTR_s_loggerSetting_common_data_handle_00459f90);
        }
        iVar8 = FUN_0043d0ce();
        if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
          compress_log_output(0x10000000,_DAT_0045a2ac,_DAT_0045a2ac);
        }
        FUN_0043d3a6(*(uint *)(pbVar10 + 4) & 0xff);
        func_0x0043d0d4(*(uint *)(pbVar10 + 4) & 0xff);
        puVar4 = _DAT_0045a258;
        FUN_0043c0e4(_DAT_0045a258,0x508,0);
        uVar5 = _DAT_0045a25c;
        FUN_0043c0e4(_DAT_0045a25c,0x578,0);
        *puVar4 = 2;
        puVar4[1] = bVar1;
        *(undefined2 *)(puVar4 + 2) = 4;
        FUN_004905f4(auStack_30,uVar5,0x578);
        FUN_00439c04(auStack_58,auStack_30,0x14);
        iVar8 = FUN_00490c32(auStack_58,puVar3,puVar4);
        if (iVar8 == 0) {
          return 0;
        }
        iVar8 = Thread_MsgPbTxByBle(1,0xf,uVar5,uStack_4c & 0xffff);
      }
      else {
        if (bVar2 == 4) {
          iVar8 = FUN_0043d0ce();
          if (iVar8 << 0x1e < 0) {
            puStack_134 = PTR_s_loggerSetting_common_data_handle_0045a388;
            uStack_138 = 0x12d;
            FUN_0043d574(4,PTR_s_logger_setting_00459f98,
                         PTR_s_D__01_workspace_s200_ap510b_iar__00459f94,
                         PTR_s_loggerSetting_common_data_handle_00459f90);
          }
          iVar8 = FUN_0043d0ce();
          if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
            compress_log_output(0x10000000,PTR_s__logger_setting_loggerSetting_co_0045a38c,
                                PTR_s__logger_setting_loggerSetting_co_0045a38c);
          }
          ble_state_skip_manual_start(0);
          svc_compress_log_force_sync_to_files();
          iVar8 = scan_log_files();
          if (iVar8 != 0) {
            iVar8 = FUN_0043d0ce();
            if (iVar8 << 0x1e < 0) {
              puStack_134 = PTR_s_Failed_to_scan__log_directory_0045a46c;
              uStack_138 = 0x170;
              FUN_0043d574(1,PTR_s_logger_setting_00459f98,
                           PTR_s_D__01_workspace_s200_ap510b_iar__00459f94,
                           PTR_s_loggerSetting_common_data_handle_00459f90);
            }
            iVar8 = FUN_0043d0ce();
            if ((-1 < iVar8 << 0x1f) && (iVar8 = FUN_0043d0ce(), -1 < iVar8 << 0x1d)) {
              return 0;
            }
            compress_log_output(0x4000000,PTR_s__logger_setting_Failed_to_scan___0045a470,
                                PTR_s__logger_setting_Failed_to_scan___0045a470);
            return 0;
          }
          iVar8 = FUN_0043d0ce();
          if (iVar8 << 0x1e < 0) {
            pbStack_130 = *(byte **)(_DAT_00459d58 + 800);
            puStack_134 = PTR_s_Successfully_scanned__d_files_in_0045a390;
            uStack_138 = 0x136;
            FUN_0043d574(4,PTR_s_logger_setting_00459f98,
                         PTR_s_D__01_workspace_s200_ap510b_iar__00459f94,
                         PTR_s_loggerSetting_common_data_handle_00459f90);
          }
          iVar8 = FUN_0043d0ce();
          if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
            compress_log_output(0x10400000,PTR_s__logger_setting_Successfully_sca_0045a394,
                                PTR_s__logger_setting_Successfully_sca_0045a394,
                                *(undefined4 *)(_DAT_00459d58 + 800));
          }
          for (pbVar10 = (byte *)0x0; puVar4 = _DAT_0045a258, iVar8 = _DAT_00459d58,
              pbVar10 < *(byte **)(_DAT_00459d58 + 800); pbVar10 = pbVar10 + 1) {
            iVar9 = FUN_0043d0ce();
            if (iVar9 << 0x1e < 0) {
              uStack_124 = (uint)*(byte *)((int)pbVar10 * 0x28 + iVar8 + 0x24);
              uStack_128 = *(undefined4 *)((int)pbVar10 * 0x28 + iVar8 + 0x20);
              uStack_12c = (int)pbVar10 * 0x28 + iVar8;
              puStack_134 = PTR_s___d___s____d_bytes__type___d__0045a398;
              uStack_138 = 0x13e;
              pbStack_130 = pbVar10;
              FUN_0043d574(4,PTR_s_logger_setting_00459f98,
                           PTR_s_D__01_workspace_s200_ap510b_iar__00459f94,
                           PTR_s_loggerSetting_common_data_handle_00459f90);
            }
            iVar9 = FUN_0043d0ce();
            if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
              pbStack_130 = (byte *)(uint)*(byte *)((int)pbVar10 * 0x28 + iVar8 + 0x24);
              puStack_134 = *(undefined **)((int)pbVar10 * 0x28 + iVar8 + 0x20);
              uStack_138 = (int)pbVar10 * 0x28 + iVar8;
              compress_log_output(0x11000000,PTR_s__logger_setting____d___s____d_by_0045a39c,
                                  PTR_s__logger_setting____d___s____d_by_0045a39c,pbVar10);
            }
          }
          FUN_0043c0e4(_DAT_0045a258,0x508,0);
          uVar5 = _DAT_0045a25c;
          FUN_0043c0e4(_DAT_0045a25c,0x578,0);
          *puVar4 = 4;
          puVar4[1] = bVar1;
          *(undefined2 *)(puVar4 + 2) = 6;
          *(short *)(puVar4 + 4) = (short)*(undefined4 *)(iVar8 + 800);
          for (uVar12 = 0; uVar12 < *(uint *)(iVar8 + 800); uVar12 = uVar12 + 1) {
            iVar9 = FUN_0045a568(0x52);
            if (iVar9 == 1) {
              uVar11 = 0x52;
            }
            else {
              uVar11 = 0x4c;
            }
            simplify_log_filename(uVar12 * 0x28 + iVar8,uVar11,puVar4 + uVar12 * 0x20 + 6,0x20);
          }
          iVar8 = FUN_0045a568();
          piVar6 = _DAT_0045a464;
          if (iVar8 == 2) {
            FUN_004905f4(auStack_30,uVar5,0x578);
            FUN_00439c04(auStack_6c,auStack_30,0x14);
            iVar8 = FUN_00490c32(auStack_6c,puVar3,puVar4);
            if (iVar8 == 0) {
              iVar8 = FUN_0043d0ce();
              if (iVar8 << 0x1e < 0) {
                puStack_134 = PTR_s_loggerSetting_common_data_handle_0045a3a0;
                uStack_138 = 0x158;
                FUN_0043d574(1,PTR_s_logger_setting_00459f98,
                             PTR_s_D__01_workspace_s200_ap510b_iar__00459f94,
                             PTR_s_loggerSetting_common_data_handle_00459f90);
              }
              iVar8 = FUN_0043d0ce();
              if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
                compress_log_output(0x4000000,PTR_s__logger_setting_loggerSetting_co_0045a3a4,
                                    PTR_s__logger_setting_loggerSetting_co_0045a3a4);
              }
              return 0;
            }
            FUN_00454b4c(100);
            uStack_138 = 0xb;
            FUN_00465480(0xf,uVar5,uStack_60 & 0xffff,0);
            iVar8 = FUN_0043d0ce();
            if (iVar8 << 0x1e < 0) {
              puStack_134 = PTR_s_loggerSetting_common_data_handle_0045a3a8;
              uStack_138 = 0x161;
              FUN_0043d574(4,PTR_s_logger_setting_00459f98,
                           PTR_s_D__01_workspace_s200_ap510b_iar__00459f94,
                           PTR_s_loggerSetting_common_data_handle_00459f90);
            }
            iVar8 = FUN_0043d0ce();
            if ((-1 < iVar8 << 0x1f) && (iVar8 = FUN_0043d0ce(), -1 < iVar8 << 0x1d)) {
              return 0;
            }
            compress_log_output(0x10000000,PTR_s__logger_setting_loggerSetting_co_0045a3ac,
                                PTR_s__logger_setting_loggerSetting_co_0045a3ac);
            return 0;
          }
          *_DAT_0045a464 = 1;
          iVar8 = FUN_0043d0ce();
          if (iVar8 << 0x1e < 0) {
            pbStack_130 = (byte *)*piVar6;
            puStack_134 = PTR_s_master_file_list_stored_flag_____0045a3b0;
            uStack_138 = 0x164;
            FUN_0043d574(4,PTR_s_logger_setting_00459f98,
                         PTR_s_D__01_workspace_s200_ap510b_iar__00459f94,
                         PTR_s_loggerSetting_common_data_handle_00459f90);
          }
          iVar8 = FUN_0043d0ce();
          if ((-1 < iVar8 << 0x1f) && (iVar8 = FUN_0043d0ce(), -1 < iVar8 << 0x1d)) {
            return 0;
          }
          compress_log_output(0x10400000,PTR_s__logger_setting_master_file_list_0045a468,
                              PTR_s__logger_setting_master_file_list_0045a468,*piVar6);
          return 0;
        }
        if (bVar2 == 5) {
          if (*(short *)(pbVar10 + 2) != 7) {
            return 0;
          }
          iVar8 = FUN_0043d0ce();
          if (iVar8 << 0x1e < 0) {
            puStack_134 = PTR_s_receive_delete_file_name_request_0045a474;
            uStack_138 = 0x179;
            FUN_0043d574(3,PTR_s_logger_setting_00459f98,
                         PTR_s_D__01_workspace_s200_ap510b_iar__00459f94,
                         PTR_s_loggerSetting_common_data_handle_00459f90);
          }
          iVar8 = FUN_0043d0ce();
          if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
            compress_log_output(0xc000000,PTR_s__logger_setting_receive_delete_f_0045a478,
                                PTR_s__logger_setting_receive_delete_f_0045a478);
          }
          FUN_0044b5a0(abStack_8c,pbVar10 + 4,0x1f);
          uStack_6d = 0;
          FUN_0044b728(abStack_cc,0x40,0x459d5c,abStack_8c);
          pbVar10 = (byte *)0x0;
          iVar8 = FUN_0045a568();
          if (iVar8 == 2) {
            iVar8 = FUN_0044b610(abStack_cc,PTR_s_L__log__0045a47c,7);
            if (iVar8 != 0) {
              iVar8 = FUN_0043d0ce();
              if (iVar8 << 0x1e < 0) {
                pbStack_130 = abStack_cc;
                puStack_134 = PTR_s_not_slave_file_path__current_pat_0045a480;
                uStack_138 = 0x186;
                FUN_0043d574(4,PTR_s_logger_setting_00459f98,
                             PTR_s_D__01_workspace_s200_ap510b_iar__00459f94,
                             PTR_s_loggerSetting_common_data_handle_00459f90);
              }
              iVar8 = FUN_0043d0ce();
              if ((-1 < iVar8 << 0x1f) && (iVar8 = FUN_0043d0ce(), -1 < iVar8 << 0x1d)) {
                return 0;
              }
              compress_log_output(0x10400000,PTR_s__logger_setting_not_slave_file_p_0045a484,
                                  PTR_s__logger_setting_not_slave_file_p_0045a484,abStack_cc);
              return 0;
            }
            pbVar10 = abStack_ca;
          }
          else {
            iVar8 = FUN_0045a568();
            if (iVar8 == 1) {
              iVar8 = FUN_0044b610(abStack_cc,PTR_s_R__log__0045a488,7);
              if (iVar8 != 0) {
                iVar8 = FUN_0043d0ce();
                if (iVar8 << 0x1e < 0) {
                  pbStack_130 = abStack_cc;
                  puStack_134 = PTR_s_not_master_file_path__current_pa_0045a48c;
                  uStack_138 = 0x18c;
                  FUN_0043d574(4,PTR_s_logger_setting_00459f98,
                               PTR_s_D__01_workspace_s200_ap510b_iar__00459f94,
                               PTR_s_loggerSetting_common_data_handle_00459f90);
                }
                iVar8 = FUN_0043d0ce();
                if ((-1 < iVar8 << 0x1f) && (iVar8 = FUN_0043d0ce(), -1 < iVar8 << 0x1d)) {
                  return 0;
                }
                compress_log_output(0x10400000,PTR_s__logger_setting_not_master_file_p_0045a490,
                                    PTR_s__logger_setting_not_master_file_p_0045a490,abStack_cc);
                return 0;
              }
              pbVar10 = abStack_ca;
            }
          }
          iVar8 = FUN_0043d0ce();
          if (iVar8 << 0x1e < 0) {
            puStack_134 = PTR_s_loggerSetting_delete_file___s_0045a494;
            uStack_138 = 0x191;
            pbStack_130 = pbVar10;
            FUN_0043d574(3,PTR_s_logger_setting_00459f98,
                         PTR_s_D__01_workspace_s200_ap510b_iar__00459f94,
                         PTR_s_loggerSetting_common_data_handle_00459f90);
          }
          iVar8 = FUN_0043d0ce();
          if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
            compress_log_output(0xc400000,PTR_s__logger_setting_loggerSetting_de_0045a498,
                                PTR_s__logger_setting_loggerSetting_de_0045a498,pbVar10);
          }
          iVar8 = file_remove(pbVar10);
          if (iVar8 == 0) {
            iVar8 = FUN_0043d0ce();
            if (iVar8 << 0x1e < 0) {
              puStack_134 = PTR_s_loggerSetting_delete_file_succes_0045a4a4;
              uStack_138 = 0x196;
              pbStack_130 = pbVar10;
              FUN_0043d574(4,PTR_s_logger_setting_00459f98,
                           PTR_s_D__01_workspace_s200_ap510b_iar__00459f94,
                           PTR_s_loggerSetting_common_data_handle_00459f90);
            }
            iVar8 = FUN_0043d0ce();
            if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
              compress_log_output(0x10400000,PTR_s__logger_setting_loggerSetting_de_0045a4a8,
                                  PTR_s__logger_setting_loggerSetting_de_0045a4a8,pbVar10);
            }
          }
          else {
            iVar8 = FUN_0043d0ce();
            if (iVar8 << 0x1e < 0) {
              puStack_134 = PTR_s_loggerSetting_delete_file_failed_0045a49c;
              uStack_138 = 0x194;
              pbStack_130 = pbVar10;
              FUN_0043d574(1,PTR_s_logger_setting_00459f98,
                           PTR_s_D__01_workspace_s200_ap510b_iar__00459f94,
                           PTR_s_loggerSetting_common_data_handle_00459f90);
            }
            iVar8 = FUN_0043d0ce();
            if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
              compress_log_output(0x4400000,PTR_s__logger_setting_loggerSetting_de_0045a4a0,
                                  PTR_s__logger_setting_loggerSetting_de_0045a4a0,pbVar10);
            }
          }
          puVar4 = _DAT_0045a258;
          FUN_0043c0e4(_DAT_0045a258,0x508,0);
          uVar5 = _DAT_0045a25c;
          FUN_0043c0e4(_DAT_0045a25c,0x578,0);
          *puVar4 = 5;
          puVar4[1] = bVar1;
          *(undefined2 *)(puVar4 + 2) = 7;
          FUN_0044b5a0(puVar4 + 4,abStack_8c,0x1f);
          puVar4[0x23] = 0;
          FUN_004905f4(auStack_30,uVar5,0x578);
          FUN_00439c04(auStack_108,auStack_30,0x14);
          iVar8 = FUN_00490c32(auStack_108,puVar3,puVar4);
          if (iVar8 == 0) {
            return 0;
          }
          iVar8 = FUN_0045a568();
          if (iVar8 == 2) {
            iVar8 = FUN_0043d0ce();
            if (iVar8 << 0x1e < 0) {
              uStack_12c = uStack_fc;
              pbStack_130 = abStack_8c;
              puStack_134 = PTR_s_loggerSetting_slave_send_delete_r_0045a4ac;
              uStack_138 = 0x1a8;
              FUN_0043d574(4,PTR_s_logger_setting_00459f98,
                           PTR_s_D__01_workspace_s200_ap510b_iar__00459f94,
                           PTR_s_loggerSetting_common_data_handle_00459f90);
            }
            iVar8 = FUN_0043d0ce();
            if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
              uStack_138 = uStack_fc;
              compress_log_output(0x10800000,PTR_s__logger_setting_loggerSetting_sl_0045a4b0,
                                  PTR_s__logger_setting_loggerSetting_sl_0045a4b0,abStack_8c);
            }
            uStack_138 = 0xc;
            iVar8 = FUN_00465480(0xf,uVar5,uStack_fc & 0xffff,0);
            if (iVar8 == 0) {
              return 0;
            }
            iVar9 = FUN_0043d0ce();
            if (iVar9 << 0x1e < 0) {
              puStack_134 = PTR_s_loggerSetting_slave_send_delete_r_0045a4b4;
              uStack_138 = 0x1ac;
              FUN_0043d574(1,PTR_s_logger_setting_00459f98,
                           PTR_s_D__01_workspace_s200_ap510b_iar__00459f94,
                           PTR_s_loggerSetting_common_data_handle_00459f90);
            }
            iVar9 = FUN_0043d0ce();
            if ((-1 < iVar9 << 0x1f) && (iVar9 = FUN_0043d0ce(), -1 < iVar9 << 0x1d)) {
              return iVar8;
            }
            compress_log_output(0x4000000,PTR_s__logger_setting_loggerSetting_sl_0045a4b8,
                                PTR_s__logger_setting_loggerSetting_sl_0045a4b8);
            return iVar8;
          }
          iVar8 = Thread_MsgPbTxByBle(1,0xf,uVar5,uStack_fc & 0xffff);
        }
        else {
          if (bVar2 != 6) {
            iVar8 = FUN_0043d0ce();
            if (iVar8 << 0x1e < 0) {
              pbStack_130 = (byte *)(uint)bVar2;
              puStack_134 = PTR_s_sync_info_data_handler__unknown_c_0045a4d8;
              uStack_138 = 0x1d2;
              FUN_0043d574(2,PTR_s_logger_setting_00459f98,
                           PTR_s_D__01_workspace_s200_ap510b_iar__00459f94,
                           PTR_s_loggerSetting_common_data_handle_00459f90);
            }
            iVar8 = FUN_0043d0ce();
            if ((-1 < iVar8 << 0x1f) && (iVar8 = FUN_0043d0ce(), -1 < iVar8 << 0x1d)) {
              return 0;
            }
            compress_log_output(0x8400000,PTR_s__logger_setting_sync_info_data_h_0045a4dc,
                                PTR_s__logger_setting_sync_info_data_h_0045a4dc,bVar2);
            return 0;
          }
          iVar8 = FUN_0043d0ce();
          if (iVar8 << 0x1e < 0) {
            puStack_134 = PTR_s_receive_delete_all_logger_file_r_0045a4bc;
            uStack_138 = 0x1ba;
            FUN_0043d574(3,PTR_s_logger_setting_00459f98,
                         PTR_s_D__01_workspace_s200_ap510b_iar__00459f94,
                         PTR_s_loggerSetting_common_data_handle_00459f90);
          }
          iVar8 = FUN_0043d0ce();
          if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
            compress_log_output(0xc000000,PTR_s__logger_setting_receive_delete_a_0045a4c0,
                                PTR_s__logger_setting_receive_delete_a_0045a4c0);
          }
          pbVar10 = (byte *)delete_all_files_in_dir(PTR_DAT_0045a4c4);
          if ((int)pbVar10 < 0) {
            iVar8 = FUN_0043d0ce();
            if (iVar8 << 0x1e < 0) {
              puStack_134 = PTR_s_loggerSetting_delete_all_logger_f_0045a4c8;
              uStack_138 = 0x1bd;
              FUN_0043d574(1,PTR_s_logger_setting_00459f98,
                           PTR_s_D__01_workspace_s200_ap510b_iar__00459f94,
                           PTR_s_loggerSetting_common_data_handle_00459f90);
            }
            iVar8 = FUN_0043d0ce();
            if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
              compress_log_output(0x4000000,PTR_s__logger_setting_loggerSetting_de_0045a4cc,
                                  PTR_s__logger_setting_loggerSetting_de_0045a4cc);
            }
          }
          else {
            iVar8 = FUN_0043d0ce();
            if (iVar8 << 0x1e < 0) {
              puStack_134 = PTR_s_loggerSetting_deleted__d_files_s_0045a4d0;
              uStack_138 = 0x1bf;
              pbStack_130 = pbVar10;
              FUN_0043d574(4,PTR_s_logger_setting_00459f98,
                           PTR_s_D__01_workspace_s200_ap510b_iar__00459f94,
                           PTR_s_loggerSetting_common_data_handle_00459f90);
            }
            iVar8 = FUN_0043d0ce();
            if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
              compress_log_output(0x10400000,PTR_s__logger_setting_loggerSetting_de_0045a4d4,
                                  PTR_s__logger_setting_loggerSetting_de_0045a4d4,pbVar10);
            }
          }
          puVar4 = _DAT_0045a258;
          FUN_0043c0e4(_DAT_0045a258,0x508,0);
          uVar5 = _DAT_0045a25c;
          FUN_0043c0e4(_DAT_0045a25c,0x578,0);
          puVar4[1] = bVar1;
          *puVar4 = 6;
          FUN_004905f4(auStack_30,uVar5,0x578);
          FUN_00439c04(auStack_e0,auStack_30,0x14);
          iVar8 = FUN_00490c32(auStack_e0,puVar3,puVar4);
          if (iVar8 == 0) {
            return 0;
          }
          iVar8 = Thread_MsgPbTxByBle(1,0xf,uVar5,uStack_d4 & 0xffff);
        }
      }
      if (iVar8 != 0) {
        return iVar8;
      }
    }
  }
  else if (param_1 == 0xb) {
    FUN_0043c0e4(_DAT_00459fa0,0x508,0);
    FUN_0048f49c(&uStack_138,param_2,param_3);
    FUN_00439c04(&uStack_128,&uStack_138,0x10);
    puVar3 = PTR_DAT_0045a05c;
    cVar7 = FUN_00490120(&uStack_128,PTR_DAT_0045a05c,pbVar10);
    if (cVar7 == '\0') {
      iVar8 = FUN_0043d0ce();
      if (iVar8 << 0x1e < 0) {
        pbStack_130 = PTR_s__none__0045a060;
        if (pbStack_11c != (byte *)0x0) {
          pbStack_130 = pbStack_11c;
        }
        puStack_134 = PTR_s_loggerSetting_common_data_handle_0045a064;
        uStack_138 = 0x1db;
        FUN_0043d574(1,PTR_s_logger_setting_00459f98,PTR_s_D__01_workspace_s200_ap510b_iar__00459f94
                     ,PTR_s_loggerSetting_common_data_handle_00459f90);
      }
      iVar8 = FUN_0043d0ce();
      if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
        pbVar10 = PTR_s__none__0045a060;
        if (pbStack_11c != (byte *)0x0) {
          pbVar10 = pbStack_11c;
        }
        compress_log_output(0x4400000,PTR_s__logger_setting_loggerSetting_co_0045a068,
                            PTR_s__logger_setting_loggerSetting_co_0045a068,pbVar10);
      }
      return 0;
    }
    bVar1 = *pbVar10;
    bVar2 = pbVar10[1];
    iVar8 = FUN_0043d0ce();
    if (iVar8 << 0x1e < 0) {
      uStack_12c = (uint)bVar2;
      pbStack_130 = (byte *)(uint)bVar1;
      puStack_134 = PTR_s_loggerSetting_common_data_handle_0045a06c;
      uStack_138 = 0x1e0;
      FUN_0043d574(4,PTR_s_logger_setting_0045a4e8,PTR_s_D__01_workspace_s200_ap510b_iar__0045a4e4,
                   PTR_s_loggerSetting_common_data_handle_0045a4e0);
    }
    iVar8 = FUN_0043d0ce();
    if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
      uStack_138 = (uint)bVar2;
      compress_log_output(0x10800000,PTR_s__logger_setting_loggerSetting_co_0045a070,
                          PTR_s__logger_setting_loggerSetting_co_0045a070,bVar1);
    }
    piVar6 = _DAT_0045a464;
    if (bVar1 == 4) {
      if (*_DAT_0045a464 == 1) {
        iVar8 = FUN_0043d0ce();
        if (iVar8 << 0x1e < 0) {
          puStack_134 = PTR_s_loggerSetting_common_data_handle_0045a4ec;
          uStack_138 = 0x1e4;
          FUN_0043d574(4,PTR_s_logger_setting_0045a4e8,
                       PTR_s_D__01_workspace_s200_ap510b_iar__0045a4e4,
                       PTR_s_loggerSetting_common_data_handle_0045a4e0);
        }
        iVar8 = FUN_0043d0ce();
        if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
          compress_log_output(0x10000000,PTR_s__logger_setting_loggerSetting_co_0045a4f0,
                              PTR_s__logger_setting_loggerSetting_co_0045a4f0);
        }
        for (iVar8 = 0; puVar4 = _DAT_0045a258, iVar8 < (int)(uint)*(ushort *)(pbVar10 + 4);
            iVar8 = iVar8 + 1) {
          iVar9 = FUN_0043d0ce();
          if (iVar9 << 0x1e < 0) {
            pbStack_130 = pbVar10 + iVar8 * 0x20 + 6;
            puStack_134 = PTR_s_loggerSetting_common_data_handle_0045a4f4;
            uStack_138 = 0x1e6;
            FUN_0043d574(4,PTR_s_logger_setting_0045a4e8,
                         PTR_s_D__01_workspace_s200_ap510b_iar__0045a4e4,
                         PTR_s_loggerSetting_common_data_handle_0045a4e0);
          }
          iVar9 = FUN_0043d0ce();
          if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
            compress_log_output(0x10400000,PTR_s__logger_setting_loggerSetting_co_0045a4f8,
                                PTR_s__logger_setting_loggerSetting_co_0045a4f8,
                                pbVar10 + iVar8 * 0x20 + 6);
          }
          FUN_00439be4(_DAT_0045a258 + (iVar8 + (uint)*(ushort *)(_DAT_0045a258 + 4)) * 0x20 + 6,
                       pbVar10 + iVar8 * 0x20 + 6,0x20);
        }
        *(short *)(_DAT_0045a258 + 4) = *(short *)(pbVar10 + 4) + *(short *)(_DAT_0045a258 + 4);
        uVar5 = _DAT_0045a25c;
        FUN_004905f4(auStack_30,_DAT_0045a25c,0x578);
        FUN_00439c04(auStack_f4,auStack_30,0x14);
        iVar8 = FUN_00490c32(auStack_f4,puVar3,puVar4);
        if (iVar8 == 0) {
          iVar8 = FUN_0043d0ce();
          if (iVar8 << 0x1e < 0) {
            puStack_134 = PTR_s_loggerSetting_protobuf_encode_fa_0045a4fc;
            uStack_138 = 0x1ed;
            FUN_0043d574(1,PTR_s_logger_setting_0045a4e8,
                         PTR_s_D__01_workspace_s200_ap510b_iar__0045a4e4,
                         PTR_s_loggerSetting_common_data_handle_0045a4e0);
          }
          iVar8 = FUN_0043d0ce();
          if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
            compress_log_output(0x4000000,PTR_s__logger_setting_loggerSetting_pr_0045a500,
                                PTR_s__logger_setting_loggerSetting_pr_0045a500);
          }
          return 0;
        }
        iVar8 = Thread_MsgPbTxByBle(1,0xf,uVar5,uStack_e8 & 0xffff);
        if (iVar8 != 0) {
          iVar9 = FUN_0043d0ce();
          if (iVar9 << 0x1e < 0) {
            puStack_134 = PTR_s_loggerSetting_send_file_list_to_m_0045a504;
            uStack_138 = 500;
            FUN_0043d574(1,PTR_s_logger_setting_0045a4e8,
                         PTR_s_D__01_workspace_s200_ap510b_iar__0045a4e4,
                         PTR_s_loggerSetting_common_data_handle_0045a4e0);
          }
          iVar9 = FUN_0043d0ce();
          if ((-1 < iVar9 << 0x1f) && (iVar9 = FUN_0043d0ce(), -1 < iVar9 << 0x1d)) {
            return iVar8;
          }
          compress_log_output(0x4000000,PTR_s__logger_setting_loggerSetting_se_0045a508,
                              PTR_s__logger_setting_loggerSetting_se_0045a508);
          return iVar8;
        }
        iVar8 = FUN_0043d0ce();
        if (iVar8 << 0x1e < 0) {
          puStack_134 = PTR_s_loggerSetting_send_file_list_to_m_0045a50c;
          uStack_138 = 0x1f7;
          FUN_0043d574(4,PTR_s_logger_setting_0045a4e8,
                       PTR_s_D__01_workspace_s200_ap510b_iar__0045a4e4,
                       PTR_s_loggerSetting_common_data_handle_0045a4e0);
        }
        iVar8 = FUN_0043d0ce();
        if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
          compress_log_output(0x10000000,PTR_s__logger_setting_loggerSetting_se_0045a510,
                              PTR_s__logger_setting_loggerSetting_se_0045a510);
        }
        *piVar6 = 0;
      }
      else {
        iVar8 = FUN_0045a568();
        if (iVar8 == 1) {
          iVar8 = FUN_0043d0ce();
          if (iVar8 << 0x1e < 0) {
            puStack_134 = PTR_s_loggerSetting_common_data_handle_0045a514;
            uStack_138 = 0x1fd;
            FUN_0043d574(2,PTR_s_logger_setting_0045a4e8,
                         PTR_s_D__01_workspace_s200_ap510b_iar__0045a4e4,
                         PTR_s_loggerSetting_common_data_handle_0045a4e0);
          }
          iVar8 = FUN_0043d0ce();
          if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
            compress_log_output(0x8000000,PTR_s__logger_setting_loggerSetting_co_0045a518,
                                PTR_s__logger_setting_loggerSetting_co_0045a518);
          }
        }
      }
    }
    else {
      iVar8 = FUN_0043d0ce();
      if (iVar8 << 0x1e < 0) {
        pbStack_130 = (byte *)(uint)bVar1;
        puStack_134 = PTR_s_loggerSetting_common_data_handle_0045a51c;
        uStack_138 = 0x204;
        FUN_0043d574(2,PTR_s_logger_setting_0045a4e8,PTR_s_D__01_workspace_s200_ap510b_iar__0045a4e4
                     ,PTR_s_loggerSetting_common_data_handle_0045a4e0);
      }
      iVar8 = FUN_0043d0ce();
      if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
        compress_log_output(0x8400000,PTR_s__logger_setting_loggerSetting_co_0045a520,
                            PTR_s__logger_setting_loggerSetting_co_0045a520,bVar1);
      }
    }
  }
  else if (param_1 == 0xc) {
    iVar8 = FUN_0043d0ce();
    if (iVar8 << 0x1e < 0) {
      puStack_134 = PTR_s_master_recv_slave_delete_result__0045a524;
      uStack_138 = 0x209;
      pbStack_130 = param_3;
      FUN_0043d574(3,PTR_s_logger_setting_0045a4e8,PTR_s_D__01_workspace_s200_ap510b_iar__0045a4e4,
                   PTR_s_loggerSetting_common_data_handle_0045a4e0);
    }
    iVar8 = FUN_0043d0ce();
    if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
      compress_log_output(0xc400000,PTR_s__logger_setting_master_recv_slav_0045a528,
                          PTR_s__logger_setting_master_recv_slav_0045a528,param_3);
    }
    iVar8 = Thread_MsgPbTxByBle(1,0xf,param_2,(uint)param_3 & 0xffff);
    if (iVar8 != 0) {
      iVar9 = FUN_0043d0ce();
      if (iVar9 << 0x1e < 0) {
        puStack_134 = PTR_s_loggerSetting_master_forward_sla_0045a52c;
        uStack_138 = 0x20c;
        FUN_0043d574(1,PTR_s_logger_setting_0045a4e8,PTR_s_D__01_workspace_s200_ap510b_iar__0045a4e4
                     ,PTR_s_loggerSetting_common_data_handle_0045a4e0);
      }
      iVar9 = FUN_0043d0ce();
      if ((-1 < iVar9 << 0x1f) && (iVar9 = FUN_0043d0ce(), -1 < iVar9 << 0x1d)) {
        return iVar8;
      }
      compress_log_output(0x4000000,PTR_s__logger_setting_loggerSetting_ma_0045a530,
                          PTR_s__logger_setting_loggerSetting_ma_0045a530);
      return iVar8;
    }
    iVar8 = FUN_0043d0ce();
    if (iVar8 << 0x1e < 0) {
      puStack_134 = PTR_s_loggerSetting_master_forward_sla_0045a534;
      uStack_138 = 0x20f;
      FUN_0043d574(3,PTR_s_logger_setting_0045a4e8,PTR_s_D__01_workspace_s200_ap510b_iar__0045a4e4,
                   PTR_s_loggerSetting_common_data_handle_0045a4e0);
    }
    iVar8 = FUN_0043d0ce();
    if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
      compress_log_output(0xc000000,PTR_s__logger_setting_loggerSetting_ma_0045a538,
                          PTR_s__logger_setting_loggerSetting_ma_0045a538);
    }
  }
  return 0;
}

