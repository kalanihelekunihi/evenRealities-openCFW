
void FUN_004dfb78(int *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  int local_74;
  undefined *local_70;
  undefined *local_64;
  int *local_58;
  undefined *local_54;
  undefined4 local_44;
  undefined4 uStack_14;
  
  if ((param_1 != (int *)0x0) && (*param_1 != 0)) {
    uStack_14 = param_4;
    iVar1 = FUN_0043e2ea(*param_1);
    if (iVar1 == 0) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(2,PTR_s_common_text_container_004dfff4,
                     PTR_s_D__01_workspace_s200_ap510b_iar__004dfff0,
                     PTR_s_common_text_scroll_with_anim_004e02dc,0x1f2,
                     PTR_s_common_text_scroll_with_anim__sc_004e02d8);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x8000000,PTR_s__common_text_container_common_te_004e02e0,
                            PTR_s__common_text_container_common_te_004e02e0);
      }
    }
    else {
      param_1[5] = *param_1;
      *(undefined1 *)((int)param_1 + 0x13) = 1;
      FUN_004503d6(&local_74);
      local_74 = *param_1;
      uVar2 = FUN_0044e498(*param_1);
      FUN_004506ce(&local_74,uVar2,param_2);
      local_70 = PTR_FUN_004df9a2_1_004e02e4;
      local_54 = PTR_LAB_00450672_1_004e02e8;
      local_64 = PTR_FUN_004dfa2c_1_004e02ec;
      local_58 = param_1;
      local_44 = param_3;
      FUN_00450408(&local_74);
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        uVar2 = FUN_0044e498(*param_1);
        FUN_0043d574(4,PTR_s_common_text_container_004dfff4,
                     PTR_s_D__01_workspace_s200_ap510b_iar__004dfff0,
                     PTR_s_common_text_scroll_with_anim_004e02dc,0x206,
                     PTR_s_common_text_scroll_with_anim__St_004e02f0,uVar2,param_2,param_3);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        uVar2 = FUN_0044e498(*param_1);
        compress_log_output(0x10c00000,PTR_s__common_text_container_common_te_004e02f4,
                            PTR_s__common_text_container_common_te_004e02f4,uVar2,param_2,param_3);
      }
    }
  }
  return;
}

