
/* WARNING: Type propagation algorithm not settling */

void common_exit_prompt_check_foreground_app(void)

{
  int iVar1;
  uint local_c [2];
  
  iVar1 = FUN_0045a568();
  if (iVar1 == 1) {
    local_c[0] = 0;
    local_c[1] = 0;
    FUN_00443504(local_c + 1,local_c);
    if (local_c[0] != 0) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(3,PTR_s_exit_prompt_0058c0c4,PTR_s_D__01_workspace_s200_ap510b_iar__0058c0c0,
                     PTR_s_common_exit_prompt_check_foregro_0058c0bc,0x21,
                     PTR_s_foreground_app_exist__stop_foreg_0058c0b8,local_c[0]);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0xc400000,PTR_s__exit_prompt_foreground_app_exis_0058c0c8,
                            PTR_s__exit_prompt_foreground_app_exis_0058c0c8,local_c[0]);
      }
      FUN_00464c36(local_c[0] & 0xffff,0,0,0);
    }
  }
  return;
}

