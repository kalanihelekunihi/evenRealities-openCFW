
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

longlong FUN_00556428(undefined4 param_1,undefined4 param_2)

{
  int iVar1;
  uint unaff_r5;
  
  if (*(int *)(_DAT_00556cbc + 0x18) == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      unaff_r5 = 0x66b;
      FUN_0043d574(1,PTR_s_teleprompt_ui_0055648c,PTR_s_D__01_workspace_s200_ap510b_iar__00556488,
                   PTR_s_teleprompt_ui_action_main_scroll_00556eb0,0x66b,
                   PTR_s_scroll_container_is_NULL_00556ea8);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,_DAT_005570fc,_DAT_005570fc);
    }
  }
  else {
    FUN_0044ea04(*(undefined4 *)(_DAT_00556cbc + 0x18),param_2,1);
  }
  return (ulonglong)unaff_r5 << 0x20;
}

