
undefined4 FUN_00548b98(void)

{
  int *piVar1;
  undefined4 *puVar2;
  undefined4 *puVar3;
  int iVar4;
  undefined4 uVar5;
  undefined4 uVar6;
  int iVar7;
  int iVar8;
  
  piVar1 = DAT_00548f38;
  if (*DAT_00548f38 != 0) {
    FUN_0044d878(*DAT_00548f38);
  }
  iVar4 = FUN_0043d0ce();
  if (iVar4 << 0x1e < 0) {
    FUN_0043d574(4,PTR_s_navigation_ui_005496f0,PTR_s_D__01_workspace_s200_ap510b_iar__005496ec,
                 PTR_s_navigation_ui_create_mode_list_p_005496e8,0x6a6,
                 PTR_s_Creating_mode_select_page_with_2_005496e4);
  }
  iVar4 = FUN_0043d0ce();
  if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
    compress_log_output(0x10000000,PTR_s__navigation_ui_Creating_mode_sel_005496f4,
                        PTR_s__navigation_ui_Creating_mode_sel_005496f4);
  }
  puVar2 = DAT_005496f8;
  uVar5 = FUN_0043de82(*piVar1);
  *puVar2 = uVar5;
  FUN_0043f506(*puVar2,500);
  FUN_0043f568(*puVar2,200);
  FUN_0043f0e0(*puVar2,0x28);
  FUN_0043f142(*puVar2,0x14);
  FUN_0044e368(*puVar2,0);
  FUN_0044e3ca(*puVar2,0xc);
  FUN_0044129e(*puVar2,0,0);
  FUN_0044146a(*puVar2,10,0);
  uVar5 = FUN_0044104c(0);
  FUN_004412ec(*puVar2,uVar5,0);
  FUN_0044131c(*puVar2,0,0);
  FUN_0044120e(*puVar2,0x10,0);
  FUN_0044121c(*puVar2,0x10,0);
  FUN_0044122a(*puVar2,0,0);
  FUN_00441238(*puVar2,0,0);
  puVar3 = DAT_005496fc;
  uVar5 = FUN_0043de82(*puVar2);
  *puVar3 = uVar5;
  FUN_0043f506(*puVar3,500);
  FUN_0043f568(*puVar3,0xd8);
  FUN_0043f0e0(*puVar3,0);
  FUN_0043f142(*puVar3,0);
  FUN_0044129e(*puVar3,0,0);
  FUN_0044131c(*puVar3,0,0);
  FUN_00545594(*puVar3,0,0);
  FUN_0043dfa4(*puVar3,0x10);
  FUN_00450500(*puVar3,0);
  iVar4 = FUN_0043d0ce();
  if (iVar4 << 0x1e < 0) {
    FUN_0043d574(4,PTR_s_navigation_ui_005496f0,PTR_s_D__01_workspace_s200_ap510b_iar__005496ec,
                 PTR_s_navigation_ui_create_mode_list_p_005496e8,0x6ce,DAT_00549700,0xd8);
  }
  iVar4 = FUN_0043d0ce();
  if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_00549704,DAT_00549704,0xd8);
  }
  for (iVar4 = 0; puVar2 = DAT_00549978, iVar4 < 2; iVar4 = iVar4 + 1) {
    uVar5 = FUN_0043de82(*puVar3);
    puVar2[iVar4] = uVar5;
    FUN_0044122a(puVar2[iVar4],0x14,0);
    FUN_00441238(puVar2[iVar4],0x14,0);
    FUN_0043f4c0(puVar2[iVar4],0x3fffffff,0x28);
    FUN_0043f0e0(puVar2[iVar4],0);
    uVar5 = FUN_0054dad8(iVar4,2);
    FUN_0043f142(puVar2[iVar4],uVar5);
    uVar5 = FUN_0044104c(0);
    FUN_0044127e(puVar2[iVar4],uVar5,0);
    FUN_0044129e(puVar2[iVar4],0,0);
    FUN_0044146a(puVar2[iVar4],10,0);
    if (iVar4 == 0) {
      FUN_0044131c(*puVar2,1,0);
      uVar5 = FUN_0044104c(0xffffff);
      FUN_004412ec(*puVar2,uVar5,0);
    }
    else {
      FUN_0044131c(puVar2[iVar4],0,0);
    }
    FUN_0043dfa4(puVar2[iVar4],0x10);
    uVar5 = FUN_00499416(puVar2[iVar4]);
    iVar8 = DAT_0054997c;
    uVar6 = FUN_00460084(*(undefined4 *)(DAT_0054997c + iVar4 * 4));
    uVar6 = FUN_0045fffe(*(undefined4 *)(iVar8 + iVar4 * 4),uVar6);
    FUN_0049942e(uVar5,uVar6);
    FUN_0044143e(uVar5,*DAT_00548f50,0);
    uVar6 = FUN_0044104c(DAT_00548f70);
    FUN_0044140e(uVar5,uVar6,0);
    FUN_004409fa(uVar5);
    iVar7 = FUN_0043d0ce();
    if (iVar7 << 0x1e < 0) {
      FUN_0043d574(4,PTR_s_navigation_ui_005496f0,PTR_s_D__01_workspace_s200_ap510b_iar__005496ec,
                   PTR_s_navigation_ui_create_mode_list_p_005496e8,0x6f3,DAT_00549980,iVar4,
                   *(undefined4 *)(iVar8 + iVar4 * 4));
    }
    iVar7 = FUN_0043d0ce();
    if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
      compress_log_output(0x10800000,DAT_00549984,DAT_00549984,iVar4,
                          *(undefined4 *)(iVar8 + iVar4 * 4));
    }
  }
  *DAT_00549988 = 0;
  *DAT_0054998c = 0;
  FUN_0043f66c(*piVar1);
  for (iVar4 = 0; puVar2 = DAT_00549978, iVar4 < 2; iVar4 = iVar4 + 1) {
    if (DAT_00549978[iVar4] != 0) {
      iVar8 = FUN_0043fd9e(DAT_00549978[iVar4]);
      FUN_0043f0e0(puVar2[iVar4],(500 - iVar8) / 2);
    }
  }
  FUN_0054db30();
  iVar4 = FUN_0043d0ce();
  if (iVar4 << 0x1e < 0) {
    FUN_0043d574(4,PTR_s_navigation_ui_005496f0,PTR_s_D__01_workspace_s200_ap510b_iar__005496ec,
                 PTR_s_navigation_ui_create_mode_list_p_005496e8,0x70a,DAT_00549990);
  }
  iVar4 = FUN_0043d0ce();
  if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
    compress_log_output(0x10000000,PTR_s__navigation_ui_Mode_select_page_i_00549b6c,
                        PTR_s__navigation_ui_Mode_select_page_i_00549b6c);
  }
  return 0;
}

