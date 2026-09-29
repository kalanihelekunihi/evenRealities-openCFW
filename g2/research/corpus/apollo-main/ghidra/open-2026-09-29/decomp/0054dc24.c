
undefined8 FUN_0054dc24(undefined4 param_1,undefined *param_2,uint param_3,undefined4 param_4)

{
  undefined4 *puVar1;
  int iVar2;
  undefined4 local_18;
  undefined *local_14;
  uint local_10;
  undefined4 uStack_c;
  
  puVar1 = DAT_0054e5e4;
  local_10 = param_3;
  uStack_c = param_4;
  iVar2 = ui_common_api_fn_00509dfa(*DAT_0054e5e4);
  local_18 = param_1;
  local_14 = param_2;
  if (iVar2 == 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      local_14 = PTR_s_Mode_select_page__receive_event_f_0054e5e8;
      local_18 = 0xe45;
      FUN_0043d574(4,DAT_0054e448,DAT_0054e444,PTR_s_navigation_mode_select_page_anim_0054e5ec);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10000000,PTR_s__navigation_ui_Mode_select_page__0054e5f0,
                          PTR_s__navigation_ui_Mode_select_page__0054e5f0);
    }
    ui_common_api_fn_00509e14(*puVar1,&local_10,1);
    if ((local_10 & 0xff) == 10) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        local_14 = PTR_s_Mode_select_page__receive_clicke_0054e5f4;
        local_18 = 0xe4a;
        FUN_0043d574(4,DAT_0054e448,DAT_0054e444,PTR_s_navigation_mode_select_page_anim_0054e5ec);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x10000000,PTR_s__navigation_ui_Mode_select_page__0054e5f8);
      }
      FUN_0054e1a8(2);
    }
    else if ((local_10 & 0xff) == 0x44) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        local_14 = PTR_s_Mode_select_page__receive_scroll_0054e5fc;
        local_18 = 0xe4d;
        FUN_0043d574(4,DAT_0054e448,DAT_0054e444,PTR_s_navigation_mode_select_page_anim_0054e5ec);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x10000000,PTR_s__navigation_ui_Mode_select_page__0054e600,
                            PTR_s__navigation_ui_Mode_select_page__0054e600);
      }
      FUN_0054e1a8(1);
    }
    else if ((local_10 & 0xff) == 0x45) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        local_14 = PTR_s_Mode_select_page__receive_scroll_0054e604;
        local_18 = 0xe50;
        FUN_0043d574(4,DAT_0054e448,DAT_0054e444,PTR_s_navigation_mode_select_page_anim_0054e5ec);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x10000000,PTR_s__navigation_ui_Mode_select_page__0054e608,
                            PTR_s__navigation_ui_Mode_select_page__0054e608);
      }
      FUN_0054e1a8(0);
    }
  }
  return CONCAT44(local_14,local_18);
}

