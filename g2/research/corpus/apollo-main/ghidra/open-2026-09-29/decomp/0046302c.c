
longlong FUN_0046302c(char *param_1,uint param_2,undefined *param_3,uint param_4)

{
  char cVar1;
  byte bVar2;
  int iVar3;
  
  if (param_2 != 0) {
    if (*param_1 == '\0') {
      cVar1 = param_1[1];
      if (*DAT_00463b94 == '\0') {
        if (cVar1 == '\n') {
          FUN_00461620(2);
        }
        else if (cVar1 == 'D') {
          FUN_00461620(1);
        }
        else if (cVar1 == 'E') {
          FUN_00461620(0);
        }
        else if (cVar1 == 'F') {
          FUN_00462594(param_1[2]);
        }
        else if (cVar1 == 'H') {
          iVar3 = FUN_0045a568();
          if (iVar3 == 1) {
            FUN_00464c36(3,0,0,0);
          }
        }
        else {
          iVar3 = FUN_0043d0ce();
          if (iVar3 << 0x1e < 0) {
            param_2 = 0x629;
            FUN_0043d574(2,DAT_004631bc,DAT_004631b8,PTR_s_Menu_ReflashEventHandler_00463b9c,0x629,
                         PTR_s_unknown_menu_event_code___d_00463ba4,cVar1);
          }
          iVar3 = FUN_0043d0ce();
          if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
            compress_log_output(0x8400000,PTR_s__menu_page_unknown_menu_event_co_00463ba8,
                                PTR_s__menu_page_unknown_menu_event_co_00463ba8,cVar1);
          }
        }
      }
      else {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          param_2 = 0x60d;
          FUN_0043d574(3,DAT_004631bc,DAT_004631b8,PTR_s_Menu_ReflashEventHandler_00463b9c,0x60d,
                       PTR_s_menu_is_animating__push_event_to_00463b98,cVar1);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0xc400000,PTR_s__menu_page_menu_is_animating__pu_00463ba0,
                              PTR_s__menu_page_menu_is_animating__pu_00463ba0,cVar1);
        }
        FUN_00460242(param_1 + 1,5);
      }
    }
    else if ((*param_1 == '\x01') && (bVar2 = param_1[2], param_1[1] == -0x10)) {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        param_4 = (uint)bVar2;
        param_2 = 0x633;
        param_3 = PTR_s_MENU_INDEX_JUMP_EVENT__jump_to_t_00463bac;
        FUN_0043d574(4,DAT_004631bc,DAT_004631b8,PTR_s_Menu_ReflashEventHandler_00463b9c,0x633,
                     PTR_s_MENU_INDEX_JUMP_EVENT__jump_to_t_00463bac,param_4);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x10400000,PTR_s__menu_page_MENU_INDEX_JUMP_EVENT_00463bb0,
                            PTR_s__menu_page_MENU_INDEX_JUMP_EVENT_00463bb0,bVar2,param_2,param_3,
                            param_4);
      }
      FUN_00462a7c(bVar2);
    }
  }
  return (ulonglong)param_2 << 0x20;
}

