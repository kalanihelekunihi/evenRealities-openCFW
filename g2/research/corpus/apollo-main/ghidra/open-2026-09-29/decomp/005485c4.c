
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_005485c4(void)

{
  uint *puVar1;
  int *piVar2;
  undefined4 *puVar3;
  undefined4 *puVar4;
  undefined4 *puVar5;
  int iVar6;
  undefined4 uVar7;
  undefined4 uVar8;
  int iVar9;
  undefined *puVar10;
  undefined4 uVar11;
  undefined4 in_r3;
  uint uVar12;
  uint uVar13;
  undefined *apuStack_68 [15];
  undefined1 uStack_29;
  undefined4 uStack_28;
  
  uStack_28 = in_r3;
  if (*DAT_00548f38 != 0) {
    FUN_0044d878(*DAT_00548f38);
  }
  iVar6 = FUN_0043d0ce();
  if (iVar6 << 0x1e < 0) {
    FUN_0043d574(4,DAT_00548b50,DAT_00548b4c,PTR_s_navigation_ui_create_location_li_00548f44,0x604,
                 PTR_s_Creating_navigation_location_lis_00548f40,*_DAT_00548f3c);
  }
  iVar6 = FUN_0043d0ce();
  if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
    compress_log_output(0x10400000,PTR_s__navigation_ui_Creating_navigati_00548f48,
                        PTR_s__navigation_ui_Creating_navigati_00548f48,*_DAT_00548f3c);
  }
  uVar7 = FUN_00499416(*DAT_00548f38);
  puVar10 = PTR_s_ID_NAVIGATE_SELECT_00548f4c;
  uVar8 = FUN_00460084(PTR_s_ID_NAVIGATE_SELECT_00548f4c);
  uVar8 = FUN_0045fffe(puVar10,uVar8);
  FUN_0049942e(uVar7,uVar8);
  FUN_0044143e(uVar7,*DAT_00548f50,0);
  uVar8 = FUN_0044104c(0xffffff);
  FUN_0044140e(uVar7,uVar8,0);
  FUN_0043f0e0(uVar7,0);
  FUN_0043f142(uVar7,0);
  puVar3 = _DAT_00548f54;
  uVar7 = FUN_0043de82(*DAT_00548f38);
  *puVar3 = uVar7;
  FUN_0043f506(*puVar3,0x228);
  FUN_0043f568(*puVar3,200);
  FUN_0043f0e0(*puVar3,0);
  FUN_0043f142(*puVar3,0x3c);
  FUN_0044e368(*puVar3,0);
  FUN_0044e3ca(*puVar3,0xc);
  FUN_0044129e(*puVar3,0,0);
  FUN_0044146a(*puVar3,10,0);
  uVar7 = FUN_0044104c(0);
  FUN_004412ec(*puVar3,uVar7,0);
  FUN_0044131c(*puVar3,0,0);
  FUN_0044120e(*puVar3,0,0);
  FUN_0044121c(*puVar3,0,0);
  FUN_0044122a(*puVar3,0,0);
  FUN_00441238(*puVar3,0,0);
  puVar4 = _DAT_00548f58;
  puVar1 = _DAT_00548f3c;
  uVar13 = *_DAT_00548f3c;
  uVar7 = FUN_0043de82(*puVar3);
  *puVar4 = uVar7;
  if ((int)uVar13 < 5) {
    iVar6 = 0xd8;
  }
  else if (uVar13 == 5) {
    iVar6 = 0x10a;
  }
  else {
    iVar6 = uVar13 * 0x28 + 0x3c;
  }
  FUN_0043f506(*puVar4,0x228);
  FUN_0043f568(*puVar4,iVar6);
  FUN_0043f0e0(*puVar4,0);
  FUN_0043f142(*puVar4,0);
  FUN_0044129e(*puVar4,0,0);
  FUN_0044131c(*puVar4,0,0);
  FUN_00545594(*puVar4,0,0);
  FUN_0043dfa4(*puVar4,0x10);
  FUN_00450500(*puVar4,0);
  iVar9 = FUN_0043d0ce();
  if (iVar9 << 0x1e < 0) {
    apuStack_68[0] = PTR_s_normal_00548f60;
    if ((int)uVar13 < 5) {
      apuStack_68[0] = PTR_s_top_aligned_00548f5c;
    }
    FUN_0043d574(4,DAT_00548b50,DAT_00548b4c,PTR_s_navigation_ui_create_location_li_00548f44,0x646,
                 PTR_s_Navigation_content_height_set_to_00548f64,iVar6,uVar13);
  }
  iVar9 = FUN_0043d0ce();
  if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
    puVar10 = PTR_s_normal_00548f60;
    if ((int)uVar13 < 5) {
      puVar10 = PTR_s_top_aligned_00548f5c;
    }
    compress_log_output(0x10c00000,PTR_s__navigation_ui_Navigation_conten_00548f68,
                        PTR_s__navigation_ui_Navigation_conten_00548f68,iVar6,uVar13,puVar10);
  }
  osMutexAcquire(*_DAT_00548f6c,0xffffffff);
  for (uVar12 = 0; (puVar5 = _DAT_00549598, uVar12 < *puVar1 && ((int)uVar12 < 0x14));
      uVar12 = uVar12 + 1) {
    uVar7 = FUN_0043de82(*puVar4);
    puVar5[uVar12] = uVar7;
    FUN_0044122a(puVar5[uVar12],0xc,0);
    FUN_00441238(puVar5[uVar12],0xc,0);
    FUN_0043f4c0(puVar5[uVar12],0x3fffffff,0x28);
    FUN_0043f0e0(puVar5[uVar12],0);
    uVar7 = FUN_0054c3ec(uVar12,uVar13);
    FUN_0043f142(puVar5[uVar12],uVar7);
    uVar7 = FUN_0044104c(0);
    FUN_0044127e(puVar5[uVar12],uVar7,0);
    FUN_0044129e(puVar5[uVar12],0,0);
    FUN_0044146a(puVar5[uVar12],10,0);
    if (uVar12 == 0) {
      FUN_0044131c(*puVar5,1,0);
      uVar7 = FUN_0044104c(0xffffff);
      FUN_004412ec(*puVar5,uVar7,0);
    }
    else {
      FUN_0044131c(puVar5[uVar12],0,0);
    }
    FUN_0043dfa4(puVar5[uVar12],0x10);
    uVar7 = FUN_00498668(puVar5[uVar12]);
    if (puVar1[uVar12 + 0x142] == 1) {
      FUN_00498680(uVar7,_DAT_0054959c);
    }
    else if (puVar1[uVar12 + 0x142] == 2) {
      FUN_00498680(uVar7,_DAT_005495a0);
    }
    else {
      FUN_00498680(uVar7,PTR_DAT_00548f74);
    }
    FUN_0043f506(uVar7,0x18);
    FUN_0043f568(uVar7,0x18);
    FUN_0043f6b8(uVar7,7,0,0);
    uVar8 = FUN_00499416(puVar5[uVar12]);
    FUN_0043c0e4(apuStack_68,0x40,0);
    FUN_0043c0e4(apuStack_68,0x40,0);
    uVar11 = FUN_0044a43c((int)puVar1 + uVar12 * 0x40 + 6);
    FUN_0044b5a0(apuStack_68,(int)puVar1 + uVar12 * 0x40 + 6,uVar11);
    uStack_29 = 0;
    FUN_00499678(uVar8,1);
    FUN_00441180(uVar8,0x1ea,0);
    piVar2 = DAT_00548f50;
    FUN_0043f568(uVar8,*(undefined4 *)(*DAT_00548f50 + 0xc));
    FUN_0049942e(uVar8,apuStack_68);
    FUN_0044143e(uVar8,*piVar2,0);
    FUN_0043f6d6(uVar8,uVar7,0x14,8,0);
    if (uVar12 == 0) {
      FUN_004413ce(uVar7,0xff,0);
      uVar7 = FUN_0044104c(0xffffff);
      FUN_0044140e(uVar8,uVar7,0);
    }
    else {
      FUN_004413ce(uVar7,100,0);
      uVar7 = FUN_0044104c(DAT_00548f70);
      FUN_0044140e(uVar8,uVar7,0);
    }
    iVar6 = FUN_0043d0ce();
    if (iVar6 << 0x1e < 0) {
      FUN_0043d574(4,DAT_00548b50,DAT_00548b4c,PTR_s_navigation_ui_create_location_li_00548f44,0x684
                   ,PTR_s_Created_navigation_location_item_00548f78,uVar12,apuStack_68);
    }
    iVar6 = FUN_0043d0ce();
    if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
      compress_log_output(0x10800000,PTR_s__navigation_ui_Created_navigatio_00548f7c,
                          PTR_s__navigation_ui_Created_navigatio_00548f7c,uVar12,apuStack_68);
    }
  }
  osMutexRelease(*_DAT_00548f6c);
  puVar4 = _DAT_005495a4;
  *_DAT_005495a4 = 0;
  *_DAT_005496d0 = 0;
  FUN_0043f66c(*DAT_00548f38);
  uVar7 = FUN_0054cc00(*puVar4);
  iVar6 = FUN_0043d0ce();
  if (iVar6 << 0x1e < 0) {
    FUN_0043d574(4,DAT_00548b50,DAT_00548b4c,PTR_s_navigation_ui_create_location_li_00548f44,0x693,
                 PTR_s_Initial_navigation_selected_inde_005496d4,*puVar4,uVar7);
  }
  iVar6 = FUN_0043d0ce();
  if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
    compress_log_output(0x10800000,PTR_s__navigation_ui_Initial_navigatio_005496d8,
                        PTR_s__navigation_ui_Initial_navigatio_005496d8,*puVar4,uVar7);
  }
  FUN_0044ea04(*puVar3,uVar7,0);
  FUN_0054d9a4();
  iVar6 = FUN_0043d0ce();
  if (iVar6 << 0x1e < 0) {
    FUN_0043d574(4,DAT_00548b50,DAT_00548b4c,PTR_s_navigation_ui_create_location_li_00548f44,0x69a,
                 PTR_s_Navigation_location_list_page_in_005496dc,*puVar1);
  }
  iVar6 = FUN_0043d0ce();
  if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
    compress_log_output(0x10400000,PTR_s__navigation_ui_Navigation_locati_005496e0,
                        PTR_s__navigation_ui_Navigation_locati_005496e0,*puVar1);
  }
  return 0;
}

