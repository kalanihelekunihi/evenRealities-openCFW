
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

uint FUN_00496544(int *param_1,int param_2,short param_3)

{
  byte bVar1;
  ushort uVar2;
  byte *pbVar3;
  char cVar4;
  undefined1 uVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  uint uVar9;
  int iVar10;
  undefined *puVar11;
  undefined *puStack_4c;
  undefined *puStack_48;
  undefined4 uStack_44;
  undefined *puStack_40;
  undefined1 auStack_3c [12];
  undefined *puStack_30;
  undefined1 auStack_2c [16];
  
  iVar6 = FUN_0043d0ce();
  if (iVar6 << 0x1e < 0) {
    puStack_4c = PTR_s_evenhub_ui_page_reflash_event_ha_0049718c;
    FUN_0043d574(4,PTR_s_evenhub_ui_00497198,PTR_s_D__01_workspace_s200_ap510b_iar__00497194,
                 PTR_s_evenhub_ui_reflash_event_handler_00497190,0x5c6);
  }
  iVar6 = FUN_0043d0ce();
  if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
    compress_log_output(0x10000000,PTR_s__evenhub_ui_evenhub_ui_page_refl_0049719c,
                        PTR_s__evenhub_ui_evenhub_ui_page_refl_0049719c);
  }
  pbVar3 = _DAT_004971b0;
  if (param_1 == (int *)0x0) {
    iVar6 = FUN_0043d0ce();
    if (iVar6 << 0x1e < 0) {
      puStack_4c = PTR_s_evenhub_ui_page_create_manager_c_004971a0;
      FUN_0043d574(1,PTR_s_evenhub_ui_00497198,PTR_s_D__01_workspace_s200_ap510b_iar__00497194,
                   PTR_s_evenhub_ui_reflash_event_handler_00497190,0x5ca);
    }
    iVar6 = FUN_0043d0ce();
    if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__evenhub_ui_evenhub_ui_page_crea_004971a4,
                          PTR_s__evenhub_ui_evenhub_ui_page_crea_004971a4);
    }
    return 0xffffffff;
  }
  if ((param_2 == 0) || (param_3 == 0)) {
    iVar6 = FUN_0043d0ce();
    if (iVar6 << 0x1e < 0) {
      puStack_4c = PTR_s_evenhub_ui_page_create_data_is_N_004971a8;
      FUN_0043d574(1,PTR_s_evenhub_ui_00497198,PTR_s_D__01_workspace_s200_ap510b_iar__00497194,
                   PTR_s_evenhub_ui_reflash_event_handler_00497190,0x5cf);
    }
    iVar6 = FUN_0043d0ce();
    if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__evenhub_ui_evenhub_ui_page_crea_004971ac,
                          PTR_s__evenhub_ui_evenhub_ui_page_crea_004971ac);
    }
    return 0xffffffff;
  }
  FUN_0043c0e4(_DAT_004971b0,0x3758,0);
  FUN_0048f49c(auStack_2c,param_2,param_3);
  FUN_00439c04(auStack_3c,auStack_2c,0x10);
  cVar4 = FUN_00490120(auStack_3c,PTR_DAT_004971b4,pbVar3);
  if (cVar4 == '\0') {
    iVar6 = FUN_0043d0ce();
    if (iVar6 << 0x1e < 0) {
      puStack_48 = PTR_s__none__004971b8;
      if (puStack_30 != (undefined *)0x0) {
        puStack_48 = puStack_30;
      }
      puStack_4c = PTR_s_evenhub_protobuf_decode_failed____004971bc;
      FUN_0043d574(1,PTR_s_evenhub_ui_00497198,PTR_s_D__01_workspace_s200_ap510b_iar__00497194,
                   PTR_s_evenhub_ui_reflash_event_handler_00497190,0x5d7);
    }
    iVar6 = FUN_0043d0ce();
    if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
      puVar11 = PTR_s__none__004971b8;
      if (puStack_30 != (undefined *)0x0) {
        puVar11 = puStack_30;
      }
      compress_log_output(0x4400000,PTR_s__evenhub_ui_evenhub_protobuf_dec_004971c0,
                          PTR_s__evenhub_ui_evenhub_protobuf_dec_004971c0,puVar11);
    }
    return 0xffffffff;
  }
  bVar1 = *pbVar3;
  uVar2 = *(ushort *)(pbVar3 + 2);
  if (bVar1 == 5) {
    iVar6 = FUN_0043d0ce();
    if (iVar6 << 0x1e < 0) {
      puStack_4c = PTR_s_evenhub_ui_page_create__receive_t_0049724c;
      FUN_0043d574(4,PTR_s_evenhub_ui_00497198,PTR_s_D__01_workspace_s200_ap510b_iar__00497194,
                   PTR_s_evenhub_ui_reflash_event_handler_00497190,0x681);
    }
    iVar6 = FUN_0043d0ce();
    if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
      compress_log_output(0x10000000,PTR_s__evenhub_ui_evenhub_ui_page_crea_00497250,
                          PTR_s__evenhub_ui_evenhub_ui_page_crea_00497250);
    }
    if (uVar2 == 9) {
      iVar6 = FUN_0043d0ce();
      if (iVar6 << 0x1e < 0) {
        puStack_4c = PTR_s_evenhub_ui_page_create__receive_t_0049724c;
        FUN_0043d574(4,PTR_s_evenhub_ui_00497198,PTR_s_D__01_workspace_s200_ap510b_iar__00497194,
                     PTR_s_evenhub_ui_reflash_event_handler_00497190,0x683);
      }
      iVar6 = FUN_0043d0ce();
      if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
        compress_log_output(0x10000000,PTR_s__evenhub_ui_evenhub_ui_page_crea_00497250,
                            PTR_s__evenhub_ui_evenhub_ui_page_crea_00497250);
      }
      iVar6 = FUN_00493fa8(param_1,*(undefined4 *)(pbVar3 + 4));
      if (iVar6 != 0) {
        iVar7 = *(int *)(iVar6 + 0x10);
        FUN_0044b5a0(iVar7 + 0x20,pbVar3 + 0x20,0x7ff);
        *(undefined1 *)(iVar7 + 0x81f) = 0;
        iVar6 = FUN_0043d0ce();
        if (iVar6 << 0x1e < 0) {
          puStack_4c = PTR_s_evenhub_ui_page_create__update_t_00497254;
          FUN_0043d574(4,PTR_s_evenhub_ui_00497198,PTR_s_D__01_workspace_s200_ap510b_iar__00497194,
                       PTR_s_evenhub_ui_reflash_event_handler_00497190,0x689);
        }
        iVar6 = FUN_0043d0ce();
        if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
          compress_log_output(0x10000000,PTR_s__evenhub_ui_evenhub_ui_page_crea_00497258,
                              PTR_s__evenhub_ui_evenhub_ui_page_crea_00497258);
        }
        FUN_004e033c(iVar7,2,0,0);
        uVar9 = FUN_004d9c86(6,pbVar3[1],10,8);
        return uVar9;
      }
      iVar6 = FUN_0043d0ce();
      if (iVar6 << 0x1e < 0) {
        puStack_48 = *(undefined **)(pbVar3 + 4);
        puStack_4c = PTR_s_evenhub_ui_page_create__containe_0049725c;
        FUN_0043d574(1,PTR_s_evenhub_ui_00497198,PTR_s_D__01_workspace_s200_ap510b_iar__00497194,
                     PTR_s_evenhub_ui_reflash_event_handler_00497190,0x68e);
      }
      iVar6 = FUN_0043d0ce();
      if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
        compress_log_output(0x4400000,PTR_s__evenhub_ui_evenhub_ui_page_crea_00497260,
                            PTR_s__evenhub_ui_evenhub_ui_page_crea_00497260,
                            *(undefined4 *)(pbVar3 + 4));
      }
      uVar9 = FUN_004d9c86(6,pbVar3[1],10,9);
      return uVar9;
    }
    iVar6 = FUN_0043d0ce();
    if (iVar6 << 0x1e < 0) {
      puStack_48 = (undefined *)(uint)uVar2;
      puStack_4c = PTR_s_evenhub_ui_page_create__unknown_w_00497264;
      FUN_0043d574(1,PTR_s_evenhub_ui_00497198,PTR_s_D__01_workspace_s200_ap510b_iar__00497194,
                   PTR_s_evenhub_ui_reflash_event_handler_00497190,0x693);
    }
    iVar6 = FUN_0043d0ce();
    if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
      compress_log_output(0x4400000,PTR_s__evenhub_ui_evenhub_ui_page_crea_00497268,
                          PTR_s__evenhub_ui_evenhub_ui_page_crea_00497268,uVar2);
    }
    uVar9 = FUN_004d9c86(6,pbVar3[1],10,9);
    return uVar9;
  }
  if (bVar1 == 7) {
    if (*(char *)((int)param_1 + 0x35) == '\x01') {
      iVar6 = FUN_0043d0ce();
      if (iVar6 << 0x1e < 0) {
        puStack_4c = PTR_s_evenhub_ui_reflash_event_handler_0049721c;
        FUN_0043d574(4,PTR_s_evenhub_ui_00497198,PTR_s_D__01_workspace_s200_ap510b_iar__00497194,
                     PTR_s_evenhub_ui_reflash_event_handler_00497190,0x655);
      }
      iVar6 = FUN_0043d0ce();
      if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
        compress_log_output(0x10000000,PTR_s__evenhub_ui_evenhub_ui_reflash_e_00497220,
                            PTR_s__evenhub_ui_evenhub_ui_reflash_e_00497220);
      }
      return 0;
    }
    FUN_00494484(param_1);
    FUN_00493d02(param_1);
    iVar6 = FUN_004955b4(param_2,param_3,param_1);
    if (iVar6 != 0) {
      iVar6 = FUN_0043d0ce();
      if (iVar6 << 0x1e < 0) {
        puStack_4c = PTR_s_evenhub_ui_page_create__rebuild_p_00497224;
        FUN_0043d574(1,PTR_s_evenhub_ui_00497198,PTR_s_D__01_workspace_s200_ap510b_iar__00497194,
                     PTR_s_evenhub_ui_reflash_event_handler_00497190,0x65c);
      }
      iVar6 = FUN_0043d0ce();
      if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
        compress_log_output(0x4000000,PTR_s__evenhub_ui_evenhub_ui_page_crea_00497228,
                            PTR_s__evenhub_ui_evenhub_ui_page_crea_00497228);
      }
      iVar6 = FUN_0045a570();
      if (iVar6 == 1) {
        iVar6 = FUN_0043d0ce();
        if (iVar6 << 0x1e < 0) {
          puStack_4c = PTR_s_evenhub_ui_event_handler_rebuild_0049722c;
          FUN_0043d574(1,PTR_s_evenhub_ui_00497198,PTR_s_D__01_workspace_s200_ap510b_iar__00497194,
                       PTR_s_evenhub_ui_reflash_event_handler_00497190,0x65e);
        }
        iVar6 = FUN_0043d0ce();
        if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
          compress_log_output(0x4000000,PTR_s__evenhub_ui_evenhub_ui_event_han_00497230,
                              PTR_s__evenhub_ui_evenhub_ui_event_han_00497230);
        }
        puStack_4c = (undefined *)0x0;
        FUN_004da16a(0,0,0,6,0);
        FUN_00464c36(0xe0,0,0,0);
      }
      else {
        iVar6 = FUN_0043d0ce();
        if (iVar6 << 0x1e < 0) {
          puStack_4c = PTR_s_evenhub_ui_event_handler_rebuild_00497234;
          FUN_0043d574(1,PTR_s_evenhub_ui_00497198,PTR_s_D__01_workspace_s200_ap510b_iar__00497194,
                       PTR_s_evenhub_ui_reflash_event_handler_00497190,0x663);
        }
        iVar6 = FUN_0043d0ce();
        if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
          compress_log_output(0x4000000,PTR_s__evenhub_ui_evenhub_ui_event_han_00497238,
                              PTR_s__evenhub_ui_evenhub_ui_event_han_00497238);
        }
        FUN_0043c0e4(&puStack_4c,5,0);
        puStack_4c = (undefined *)((uint)puStack_4c & 0xffffff00);
        FUN_00465480(0xe0,&puStack_4c,1,0,5);
      }
      return 0xffffffff;
    }
    return 0;
  }
  if (bVar1 == 9) {
    if (uVar2 != 0xb) {
      iVar6 = FUN_0043d0ce();
      if (iVar6 << 0x1e < 0) {
        puStack_48 = (undefined *)(uint)uVar2;
        puStack_4c = PTR_s_evenhub_ui_page_create__unknown_w_00497264;
        FUN_0043d574(1,PTR_s_evenhub_ui_00497198,PTR_s_D__01_workspace_s200_ap510b_iar__00497194,
                     PTR_s_evenhub_ui_reflash_event_handler_00497190,0x6b2);
      }
      iVar6 = FUN_0043d0ce();
      if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
        compress_log_output(0x4400000,PTR_s__evenhub_ui_evenhub_ui_page_crea_00497268,
                            PTR_s__evenhub_ui_evenhub_ui_page_crea_00497268,uVar2);
      }
      uVar9 = FUN_004d9c86(10,pbVar3[1],0xc,0xb);
      return uVar9;
    }
    iVar6 = FUN_0043d0ce();
    if (iVar6 << 0x1e < 0) {
      puStack_4c = PTR_s_evenhub_ui_page_create__receive_s_0049726c;
      FUN_0043d574(4,PTR_s_evenhub_ui_00497198,PTR_s_D__01_workspace_s200_ap510b_iar__00497194,
                   PTR_s_evenhub_ui_reflash_event_handler_00497190,0x69c);
    }
    iVar6 = FUN_0043d0ce();
    if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
      compress_log_output(0x10000000,PTR_s__evenhub_ui_evenhub_ui_page_crea_00497270,
                          PTR_s__evenhub_ui_evenhub_ui_page_crea_00497270);
    }
    FUN_004d9c86(10,pbVar3[1],0xc,10);
    if (*(int *)(pbVar3 + 4) == 0) {
      func_0x004e0cb2(1);
      iVar6 = FUN_0043d0ce();
      if (iVar6 << 0x1e < 0) {
        puStack_4c = PTR_s_evenhub_ui_page_create__exit_imm_00497274;
        FUN_0043d574(4,PTR_s_evenhub_ui_00497198,PTR_s_D__01_workspace_s200_ap510b_iar__00497194,
                     PTR_s_evenhub_ui_reflash_event_handler_00497190,0x6a3);
      }
      iVar6 = FUN_0043d0ce();
      if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
        compress_log_output(0x10000000,PTR_s__evenhub_ui_evenhub_ui_page_crea_00497278,
                            PTR_s__evenhub_ui_evenhub_ui_page_crea_00497278);
      }
      if (*param_1 == 0) {
        return 0;
      }
      FUN_004641b6(*param_1,0xe0);
      FUN_004e0ca0();
      uStack_44 = *(undefined4 *)PTR_DAT_0049727c;
      puStack_40 = *(undefined **)(PTR_DAT_0049727c + 4);
      uStack_44 = FUN_004935fe();
      uVar9 = FUN_0048eb32(_DAT_00497280,2,&uStack_44);
      return uVar9;
    }
    func_0x004e0cb2(1);
    uVar9 = FUN_0045a568();
    if (uVar9 != 1) {
      return uVar9;
    }
    iVar6 = FUN_0043d0ce();
    if (iVar6 << 0x1e < 0) {
      puStack_4c = PTR_s_evenhub_ui_page_create__pop_up_f_00497284;
      FUN_0043d574(4,PTR_s_evenhub_ui_00497198,PTR_s_D__01_workspace_s200_ap510b_iar__00497194,
                   PTR_s_evenhub_ui_reflash_event_handler_00497190,0x6ad);
    }
    iVar6 = FUN_0043d0ce();
    if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
      compress_log_output(0x10000000,PTR_s__evenhub_ui_evenhub_ui_page_crea_00497288,
                          PTR_s__evenhub_ui_evenhub_ui_page_crea_00497288);
    }
    uVar9 = system_close_page_factory_0046ae9c(1,0xe0);
    return uVar9;
  }
  if (bVar1 != 0xb) {
    if (bVar1 == 0xc) {
      if (uVar2 != 0xe) {
        return 0xc;
      }
      func_0x004e0cba();
      uVar9 = FUN_004d9bfe(pbVar3[1],0xc,*(undefined4 *)(pbVar3 + 4));
      return uVar9;
    }
    if (bVar1 == 0xe) {
      if (pbVar3[4] == 0) {
        iVar6 = FUN_0043d0ce();
        if (iVar6 << 0x1e < 0) {
          puStack_4c = PTR_s_evenhub_ui_page_create__receive_s_0049723c;
          FUN_0043d574(4,PTR_s_evenhub_ui_00497198,PTR_s_D__01_workspace_s200_ap510b_iar__00497194,
                       PTR_s_evenhub_ui_reflash_event_handler_00497190,0x671);
        }
        iVar6 = FUN_0043d0ce();
        if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
          compress_log_output(0x10000000,PTR_s__evenhub_ui_evenhub_ui_page_crea_00497240,
                              PTR_s__evenhub_ui_evenhub_ui_page_crea_00497240);
        }
        FUN_00494484(param_1);
        FUN_00493d02(param_1);
        FUN_0044d878(*param_1);
        FUN_00496430(*param_1);
        func_0x004e0cc4();
        *(undefined1 *)((int)param_1 + 0x35) = 1;
        return 1;
      }
      if (pbVar3[4] != 1) {
        return (uint)pbVar3[4];
      }
      iVar6 = FUN_0043d0ce();
      if (iVar6 << 0x1e < 0) {
        puStack_4c = PTR_s_evenhub_ui_page_create__receive_s_00497244;
        FUN_0043d574(4,PTR_s_evenhub_ui_00497198,PTR_s_D__01_workspace_s200_ap510b_iar__00497194,
                     PTR_s_evenhub_ui_reflash_event_handler_00497190,0x679);
      }
      iVar6 = FUN_0043d0ce();
      if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
        compress_log_output(0x10000000,PTR_s__evenhub_ui_evenhub_ui_page_crea_00497248,
                            PTR_s__evenhub_ui_evenhub_ui_page_crea_00497248);
      }
      FUN_004641b6(*param_1,0xe0);
      uVar9 = FUN_004e0ca0();
      return uVar9;
    }
    if (bVar1 != 0xf) {
      iVar6 = FUN_0043d0ce();
      if (iVar6 << 0x1e < 0) {
        puStack_48 = (undefined *)(uint)bVar1;
        puStack_4c = PTR_s_evenhub_ui_page_create__unknown_c_00497294;
        FUN_0043d574(1,PTR_s_evenhub_ui_00497198,PTR_s_D__01_workspace_s200_ap510b_iar__00497194,
                     PTR_s_evenhub_ui_reflash_event_handler_00497190,0x6cd);
      }
      iVar6 = FUN_0043d0ce();
      if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
        compress_log_output(0x4400000,PTR_s__evenhub_ui_evenhub_ui_page_crea_00497298,
                            PTR_s__evenhub_ui_evenhub_ui_page_crea_00497298,bVar1);
      }
      return 0xffffffff;
    }
    if (uVar2 != 0x12) {
      return 0xf;
    }
    iVar6 = FUN_0043d0ce();
    if (iVar6 << 0x1e < 0) {
      puStack_48 = *(undefined **)(pbVar3 + 4);
      puStack_4c = PTR_s_evenhub_ui_page_create__receive_a_0049728c;
      FUN_0043d574(4,PTR_s_evenhub_ui_00497198,PTR_s_D__01_workspace_s200_ap510b_iar__00497194,
                   PTR_s_evenhub_ui_reflash_event_handler_00497190,0x6c3);
    }
    iVar6 = FUN_0043d0ce();
    if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
      compress_log_output(0x10400000,PTR_s__evenhub_ui_evenhub_ui_page_crea_00497290,
                          PTR_s__evenhub_ui_evenhub_ui_page_crea_00497290,
                          *(undefined4 *)(pbVar3 + 4));
    }
    uVar5 = FUN_004e1406(*(undefined4 *)(pbVar3 + 4));
    uVar9 = FUN_004da56e(pbVar3[1],uVar5);
    return uVar9;
  }
  if (uVar2 != 0x10) {
    return 0xb;
  }
  iVar6 = FUN_0043d0ce();
  if (iVar6 << 0x1e < 0) {
    puStack_4c = PTR_s_evenhub_ui_reflash_event_handler_004971c4;
    FUN_0043d574(3,PTR_s_evenhub_ui_00497198,PTR_s_D__01_workspace_s200_ap510b_iar__00497194,
                 PTR_s_evenhub_ui_reflash_event_handler_00497190,0x5e2);
  }
  iVar6 = FUN_0043d0ce();
  if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
    compress_log_output(0xc000000,PTR_s__evenhub_ui_evenhub_ui_reflash_e_004971c8,
                        PTR_s__evenhub_ui_evenhub_ui_reflash_e_004971c8);
  }
  iVar6 = FUN_00493fa8(param_1,*(undefined4 *)(pbVar3 + 4));
  iVar7 = FUN_0043d0ce();
  if (iVar7 << 0x1e < 0) {
    puStack_48 = *(undefined **)(pbVar3 + 4);
    puStack_4c = PTR_s_evenhub_ui_reflash_event_handler_004971cc;
    FUN_0043d574(3,PTR_s_evenhub_ui_00497198,PTR_s_D__01_workspace_s200_ap510b_iar__00497194,
                 PTR_s_evenhub_ui_reflash_event_handler_00497190,0x5e4);
  }
  iVar7 = FUN_0043d0ce();
  if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
    compress_log_output(0xc400000,PTR_s__evenhub_ui_evenhub_ui_reflash_e_004971d0,
                        PTR_s__evenhub_ui_evenhub_ui_reflash_e_004971d0,*(undefined4 *)(pbVar3 + 4))
    ;
  }
  if (iVar6 == 0) {
    iVar6 = FUN_0043d0ce();
    if (iVar6 << 0x1e < 0) {
      puStack_48 = *(undefined **)(pbVar3 + 4);
      puStack_4c = PTR_s_evenhub_ui_reflash_event_handler_00497214;
      FUN_0043d574(1,PTR_s_evenhub_ui_00497198,PTR_s_D__01_workspace_s200_ap510b_iar__00497194,
                   PTR_s_evenhub_ui_reflash_event_handler_00497190,0x64d);
    }
    iVar6 = FUN_0043d0ce();
    if (-1 < iVar6 << 0x1f) {
      iVar6 = FUN_0043d0ce();
      if (-1 < iVar6 << 0x1d) {
        return iVar6 << 0x1d;
      }
    }
    uVar9 = compress_log_output(0x4400000,PTR_s__evenhub_ui_evenhub_ui_reflash_e_00497218,
                                PTR_s__evenhub_ui_evenhub_ui_reflash_e_00497218,
                                *(undefined4 *)(pbVar3 + 4));
    return uVar9;
  }
  if (*(char *)(iVar6 + 8) == '\0') {
    uVar5 = 0xff;
    iVar7 = *(int *)(pbVar3 + 0x18);
    if (iVar7 == 10) {
      uVar5 = 2;
    }
    else if (iVar7 == 0x44) {
      uVar5 = 0;
    }
    else if (iVar7 == 0x45) {
      uVar5 = 1;
    }
    uVar9 = FUN_004de354(*(undefined4 *)(iVar6 + 0x10),uVar5);
    return uVar9;
  }
  if (*(char *)(iVar6 + 8) == '\x01') {
    uVar5 = 0xff;
    if (*(int *)(pbVar3 + 0x18) == 0x44) {
      uVar5 = 0;
    }
    else if (*(int *)(pbVar3 + 0x18) == 0x45) {
      uVar5 = 1;
    }
    uVar9 = FUN_004e033c(*(undefined4 *)(iVar6 + 0x10),uVar5,*(uint *)(pbVar3 + 0x1c) >> 0x10,
                         *(uint *)(pbVar3 + 0x1c) & 0xffff);
    return uVar9;
  }
  if (*(byte *)(iVar6 + 8) != 2) {
    return (uint)*(byte *)(iVar6 + 8);
  }
  iVar7 = *(int *)(iVar6 + 0x10);
  iVar6 = FUN_0043d0ce();
  if (iVar6 << 0x1e < 0) {
    puStack_4c = PTR_s_evenhub_ui_reflash_event_handler_004971d4;
    FUN_0043d574(3,PTR_s_evenhub_ui_00497198,PTR_s_D__01_workspace_s200_ap510b_iar__00497194,
                 PTR_s_evenhub_ui_reflash_event_handler_00497190,0x609);
  }
  iVar6 = FUN_0043d0ce();
  if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
    compress_log_output(0xc000000,PTR_s__evenhub_ui_evenhub_ui_reflash_e_004971d8,
                        PTR_s__evenhub_ui_evenhub_ui_reflash_e_004971d8);
  }
  if (*(int *)(pbVar3 + 0x18) != 0x4c) {
    iVar6 = FUN_0043d0ce();
    if (iVar6 << 0x1e < 0) {
      puStack_48 = *(undefined **)(pbVar3 + 0x18);
      puStack_4c = PTR_s_evenhub_ui_reflash_event_handler_0049720c;
      FUN_0043d574(1,PTR_s_evenhub_ui_00497198,PTR_s_D__01_workspace_s200_ap510b_iar__00497194,
                   PTR_s_evenhub_ui_reflash_event_handler_00497190,0x647);
    }
    iVar6 = FUN_0043d0ce();
    if (-1 < iVar6 << 0x1f) {
      iVar6 = FUN_0043d0ce();
      if (-1 < iVar6 << 0x1d) {
        return iVar6 << 0x1d;
      }
    }
    uVar9 = compress_log_output(0x4400000,PTR_s__evenhub_ui_evenhub_ui_reflash_e_00497210,
                                PTR_s__evenhub_ui_evenhub_ui_reflash_e_00497210,
                                *(undefined4 *)(pbVar3 + 0x18));
    return uVar9;
  }
  iVar6 = *(int *)(iVar7 + 0xc);
  puVar11 = *(undefined **)(iVar7 + 0x20);
  iVar10 = 0;
  if ((*(int *)(iVar7 + 0x18) == 1) || (*(int *)(iVar7 + 0x18) == 2)) {
    iVar10 = file_heap_allocate(*(undefined4 *)(iVar7 + 0x44));
    if (iVar10 == 0) {
      iVar6 = FUN_0043d0ce();
      if (iVar6 << 0x1e < 0) {
        puStack_48 = *(undefined **)(iVar7 + 0x44);
        puStack_4c = PTR_s_evenhub_ui__alloc_decode_buffer_f_004971dc;
        FUN_0043d574(1,PTR_s_evenhub_ui_00497198,PTR_s_D__01_workspace_s200_ap510b_iar__00497194,
                     PTR_s_evenhub_ui_reflash_event_handler_00497190,0x618);
      }
      iVar6 = FUN_0043d0ce();
      if (-1 < iVar6 << 0x1f) {
        iVar6 = FUN_0043d0ce();
        if (-1 < iVar6 << 0x1d) {
          return iVar6 << 0x1d;
        }
      }
      uVar9 = compress_log_output(0x4400000,PTR_s__evenhub_ui_evenhub_ui__alloc_de_004971e0,
                                  PTR_s__evenhub_ui_evenhub_ui__alloc_de_004971e0,
                                  *(undefined4 *)(iVar7 + 0x44));
      return uVar9;
    }
    if (*(int *)(iVar7 + 0x18) == 2) {
      puVar11 = (undefined *)
                func_0x004e0c0c(*(undefined4 *)(iVar7 + 0xc),*(undefined4 *)(iVar7 + 0x20),iVar10,
                                *(undefined4 *)(iVar7 + 0x44));
    }
    else {
      puVar11 = (undefined *)
                func_0x004e0c34(*(undefined4 *)(iVar7 + 0xc),*(undefined4 *)(iVar7 + 0x20),iVar10,
                                *(undefined4 *)(iVar7 + 0x44));
    }
    if (puVar11 == (undefined *)0x0) {
      iVar6 = FUN_0043d0ce();
      if (iVar6 << 0x1e < 0) {
        uStack_44 = *(undefined4 *)(iVar7 + 0x20);
        puStack_48 = *(undefined **)(iVar7 + 0x18);
        puStack_4c = PTR_s_evenhub_ui__decompress_failed__m_004971e4;
        FUN_0043d574(1,PTR_s_evenhub_ui_00497198,PTR_s_D__01_workspace_s200_ap510b_iar__00497194,
                     PTR_s_evenhub_ui_reflash_event_handler_00497190,0x62d);
      }
      iVar6 = FUN_0043d0ce();
      if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
        compress_log_output(0x4800000,PTR_s__evenhub_ui_evenhub_ui__decompre_004971e8,
                            PTR_s__evenhub_ui_evenhub_ui__decompre_004971e8,
                            *(undefined4 *)(iVar7 + 0x18),*(undefined4 *)(iVar7 + 0x20));
      }
      uVar9 = file_heap_free(iVar10);
      return uVar9;
    }
    iVar6 = FUN_0043d0ce();
    if (iVar6 << 0x1e < 0) {
      uStack_44 = *(undefined4 *)(iVar7 + 0x20);
      puStack_48 = *(undefined **)(iVar7 + 0x18);
      puStack_4c = PTR_s_evenhub_ui__decompress_mode__u___004971ec;
      puStack_40 = puVar11;
      FUN_0043d574(3,PTR_s_evenhub_ui_00497198,PTR_s_D__01_workspace_s200_ap510b_iar__00497194,
                   PTR_s_evenhub_ui_reflash_event_handler_00497190,0x632);
    }
    iVar8 = FUN_0043d0ce();
    iVar6 = iVar10;
    if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
      puStack_4c = puVar11;
      compress_log_output(0xcc00000,PTR_s__evenhub_ui_evenhub_ui__decompre_004971f0,
                          PTR_s__evenhub_ui_evenhub_ui__decompre_004971f0,
                          *(undefined4 *)(iVar7 + 0x18),*(undefined4 *)(iVar7 + 0x20));
    }
  }
  else if (*(int *)(iVar7 + 0x18) != 0) {
    iVar8 = FUN_0043d0ce();
    if (iVar8 << 0x1e < 0) {
      puStack_48 = *(undefined **)(iVar7 + 0x18);
      puStack_4c = PTR_s_evenhub_ui__unsupported_compress_004971f4;
      FUN_0043d574(2,PTR_s_evenhub_ui_00497198,PTR_s_D__01_workspace_s200_ap510b_iar__00497194,
                   PTR_s_evenhub_ui_reflash_event_handler_00497190,0x637);
    }
    iVar8 = FUN_0043d0ce();
    if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
      compress_log_output(0x8400000,PTR_s__evenhub_ui_evenhub_ui__unsuppor_004971f8,
                          PTR_s__evenhub_ui_evenhub_ui__unsuppor_004971f8,
                          *(undefined4 *)(iVar7 + 0x18));
    }
  }
  puVar11 = (undefined *)FUN_004dc5ae(iVar7,iVar6,puVar11);
  if (puVar11 == (undefined *)0x0) {
    iVar6 = FUN_0043d0ce();
    if (iVar6 << 0x1e < 0) {
      puStack_4c = PTR_s_evenhub_ui_reflash_event_handler_004971fc;
      FUN_0043d574(3,PTR_s_evenhub_ui_00497198,PTR_s_D__01_workspace_s200_ap510b_iar__00497194,
                   PTR_s_evenhub_ui_reflash_event_handler_00497190,0x63c);
    }
    iVar6 = FUN_0043d0ce();
    if (-1 < iVar6 << 0x1f) {
      iVar6 = FUN_0043d0ce();
      uVar9 = iVar6 << 0x1d;
      if (-1 < (int)uVar9) goto LAB_00496aa6;
    }
    uVar9 = compress_log_output(0xc000000,PTR_s__evenhub_ui_evenhub_ui_reflash_e_00497200,
                                PTR_s__evenhub_ui_evenhub_ui_reflash_e_00497200);
  }
  else {
    iVar6 = FUN_0043d0ce();
    if (iVar6 << 0x1e < 0) {
      puStack_4c = PTR_s_evenhub_ui_reflash_event_handler_00497204;
      puStack_48 = puVar11;
      FUN_0043d574(1,PTR_s_evenhub_ui_00497198,PTR_s_D__01_workspace_s200_ap510b_iar__00497194,
                   PTR_s_evenhub_ui_reflash_event_handler_00497190,0x63e);
    }
    iVar6 = FUN_0043d0ce();
    if (-1 < iVar6 << 0x1f) {
      iVar6 = FUN_0043d0ce();
      uVar9 = iVar6 << 0x1d;
      if (-1 < (int)uVar9) goto LAB_00496aa6;
    }
    uVar9 = compress_log_output(0x4400000,PTR_s__evenhub_ui_evenhub_ui_reflash_e_00497208,
                                PTR_s__evenhub_ui_evenhub_ui_reflash_e_00497208,puVar11);
  }
LAB_00496aa6:
  if (iVar10 != 0) {
    uVar9 = file_heap_free(iVar10);
  }
  return uVar9;
}

