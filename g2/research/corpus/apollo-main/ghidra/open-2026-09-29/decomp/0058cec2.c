
longlong FUN_0058cec2(void)

{
  int iVar1;
  uint unaff_r5;
  
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    unaff_r5 = 0xef;
    FUN_0043d574(4,DAT_0058d2dc,DAT_0058d2d8,PTR_s_teleprompt_action_app_resume_0058d48c,0xef,
                 PTR_s_teleprompt_action_resume_0058d488);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10000000,PTR_s__teleprompt_fsm_teleprompt_actio_0058d490,
                        PTR_s__teleprompt_fsm_teleprompt_actio_0058d490);
  }
  FUN_00589b68(8,0);
  return (ulonglong)unaff_r5 << 0x20;
}

