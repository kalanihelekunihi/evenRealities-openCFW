
undefined8 EFS_CancelExport(int param_1,undefined *param_2,undefined4 param_3,undefined4 param_4)

{
  char *pcVar1;
  int *piVar2;
  int iVar3;
  int iVar4;
  
  pcVar1 = DAT_00458d8c;
  if (*DAT_00458d8c != '\0') {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      param_1 = 0x3a8;
      param_2 = PTR_s_EFS_cancel_export__device_local_s_00458de4;
      FUN_0043d574(2,PTR_s_efs_service_00458d3c,PTR_s_D__01_workspace_s200_ap510b_iar__00458d38,
                   PTR_s_EFS_CancelExport_00458de8,0x3a8,
                   PTR_s_EFS_cancel_export__device_local_s_00458de4,param_3,param_4);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x8000000,PTR_s__efs_service_EFS_cancel_export__d_00458dec,
                          PTR_s__efs_service_EFS_cancel_export__d_00458dec);
    }
    _evenEfsReplyToAPP(0xc6,3,8);
    piVar2 = DAT_00458de0;
    if ((char)DAT_00458de0[1] == '\x01') {
      if (*DAT_00458de0 == 0) {
        iVar3 = 0;
      }
      else {
        iVar3 = file_close(*DAT_00458de0);
        *piVar2 = 0;
      }
      if (iVar3 < 0) {
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          param_1 = 0x3b3;
          param_2 = PTR_s_ERR_Close_failed__s____d_00458d40;
          FUN_0043d574(1,PTR_s_efs_service_00458d3c,PTR_s_D__01_workspace_s200_ap510b_iar__00458d38,
                       PTR_s_EFS_CancelExport_00458de8,0x3b3,PTR_s_ERR_Close_failed__s____d_00458d40
                       ,(int)piVar2 + 5,iVar3);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0x4800000,PTR_s__efs_service_ERR_Close_failed__s_00458d44,
                              PTR_s__efs_service_ERR_Close_failed__s_00458d44,(int)piVar2 + 5);
          param_1 = iVar3;
        }
      }
    }
    FUN_0043c0e4(piVar2,0x78,0);
    *pcVar1 = '\0';
    compress_log_export_notify(0);
    ble_param_reset_delayed_event(2000);
  }
  return CONCAT44(param_2,param_1);
}

