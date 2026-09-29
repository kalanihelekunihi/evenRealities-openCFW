
undefined4
common_exit_prompt_show(int param_1,undefined4 param_2,undefined4 param_3,char param_4,int param_5)

{
  int *piVar1;
  int iVar2;
  undefined4 uVar3;
  
  if (param_1 == 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,PTR_s_exit_prompt_0058c0c4,PTR_s_D__01_workspace_s200_ap510b_iar__0058c0c0,
                   PTR_s_common_exit_prompt_show_0058c118,0x50,PTR_s_obj_is_not_valid_0058c114);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__exit_prompt_obj_is_not_valid_007600ef_1_0058c11c,
                          PTR_s__exit_prompt_obj_is_not_valid_007600ef_1_0058c11c);
    }
    uVar3 = 0xffffffff;
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      iVar2 = param_5;
      if (param_5 == 0) {
        iVar2 = 0x2ee;
      }
      FUN_0043d574(3,PTR_s_exit_prompt_0058c0c4,PTR_s_D__01_workspace_s200_ap510b_iar__0058c0c0,
                   PTR_s_common_exit_prompt_show_0058c118,0x54,
                   PTR_s_exit_prompt__text__s__app_id__u__0058c120,param_2,param_3,iVar2);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      iVar2 = param_5;
      if (param_5 == 0) {
        iVar2 = 0x2ee;
      }
      compress_log_output(0xcc00000,PTR_s__exit_prompt_exit_prompt__text___0058c124,
                          PTR_s__exit_prompt_exit_prompt__text___0058c124,param_2,param_3,iVar2);
    }
    FUN_00450500(param_1,0);
    piVar1 = DAT_0058c0dc;
    *DAT_0058c0dc = param_1;
    *DAT_0058c0e0 = param_2;
    *DAT_0058c0d8 = param_3;
    if (param_5 == 0) {
      *DAT_0058c0ec = 0x2ee;
    }
    else {
      *DAT_0058c0ec = param_5;
    }
    common_exit_prompt_check_foreground_app();
    if (param_4 == '\0') {
      common_exit_prompt_fade_cb_step1(0);
    }
    else {
      FUN_0058c426(*piVar1,0xfa,PTR_common_exit_prompt_fade_cb_step1_1_0058c128);
    }
    uVar3 = 0;
  }
  return uVar3;
}

