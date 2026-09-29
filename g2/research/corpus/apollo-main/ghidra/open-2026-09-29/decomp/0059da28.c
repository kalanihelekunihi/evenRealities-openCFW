
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 translate_ui_0059da28(int param_1)

{
  undefined *puVar1;
  int iVar2;
  undefined4 unaff_r5;
  undefined *unaff_r6;
  
  if (*DAT_0059e5cc == 0) {
    iVar2 = FUN_0043d0ce();
    puVar1 = PTR_s_main_page_is_NULL_0059e488;
    if (iVar2 << 0x1e < 0) {
      unaff_r5 = 0xfb;
      FUN_0043d574(1,DAT_0059defc,DAT_0059def8,PTR_s_translate_ui_main_page_input_eve_0059e48c);
      unaff_r6 = puVar1;
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,_DAT_0059e5d0,_DAT_0059e5d0);
    }
  }
  else if (param_1 == 0x48) {
    system_close_page_factory_0046ae9c(1,5);
  }
  else if (param_1 == 10) {
    FUN_0059ec28(1,DAT_0059e5cc[9]);
  }
  return CONCAT44(unaff_r6,unaff_r5);
}

