
undefined4 FUN_00467d68(int param_1,undefined *param_2,int param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  int iStack_18;
  undefined *puStack_14;
  int iStack_10;
  undefined4 uStack_c;
  
  iStack_18 = param_1;
  puStack_14 = param_2;
  iStack_10 = param_3;
  uStack_c = param_4;
  if (param_3 == 10) {
    iVar3 = FUN_0045a568();
    if (iVar3 == 1) {
      iVar3 = settings_get_config();
      uVar1 = semantic_get_heading_degrees();
      *(undefined4 *)(iVar3 + 0x10) = uVar1;
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        iVar3 = settings_get_config();
        iStack_10 = *(int *)(iVar3 + 0x10);
        puStack_14 = PTR_s_LV_EVENT_CLICKED_head_up_angle_c_00467fc8;
        iStack_18 = 0x2de;
        FUN_0043d574(3,PTR_s_setting_00467f14,PTR_s_D__01_workspace_s200_ap510b_iar__00467f10,
                     PTR_s_setting_page_event_handler_00467fcc);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        iVar3 = settings_get_config();
        compress_log_output(0xc400000,PTR_s__setting_LV_EVENT_CLICKED_head_u_00467fd0,
                            PTR_s__setting_LV_EVENT_CLICKED_head_u_00467fd0,
                            *(undefined4 *)(iVar3 + 0x10));
      }
      iVar3 = settings_get_config();
      iVar2 = settings_get_config();
      iStack_18 = *(int *)(iVar2 + 0x10) + *(int *)(iVar3 + 0xc);
      if (0x5a < iStack_18) {
        iStack_18 = 0x5a;
      }
      if (iStack_18 < -0x5a) {
        iStack_18 = -0x5a;
      }
      puStack_14 = *(undefined **)(PTR_DAT_00467fd4 + 4);
      HUB_ParameterConfig(1,&iStack_18);
      FUN_00464bb2(9,0,0,0);
    }
  }
  else if ((((param_3 != 0x42) && (param_3 != 0x43)) && (param_3 == 0x48)) &&
          (iVar3 = FUN_0045a568(), iVar3 == 1)) {
    FUN_00464c36(9,0,0,0);
  }
  return 1;
}

