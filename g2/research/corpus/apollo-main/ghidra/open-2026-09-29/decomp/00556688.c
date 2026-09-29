
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_00556688(undefined4 param_1,uint param_2)

{
  char cVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  int iVar5;
  undefined4 uVar6;
  uint uVar7;
  undefined1 uVar8;
  uint uVar9;
  
  iVar2 = _DAT_00556cbc;
  if (*(int *)(_DAT_00556cbc + 0x18) == 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,PTR_s_teleprompt_ui_00556ec4,PTR_s_D__01_workspace_s200_ap510b_iar__00556ec0,
                   PTR_s_teleprompt_ui_action_scroll_sync_00557198,0x6af,
                   PTR_s_scroll_container_is_NULL_00556ea8);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,_DAT_005570fc);
    }
  }
  else if (*(int *)(_DAT_00556cac + 0xc) == 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(2,PTR_s_teleprompt_ui_00556ec4,PTR_s_D__01_workspace_s200_ap510b_iar__00556ec0,
                   PTR_s_teleprompt_ui_action_scroll_sync_00557198,0x6b4,
                   PTR_s_total_pages_is_0__skip_scroll_sy_0055719c);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x8000000,PTR_s__teleprompt_ui_total_pages_is_0__005571a0,
                          PTR_s__teleprompt_ui_total_pages_is_0__005571a0);
    }
  }
  else {
    uVar7 = param_2 / 10;
    param_2 = param_2 % 10;
    if (uVar7 < *(uint *)(_DAT_00556cac + 0xc)) {
      if (9 < param_2) {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(2,PTR_s_teleprompt_ui_00556ec4,
                       PTR_s_D__01_workspace_s200_ap510b_iar__00556ec0,
                       PTR_s_teleprompt_ui_action_scroll_sync_00557198,0x6bf,
                       PTR_s_scroll_sync_target_line_overflow_0055726c,param_2);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x8400000,PTR_s__teleprompt_ui_scroll_sync_targe_00557270,
                              PTR_s__teleprompt_ui_scroll_sync_targe_00557270,param_2);
        }
        param_2 = 9;
      }
      uVar9 = *(uint *)(iVar2 + 0x2c);
      if (((uVar7 < uVar9) || (uVar9 + 4 <= uVar7)) ||
         (iVar3 = FUN_005549e6(*(undefined4 *)(iVar2 + 0x18),uVar9,uVar7,param_2), iVar3 == 0)) {
        uVar8 = 0;
      }
      else {
        uVar8 = 1;
      }
      uVar4 = FUN_00554a16(*(undefined4 *)(iVar2 + 0x18),uVar9,uVar7,param_2);
      if (uVar4 != uVar9) {
        *(uint *)(iVar2 + 0x2c) = uVar4;
        FUN_0055553c(iVar2,*(undefined4 *)(iVar2 + 0x2c));
        FUN_0043f66c(*(undefined4 *)(iVar2 + 0x18));
      }
      iVar3 = teleprompt_page_data_get(uVar7);
      cVar1 = semantic_page_in_ensure_window(uVar7);
      if ((iVar3 == 0 || uVar4 != uVar9) || (cVar1 == '\0')) {
        if (cVar1 == '\0') {
          iVar5 = FUN_0043d0ce();
          if (iVar5 << 0x1e < 0) {
            FUN_0043d574(3,PTR_s_teleprompt_ui_00556ec4,
                         PTR_s_D__01_workspace_s200_ap510b_iar__00556ec0,
                         PTR_s_teleprompt_ui_action_scroll_sync_00557198,0x6db,
                         PTR_s_scroll_sync__page__u_outside_13__00557274,uVar7,
                         *(undefined4 *)(iVar2 + 0x2c));
          }
          iVar5 = FUN_0043d0ce();
          if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
            compress_log_output(0xc800000,PTR_s__teleprompt_ui_scroll_sync__page_00557278,
                                PTR_s__teleprompt_ui_scroll_sync__page_00557278,uVar7,
                                *(undefined4 *)(iVar2 + 0x2c));
          }
        }
        teleprompt_page_data_set_window(*(undefined4 *)(iVar2 + 0x2c));
      }
      if (iVar3 != 0) {
        FUN_0058c882();
      }
      else {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(2,PTR_s_teleprompt_ui_00556ec4,
                       PTR_s_D__01_workspace_s200_ap510b_iar__00556ec0,
                       PTR_s_teleprompt_ui_action_scroll_sync_00557198,0x6e1,
                       PTR_s_scroll_sync_target_page_not_read_0055727c,uVar7);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x8400000,PTR_s__teleprompt_ui_scroll_sync_targe_005573e8,
                              PTR_s__teleprompt_ui_scroll_sync_targe_005573e8,uVar7);
        }
        FUN_0058c874(uVar7);
      }
      uVar6 = FUN_00554a84(*(undefined4 *)(iVar2 + 0x18),uVar7,param_2,0);
      *(uint *)(iVar2 + 0x30) = uVar7;
      *(uint *)(iVar2 + 0x34) = param_2;
      *(undefined4 *)(iVar2 + 0x38) = uVar6;
      FUN_00554d58(*(undefined4 *)(iVar2 + 0x1c),*(undefined4 *)(iVar2 + 0x30),
                   *(undefined4 *)(iVar2 + 0x34));
      FUN_0044ea04(*(undefined4 *)(iVar2 + 0x18),uVar6,uVar8);
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(2,PTR_s_teleprompt_ui_00556ec4,PTR_s_D__01_workspace_s200_ap510b_iar__00556ec0,
                     PTR_s_teleprompt_ui_action_scroll_sync_00557198,0x6bb,
                     PTR_s_scroll_sync_target_page_invalid__00557264,uVar7);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x8400000,PTR_s__teleprompt_ui_scroll_sync_targe_00557268,
                            PTR_s__teleprompt_ui_scroll_sync_targe_00557268,uVar7);
      }
    }
  }
  return 0;
}

