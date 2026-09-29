
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_005476e4(void)

{
  undefined *puVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  undefined4 in_r3;
  
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    FUN_0043d574(4,PTR_s_navigation_ui_00547790,PTR_s_D__01_workspace_s200_ap510b_iar__0054778c,
                 PTR_s_navigation_ui_create_break_exit__00547ff8,0x4fb,
                 PTR_s_navigation_ui_create_break_exit__00547ff4,in_r3);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x10000000,PTR_s__navigation_ui_navigation_ui_cre_00547ffc,
                        PTR_s__navigation_ui_navigation_ui_cre_00547ffc);
  }
  uVar3 = FUN_00499416(*_DAT_00547798);
  FUN_0043f506(uVar3,0x3fffffff);
  FUN_0043f568(uVar3,0x3fffffff);
  FUN_0043f6ac(uVar3,9);
  puVar1 = PTR_s_ID_NAVIGATE_CONNECTION_TIME_OUT_00548000;
  uVar4 = FUN_00460084(PTR_s_ID_NAVIGATE_CONNECTION_TIME_OUT_00548000);
  uVar4 = FUN_0045fffe(puVar1,uVar4);
  FUN_0049942e(uVar3,uVar4);
  FUN_0044143e(uVar3,*_DAT_00547868,0);
  uVar4 = FUN_0044104c(0xffffff);
  FUN_0044140e(uVar3,uVar4,0);
  return;
}

