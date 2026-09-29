
void FUN_004df858(int *param_1)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  if ((param_1 != (int *)0x0) && (*param_1 != 0)) {
    iVar1 = FUN_0043e2ea(*param_1);
    if (iVar1 == 0) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(2,PTR_s_common_text_container_004dfa0c,DAT_004dfa08,
                     PTR_s_common_text_update_scroll_state_004e02a0,0x184,
                     PTR_s_common_text_update_scroll_state__004e029c);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x8000000,PTR_s__common_text_container_common_te_004e02a4,
                            PTR_s__common_text_container_common_te_004e02a4);
      }
    }
    else {
      FUN_0043f66c(*param_1);
      iVar1 = FUN_0044e4aa(*param_1);
      iVar2 = FUN_0044e4bc(*param_1);
      iVar3 = FUN_0043fdda(*param_1);
      *(bool *)((int)param_1 + 0x12) = iVar3 < iVar2 + iVar1 + iVar3;
      param_1[3] = iVar2 + iVar1;
      iVar1 = FUN_0044e498(*param_1);
      *(bool *)(param_1 + 4) = iVar1 < 3;
      *(bool *)((int)param_1 + 0x11) = iVar2 < 3;
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(4,PTR_s_common_text_container_004dfa0c,DAT_004dfa08,
                     PTR_s_common_text_update_scroll_state_004e02a0,0x19f,
                     PTR_s_common_text_update_scroll_state__004e02a8,
                     *(undefined1 *)((int)param_1 + 0x12),param_1[3],(char)param_1[4],
                     *(undefined1 *)((int)param_1 + 0x11));
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x11000000,PTR_s__common_text_container_common_te_004e02ac,
                            PTR_s__common_text_container_common_te_004e02ac,
                            *(undefined1 *)((int)param_1 + 0x12),param_1[3],(char)param_1[4],
                            *(undefined1 *)((int)param_1 + 0x11));
      }
    }
  }
  return;
}

