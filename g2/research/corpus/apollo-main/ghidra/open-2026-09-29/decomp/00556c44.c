
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

longlong FUN_00556c44(void)

{
  int iVar1;
  uint unaff_r5;
  
  if (*(char *)(_DAT_005573f8 + 4) == '\0') {
    FUN_0044dce2(*(undefined4 *)(DAT_005573fc + 0x14),1);
    FUN_0058c84e();
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      unaff_r5 = 0x7c0;
      FUN_0043d574(2,PTR_s_teleprompt_ui_00556ec4,PTR_s_D__01_workspace_s200_ap510b_iar__00556ec0,
                   PTR_s_teleprompt_ui_action_gif_complet_00557410,0x7c0,
                   PTR_s_GIF_animation_complete__but_mode_0055740c);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8000000,PTR_s__teleprompt_ui_GIF_animation_com_00557414,
                          PTR_s__teleprompt_ui_GIF_animation_com_00557414);
    }
  }
  return (ulonglong)unaff_r5 << 0x20;
}

