
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void even_ai_answer_text_reflash(void)

{
  int iVar1;
  undefined4 uVar2;
  undefined1 auStack_210 [516];
  
  iVar1 = _DAT_004e7504;
  if (*(short *)(_DAT_004e7504 + 0xe) == 0) {
    return;
  }
  FUN_0043c0e4(auStack_210,0x201,0);
  FUN_00439be4(auStack_210,iVar1 + 0x10,*(undefined2 *)(iVar1 + 0xe));
  if (*(char *)(iVar1 + 10) != '\0') {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(3,PTR_s_even_ai_ui_004e7514,PTR_s_D__01_workspace_s200_ap510b_iar__004e7510,
                   PTR_s_even_ai_answer_text_reflash_004e750c,0x7e8,_DAT_004e7524);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0xc000000,_DAT_004e7528,_DAT_004e7528);
    }
    FUN_004e1fa6();
    uVar2 = text_stream_pending_text(*_DAT_004e752c);
    iVar1 = even_ai_add_answer(uVar2,0,0xff,0,0);
    if (iVar1 != 0) {
      FUN_005537cc(0);
    }
    FUN_004e1fbe();
    even_ai_layout_refresh();
    return;
  }
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(3,PTR_s_even_ai_ui_004e7514,PTR_s_D__01_workspace_s200_ap510b_iar__004e7510,
                 PTR_s_even_ai_answer_text_reflash_004e750c,0x7d9,
                 PTR_s_Even_AI_REPLY__using_streaming_m_004e7508);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0xc000000,PTR_s__even_ai_ui_Even_AI_REPLY__using_004e7518,
                        PTR_s__even_ai_ui_Even_AI_REPLY__using_004e7518);
  }
  iVar1 = even_ai_add_answer(0x4e6c20,0,0xff,0,0);
  if (iVar1 != 0) {
    FUN_005537cc(3);
  }
  *_DAT_004e751c = *(undefined4 *)(DAT_004e74fc + 0x14);
  *_DAT_004e7520 = 0;
  even_ai_stream_init_from_service(0);
  even_ai_stream_on_auto_reflash();
  return;
}

