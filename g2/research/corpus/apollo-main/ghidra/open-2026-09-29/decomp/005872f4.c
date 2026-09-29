
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

uint navigation_data_dispatch(undefined4 param_1,int param_2)

{
  byte bVar1;
  byte *pbVar2;
  undefined4 *puVar3;
  uint *puVar4;
  char cVar5;
  byte bVar6;
  int iVar7;
  uint uVar8;
  int iVar9;
  undefined *puVar10;
  byte *pbVar11;
  undefined1 *puVar12;
  undefined1 *puVar13;
  undefined4 uVar14;
  undefined1 *puVar15;
  undefined4 uStack_d8;
  undefined1 *puStack_d4;
  undefined1 *puStack_d0;
  undefined4 uStack_cc;
  undefined1 *puStack_c8;
  undefined1 *puStack_c4;
  undefined4 uStack_c0;
  undefined1 *puStack_bc;
  undefined4 uStack_b8;
  undefined1 auStack_b4 [12];
  undefined1 *puStack_a8;
  undefined1 uStack_a4;
  byte bStack_a3;
  undefined1 uStack_98;
  byte bStack_97;
  undefined1 uStack_8c;
  byte bStack_8b;
  undefined1 uStack_80;
  byte bStack_7f;
  undefined1 uStack_74;
  byte bStack_73;
  undefined1 uStack_68;
  byte bStack_67;
  undefined1 uStack_5c;
  byte bStack_5b;
  undefined4 uStack_50;
  undefined4 uStack_4c;
  undefined1 uStack_48;
  byte bStack_47;
  undefined1 uStack_3c;
  byte bStack_3b;
  undefined1 uStack_30;
  byte bStack_2f;
  
  FUN_00585ca4();
  pbVar2 = _DAT_00588028;
  if (param_2 == 0) {
    iVar7 = FUN_0043d0ce();
    if (iVar7 << 0x1e < 0) {
      puStack_d4 = PTR_s_navigation_data_handler__len_is_0_00588014;
      uStack_d8 = (byte *)0x2d3;
      FUN_0043d574(1,PTR_s_navigation_datahandler_00588020,
                   PTR_s_D__01_workspace_s200_ap510b_iar__0058801c,
                   PTR_s_navigation_data_handler_00588018);
    }
    iVar7 = FUN_0043d0ce();
    if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__navigation_datahandler_navigati_00588024,
                          PTR_s__navigation_datahandler_navigati_00588024);
    }
    uVar8 = 0xffffffff;
  }
  else {
    FUN_0043c0e4(_DAT_00588028,0x2024,0);
    FUN_0048f49c(&uStack_d8,param_1,param_2);
    FUN_00439c04(auStack_b4,&uStack_d8,0x10);
    cVar5 = FUN_00490120(auStack_b4,PTR_DAT_0058802c,pbVar2);
    puVar3 = _DAT_005881b0;
    if (cVar5 == '\0') {
      iVar7 = FUN_0043d0ce();
      if (iVar7 << 0x1e < 0) {
        puStack_d0 = PTR_s__none__00588030;
        if (puStack_a8 != (undefined1 *)0x0) {
          puStack_d0 = puStack_a8;
        }
        puStack_d4 = PTR_s_navigation_protobuf_decode_faile_00588034;
        uStack_d8 = (byte *)0x2db;
        FUN_0043d574(1,PTR_s_navigation_datahandler_00588020,
                     PTR_s_D__01_workspace_s200_ap510b_iar__0058801c,
                     PTR_s_navigation_data_handler_00588018);
      }
      iVar7 = FUN_0043d0ce();
      if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
        puVar10 = PTR_s__none__00588030;
        if (puStack_a8 != (undefined1 *)0x0) {
          puVar10 = puStack_a8;
        }
        compress_log_output(0x4400000,PTR_s__navigation_datahandler_navigati_00588038,
                            PTR_s__navigation_datahandler_navigati_00588038,puVar10);
      }
      uVar8 = 0;
    }
    else {
      bVar1 = pbVar2[1];
      uVar8 = (uint)*pbVar2;
      if (uVar8 == 0) {
        bVar6 = FUN_0045a570();
        uVar8 = (uint)bVar6;
        if (((uVar8 == 1) && (uVar8 = FUN_00443484(), uVar8 == 1)) &&
           (uVar8 = FUN_004434d0(8), uVar8 == 1)) {
          uStack_30 = 0;
          bStack_2f = bVar1;
          uVar8 = FUN_00464bb2(8,&uStack_30,6,0);
        }
      }
      else if (uVar8 == 2) {
        uVar8 = (uint)*(ushort *)(pbVar2 + 2);
        if (uVar8 == 4) {
          osMutexAcquire(*_DAT_005881b0,0xffffffff);
          puVar4 = _DAT_005881b4;
          FUN_0043c0e4(_DAT_005881b4,0x55c,0);
          *_DAT_005881b8 = 1;
          *puVar4 = (uint)*(ushort *)(pbVar2 + 8);
          for (puVar12 = (undefined1 *)0x0; puVar12 < *(undefined1 **)(pbVar2 + 4);
              puVar12 = puVar12 + 1) {
            iVar7 = FUN_0043d0ce();
            if (iVar7 << 0x1e < 0) {
              puStack_c4 = *(undefined1 **)(pbVar2 + (int)puVar12 * 4 + 0x50c);
              uStack_cc = pbVar2 + (int)puVar12 * 0x40 + 10;
              puStack_d4 = _DAT_005881bc;
              uStack_d8 = (byte *)0x2f8;
              puStack_d0 = puVar12;
              puStack_c8 = puVar12;
              FUN_0043d574(3,PTR_s_navigation_datahandler_00588020,
                           PTR_s_D__01_workspace_s200_ap510b_iar__0058801c,
                           PTR_s_navigation_data_handler_00588018);
            }
            iVar7 = FUN_0043d0ce();
            if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
              puStack_d0 = *(undefined1 **)(pbVar2 + (int)puVar12 * 4 + 0x50c);
              uStack_d8 = pbVar2 + (int)puVar12 * 0x40 + 10;
              puStack_d4 = puVar12;
              compress_log_output(0xd000000,_DAT_005881c0,_DAT_005881c0,puVar12);
            }
            uVar14 = FUN_0044a43c(pbVar2 + (int)puVar12 * 0x40 + 10);
            FUN_00439be4((int)puVar4 + (int)puVar12 * 0x40 + 6,pbVar2 + (int)puVar12 * 0x40 + 10,
                         uVar14);
            puVar4[(int)(puVar12 + 0x142)] = *(uint *)(pbVar2 + (int)puVar12 * 4 + 0x50c);
          }
          osMutexRelease(*puVar3);
          bVar6 = FUN_0045a570();
          uVar8 = (uint)bVar6;
          if (((uVar8 == 1) && (uVar8 = FUN_00443484(), uVar8 == 1)) &&
             (uVar8 = FUN_004434d0(8), uVar8 == 1)) {
            uStack_3c = 2;
            bStack_3b = bVar1;
            uVar8 = FUN_0045aaca(8,&uStack_3c,2,500);
          }
        }
      }
      else if (uVar8 == 3) {
        bVar6 = FUN_0045a570();
        uVar8 = (uint)bVar6;
        if (((uVar8 == 1) && (uVar8 = FUN_00443484(), uVar8 == 1)) &&
           (uVar8 = FUN_004434d0(8), uVar8 == 1)) {
          uStack_48 = 3;
          bStack_47 = bVar1;
          uVar8 = FUN_00464bb2(8,&uStack_48,6,0);
        }
      }
      else if (uVar8 == 5) {
        bVar6 = FUN_0045a570();
        uVar8 = (uint)bVar6;
        if (uVar8 == 1) {
          FUN_0043c0e4(&uStack_c0,10,0);
          uStack_c0._0_2_ = CONCAT11(bVar1,5);
          FUN_00464b2e(8,&uStack_c0,6,0);
          uStack_50 = *_DAT_005882e8;
          uStack_4c = _DAT_005882e8[1];
          uVar8 = FUN_0048eb32(_DAT_005882ec,2,&uStack_50);
        }
      }
      else if (uVar8 == 6) {
        bVar6 = FUN_0045a570();
        uVar8 = (uint)bVar6;
        if (((uVar8 == 1) && (uVar8 = FUN_00443484(), uVar8 == 1)) &&
           (uVar8 = FUN_004434d0(8), uVar8 == 1)) {
          FUN_0043c0e4(&uStack_d8,10,0);
          uStack_d8._0_3_ = CONCAT12((char)*(undefined4 *)(pbVar2 + 0x48),CONCAT11(bVar1,6));
          uVar8 = FUN_00464bb2(8,&uStack_d8,6,0);
        }
      }
      else if (uVar8 == 7) {
        osMutexAcquire(*_DAT_005881b0,0xffffffff);
        puVar12 = _DAT_005882f0;
        FUN_0043c0e4(_DAT_005882f0,0x18c,0);
        *puVar12 = 1;
        *(undefined4 *)(puVar12 + 4) = *(undefined4 *)(pbVar2 + 4);
        uVar14 = FUN_0044a43c(pbVar2 + 8);
        puVar13 = _DAT_005882f4;
        FUN_00439be4(_DAT_005882f4,pbVar2 + 8,uVar14);
        uVar14 = FUN_0044a43c(pbVar2 + 0x48);
        pbVar11 = _DAT_005882f8;
        FUN_00439be4(_DAT_005882f8,pbVar2 + 0x48,uVar14);
        uVar14 = FUN_0044a43c(pbVar2 + 0x88);
        puVar15 = _DAT_005882fc;
        FUN_00439be4(_DAT_005882fc,pbVar2 + 0x88,uVar14);
        uVar14 = FUN_0044a43c(pbVar2 + 200);
        FUN_00439be4(puVar12 + 200,pbVar2 + 200,uVar14);
        uVar14 = FUN_0044a43c(pbVar2 + 0x108);
        FUN_00439be4(puVar12 + 0x108,pbVar2 + 0x108,uVar14);
        uVar14 = FUN_0044a43c(pbVar2 + 0x148);
        FUN_00439be4(puVar12 + 0x148,pbVar2 + 0x148,uVar14);
        *(undefined4 *)(puVar12 + 0x188) = *(undefined4 *)(pbVar2 + 0x188);
        osMutexRelease(*puVar3);
        iVar7 = FUN_0043d0ce();
        if (iVar7 << 0x1e < 0) {
          uStack_b8 = *(undefined4 *)(puVar12 + 0x188);
          puStack_bc = puVar12 + 0x148;
          uStack_c0 = puVar12 + 0x108;
          puStack_c4 = puVar12 + 200;
          puStack_c8 = puVar15;
          uStack_cc = pbVar11;
          puStack_d0 = puVar13;
          puStack_d4 = _DAT_00588300;
          uStack_d8 = (byte *)0x347;
          FUN_0043d574(3,PTR_s_navigation_datahandler_00588020,
                       PTR_s_D__01_workspace_s200_ap510b_iar__0058801c,
                       PTR_s_navigation_data_handler_00588018);
        }
        iVar7 = FUN_0043d0ce();
        if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
          puStack_c4 = *(undefined1 **)(puVar12 + 0x188);
          puStack_c8 = puVar12 + 0x148;
          uStack_cc = puVar12 + 0x108;
          puStack_d0 = puVar12 + 200;
          puStack_d4 = puVar15;
          uStack_d8 = pbVar11;
          compress_log_output(0xdc00000,_DAT_00588304,_DAT_00588304,puVar13);
        }
        bVar6 = FUN_0045a570();
        uVar8 = (uint)bVar6;
        if (((uVar8 == 1) && (uVar8 = FUN_00443484(), uVar8 == 1)) &&
           (uVar8 = FUN_004434d0(8), uVar8 == 1)) {
          uStack_5c = 7;
          bStack_5b = bVar1;
          uVar8 = FUN_0045aaca(8,&uStack_5c,6,500);
        }
      }
      else if (uVar8 == 8) {
        uStack_c0 = *(undefined1 **)(pbVar2 + 0x2018);
        pbVar11 = *(byte **)(pbVar2 + 4);
        puVar12 = *(undefined1 **)(pbVar2 + 8);
        puVar13 = *(undefined1 **)(pbVar2 + 0x201c);
        uVar14 = *(undefined4 *)(pbVar2 + 0x2020);
        puVar15 = (undefined1 *)(uint)*(ushort *)(pbVar2 + 0xc);
        osMutexAcquire(*_DAT_005881b0,0xffffffff);
        iVar7 = _DAT_00588308;
        if ((*(int *)(_DAT_00588308 + 0x20) == 0) && (*(int *)(_DAT_00588308 + 0x18) == 0)) {
          if (*(int *)(pbVar2 + 0x201c) == 0) {
            *(undefined1 **)(_DAT_00588308 + 4) = uStack_c0;
            *(byte **)(iVar7 + 8) = pbVar11;
            *(undefined1 **)(iVar7 + 0xc) = puVar12;
            *(undefined4 *)(iVar7 + 0x10) = *(undefined4 *)(pbVar2 + 0x2010);
            *(undefined4 *)(iVar7 + 0x14) = *(undefined4 *)(pbVar2 + 0x2014);
            *(undefined1 **)(iVar7 + 0x18) = puVar13;
            *(undefined4 *)(iVar7 + 0x1c) = uVar14;
            if ((undefined1 *)0x4650 < puVar15) {
              iVar9 = FUN_0043d0ce();
              if (iVar9 << 0x1e < 0) {
                uStack_cc = (byte *)0x4650;
                puStack_d4 = _DAT_0058830c;
                uStack_d8 = (byte *)0x36c;
                puStack_d0 = puVar15;
                FUN_0043d574(1,PTR_s_navigation_datahandler_00588020,
                             PTR_s_D__01_workspace_s200_ap510b_iar__0058801c,
                             PTR_s_navigation_data_handler_00588018);
              }
              iVar9 = FUN_0043d0ce();
              if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
                uStack_d8 = (byte *)0x4650;
                compress_log_output(0x4800000,_DAT_00588310,_DAT_00588310,puVar15);
              }
              uStack_d8 = puVar12;
              puStack_d4 = puVar13;
              puStack_d0 = (undefined1 *)uVar14;
              navigation_send_type_8_shared(bVar1,7,uStack_c0,pbVar11);
              FUN_0043c0e4(iVar7,0x4674,0);
              uVar8 = osMutexRelease(*_DAT_005881b0);
              return uVar8;
            }
            FUN_00439be4(*(int *)(iVar7 + 0x20) + iVar7 + 0x24,pbVar2 + 0xe,puVar15);
            *(undefined1 **)(iVar7 + 0x20) = puVar15 + *(int *)(iVar7 + 0x20);
            puStack_d0 = *(undefined1 **)(iVar7 + 0x1c);
            puStack_d4 = *(undefined1 **)(iVar7 + 0x18);
            uStack_d8 = *(byte **)(iVar7 + 0xc);
            navigation_send_type_8_shared
                      (bVar1,0,*(undefined4 *)(iVar7 + 4),*(undefined4 *)(iVar7 + 8));
            iVar9 = _DAT_00588314;
            if (*(byte **)(iVar7 + 0x20) == pbVar11) {
              *(undefined1 *)(_DAT_00588314 + 0x18c) = 1;
              *(undefined4 *)(iVar9 + 400) = *(undefined4 *)(iVar7 + 8);
              *(undefined4 *)(iVar9 + 0x194) = *(undefined4 *)(iVar7 + 0xc);
              *(undefined4 *)(iVar9 + 0x198) = *(undefined4 *)(iVar7 + 0x10);
              *(char *)(iVar9 + 0x47ec) = (char)*(undefined4 *)(iVar7 + 0x14);
              FUN_0043c0e4(iVar9 + 0x19c,18000,0);
              FUN_00439be4(iVar9 + 0x19c,iVar7 + 0x24,*(undefined4 *)(iVar7 + 8));
              iVar9 = FUN_0043d0ce();
              if (iVar9 << 0x1e < 0) {
                uStack_cc = *(byte **)(iVar7 + 0xc);
                puStack_d0 = *(undefined1 **)(iVar7 + 8);
                puStack_d4 = PTR_s_mini_map_complete__single_fragme_00588318;
                uStack_d8 = (undefined1 *)0x386;
                FUN_0043d574(3,PTR_s_navigation_datahandler_00588020,
                             PTR_s_D__01_workspace_s200_ap510b_iar__0058801c,
                             PTR_s_navigation_data_handler_00588018);
              }
              iVar9 = FUN_0043d0ce();
              if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
                uStack_d8 = *(byte **)(iVar7 + 0xc);
                compress_log_output(0xc800000,PTR_s__navigation_datahandler_mini_map_0058831c,
                                    PTR_s__navigation_datahandler_mini_map_0058831c,
                                    *(undefined4 *)(iVar7 + 8));
              }
              FUN_0043c0e4(iVar7,0x4674,0);
              cVar5 = FUN_0045a570();
              if (((cVar5 == '\x01') && (iVar7 = FUN_00443484(), iVar7 == 1)) &&
                 (iVar7 = FUN_004434d0(8), iVar7 == 1)) {
                uStack_68 = 8;
                bStack_67 = bVar1;
                FUN_0045aaca(8,&uStack_68,6,200);
              }
            }
          }
          else {
            iVar7 = FUN_0043d0ce();
            if (iVar7 << 0x1e < 0) {
              puStack_d4 = PTR_s_navigation_data_handler_mini_map_00588320;
              uStack_d8 = (byte *)0x393;
              puStack_d0 = puVar13;
              FUN_0043d574(2,PTR_s_navigation_datahandler_00588020,
                           PTR_s_D__01_workspace_s200_ap510b_iar__0058801c,
                           PTR_s_navigation_data_handler_00588018);
            }
            iVar7 = FUN_0043d0ce();
            if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
              compress_log_output(0x8400000,PTR_s__navigation_datahandler_navigati_00588324,
                                  PTR_s__navigation_datahandler_navigati_00588324,puVar13);
            }
            uStack_d8 = puVar12;
            puStack_d4 = puVar13;
            puStack_d0 = (undefined1 *)uVar14;
            navigation_send_type_8_shared(bVar1,7,uStack_c0,pbVar11);
          }
        }
        else if (((*(undefined1 **)(_DAT_00588308 + 4) == uStack_c0) &&
                 ((*(byte **)(_DAT_00588308 + 8) == pbVar11 &&
                  (*(undefined1 **)(_DAT_00588308 + 0xc) == puVar12)))) &&
                (*(undefined1 **)(_DAT_00588308 + 0x18) == puVar13 + -1)) {
          *(undefined1 **)(_DAT_00588308 + 0x18) = puVar13;
          if (puVar15 + *(int *)(iVar7 + 0x20) < (undefined1 *)0x4651) {
            FUN_00439be4(*(int *)(iVar7 + 0x20) + iVar7 + 0x24,pbVar2 + 0xe,puVar15);
            *(undefined1 **)(iVar7 + 0x20) = puVar15 + *(int *)(iVar7 + 0x20);
            puStack_d4 = *(undefined1 **)(iVar7 + 0x18);
            uStack_d8 = *(byte **)(iVar7 + 0xc);
            puStack_d0 = (undefined1 *)uVar14;
            navigation_send_type_8_shared
                      (bVar1,0,*(undefined4 *)(iVar7 + 4),*(undefined4 *)(iVar7 + 8));
            iVar9 = FUN_0043d0ce();
            if (iVar9 << 0x1e < 0) {
              puStack_c8 = *(undefined1 **)(iVar7 + 0x20);
              uStack_cc = *(byte **)(iVar7 + 8);
              puStack_d0 = *(undefined1 **)(iVar7 + 0x18);
              puStack_d4 = PTR_s_received_mini_map_fragment__inde_00588338;
              uStack_d8 = (undefined1 *)0x3b7;
              FUN_0043d574(3,PTR_s_navigation_datahandler_00588020,
                           PTR_s_D__01_workspace_s200_ap510b_iar__0058801c,
                           PTR_s_navigation_data_handler_00588018);
            }
            iVar9 = FUN_0043d0ce();
            if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
              puStack_d4 = *(undefined1 **)(iVar7 + 0x20);
              uStack_d8 = *(byte **)(iVar7 + 8);
              compress_log_output(0xcc00000,PTR_s__navigation_datahandler_received_0058833c,
                                  PTR_s__navigation_datahandler_received_0058833c,
                                  *(undefined4 *)(iVar7 + 0x18));
            }
            if (*(int *)(iVar7 + 0x20) == *(int *)(iVar7 + 8)) {
              iVar9 = FUN_0043d0ce();
              if (iVar9 << 0x1e < 0) {
                puStack_d0 = *(undefined1 **)(iVar7 + 8);
                puStack_d4 = PTR_s_mini_map_complete__multi_fragmen_00588340;
                uStack_d8 = (undefined1 *)0x3b9;
                FUN_0043d574(3,PTR_s_navigation_datahandler_00588020,
                             PTR_s_D__01_workspace_s200_ap510b_iar__0058801c,
                             PTR_s_navigation_data_handler_00588018);
              }
              iVar9 = FUN_0043d0ce();
              if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
                compress_log_output(0xc400000,PTR_s__navigation_datahandler_mini_map_00588344,
                                    PTR_s__navigation_datahandler_mini_map_00588344,
                                    *(undefined4 *)(iVar7 + 8));
              }
              iVar9 = _DAT_00588314;
              *(undefined1 *)(_DAT_00588314 + 0x18c) = 1;
              *(undefined4 *)(iVar9 + 400) = *(undefined4 *)(iVar7 + 8);
              *(undefined4 *)(iVar9 + 0x194) = *(undefined4 *)(iVar7 + 0xc);
              *(undefined4 *)(iVar9 + 0x198) = *(undefined4 *)(iVar7 + 0x10);
              *(char *)(iVar9 + 0x47ec) = (char)*(undefined4 *)(iVar7 + 0x14);
              FUN_0043c0e4(iVar9 + 0x19c,18000,0);
              FUN_00439be4(iVar9 + 0x19c,iVar7 + 0x24,*(undefined4 *)(iVar7 + 8));
              FUN_0043c0e4(iVar7,0x4674,0);
              cVar5 = FUN_0045a570();
              if (((cVar5 == '\x01') && (iVar7 = FUN_00443484(), iVar7 == 1)) &&
                 (iVar7 = FUN_004434d0(8), iVar7 == 1)) {
                uStack_74 = 8;
                bStack_73 = bVar1;
                FUN_0045aaca(8,&uStack_74,6,200);
              }
            }
          }
          else {
            iVar9 = FUN_0043d0ce();
            if (iVar9 << 0x1e < 0) {
              puStack_d4 = PTR_s_over_mini_map_raw_data_size__cle_00588348;
              uStack_d8 = (byte *)0x3cc;
              FUN_0043d574(1,PTR_s_navigation_datahandler_00588020,
                           PTR_s_D__01_workspace_s200_ap510b_iar__0058801c,
                           PTR_s_navigation_data_handler_00588018);
            }
            iVar9 = FUN_0043d0ce();
            if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
              compress_log_output(0x4000000,PTR_s__navigation_datahandler_over_min_0058834c,
                                  PTR_s__navigation_datahandler_over_min_0058834c);
            }
            uStack_d8 = *(byte **)(iVar7 + 0xc);
            puStack_d4 = puVar13;
            puStack_d0 = (undefined1 *)uVar14;
            navigation_send_type_8_shared
                      (bVar1,7,*(undefined4 *)(iVar7 + 4),*(undefined4 *)(iVar7 + 8));
            FUN_0043c0e4(iVar7,0x4674,0);
          }
        }
        else {
          iVar9 = FUN_0043d0ce();
          if (iVar9 << 0x1e < 0) {
            puStack_d4 = PTR_s_navigation_data_handler_mini_map_00588328;
            uStack_d8 = (byte *)0x39e;
            FUN_0043d574(2,PTR_s_navigation_datahandler_00588020,
                         PTR_s_D__01_workspace_s200_ap510b_iar__0058801c,
                         PTR_s_navigation_data_handler_00588018);
          }
          iVar9 = FUN_0043d0ce();
          if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
            compress_log_output(0x8000000,PTR_s__navigation_datahandler_navigati_0058832c,
                                PTR_s__navigation_datahandler_navigati_0058832c);
          }
          iVar9 = FUN_0043d0ce();
          if (iVar9 << 0x1e < 0) {
            puStack_d0 = uStack_c0;
            puStack_d4 = PTR_s_session_id__d_total_size__d_comp_00588330;
            uStack_d8 = (byte *)0x3a0;
            uStack_cc = pbVar11;
            puStack_c8 = puVar12;
            puStack_c4 = puVar13;
            FUN_0043d574(2,PTR_s_navigation_datahandler_00588020,
                         PTR_s_D__01_workspace_s200_ap510b_iar__0058801c,
                         PTR_s_navigation_data_handler_00588018);
          }
          iVar9 = FUN_0043d0ce();
          if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
            uStack_d8 = pbVar11;
            puStack_d4 = puVar12;
            puStack_d0 = puVar13;
            compress_log_output(0x9000000,PTR_s__navigation_datahandler_session__00588334,
                                PTR_s__navigation_datahandler_session__00588334,uStack_c0);
          }
          uStack_d8 = *(byte **)(iVar7 + 0xc);
          puStack_d4 = puVar13;
          puStack_d0 = (undefined1 *)uVar14;
          navigation_send_type_8_shared
                    (bVar1,7,*(undefined4 *)(iVar7 + 4),*(undefined4 *)(iVar7 + 8));
          FUN_0043c0e4(iVar7,0x4674,0);
        }
        uVar8 = osMutexRelease(*_DAT_005881b0);
      }
      else if (uVar8 == 9) {
        uStack_c0 = *(undefined1 **)(pbVar2 + 4);
        pbVar11 = *(byte **)(pbVar2 + 8);
        puVar12 = *(undefined1 **)(pbVar2 + 0xc);
        puVar13 = *(undefined1 **)(pbVar2 + 0x10);
        uVar14 = *(undefined4 *)(pbVar2 + 0x14);
        osMutexAcquire(*_DAT_005881b0,0xffffffff);
        iVar7 = _DAT_00588350;
        if ((*(int *)(_DAT_00588350 + 0x18) == 0) && (*(int *)(_DAT_00588350 + 0x10) == 0)) {
          if (*(int *)(pbVar2 + 0x10) == 0) {
            *(undefined4 *)(_DAT_00588350 + 4) = *(undefined4 *)(pbVar2 + 4);
            *(undefined4 *)(iVar7 + 8) = *(undefined4 *)(pbVar2 + 8);
            *(undefined4 *)(iVar7 + 0xc) = *(undefined4 *)(pbVar2 + 0xc);
            *(undefined4 *)(iVar7 + 0x10) = *(undefined4 *)(pbVar2 + 0x10);
            FUN_00439be4(*(int *)(iVar7 + 0x18) + iVar7 + 0x1c,pbVar2 + 0x1a,
                         *(undefined2 *)(pbVar2 + 0x18));
            *(uint *)(iVar7 + 0x18) = *(int *)(iVar7 + 0x18) + (uint)*(ushort *)(pbVar2 + 0x18);
            puStack_d0 = *(undefined1 **)(iVar7 + 0x14);
            puStack_d4 = *(undefined1 **)(iVar7 + 0x10);
            uStack_d8 = *(byte **)(iVar7 + 0xc);
            navigation_send_type_9_shared
                      (bVar1,0,*(undefined4 *)(iVar7 + 4),*(undefined4 *)(iVar7 + 8));
            iVar9 = _DAT_00588314;
            if (*(byte **)(iVar7 + 0x18) == pbVar11) {
              *(undefined1 *)(_DAT_00588314 + 0x47ed) = 1;
              *(undefined4 *)(iVar9 + 0x47f4) = *(undefined4 *)(iVar7 + 0xc);
              *(undefined4 *)(iVar9 + 0x47f0) = *(undefined4 *)(iVar7 + 8);
              FUN_00439be4(iVar9 + 0x47f8,iVar7 + 0x1c,*(undefined4 *)(iVar7 + 8));
              FUN_0043c0e4(iVar7,0xea7c,0);
              cVar5 = FUN_0045a570();
              if (((cVar5 == '\x01') && (iVar7 = FUN_00443484(), iVar7 == 1)) &&
                 (iVar7 = FUN_004434d0(8), iVar7 == 1)) {
                uStack_80 = 9;
                bStack_7f = bVar1;
                FUN_0045aaca(8,&uStack_80,6,200);
              }
            }
          }
          else {
            iVar7 = FUN_0043d0ce();
            if (iVar7 << 0x1e < 0) {
              puStack_d4 = PTR_s_navigation_data_handler_receive_m_00588354;
              uStack_d8 = (byte *)0x40a;
              FUN_0043d574(2,PTR_s_navigation_datahandler_00588020,
                           PTR_s_D__01_workspace_s200_ap510b_iar__0058801c,
                           PTR_s_navigation_data_handler_00588018);
            }
            iVar7 = FUN_0043d0ce();
            if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
              compress_log_output(0x8000000,PTR_s__navigation_datahandler_navigati_00588358,
                                  PTR_s__navigation_datahandler_navigati_00588358);
            }
            iVar7 = FUN_0043d0ce();
            if (iVar7 << 0x1e < 0) {
              puStack_d0 = uStack_c0;
              puStack_d4 = PTR_s_max_map_session_id____d_max_map__0058835c;
              uStack_d8 = (byte *)0x40c;
              uStack_cc = pbVar11;
              puStack_c8 = puVar12;
              puStack_c4 = puVar13;
              FUN_0043d574(2,PTR_s_navigation_datahandler_00588020,
                           PTR_s_D__01_workspace_s200_ap510b_iar__0058801c,
                           PTR_s_navigation_data_handler_00588018);
            }
            iVar7 = FUN_0043d0ce();
            if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
              uStack_d8 = pbVar11;
              puStack_d4 = puVar12;
              puStack_d0 = puVar13;
              compress_log_output(0x9000000,PTR_s__navigation_datahandler_max_map__00588360,
                                  PTR_s__navigation_datahandler_max_map__00588360,uStack_c0);
            }
            uStack_d8 = puVar12;
            puStack_d4 = puVar13;
            puStack_d0 = (undefined1 *)uVar14;
            navigation_send_type_9_shared(bVar1,7,uStack_c0,pbVar11);
          }
        }
        else if ((*(undefined1 **)(_DAT_00588350 + 4) == uStack_c0) &&
                (((*(byte **)(_DAT_00588350 + 8) == pbVar11 &&
                  (*(undefined1 **)(_DAT_00588350 + 0xc) == puVar12)) &&
                 (*(undefined1 **)(_DAT_00588350 + 0x10) == puVar13 + -1)))) {
          *(undefined4 *)(_DAT_00588350 + 0x10) = *(undefined4 *)(pbVar2 + 0x10);
          if (*(int *)(iVar7 + 0x18) + (uint)*(ushort *)(pbVar2 + 0x18) < 0xea61) {
            FUN_00439be4(*(int *)(iVar7 + 0x18) + iVar7 + 0x1c,pbVar2 + 0x1a,
                         *(undefined2 *)(pbVar2 + 0x18));
            *(uint *)(iVar7 + 0x18) = *(int *)(iVar7 + 0x18) + (uint)*(ushort *)(pbVar2 + 0x18);
            puStack_d4 = *(undefined1 **)(iVar7 + 0x10);
            uStack_d8 = *(byte **)(iVar7 + 0xc);
            puStack_d0 = (undefined1 *)uVar14;
            navigation_send_type_9_shared
                      (bVar1,0,*(undefined4 *)(iVar7 + 4),*(undefined4 *)(iVar7 + 8));
            iVar9 = FUN_0043d0ce();
            if (iVar9 << 0x1e < 0) {
              uStack_cc = *(byte **)(iVar7 + 8);
              puStack_d0 = *(undefined1 **)(iVar7 + 0x10);
              puStack_d4 = PTR_s_received_max_map_data_____curren_00588364;
              uStack_d8 = (undefined1 *)0x430;
              FUN_0043d574(3,PTR_s_navigation_datahandler_00588370,
                           PTR_s_D__01_workspace_s200_ap510b_iar__0058836c,
                           PTR_s_navigation_data_handler_00588368);
            }
            iVar9 = FUN_0043d0ce();
            if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
              uStack_d8 = *(byte **)(iVar7 + 8);
              compress_log_output(0xc800000,PTR_s__navigation_datahandler_received_00588374,
                                  PTR_s__navigation_datahandler_received_00588374,
                                  *(undefined4 *)(iVar7 + 0x10));
            }
            if (*(int *)(iVar7 + 0x18) == *(int *)(iVar7 + 8)) {
              iVar9 = FUN_0043d0ce();
              if (iVar9 << 0x1e < 0) {
                puStack_d0 = *(undefined1 **)(iVar7 + 8);
                puStack_d4 = PTR_s_received_all_map_data______total_00588378;
                uStack_d8 = (undefined1 *)0x433;
                FUN_0043d574(3,PTR_s_navigation_datahandler_00588370,
                             PTR_s_D__01_workspace_s200_ap510b_iar__0058836c,
                             PTR_s_navigation_data_handler_00588368);
              }
              iVar9 = FUN_0043d0ce();
              if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
                compress_log_output(0xc400000,PTR_s__navigation_datahandler_received_0058837c,
                                    PTR_s__navigation_datahandler_received_0058837c,
                                    *(undefined4 *)(iVar7 + 8));
              }
              iVar9 = _DAT_00588314;
              *(undefined1 *)(_DAT_00588314 + 0x47ed) = 1;
              *(undefined4 *)(iVar9 + 0x47f4) = *(undefined4 *)(iVar7 + 0xc);
              *(undefined4 *)(iVar9 + 0x47f0) = *(undefined4 *)(iVar7 + 8);
              FUN_00439be4(iVar9 + 0x47f8,iVar7 + 0x1c,*(undefined4 *)(iVar7 + 8));
              FUN_0043c0e4(iVar7,0xea7c,0);
              cVar5 = FUN_0045a570();
              if (((cVar5 == '\x01') && (iVar7 = FUN_00443484(), iVar7 == 1)) &&
                 (iVar7 = FUN_004434d0(8), iVar7 == 1)) {
                uStack_8c = 9;
                bStack_8b = bVar1;
                FUN_0045aaca(8,&uStack_8c,6,200);
              }
            }
          }
          else {
            iVar9 = FUN_0043d0ce();
            if (iVar9 << 0x1e < 0) {
              puStack_d4 = PTR_s_over_max_map_raw_data_size_clear_00588380;
              uStack_d8 = (byte *)0x449;
              FUN_0043d574(1,PTR_s_navigation_datahandler_00588370,
                           PTR_s_D__01_workspace_s200_ap510b_iar__0058836c,
                           PTR_s_navigation_data_handler_00588368);
            }
            iVar9 = FUN_0043d0ce();
            if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
              compress_log_output(0x4000000,PTR_s__navigation_datahandler_over_max_00588384,
                                  PTR_s__navigation_datahandler_over_max_00588384);
            }
            uStack_d8 = *(byte **)(iVar7 + 0xc);
            puStack_d4 = puVar13;
            puStack_d0 = (undefined1 *)uVar14;
            navigation_send_type_9_shared
                      (bVar1,7,*(undefined4 *)(iVar7 + 4),*(undefined4 *)(iVar7 + 8));
            FUN_0043c0e4(iVar7,0xea7c,0);
          }
        }
        else {
          FUN_0043c0e4(_DAT_00588350,0xea7c,0);
          iVar9 = FUN_0043d0ce();
          if (iVar9 << 0x1e < 0) {
            puStack_d4 = PTR_s_navigation_data_handler_receive_m_00588354;
            uStack_d8 = (byte *)0x41b;
            FUN_0043d574(2,PTR_s_navigation_datahandler_00588020,
                         PTR_s_D__01_workspace_s200_ap510b_iar__0058801c,
                         PTR_s_navigation_data_handler_00588018);
          }
          iVar9 = FUN_0043d0ce();
          if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
            compress_log_output(0x8000000,PTR_s__navigation_datahandler_navigati_00588358,
                                PTR_s__navigation_datahandler_navigati_00588358);
          }
          uStack_d8 = *(byte **)(iVar7 + 0xc);
          puStack_d4 = puVar13;
          puStack_d0 = (undefined1 *)uVar14;
          navigation_send_type_9_shared
                    (bVar1,7,*(undefined4 *)(iVar7 + 4),*(undefined4 *)(iVar7 + 8));
        }
        uVar8 = osMutexRelease(*puVar3);
      }
      else if (uVar8 == 10) {
        bVar6 = FUN_0045a570();
        uVar8 = (uint)bVar6;
        if (((uVar8 == 1) && (uVar8 = FUN_00443484(), uVar8 == 1)) &&
           (uVar8 = FUN_004434d0(8), uVar8 == 1)) {
          uStack_98 = 10;
          bStack_97 = bVar1;
          uVar8 = FUN_00464bb2(8,&uStack_98,6,0);
        }
      }
      else if (uVar8 == 0xb) {
        bVar6 = FUN_0045a570();
        uVar8 = (uint)bVar6;
        if (((uVar8 == 1) && (uVar8 = FUN_00443484(), uVar8 == 1)) &&
           (uVar8 = FUN_004434d0(8), uVar8 == 1)) {
          uStack_a4 = 0xb;
          bStack_a3 = bVar1;
          uVar8 = FUN_00464bb2(8,&uStack_a4,6,0);
        }
      }
      else if (uVar8 == 0xc) {
        bVar6 = FUN_0045a570();
        uVar8 = (uint)bVar6;
        if (((uVar8 == 1) && (uVar8 = FUN_00443484(), uVar8 == 1)) &&
           (uVar8 = FUN_004434d0(8), uVar8 == 1)) {
          FUN_0043c0e4(&uStack_cc,10,0);
          uStack_cc._0_2_ = CONCAT11(bVar1,0xc);
          uVar8 = FUN_00464bb2(8,&uStack_cc,6,0);
        }
      }
    }
  }
  return uVar8;
}

