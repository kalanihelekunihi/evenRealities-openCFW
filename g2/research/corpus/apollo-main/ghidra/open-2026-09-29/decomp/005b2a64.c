
longlong FUN_005b2a64(undefined4 param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  
  iVar2 = DAT_005b2d38;
  uVar3 = param_2;
  iVar1 = FUN_005b0c18(0);
  if (param_2 != 0) {
    if (param_2 == 0xaa) {
      if (*(int *)(iVar2 + 0x7c) == 0) {
        FUN_0058a680(*(undefined4 *)(iVar2 + 100),0,0,0,uVar3,param_3);
      }
      else {
        FUN_0058a680(*(undefined4 *)(iVar2 + 100),0x28,0,0,uVar3,param_3);
      }
    }
    else if (*(int *)(iVar2 + 0x84) < iVar1 + -1) {
      iVar1 = FUN_0044dce2(*(undefined4 *)(iVar2 + 100),*(int *)(iVar2 + 0x84) + 1);
      if (iVar1 == 0) {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          uVar3 = 0xf3;
          FUN_0043d574(1,DAT_005b2d30,DAT_005b2d2c,PTR_s_conversate_ui_action_main_page_s_005b34e8,
                       0xf3,PTR_s_No_next_button_found_005b34f0,param_4);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0x4000000,PTR_s__conversate_ui_No_next_button_fo_005b34f4,
                              PTR_s__conversate_ui_No_next_button_fo_005b34f4);
        }
      }
      else {
        FUN_005b0edc(2,0,PTR_s_main_page_scroll_down_005b34f8);
        FUN_005896fc(*(undefined4 *)(iVar2 + 0x80),iVar1,200);
        *(int *)(iVar2 + 0x80) = iVar1;
        *(int *)(iVar2 + 0x84) = *(int *)(iVar2 + 0x84) + 1;
      }
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        uVar3 = 0xed;
        FUN_0043d574(4,DAT_005b2d30,DAT_005b2d2c,PTR_s_conversate_ui_action_main_page_s_005b34e8,
                     0xed,PTR_s_Reached_bottom_button_during_scr_005b34e4,
                     *(undefined4 *)(iVar2 + 0x84));
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x10400000,PTR_s__conversate_ui_Reached_bottom_bu_005b34ec,
                            PTR_s__conversate_ui_Reached_bottom_bu_005b34ec,
                            *(undefined4 *)(iVar2 + 0x84));
      }
    }
  }
  return (ulonglong)uVar3 << 0x20;
}

