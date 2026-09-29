
longlong translate_ui_0059de88(undefined4 param_1,undefined4 param_2,uint param_3)

{
  undefined4 *puVar1;
  int iVar2;
  
  puVar1 = DAT_0059e268;
  FUN_0044d878(*DAT_0059e268);
  translate_ui_0059d850(*puVar1);
  puVar1 = DAT_0059df78;
  translate_ui_0059d6b6(*DAT_0059df78);
  translate_ui_0059d50c(*puVar1);
  translate_ui_0059d400(*puVar1);
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    param_3 = 0x1c2;
    FUN_0043d574(4,DAT_0059defc,DAT_0059def8,PTR_s_translate_ui_action_display_main_0059e62c,0x1c2,
                 PTR_s_Minimized_page_displayed_0059e628);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x10000000,PTR_s__translate_ui_Minimized_page_dis_0059e630,
                        PTR_s__translate_ui_Minimized_page_dis_0059e630);
  }
  return (ulonglong)param_3 << 0x20;
}

