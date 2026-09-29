
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_0049ddb8(int param_1,char *param_2,int param_3,undefined4 param_4)

{
  char cVar1;
  int iVar2;
  int iVar3;
  char *pcStack_30;
  undefined *puStack_2c;
  int iStack_28;
  char *apcStack_24 [2];
  undefined1 auStack_1c [8];
  undefined4 uStack_14;
  
  uStack_14 = param_4;
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    puStack_2c = PTR_s_Dashboard_recv_data_len____d__ra_0049e670;
    pcStack_30 = (char *)0x320;
    iStack_28 = param_3;
    apcStack_24[0] = param_2;
    FUN_0043d574(4,PTR_s_dashboard_0049e444,PTR_s_D__01_workspace_s200_ap510b_iar__0049e440,
                 PTR_s_Dashboard_common_data_handler_0049e674);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    pcStack_30 = param_2;
    compress_log_output(0x10800000,PTR_s__dashboard_Dashboard_recv_data_l_0049e678,
                        PTR_s__dashboard_Dashboard_recv_data_l_0049e678,param_3);
  }
  FUN_0049c09a();
  iVar2 = _DAT_0049e67c;
  if (param_1 == 0) {
    if ((param_2 != (char *)0x0) && (param_3 != 0)) {
      cVar1 = FUN_004fe318(param_2,param_3,_DAT_0049e67c);
      if (cVar1 == '\0') {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          puStack_2c = PTR_s_dashboard_parse_data_package_fai_0049e680;
          pcStack_30 = (char *)0x327;
          FUN_0043d574(1,PTR_s_dashboard_0049e444,PTR_s_D__01_workspace_s200_ap510b_iar__0049e440,
                       PTR_s_Dashboard_common_data_handler_0049e674);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0x4000000,PTR_s__dashboard_dashboard_parse_data__0049e684,
                              PTR_s__dashboard_dashboard_parse_data__0049e684);
        }
      }
      else {
        FUN_0049ce14(iVar2);
        if (*(char *)(iVar2 + 0x14b8) == '\x01') {
          FUN_004fedcc();
        }
        else if (*(char *)(iVar2 + 0x14b9) != '\x01') {
          if (*(char *)(iVar2 + 0x14b3) == '\x01') {
            FUN_004fec98(1);
          }
          else {
            FUN_004fec98();
          }
        }
      }
    }
  }
  else if (param_1 == 5) {
    cVar1 = *param_2;
    if (cVar1 == '\x10') {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        puStack_2c = PTR_s_DASHBOARD_NEWS_LOAD_CACHE_NEWS_D_0049e688;
        pcStack_30 = (char *)0x34b;
        FUN_0043d574(3,PTR_s_dashboard_0049e444,PTR_s_D__01_workspace_s200_ap510b_iar__0049e440,
                     PTR_s_Dashboard_common_data_handler_0049e674);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0xc000000,_DAT_0049ea04,_DAT_0049ea04);
      }
      func_0x004fdf74(_DAT_0049ea08);
      iVar2 = FUN_0045a568();
      if (((iVar2 == 1) && (iVar2 = FUN_00443484(), iVar2 == 1)) &&
         (iVar2 = FUN_004434d0(1), iVar2 == 1)) {
        FUN_0043c0e4(auStack_1c,5,0);
        auStack_1c[0] = 0xf;
        iVar2 = FUN_0045aaca(1,auStack_1c,1,100);
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          puStack_2c = PTR_s_dashboard_send_news_event_to_UI_a_0049ea0c;
          pcStack_30 = (char *)0x355;
          iStack_28 = iVar2;
          FUN_0043d574(4,PTR_s_dashboard_0049e444,PTR_s_D__01_workspace_s200_ap510b_iar__0049e440,
                       PTR_s_Dashboard_common_data_handler_0049e674);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x10400000,PTR_s__dashboard_dashboard_send_news_e_0049ea10,
                              PTR_s__dashboard_dashboard_send_news_e_0049ea10,iVar2);
        }
      }
    }
    else if (cVar1 == '\x11') {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        puStack_2c = PTR_s_DASHBOARD_CLEAR_ALL_DATA_EVENT__c_0049ea14;
        pcStack_30 = (char *)0x35b;
        FUN_0043d574(3,PTR_s_dashboard_0049e444,PTR_s_D__01_workspace_s200_ap510b_iar__0049e440,
                     PTR_s_Dashboard_common_data_handler_0049e674);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0xc000000,PTR_s__dashboard_DASHBOARD_CLEAR_ALL_D_0049ea18,
                            PTR_s__dashboard_DASHBOARD_CLEAR_ALL_D_0049ea18);
      }
      func_0x004fdf08();
      FUN_0043c0e4(_DAT_0049ea08,0x8ef8,0);
      iVar2 = FUN_0045a568();
      if (((iVar2 == 1) && (iVar2 = FUN_00443484(), iVar2 == 1)) &&
         (iVar2 = FUN_004434d0(1), iVar2 == 1)) {
        FUN_0043c0e4(apcStack_24,5,0);
        apcStack_24[0] = (char *)CONCAT31(apcStack_24[0]._1_3_,0x12);
        iVar2 = FUN_0045aaca(1,apcStack_24,1,100);
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          puStack_2c = PTR_s_dashboard_send_news_event_to_UI_a_0049ea0c;
          pcStack_30 = (char *)0x365;
          iStack_28 = iVar2;
          FUN_0043d574(4,PTR_s_dashboard_0049e444,PTR_s_D__01_workspace_s200_ap510b_iar__0049e440,
                       PTR_s_Dashboard_common_data_handler_0049e674);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x10400000,PTR_s__dashboard_dashboard_send_news_e_0049ea10,
                              PTR_s__dashboard_dashboard_send_news_e_0049ea10,iVar2);
        }
      }
    }
    else if (cVar1 == '\x13') {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        puStack_2c = PTR_s_DASHBOARD_RING_STATUS_CHANGE_EVE_0049ea1c;
        pcStack_30 = (char *)0x36b;
        FUN_0043d574(3,PTR_s_dashboard_0049e444,PTR_s_D__01_workspace_s200_ap510b_iar__0049e440,
                     PTR_s_Dashboard_common_data_handler_0049e674);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0xc000000,PTR_s__dashboard_DASHBOARD_RING_STATUS_0049ea20,
                            PTR_s__dashboard_DASHBOARD_RING_STATUS_0049ea20);
      }
      iVar2 = FUN_0045a568();
      if (((iVar2 == 1) && (iVar2 = FUN_00443484(), iVar2 == 1)) &&
         (iVar2 = FUN_004434d0(1), iVar2 == 1)) {
        FUN_0043c0e4(&pcStack_30,3,0);
        FUN_0043c0e4(&pcStack_30,3,0);
        FUN_00439be4(&pcStack_30,param_2,param_3);
        FUN_00464bb2(1,&pcStack_30,3,0);
      }
    }
  }
  return 0;
}

