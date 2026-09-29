
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_004e93e4(undefined4 param_1)

{
  undefined4 *puVar1;
  int *piVar2;
  undefined4 *puVar3;
  uint *puVar4;
  undefined4 *puVar5;
  uint *puVar6;
  undefined4 *puVar7;
  uint *puVar8;
  byte bVar9;
  int iVar10;
  undefined4 uVar11;
  int iVar12;
  uint uVar13;
  uint uStack_a0;
  undefined *puStack_9c;
  uint uStack_98;
  uint uStack_94;
  int iStack_90;
  undefined4 uStack_8c;
  undefined4 uStack_88;
  undefined4 uStack_84;
  undefined *puStack_80;
  undefined *puStack_74;
  undefined *puStack_64;
  undefined4 uStack_54;
  
  piVar2 = _DAT_004e9d40;
  if (*_DAT_004e9d40 == 0) {
    iVar10 = ui_common_api_fn_00509c1c();
    *piVar2 = iVar10;
  }
  *DAT_004e9d3c = 0;
  puVar3 = _DAT_004e9d44;
  uVar11 = FUN_0043de82(param_1);
  *puVar3 = uVar11;
  FUN_0043dfa4(*puVar3,0x10);
  FUN_0043f506(*puVar3,0x240);
  FUN_0043f568(*puVar3,0x120);
  FUN_0043f09a(*puVar3,0,0);
  FUN_0043dfa4(*puVar3,0x10);
  uVar11 = FUN_0044104c(0);
  FUN_0044127e(*puVar3,uVar11,0);
  FUN_0044129e(*puVar3,0xff,0);
  uVar11 = FUN_0044104c(0xffffff);
  FUN_0044140e(*puVar3,uVar11,0);
  FUN_0044142e(*puVar3,0xff,0);
  uVar11 = FUN_0044104c(0);
  FUN_004412ec(*puVar3,uVar11,0);
  FUN_0044131c(*puVar3,0,0);
  FUN_0044133a(*puVar3,0,0);
  FUN_00441378(*puVar3,0,0);
  FUN_00441386(*puVar3,0,0);
  FUN_004413b0(*puVar3,0,0);
  FUN_00441394(*puVar3,0,0);
  FUN_004413a2(*puVar3,0,0);
  FUN_0044146a(*puVar3,0,0);
  func_0x004e75b0(*puVar3,0,0);
  FUN_0044120e(*puVar3,0,0);
  FUN_0044121c(*puVar3,0,0);
  FUN_0044122a(*puVar3,0,0);
  FUN_00441238(*puVar3,0,0);
  puVar1 = _DAT_004e9d48;
  uVar11 = FUN_0043de82(*puVar3);
  *puVar1 = uVar11;
  FUN_0043dfa4(*puVar1,0x10);
  FUN_0043f506(*puVar1,0x240);
  FUN_0043f568(*puVar1,0x120);
  ui_common_api_fn_00509f7a(&uStack_88,&uStack_8c);
  FUN_0043f09a(*puVar1,uStack_88,uStack_8c);
  uVar11 = FUN_0044104c(0);
  FUN_0044127e(*puVar1,uVar11,0);
  FUN_0044129e(*puVar1,0,0);
  FUN_0044131c(*puVar1,0,0);
  FUN_0044133a(*puVar1,0,0);
  FUN_00441378(*puVar1,0,0);
  FUN_00441386(*puVar1,0,0);
  FUN_004413b0(*puVar1,0,0);
  FUN_00441394(*puVar1,0,0);
  FUN_004413a2(*puVar1,0,0);
  func_0x004e75b0(*puVar1,0,0);
  FUN_0044120e(*puVar1,0,0);
  FUN_0044121c(*puVar1,0,0);
  FUN_0044122a(*puVar1,0,0);
  FUN_00441238(*puVar1,0,0);
  FUN_0044146a(*puVar1,0,0);
  uVar11 = FUN_0044104c(0);
  FUN_004412ec(*puVar1,uVar11,0);
  uVar11 = FUN_0044104c(0xffffff);
  FUN_0044140e(*puVar1,uVar11,0);
  FUN_0044142e(*puVar1,0xff,0);
  FUN_00502174();
  iStack_90 = FUN_00558142();
  func_0x004e75e2(iStack_90);
  if ((*_DAT_004e9d4c != 0) && (iVar10 = FUN_00558314(iStack_90,_DAT_004e9d50), iVar10 == 0)) {
    iVar10 = FUN_0043d0ce();
    if (iVar10 << 0x1e < 0) {
      uStack_98 = *_DAT_004e9d54;
      puStack_9c = PTR_s_dashboard_layout_changed__reset_l_004e9d58;
      uStack_a0 = 0x6bf;
      FUN_0043d574(3,PTR_s_dashborad_ui_004e9d64,PTR_s_D__01_workspace_s200_ap510b_iar__004e9d60,
                   PTR_s_ui_Screen1_screen_init_004e9d5c);
    }
    iVar10 = FUN_0043d0ce();
    if ((iVar10 << 0x1f < 0) || (iVar10 = FUN_0043d0ce(), iVar10 << 0x1d < 0)) {
      compress_log_output(0xc400000,PTR_s__dashborad_ui_dashboard_layout_c_004e9d68,
                          PTR_s__dashborad_ui_dashboard_layout_c_004e9d68,*_DAT_004e9d54);
    }
    *_DAT_004e9d54 = 0;
  }
  puVar4 = _DAT_004e9d54;
  if ((int)(uint)*(byte *)(iStack_90 + 1) <= (int)*_DAT_004e9d54) {
    *_DAT_004e9d54 = 0;
  }
  puVar5 = _DAT_004e9d6c;
  iVar10 = dashboard_watchface_manager_init(*puVar1,*_DAT_004e9d6c);
  if (iVar10 != 0) {
    iVar10 = FUN_0043d0ce();
    if (iVar10 << 0x1e < 0) {
      puStack_9c = _DAT_004e9d70;
      uStack_a0 = 0x6cc;
      FUN_0043d574(1,PTR_s_dashborad_ui_004e9d64,PTR_s_D__01_workspace_s200_ap510b_iar__004e9d60,
                   PTR_s_ui_Screen1_screen_init_004e9d5c);
    }
    iVar10 = FUN_0043d0ce();
    if ((iVar10 << 0x1f < 0) || (iVar10 = FUN_0043d0ce(), iVar10 << 0x1d < 0)) {
      compress_log_output(0x4000000,_DAT_004e9d74,_DAT_004e9d74);
    }
  }
  puVar6 = _DAT_004e9d78;
  *_DAT_004e9d78 = (uint)*(byte *)(iStack_90 + 1);
  puVar7 = _DAT_004e9d7c;
  FUN_0043c0e4(_DAT_004e9d7c,0x18,0);
  if ((int)*puVar6 < 2) {
    iVar10 = FUN_0043d0ce();
    if (iVar10 << 0x1e < 0) {
      uStack_98 = *puVar6;
      puStack_9c = PTR_s_Dashboard_init__widget_count__d__004e9d8c;
      uStack_a0 = 0x70a;
      FUN_0043d574(3,PTR_s_dashborad_ui_004e9d64,PTR_s_D__01_workspace_s200_ap510b_iar__004e9d60,
                   PTR_s_ui_Screen1_screen_init_004e9d5c);
    }
    iVar10 = FUN_0043d0ce();
    if ((iVar10 << 0x1f < 0) || (iVar10 = FUN_0043d0ce(), iVar10 << 0x1d < 0)) {
      compress_log_output(0xc400000,PTR_s__dashborad_ui_Dashboard_init__wi_004e9d90,
                          PTR_s__dashborad_ui_Dashboard_init__wi_004e9d90,*puVar6);
    }
  }
  else {
    for (iVar10 = 0; iVar10 < (int)*puVar6; iVar10 = iVar10 + 1) {
      uVar11 = FUN_0043de82(*puVar1);
      puVar7[iVar10] = uVar11;
      FUN_0043f4c0(puVar7[iVar10],*(undefined4 *)PTR_DAT_004e9d84,*(undefined4 *)PTR_DAT_004e9d84);
      FUN_0044131c(puVar7[iVar10],0,0);
      FUN_0044146a(puVar7[iVar10],0,0);
      FUN_0044130c(puVar7[iVar10],0,0);
      uVar13 = *puVar6;
      iVar12 = *(int *)PTR_DAT_004e9d88;
      FUN_0043f6ac(puVar7[iVar10],7);
      FUN_0043f09a(puVar7[iVar10],puVar5[3],(int)(iVar12 * ((iVar10 * 2 - uVar13) + 1)) / 2);
      if (iVar10 == 0) {
        uVar11 = FUN_0044104c(0xffffff);
        FUN_0044127e(*puVar7,uVar11,0);
        FUN_0044129e(*puVar7,0xff,0);
      }
      else {
        uVar11 = FUN_0044104c(_DAT_004e9d80);
        FUN_0044127e(puVar7[iVar10],uVar11,0);
        FUN_0044129e(puVar7[iVar10],0x96,0);
      }
      FUN_0043dfa4(puVar7[iVar10],2);
    }
  }
  *_DAT_004e9d94 = 0;
  piVar2 = _DAT_004e9d98;
  *_DAT_004e9d98 = 0;
  puVar1 = DAT_004e9d30;
  *DAT_004e9d30 = 0;
  if (puVar5[5] != 0) {
    iVar10 = FUN_0050fef8(*puVar3);
    *piVar2 = iVar10;
    uVar11 = FUN_0044104c(0);
    FUN_0044127e(*piVar2,uVar11,0);
    FUN_0043f4c0(*piVar2,0x160,0x130);
    ui_common_api_fn_00509f7a(&puStack_9c,&uStack_a0);
    FUN_0043f09a(*piVar2,puVar5[1],uStack_a0);
    FUN_0044e368(*piVar2,0);
    FUN_0044131c(*piVar2,0,0);
    FUN_0044146a(*piVar2,0,0);
    func_0x004e75b0(*piVar2,0,0);
    FUN_0043f66c(*piVar2);
    FUN_004e9280();
    for (uVar13 = 0; iVar10 = _DAT_004e9cfc, (int)uVar13 < (int)*puVar6; uVar13 = uVar13 + 1) {
      uVar11 = FUN_0050ff0e(*piVar2,0,uVar13 & 0xff,0xc);
      *(undefined4 *)(iVar10 + uVar13 * 8) = uVar11;
      func_0x004e75b0(*(undefined4 *)(iVar10 + uVar13 * 8),0,0);
      uVar11 = FUN_0043de82(*(undefined4 *)(iVar10 + uVar13 * 8));
      *(undefined4 *)(iVar10 + uVar13 * 8 + 4) = uVar11;
      FUN_0043f4c0(*(undefined4 *)(iVar10 + uVar13 * 8 + 4),0x160,0x120);
      uStack_a0 = 0;
      FUN_0043f6d6(*(undefined4 *)(iVar10 + uVar13 * 8 + 4),*(undefined4 *)(iVar10 + uVar13 * 8),1,0
                  );
      FUN_0044129e(*(undefined4 *)(iVar10 + uVar13 * 8 + 4),0,0);
      FUN_0044131c(*(undefined4 *)(iVar10 + uVar13 * 8 + 4),1,0);
      uVar11 = FUN_0044104c(0xffffff);
      FUN_004412ec(*(undefined4 *)(iVar10 + uVar13 * 8 + 4),uVar11,0);
      FUN_0044146a(*(undefined4 *)(iVar10 + uVar13 * 8 + 4),6,0);
      FUN_0044130c(*(undefined4 *)(iVar10 + uVar13 * 8 + 4),0xff,0);
      func_0x004e75b0(*(undefined4 *)(iVar10 + uVar13 * 8 + 4),0,0);
      FUN_0043dfa4(*(undefined4 *)(iVar10 + uVar13 * 8 + 4),2);
    }
    FUN_0043f66c(*piVar2);
    for (uVar13 = 0; (int)uVar13 < (int)*puVar6; uVar13 = uVar13 + 1) {
      bVar9 = *(byte *)(iStack_90 + uVar13 + 2);
      if (bVar9 == 0) {
        FUN_004f091c(uVar13);
      }
      else if (bVar9 == 2) {
        FUN_004edac4(uVar13);
      }
      else if (bVar9 < 2) {
        FUN_004ec2dc(uVar13);
      }
      else if (bVar9 == 4) {
        FUN_004f891c(uVar13);
      }
      else if (bVar9 < 4) {
        FUN_004fb760(uVar13);
      }
      else {
        iVar10 = FUN_0043d0ce();
        if (iVar10 << 0x1e < 0) {
          uStack_98 = (uint)*(byte *)(iStack_90 + uVar13 + 2);
          puStack_9c = _DAT_004e9d9c;
          uStack_a0 = 0x74a;
          uStack_94 = uVar13;
          FUN_0043d574(2,PTR_s_dashborad_ui_004e9d64,PTR_s_D__01_workspace_s200_ap510b_iar__004e9d60
                       ,PTR_s_ui_Screen1_screen_init_004e9d5c);
        }
        iVar10 = FUN_0043d0ce();
        if ((iVar10 << 0x1f < 0) || (iVar10 = FUN_0043d0ce(), iVar10 << 0x1d < 0)) {
          uStack_a0 = uVar13;
          compress_log_output(0x8800000,_DAT_004e9da0,_DAT_004e9da0,
                              *(undefined1 *)(iStack_90 + uVar13 + 2));
        }
      }
    }
    uVar11 = FUN_0050fef8(*puVar3);
    *puVar1 = uVar11;
    uVar11 = FUN_0044104c(0);
    FUN_0044127e(*puVar1,uVar11,0);
    FUN_0043f4c0(*puVar1,0x160,0x120);
    FUN_0044146a(*puVar1,6,0);
    func_0x004e75b0(*puVar1,0,0);
    uStack_a0 = 0;
    FUN_0043f6d6(*puVar1,*puVar3,*(undefined1 *)(puVar5 + 2),0);
    FUN_0044e368(*puVar1,0);
    uVar11 = FUN_0044104c(0xffffff);
    FUN_004412ec(*puVar1,uVar11,0);
    FUN_0044131c(*puVar1,1,0);
    FUN_0044129e(*puVar1,0xff,0);
    FUN_0043ded4(*puVar1,1);
    FUN_0043f66c(*puVar1);
  }
  puVar8 = _DAT_004e9da4;
  if (((*piVar2 == 0) || ((int)*puVar4 < 1)) || ((int)*puVar6 <= (int)*puVar4)) {
    *_DAT_004e9da4 = 0;
    iVar10 = FUN_0043d0ce();
    if (iVar10 << 0x1e < 0) {
      uStack_94 = *puVar6;
      uStack_98 = *puVar4;
      puStack_9c = PTR_s_Dashboard_init__starting_from_ti_004e9db0;
      uStack_a0 = 0x773;
      FUN_0043d574(3,PTR_s_dashborad_ui_004e9d64,PTR_s_D__01_workspace_s200_ap510b_iar__004e9d60,
                   PTR_s_ui_Screen1_screen_init_004e9d5c);
    }
    iVar10 = FUN_0043d0ce();
    if ((iVar10 << 0x1f < 0) || (iVar10 = FUN_0043d0ce(), iVar10 << 0x1d < 0)) {
      uStack_a0 = *puVar6;
      compress_log_output(0xc800000,PTR_s__dashborad_ui_Dashboard_init__st_004e9db4,
                          PTR_s__dashborad_ui_Dashboard_init__st_004e9db4,*puVar4);
    }
    iVar10 = FUN_0045a570();
    if (iVar10 == 1) {
      bVar9 = FUN_004ffeb4(*puVar8);
      iVar10 = FUN_005000cc(*puVar8,bVar9);
      if (iVar10 != 0) {
        iVar10 = FUN_0043d0ce();
        if (iVar10 << 0x1e < 0) {
          uStack_94 = (uint)bVar9;
          uStack_98 = *puVar8;
          puStack_9c = PTR_s_Failed_to_sync_dashboard_main_pa_004e9db8;
          uStack_a0 = 0x779;
          FUN_0043d574(2,PTR_s_dashborad_ui_004e9d64,PTR_s_D__01_workspace_s200_ap510b_iar__004e9d60
                       ,PTR_s_ui_Screen1_screen_init_004e9d5c);
        }
        iVar10 = FUN_0043d0ce();
        if ((iVar10 << 0x1f < 0) || (iVar10 = FUN_0043d0ce(), iVar10 << 0x1d < 0)) {
          uStack_a0 = (uint)bVar9;
          compress_log_output(0x8800000,PTR_s__dashborad_ui_Failed_to_sync_das_004e9dbc,
                              PTR_s__dashborad_ui_Failed_to_sync_das_004e9dbc,*puVar8);
        }
      }
    }
  }
  else {
    uVar13 = *puVar4 * 0x130;
    FUN_0044ea04(*piVar2,uVar13,0);
    puVar6 = _DAT_004e9da4;
    *_DAT_004e9da4 = *puVar4;
    FUN_004e772c(*puVar6);
    iVar10 = FUN_0043d0ce();
    if (iVar10 << 0x1e < 0) {
      uStack_98 = *puVar4;
      puStack_9c = PTR_s_Dashboard_init__restored_to_save_004e9da8;
      uStack_a0 = 0x76f;
      uStack_94 = uVar13;
      FUN_0043d574(3,PTR_s_dashborad_ui_004e9d64,PTR_s_D__01_workspace_s200_ap510b_iar__004e9d60,
                   PTR_s_ui_Screen1_screen_init_004e9d5c);
    }
    iVar10 = FUN_0043d0ce();
    if ((iVar10 << 0x1f < 0) || (iVar10 = FUN_0043d0ce(), iVar10 << 0x1d < 0)) {
      uStack_a0 = uVar13;
      compress_log_output(0xc800000,PTR_s__dashborad_ui_Dashboard_init__re_004e9dac,
                          PTR_s__dashborad_ui_Dashboard_init__re_004e9dac,*puVar4);
    }
  }
  FUN_00441488(*puVar3,0,0);
  FUN_004503d6(&uStack_84);
  uStack_84 = *puVar3;
  FUN_004506ce(&uStack_84,0,0xff);
  uStack_54 = 0xfa;
  puStack_80 = PTR_FUN_004e79a8_1_004e9dc0;
  puStack_64 = PTR_LAB_0045065a_1_004e9dc4;
  puStack_74 = PTR_FUN_004e79b4_1_004e9dc8;
  *DAT_004e9d3c = 1;
  FUN_00450408(&uStack_84);
  iVar10 = FUN_0043d0ce();
  if (iVar10 << 0x1e < 0) {
    puStack_9c = PTR_s_Dashboard_screen_fade_in_animati_004e9dcc;
    uStack_a0 = 0x791;
    FUN_0043d574(4,PTR_s_dashborad_ui_004e9d64,PTR_s_D__01_workspace_s200_ap510b_iar__004e9d60,
                 PTR_s_ui_Screen1_screen_init_004e9d5c);
  }
  iVar10 = FUN_0043d0ce();
  if ((iVar10 << 0x1f < 0) || (iVar10 = FUN_0043d0ce(), iVar10 << 0x1d < 0)) {
    compress_log_output(0x10000000,PTR_s__dashborad_ui_Dashboard_screen_f_004e9dd0,
                        PTR_s__dashborad_ui_Dashboard_screen_f_004e9dd0);
  }
  return;
}

