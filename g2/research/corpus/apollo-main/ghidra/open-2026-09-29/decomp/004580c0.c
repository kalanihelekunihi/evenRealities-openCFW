
void _efsExportFileParse(byte param_1,int *param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  int *piVar2;
  char cVar3;
  undefined1 uVar4;
  int iVar5;
  undefined4 uVar6;
  uint uVar7;
  int iVar8;
  int iVar9;
  char cVar10;
  uint uVar11;
  undefined1 auStack_2c [4];
  undefined1 local_28;
  undefined1 local_27;
  undefined1 local_26;
  undefined1 local_25;
  undefined1 local_24;
  undefined1 local_23;
  undefined1 local_22;
  undefined1 local_21;
  undefined1 local_20;
  undefined1 local_1f;
  undefined4 uStack_1c;
  
  uStack_1c = param_4;
  FUN_0043c0e4(auStack_2c,2,0);
  piVar1 = DAT_00458a30;
  iVar9 = -1;
  cVar3 = '\0';
  cVar10 = (char)*param_2;
  if (param_1 == 0) {
    iVar8 = osKernelGetTickCount(0);
    *piVar1 = iVar8;
    iVar8 = FUN_0043d0ce();
    if (iVar8 << 0x1e < 0) {
      FUN_0043d574(4,PTR_s_efs_service_00458d3c,PTR_s_D__01_workspace_s200_ap510b_iar__00458d38,
                   PTR_s__efsExportFileParse_00458d34,0x288,
                   PTR_s_eEvenFileExportServiceCID_EVEN_F_00458c38,*piVar1);
    }
    iVar8 = FUN_0043d0ce();
    if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
      compress_log_output(0x10400000,PTR_s__efs_service_eEvenFileExportServ_00458c3c,
                          PTR_s__efs_service_eEvenFileExportServ_00458c3c,*piVar1);
    }
    compress_log_export_notify(1);
    APP_ConnectParamOTASetFastMode();
    piVar1 = DAT_004586f8;
    if ((char)DAT_004586f8[1] == '\x01') {
      iVar8 = FUN_0043d0ce();
      if (iVar8 << 0x1e < 0) {
        FUN_0043d574(2,PTR_s_efs_service_00458d3c,PTR_s_D__01_workspace_s200_ap510b_iar__00458d38,
                     PTR_s__efsExportFileParse_00458d34,0x28d,
                     PTR_s_file_is_open__close_file_first_00458c40);
      }
      iVar8 = FUN_0043d0ce();
      if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
        compress_log_output(0x8000000,PTR_s__efs_service_file_is_open__close_00458c44,
                            PTR_s__efs_service_file_is_open__close_00458c44);
      }
      if (*piVar1 == 0) {
        iVar8 = 0;
      }
      else {
        iVar8 = file_close(*piVar1);
        *piVar1 = 0;
      }
      if (iVar8 < 0) {
        iVar9 = FUN_0043d0ce();
        if (iVar9 << 0x1e < 0) {
          FUN_0043d574(1,PTR_s_efs_service_00458d3c,PTR_s_D__01_workspace_s200_ap510b_iar__00458d38,
                       PTR_s__efsExportFileParse_00458d34,0x290,
                       PTR_s_ERR_Close_failed__s____d_00458d40,(int)piVar1 + 5,iVar8);
        }
        iVar9 = FUN_0043d0ce();
        if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
          compress_log_output(0x4800000,PTR_s__efs_service_ERR_Close_failed__s_00458d44,
                              PTR_s__efs_service_ERR_Close_failed__s_00458d44,(int)piVar1 + 5,iVar8)
          ;
        }
        goto LAB_00458222;
      }
    }
    FUN_0043c0e4(piVar1,0x78,0);
    piVar1[0x16] = *param_2;
    iVar8 = piVar1[0x16];
    if (iVar8 == 0) {
      iVar8 = FUN_0043d0ce();
      if (iVar8 << 0x1e < 0) {
        FUN_0043d574(4,PTR_s_efs_service_00458d3c,PTR_s_D__01_workspace_s200_ap510b_iar__00458d38,
                     PTR_s__efsExportFileParse_00458d34,0x299,DAT_004586fc);
      }
      iVar8 = FUN_0043d0ce();
      if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_00458700,DAT_00458700);
      }
      FUN_0044b5a0((int)piVar1 + 5,PTR_s_user_notify_whitelist_json_00458d48,0x1a);
    }
    else if (iVar8 == 2) {
      iVar5 = (int)piVar1 + 5;
      FUN_0044b5a0(iVar5,param_2 + 1,0x50);
      *(undefined1 *)(piVar1 + 0x15) = 0;
      iVar8 = FUN_0043d0ce();
      if (iVar8 << 0x1e < 0) {
        FUN_0043d574(4,PTR_s_efs_service_00458d3c,PTR_s_D__01_workspace_s200_ap510b_iar__00458d38,
                     PTR_s__efsExportFileParse_00458d34,0x2ab,
                     PTR_s_eEvenFileServiceType_LOGGER_FILE_00458d54,iVar5);
      }
      iVar8 = FUN_0043d0ce();
      if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
        compress_log_output(0x10400000,PTR_s__efs_service_eEvenFileServiceTyp_00458d58,
                            PTR_s__efs_service_eEvenFileServiceTyp_00458d58,iVar5);
      }
      iVar8 = FUN_00456606(iVar5);
      if (iVar8 == 0) {
        iVar9 = FUN_0043d0ce();
        if (iVar9 << 0x1e < 0) {
          FUN_0043d574(2,PTR_s_efs_service_00458d3c,PTR_s_D__01_workspace_s200_ap510b_iar__00458d38,
                       PTR_s__efsExportFileParse_00458d34,0x2ad,
                       PTR_s_invalid_logger_export_path___s_00458d5c,iVar5);
        }
        iVar9 = FUN_0043d0ce();
        if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
          compress_log_output(0x8400000,PTR_s__efs_service_invalid_logger_expo_00458d60,
                              PTR_s__efs_service_invalid_logger_expo_00458d60,iVar5);
        }
        _evenEfsReplyToAPP(0xc6,0,1);
        goto LAB_00458222;
      }
    }
    else if (iVar8 == 3) {
      iVar5 = (int)piVar1 + 5;
      FUN_0044b5a0(iVar5,param_2 + 1,0x50);
      *(undefined1 *)(piVar1 + 0x15) = 0;
      iVar8 = FUN_0043d0ce();
      if (iVar8 << 0x1e < 0) {
        FUN_0043d574(4,PTR_s_efs_service_00458d3c,PTR_s_D__01_workspace_s200_ap510b_iar__00458d38,
                     PTR_s__efsExportFileParse_00458d34,0x2b8,
                     PTR_s_eEvenFileServiceType_TRACEPOINT__00458d64,iVar5);
      }
      iVar8 = FUN_0043d0ce();
      if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
        compress_log_output(0x10400000,PTR_s__efs_service_eEvenFileServiceTyp_00458d68,
                            PTR_s__efs_service_eEvenFileServiceTyp_00458d68,iVar5);
      }
      iVar8 = FUN_00456580(iVar5);
      if (iVar8 == 0) {
        iVar9 = FUN_0043d0ce();
        if (iVar9 << 0x1e < 0) {
          FUN_0043d574(2,PTR_s_efs_service_00458d3c,PTR_s_D__01_workspace_s200_ap510b_iar__00458d38,
                       PTR_s__efsExportFileParse_00458d34,0x2ba,
                       PTR_s_invalid_tracepoint_export_path____00458d6c,iVar5);
        }
        iVar9 = FUN_0043d0ce();
        if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
          compress_log_output(0x8400000,PTR_s__efs_service_invalid_tracepoint_e_00458d70,
                              PTR_s__efs_service_invalid_tracepoint_e_00458d70,iVar5);
        }
        _evenEfsReplyToAPP(0xc6,0,1);
        goto LAB_00458222;
      }
      cVar3 = '\x01';
    }
    else if (iVar8 == 0xaa) {
      iVar5 = (int)piVar1 + 5;
      FUN_0044b5a0(iVar5,param_2 + 1,0x50);
      *(undefined1 *)(piVar1 + 0x15) = 0;
      iVar8 = FUN_0043d0ce();
      if (iVar8 << 0x1e < 0) {
        FUN_0043d574(4,PTR_s_efs_service_00458d3c,PTR_s_D__01_workspace_s200_ap510b_iar__00458d38,
                     PTR_s__efsExportFileParse_00458d34,0x2a2,
                     PTR_s_eEvenFileServiceType_OTHER_FILE___00458d4c,iVar5);
      }
      iVar8 = FUN_0043d0ce();
      if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
        compress_log_output(0x10400000,PTR_s__efs_service_eEvenFileServiceTyp_00458d50,
                            PTR_s__efs_service_eEvenFileServiceTyp_00458d50,iVar5);
      }
      cVar3 = FUN_00456580(iVar5);
    }
    if ((cVar3 != '\0') && (iVar8 = FUN_0048ec9e(), iVar8 != 0)) {
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        FUN_0043d574(2,PTR_s_efs_service_00458d3c,PTR_s_D__01_workspace_s200_ap510b_iar__00458d38,
                     PTR_s__efsExportFileParse_00458d34,0x2ca,
                     PTR_s_tracepoint_prepare_pull_failed_b_00458d74,iVar8);
      }
      iVar5 = FUN_0043d0ce();
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        compress_log_output(0x8400000,PTR_s__efs_service_tracepoint_prepare_p_00458d78,
                            PTR_s__efs_service_tracepoint_prepare_p_00458d78,iVar8);
      }
    }
    iVar5 = (int)piVar1 + 5;
    iVar8 = _fileCaculateCRC(piVar1,iVar5,piVar1 + 0x17,piVar1 + 0x19);
    if (iVar8 == 0) {
      iVar9 = FUN_0043d0ce();
      if (iVar9 << 0x1e < 0) {
        FUN_0043d574(1,PTR_s_efs_service_00458d3c,PTR_s_D__01_workspace_s200_ap510b_iar__00458d38,
                     PTR_s__efsExportFileParse_00458d34,0x2cf,
                     PTR_s_Failed_to_read_calculate_CRC_00458d7c);
      }
      iVar9 = FUN_0043d0ce();
      if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
        compress_log_output(0x4000000,PTR_s__efs_service_Failed_to_read_calc_00458d80,
                            PTR_s__efs_service_Failed_to_read_calc_00458d80);
      }
      _evenEfsReplyToAPP(0xc6,0,2);
      goto LAB_00458222;
    }
    FUN_0043c0e4(&local_28,10,0);
    local_28 = 0;
    local_27 = 0;
    local_26 = (undefined1)piVar1[0x17];
    local_25 = (undefined1)((uint)piVar1[0x17] >> 8);
    local_24 = (undefined1)((uint)piVar1[0x17] >> 0x10);
    local_23 = (undefined1)((uint)piVar1[0x17] >> 0x18);
    local_22 = (undefined1)piVar1[0x19];
    local_21 = (undefined1)((uint)piVar1[0x19] >> 8);
    local_20 = (undefined1)((uint)piVar1[0x19] >> 0x10);
    local_1f = (undefined1)((uint)piVar1[0x19] >> 0x18);
    piVar1[0x1c] = piVar1[0x17];
    Thread_MsgEfsTxByBle(1,0xc6,&local_28,10);
    uVar6 = FUN_0045669a(1);
    iVar8 = file_open(iVar5,uVar6);
    *piVar1 = iVar8;
    if (*piVar1 == 0) {
      *(undefined1 *)(piVar1 + 1) = 0;
    }
    else {
      iVar9 = 0;
      *(undefined1 *)(piVar1 + 1) = 1;
    }
    if (iVar9 < 0) {
      iVar8 = FUN_0043d0ce();
      if (iVar8 << 0x1e < 0) {
        FUN_0043d574(1,PTR_s_efs_service_00458d3c,PTR_s_D__01_workspace_s200_ap510b_iar__00458d38,
                     PTR_s__efsExportFileParse_00458d34,0x2e6,PTR_s_ERR_Open_failed__s____d_00458d84
                     ,iVar5,iVar9);
      }
      iVar8 = FUN_0043d0ce();
      if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
        compress_log_output(0x4800000,PTR_s__efs_service_ERR_Open_failed__s___00458d88,
                            PTR_s__efs_service_ERR_Open_failed__s___00458d88,iVar5,iVar9);
      }
      goto LAB_00458222;
    }
    *(undefined1 *)((int)piVar1 + 0x75) = 1;
    *DAT_00458d8c = 1;
    iVar9 = FUN_0043d0ce();
    if (iVar9 << 0x1e < 0) {
      FUN_0043d574(4,PTR_s_efs_service_00458d3c,PTR_s_D__01_workspace_s200_ap510b_iar__00458d38,
                   PTR_s__efsExportFileParse_00458d34,0x2eb,
                   PTR_s__g_bleEfsFileTrans_isStart____d_00458d90,
                   *(undefined1 *)((int)piVar1 + 0x75));
    }
    iVar9 = FUN_0043d0ce();
    if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
      compress_log_output(0x10400000,PTR_s__efs_service__g_bleEfsFileTrans__00458d94,
                          PTR_s__efs_service__g_bleEfsFileTrans__00458d94,
                          *(undefined1 *)((int)piVar1 + 0x75));
    }
    osDelay(0x1e);
    cVar10 = '\0';
  }
  else {
    if (param_1 == 2) {
      iVar9 = FUN_0043d0ce();
      if (iVar9 << 0x1e < 0) {
        FUN_0043d574(4,PTR_s_efs_service_00458d3c,PTR_s_D__01_workspace_s200_ap510b_iar__00458d38,
                     PTR_s__efsExportFileParse_00458d34,0x32c,
                     PTR_s_eEvenFileExportServiceCID_EVEN_F_00458dd0,cVar10);
      }
      iVar9 = FUN_0043d0ce();
      if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
        compress_log_output(0x10400000,PTR_s__efs_service_eEvenFileExportServ_00458dd4,
                            PTR_s__efs_service_eEvenFileExportServ_00458dd4,cVar10);
      }
      goto LAB_00458222;
    }
    if (1 < param_1) {
      if (param_1 != 3) {
        return;
      }
      iVar9 = FUN_0043d0ce();
      if (iVar9 << 0x1e < 0) {
        FUN_0043d574(2,PTR_s_efs_service_00458d3c,PTR_s_D__01_workspace_s200_ap510b_iar__00458d38,
                     PTR_s__efsExportFileParse_00458d34,0x332,
                     PTR_s_eEvenFileExportServiceCID_EVEN_F_00458dd8);
      }
      iVar9 = FUN_0043d0ce();
      if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
        compress_log_output(0x8000000,PTR_s__efs_service_eEvenFileExportServ_00458ddc,
                            PTR_s__efs_service_eEvenFileExportServ_00458ddc);
      }
      _evenEfsReplyToAPP(0xc6,3,0);
      goto LAB_00458222;
    }
  }
  piVar1 = DAT_004586f8;
  if (*(char *)((int)DAT_004586f8 + 0x75) == '\0') {
    return;
  }
  if (cVar10 == '\0') {
    uVar6 = osKernelGetTickCount();
    *DAT_00458da0 = uVar6;
    uVar6 = DAT_00458da4;
    uVar11 = 0x1000;
    FUN_0043c0e4(DAT_00458da4,0x1000,0);
    if ((uint)piVar1[0x1c] < 0x1000) {
      uVar11 = piVar1[0x1c];
    }
    iVar9 = FUN_0043d0ce();
    if (iVar9 << 0x1e < 0) {
      FUN_0043d574(4,PTR_s_efs_service_00458d3c,PTR_s_D__01_workspace_s200_ap510b_iar__00458d38,
                   PTR_s__efsExportFileParse_00458d34,0x2ff,
                   PTR_s_readLen____d___g_bleEfsFileTrans_00458da8,uVar11,piVar1[0x1c]);
    }
    iVar9 = FUN_0043d0ce();
    if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
      compress_log_output(0x10800000,PTR_s__efs_service_readLen____d___g_bl_00458dac,
                          PTR_s__efs_service_readLen____d___g_bl_00458dac,uVar11,piVar1[0x1c]);
    }
    uVar7 = file_read(uVar6,1,uVar11,*piVar1);
    if (uVar7 == uVar11) {
      iVar9 = FUN_0043d0ce();
      if (iVar9 << 0x1e < 0) {
        FUN_0043d574(4,PTR_s_efs_service_00458d3c,PTR_s_D__01_workspace_s200_ap510b_iar__00458d38,
                     PTR_s__efsExportFileParse_00458d34,0x309,PTR_s_readResult____d_00458db8,uVar7);
      }
      iVar9 = FUN_0043d0ce();
      if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
        compress_log_output(0x10400000,PTR_s__efs_service_readResult____d_00458dbc,
                            PTR_s__efs_service_readResult____d_00458dbc,uVar7);
      }
      piVar1[0x1b] = uVar7 + piVar1[0x1b];
      piVar1[0x1a] = uVar7;
      piVar1[0x1c] = piVar1[0x17] - piVar1[0x1b];
      Thread_MsgEfsNotifyByBle(1,199,uVar6,uVar7 & 0xffff);
      if (piVar1[0x17] != 0) {
        uVar4 = FUN_0047cc60((int)((ulonglong)(uint)piVar1[0x1b] * 100),
                             (int)((ulonglong)(uint)piVar1[0x1b] * 100 >> 0x20),piVar1[0x17],0);
        *(undefined1 *)(piVar1 + 0x1d) = uVar4;
      }
      piVar2 = DAT_00458a2c;
      iVar9 = osKernelGetTickCount();
      *piVar2 = iVar9;
      iVar9 = FUN_0043d0ce();
      if (iVar9 << 0x1e < 0) {
        FUN_0043d574(4,PTR_s_efs_service_00458d3c,PTR_s_D__01_workspace_s200_ap510b_iar__00458d38,
                     PTR_s__efsExportFileParse_00458d34,0x315,
                     PTR_s_export_file__d___eclipse_time____00458dc0,(char)piVar1[0x1d],
                     *piVar2 - *DAT_00458a30,
                     ((uint)(piVar1[0x1b] * 1000) >> 10) / (uint)(*piVar2 - *DAT_00458a30));
      }
      iVar9 = FUN_0043d0ce();
      if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
        compress_log_output(0x10c00000,PTR_s__efs_service_export_file__d___ec_00458dc4,
                            PTR_s__efs_service_export_file__d___ec_00458dc4,(char)piVar1[0x1d],
                            *piVar2 - *DAT_00458a30,
                            ((uint)(piVar1[0x1b] * 1000) >> 10) / (uint)(*piVar2 - *DAT_00458a30));
      }
      iVar9 = FUN_0043d0ce();
      if (iVar9 << 0x1e < 0) {
        FUN_0043d574(4,PTR_s_efs_service_00458d3c,PTR_s_D__01_workspace_s200_ap510b_iar__00458d38,
                     PTR_s__efsExportFileParse_00458d34,0x318,
                     PTR_s_recvTotalLen____d__fileSize____d_00458dc8,piVar1[0x1b],piVar1[0x17],
                     piVar1[0x19]);
      }
      iVar9 = FUN_0043d0ce();
      if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
        compress_log_output(0x10c00000,PTR_s__efs_service_recvTotalLen____d__f_00458dcc,
                            PTR_s__efs_service_recvTotalLen____d__f_00458dcc,piVar1[0x1b],
                            piVar1[0x17],piVar1[0x19]);
      }
      if ((uint)piVar1[0x1b] < (uint)piVar1[0x17]) {
        return;
      }
      *(undefined1 *)((int)piVar1 + 0x75) = 0;
      if (*piVar1 == 0) {
        iVar9 = 0;
      }
      else {
        iVar9 = file_close(*piVar1);
        *piVar1 = 0;
      }
      if (-1 < iVar9) {
        FUN_0043c0e4(piVar1,0x78,0);
        *DAT_00458d8c = 0;
        compress_log_export_notify(0);
        ble_param_reset_delayed_event(2000);
        return;
      }
      iVar8 = FUN_0043d0ce();
      if (iVar8 << 0x1e < 0) {
        FUN_0043d574(1,PTR_s_efs_service_00458d3c,PTR_s_D__01_workspace_s200_ap510b_iar__00458d38,
                     PTR_s__efsExportFileParse_00458d34,0x31d,
                     PTR_s_ERR_Close_failed__s____d_00458d40,(int)piVar1 + 5,iVar9);
      }
      iVar8 = FUN_0043d0ce();
      if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
        compress_log_output(0x4800000,PTR_s__efs_service_ERR_Close_failed__s_00458d44,
                            PTR_s__efs_service_ERR_Close_failed__s_00458d44,(int)piVar1 + 5,iVar9);
      }
    }
    else {
      iVar9 = FUN_0043d0ce();
      if (iVar9 << 0x1e < 0) {
        FUN_0043d574(1,PTR_s_efs_service_00458d3c,PTR_s_D__01_workspace_s200_ap510b_iar__00458d38,
                     PTR_s__efsExportFileParse_00458d34,0x302,PTR_s_ERR_Read_failed__d_00458db0,
                     uVar7);
      }
      iVar9 = FUN_0043d0ce();
      if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
        compress_log_output(0x4400000,PTR_s__efs_service_ERR_Read_failed__d_00458db4,
                            PTR_s__efs_service_ERR_Read_failed__d_00458db4,uVar7);
      }
      if (*piVar1 == 0) {
        iVar9 = 0;
      }
      else {
        iVar9 = file_close(*piVar1);
        *piVar1 = 0;
      }
      if (iVar9 < 0) {
        iVar8 = FUN_0043d0ce();
        if (iVar8 << 0x1e < 0) {
          FUN_0043d574(1,PTR_s_efs_service_00458d3c,PTR_s_D__01_workspace_s200_ap510b_iar__00458d38,
                       PTR_s__efsExportFileParse_00458d34,0x305,
                       PTR_s_ERR_Close_failed__s____d_00458d40,(int)piVar1 + 5,iVar9);
        }
        iVar8 = FUN_0043d0ce();
        if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
          compress_log_output(0x4800000,PTR_s__efs_service_ERR_Close_failed__s_00458d44,
                              PTR_s__efs_service_ERR_Close_failed__s_00458d44,(int)piVar1 + 5,iVar9)
          ;
        }
      }
    }
  }
  else {
    iVar9 = FUN_0043d0ce();
    if (iVar9 << 0x1e < 0) {
      FUN_0043d574(1,PTR_s_efs_service_00458d3c,PTR_s_D__01_workspace_s200_ap510b_iar__00458d38,
                   PTR_s__efsExportFileParse_00458d34,0x2f7,
                   PTR_s_ERR_Export_failed_response__d_00458d98,cVar10);
    }
    iVar9 = FUN_0043d0ce();
    if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
      compress_log_output(0x4400000,PTR_s__efs_service_ERR_Export_failed_r_00458d9c,
                          PTR_s__efs_service_ERR_Export_failed_r_00458d9c,cVar10);
    }
  }
