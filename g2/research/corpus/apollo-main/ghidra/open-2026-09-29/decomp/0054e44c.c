
int FUN_0054e44c(int param_1,int param_2,int param_3,undefined4 param_4,undefined4 param_5)

{
  int iVar1;
  int iVar2;
  
  if (param_1 == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(1,PTR_s_navigation_ui_0054ed7c,PTR_s_D__01_workspace_s200_ap510b_iar__0054ed78,
                   PTR_s_navigation_create_rotated_img_0054ed74,0xf07,
                   PTR_s_Invalid_parent_object_0054ed70);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__navigation_ui_Invalid_parent_ob_0054ed80,
                          PTR_s__navigation_ui_Invalid_parent_ob_0054ed80);
    }
    iVar1 = 0;
  }
  else {
    iVar1 = FUN_00498668();
    if (iVar1 == 0) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(1,PTR_s_navigation_ui_0054ed7c,PTR_s_D__01_workspace_s200_ap510b_iar__0054ed78,
                     PTR_s_navigation_create_rotated_img_0054ed74,0xf0e,
                     PTR_s_Failed_to_create_image_object_fo_0054ed84);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x4000000,PTR_s__navigation_ui_Failed_to_create_i_0054ed88,
                            PTR_s__navigation_ui_Failed_to_create_i_0054ed88);
      }
      iVar1 = 0;
    }
    else {
      if ((param_2 != 0x78) || (param_3 != 0x78)) {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(2,PTR_s_navigation_ui_0054ed7c,
                       PTR_s_D__01_workspace_s200_ap510b_iar__0054ed78,
                       PTR_s_navigation_create_rotated_img_0054ed74,0xf15,
                       PTR_s_Display_size_mismatch__expected___0054ed8c,0x78,0x78,param_2,param_3);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0x9000000,PTR_s__navigation_ui_Display_size_mism_0054ed90,
                              PTR_s__navigation_ui_Display_size_mism_0054ed90,0x78,0x78,param_2,
                              param_3);
        }
      }
      FUN_0043f4c0(iVar1,param_2,param_3);
      FUN_0043f09a(iVar1,param_4,param_5);
      FUN_00498680(iVar1,0);
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(4,PTR_s_navigation_ui_0054ed7c,PTR_s_D__01_workspace_s200_ap510b_iar__0054ed78,
                     PTR_s_navigation_create_rotated_img_0054ed74,0xf24,
                     PTR_s_Created_rotated_image_object___d_0054ed94,param_2,param_3,param_4,param_5
                    );
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x11000000,PTR_s__navigation_ui_Created_rotated_i_0054ed98,
                            PTR_s__navigation_ui_Created_rotated_i_0054ed98,param_2,param_3,param_4,
                            param_5);
      }
    }
  }
  return iVar1;
}

