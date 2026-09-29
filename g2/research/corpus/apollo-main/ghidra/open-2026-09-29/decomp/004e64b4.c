
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void even_ai_gray_question(byte param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int *piVar2;
  int iVar3;
  
  iVar3 = _DAT_004e655c;
  if (param_1 < *(byte *)(_DAT_004e655c + 0x18)) {
    piVar2 = (int *)even_ai_dialog_get(param_1);
    if ((((piVar2 != (int *)0x0) && (*piVar2 != 0)) && (iVar3 = FUN_0043e2ea(*piVar2), iVar3 != 0))
       && ((char)piVar2[5] == '\0')) {
      *(undefined1 *)(piVar2 + 5) = 1;
    }
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(2,PTR_s_even_ai_ui_004e6a7c,PTR_s_D__01_workspace_s200_ap510b_iar__004e6a78,
                   PTR_s_even_ai_gray_question_004e6c40,0x62b,
                   PTR_s_dialog_index__d_>__dialog_count___004e6c38,param_1,
                   *(undefined1 *)(iVar3 + 0x18),param_4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8800000,PTR_s__even_ai_ui_dialog_index__d_>__d_004e6c3c,
                          PTR_s__even_ai_ui_dialog_index__d_>__d_004e6c3c,param_1,
                          *(undefined1 *)(iVar3 + 0x18));
    }
  }
  return;
}

