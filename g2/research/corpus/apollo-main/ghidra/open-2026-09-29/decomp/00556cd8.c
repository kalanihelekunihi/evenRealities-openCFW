
undefined4 FUN_00556cd8(undefined4 param_1,uint param_2)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  uint uVar4;
  
  iVar1 = DAT_005573fc;
  *(undefined4 *)(DAT_005573fc + 0x3c) = 1;
  uVar4 = (param_2 & 0xffff) - 1;
  if (uVar4 < *(uint *)(iVar1 + 0x2c)) {
    iVar2 = teleprompt_page_data_get(uVar4);
    if (iVar2 == 0) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(2,PTR_s_teleprompt_ui_00556ec4,PTR_s_D__01_workspace_s200_ap510b_iar__00556ec0,
                     PTR_s_teleprompt_ui_action_main_page_s_0055741c,0x7df,
                     PTR_s_switch_prev_target_page_not_read_00557424,uVar4);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x8400000,PTR_s__teleprompt_ui_switch_prev_targe_00557428,
                            PTR_s__teleprompt_ui_switch_prev_targe_00557428,uVar4);
      }
      FUN_0058c874(uVar4);
      teleprompt_page_data_set_window(uVar4);
      *(undefined4 *)(iVar1 + 0x3c) = 0;
    }
    else {
      FUN_0058c882();
      *(uint *)(iVar1 + 0x34) = param_2 >> 0x10;
      *(uint *)(iVar1 + 0x30) = param_2 & 0xffff;
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(3,PTR_s_teleprompt_ui_00556ec4,PTR_s_D__01_workspace_s200_ap510b_iar__00556ec0,
                     PTR_s_teleprompt_ui_action_main_page_s_0055741c,0x7ea,
                     PTR_s_switch_start___window__start_pag_0055742c,*(undefined4 *)(iVar1 + 0x2c),4
                     ,*(undefined4 *)(iVar1 + 0x30),*(undefined4 *)(iVar1 + 0x34),uVar4);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0xd400000,PTR_s__teleprompt_ui_switch_start___wi_00557430,
                            PTR_s__teleprompt_ui_switch_start___wi_00557430,
                            *(undefined4 *)(iVar1 + 0x2c),4,*(undefined4 *)(iVar1 + 0x30),
                            *(undefined4 *)(iVar1 + 0x34),uVar4);
      }
      uVar3 = FUN_0044dce2(*(undefined4 *)(iVar1 + 0x18),3);
      FUN_00555514(uVar3,uVar4);
      FUN_00554b2c(uVar3,uVar4);
      FUN_0044daca(uVar3,0);
      FUN_0043f66c(*(undefined4 *)(iVar1 + 0x18));
      *(uint *)(iVar1 + 0x2c) = uVar4;
      teleprompt_page_data_set_window(*(undefined4 *)(iVar1 + 0x2c));
      FUN_0044ea04(*(undefined4 *)(iVar1 + 0x18),*(int *)(iVar1 + 0x34) * 0x1c + 0x118,0);
      *(undefined4 *)(iVar1 + 0x3c) = 0;
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(3,PTR_s_teleprompt_ui_00556ec4,PTR_s_D__01_workspace_s200_ap510b_iar__00556ec0,
                     PTR_s_teleprompt_ui_action_main_page_s_0055741c,0x7fa,
                     PTR_s_switch_complete___window__start__00557434,*(undefined4 *)(iVar1 + 0x2c));
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0xc400000,PTR_s__teleprompt_ui_switch_complete____00557438,
                            PTR_s__teleprompt_ui_switch_complete____00557438,
                            *(undefined4 *)(iVar1 + 0x2c));
      }
    }
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(2,PTR_s_teleprompt_ui_00556ec4,PTR_s_D__01_workspace_s200_ap510b_iar__00556ec0,
                   PTR_s_teleprompt_ui_action_main_page_s_0055741c,0x7d9,
                   PTR_s_switch_page_id_is_in_window_rang_00557418);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x8000000,PTR_s__teleprompt_ui_switch_page_id_is_00557420);
    }
    *(undefined4 *)(iVar1 + 0x3c) = 0;
  }
  return 0;
}

