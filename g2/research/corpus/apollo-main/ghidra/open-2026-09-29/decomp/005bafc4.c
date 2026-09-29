
undefined4 FUN_005bafc4(char *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  
  if (param_1 == (char *)0x0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(1,PTR_s_dashboard_wf_l4_005bb2d8,PTR_s_D__01_workspace_s200_ap510b_iar__005bb2d4,
                   PTR_s_layout4_validate_cfg_005bbb78,0x18e,
                   PTR_s_layout4_cfg_validate__cfg_NULL_005bbb74,param_3,param_4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__dashboard_wf_l4_layout4_cfg_val_005bbb7c,
                          PTR_s__dashboard_wf_l4_layout4_cfg_val_005bbb7c);
    }
    uVar2 = 0;
  }
  else if (*param_1 == '\x04') {
    if (param_1[5] == '\0') {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(1,PTR_s_dashboard_wf_l4_005bb2d8,
                     PTR_s_D__01_workspace_s200_ap510b_iar__005bb2d4,
                     PTR_s_layout4_validate_cfg_005bbb78,0x19b,DAT_005bbc7c,3);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x4400000,PTR_s__dashboard_wf_l4_layout4_cfg_val_005bbcb4,
                            PTR_s__dashboard_wf_l4_layout4_cfg_val_005bbcb4,3);
      }
      uVar2 = 0;
    }
    else if ((byte)param_1[5] < 4) {
      if (param_1[0x14] == param_1[5]) {
        if (param_1[6] == param_1[5]) {
          uVar2 = 1;
        }
        else {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            FUN_0043d574(1,PTR_s_dashboard_wf_l4_005bb2d8,
                         PTR_s_D__01_workspace_s200_ap510b_iar__005bb2d4,
                         PTR_s_layout4_validate_cfg_005bbb78,0x1aa,
                         PTR_s_layout4_cfg_validate__offset_cou_005bbcc8,param_1[6],param_1[5]);
          }
          iVar1 = FUN_0043d0ce();
          if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
            compress_log_output(0x4800000,PTR_s__dashboard_wf_l4_layout4_cfg_val_005bbccc,
                                PTR_s__dashboard_wf_l4_layout4_cfg_val_005bbccc,param_1[6],
                                param_1[5]);
          }
          uVar2 = 0;
        }
      }
      else {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          FUN_0043d574(1,PTR_s_dashboard_wf_l4_005bb2d8,
                       PTR_s_D__01_workspace_s200_ap510b_iar__005bb2d4,
                       PTR_s_layout4_validate_cfg_005bbb78,0x1a5,
                       PTR_s_layout4_cfg_validate__name_count_005bbcc0,param_1[0x14],param_1[5]);
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0x4800000,PTR_s__dashboard_wf_l4_layout4_cfg_val_005bbcc4,
                              PTR_s__dashboard_wf_l4_layout4_cfg_val_005bbcc4,param_1[0x14],
                              param_1[5]);
        }
        uVar2 = 0;
      }
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(1,PTR_s_dashboard_wf_l4_005bb2d8,
                     PTR_s_D__01_workspace_s200_ap510b_iar__005bb2d4,
                     PTR_s_layout4_validate_cfg_005bbb78,0x1a0,
                     PTR_s_layout4_cfg_validate__world_cloc_005bbcb8,param_1[5],3);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x4800000,PTR_s__dashboard_wf_l4_layout4_cfg_val_005bbcbc,
                            PTR_s__dashboard_wf_l4_layout4_cfg_val_005bbcbc,param_1[5],3);
      }
      uVar2 = 0;
    }
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(1,PTR_s_dashboard_wf_l4_005bb2d8,PTR_s_D__01_workspace_s200_ap510b_iar__005bb2d4,
                   PTR_s_layout4_validate_cfg_005bbb78,0x193,
                   PTR_s_layout4_cfg_validate__kind_misma_005bbb80,*param_1,4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4800000,DAT_005bbc38,DAT_005bbc38,*param_1,4);
    }
    uVar2 = 0;
  }
  return uVar2;
}

