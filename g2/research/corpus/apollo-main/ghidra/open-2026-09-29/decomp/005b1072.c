
undefined8 FUN_005b1072(int param_1,uint param_2,undefined *param_3,undefined4 param_4)

{
  int iVar1;
  uint uVar2;
  
  uVar2 = param_2;
  if ((param_1 == 0) || (iVar1 = FUN_0043e2ea(param_1), iVar1 == 0)) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      uVar2 = 0x122;
      param_3 = PTR_s_Set_list_button_style_skipped__b_005b1a70;
      FUN_0043d574(2,DAT_005b15d0,DAT_005b15cc,PTR_s_conversate_ui_list_button_set_005b1a74,0x122,
                   PTR_s_Set_list_button_style_skipped__b_005b1a70,param_4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8000000,PTR_s__conversate_ui_Set_list_button_s_005b1a78);
    }
  }
  else if ((param_2 & 0xff) == 1) {
    FUN_005897ee(param_1);
    FUN_0044130c(param_1,0xff,0);
  }
  else if ((param_2 & 0xff) == 0) {
    FUN_00589892(param_1);
    FUN_0044130c(param_1,0,0);
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      uVar2 = 0x132;
      param_3 = PTR_s_Unknown_select_mode___d_005b1a7c;
      FUN_0043d574(2,DAT_005b15d0,DAT_005b15cc,PTR_s_conversate_ui_list_button_set_005b1a74,0x132,
                   PTR_s_Unknown_select_mode___d_005b1a7c,param_2 & 0xff);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8400000,PTR_s__conversate_ui_Unknown_select_mo_005b1a80,
                          PTR_s__conversate_ui_Unknown_select_mo_005b1a80,param_2 & 0xff);
    }
  }
  return CONCAT44(param_3,uVar2);
}

