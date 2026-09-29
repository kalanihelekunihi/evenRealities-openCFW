
undefined8 FUN_004df9a2(int param_1,undefined4 param_2,undefined *param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  
  uVar2 = param_2;
  if ((param_1 == 0) || (iVar1 = FUN_0043e2ea(param_1), iVar1 == 0)) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      uVar2 = 0x1c7;
      param_3 = PTR_s_common_text_scroll_anim_exec_cb__004e02b0;
      FUN_0043d574(2,PTR_s_common_text_container_004dfff4,
                   PTR_s_D__01_workspace_s200_ap510b_iar__004dfff0,
                   PTR_s_common_text_scroll_anim_exec_cb_004e02b4,0x1c7,
                   PTR_s_common_text_scroll_anim_exec_cb__004e02b0,param_4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8000000,PTR_s__common_text_container_common_te_004e02b8,
                          PTR_s__common_text_container_common_te_004e02b8);
    }
  }
  else {
    FUN_0044ea04(param_1,param_2,0);
  }
  return CONCAT44(param_3,uVar2);
}

