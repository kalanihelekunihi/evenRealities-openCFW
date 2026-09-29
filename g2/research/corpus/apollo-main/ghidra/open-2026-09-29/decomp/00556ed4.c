
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_00556ed4(undefined4 param_1,uint param_2)

{
  bool bVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;
  
  iVar2 = DAT_005573fc;
  iVar3 = _DAT_005571a4;
  *(undefined4 *)(DAT_005573fc + 0x3c) = 1;
  uVar5 = param_2 & 0xffff;
  if (uVar5 == 0) {
    uVar6 = 0;
  }
  else {
    uVar6 = uVar5 - 1;
  }
  if ((4 < *(uint *)(iVar3 + 0xc)) && (*(uint *)(iVar3 + 0xc) < uVar6 + 4)) {
    uVar6 = *(int *)(iVar3 + 0xc) - 4;
  }
  if (*(uint *)(iVar3 + 0xc) < 5) {
    uVar6 = 0;
  }
  if (*(uint *)(iVar2 + 0x2c) < uVar6) {
    bVar1 = true;
    uVar8 = uVar6;
    while( true ) {
      uVar7 = 0;
      if ((uVar6 + 4 <= uVar8) || (*(uint *)(iVar3 + 0xc) <= uVar8)) goto LAB_00556f9a;
      iVar4 = teleprompt_page_data_get(uVar8);
      if (iVar4 == 0) break;
      uVar8 = uVar8 + 1;
    }
    bVar1 = false;
    uVar7 = uVar8;
LAB_00556f9a:
    if (bVar1) {
      FUN_0058c882();
      *(uint *)(iVar2 + 0x34) = param_2 >> 0x10;
      *(uint *)(iVar2 + 0x30) = uVar5;
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(3,PTR_s_teleprompt_ui_00557448,PTR_s_D__01_workspace_s200_ap510b_iar__00557444,
                     PTR_s_teleprompt_ui_action_main_page_s_00557440,0x834,
                     PTR_s_switch_start_next____window_star_00557458,*(undefined4 *)(iVar2 + 0x2c),
                     uVar6,4,*(undefined4 *)(iVar2 + 0x30),*(undefined4 *)(iVar2 + 0x34));
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0xd400000,PTR_s__teleprompt_ui_switch_start_next_0055745c,
                            PTR_s__teleprompt_ui_switch_start_next_0055745c,
                            *(undefined4 *)(iVar2 + 0x2c),uVar6,4,*(undefined4 *)(iVar2 + 0x30),
                            *(undefined4 *)(iVar2 + 0x34));
      }
      *(uint *)(iVar2 + 0x2c) = uVar6;
      FUN_0055553c(iVar2,uVar6);
      teleprompt_page_data_set_window(uVar6);
      FUN_0043f66c(*(undefined4 *)(iVar2 + 0x18));
      FUN_0044ea04(*(undefined4 *)(iVar2 + 0x18),
                   (*(int *)(iVar2 + 0x30) - *(int *)(iVar2 + 0x2c)) * 0x118 +
                   *(int *)(iVar2 + 0x34) * 0x1c,0);
      *(undefined4 *)(iVar2 + 0x3c) = 0;
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(3,PTR_s_teleprompt_ui_00557448,PTR_s_D__01_workspace_s200_ap510b_iar__00557444,
                     PTR_s_teleprompt_ui_action_main_page_s_00557440,0x840,
                     PTR_s_switch_complete_next____window_s_00557460,*(undefined4 *)(iVar2 + 0x2c));
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0xc400000,PTR_s__teleprompt_ui_switch_complete_n_00557464,
                            PTR_s__teleprompt_ui_switch_complete_n_00557464,
                            *(undefined4 *)(iVar2 + 0x2c));
      }
    }
    else {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(2,PTR_s_teleprompt_ui_00557448,PTR_s_D__01_workspace_s200_ap510b_iar__00557444,
                     PTR_s_teleprompt_ui_action_main_page_s_00557440,0x829,
                     PTR_s_switch_next__target_window_page___00557450,uVar7);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x8400000,PTR_s__teleprompt_ui_switch_next__targ_00557454,
                            PTR_s__teleprompt_ui_switch_next__targ_00557454,uVar7);
      }
      FUN_0058c874(uVar7);
      teleprompt_page_data_set_window(uVar6);
      *(undefined4 *)(iVar2 + 0x3c) = 0;
    }
  }
  else {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(2,PTR_s_teleprompt_ui_00557448,PTR_s_D__01_workspace_s200_ap510b_iar__00557444,
                   PTR_s_teleprompt_ui_action_main_page_s_00557440,0x819,
                   PTR_s_switch_next__no_need_to_slide_fo_0055743c);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x8000000,PTR_s__teleprompt_ui_switch_next__no_n_0055744c);
    }
    *(undefined4 *)(iVar2 + 0x3c) = 0;
  }
  return 0;
}

