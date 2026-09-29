
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

longlong FUN_0054c268(undefined4 param_1,undefined4 param_2,uint param_3)

{
  int iVar1;
  
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    param_3 = 0xb65;
    FUN_0043d574(4,PTR_s_navigation_ui_0054c5ac,PTR_s_D__01_workspace_s200_ap510b_iar__0054c5a8,
                 PTR_s_navigation_ui_exit_page_handler_0054cc98,0xb65,
                 PTR_s_navigation_ui_exit_page_handler_0054cc94);
  }
  iVar1 = FUN_0043d0ce();
  if (-1 < iVar1 << 0x1f) {
    iVar1 = FUN_0043d0ce();
    if (-1 < iVar1 << 0x1d) goto LAB_0054c2aa;
  }
  compress_log_output(0x10000000,PTR_s__navigation_ui_navigation_ui_exi_0054cc9c,
                      PTR_s__navigation_ui_navigation_ui_exi_0054cc9c);
LAB_0054c2aa:
  FUN_00545c5a();
  navigation_send_type_13_allocating();
  *DAT_0054cca0 = 0;
  if (*DAT_0054cca4 != 0) {
    FUN_00450500(*DAT_0054cca4,0);
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      param_3 = 0xb6d;
      FUN_0043d574(4,PTR_s_navigation_ui_0054c5ac,PTR_s_D__01_workspace_s200_ap510b_iar__0054c5a8,
                   PTR_s_navigation_ui_exit_page_handler_0054cc98,0xb6d,_DAT_0054cca8);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10000000,_DAT_0054ccac,_DAT_0054ccac);
    }
  }
  if (*DAT_0054ccb0 != 0) {
    FUN_00450500(*DAT_0054ccb0,0);
  }
  if (*_DAT_0054ccb4 != 0) {
    FUN_00450500(*_DAT_0054ccb4,0);
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      param_3 = 0xb75;
      FUN_0043d574(4,PTR_s_navigation_ui_0054c5ac,PTR_s_D__01_workspace_s200_ap510b_iar__0054c5a8,
                   PTR_s_navigation_ui_exit_page_handler_0054cc98,0xb75,_DAT_0054ccb8);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10000000,_DAT_0054ccbc,_DAT_0054ccbc);
    }
  }
  if (*_DAT_0054ccc0 != 0) {
    FUN_00450500(*_DAT_0054ccc0,0);
  }
  *_DAT_0054ccc4 = 0;
  *_DAT_0054ccc8 = 0;
  *DAT_0054cccc = 0;
  *_DAT_0054ccd0 = 0;
  FUN_0043c0e4(_DAT_0054c818,0x55c,0);
  *_DAT_0054c814 = 0;
  return (ulonglong)param_3 << 0x20;
}

