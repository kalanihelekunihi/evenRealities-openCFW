
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8
onboarding_page_event_handler
          (undefined4 param_1,undefined4 param_2,undefined *param_3,undefined4 *param_4)

{
  int *piVar1;
  int *piVar2;
  int iVar3;
  undefined4 *puVar4;
  
  piVar2 = _DAT_00469124;
  piVar1 = _DAT_00469118;
  if (param_3 == (undefined1 *)0x42) {
    puVar4 = (undefined4 *)0x0;
    if (param_4 != (undefined4 *)0x0) {
      puVar4 = (undefined4 *)*param_4;
    }
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      param_2 = 0x1cf;
      param_3 = PTR_s_foregroundID____d_0046910c;
      param_4 = puVar4;
      FUN_0043d574(3,PTR_s_onboarding_004690e0,PTR_s_D__01_workspace_s200_ap510b_iar__004690dc,
                   PTR_s_onboarding_page_event_handler_00469110,0x1cf,
                   PTR_s_foregroundID____d_0046910c,puVar4);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0xc400000,PTR_s__onboarding_foregroundID____d_00469114,
                          PTR_s__onboarding_foregroundID____d_00469114,puVar4,param_2,param_3,
                          param_4);
    }
    piVar1 = _DAT_00469118;
    if (((*_DAT_00469118 != 0) && (puVar4 != (undefined4 *)0x0)) && (puVar4 != (undefined4 *)0x21))
    {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        param_2 = 0x1d4;
        FUN_0043d574(4,PTR_s_onboarding_004690e0,PTR_s_D__01_workspace_s200_ap510b_iar__004690dc,
                     PTR_s_onboarding_page_event_handler_00469110,0x1d4,_DAT_0046911c);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x10000000,_DAT_00469120,_DAT_00469120);
      }
      onboarding_darken_widget_colors_recursive(*piVar1);
      *_DAT_00469124 = 1;
    }
  }
  else if (param_3 == (undefined1 *)0x43) {
    if ((*_DAT_00469118 != 0) && (*_DAT_00469124 == 1)) {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        param_2 = 0x1de;
        FUN_0043d574(4,PTR_s_onboarding_004690e0,PTR_s_D__01_workspace_s200_ap510b_iar__004690dc,
                     PTR_s_onboarding_page_event_handler_00469110,0x1de,
                     PTR_s_onboarding_resume_widget_colors__00469128);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x10000000,PTR_s__onboarding_onboarding_resume_wi_0046912c,
                            PTR_s__onboarding_onboarding_resume_wi_0046912c);
      }
      onboarding_resume_widget_colors_recursive(*piVar1);
      *piVar2 = 0;
    }
    iVar3 = FUN_0045a568();
    if ((iVar3 == 1) && (*_DAT_00468f20 == '\x04')) {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        param_2 = 0x1f2;
        FUN_0043d574(3,PTR_s_onboarding_004690e0,PTR_s_D__01_workspace_s200_ap510b_iar__004690dc,
                     PTR_s_onboarding_page_event_handler_00469110,0x1f2,
                     PTR_s_Onboarding__request_display_stop_00469130);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0xc000000,PTR_s__onboarding_Onboarding__request_d_00469134,
                            PTR_s__onboarding_Onboarding__request_d_00469134);
      }
      FUN_00464c36(0x10,0,0,0);
    }
  }
  else if (param_3 == (undefined1 *)0xa) {
    iVar3 = FUN_0045a568();
    if (iVar3 != 2) {
      ui_onboarding_main_sub_004A8E6C(10,param_4);
    }
  }
  else if (param_3 == &SUB_00000048) {
    iVar3 = FUN_0045a568();
    if (iVar3 != 2) {
      ui_onboarding_main_sub_004A8E6C(0x48,param_4);
    }
  }
  else if (param_3 == (undefined1 *)0x4b) {
    iVar3 = FUN_0045a568();
    if (iVar3 != 2) {
      ui_onboarding_main_sub_004A8E6C(0x4b,param_4);
    }
  }
  else if (param_3 != (undefined1 *)0x49) {
    if (param_3 == (undefined1 *)0x44) {
      iVar3 = FUN_0045a568();
      if (iVar3 != 2) {
        ui_onboarding_main_sub_004A8E6C(0x44,param_4);
      }
    }
    else if (param_3 == (undefined1 *)0x45) {
      iVar3 = FUN_0045a568();
      if (iVar3 != 2) {
        ui_onboarding_main_sub_004A8E6C(0x45,param_4);
      }
    }
    else if (param_3 == (undefined1 *)0x4a) {
      FUN_0045a568();
    }
    else if (param_3 == &NMI) {
      iVar3 = FUN_0045a568();
      if (iVar3 != 2) {
        ui_onboarding_main_sub_004A8E6C(8,param_4);
      }
    }
    else if (param_3 == &IRQ) {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        param_2 = 0x232;
        FUN_0043d574(4,PTR_s_onboarding_004690e0,PTR_s_D__01_workspace_s200_ap510b_iar__004690dc,
                     PTR_s_onboarding_page_event_handler_00469110,0x232,
                     PTR_s_IMU_Reflash_Event__00469138);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x10000000,PTR_s__onboarding_IMU_Reflash_Event__0046913c,
                            PTR_s__onboarding_IMU_Reflash_Event__0046913c);
      }
    }
  }
  return CONCAT44(param_2,1);
}

