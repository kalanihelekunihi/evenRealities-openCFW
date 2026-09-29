
undefined4 FUN_00557280(undefined4 param_1,uint param_2)

{
  undefined *puVar1;
  int iVar2;
  int iVar3;
  undefined4 uVar4;
  uint uVar5;
  uint uVar6;
  uint uVar7;
  
  iVar2 = DAT_005573fc;
  if (*(int *)(DAT_005573fc + 0x14) == 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(2,PTR_s_teleprompt_ui_00557448,PTR_s_D__01_workspace_s200_ap510b_iar__00557444,
                   PTR_s_teleprompt_ui_action_update_elap_00557490,0x88b,
                   PTR_s_title_bar_is_NULL_0055748c);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x8000000,PTR_s__teleprompt_ui_title_bar_is_NULL_00557494);
    }
  }
  else {
    iVar3 = FUN_0044dce2(*(undefined4 *)(DAT_005573fc + 0x14),0);
    puVar1 = PTR_s_ID_TELEPROMPT_ELAPSED_005574a0;
    if (iVar3 == 0) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(2,PTR_s_teleprompt_ui_00557448,PTR_s_D__01_workspace_s200_ap510b_iar__00557444,
                     PTR_s_teleprompt_ui_action_update_elap_00557490,0x892,
                     PTR_s_time_label_is_NULL_00557498);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x8000000,PTR_s__teleprompt_ui_time_label_is_NUL_0055749c,
                            PTR_s__teleprompt_ui_time_label_is_NUL_0055749c);
      }
    }
    else {
      uVar5 = param_2 / 0xe10;
      uVar6 = (param_2 % 0xe10) / 0x3c;
      uVar7 = param_2 % 0x3c;
      uVar4 = FUN_00460084(PTR_s_ID_TELEPROMPT_ELAPSED_005574a0);
      uVar4 = FUN_0045fffe(puVar1,uVar4);
      FUN_0049954c(iVar3,PTR_s__s__d__02d__02d_005574a4,uVar4,uVar5,uVar6,uVar7);
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        uVar4 = FUN_00460084(puVar1);
        uVar4 = FUN_0045fffe(puVar1,uVar4);
        FUN_0043d574(4,PTR_s_teleprompt_ui_00557448,PTR_s_D__01_workspace_s200_ap510b_iar__00557444,
                     PTR_s_teleprompt_ui_action_update_elap_00557490,0x8a1,
                     PTR_s_Updated_elapsed_time___s__d__02d_005574a8,uVar4,uVar5,uVar6,uVar7,
                     *(undefined4 *)(iVar2 + 0x24),param_2);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        uVar4 = FUN_00460084(puVar1);
        uVar4 = FUN_0045fffe(puVar1,uVar4);
        compress_log_output(0x11800000,PTR_s__teleprompt_ui_Updated_elapsed_t_005574ac,
                            PTR_s__teleprompt_ui_Updated_elapsed_t_005574ac,uVar4,uVar5,uVar6,uVar7,
                            *(undefined4 *)(iVar2 + 0x24),param_2);
      }
    }
  }
  return 0;
}

