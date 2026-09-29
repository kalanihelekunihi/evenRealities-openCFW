
undefined8 FUN_004f0f26(undefined4 param_1,undefined4 param_2,undefined *param_3,undefined4 param_4)

{
  int *piVar1;
  int iVar2;
  undefined4 uStack_18;
  undefined *puStack_14;
  undefined4 uStack_10;
  
  uStack_18 = param_2;
  puStack_14 = param_3;
  uStack_10 = param_4;
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    uStack_10 = *DAT_004f19e8;
    puStack_14 = PTR_s_Scroll_animation_completed__show_004f19ec;
    uStack_18 = 0x294;
    FUN_0043d574(4,DAT_004f18a0,DAT_004f189c,PTR_s_widget_news_scroll_anim_ready_cb_004f19f0);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x10400000,PTR_s__dashborad_news_widget_Scroll_an_004f19f4,
                        PTR_s__dashborad_news_widget_Scroll_an_004f19f4,*DAT_004f19e8);
  }
  FUN_004f0e18(*DAT_004f19e8);
  *DAT_004f19f8 = 0;
  piVar1 = DAT_004f19fc;
  if ((*DAT_004f19fc != 0) && (iVar2 = ui_common_api_fn_00509dfa(*DAT_004f19fc), iVar2 == 0)) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      puStack_14 = DAT_004f1a00;
      uStack_18 = 0x298;
      FUN_0043d574(4,DAT_004f18a0,DAT_004f189c,PTR_s_widget_news_scroll_anim_ready_cb_004f19f0);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_004f1a04);
    }
    FUN_0043c0e4(&uStack_18,10,0);
    FUN_0043c0e4(&uStack_18,10,0);
    ui_common_api_fn_00509e14(*piVar1,&uStack_18,6);
    FUN_004f3440(&uStack_18,6);
  }
  return CONCAT44(puStack_14,uStack_18);
}

