
undefined8 FUN_00467c34(int *param_1,undefined *param_2,undefined4 param_3,undefined4 param_4)

{
  char cVar1;
  int iVar2;
  int *piVar3;
  
  if (param_1 == (int *)0x0) {
    iVar2 = FUN_0043d0ce();
    piVar3 = param_1;
    if (iVar2 << 0x1e < 0) {
      piVar3 = (int *)0x2b3;
      param_2 = PTR_s_control_data_is_NULL_00467fa4;
      FUN_0043d574(2,PTR_s_setting_00467f14,PTR_s_D__01_workspace_s200_ap510b_iar__00467f10,
                   PTR_s_setting_handle_app_control_devic_00467fa8,0x2b3,
                   PTR_s_control_data_is_NULL_00467fa4,param_3,param_4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x8000000,PTR_s__setting_control_data_is_NULL_00467fac,
                          PTR_s__setting_control_data_is_NULL_00467fac);
    }
  }
  else {
    piVar3 = param_1;
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      piVar3 = (int *)0x2b7;
      param_2 = PTR_s_Received_app_control_device__tur_00467fb0;
      FUN_0043d574(4,PTR_s_setting_00467f14,PTR_s_D__01_workspace_s200_ap510b_iar__00467f10,
                   PTR_s_setting_handle_app_control_devic_00467fa8,0x2b7,
                   PTR_s_Received_app_control_device__tur_00467fb0,*param_1);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10400000,PTR_s__setting_Received_app_control_de_00467fb4,
                          PTR_s__setting_Received_app_control_de_00467fb4,*param_1);
    }
    if (*param_1 == 1) {
      iVar2 = FUN_00443484();
      if (iVar2 == 0) {
        cVar1 = FUN_0045a570();
        if (cVar1 == '\x01') {
          iVar2 = FUN_0043d0ce();
          if (iVar2 << 0x1e < 0) {
            piVar3 = (int *)0x2bd;
            param_2 = PTR_s_Device_not_running__start_backgr_00467fb8;
            FUN_0043d574(3,PTR_s_setting_00467f14,PTR_s_D__01_workspace_s200_ap510b_iar__00467f10,
                         PTR_s_setting_handle_app_control_devic_00467fa8);
          }
          iVar2 = FUN_0043d0ce();
          if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
            compress_log_output(0xc000000,PTR_s__setting_Device_not_running__sta_00467fbc,
                                PTR_s__setting_Device_not_running__sta_00467fbc);
          }
          FUN_00466890();
        }
      }
      else {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          piVar3 = (int *)0x2c1;
          param_2 = PTR_s_Device_already_running__ignore_t_00467fc0;
          FUN_0043d574(4,PTR_s_setting_00467f14,PTR_s_D__01_workspace_s200_ap510b_iar__00467f10,
                       PTR_s_setting_handle_app_control_devic_00467fa8);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0x10000000,PTR_s__setting_Device_already_running__00467fc4,
                              PTR_s__setting_Device_already_running__00467fc4);
        }
      }
    }
  }
  return CONCAT44(param_2,piVar3);
}

