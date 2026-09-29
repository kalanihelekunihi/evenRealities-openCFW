
undefined4
FUN_0058cf50(undefined4 param_1,undefined2 *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  
  if (param_2 == (undefined2 *)0x0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(1,DAT_0058d2dc,DAT_0058d2d8,PTR_s_teleprompt_action_file_list_0058d4a0,0x10f,
                   PTR_s_file_list_is_NULL_0058d49c,param_3,param_4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__teleprompt_fsm_file_list_is_NUL_0058d4a4);
    }
    uVar2 = 0xffffffff;
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(3,DAT_0058d2dc,DAT_0058d2d8,PTR_s_teleprompt_action_file_list_0058d4a0,0x113,
                   PTR_s_file_count__d_0058d4a8,*param_2);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0xc400000,PTR_s__teleprompt_fsm_file_count__d_0058d4ac,
                          PTR_s__teleprompt_fsm_file_count__d_0058d4ac,*param_2);
    }
    teleprompt_file_list_update(param_2);
    FUN_00589b68(3,0);
    uVar2 = 0;
  }
  return uVar2;
}