LAB_00458222:
  piVar1 = DAT_004586f8;
  if ((char)DAT_004586f8[1] == '\x01') {
    if (*DAT_004586f8 == 0) {
      iVar9 = 0;
    }
    else {
      iVar9 = file_close(*DAT_004586f8);
      *piVar1 = 0;
    }
    if (iVar9 < 0) {
      iVar8 = FUN_0043d0ce();
      if (iVar8 << 0x1e < 0) {
        FUN_0043d574(1,PTR_s_efs_service_00458d3c,PTR_s_D__01_workspace_s200_ap510b_iar__00458d38,
                     PTR_s__efsExportFileParse_00458d34,0x342,
                     PTR_s_ERR_Close_failed__s____d_00458d40,(int)piVar1 + 5,iVar9);
      }
      iVar8 = FUN_0043d0ce();
      if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
        compress_log_output(0x4800000,PTR_s__efs_service_ERR_Close_failed__s_00458d44,
                            PTR_s__efs_service_ERR_Close_failed__s_00458d44,(int)piVar1 + 5,iVar9);
      }
    }
  }
  FUN_0043c0e4(piVar1,0x78,0);
  *DAT_00458d8c = 0;
  compress_log_export_notify(0);
  ble_param_reset_delayed_event(2000);
  return;
}

