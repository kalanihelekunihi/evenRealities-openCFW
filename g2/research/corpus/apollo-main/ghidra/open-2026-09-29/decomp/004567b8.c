
undefined4 _fileCaculateCRC(int *param_1,undefined4 param_2,uint *param_3,undefined4 *param_4)

{
  undefined4 uVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  int iVar5;
  
  iVar5 = -1;
  uVar1 = FUN_0045669a(1);
  iVar2 = file_open(param_2,uVar1);
  *param_1 = iVar2;
  if (*param_1 == 0) {
    *(undefined1 *)(DAT_00456bd0 + 4) = 0;
  }
  else {
    iVar5 = 0;
    *(undefined1 *)(DAT_00456bd0 + 4) = 1;
  }
  if (-1 < iVar5) {
    uVar3 = FUN_004566d8(*param_1);
    if ((int)uVar3 < 0) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(1,PTR_s_efs_service_00456bc8,PTR_s_D__01_workspace_s200_ap510b_iar__00456bc4,
                     PTR_s__fileCaculateCRC_00456bd8,0x125,
                     PTR_s_ERR_get_size_failed__s____d_00456be0,param_2,uVar3);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4800000,PTR_s__efs_service_ERR_get_size_failed_00456be4,
                            PTR_s__efs_service_ERR_get_size_failed_00456be4,param_2,uVar3);
      }
      if (*param_1 == 0) {
        iVar2 = 0;
      }
      else {
        iVar2 = file_close(*param_1);
        *param_1 = 0;
      }
      if (iVar2 < 0) {
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          FUN_0043d574(1,PTR_s_efs_service_00456bc8,PTR_s_D__01_workspace_s200_ap510b_iar__00456bc4,
                       PTR_s__fileCaculateCRC_00456bd8,0x128,DAT_00457560,param_2,iVar2);
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          compress_log_output(0x4800000,DAT_004575dc,DAT_004575dc,param_2,iVar2);
        }
      }
      return 0;
    }
    *param_3 = uVar3;
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(4,PTR_s_efs_service_00456bc8,PTR_s_D__01_workspace_s200_ap510b_iar__00456bc4,
                   PTR_s__fileCaculateCRC_00456bd8,0x12e,PTR_s_File_size___ld_bytes_00456be8,
                   *param_3);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10400000,PTR_s__efs_service_File_size___ld_byte_00456bec,
                          PTR_s__efs_service_File_size___ld_byte_00456bec,*param_3);
    }
    for (uVar3 = 0; uVar1 = DAT_00456bf0, uVar3 < *param_3 >> 0xc; uVar3 = uVar3 + 1) {
      iVar2 = file_read(DAT_00456bf0,1,0x1000,*param_1);
      if (iVar2 != 0x1000) {
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          FUN_0043d574(1,PTR_s_efs_service_00456bc8,PTR_s_D__01_workspace_s200_ap510b_iar__00456bc4,
                       PTR_s__fileCaculateCRC_00456bd8,0x133,PTR_s_read_failed__d_00456bf4,iVar2);
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          compress_log_output(0x4400000,PTR_s__efs_service_read_failed__d_00456bf8,
                              PTR_s__efs_service_read_failed__d_00456bf8,iVar2);
        }
        if (*param_1 == 0) {
          iVar2 = 0;
        }
        else {
          iVar2 = file_close(*param_1);
          *param_1 = 0;
        }
        if (iVar2 < 0) {
          iVar5 = FUN_0043d0ce();
          if (iVar5 << 0x1e < 0) {
            FUN_0043d574(1,PTR_s_efs_service_00456bc8,
                         PTR_s_D__01_workspace_s200_ap510b_iar__00456bc4,
                         PTR_s__fileCaculateCRC_00456bd8,0x136,DAT_00457560,param_2,iVar2);
          }
          iVar5 = FUN_0043d0ce();
          if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
            compress_log_output(0x4800000,DAT_004575dc,DAT_004575dc,param_2,iVar2);
          }
        }
        return 0;
      }
      FUN_0047cbc4(uVar1,0x1000,param_4);
    }
    uVar3 = *param_3 & 0xfff;
    if (uVar3 != 0) {
      uVar4 = file_read(DAT_00456bf0,1,uVar3,*param_1);
      if (uVar4 != uVar3) {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(1,PTR_s_efs_service_00456bc8,PTR_s_D__01_workspace_s200_ap510b_iar__00456bc4,
                       PTR_s__fileCaculateCRC_00456bd8,0x141,PTR_s_read_failed__d__d__00456bfc,uVar4
                       ,uVar3);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0x4800000,PTR_s__efs_service_read_failed__d__d__00456c00,
                              PTR_s__efs_service_read_failed__d__d__00456c00,uVar4,uVar3);
        }
        if (*param_1 == 0) {
          iVar2 = 0;
        }
        else {
          iVar2 = file_close(*param_1);
          *param_1 = 0;
        }
        if (iVar2 < 0) {
          iVar5 = FUN_0043d0ce();
          if (iVar5 << 0x1e < 0) {
            FUN_0043d574(1,PTR_s_efs_service_00456bc8,
                         PTR_s_D__01_workspace_s200_ap510b_iar__00456bc4,
                         PTR_s__fileCaculateCRC_00456bd8,0x144,DAT_00457560,param_2,iVar2);
          }
          iVar5 = FUN_0043d0ce();
          if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
            compress_log_output(0x4800000,DAT_004575dc,DAT_004575dc,param_2,iVar2);
          }
        }
        return 0;
      }
      FUN_0047cbc4(uVar1,uVar3,param_4);
    }
    if (*param_1 == 0) {
      iVar2 = 0;
    }
    else {
      iVar2 = file_close(*param_1);
      *param_1 = 0;
    }
    if (iVar2 < 0) {
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        FUN_0043d574(1,PTR_s_efs_service_00456bc8,PTR_s_D__01_workspace_s200_ap510b_iar__00456bc4,
                     PTR_s__fileCaculateCRC_00456bd8,0x14c,DAT_00457560,param_2,iVar2);
      }
      iVar5 = FUN_0043d0ce();
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        compress_log_output(0x4800000,DAT_004575dc,DAT_004575dc,param_2,iVar2);
      }
    }
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(4,PTR_s_efs_service_00456bc8,PTR_s_D__01_workspace_s200_ap510b_iar__00456bc4,
                   PTR_s__fileCaculateCRC_00456bd8,0x14e,
                   PTR_s_filePath____s__fileSize____d__ca_00456c04,param_2,*param_3,*param_4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10c00000,PTR_s__efs_service_filePath____s__file_00456c08,
                          PTR_s__efs_service_filePath____s__file_00456c08,param_2,*param_3,*param_4)
      ;
    }
    return 1;
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    FUN_0043d574(1,PTR_s_efs_service_00456bc8,PTR_s_D__01_workspace_s200_ap510b_iar__00456bc4,
                 PTR_s__fileCaculateCRC_00456bd8,0x11f,PTR_s_ERR_Open_failed__s____d_00456bd4,
                 param_2,iVar5);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x4800000,PTR_s__efs_service_ERR_Open_failed__s___00456bdc,
                        PTR_s__efs_service_ERR_Open_failed__s___00456bdc,param_2,iVar5);
  }
  return 0;
}

