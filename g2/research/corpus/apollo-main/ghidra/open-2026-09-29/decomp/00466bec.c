
undefined8 FUN_00466bec(ushort *param_1,undefined *param_2,undefined4 param_3,undefined4 param_4)

{
  ushort uVar1;
  int iVar2;
  ushort *puVar3;
  
  if (param_1 == (ushort *)0x0) {
    iVar2 = FUN_0043d0ce();
    puVar3 = param_1;
    if (iVar2 << 0x1e < 0) {
      puVar3 = (ushort *)0xf1;
      param_2 = PTR_s_bri_data_is_NULL_004674d4;
      FUN_0043d574(2,PTR_s_setting_004672f0,PTR_s_D__01_workspace_s200_ap510b_iar__004672ec,
                   PTR_s_setting_handle_brightness_settin_004674d8,0xf1,
                   PTR_s_bri_data_is_NULL_004674d4,param_3,param_4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x8000000,PTR_s__setting_bri_data_is_NULL_004674dc,
                          PTR_s__setting_bri_data_is_NULL_004674dc);
    }
  }
  else {
    uVar1 = *param_1;
    puVar3 = param_1;
    if (uVar1 == 1) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        puVar3 = (ushort *)0xf7;
        param_2 = PTR_s_Received_auto_adjust_value___d_004674e0;
        FUN_0043d574(3,PTR_s_setting_004672f0,PTR_s_D__01_workspace_s200_ap510b_iar__004672ec,
                     PTR_s_setting_handle_brightness_settin_004674d8,0xf7,
                     PTR_s_Received_auto_adjust_value___d_004674e0,*(undefined4 *)(param_1 + 2));
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0xc400000,PTR_s__setting_Received_auto_adjust_va_004674e4,
                            PTR_s__setting_Received_auto_adjust_va_004674e4,
                            *(undefined4 *)(param_1 + 2));
      }
      settings_configure_auto_brightness(*(undefined4 *)(param_1 + 2));
    }
    else {
      if (uVar1 != 0) {
        if (uVar1 == 3) {
          iVar2 = FUN_0043d0ce();
          if (iVar2 << 0x1e < 0) {
            puVar3 = (ushort *)0x101;
            param_2 = PTR_s__Left_Calibration__Received_leve_004674f0;
            FUN_0043d574(3,PTR_s_setting_004672f0,PTR_s_D__01_workspace_s200_ap510b_iar__004672ec,
                         PTR_s_setting_handle_brightness_settin_004674d8,0x101,
                         PTR_s__Left_Calibration__Received_leve_004674f0,
                         *(undefined4 *)(param_1 + 2));
          }
          iVar2 = FUN_0043d0ce();
          if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
            compress_log_output(0xc400000,PTR_s__setting__Left_Calibration__Rece_004674f4,
                                PTR_s__setting__Left_Calibration__Rece_004674f4,
                                *(undefined4 *)(param_1 + 2));
          }
          if (*(uint *)(param_1 + 2) < 0xb) {
            iVar2 = settings_get_config();
            *(char *)(iVar2 + 0x16) = (char)*(undefined4 *)(param_1 + 2);
          }
          else {
            iVar2 = settings_get_config();
            *(undefined1 *)(iVar2 + 0x16) = 10;
          }
          iVar2 = settings_get_config();
          *(undefined1 *)(iVar2 + 0x17) = 0;
          settings_apply_auto_brightness();
          goto LAB_00466e1a;
        }
        if (uVar1 < 3) {
          iVar2 = FUN_0043d0ce();
          if (iVar2 << 0x1e < 0) {
            puVar3 = (ushort *)0xfc;
            param_2 = PTR_s__Brightness_Level__Received_brig_004674e8;
            FUN_0043d574(3,PTR_s_setting_004672f0,PTR_s_D__01_workspace_s200_ap510b_iar__004672ec,
                         PTR_s_setting_handle_brightness_settin_004674d8,0xfc,
                         PTR_s__Brightness_Level__Received_brig_004674e8,
                         *(undefined4 *)(param_1 + 2));
          }
          iVar2 = FUN_0043d0ce();
          if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
            compress_log_output(0xc400000,PTR_s__setting__Brightness_Level__Rece_004674ec,
                                PTR_s__setting__Brightness_Level__Rece_004674ec,
                                *(undefined4 *)(param_1 + 2));
          }
          settings_set_brightness_level(*(undefined4 *)(param_1 + 2));
          goto LAB_00466e1a;
        }
        if (uVar1 == 4) {
          iVar2 = FUN_0043d0ce();
          if (iVar2 << 0x1e < 0) {
            puVar3 = (ushort *)0x110;
            param_2 = PTR_s__Right_Calibration__Received_rig_004674f8;
            FUN_0043d574(3,PTR_s_setting_004672f0,PTR_s_D__01_workspace_s200_ap510b_iar__004672ec,
                         PTR_s_setting_handle_brightness_settin_004674d8,0x110,
                         PTR_s__Right_Calibration__Received_rig_004674f8,
                         *(undefined4 *)(param_1 + 2));
          }
          iVar2 = FUN_0043d0ce();
          if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
            compress_log_output(0xc400000,PTR_s__setting__Right_Calibration__Rec_004674fc,
                                PTR_s__setting__Right_Calibration__Rec_004674fc,
                                *(undefined4 *)(param_1 + 2));
          }
          if (*(uint *)(param_1 + 2) < 0xb) {
            iVar2 = settings_get_config();
            *(char *)(iVar2 + 0x17) = (char)*(undefined4 *)(param_1 + 2);
          }
          else {
            iVar2 = settings_get_config();
            *(undefined1 *)(iVar2 + 0x17) = 10;
          }
          iVar2 = settings_get_config();
          *(undefined1 *)(iVar2 + 0x16) = 0;
          settings_apply_auto_brightness();
          goto LAB_00466e1a;
        }
      }
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        puVar3 = (ushort *)0x11e;
        param_2 = PTR_s_Unknown_brightness_type___d_00467500;
        FUN_0043d574(2,PTR_s_setting_004672f0,PTR_s_D__01_workspace_s200_ap510b_iar__004672ec,
                     PTR_s_setting_handle_brightness_settin_004674d8,0x11e,
                     PTR_s_Unknown_brightness_type___d_00467500,*param_1);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x8400000,PTR_s__setting_Unknown_brightness_type_00467504,
                            PTR_s__setting_Unknown_brightness_type_00467504,*param_1);
      }
    }
  }
LAB_00466e1a:
  return CONCAT44(param_2,puVar3);
}

