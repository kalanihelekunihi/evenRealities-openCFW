
void translate_ui_0059da94
               (undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  iVar1 = FUN_0045a568();
  if (iVar1 == 1) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,DAT_0059defc,DAT_0059def8,PTR_s_translate_input_event_handler_0059e494,0x10d,
                   PTR_s_translate_input_event_handler__c_0059e554,
                   *(undefined1 *)(DAT_0059e5cc + 0x20),param_1,param_4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10800000,PTR_s__translate_ui_translate_input_ev_0059e558,
                          PTR_s__translate_ui_translate_input_ev_0059e558,
                          *(undefined1 *)(DAT_0059e5cc + 0x20),param_1);
    }
    if (*(char *)(DAT_0059e5cc + 0x20) == '\x01') {
      translate_ui_0059da28(param_1,param_2);
    }
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,DAT_0059defc,DAT_0059def8,PTR_s_translate_input_event_handler_0059e494,0x109,
                   PTR_s_translate_input_event_handler__b_0059e490);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10000000,PTR_s__translate_ui_translate_input_ev_0059e550);
    }
  }
  return;
}

