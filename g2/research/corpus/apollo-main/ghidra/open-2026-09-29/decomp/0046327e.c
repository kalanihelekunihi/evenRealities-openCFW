
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_0046327e(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  int iVar2;
  int *piVar3;
  undefined4 *puVar4;
  undefined4 *puVar5;
  int *piVar6;
  undefined *puVar7;
  int iVar8;
  undefined4 uVar9;
  undefined4 uVar10;
  int iVar11;
  int iVar12;
  
  if (param_1 == 2) {
    iVar8 = FUN_0043d0ce();
    if (iVar8 << 0x1e < 0) {
      FUN_0043d574(4,PTR_s_menu_page_00463bc0,PTR_s_D__01_workspace_s200_ap510b_iar__00463bbc,
                   PTR_s_Menu_ui_event_handler_00463bb8,0x673,
                   PTR_s_menu_page_UI_EVENT_TYPE_INIT_00463bb4);
    }
    iVar8 = FUN_0043d0ce();
    if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
      compress_log_output(0x10000000,PTR_s__menu_page_menu_page_UI_EVENT_TY_00463bc4,
                          PTR_s__menu_page_menu_page_UI_EVENT_TY_00463bc4);
    }
    FUN_00460178();
    FUN_0046018e();
    if (*_DAT_00463bc8 == 0) {
      iVar8 = FUN_0043d0ce();
      if (iVar8 << 0x1e < 0) {
        FUN_0043d574(3,PTR_s_menu_page_00463bc0,PTR_s_D__01_workspace_s200_ap510b_iar__00463bbc,
                     PTR_s_Menu_ui_event_handler_00463bb8,0x677,_DAT_00463bcc);
      }
      iVar8 = FUN_0043d0ce();
      if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
        compress_log_output(0xc000000,_DAT_00463bd0,_DAT_00463bd0);
      }
      *_DAT_00463bd4 = 8;
      FUN_00439be4(_DAT_00463bdc,_DAT_00463bd8,0x1a0);
    }
    else {
      iVar8 = FUN_0043d0ce();
      if (iVar8 << 0x1e < 0) {
        FUN_0043d574(3,PTR_s_menu_page_00463bc0,PTR_s_D__01_workspace_s200_ap510b_iar__00463bbc,
                     PTR_s_Menu_ui_event_handler_00463bb8,0x67b,_DAT_00463be0);
      }
      iVar8 = FUN_0043d0ce();
      if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
        compress_log_output(0xc000000,_DAT_00463be4,_DAT_00463be4);
      }
      piVar1 = _DAT_00463be8;
      *_DAT_00463bd4 = *_DAT_00463be8;
      FUN_00439be4(_DAT_00463bdc,_DAT_00463bec,*piVar1 * 0x34);
    }
    FUN_004601ea();
    FUN_0044368e();
    iVar8 = 0;
    for (iVar12 = 0; iVar11 = _DAT_00463bdc, piVar1 = _DAT_00463bd4, iVar12 < *_DAT_00463bd4;
        iVar12 = iVar12 + 1) {
      if (*(char *)(iVar12 * 0x34 + _DAT_00463bdc + 0x28) == '\0') {
        uVar9 = FUN_00460084(iVar12 * 0x34 + _DAT_00463bdc + 4);
        iVar11 = FUN_0045fffe(iVar11 + iVar12 * 0x34 + 4,uVar9);
      }
      else {
        iVar11 = _DAT_00463bdc + iVar12 * 0x34 + 4;
      }
      uVar9 = FUN_0044a43c(iVar11);
      iVar11 = FUN_00489934(iVar11,uVar9,*_DAT_00463bf0,0);
      if (iVar8 < iVar11) {
        iVar8 = iVar11;
      }
    }
    iVar8 = iVar8 + 0x60;
    if (0x110 < iVar8) {
      iVar8 = 0x110;
    }
    if (iVar8 == 0xd3) {
      iVar8 = FUN_0043d0ce();
      if (iVar8 << 0x1e < 0) {
        FUN_0043d574(3,PTR_s_menu_page_00463bc0,PTR_s_D__01_workspace_s200_ap510b_iar__00463bbc,
                     PTR_s_Menu_ui_event_handler_00463bb8,0x6a2,_DAT_00463bf4);
      }
      iVar8 = FUN_0043d0ce();
      if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
        compress_log_output(0xc000000,_DAT_00463bf8,_DAT_00463bf8);
      }
      iVar8 = 0xd4;
    }
    puVar4 = _DAT_00463bfc;
    iVar11 = iVar8 + -0x60;
    uVar9 = FUN_0043de82(param_4);
    *puVar4 = uVar9;
    FUN_0043f506(*puVar4,iVar8);
    FUN_0043f568(*puVar4,0x120);
    FUN_0043f0e0(*puVar4,0);
    FUN_0043f142(*puVar4,0);
    FUN_0043ded4(*puVar4,0x50000);
    FUN_0043dfa4(*puVar4,0x2004);
    FUN_0044e368(*puVar4,0);
    uVar9 = FUN_0044104c(0);
    FUN_0044127e(*puVar4,uVar9,0);
    FUN_0044129e(*puVar4,0xff,0);
    uVar9 = FUN_0044104c(0);
    FUN_004412ec(*puVar4,uVar9,0);
    FUN_0044131c(*puVar4,0,0);
    func_0x00460128(*puVar4,0,0);
    puVar5 = _DAT_00463c00;
    uVar9 = FUN_0043de82(*puVar4);
    *puVar5 = uVar9;
    FUN_0043f506(*puVar5,iVar8 + -0x10);
    FUN_0043f568(*puVar5,0x120);
    iVar12 = FUN_0045a568();
    if (iVar12 == 1) {
      FUN_0043f0e0(*puVar5,0);
    }
    else {
      iVar12 = FUN_0045a568();
      if (iVar12 == 2) {
        FUN_0043f0e0(*puVar5,0x10);
      }
    }
    FUN_0043f142(*puVar5,0);
    FUN_0044e368(*puVar5,0);
    FUN_0043dfa4(*puVar5,0x10);
    FUN_0044129e(*puVar5,0,0);
    FUN_0044146a(*puVar5,6,0);
    uVar9 = FUN_0044104c(0xffffff);
    FUN_004412ec(*puVar5,uVar9,0);
    FUN_0044131c(*puVar5,1,0);
    FUN_0044130c(*puVar5,0xff,0);
    FUN_00441478(*puVar5,1,0);
    FUN_0044120e(*puVar5,0x13,0);
    FUN_0044121c(*puVar5,0x13,0);
    FUN_0044122a(*puVar5,0,0);
    FUN_00441238(*puVar5,0,0);
    piVar6 = _DAT_00463c04;
    iVar12 = FUN_0043de82(*puVar5);
    *piVar6 = iVar12;
    FUN_0043f506(*piVar6,iVar8 + -0x10);
    FUN_0043f568(*piVar6,0xfa);
    FUN_0043f09a(*piVar6,0,0);
    FUN_0044e3ca(*piVar6,0xc);
    FUN_0044e368(*piVar6,0);
    FUN_0044129e(*piVar6,0,0);
    FUN_0044131c(*piVar6,0,0);
    func_0x00460128(*piVar6,0,0);
    FUN_00441478(*piVar6,1,0);
    iVar12 = FUN_0043de82(*piVar6);
    *_DAT_00463c08 = iVar12;
    iVar12 = *(int *)PTR_DAT_00463c0c * *piVar1 + 0x1e;
    FUN_0043f506(*_DAT_00463c08,iVar8 + -0x10);
    FUN_0043f568(*_DAT_00463c08,iVar12);
    FUN_0043f0e0(*_DAT_00463c08,0);
    FUN_0043f142(*_DAT_00463c08,0);
    FUN_0044129e(*_DAT_00463c08,0,0);
    FUN_0044131c(*_DAT_00463c08,0,0);
    func_0x00460128(*_DAT_00463c08,0,0);
    FUN_0043dfa4(*_DAT_00463c08,0x10);
    FUN_00450500(*_DAT_00463c08,0);
    iVar8 = FUN_0043d0ce();
    if (iVar8 << 0x1e < 0) {
      FUN_0043d574(4,PTR_s_menu_page_00463bc0,PTR_s_D__01_workspace_s200_ap510b_iar__00463bbc,
                   PTR_s_Menu_ui_event_handler_00463bb8,0x6f0,
                   PTR_s_menu_content_container_initializ_00463c10,iVar12);
    }
    iVar8 = FUN_0043d0ce();
    if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
      compress_log_output(0x10400000,PTR_s__menu_page_menu_content_containe_00463c14,
                          PTR_s__menu_page_menu_content_containe_00463c14,iVar12);
    }
    iVar8 = FUN_0043d0ce();
    if (iVar8 << 0x1e < 0) {
      FUN_0043d574(4,PTR_s_menu_page_00463bc0,PTR_s_D__01_workspace_s200_ap510b_iar__00463bbc,
                   PTR_s_Menu_ui_event_handler_00463bb8,0x6f3,
                   PTR_s_Content_height_set_to___d_pixels_00463c18,iVar12,*piVar1,
                   *(undefined4 *)PTR_DAT_00463c0c);
    }
    iVar8 = FUN_0043d0ce();
    if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
      compress_log_output(0x10c00000,PTR_s__menu_page_Content_height_set_to_00463c1c,
                          PTR_s__menu_page_Content_height_set_to_00463c1c,iVar12,*piVar1,
                          *(undefined4 *)PTR_DAT_00463c0c);
    }
    for (iVar8 = 0; piVar3 = _DAT_00463c24, iVar2 = _DAT_00463c20, iVar8 < *piVar1;
        iVar8 = iVar8 + 1) {
      uVar9 = FUN_0043de82(*_DAT_00463c08);
      *(undefined4 *)(iVar2 + iVar8 * 4) = uVar9;
      func_0x00460128(*(undefined4 *)(iVar2 + iVar8 * 4),0,0);
      puVar7 = PTR_DAT_00463c0c;
      FUN_0043f4c0(*(undefined4 *)(iVar2 + iVar8 * 4),0x3fffffff,*(undefined4 *)PTR_DAT_00463c0c);
      FUN_0043f0e0(*(undefined4 *)(iVar2 + iVar8 * 4),10);
      FUN_0043f142(*(undefined4 *)(iVar2 + iVar8 * 4),*(int *)puVar7 * iVar8);
      uVar9 = FUN_0044104c(0);
      FUN_0044127e(*(undefined4 *)(iVar2 + iVar8 * 4),uVar9,0);
      FUN_0044129e(*(undefined4 *)(iVar2 + iVar8 * 4),0,0);
      FUN_0044131c(*(undefined4 *)(iVar2 + iVar8 * 4),0,0);
      FUN_0043dfa4(*(undefined4 *)(iVar2 + iVar8 * 4),0x10);
      uVar9 = *(undefined4 *)(iVar2 + iVar8 * 4);
      FUN_00462ea8(uVar9,iVar8);
      uVar9 = FUN_00499416(uVar9);
      FUN_0043f506(uVar9,iVar11);
      piVar3 = _DAT_00463bf0;
      FUN_0043f568(uVar9,*(undefined4 *)(*_DAT_00463bf0 + 0xc));
      FUN_0043f0e0(uVar9,0x34);
      FUN_0043f142(uVar9,10);
      iVar2 = _DAT_00463bdc;
      if (*(char *)(iVar8 * 0x34 + _DAT_00463bdc + 0x28) == '\0') {
        uVar10 = FUN_00460084(iVar8 * 0x34 + _DAT_00463bdc + 4);
        uVar10 = FUN_0045fffe(iVar2 + iVar8 * 0x34 + 4,uVar10);
        FUN_0049942e(uVar9,uVar10);
      }
      else {
        FUN_0049942e(uVar9,_DAT_00463bdc + iVar8 * 0x34 + 4);
      }
      FUN_00499678(uVar9,1);
      FUN_0044143e(uVar9,*piVar3,0);
      uVar10 = FUN_0044104c(_DAT_00463b90);
      FUN_0044140e(uVar9,uVar10,0);
    }
    *_DAT_00463c24 = 0;
    puVar5 = _DAT_00463c28;
    *_DAT_00463c28 = 0;
    FUN_0043f66c(*puVar4);
    uVar9 = FUN_00460d6c(*piVar3);
    iVar11 = FUN_0043d0ce();
    iVar8 = _DAT_00463bdc;
    if (iVar11 << 0x1e < 0) {
      uVar10 = FUN_00460084(*piVar3 * 0x34 + _DAT_00463bdc + 4);
      uVar10 = FUN_0045fffe(iVar8 + *piVar3 * 0x34 + 4,uVar10);
      FUN_0043d574(4,PTR_s_menu_page_00463bc0,PTR_s_D__01_workspace_s200_ap510b_iar__00463bbc,
                   PTR_s_Menu_ui_event_handler_00463bb8,0x720,
                   PTR_s_Initial_state__selected_index__d_00463c2c,*piVar3,uVar10,*puVar5,uVar9);
    }
    iVar8 = FUN_0043d0ce();
    if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
      iVar8 = _DAT_00463bdc;
      uVar10 = FUN_00460084(*piVar3 * 0x34 + _DAT_00463bdc + 4);
      uVar10 = FUN_0045fffe(iVar8 + *piVar3 * 0x34 + 4,uVar10);
      compress_log_output(0x11000000,PTR_s__menu_page_Initial_state__select_00463c30,
                          PTR_s__menu_page_Initial_state__select_00463c30,*piVar3,uVar10,*puVar5,
                          uVar9);
    }
    FUN_0044ea04(*piVar6,uVar9,0);
    FUN_00462db6();
    FUN_00462db4();
    iVar8 = FUN_0043d0ce();
    if (iVar8 << 0x1e < 0) {
      FUN_0043d574(4,PTR_s_menu_page_00463bc0,PTR_s_D__01_workspace_s200_ap510b_iar__00463bbc,
                   PTR_s_Menu_ui_event_handler_00463bb8,0x728,
                   PTR_s_Menu_initialization_complete__00463c34);
    }
    iVar8 = FUN_0043d0ce();
    if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
      compress_log_output(0x10000000,PTR_s__menu_page_Menu_initialization_c_00463c38,
                          PTR_s__menu_page_Menu_initialization_c_00463c38);
    }
    iVar8 = FUN_0043d0ce();
    if (iVar8 << 0x1e < 0) {
      FUN_0043d574(4,PTR_s_menu_page_00463bc0,PTR_s_D__01_workspace_s200_ap510b_iar__00463bbc,
                   PTR_s_Menu_ui_event_handler_00463bb8,0x729,
                   PTR_s___Container__225x260__Content_he_00463c3c,iVar12);
    }
    iVar8 = FUN_0043d0ce();
    if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
      compress_log_output(0x10400000,PTR_s__menu_page___Container__225x260__00463c40,
                          PTR_s__menu_page___Container__225x260__00463c40,iVar12);
    }
    iVar8 = FUN_0043d0ce();
    if (iVar8 << 0x1e < 0) {
      FUN_0043d574(4,PTR_s_menu_page_00463bc0,PTR_s_D__01_workspace_s200_ap510b_iar__00463bbc,
                   PTR_s_Menu_ui_event_handler_00463bb8,0x72a,
                   PTR_s___Items___d__Height___d_each_00463c44,*piVar1,
                   *(undefined4 *)PTR_DAT_00463c0c);
    }
    iVar8 = FUN_0043d0ce();
    if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
      compress_log_output(0x10800000,PTR_s__menu_page___Items___d__Height____00463c48,
                          PTR_s__menu_page___Items___d__Height____00463c48,*piVar1,
                          *(undefined4 *)PTR_DAT_00463c0c);
    }
    iVar8 = FUN_0043d0ce();
    if (iVar8 << 0x1e < 0) {
      FUN_0043d574(4,PTR_s_menu_page_00463bc0,PTR_s_D__01_workspace_s200_ap510b_iar__00463bbc,
                   PTR_s_Menu_ui_event_handler_00463bb8,0x72b,
                   PTR_s___Initial__selected__d__scroll_o_00463c4c,*piVar3,*puVar5);
    }
    iVar8 = FUN_0043d0ce();
    if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
      compress_log_output(0x10800000,PTR_s__menu_page___Initial__selected___00463c50,
                          PTR_s__menu_page___Initial__selected___00463c50,*piVar3,*puVar5);
    }
    *(undefined4 *)(_DAT_00463c54 + 4) = *puVar4;
  }
  else if (param_1 == 3) {
    FUN_0046302c(param_2,param_3);
  }
  else if ((param_1 != 4) && (param_1 == 5)) {
    iVar8 = FUN_0043d0ce();
    if (iVar8 << 0x1e < 0) {
      FUN_0043d574(4,PTR_s_menu_page_00463bc0,PTR_s_D__01_workspace_s200_ap510b_iar__00463bbc,
                   PTR_s_Menu_ui_event_handler_00463bb8,0x734,PTR_s_menu_DISPLAY_EXIT_00463c58);
    }
    iVar8 = FUN_0043d0ce();
    if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
      compress_log_output(0x10000000,PTR_s__menu_page_menu_DISPLAY_EXIT_00463c5c,
                          PTR_s__menu_page_menu_DISPLAY_EXIT_00463c5c);
    }
    *DAT_00463b94 = 0;
    piVar1 = _DAT_00463c08;
    if (*_DAT_00463c08 != 0) {
      FUN_00450500(*_DAT_00463c08,0);
      FUN_0043f142(*piVar1,0);
      iVar8 = FUN_0043d0ce();
      if (iVar8 << 0x1e < 0) {
        FUN_0043d574(4,PTR_s_menu_page_00463bc0,PTR_s_D__01_workspace_s200_ap510b_iar__00463bbc,
                     PTR_s_Menu_ui_event_handler_00463bb8,0x73b,
                     PTR_s_Reset_menu_content_container_Y_t_00463c60);
      }
      iVar8 = FUN_0043d0ce();
      if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
        compress_log_output(0x10000000,PTR_s__menu_page_Reset_menu_content_co_00463c64,
                            PTR_s__menu_page_Reset_menu_content_co_00463c64);
      }
    }
    piVar1 = _DAT_00463c04;
    if (*_DAT_00463c04 != 0) {
      FUN_00450500(*_DAT_00463c04,0);
      FUN_0043f142(*piVar1,0);
    }
    FUN_00460344();
    FUN_00460374();
  }
  return 0;
}

