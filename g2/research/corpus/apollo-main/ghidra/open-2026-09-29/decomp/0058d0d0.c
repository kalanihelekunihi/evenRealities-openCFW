
undefined4 FUN_0058d0d0(int param_1,int *param_2)

{
  char cVar1;
  int iVar2;
  undefined4 uVar3;
  
  if (param_2 == (int *)0x0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,DAT_0058d2dc,DAT_0058d2d8,PTR_s_teleprompt_action_ai_sync_0058d4c4,0x154,
                   PTR_s_ai_sync_is_NULL_0058d4c0);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__teleprompt_fsm_ai_sync_is_NULL_0058d4c8);
    }
    uVar3 = 0xffffffff;
  }
  else if (*(char *)(param_1 + 4) == '\0') {
    cVar1 = FUN_005540b2();
    if (cVar1 == '\x02') {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(3,DAT_0058d2dc,DAT_0058d2d8,PTR_s_teleprompt_action_ai_sync_0058d4c4,0x163,
                     PTR_s_ai_sync__page_id__d__line_id__d__0058d4dc,*param_2,param_2[1],param_2[2])
        ;
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0xcc00000,PTR_s__teleprompt_fsm_ai_sync__page_id_0058d4e0,
                            PTR_s__teleprompt_fsm_ai_sync__page_id_0058d4e0,*param_2,param_2[1],
                            param_2[2]);
      }
      FUN_00439be4(param_1 + 0x30,param_2,0xc);
      FUN_00589b68(0x10,*param_2 * 10 + param_2[1]);
      uVar3 = 0;
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(2,DAT_0058d2dc,DAT_0058d2d8,PTR_s_teleprompt_action_ai_sync_0058d4c4,0x15f,
                     PTR_s_current_ui_state_is_not_main__sk_0058d4d4);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x8000000,PTR_s__teleprompt_fsm_current_ui_state_0058d4d8,
                            PTR_s__teleprompt_fsm_current_ui_state_0058d4d8);
      }
      uVar3 = 0;
    }
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,DAT_0058d2dc,DAT_0058d2d8,PTR_s_teleprompt_action_ai_sync_0058d4c4,0x159,
                   PTR_s_mode_is_not_AI__skip_ai_sync_0058d4cc);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__teleprompt_fsm_mode_is_not_AI__s_0058d4d0,
                          PTR_s__teleprompt_fsm_mode_is_not_AI__s_0058d4d0);
    }
    uVar3 = 0;
  }
  return uVar3;
}

