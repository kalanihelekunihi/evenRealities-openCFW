
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

longlong FUN_00556134(undefined4 param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  
  if (param_2 == 0xaa) {
    FUN_0058a680(*(undefined4 *)(_DAT_00556260 + 4),0x38,1,0,0xaa,param_3,param_4);
    uVar4 = param_2;
  }
  else {
    uVar4 = param_2;
    iVar1 = FUN_0043d0ce(0);
    if (iVar1 << 0x1e < 0) {
      uVar4 = 0x60d;
      FUN_0043d574(3,PTR_s_teleprompt_ui_0055648c,PTR_s_D__01_workspace_s200_ap510b_iar__00556488,
                   PTR_s_teleprompt_ui_action_menu_scroll_00556c3c,0x60d,
                   PTR_s_menu_scroll_up__scroll_count___d_00556c38,param_2);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0xc400000,PTR_s__teleprompt_ui_menu_scroll_up__s_00556c40,
                          PTR_s__teleprompt_ui_menu_scroll_up__s_00556c40,param_2);
    }
    for (uVar3 = 0; iVar1 = _DAT_00556260, uVar3 < param_2; uVar3 = uVar3 + 1) {
      if (*(int *)(_DAT_00556260 + 0xc) < 1) {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          uVar4 = 0x612;
          FUN_0043d574(4,PTR_s_teleprompt_ui_0055648c,
                       PTR_s_D__01_workspace_s200_ap510b_iar__00556488,
                       PTR_s_teleprompt_ui_action_menu_scroll_00556c3c,0x612,
                       PTR_s_Reached_top_button_during_scroll_00556cb0,*(undefined4 *)(iVar1 + 0xc))
          ;
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0x10400000,PTR_s__teleprompt_ui_Reached_top_butto_00556cb4,
                              PTR_s__teleprompt_ui_Reached_top_butto_00556cb4,
                              *(undefined4 *)(iVar1 + 0xc));
        }
        break;
      }
      iVar2 = FUN_0044dce2(*(undefined4 *)(_DAT_00556260 + 4),*(int *)(_DAT_00556260 + 0xc) + -1);
      if (iVar2 == 0) {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          uVar4 = 0x61a;
          FUN_0043d574(2,PTR_s_teleprompt_ui_0055648c,
                       PTR_s_D__01_workspace_s200_ap510b_iar__00556488,
                       PTR_s_teleprompt_ui_action_menu_scroll_00556c3c,0x61a,
                       PTR_s_Failed_to_get_previous_button_at_00556cb8,*(int *)(iVar1 + 0xc) + -1);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0x8400000,PTR_s__teleprompt_ui_Failed_to_get_pre_00556ea0,
                              PTR_s__teleprompt_ui_Failed_to_get_pre_00556ea0,
                              *(int *)(iVar1 + 0xc) + -1);
        }
        break;
      }
      FUN_005896fc(*(undefined4 *)(iVar1 + 8),iVar2,200);
      *(int *)(iVar1 + 8) = iVar2;
      *(int *)(iVar1 + 0xc) = *(int *)(iVar1 + 0xc) + -1;
    }
  }
  return (ulonglong)uVar4 << 0x20;
}

