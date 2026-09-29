
undefined8 common_exit_prompt_fade_cb_step2(void)

{
  int iVar1;
  undefined4 unaff_r5;
  undefined *unaff_r6;
  
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    unaff_r5 = 0x36;
    unaff_r6 = PTR_s_step_2__hold__u_ms_then_fade_out_0058c0f0;
    FUN_0043d574(3,PTR_s_exit_prompt_0058c0c4,PTR_s_D__01_workspace_s200_ap510b_iar__0058c0c0,
                 PTR_s_common_exit_prompt_fade_cb_step2_0058c0f4,0x36,
                 PTR_s_step_2__hold__u_ms_then_fade_out_0058c0f0,*DAT_0058c0ec);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0xc400000,PTR_s__exit_prompt_step_2__hold__u_ms_t_0058c0f8,
                        PTR_s__exit_prompt_step_2__hold__u_ms_t_0058c0f8,*DAT_0058c0ec);
  }
  FUN_0058c516(*DAT_0058c0dc,0xfa,*DAT_0058c0ec,PTR_common_exit_prompt_fade_cb_step4_1_0058c0fc);
  return CONCAT44(unaff_r6,unaff_r5);
}

