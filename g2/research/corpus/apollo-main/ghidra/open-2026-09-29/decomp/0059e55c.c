
longlong translate_ui_0059e55c(undefined4 param_1,undefined4 param_2,uint param_3)

{
  int iVar1;
  
  iVar1 = DAT_0059e5cc;
  if (*(int *)(DAT_0059e5cc + 8) == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      param_3 = 0x2a7;
      FUN_0043d574(2,DAT_0059e640,DAT_0059e63c,PTR_s_translate_ui_action_resume_0059e6c8,0x2a7,
                   PTR_s_gif_animation_is_NULL_or_invalid_0059e6c4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8000000,PTR_s__translate_ui_gif_animation_is_N_0059e6cc,
                          PTR_s__translate_ui_gif_animation_is_N_0059e6cc);
    }
  }
  else {
    FUN_0058c84e(*(undefined4 *)(DAT_0059e5cc + 8));
    FUN_0043dfa4(*(undefined4 *)(iVar1 + 8),1);
    iVar1 = FUN_0044dce2(*(undefined4 *)(iVar1 + 4),2);
    if (iVar1 != 0) {
      FUN_0044d7b8();
    }
  }
  return (ulonglong)param_3 << 0x20;
}

