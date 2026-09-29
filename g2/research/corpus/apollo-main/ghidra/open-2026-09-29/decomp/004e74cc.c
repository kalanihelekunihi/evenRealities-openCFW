
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void even_ai_page_deinit(void)

{
  int *piVar1;
  
  FUN_004e1fa6();
  even_ai_deinit_text_stream_service();
  FUN_004e1fbe();
  *(undefined1 *)(DAT_004e74fc + 0x18) = 0;
  *_DAT_004e7594 = 0;
  piVar1 = _DAT_004e7530;
  if (*_DAT_004e7530 != 0) {
    ui_common_api_fn_00509c96(*_DAT_004e7530);
    *piVar1 = 0;
  }
  return;
}

