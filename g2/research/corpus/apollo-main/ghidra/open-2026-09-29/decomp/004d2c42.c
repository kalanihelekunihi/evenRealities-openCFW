
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_004d2c42(undefined4 param_1,undefined4 param_2,int param_3,undefined4 param_4)

{
  int iVar1;
  int iStack_10;
  undefined4 uStack_c;
  
  iStack_10 = param_3;
  uStack_c = param_4;
  if (param_3 == 10) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,PTR_s_system_alert_004d3428,PTR_s_D__01_workspace_s200_ap510b_iar__004d3424,
                   PTR_s_system_alert_page_event_handler_004d3438,0x4a,
                   PTR_s_LV_EVENT_CLICKED_004d3434);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10000000,PTR_s__system_alert_LV_EVENT_CLICKED_004d343c,
                          PTR_s__system_alert_LV_EVENT_CLICKED_004d343c);
    }
    iVar1 = FUN_0045a568();
    if ((iVar1 != 2) && (iVar1 = FUN_0045a568(), iVar1 == 1)) {
      *_DAT_004d3440 = 0;
      *_DAT_004d3444 = 0xb4;
      FUN_00464c36(0x21,0,0,0);
    }
  }
  else if (param_3 == 0x48) {
    iVar1 = FUN_0045a568();
    if ((iVar1 != 2) && (iVar1 = FUN_0045a568(), iVar1 == 1)) {
      *_DAT_004d3440 = 0;
      *_DAT_004d3444 = 0xb4;
      FUN_00464c36(0x21,0,0,0);
    }
  }
  else if (param_3 == 0x44) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,PTR_s_system_alert_004d3428,PTR_s_D__01_workspace_s200_ap510b_iar__004d3424,
                   PTR_s_system_alert_page_event_handler_004d3438,0x61,PTR_s_SCROLLUP_EVENT_004d3448
                  );
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10000000,PTR_s__system_alert_SCROLLUP_EVENT_004d344c,
                          PTR_s__system_alert_SCROLLUP_EVENT_004d344c);
    }
    iVar1 = FUN_0045a568();
    if ((iVar1 != 2) && (iVar1 = FUN_0045a568(), iVar1 == 1)) {
      *_DAT_004d3440 = 0;
      *_DAT_004d3444 = 0xb4;
      FUN_00464c36(0x21,0,0,0);
    }
  }
  else if (param_3 == 0x45) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,PTR_s_system_alert_004d3428,PTR_s_D__01_workspace_s200_ap510b_iar__004d3424,
                   PTR_s_system_alert_page_event_handler_004d3438,0x6d,
                   PTR_s_SCROLLDOWN_EVENT_004d3450);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10000000,PTR_s__system_alert_SCROLLDOWN_EVENT_004d3454,
                          PTR_s__system_alert_SCROLLDOWN_EVENT_004d3454);
    }
    iVar1 = FUN_0045a568();
    if ((iVar1 != 2) && (iVar1 = FUN_0045a568(), iVar1 == 1)) {
      *_DAT_004d3440 = 0;
      *_DAT_004d3444 = 0xb4;
      FUN_00464c36(0x21,0,0,0);
    }
  }
  else if (param_3 == 0x4d) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(3,PTR_s_system_alert_004d3428,PTR_s_D__01_workspace_s200_ap510b_iar__004d3424,
                   PTR_s_system_alert_page_event_handler_004d3438,0x79,
                   PTR_s_PAGE_EVENT_FOREGROUND_ENTER_ANIM_004d3458);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0xc000000,PTR_s__system_alert_PAGE_EVENT_FOREGRO_004d345c,
                          PTR_s__system_alert_PAGE_EVENT_FOREGRO_004d345c);
    }
    *_DAT_004d3440 = 1;
    *_DAT_004d3444 = 0xb4;
    iVar1 = FUN_0045a568();
    if (iVar1 == 1) {
      FUN_0043c0e4(&iStack_10,1,0);
      iStack_10 = CONCAT31(iStack_10._1_3_,5);
      FUN_0045aaca(0x21,&iStack_10,1,3000);
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(3,PTR_s_system_alert_004d3428,PTR_s_D__01_workspace_s200_ap510b_iar__004d3424,
                     PTR_s_system_alert_page_event_handler_004d3438,0x80,
                     PTR_s_send_system_alert_auto_exit_even_004d3460);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0xc000000,PTR_s__system_alert_send_system_alert_a_004d3464,
                            PTR_s__system_alert_send_system_alert_a_004d3464);
      }
    }
  }
  else if (param_3 == 0x4e) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(3,PTR_s_system_alert_004d3428,PTR_s_D__01_workspace_s200_ap510b_iar__004d3424,
                   PTR_s_system_alert_page_event_handler_004d3438,0x85,
                   PTR_s_PAGE_EVENT_FOREGROUND_EXIT_ANIM__004d3468);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0xc000000,PTR_s__system_alert_PAGE_EVENT_FOREGRO_004d346c,
                          PTR_s__system_alert_PAGE_EVENT_FOREGRO_004d346c);
    }
  }
  else if (param_3 == 0x40) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,PTR_s_system_alert_004d3428,PTR_s_D__01_workspace_s200_ap510b_iar__004d3424,
                   PTR_s_system_alert_page_event_handler_004d3438,0x89,
                   PTR_s_IMU_Reflash_Event__004d3470);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10000000,PTR_s__system_alert_IMU_Reflash_Event__004d3474,
                          PTR_s__system_alert_IMU_Reflash_Event__004d3474);
    }
  }
  return 1;
}

