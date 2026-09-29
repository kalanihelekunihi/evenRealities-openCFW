
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

longlong FUN_00556284(undefined4 param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  
  if (param_2 == 0xaa) {
    FUN_0058a680(*(undefined4 *)(_DAT_00556cbc + 4),0x38,0,0,0xaa,param_3,param_4);
    uVar4 = param_2;
  }
  else {
    uVar4 = param_2;
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      uVar4 = 0x635;
      FUN_0043d574(3,PTR_s_teleprompt_ui_0055648c,PTR_s_D__01_workspace_s200_ap510b_iar__00556488,
                   PTR_s_teleprompt_ui_action_menu_scroll_00556cc4,0x635,
                   PTR_s_menu_scroll_down__scroll_count____00556cc0,param_2);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0xc400000,PTR_s__teleprompt_ui_menu_scroll_down__00556cc8,
                          PTR_s__teleprompt_ui_menu_scroll_down__00556cc8,param_2);
    }
    iVar2 = 0;
    for (uVar3 = 0; uVar3 < param_2; uVar3 = uVar3 + 1) {
      iVar2 = FUN_00555710(iVar2);
      iVar1 = _DAT_00556cbc;
      if (iVar2 - 1U <= *(uint *)(_DAT_00556cbc + 0xc)) {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          uVar4 = 0x63c;
          FUN_0043d574(4,PTR_s_teleprompt_ui_0055648c,
                       PTR_s_D__01_workspace_s200_ap510b_iar__00556488,
                       PTR_s_teleprompt_ui_action_menu_scroll_00556cc4,0x63c,
                       PTR_s_Reached_bottom_button_during_scr_00556ccc,*(undefined4 *)(iVar1 + 0xc))
          ;
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0x10400000,PTR_s__teleprompt_ui_Reached_bottom_bu_00556cd0,
                              PTR_s__teleprompt_ui_Reached_bottom_bu_00556cd0,
                              *(undefined4 *)(iVar1 + 0xc));
        }
        break;
      }
      iVar2 = FUN_0044dce2(*(undefined4 *)(_DAT_00556cbc + 4),*(int *)(_DAT_00556cbc + 0xc) + 1);
      if (iVar2 == 0) {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          uVar4 = 0x644;
          FUN_0043d574(2,PTR_s_teleprompt_ui_0055648c,
                       PTR_s_D__01_workspace_s200_ap510b_iar__00556488,
                       PTR_s_teleprompt_ui_action_menu_scroll_00556cc4,0x644,
                       PTR_s_Failed_to_get_next_button_at_ind_00556cd4,*(int *)(iVar1 + 0xc) + 1);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0x8400000,PTR_s__teleprompt_ui_Failed_to_get_nex_00556ea4,
                              PTR_s__teleprompt_ui_Failed_to_get_nex_00556ea4,
                              *(int *)(iVar1 + 0xc) + 1);
        }
        break;
      }
      FUN_005896fc(*(undefined4 *)(iVar1 + 8),iVar2,200);
      *(int *)(iVar1 + 8) = iVar2;
      iVar2 = *(int *)(iVar1 + 0xc) + 1;
      *(int *)(iVar1 + 0xc) = iVar2;
    }
  }
  return (ulonglong)uVar4 << 0x20;
}

