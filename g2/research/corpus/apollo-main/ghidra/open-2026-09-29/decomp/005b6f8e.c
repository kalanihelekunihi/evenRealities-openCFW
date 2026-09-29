
undefined4 FUN_005b6f8e(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  iVar3 = DAT_005b7604;
  if (*(int *)(DAT_005b7604 + 0x28) != 0) {
    iVar1 = FUN_005b6a3a(param_2,0,param_3,param_4,param_1,param_2,param_3,param_4);
    FUN_0044e498(*(undefined4 *)(iVar3 + 0x24));
    iVar2 = FUN_005b6a3a();
    if (iVar2 == iVar1) {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(2,PTR_s_conversate_prep_005b7614,DAT_005b7610,
                     PTR_s_conversate_ui_action_prep_note_p_005b7640,0x11e,
                     PTR_s_prep_scroll_target_y__d_is_same_a_005b763c,iVar1);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x8400000,PTR_s__conversate_prep_prep_scroll_tar_005b7644,
                            PTR_s__conversate_prep_prep_scroll_tar_005b7644,iVar1);
      }
    }
    else {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        FUN_0043d574(3,PTR_s_conversate_prep_005b7614,DAT_005b7610,
                     PTR_s_conversate_ui_action_prep_note_p_005b7640,0x122,
                     PTR_s_prep_scroll_begin_y__d_target__d_005b7648,iVar2,iVar1);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0xc800000,PTR_s__conversate_prep_prep_scroll_beg_005b764c,
                            PTR_s__conversate_prep_prep_scroll_beg_005b764c,iVar2,iVar1);
      }
      FUN_0044ea04(*(undefined4 *)(iVar3 + 0x24),iVar1,1);
    }
  }
  return 0;
}

