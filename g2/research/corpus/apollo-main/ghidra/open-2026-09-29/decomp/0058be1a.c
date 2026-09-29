
undefined8 common_exit_prompt_fade_cb_step4(void)

{
  undefined *puVar1;
  int iVar2;
  undefined4 unaff_r5;
  undefined *unaff_r6;
  
  iVar2 = FUN_0043d0ce();
  puVar1 = PTR_s_step_4_0058c0cc;
  if (iVar2 << 0x1e < 0) {
    unaff_r5 = 0x28;
    FUN_0043d574(3,PTR_s_exit_prompt_0058c0c4,PTR_s_D__01_workspace_s200_ap510b_iar__0058c0c0,
                 PTR_s_common_exit_prompt_fade_cb_step4_0058c0d0);
    unaff_r6 = puVar1;
  }
  iVar2 = FUN_0043d0ce();
  if (-1 < iVar2 << 0x1f) {
    iVar2 = FUN_0043d0ce();
    if (-1 < iVar2 << 0x1d) goto LAB_0058be54;
  }
  compress_log_output(0xc000000,PTR_s__exit_prompt_step_4_0058c0d4,
                      PTR_s__exit_prompt_step_4_0058c0d4);
LAB_0058be54:
  iVar2 = FUN_0045a568();
  if (iVar2 == 1) {
    common_exit_prompt_check_foreground_app();
    FUN_00464c36(*DAT_0058c0d8 & 0xffff,0,0,0);
  }
  *DAT_0058c0dc = 0;
  *DAT_0058c0e0 = 0;
  *DAT_0058c0d8 = 0;
  iVar2 = FUN_0043d0ce();
  puVar1 = DAT_0058c0e4;
  if (iVar2 << 0x1e < 0) {
    unaff_r5 = 0x31;
    FUN_0043d574(3,PTR_s_exit_prompt_0058c0c4,PTR_s_D__01_workspace_s200_ap510b_iar__0058c0c0,
                 PTR_s_common_exit_prompt_fade_cb_step4_0058c0d0);
    unaff_r6 = puVar1;
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0xc000000,DAT_0058c0e8,DAT_0058c0e8);
  }
  return CONCAT44(unaff_r6,unaff_r5);
}

