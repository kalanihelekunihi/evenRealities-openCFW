
undefined8 FUN_0054c3f2(undefined4 param_1,undefined4 param_2,undefined *param_3,uint param_4)

{
  char *pcVar1;
  undefined4 *puVar2;
  int iVar3;
  undefined4 local_18;
  undefined *local_14;
  uint local_10;
  
  puVar2 = DAT_0054ceb4;
  pcVar1 = DAT_0054ceb0;
  local_18 = param_2;
  local_14 = param_3;
  if (*DAT_0054ceb0 == '\x02') {
    local_10 = param_4;
    iVar3 = ui_common_api_fn_00509dfa(*DAT_0054ceb4);
    if (iVar3 == 0) {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        local_14 = DAT_0054ceb8;
        local_18 = 0xb8f;
        FUN_0043d574(4,PTR_s_navigation_ui_0054c5ac,PTR_s_D__01_workspace_s200_ap510b_iar__0054c5a8,
                     PTR_s_navigation_location_list_select__0054cf2c);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x10000000,PTR_s__navigation_ui_navigation_ui_ref_0054cf30,
                            PTR_s__navigation_ui_navigation_ui_ref_0054cf30);
      }
      ui_common_api_fn_00509e14(*puVar2,&local_10,1);
      if ((local_10 & 0xff) == 10) {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          local_14 = PTR_s_navigation_ui_reflash_page_handl_0054cf34;
          local_18 = 0xb94;
          FUN_0043d574(4,PTR_s_navigation_ui_0054c5ac,
                       PTR_s_D__01_workspace_s200_ap510b_iar__0054c5a8,
                       PTR_s_navigation_location_list_select__0054cf2c);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x10000000,PTR_s__navigation_ui_navigation_ui_ref_0054cf38);
        }
        FUN_0054cfd0(2);
        if (*DAT_0054c588 != 0) {
          FUN_0044d878(*DAT_0054c588);
        }
        *pcVar1 = '\t';
        *DAT_0054cccc = 0;
        *DAT_0054cca0 = 0;
        ui_common_api_fn_00509f52(*puVar2);
        FUN_00548b98();
      }
      else if ((local_10 & 0xff) == 0x44) {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          local_14 = PTR_s_navigation_ui_reflash_page_handl_0054cf3c;
          local_18 = 0xba9;
          FUN_0043d574(4,PTR_s_navigation_ui_0054c5ac,
                       PTR_s_D__01_workspace_s200_ap510b_iar__0054c5a8,
                       PTR_s_navigation_location_list_select__0054cf2c);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x10000000,PTR_s__navigation_ui_navigation_ui_ref_0054cf40,
                              PTR_s__navigation_ui_navigation_ui_ref_0054cf40);
        }
        FUN_0054cfd0(1);
      }
      else if ((local_10 & 0xff) == 0x45) {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          local_14 = PTR_s_navigation_ui_reflash_page_handl_0054cf44;
          local_18 = 0xbac;
          FUN_0043d574(4,PTR_s_navigation_ui_0054c5ac,
                       PTR_s_D__01_workspace_s200_ap510b_iar__0054c5a8,
                       PTR_s_navigation_location_list_select__0054cf2c);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x10000000,PTR_s__navigation_ui_navigation_ui_ref_0054cf48,
                              PTR_s__navigation_ui_navigation_ui_ref_0054cf48);
        }
        FUN_0054cfd0(0);
      }
    }
  }
  return CONCAT44(local_14,local_18);
}

