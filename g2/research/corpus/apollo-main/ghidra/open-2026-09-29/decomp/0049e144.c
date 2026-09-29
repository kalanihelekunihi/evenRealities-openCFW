
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_0049e144(undefined4 param_1,undefined4 param_2,int param_3,int *param_4)

{
  int *piVar1;
  int *piVar2;
  int iVar3;
  uint uVar4;
  int iVar5;
  undefined4 uStack_38;
  undefined *puStack_34;
  int iStack_30;
  undefined1 uStack_1c;
  undefined1 uStack_18;
  
  piVar2 = _DAT_0049ea3c;
  piVar1 = _DAT_0049ea30;
  if (param_3 == 0x42) {
    iVar5 = 0;
    if (param_4 != (int *)0x0) {
      iVar5 = *param_4;
    }
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      puStack_34 = PTR_s_foregroundID____d_0049ea24;
      uStack_38 = 0x38a;
      iStack_30 = iVar5;
      FUN_0043d574(3,PTR_s_dashboard_0049e444,PTR_s_D__01_workspace_s200_ap510b_iar__0049e440,
                   PTR_s_dashboard_page_event_handler_0049ea28);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0xc400000,PTR_s__dashboard_foregroundID____d_0049ea2c,
                          PTR_s__dashboard_foregroundID____d_0049ea2c,iVar5);
    }
    piVar1 = _DAT_0049ea30;
    if (((*_DAT_0049ea30 != 0) && (iVar5 != 0)) && (iVar5 != 0x21)) {
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        puStack_34 = _DAT_0049ea34;
        uStack_38 = 0x38c;
        FUN_0043d574(4,PTR_s_dashboard_0049e444,PTR_s_D__01_workspace_s200_ap510b_iar__0049e440,
                     PTR_s_dashboard_page_event_handler_0049ea28);
      }
      iVar5 = FUN_0043d0ce();
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        compress_log_output(0x10000000,_DAT_0049ea38,_DAT_0049ea38);
      }
      FUN_0049c7fe();
      FUN_0049c93e(*piVar1);
      *_DAT_0049ea3c = 1;
    }
    iVar5 = FUN_0045a568();
    if (iVar5 == 1) {
      *_DAT_0049ea40 = 1;
      *_DAT_0049ea48 = *_DAT_0049ea44;
    }
  }
  else if (param_3 == 0x43) {
    if ((*_DAT_0049ea30 != 0) && (*_DAT_0049ea3c == 1)) {
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        puStack_34 = PTR_s_resume_widget_colors_recursive_0049ea4c;
        uStack_38 = 0x39c;
        FUN_0043d574(4,PTR_s_dashboard_0049e444,PTR_s_D__01_workspace_s200_ap510b_iar__0049e440,
                     PTR_s_dashboard_page_event_handler_0049ea28);
      }
      iVar5 = FUN_0043d0ce();
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        compress_log_output(0x10000000,PTR_s__dashboard_resume_widget_colors__0049ea50,
                            PTR_s__dashboard_resume_widget_colors__0049ea50);
      }
      FUN_0049c89e();
      FUN_0049cb50(*piVar1);
      *piVar2 = 0;
    }
    iVar5 = FUN_0045a568();
    if (iVar5 == 1) {
      *_DAT_0049ea40 = 0;
      *_DAT_0049ea48 = *_DAT_0049ea44;
      service_time_current_calendar_get(&puStack_34);
      uVar4 = service_time_current_epoch_get();
      FUN_0043c0e4(&uStack_38,4,0);
      FUN_0043c0e4(&uStack_38,4,0);
      uStack_38 = CONCAT13((char)(uVar4 / 0xe10) + (char)((uVar4 / 0xe10) / 0x18) * -0x18,
                           CONCAT12(uStack_18,CONCAT11(uStack_1c,7)));
      FUN_00464bb2(1,&uStack_38,4,0);
    }
  }
  else if (param_3 == 10) {
    iVar5 = FUN_0045a568();
    if (iVar5 != 2) {
      FUN_004e814c(10,param_4);
      *_DAT_0049ea48 = *_DAT_0049ea44;
    }
  }
  else if (param_3 == 0x48) {
    iVar5 = FUN_0045a568();
    if (iVar5 != 2) {
      FUN_004e814c(0x48,param_4);
      *_DAT_0049ea48 = *_DAT_0049ea44;
    }
  }
  else if (param_3 != 0x49) {
    if (param_3 == 0x44) {
      iVar5 = FUN_0045a568();
      if (iVar5 != 2) {
        FUN_004e814c(0x44,param_4);
        *_DAT_0049ea48 = *_DAT_0049ea44;
      }
    }
    else if (param_3 == 0x45) {
      iVar5 = FUN_0045a568();
      if (iVar5 != 2) {
        FUN_004e814c(0x45,param_4);
        *_DAT_0049ea48 = *_DAT_0049ea44;
      }
    }
    else if (param_3 == 0x4a) {
      FUN_0045a568();
    }
    else if (param_3 == 0x40) {
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        puStack_34 = PTR_s_IMU_Reflash_Event__0049ea54;
        uStack_38 = 1000;
        FUN_0043d574(4,PTR_s_dashboard_0049e444,PTR_s_D__01_workspace_s200_ap510b_iar__0049e440,
                     PTR_s_dashboard_page_event_handler_0049ea28);
      }
      iVar5 = FUN_0043d0ce();
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        compress_log_output(0x10000000,PTR_s__dashboard_IMU_Reflash_Event__0049ea58,
                            PTR_s__dashboard_IMU_Reflash_Event__0049ea58);
      }
    }
  }
  return 1;
}

