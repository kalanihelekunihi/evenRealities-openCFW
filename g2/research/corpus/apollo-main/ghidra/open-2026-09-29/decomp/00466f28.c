
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 FUN_00466f28(ushort *param_1,undefined *param_2,undefined4 param_3,undefined4 param_4)

{
  ushort uVar1;
  char *pcVar2;
  char cVar3;
  int iVar4;
  ushort *puVar5;
  
  if (param_1 == (ushort *)0x0) {
    iVar4 = FUN_0043d0ce();
    puVar5 = param_1;
    if (iVar4 << 0x1e < 0) {
      puVar5 = (ushort *)0x16a;
      param_2 = PTR_s_head_up_data_is_NULL_00467520;
      FUN_0043d574(2,PTR_s_setting_004672f0,PTR_s_D__01_workspace_s200_ap510b_iar__004672ec,
                   PTR_s_setting_handle_head_up_setting_00467524,0x16a,
                   PTR_s_head_up_data_is_NULL_00467520,param_3,param_4);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x8000000,PTR_s__setting_head_up_data_is_NULL_00467528,
                          PTR_s__setting_head_up_data_is_NULL_00467528);
    }
  }
  else {
    uVar1 = *param_1;
    puVar5 = param_1;
    if (uVar1 == 1) {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        puVar5 = (ushort *)0x172;
        param_2 = PTR_s_Received_head_up_switch___d_0046752c;
        FUN_0043d574(3,PTR_s_setting_004672f0,PTR_s_D__01_workspace_s200_ap510b_iar__004672ec,
                     PTR_s_setting_handle_head_up_setting_00467524,0x172,
                     PTR_s_Received_head_up_switch___d_0046752c,*(undefined4 *)(param_1 + 2));
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0xc400000,PTR_s__setting_Received_head_up_switch_00467530,
                            PTR_s__setting_Received_head_up_switch_00467530,
                            *(undefined4 *)(param_1 + 2));
      }
      iVar4 = settings_get_config();
      *(char *)(iVar4 + 10) = (char)*(undefined4 *)(param_1 + 2);
    }
    else if (uVar1 != 0) {
      if (uVar1 == 3) {
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          puVar5 = (ushort *)0x17e;
          param_2 = PTR_s_Received_head_up_calibration_swi_0046753c;
          FUN_0043d574(3,PTR_s_setting_004672f0,PTR_s_D__01_workspace_s200_ap510b_iar__004672ec,
                       PTR_s_setting_handle_head_up_setting_00467524,0x17e,
                       PTR_s_Received_head_up_calibration_swi_0046753c,*(undefined4 *)(param_1 + 2))
          ;
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0xc400000,PTR_s__setting_Received_head_up_calibr_00467c18,
                              PTR_s__setting_Received_head_up_calibr_00467c18,
                              *(undefined4 *)(param_1 + 2));
        }
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          puVar5 = (ushort *)0x17f;
          param_2 = PTR_s______is_calibration_ui_showing___00467c1c;
          FUN_0043d574(4,PTR_s_setting_004672f0,PTR_s_D__01_workspace_s200_ap510b_iar__004672ec,
                       PTR_s_setting_handle_head_up_setting_00467524,0x17f,
                       PTR_s______is_calibration_ui_showing___00467c1c,*_DAT_00467d54);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0x10400000,PTR_s__setting______is_calibration_ui__00467c20,
                              PTR_s__setting______is_calibration_ui__00467c20,*_DAT_00467d54);
        }
        pcVar2 = _DAT_00467d54;
        if (*(int *)(param_1 + 2) == 1) {
          if (*_DAT_00467d54 == '\x01') goto LAB_00467132;
          cVar3 = FUN_0045a570();
          iVar4 = settings_get_config();
          *(undefined4 *)(iVar4 + 0x40) = 0;
          if (cVar3 == '\x01') {
            FUN_00464c36(0,0,0,0);
            FUN_00464b2e(9,0,0,0);
          }
          *pcVar2 = '\x01';
          setting_notify_recalibration_status_to_app(0);
        }
        else {
          *_DAT_00467d54 = '\0';
          cVar3 = FUN_0045a570();
          if (cVar3 == '\x01') {
            FUN_00464c36(9,0,0,0);
          }
        }
      }
      else if (uVar1 < 3) {
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          puVar5 = (ushort *)0x178;
          param_2 = PTR_s_Received_head_up_angle___d_00467534;
          FUN_0043d574(3,PTR_s_setting_004672f0,PTR_s_D__01_workspace_s200_ap510b_iar__004672ec,
                       PTR_s_setting_handle_head_up_setting_00467524,0x178,
                       PTR_s_Received_head_up_angle___d_00467534,*(undefined4 *)(param_1 + 2));
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0xc400000,PTR_s__setting_Received_head_up_angle__00467538,
                              PTR_s__setting_Received_head_up_angle__00467538,
                              *(undefined4 *)(param_1 + 2));
        }
        iVar4 = settings_get_config();
        *(undefined4 *)(iVar4 + 0xc) = *(undefined4 *)(param_1 + 2);
      }
    }
    if (*param_1 != 3) {
      SVC_Settings_HeadUpConfig();
    }
  }
LAB_00467132:
  return CONCAT44(param_2,puVar5);
}

