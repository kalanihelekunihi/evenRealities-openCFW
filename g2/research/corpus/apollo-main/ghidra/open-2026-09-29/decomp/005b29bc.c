
longlong FUN_005b29bc(undefined4 param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  
  iVar1 = DAT_005b2d38;
  iVar2 = 0;
  if (param_2 != 0) {
    if ((*(int *)(DAT_005b2d38 + 0x7c) == 0) || (*(int *)(DAT_005b2d38 + 0x84) != 0)) {
      if (0 < *(int *)(DAT_005b2d38 + 0x84)) {
        iVar2 = FUN_0044dce2(*(undefined4 *)(DAT_005b2d38 + 100),*(int *)(DAT_005b2d38 + 0x84) + -1)
        ;
      }
    }
    else {
      iVar2 = *(int *)(DAT_005b2d38 + 0x7c);
    }
    if (iVar2 == 0) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        param_2 = 0xcb;
        FUN_0043d574(1,DAT_005b2d30,DAT_005b2d2c,PTR_s_conversate_ui_action_main_page_s_005b34d8,
                     0xcb,PTR_s_No_prev_button_found_005b34d4,param_4);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x4000000,PTR_s__conversate_ui_No_prev_button_fo_005b34dc);
      }
    }
    else {
      FUN_005b0edc(2,0,PTR_s_main_page_scroll_up_005b34e0);
      FUN_005896fc(*(undefined4 *)(iVar1 + 0x80),iVar2,200);
      *(int *)(iVar1 + 0x80) = iVar2;
      *(int *)(iVar1 + 0x84) = *(int *)(iVar1 + 0x84) + -1;
    }
  }
  return (ulonglong)param_2 << 0x20;
}

