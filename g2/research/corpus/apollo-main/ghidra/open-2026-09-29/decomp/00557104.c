
undefined8 FUN_00557104(undefined4 param_1,int param_2,undefined4 param_3,undefined *param_4)

{
  int iVar1;
  int iVar2;
  undefined4 uStack_18;
  undefined4 uStack_14;
  
  iVar1 = FUN_0043e2ea(param_1);
  iVar2 = DAT_005573fc;
  uStack_18 = param_3;
  uStack_14 = param_4;
  if (iVar1 != 0) {
    iVar1 = FUN_0043e2ea(*(undefined4 *)(DAT_005573fc + 0x1c));
    if ((iVar1 != 0) && (iVar1 = FUN_0043e2ea(*(undefined4 *)(iVar2 + 0x14)), iVar1 != 0)) {
      FUN_0043f568(param_1,param_2);
      FUN_0043f568(*(undefined4 *)(iVar2 + 0x1c),param_2);
      FUN_00555200(0);
      FUN_0043f09a(*(undefined4 *)(iVar2 + 0x14),0,0xfc - param_2);
      goto LAB_0055718a;
    }
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    uStack_14 = PTR_s_obj_or_scroll_bar_or_title_bar_i_00557468;
    uStack_18 = 0x853;
    FUN_0043d574(2,PTR_s_teleprompt_ui_00557448,PTR_s_D__01_workspace_s200_ap510b_iar__00557444,
                 PTR_s_teleprompt_ui_height_anim_exec_c_0055746c);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x8000000,PTR_s__teleprompt_ui_obj_or_scroll_bar_00557470,
                        PTR_s__teleprompt_ui_obj_or_scroll_bar_00557470);
  }
LAB_0055718a:
  return CONCAT44(uStack_14,uStack_18);
}

