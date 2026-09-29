
undefined4
dashboard_watchface_manager_init
          (int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  int iVar2;
  undefined4 uVar3;
  undefined1 *puVar4;
  undefined1 uVar5;
  
  piVar1 = DAT_005007fc;
  if (param_1 != 0) {
    if (*DAT_005007fc != 0) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(2,PTR_s_dashboard_wf_mgr_005007e8,DAT_005007e4,
                     PTR_s_dashboard_watchface_manager_init_005007f4,0x3b,
                     PTR_s_manager_init__already_inited__de_00500800);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x8000000,PTR_s__dashboard_wf_mgr_manager_init__a_00500804,
                            PTR_s__dashboard_wf_mgr_manager_init__a_00500804);
      }
      dashboard_watchface_manager_deinit();
    }
    iVar2 = FUN_00558142();
    if (iVar2 == 0) {
      puVar4 = (undefined1 *)0x0;
    }
    else {
      puVar4 = (undefined1 *)(iVar2 + 8);
    }
    if (puVar4 == (undefined1 *)0x0) {
      uVar5 = 0;
    }
    else {
      uVar5 = *puVar4;
    }
    uVar3 = watchface_ops_for_kind(uVar5);
    iVar2 = try_create(uVar3,param_1,param_2,puVar4);
    *piVar1 = iVar2;
    if (*piVar1 == 0) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(1,PTR_s_dashboard_wf_mgr_005007e8,DAT_005007e4,
                     PTR_s_dashboard_watchface_manager_init_005007f4,0x4e,
                     PTR_s_manager_init__all_layouts_failed_00500810);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4000000,PTR_s__dashboard_wf_mgr_manager_init__a_00500814,
                            PTR_s__dashboard_wf_mgr_manager_init__a_00500814);
      }
      uVar3 = 0xffffffff;
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(3,PTR_s_dashboard_wf_mgr_005007e8,DAT_005007e4,
                     PTR_s_dashboard_watchface_manager_init_005007f4,0x4a,
                     PTR_s_manager_init_OK__kind__d_00500808,uVar5);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0xc400000,PTR_s__dashboard_wf_mgr_manager_init_O_0050080c,
                            PTR_s__dashboard_wf_mgr_manager_init_O_0050080c,uVar5);
      }
      uVar3 = 0;
    }
    return uVar3;
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    FUN_0043d574(1,PTR_s_dashboard_wf_mgr_005007e8,DAT_005007e4,
                 PTR_s_dashboard_watchface_manager_init_005007f4,0x35,
                 PTR_s_manager_init__parent_NULL_005007f0,param_3,param_4);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x4000000,PTR_s__dashboard_wf_mgr_manager_init__p_005007f8);
  }
  return 0xffffffff;
}

