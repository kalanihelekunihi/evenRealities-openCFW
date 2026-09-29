
void _efsFileRawDataParse(undefined4 param_1,int param_2)

{
  undefined4 uVar1;
  undefined4 *puVar2;
  int *piVar3;
  undefined1 uVar4;
  int iVar5;
  int iVar6;
  bool bVar7;
  
  puVar2 = DAT_004586f8;
  if (*(char *)((int)DAT_004586f8 + 0x75) == '\x01') {
    iVar5 = DAT_004586f8[0x16];
    if (iVar5 == 0) {
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        FUN_0043d574(4,PTR_s_efs_service_0045806c,PTR_s_D__01_workspace_s200_ap510b_iar__00458068,
                     PTR_s__efsFileRawDataParse_00458070,0x21f,DAT_004586fc);
      }
      iVar5 = FUN_0043d0ce();
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_00458700);
      }
      if (*(char *)(puVar2 + 1) == '\0') {
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          FUN_0043d574(1,PTR_s_efs_service_0045806c,PTR_s_D__01_workspace_s200_ap510b_iar__00458068,
                       PTR_s__efsFileRawDataParse_00458070,0x221,
                       PTR_s_ERR_file_is_not_open____s__00458074,(int)puVar2 + 5);
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          compress_log_output(0x4400000,PTR_s__efs_service_ERR_file_is_not_ope_00458078,
                              PTR_s__efs_service_ERR_file_is_not_ope_00458078,(int)puVar2 + 5);
        }
      }
      else {
        osKernelGetTickCount();
        iVar5 = file_write(param_1,1,param_2,*puVar2);
        if (iVar5 == param_2) {
          file_seek(*puVar2,puVar2[0x1b],0);
          uVar1 = DAT_0045807c;
          iVar5 = file_read(DAT_0045807c,1,param_2,*puVar2);
          if (iVar5 == param_2) {
            iVar5 = FUN_004751c8(uVar1,param_1,param_2);
            bVar7 = iVar5 == 0;
            if (bVar7) {
              iVar5 = FUN_0043d0ce();
              if (iVar5 << 0x1e < 0) {
                FUN_0043d574(4,PTR_s_efs_service_0045806c,
                             PTR_s_D__01_workspace_s200_ap510b_iar__00458068,
                             PTR_s__efsFileRawDataParse_00458070,0x22f,
                             PTR_s__WHITELIST__Write___verify_OK____00458080,param_2,puVar2[0x1b]);
              }
              iVar5 = FUN_0043d0ce();
              if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
                compress_log_output(0x10800000,PTR_s__efs_service__WHITELIST__Write___00458084,
                                    PTR_s__efs_service__WHITELIST__Write___00458084,param_2,
                                    puVar2[0x1b]);
              }
            }
            else {
              iVar5 = FUN_0043d0ce();
              if (iVar5 << 0x1e < 0) {
                FUN_0043d574(1,PTR_s_efs_service_0045806c,
                             PTR_s_D__01_workspace_s200_ap510b_iar__00458068,
                             PTR_s__efsFileRawDataParse_00458070,0x231,
                             PTR_s__WHITELIST__Write_verify_failed___00458088);
              }
              iVar5 = FUN_0043d0ce();
              if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
                compress_log_output(0x4000000,PTR_s__efs_service__WHITELIST__Write_v_0045808c,
                                    PTR_s__efs_service__WHITELIST__Write_v_0045808c);
              }
            }
          }
          else {
            bVar7 = false;
            iVar6 = FUN_0043d0ce();
            if (iVar6 << 0x1e < 0) {
              FUN_0043d574(1,PTR_s_efs_service_0045806c,
                           PTR_s_D__01_workspace_s200_ap510b_iar__00458068,
                           PTR_s__efsFileRawDataParse_00458070,0x235,
                           PTR_s_File_read_failed__expected__d__a_00458090,param_2,iVar5);
            }
            iVar6 = FUN_0043d0ce();
            if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
              compress_log_output(0x4800000,PTR_s__efs_service_File_read_failed__e_00458094,
                                  PTR_s__efs_service_File_read_failed__e_00458094,param_2,iVar5);
            }
          }
        }
        else {
          bVar7 = false;
          iVar6 = FUN_0043d0ce();
          if (iVar6 << 0x1e < 0) {
            FUN_0043d574(1,PTR_s_efs_service_0045806c,
                         PTR_s_D__01_workspace_s200_ap510b_iar__00458068,
                         PTR_s__efsFileRawDataParse_00458070,0x239,
                         PTR_s_File_write_failed__expected__d__a_00458098,param_2,iVar5);
          }
          iVar6 = FUN_0043d0ce();
          if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
            compress_log_output(0x4800000,PTR_s__efs_service_File_write_failed__e_0045809c,
                                PTR_s__efs_service_File_write_failed__e_0045809c,param_2,iVar5);
          }
        }
        osKernelGetTickCount();
        if (bVar7) {
          FUN_0047cbc4(param_1,param_2,puVar2 + 0x19);
          puVar2[0x1b] = param_2 + puVar2[0x1b];
          _evenEfsReplyToAPP(0xc5,1,0);
          if (puVar2[0x17] != 0) {
            uVar4 = FUN_0047cc60((int)((ulonglong)(uint)puVar2[0x1b] * 100),
                                 (int)((ulonglong)(uint)puVar2[0x1b] * 100 >> 0x20),puVar2[0x17],0);
            *(undefined1 *)(puVar2 + 0x1d) = uVar4;
          }
          iVar5 = FUN_0043d0ce();
          if (iVar5 << 0x1e < 0) {
            FUN_0043d574(4,PTR_s_efs_service_0045806c,
                         PTR_s_D__01_workspace_s200_ap510b_iar__00458068,
                         PTR_s__efsFileRawDataParse_00458070,0x248,
                         PTR_s__g_bleEfsFileTrans_recvTotalLen___004580a0,puVar2[0x1b],param_2);
          }
          iVar5 = FUN_0043d0ce();
          if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
            compress_log_output(0x10800000,PTR_s__efs_service__g_bleEfsFileTrans__004580a4,
                                PTR_s__efs_service__g_bleEfsFileTrans__004580a4,puVar2[0x1b],param_2
                               );
          }
          piVar3 = DAT_00458a2c;
          iVar5 = osKernelGetTickCount();
          *piVar3 = iVar5;
          iVar5 = FUN_0043d0ce();
          if (iVar5 << 0x1e < 0) {
            FUN_0043d574(4,PTR_s_efs_service_0045806c,
                         PTR_s_D__01_workspace_s200_ap510b_iar__00458068,
                         PTR_s__efsFileRawDataParse_00458070,0x24a,
                         PTR_s_EFS_update__d___eclipse_time___d_004580ac,
                         *(undefined1 *)(puVar2 + 0x1d),*piVar3 - *DAT_00458a30,
                         ((uint)(param_2 * 1000) >> 10) / (uint)(*piVar3 - *DAT_004580a8),
                         ((uint)(puVar2[0x1b] * 1000) >> 10) / (uint)(*piVar3 - *DAT_00458a30));
          }
          iVar5 = FUN_0043d0ce();
          if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
            compress_log_output(0x11000000,PTR_s__efs_service_EFS_update__d___ecl_004580b0,
                                PTR_s__efs_service_EFS_update__d___ecl_004580b0,
                                *(undefined1 *)(puVar2 + 0x1d),*piVar3 - *DAT_00458a30,
                                ((uint)(param_2 * 1000) >> 10) / (uint)(*piVar3 - *DAT_004580a8),
                                ((uint)(puVar2[0x1b] * 1000) >> 10) /
                                (uint)(*piVar3 - *DAT_00458a30));
          }
        }
        else {
          iVar5 = FUN_0043d0ce();
          if (iVar5 << 0x1e < 0) {
            FUN_0043d574(1,PTR_s_efs_service_0045806c,
                         PTR_s_D__01_workspace_s200_ap510b_iar__00458068,
                         PTR_s__efsFileRawDataParse_00458070,0x24e,
                         PTR_s__WHITELIST__Write_failed_at_offs_004580b4,puVar2[0x1b]);
          }
          iVar5 = FUN_0043d0ce();
          if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
            compress_log_output(0x4400000,PTR_s__efs_service__WHITELIST__Write_f_004580b8,
                                PTR_s__efs_service__WHITELIST__Write_f_004580b8,puVar2[0x1b]);
          }
          _evenEfsReplyToAPP(0xc5,1,3);
        }
      }
    }
    else if (iVar5 == 1) {
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        FUN_0043d574(4,PTR_s_efs_service_0045806c,PTR_s_D__01_workspace_s200_ap510b_iar__00458068,
                     PTR_s__efsFileRawDataParse_00458070,0x255,
                     PTR_s_eEvenFileServiceType_ANDROID_MSG_0045804c);
      }
      iVar5 = FUN_0043d0ce();
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        compress_log_output(0x10000000,PTR_s__efs_service_eEvenFileServiceTyp_00458050,
                            PTR_s__efs_service_eEvenFileServiceTyp_00458050);
      }
      osKernelGetTickCount();
      FUN_00439be4(*DAT_004580bc + puVar2[0x1b],param_1,param_2);
      FUN_0047cbc4(param_1,param_2,puVar2 + 0x19);
      puVar2[0x1b] = param_2 + puVar2[0x1b];
      _evenEfsReplyToAPP(0xc5,1,0);
      if (puVar2[0x17] != 0) {
        uVar4 = FUN_0047cc60((int)((ulonglong)(uint)puVar2[0x1b] * 100),
                             (int)((ulonglong)(uint)puVar2[0x1b] * 100 >> 0x20),puVar2[0x17],0);
        *(undefined1 *)(puVar2 + 0x1d) = uVar4;
      }
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        FUN_0043d574(4,PTR_s_efs_service_0045806c,PTR_s_D__01_workspace_s200_ap510b_iar__00458068,
                     PTR_s__efsFileRawDataParse_00458070,0x263,
                     PTR_s__g_bleEfsFileTrans_recvTotalLen___004580a0,puVar2[0x1b],param_2);
      }
      iVar5 = FUN_0043d0ce();
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        compress_log_output(0x10800000,PTR_s__efs_service__g_bleEfsFileTrans__004580a4,
                            PTR_s__efs_service__g_bleEfsFileTrans__004580a4,puVar2[0x1b],param_2);
      }
      piVar3 = DAT_00458a2c;
      iVar5 = osKernelGetTickCount();
      *piVar3 = iVar5;
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        FUN_0043d574(4,PTR_s_efs_service_0045806c,PTR_s_D__01_workspace_s200_ap510b_iar__00458068,
                     PTR_s__efsFileRawDataParse_00458070,0x265,
                     PTR_s_EFS_update__d___eclipse_time___d_004580ac,*(undefined1 *)(puVar2 + 0x1d),
                     *piVar3 - *DAT_00458a30,
                     ((uint)(param_2 * 1000) >> 10) / (uint)(*piVar3 - *DAT_004580a8),
                     ((uint)(puVar2[0x1b] * 1000) >> 10) / (uint)(*piVar3 - *DAT_00458a30));
      }
      iVar5 = FUN_0043d0ce();
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        compress_log_output(0x11000000,PTR_s__efs_service_EFS_update__d___ecl_004580b0,
                            PTR_s__efs_service_EFS_update__d___ecl_004580b0,
                            *(undefined1 *)(puVar2 + 0x1d),*piVar3 - *DAT_00458a30,
                            ((uint)(param_2 * 1000) >> 10) / (uint)(*piVar3 - *DAT_004580a8),
                            ((uint)(puVar2[0x1b] * 1000) >> 10) / (uint)(*piVar3 - *DAT_00458a30));
      }
    }
    else if (iVar5 == 0xaa) {
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        FUN_0043d574(4,PTR_s_efs_service_0045806c,PTR_s_D__01_workspace_s200_ap510b_iar__00458068,
                     PTR_s__efsFileRawDataParse_00458070,0x26c,DAT_00458b5c);
      }
      iVar5 = FUN_0043d0ce();
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        compress_log_output(0x10000000,PTR_s__efs_service_eEvenFileServiceTyp_00458c34,
                            PTR_s__efs_service_eEvenFileServiceTyp_00458c34);
      }
    }
  }
  return;
}

