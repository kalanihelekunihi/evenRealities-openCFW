
undefined4 FUN_0058d228(undefined4 param_1,int *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  
  if (param_2 == (int *)0x0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(1,DAT_0058d2dc,DAT_0058d2d8,PTR_s_teleprompt_action_scroll_sync_0058d4e8,0x178,
                   PTR_s_scroll_sync_is_NULL_0058d4e4,param_3,param_4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__teleprompt_fsm_scroll_sync_is_N_0058d4ec);
    }
    uVar2 = 0xffffffff;
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(3,DAT_0058d2dc,DAT_0058d2d8,PTR_s_teleprompt_action_scroll_sync_0058d4e8,0x17c,
                   PTR_s_scroll_sync__page_id__d__line_id_0058d4f0,*param_2,param_2[1]);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0xc800000,PTR_s__teleprompt_fsm_scroll_sync__pag_0058d4f4,
                          PTR_s__teleprompt_fsm_scroll_sync__pag_0058d4f4,*param_2,param_2[1]);
    }
    FUN_00589b68(0x11,*param_2 * 10 + param_2[1]);
    uVar2 = 0;
  }
  return uVar2;
}

