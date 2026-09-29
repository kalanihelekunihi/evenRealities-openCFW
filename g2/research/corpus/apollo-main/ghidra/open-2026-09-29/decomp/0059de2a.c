
longlong translate_ui_0059de2a(void)

{
  int iVar1;
  uint unaff_r5;
  
  if (*(int *)(DAT_0059df78 + 8) == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      unaff_r5 = 0x1a5;
      FUN_0043d574(2,DAT_0059defc,DAT_0059def8,DAT_0059e620,0x1a5,DAT_0059e61c);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8000000,PTR_s__translate_ui_gif_animation_is_N_0059e624,
                          PTR_s__translate_ui_gif_animation_is_N_0059e624);
    }
  }
  else {
    FUN_0058c84e(*(undefined4 *)(DAT_0059df78 + 8));
  }
  return (ulonglong)unaff_r5 << 0x20;
}

