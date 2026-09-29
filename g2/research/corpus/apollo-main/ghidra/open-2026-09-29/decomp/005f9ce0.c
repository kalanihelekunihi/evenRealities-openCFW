
undefined4 FUN_005f9ce0(undefined4 param_1,short *param_2,undefined4 param_3,undefined4 param_4)

{
  undefined *puVar1;
  undefined1 uVar2;
  char cVar3;
  int iVar4;
  undefined4 uVar5;
  
  uVar5 = param_3;
  iVar4 = productModeGet();
  if (iVar4 == 1) {
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      FUN_0043d574(4,PTR_s_ux_setting_0078c8fb_1_005f9ed4,
                   PTR_s_D__01_workspace_s200_ap510b_iar__005f9ed0,
                   PTR_s_UX_LocalSettingsSyncHandler_005f9ee0,0x1d,
                   PTR_s_In_production_test_mode__skip_ti_005f9edc,uVar5,param_4);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x10000000,PTR_s__ux_setting_In_production_test_m_005f9ee4,
                          PTR_s__ux_setting_In_production_test_m_005f9ee4);
    }
  }
  else {
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      FUN_0043d574(4,PTR_s_ux_setting_0078c8fb_1_005f9ed4,
                   PTR_s_D__01_workspace_s200_ap510b_iar__005f9ed0,
                   PTR_s_UX_LocalSettingsSyncHandler_005f9ee0,0x22,
                   PTR_s_raw_data___0x_x_len____d_005f9ee8,param_2,param_3);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x10800000,PTR_s__ux_setting_raw_data___0x_x_len___005f9eec,
                          PTR_s__ux_setting_raw_data___0x_x_len___005f9eec,param_2,param_3);
    }
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      FUN_0043d574(4,PTR_s_ux_setting_0078c8fb_1_005f9ed4,
                   PTR_s_D__01_workspace_s200_ap510b_iar__005f9ed0,
                   PTR_s_UX_LocalSettingsSyncHandler_005f9ee0,0x23,
                   PTR_s_pMsg_>head_msgSelfRole____d_MAST_005f9ef0,(char)param_2[2],1);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x10800000,PTR_s__ux_setting_pMsg_>head_msgSelfRo_005f9ef4,
                          PTR_s__ux_setting_pMsg_>head_msgSelfRo_005f9ef4,(char)param_2[2],1);
    }
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      uVar2 = FUN_0045a568();
      FUN_0043d574(4,PTR_s_ux_setting_0078c8fb_1_005f9ed4,
                   PTR_s_D__01_workspace_s200_ap510b_iar__005f9ed0,
                   PTR_s_UX_LocalSettingsSyncHandler_005f9ee0,0x24,
                   PTR_s_pMsg_>head_msgPeerRole____d__d_005f9ef8,*(undefined1 *)((int)param_2 + 5),
                   uVar2);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      uVar2 = FUN_0045a568();
      compress_log_output(0x10800000,PTR_s__ux_setting_pMsg_>head_msgPeerRo_005f9efc,
                          PTR_s__ux_setting_pMsg_>head_msgPeerRo_005f9efc,
                          *(undefined1 *)((int)param_2 + 5),uVar2);
    }
    if (*param_2 == 0x80) {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        FUN_0043d574(4,PTR_s_ux_setting_0078c8fb_1_005f9ed4,
                     PTR_s_D__01_workspace_s200_ap510b_iar__005f9ed0,
                     PTR_s_UX_LocalSettingsSyncHandler_005f9ee0,0x28,
                     PTR_s_eDevCfgCommandId_TIME_SYNC_005f9f00);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x10000000,PTR_s__ux_setting_eDevCfgCommandId_TIM_005f9f04,
                            PTR_s__ux_setting_eDevCfgCommandId_TIM_005f9f04);
      }
      if ((((char)param_2[2] == '\x01') &&
          (cVar3 = FUN_0045a568(), *(char *)((int)param_2 + 5) == cVar3)) ||
         (((char)param_2[2] == '\0' && (*(char *)((int)param_2 + 5) == '\0')))) {
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          FUN_0043d574(4,PTR_s_ux_setting_0078c8fb_1_005f9ed4,
                       PTR_s_D__01_workspace_s200_ap510b_iar__005f9ed0,
                       PTR_s_UX_LocalSettingsSyncHandler_005f9ee0,0x2b,
                       PTR_s_sysUtcSecond____lu_time_zone_____005f9f08,*(undefined4 *)(param_2 + 4),
                       *(undefined4 *)(param_2 + 6));
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0x10800000,PTR_s__ux_setting_sysUtcSecond____lu_t_005f9f0c,
                              PTR_s__ux_setting_sysUtcSecond____lu_t_005f9f0c,
                              *(undefined4 *)(param_2 + 4),*(undefined4 *)(param_2 + 6));
        }
        SVC_SystemTimeSync(*(undefined4 *)(param_2 + 4),(int)(char)*(undefined4 *)(param_2 + 6));
      }
      puVar1 = PTR_RPC_SystemTimeSync_1_005f9f10;
      fw_event_loop_remove_delayed(PTR_RPC_SystemTimeSync_1_005f9f10);
      fw_event_loop_push_delayed(puVar1,0,30000);
    }
  }
  return 0;
}

