
void FUN_004dfa2c(int param_1)

{
  int iVar1;
  int iVar2;
  undefined1 local_1c;
  undefined2 local_1b;
  undefined2 local_19;
  
  iVar2 = *(int *)(param_1 + 0x1c);
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(4,PTR_s_common_text_container_004dfff4,
                 PTR_s_D__01_workspace_s200_ap510b_iar__004dfff0,
                 PTR_s_common_text_scroll_anim_complete_004e02c0,0x1d1,
                 PTR_s_common_text_scroll_anim_complete_004e02bc);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10000000,PTR_s__common_text_container_common_te_004e02c4,
                        PTR_s__common_text_container_common_te_004e02c4);
  }
  *(undefined1 *)(iVar2 + 0x13) = 0;
  *(undefined4 *)(iVar2 + 0x14) = 0;
  FUN_004df858(iVar2);
  iVar1 = ui_common_api_fn_00509dfa(*(undefined4 *)(iVar2 + 0x18));
  if (iVar1 == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,PTR_s_common_text_container_004dfff4,
                   PTR_s_D__01_workspace_s200_ap510b_iar__004dfff0,
                   PTR_s_common_text_scroll_anim_complete_004e02c0,0x1dc,
                   PTR_s_common_text_scroll_anim_complete_004e02c8);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10000000,PTR_s__common_text_container_common_te_004e02cc);
    }
    iVar1 = ui_common_api_fn_00509e14(*(undefined4 *)(iVar2 + 0x18),&local_1c,5);
    if (iVar1 == 5) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(4,PTR_s_common_text_container_004dfff4,
                     PTR_s_D__01_workspace_s200_ap510b_iar__004dfff0,
                     PTR_s_common_text_scroll_anim_complete_004e02c0,0x1e2,
                     PTR_s_common_text_scroll_anim_complete_004e02d0,local_1c);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x10400000,PTR_s__common_text_container_common_te_004e02d4,
                            PTR_s__common_text_container_common_te_004e02d4,local_1c);
      }
      FUN_004e033c(iVar2,local_1c,local_1b,local_19);
    }
  }
  return;
}

