
void _efsFileCmdParse(byte param_1,int *param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 *puVar1;
  int *piVar2;
  undefined4 uVar3;
  int iVar4;
  undefined *puVar5;
  int iVar6;
  int iVar7;
  undefined *puVar8;
  undefined1 auStack_20 [4];
  undefined4 uStack_1c;
  
  uStack_1c = param_4;
  FUN_0043c0e4(auStack_20,2,0);
  puVar1 = DAT_004578e8;
  iVar6 = -1;
  if (param_1 == 0) {
    uVar3 = osKernelGetTickCount(0);
    *puVar1 = uVar3;
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      FUN_0043d574(4,PTR_s_efs_service_004578f8,PTR_s_D__01_workspace_s200_ap510b_iar__004578f4,
                   PTR_s__efsFileCmdParse_004578f0,0x15b,
                   PTR_s_eEvenFileSendServiceCID_EVEN_FIL_004578ec,*puVar1);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_00457960,DAT_00457960,*puVar1);
    }
    APP_ConnectParamOTASetFastMode();
    fw_event_loop_remove_delayed(DAT_00457964);
    piVar2 = DAT_00457968;
    if ((char)DAT_00457968[1] == '\x01') {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        FUN_0043d574(2,PTR_s_efs_service_004578f8,PTR_s_D__01_workspace_s200_ap510b_iar__004578f4,
                     PTR_s__efsFileCmdParse_004578f0,0x160,DAT_0045796c);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x8000000,PTR_s__efs_service_file_is_open__close_004579bc,
                            PTR_s__efs_service_file_is_open__close_004579bc);
      }
      if (*piVar2 == 0) {
        iVar4 = 0;
      }
      else {
        iVar4 = file_close(*piVar2);
        *piVar2 = 0;
      }
      if (iVar4 < 0) {
        iVar6 = FUN_0043d0ce();
        if (iVar6 << 0x1e < 0) {
          FUN_0043d574(1,PTR_s_efs_service_004578f8,PTR_s_D__01_workspace_s200_ap510b_iar__004578f4,
                       PTR_s__efsFileCmdParse_004578f0,0x163,DAT_00457560,(int)piVar2 + 5,iVar4);
        }
        iVar6 = FUN_0043d0ce();
        if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
          compress_log_output(0x4800000,DAT_004575dc,DAT_004575dc,(int)piVar2 + 5,iVar4);
        }
        _evenEfsReplyToAPP(0xc4,0,1);
        return;
      }
    }
    FUN_0043c0e4(piVar2,0x78,0);
    piVar2[0x16] = *param_2;
    piVar2[0x17] = param_2[1];
    piVar2[0x18] = param_2[2];
    puVar8 = (undefined *)((int)piVar2 + 5);
    FUN_0044b5a0(puVar8,param_2 + 3,0x50);
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      FUN_0043d574(4,PTR_s_efs_service_004578f8,PTR_s_D__01_workspace_s200_ap510b_iar__004578f4,
                   PTR_s__efsFileCmdParse_004578f0,0x16f,PTR_s_fileType___0x_x_004579c0,piVar2[0x16]
                  );
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x10400000,PTR_s__efs_service_fileType___0x_x_004579c4,
                          PTR_s__efs_service_fileType___0x_x_004579c4,piVar2[0x16]);
    }
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      FUN_0043d574(4,PTR_s_efs_service_004578f8,PTR_s_D__01_workspace_s200_ap510b_iar__004578f4,
                   PTR_s__efsFileCmdParse_004578f0,0x170,PTR_s_fileSize___0x_x_004579c8,piVar2[0x17]
                  );
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x10400000,PTR_s__efs_service_fileSize___0x_x_004579cc,
                          PTR_s__efs_service_fileSize___0x_x_004579cc,piVar2[0x17]);
    }
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      FUN_0043d574(4,PTR_s_efs_service_004578f8,PTR_s_D__01_workspace_s200_ap510b_iar__004578f4,
                   PTR_s__efsFileCmdParse_004578f0,0x171,PTR_s_rxFileCrc___0x_x_004579d0,
                   piVar2[0x18]);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x10400000,PTR_s__efs_service_rxFileCrc___0x_x_004579d4,
                          PTR_s__efs_service_rxFileCrc___0x_x_004579d4,piVar2[0x18]);
    }
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      FUN_0043d574(4,PTR_s_efs_service_004578f8,PTR_s_D__01_workspace_s200_ap510b_iar__004578f4,
                   PTR_s__efsFileCmdParse_004578f0,0x172,PTR_s_filePath____s_004579d8,puVar8);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x10400000,PTR_s__efs_service_filePath____s_004579dc,
                          PTR_s__efs_service_filePath____s_004579dc,puVar8);
    }
    iVar4 = piVar2[0x16];
    if (iVar4 == 0) {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        FUN_0043d574(4,PTR_s_efs_service_004578f8,PTR_s_D__01_workspace_s200_ap510b_iar__004578f4,
                     PTR_s__efsFileCmdParse_004578f0,0x176,
                     PTR_s_eEvenFileServiceType_NOTIFICATIO_004579e0);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x10000000,PTR_s__efs_service_eEvenFileServiceTyp_004579e4,
                            PTR_s__efs_service_eEvenFileServiceTyp_004579e4);
      }
      puVar5 = PTR_s_user_notify_whitelist_json_004579e8;
      FUN_0044b5a0(puVar8,PTR_s_user_notify_whitelist_json_004579e8,0x1a);
    }
    else if (iVar4 == 1) {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        FUN_0043d574(4,PTR_s_efs_service_004578f8,PTR_s_D__01_workspace_s200_ap510b_iar__004578f4,
                     PTR_s__efsFileCmdParse_004578f0,0x17d,
                     PTR_s_eEvenFileServiceType_ANDROID_MSG_004579fc,piVar2[0x17],0x2137);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x10800000,PTR_s__efs_service_eEvenFileServiceTyp_00457a00,
                            PTR_s__efs_service_eEvenFileServiceTyp_00457a00,piVar2[0x17],0x2137);
      }
      puVar1 = DAT_00457a04;
      if (0x2136 < (uint)piVar2[0x17]) {
        iVar6 = FUN_0043d0ce();
        if (iVar6 << 0x1e < 0) {
          FUN_0043d574(1,PTR_s_efs_service_004578f8,PTR_s_D__01_workspace_s200_ap510b_iar__004578f4,
                       PTR_s__efsFileCmdParse_004578f0,0x183,PTR_s_fileSize_is_too_large_00457a08);
        }
        iVar6 = FUN_0043d0ce();
        if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
          compress_log_output(0x4000000,PTR_s__efs_service_fileSize_is_too_lar_00457a0c,
                              PTR_s__efs_service_fileSize_is_too_lar_00457a0c);
        }
        _evenEfsReplyToAPP(0xc4,0,1);
        return;
      }
      uVar3 = FUN_0048e0a8();
      *puVar1 = uVar3;
      FUN_0043c0e4(*puVar1,0x2137,0);
      puVar5 = (undefined *)0x0;
    }
    else {
      if ((iVar4 == 2) || (iVar4 == 3)) {
        iVar6 = FUN_0043d0ce();
        if (iVar6 << 0x1e < 0) {
          FUN_0043d574(2,PTR_s_efs_service_004578f8,PTR_s_D__01_workspace_s200_ap510b_iar__004578f4,
                       PTR_s__efsFileCmdParse_004578f0,0x192,
                       PTR_s_fileType_0x_x_is_export_only_00457a18,piVar2[0x16]);
        }
        iVar6 = FUN_0043d0ce();
        if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
          compress_log_output(0x8400000,PTR_s__efs_service_fileType_0x_x_is_ex_00457a1c,
                              PTR_s__efs_service_fileType_0x_x_is_ex_00457a1c,piVar2[0x16]);
        }
        _evenEfsReplyToAPP(0xc4,0,1);
        return;
      }
      if (iVar4 != 0xaa) {
        return;
      }
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        FUN_0043d574(4,PTR_s_efs_service_004578f8,PTR_s_D__01_workspace_s200_ap510b_iar__004578f4,
                     PTR_s__efsFileCmdParse_004578f0,0x18b,
                     PTR_s_eEvenFileServiceType_OTHER_FILE_00457a10);
      }
      iVar4 = FUN_0043d0ce();
      puVar5 = puVar8;
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x10000000,PTR_s__efs_service_eEvenFileServiceTyp_00457a14,
                            PTR_s__efs_service_eEvenFileServiceTyp_00457a14);
      }
    }
    if (puVar5 != (undefined *)0x0) {
      uVar3 = FUN_0044a43c(puVar5);
      iVar4 = FUN_0044b610(puVar8,puVar5,uVar3);
      if (iVar4 == 0) {
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          FUN_0043d574(3,PTR_s_efs_service_004578f8,PTR_s_D__01_workspace_s200_ap510b_iar__004578f4,
                       PTR_s__efsFileCmdParse_004578f0,0x19e,PTR_s_pTargetPath____s_004579ec,puVar8)
          ;
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0xc400000,PTR_s__efs_service_pTargetPath____s_004579f0,
                              PTR_s__efs_service_pTargetPath____s_004579f0,puVar8);
        }
        iVar4 = file_remove(puVar8);
        if ((iVar4 < 0) && (iVar4 != -2)) {
          iVar7 = FUN_0043d0ce();
          if (iVar7 << 0x1e < 0) {
            FUN_0043d574(1,PTR_s_efs_service_004578f8,
                         PTR_s_D__01_workspace_s200_ap510b_iar__004578f4,
                         PTR_s__efsFileCmdParse_004578f0,0x1a2,
                         PTR_s_ERR_Delete_failed__s____d_004579f4,puVar8,iVar4);
          }
          iVar7 = FUN_0043d0ce();
          if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
            compress_log_output(0x4800000,PTR_s__efs_service_ERR_Delete_failed___004579f8,
                                PTR_s__efs_service_ERR_Delete_failed___004579f8,puVar8,iVar4);
          }
        }
        else if (iVar4 == 0) {
          iVar4 = FUN_0043d0ce();
          if (iVar4 << 0x1e < 0) {
            FUN_0043d574(4,PTR_s_efs_service_004578f8,
                         PTR_s_D__01_workspace_s200_ap510b_iar__004578f4,
                         PTR_s__efsFileCmdParse_004578f0,0x1a4,PTR_s_Old_file_deleted_00457a20);
          }
          iVar4 = FUN_0043d0ce();
          if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
            compress_log_output(0x10000000,PTR_s__efs_service_Old_file_deleted_00457a24,
                                PTR_s__efs_service_Old_file_deleted_00457a24);
          }
        }
        uVar3 = FUN_0045669a(0x103);
        iVar4 = file_open(puVar8,uVar3);
        *piVar2 = iVar4;
        if (*piVar2 == 0) {
          iVar4 = -1;
          *(undefined1 *)(piVar2 + 1) = 0;
        }
        else {
          iVar4 = 0;
          *(undefined1 *)(piVar2 + 1) = 1;
        }
        if (iVar4 < 0) {
          iVar6 = FUN_0043d0ce();
          if (iVar6 << 0x1e < 0) {
            FUN_0043d574(1,PTR_s_efs_service_004578f8,
                         PTR_s_D__01_workspace_s200_ap510b_iar__004578f4,
                         PTR_s__efsFileCmdParse_004578f0,0x1a8,
                         PTR_s_ERR_Open_failed__s____d_00457a28,puVar8,iVar4);
          }
          iVar6 = FUN_0043d0ce();
          if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
            compress_log_output(0x4800000,PTR_s__efs_service_ERR_Open_failed__s___00457a2c,
                                PTR_s__efs_service_ERR_Open_failed__s___00457a2c,puVar8,iVar4);
          }
          _evenEfsReplyToAPP(0xc4,0,3);
          return;
        }
        if (*piVar2 == 0) {
          iVar4 = 0;
        }
        else {
          iVar4 = file_close(*piVar2);
          *piVar2 = 0;
        }
        if (iVar4 < 0) {
          iVar6 = FUN_0043d0ce();
          if (iVar6 << 0x1e < 0) {
            FUN_0043d574(1,PTR_s_efs_service_004578f8,
                         PTR_s_D__01_workspace_s200_ap510b_iar__004578f4,
                         PTR_s__efsFileCmdParse_004578f0,0x1ae,DAT_00457560,puVar8,iVar4);
          }
          iVar6 = FUN_0043d0ce();
          if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
            compress_log_output(0x4800000,DAT_004575dc,DAT_004575dc,puVar8,iVar4);
          }
          _evenEfsReplyToAPP(0xc4,0,3);
          return;
        }
        uVar3 = FUN_0045669a(3);
        iVar4 = file_open(puVar8,uVar3);
        *piVar2 = iVar4;
        if (*piVar2 == 0) {
          *(undefined1 *)(piVar2 + 1) = 0;
        }
        else {
          iVar6 = 0;
          *(undefined1 *)(piVar2 + 1) = 1;
        }
        if (iVar6 < 0) {
          iVar4 = FUN_0043d0ce();
          if (iVar4 << 0x1e < 0) {
            FUN_0043d574(1,PTR_s_efs_service_004578f8,
                         PTR_s_D__01_workspace_s200_ap510b_iar__004578f4,
                         PTR_s__efsFileCmdParse_004578f0,0x1b5,
                         PTR_s_ERR_Open_failed__s____d_00457a28,puVar8,iVar6);
          }
          iVar4 = FUN_0043d0ce();
          if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
            compress_log_output(0x4800000,PTR_s__efs_service_ERR_Open_failed__s___00457a2c,
                                PTR_s__efs_service_ERR_Open_failed__s___00457a2c,puVar8,iVar6);
          }
          _evenEfsReplyToAPP(0xc4,0,3);
          return;
        }
        iVar6 = FUN_0043d0ce();
        if (iVar6 << 0x1e < 0) {
          FUN_0043d574(4,PTR_s_efs_service_004578f8,PTR_s_D__01_workspace_s200_ap510b_iar__004578f4,
                       PTR_s__efsFileCmdParse_004578f0,0x1b9,
                       PTR_s_file_opened_for_writing___s_00457a30,puVar8);
        }
        iVar6 = FUN_0043d0ce();
        if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
          compress_log_output(0x10400000,PTR_s__efs_service_file_opened_for_wri_00457a34,
                              PTR_s__efs_service_file_opened_for_wri_00457a34,puVar8);
        }
      }
    }
    _evenEfsReplyToAPP(0xc4,0,0);
    return;
  }
  if (param_1 != 2) {
    if (1 < param_1) {
      return;
    }
    *(undefined1 *)((int)DAT_00457968 + 0x75) = 1;
    uVar3 = osKernelGetTickCount();
    *DAT_00457a38 = uVar3;
    return;
  }
  iVar4 = FUN_0043d0ce();
  if (iVar4 << 0x1e < 0) {
    FUN_0043d574(4,PTR_s_efs_service_004578f8,PTR_s_D__01_workspace_s200_ap510b_iar__004578f4,
                 PTR_s__efsFileCmdParse_004578f0,0x1c9,
                 PTR_s_eEvenFileSendServiceCID_EVEN_FIL_00457a3c);
  }
  iVar4 = FUN_0043d0ce();
  if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
    compress_log_output(0x10000000,PTR_s__efs_service_eEvenFileSendServic_00457a40,
                        PTR_s__efs_service_eEvenFileSendServic_00457a40);
  }
  iVar4 = FUN_0043d0ce();
  if (iVar4 << 0x1e < 0) {
    FUN_0043d574(4,PTR_s_efs_service_004578f8,PTR_s_D__01_workspace_s200_ap510b_iar__004578f4,
                 PTR_s__efsFileCmdParse_004578f0,0x1ca,
                 PTR_s_calc_bin_crc_0x_x__rxFileCrc___0_00457a44,DAT_00457968[0x19],
                 DAT_00457968[0x18]);
  }
  iVar4 = FUN_0043d0ce();
  if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
    compress_log_output(0x10800000,PTR_s__efs_service_calc_bin_crc_0x_x__r_00457a48,
                        PTR_s__efs_service_calc_bin_crc_0x_x__r_00457a48,DAT_00457968[0x19],
                        DAT_00457968[0x18]);
  }
  iVar4 = FUN_0043d0ce();
  if (iVar4 << 0x1e < 0) {
    FUN_0043d574(4,PTR_s_efs_service_004578f8,PTR_s_D__01_workspace_s200_ap510b_iar__004578f4,
                 PTR_s__efsFileCmdParse_004578f0,0x1cb,
                 PTR_s_recvTotalLen____d_fileSize____d_00457a4c,DAT_00457968[0x1b],
                 DAT_00457968[0x17]);
  }
  iVar4 = FUN_0043d0ce();
  if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
    compress_log_output(0x10800000,PTR_s__efs_service_recvTotalLen____d_f_00457a50,
                        PTR_s__efs_service_recvTotalLen____d_f_00457a50,DAT_00457968[0x1b],
                        DAT_00457968[0x17]);
  }
  piVar2 = DAT_00457968;
  iVar4 = DAT_00457968[0x16];
  if (iVar4 != 0) {
    if (iVar4 == 1) {
      iVar6 = FUN_0043d0ce();
      if (iVar6 << 0x1e < 0) {
        FUN_0043d574(4,PTR_s_efs_service_004578f8,PTR_s_D__01_workspace_s200_ap510b_iar__004578f4,
                     PTR_s__efsFileCmdParse_004578f0,0x1f6,
                     PTR_s_eEvenFileServiceType_ANDROID_MSG_0045804c);
      }
      iVar6 = FUN_0043d0ce();
      if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
        compress_log_output(0x10000000,PTR_s__efs_service_eEvenFileServiceTyp_00458050,
                            PTR_s__efs_service_eEvenFileServiceTyp_00458050);
      }
      iVar6 = FUN_0043d0ce();
      if (iVar6 << 0x1e < 0) {
        FUN_0043d574(4,PTR_s_efs_service_004578f8,PTR_s_D__01_workspace_s200_ap510b_iar__004578f4,
                     PTR_s__efsFileCmdParse_004578f0,0x1f7,
                     PTR_s_rxFileCrc___0x_x__calcFileCrc___0_00458054,piVar2[0x18],piVar2[0x19]);
      }
      iVar6 = FUN_0043d0ce();
      if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
        compress_log_output(0x10800000,PTR_s__efs_service_rxFileCrc___0x_x__c_00458058,
                            PTR_s__efs_service_rxFileCrc___0x_x__c_00458058,piVar2[0x18],
                            piVar2[0x19]);
      }
      iVar6 = FUN_0043d0ce();
      if (iVar6 << 0x1e < 0) {
        FUN_0043d574(4,PTR_s_efs_service_004578f8,PTR_s_D__01_workspace_s200_ap510b_iar__004578f4,
                     PTR_s__efsFileCmdParse_004578f0,0x1f8,
                     PTR_s_fileSize____d__recvTotalLen____d_0045805c,piVar2[0x17],piVar2[0x1b]);
      }
      iVar6 = FUN_0043d0ce();
      if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
        compress_log_output(0x10800000,PTR_s__efs_service_fileSize____d__recv_00458060,
                            PTR_s__efs_service_fileSize____d__recv_00458060,piVar2[0x17],
                            piVar2[0x1b]);
      }
      if ((piVar2[0x18] == piVar2[0x19]) && (piVar2[0x17] == piVar2[0x1b])) {
        iVar6 = FUN_0043d0ce();
        if (iVar6 << 0x1e < 0) {
          FUN_0043d574(4,PTR_s_efs_service_004578f8,PTR_s_D__01_workspace_s200_ap510b_iar__004578f4,
                       PTR_s__efsFileCmdParse_004578f0,0x1fa,
                       PTR_s_eEvenFileServiceRsp_EVEN_FILE_SE_0045801c);
        }
        iVar6 = FUN_0043d0ce();
        if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
          compress_log_output(0x10000000,PTR_s__efs_service_eEvenFileServiceRsp_00458020,
                              PTR_s__efs_service_eEvenFileServiceRsp_00458020);
        }
        _evenEfsReplyToAPP(0xc4,2,0);
        SVC_ANDROID_ParseNotification(*DAT_00457a04);
      }
      else {
        iVar6 = FUN_0043d0ce();
        if (iVar6 << 0x1e < 0) {
          FUN_0043d574(4,PTR_s_efs_service_0045806c,PTR_s_D__01_workspace_s200_ap510b_iar__00458068,
                       PTR_s__efsFileCmdParse_00458064,0x1fe,
                       PTR_s_eEvenFileServiceRsp_EVEN_FILE_SE_00458044);
        }
        iVar6 = FUN_0043d0ce();
        if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
          compress_log_output(0x10000000,PTR_s__efs_service_eEvenFileServiceRsp_00458048,
                              PTR_s__efs_service_eEvenFileServiceRsp_00458048);
        }
        _evenEfsReplyToAPP(0xc4,2,6);
      }
      ble_param_reset_delayed_event(2000);
      FUN_0043c0e4(piVar2,0x78,0);
      return;
    }
    if (iVar4 != 0xaa) {
      return;
    }
    iVar6 = FUN_0043d0ce();
    if (iVar6 << 0x1e < 0) {
      FUN_0043d574(4,PTR_s_efs_service_0045806c,PTR_s_D__01_workspace_s200_ap510b_iar__00458068,
                   PTR_s__efsFileCmdParse_00458064,0x207,
                   PTR_s_eEvenFileServiceType_OTHER_FILE_00457a10);
    }
    iVar6 = FUN_0043d0ce();
    if ((-1 < iVar6 << 0x1f) && (iVar6 = FUN_0043d0ce(), -1 < iVar6 << 0x1d)) {
      return;
    }
    compress_log_output(0x10000000,PTR_s__efs_service_eEvenFileServiceTyp_00457a14,
                        PTR_s__efs_service_eEvenFileServiceTyp_00457a14);
    return;
  }
  iVar4 = FUN_0043d0ce();
  if (iVar4 << 0x1e < 0) {
    FUN_0043d574(4,PTR_s_efs_service_004578f8,PTR_s_D__01_workspace_s200_ap510b_iar__004578f4,
                 PTR_s__efsFileCmdParse_004578f0,0x1ce,
                 PTR_s_eEvenFileServiceType_NOTIFICATIO_004579e0);
  }
  iVar4 = FUN_0043d0ce();
  if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
    compress_log_output(0x10000000,PTR_s__efs_service_eEvenFileServiceTyp_004579e4,
                        PTR_s__efs_service_eEvenFileServiceTyp_004579e4);
  }
  if ((char)piVar2[1] == '\0') {
    uVar3 = FUN_0045669a(3);
    iVar7 = (int)piVar2 + 5;
    iVar4 = file_open(iVar7,uVar3);
    *piVar2 = iVar4;
    if (*piVar2 == 0) {
      *(undefined1 *)(piVar2 + 1) = 0;
    }
    else {
      iVar6 = 0;
      *(undefined1 *)(piVar2 + 1) = 1;
    }
    if (iVar6 < 0) {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        FUN_0043d574(1,PTR_s_efs_service_004578f8,PTR_s_D__01_workspace_s200_ap510b_iar__004578f4,
                     PTR_s__efsFileCmdParse_004578f0,0x1d2,PTR_s_ERR_Open_failed__s____d_00457a28,
                     iVar7,iVar6);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x4800000,PTR_s__efs_service_ERR_Open_failed__s___00457a2c,
                            PTR_s__efs_service_ERR_Open_failed__s___00457a2c,iVar7,iVar6);
      }
      _evenEfsReplyToAPP(0xc4,2,6);
      return;
    }
  }
  FUN_004566d8(*piVar2);
  if (*piVar2 == 0) {
    iVar6 = 0;
  }
  else {
    iVar6 = file_close(*piVar2);
    *piVar2 = 0;
  }
  if (-1 < iVar6) {
    if ((piVar2[0x18] == piVar2[0x19]) && (piVar2[0x17] == piVar2[0x1b])) {
      iVar6 = FUN_0043d0ce();
      if (iVar6 << 0x1e < 0) {
        FUN_0043d574(4,PTR_s_efs_service_004578f8,PTR_s_D__01_workspace_s200_ap510b_iar__004578f4,
                     PTR_s__efsFileCmdParse_004578f0,0x1e0,
                     PTR_s_eEvenFileServiceRsp_EVEN_FILE_SE_0045801c);
      }
      iVar6 = FUN_0043d0ce();
      if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
        compress_log_output(0x10000000,PTR_s__efs_service_eEvenFileServiceRsp_00458020,
                            PTR_s__efs_service_eEvenFileServiceRsp_00458020);
      }
      iVar6 = FUN_0043d0ce();
      if (iVar6 << 0x1e < 0) {
        FUN_0043d574(4,PTR_s_efs_service_004578f8,PTR_s_D__01_workspace_s200_ap510b_iar__004578f4,
                     PTR_s__efsFileCmdParse_004578f0,0x1e1,
                     PTR_s__WHITELIST__Whitelist_file_saved_00458024,(int)piVar2 + 5);
      }
      iVar6 = FUN_0043d0ce();
      if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
        compress_log_output(0x10400000,PTR_s__efs_service__WHITELIST__Whiteli_00458028,
                            PTR_s__efs_service__WHITELIST__Whiteli_00458028,(int)piVar2 + 5);
      }
      _evenEfsReplyToAPP(0xc4,2,0);
      Thread_SendEvtToNotifTask(2);
    }
    else {
      iVar6 = FUN_0043d0ce();
      if (iVar6 << 0x1e < 0) {
        FUN_0043d574(1,PTR_s_efs_service_004578f8,PTR_s_D__01_workspace_s200_ap510b_iar__004578f4,
                     PTR_s__efsFileCmdParse_004578f0,0x1e5,
                     PTR_s__WHITELIST__Whitelist_file_verif_0045802c);
      }
      iVar6 = FUN_0043d0ce();
      if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
        compress_log_output(0x4000000,PTR_s__efs_service__WHITELIST__Whiteli_00458030,
                            PTR_s__efs_service__WHITELIST__Whiteli_00458030);
      }
      if (piVar2[0x18] != piVar2[0x19]) {
        iVar6 = FUN_0043d0ce();
        if (iVar6 << 0x1e < 0) {
          FUN_0043d574(1,PTR_s_efs_service_004578f8,PTR_s_D__01_workspace_s200_ap510b_iar__004578f4,
                       PTR_s__efsFileCmdParse_004578f0,0x1e7,
                       PTR_s__WHITELIST__CRC_mismatch_detecte_00458034);
        }
        iVar6 = FUN_0043d0ce();
        if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
          compress_log_output(0x4000000,PTR_s__efs_service__WHITELIST__CRC_mis_00458038,
                              PTR_s__efs_service__WHITELIST__CRC_mis_00458038);
        }
      }
      if (piVar2[0x17] != piVar2[0x1b]) {
        iVar6 = FUN_0043d0ce();
        if (iVar6 << 0x1e < 0) {
          FUN_0043d574(1,PTR_s_efs_service_004578f8,PTR_s_D__01_workspace_s200_ap510b_iar__004578f4,
                       PTR_s__efsFileCmdParse_004578f0,0x1ea,
                       PTR_s__WHITELIST__Size_mismatch_detect_0045803c);
        }
        iVar6 = FUN_0043d0ce();
        if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
          compress_log_output(0x4000000,PTR_s__efs_service__WHITELIST__Size_mi_00458040,
                              PTR_s__efs_service__WHITELIST__Size_mi_00458040);
        }
      }
      file_remove((int)piVar2 + 5);
      iVar6 = FUN_0043d0ce();
      if (iVar6 << 0x1e < 0) {
        FUN_0043d574(4,PTR_s_efs_service_004578f8,PTR_s_D__01_workspace_s200_ap510b_iar__004578f4,
                     PTR_s__efsFileCmdParse_004578f0,0x1ed,
                     PTR_s_eEvenFileServiceRsp_EVEN_FILE_SE_00458044);
      }
      iVar6 = FUN_0043d0ce();
      if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
        compress_log_output(0x10000000,PTR_s__efs_service_eEvenFileServiceRsp_00458048,
                            PTR_s__efs_service_eEvenFileServiceRsp_00458048);
      }
      _evenEfsReplyToAPP(0xc4,2,6);
    }
    ble_param_reset_delayed_event(2000);
    FUN_0043c0e4(piVar2,0x78,0);
    return;
  }
  iVar4 = FUN_0043d0ce();
  if (iVar4 << 0x1e < 0) {
    FUN_0043d574(1,PTR_s_efs_service_004578f8,PTR_s_D__01_workspace_s200_ap510b_iar__004578f4,
                 PTR_s__efsFileCmdParse_004578f0,0x1da,PTR_s_ERR_Close_failed__s____d_00458018,
                 (int)piVar2 + 5,iVar6);
  }
  iVar4 = FUN_0043d0ce();
  if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
    compress_log_output(0x4800000,DAT_004575dc,DAT_004575dc,(int)piVar2 + 5,iVar6);
  }
  _evenEfsReplyToAPP(0xc4,2,6);
  return;
}

