
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_004955b4(int param_1,short param_2,undefined4 *param_3)

{
  byte bVar1;
  bool bVar2;
  char cVar3;
  int iVar4;
  undefined4 uVar5;
  int iVar6;
  int iVar7;
  undefined4 *puVar8;
  int iVar9;
  int iStack_d98;
  undefined *puStack_d94;
  undefined4 *puStack_d90;
  int iStack_d8c;
  undefined1 auStack_d88 [12];
  undefined4 *puStack_d7c;
  undefined1 auStack_d78 [28];
  undefined1 auStack_d5c [2068];
  undefined1 auStack_548 [1324];
  
  iVar4 = FUN_0043d0ce();
  if (iVar4 << 0x1e < 0) {
    puStack_d94 = PTR_s_evenhub_ui_page_create_00495e6c;
    iStack_d98 = 0x3fc;
    FUN_0043d574(4,PTR_s_evenhub_ui_00495e70,DAT_004961a0,_DAT_0049619c);
  }
  iVar4 = FUN_0043d0ce();
  if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
    compress_log_output(0x10000000,PTR_s__evenhub_ui_evenhub_ui_page_crea_00495e74,
                        PTR_s__evenhub_ui_evenhub_ui_page_crea_00495e74);
  }
  iVar4 = _DAT_004961a8;
  if (param_3 == (undefined4 *)0x0) {
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      puStack_d94 = PTR_s_evenhub_ui_page_create_manager_c_00495e78;
      iStack_d98 = 0x400;
      FUN_0043d574(1,PTR_s_evenhub_ui_00495e70,DAT_004961a0,_DAT_0049619c);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__evenhub_ui_evenhub_ui_page_crea_00495e7c,
                          PTR_s__evenhub_ui_evenhub_ui_page_crea_00495e7c);
    }
    uVar5 = 0xffffffff;
  }
  else if ((param_1 == 0) || (param_2 == 0)) {
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      puStack_d94 = PTR_s_evenhub_ui_page_create_data_is_N_00495e80;
      iStack_d98 = 0x405;
      FUN_0043d574(1,PTR_s_evenhub_ui_00495e70,DAT_004961a0,_DAT_0049619c);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x4000000,_DAT_004961a4,_DAT_004961a4);
    }
    uVar5 = 0xffffffff;
  }
  else {
    FUN_0043c0e4(_DAT_004961a8,0x3758,0);
    FUN_0048f49c(&iStack_d98,param_1,param_2);
    FUN_00439c04(auStack_d88,&iStack_d98,0x10);
    cVar3 = FUN_00490120(auStack_d88,PTR_DAT_004961ac,iVar4);
    if (cVar3 == '\0') {
      iVar6 = FUN_0043d0ce();
      if (iVar6 << 0x1e < 0) {
        puStack_d90 = (undefined4 *)PTR_s__none__004961b0;
        if (puStack_d7c != (undefined4 *)0x0) {
          puStack_d90 = puStack_d7c;
        }
        puStack_d94 = PTR_s_evenhub_protobuf_decode_failed____004961b4;
        iStack_d98 = 0x40d;
        FUN_0043d574(1,PTR_s_evenhub_ui_00495e70,DAT_004961a0,_DAT_0049619c);
      }
      iVar6 = FUN_0043d0ce();
      if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
        puVar8 = (undefined4 *)PTR_s__none__004961b0;
        if (puStack_d7c != (undefined4 *)0x0) {
          puVar8 = puStack_d7c;
        }
        compress_log_output(0x4400000,PTR_s__evenhub_ui_evenhub_protobuf_dec_004961b8,
                            PTR_s__evenhub_ui_evenhub_protobuf_dec_004961b8,puVar8);
      }
      FUN_004d9c86(8,*(undefined1 *)(iVar4 + 1),8,7);
      uVar5 = 0xffffffff;
    }
    else {
      iVar6 = FUN_00493ab6(param_3,iVar4 + 4);
      if (iVar6 == 0) {
        iVar6 = FUN_0043d0ce();
        if (iVar6 << 0x1e < 0) {
          puStack_d90 = (undefined4 *)param_3[3];
          puStack_d94 = PTR_s_evenhub_ui_page_create__containe_004961c4;
          iStack_d98 = 0x41e;
          FUN_0043d574(3,PTR_s_evenhub_ui_00495e70,DAT_004961a0,_DAT_0049619c);
        }
        iVar6 = FUN_0043d0ce();
        if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
          compress_log_output(0xc400000,PTR_s__evenhub_ui_evenhub_ui_page_crea_004961c8,
                              PTR_s__evenhub_ui_evenhub_ui_page_crea_004961c8,param_3[3]);
        }
        iVar6 = FUN_0043d0ce();
        if (iVar6 << 0x1e < 0) {
          puStack_d94 = PTR_s_evenhub_ui_page_create__traversi_004961cc;
          iStack_d98 = 0x421;
          FUN_0043d574(4,PTR_s_evenhub_ui_00495e70,DAT_004961a0,_DAT_0049619c);
        }
        iVar6 = FUN_0043d0ce();
        if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
          compress_log_output(0x10000000,PTR_s__evenhub_ui_evenhub_ui_page_crea_004961d0,
                              PTR_s__evenhub_ui_evenhub_ui_page_crea_004961d0);
        }
        FUN_00493ee6(param_3,PTR_FUN_004940e8_1_004961d4,0);
        iVar6 = FUN_0043d0ce();
        if (iVar6 << 0x1e < 0) {
          puStack_d94 = PTR_s_evenhub_ui_page_create__creating_004961d8;
          iStack_d98 = 0x425;
          FUN_0043d574(4,PTR_s_evenhub_ui_00495e70,DAT_004961a0,_DAT_0049619c);
        }
        iVar6 = FUN_0043d0ce();
        if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
          compress_log_output(0x10000000,PTR_s__evenhub_ui_evenhub_ui_page_crea_004961dc,
                              PTR_s__evenhub_ui_evenhub_ui_page_crea_004961dc);
        }
        bVar2 = false;
        for (iVar6 = param_3[1]; iVar6 != 0; iVar6 = *(int *)(iVar6 + 4)) {
          bVar1 = *(byte *)(iVar6 + 8);
          if (bVar1 == 0) {
            iVar9 = *(int *)(iVar6 + 0xc);
            iVar7 = FUN_0043d0ce();
            if (iVar7 << 0x1e < 0) {
              iStack_d8c = iVar9 + 0x24;
              puStack_d90 = *(undefined4 **)(iVar9 + 0x20);
              puStack_d94 = PTR_s_evenhub_ui_page_create__creating_004963f4;
              iStack_d98 = 0x42e;
              FUN_0043d574(4,PTR_s_evenhub_ui_00495e70,DAT_004961a0,_DAT_0049619c);
            }
            iVar7 = FUN_0043d0ce();
            if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
              iStack_d98 = iVar9 + 0x24;
              compress_log_output(0x10800000,PTR_s__evenhub_ui_evenhub_ui_page_crea_004963f8,
                                  PTR_s__evenhub_ui_evenhub_ui_page_crea_004963f8,
                                  *(undefined4 *)(iVar9 + 0x20));
            }
            FUN_0043c0e4(auStack_548,0x52c,0);
            FUN_00495e84(iVar9,auStack_548);
            puVar8 = (undefined4 *)
                     FUN_004dd510(*param_3,auStack_548,PTR_FUN_004949c0_1_004963fc,param_3);
            if (puVar8 == (undefined4 *)0x0) {
              iVar6 = FUN_0043d0ce();
              if (iVar6 << 0x1e < 0) {
                puStack_d94 = PTR_s_evenhub_ui_page_create__failed_t_0049641c;
                iStack_d98 = 0x457;
                FUN_0043d574(1,PTR_s_evenhub_ui_00495e70,DAT_004961a0,_DAT_0049619c);
              }
              iVar6 = FUN_0043d0ce();
              if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
                compress_log_output(0x4000000,PTR_s__evenhub_ui_evenhub_ui_page_crea_00496420,
                                    PTR_s__evenhub_ui_evenhub_ui_page_crea_00496420);
              }
              FUN_004d9c86(8,*(undefined1 *)(iVar4 + 1),8,7);
              return 0xfffffffd;
            }
            *(undefined4 **)(iVar6 + 0x10) = puVar8;
            iVar7 = FUN_0043d0ce();
            if (iVar7 << 0x1e < 0) {
              puStack_d94 = PTR_s_evenhub_ui_page_create__List_con_00496400;
              iStack_d98 = 0x441;
              puStack_d90 = puVar8;
              FUN_0043d574(3,PTR_s_evenhub_ui_00495e70,DAT_004961a0,_DAT_0049619c);
            }
            iVar7 = FUN_0043d0ce();
            if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
              compress_log_output(0xc400000,PTR_s__evenhub_ui_evenhub_ui_page_crea_00496404,
                                  PTR_s__evenhub_ui_evenhub_ui_page_crea_00496404,puVar8);
            }
            if ((*(int *)(iVar9 + 0x548) == 1) && (!bVar2)) {
              puStack_d94 = (undefined *)0x0;
              iStack_d98 = iVar9 + 0x24;
              puStack_d90 = param_3;
              iVar7 = FUN_004942a4(param_3,puVar8,PTR_FUN_00495f9a_1_00496408,
                                   *(undefined4 *)(iVar9 + 0x20));
              if (iVar7 == 0) {
                bVar2 = true;
                iVar7 = FUN_0043d0ce();
                if (iVar7 << 0x1e < 0) {
                  puStack_d94 = PTR_s_evenhub_ui_page_create__List_con_0049640c;
                  iStack_d98 = 0x451;
                  FUN_0043d574(3,PTR_s_evenhub_ui_00495e70,DAT_004961a0,_DAT_0049619c);
                }
                iVar7 = FUN_0043d0ce();
                if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
                  compress_log_output(0xc000000,PTR_s__evenhub_ui_evenhub_ui_page_crea_00496410,
                                      PTR_s__evenhub_ui_evenhub_ui_page_crea_00496410);
                }
              }
              else {
                iVar7 = FUN_0043d0ce();
                if (iVar7 << 0x1e < 0) {
                  puStack_d94 = PTR_s_evenhub_ui_page_create__failed_t_00496414;
                  iStack_d98 = 0x453;
                  FUN_0043d574(1,PTR_s_evenhub_ui_00495e70,DAT_004961a0,_DAT_0049619c);
                }
                iVar7 = FUN_0043d0ce();
                if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
                  compress_log_output(0x4000000,PTR_s__evenhub_ui_evenhub_ui_page_crea_00496418,
                                      PTR_s__evenhub_ui_evenhub_ui_page_crea_00496418);
                }
              }
            }
          }
          else if (bVar1 == 2) {
            iVar9 = *(int *)(iVar6 + 0xc);
            iVar7 = FUN_0043d0ce();
            if (iVar7 << 0x1e < 0) {
              iStack_d8c = iVar9 + 0x14;
              puStack_d90 = *(undefined4 **)(iVar9 + 0x10);
              puStack_d94 = PTR_s_evenhub_ui_page_create__creating_00495e54;
              iStack_d98 = 0x496;
              FUN_0043d574(4,PTR_s_evenhub_ui_00495e70,DAT_004961a0,_DAT_0049619c);
            }
            iVar7 = FUN_0043d0ce();
            if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
              iStack_d98 = iVar9 + 0x14;
              compress_log_output(0x10800000,PTR_s__evenhub_ui_evenhub_ui_page_crea_00495e58,
                                  PTR_s__evenhub_ui_evenhub_ui_page_crea_00495e58,
                                  *(undefined4 *)(iVar9 + 0x10));
            }
            FUN_0043c0e4(auStack_d78,0x1c,0);
            FUN_00495f6a(iVar9,auStack_d78);
            puVar8 = (undefined4 *)FUN_004dbede(*param_3,auStack_d78);
            if (puVar8 == (undefined4 *)0x0) {
              iVar6 = FUN_0043d0ce();
              if (iVar6 << 0x1e < 0) {
                puStack_d94 = PTR_s_evenhub_ui_page_create__failed_t_00495e5c;
                iStack_d98 = 0x4ab;
                FUN_0043d574(1,PTR_s_evenhub_ui_00495e70,DAT_004961a0,_DAT_0049619c);
              }
              iVar6 = FUN_0043d0ce();
              if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
                compress_log_output(0x4000000,PTR_s__evenhub_ui_evenhub_ui_page_crea_00495e60,
                                    PTR_s__evenhub_ui_evenhub_ui_page_crea_00495e60);
              }
              FUN_004d9c86(8,*(undefined1 *)(iVar4 + 1),8,7);
              return 0xfffffffd;
            }
            *(undefined4 **)(iVar6 + 0x10) = puVar8;
            iVar7 = FUN_0043d0ce();
            if (iVar7 << 0x1e < 0) {
              puStack_d94 = PTR_s_evenhub_ui_page_create__Image_co_004963ec;
              iStack_d98 = 0x4a7;
              puStack_d90 = puVar8;
              FUN_0043d574(3,PTR_s_evenhub_ui_00495e70,DAT_004961a0,_DAT_0049619c);
            }
            iVar7 = FUN_0043d0ce();
            if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
              compress_log_output(0xc400000,PTR_s__evenhub_ui_evenhub_ui_page_crea_004963f0,
                                  PTR_s__evenhub_ui_evenhub_ui_page_crea_004963f0,puVar8);
            }
          }
          else if (bVar1 < 2) {
            iVar9 = *(int *)(iVar6 + 0xc);
            iVar7 = FUN_0043d0ce();
            if (iVar7 << 0x1e < 0) {
              iStack_d8c = iVar9 + 0x24;
              puStack_d90 = *(undefined4 **)(iVar9 + 0x20);
              puStack_d94 = PTR_s_evenhub_ui_page_create__creating_00496424;
              iStack_d98 = 0x462;
              FUN_0043d574(4,PTR_s_evenhub_ui_00495e70,DAT_004961a0,_DAT_0049619c);
            }
            iVar7 = FUN_0043d0ce();
            if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
              iStack_d98 = iVar9 + 0x24;
              compress_log_output(0x10800000,PTR_s__evenhub_ui_evenhub_ui_page_crea_00496428,
                                  PTR_s__evenhub_ui_evenhub_ui_page_crea_00496428,
                                  *(undefined4 *)(iVar9 + 0x20));
            }
            FUN_0043c0e4(auStack_d5c,0x814,0);
            FUN_00495f1a(iVar9,auStack_d5c);
            puVar8 = (undefined4 *)
                     FUN_004dee96(*param_3,auStack_d5c,PTR_FUN_00494a78_1_0049642c,param_3);
            if (puVar8 == (undefined4 *)0x0) {
              iVar6 = FUN_0043d0ce();
              if (iVar6 << 0x1e < 0) {
                puStack_d94 = PTR_s_evenhub_ui_page_create__failed_t_00495e4c;
                iStack_d98 = 0x48b;
                FUN_0043d574(1,PTR_s_evenhub_ui_00495e70,DAT_004961a0,_DAT_0049619c);
              }
              iVar6 = FUN_0043d0ce();
              if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
                compress_log_output(0x4000000,PTR_s__evenhub_ui_evenhub_ui_page_crea_00495e50,
                                    PTR_s__evenhub_ui_evenhub_ui_page_crea_00495e50);
              }
              FUN_004d9c86(8,*(undefined1 *)(iVar4 + 1),8,7);
              return 0xfffffffd;
            }
            *(undefined4 **)(iVar6 + 0x10) = puVar8;
            iVar7 = FUN_0043d0ce();
            if (iVar7 << 0x1e < 0) {
              puStack_d94 = PTR_s_evenhub_ui_page_create__Text_con_004964cc;
              iStack_d98 = 0x475;
              puStack_d90 = puVar8;
              FUN_0043d574(3,PTR_s_evenhub_ui_00495e70,DAT_004961a0,_DAT_0049619c);
            }
            iVar7 = FUN_0043d0ce();
            if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
              compress_log_output(0xc400000,PTR_s__evenhub_ui_evenhub_ui_page_crea_004964d0,
                                  PTR_s__evenhub_ui_evenhub_ui_page_crea_004964d0,puVar8);
            }
            if ((*(int *)(iVar9 + 0x34) == 1) && (!bVar2)) {
              puStack_d94 = (undefined *)0x1;
              iStack_d98 = iVar9 + 0x24;
              puStack_d90 = param_3;
              iVar7 = FUN_004942a4(param_3,puVar8,PTR_FUN_004961e4_1_004964d4,
                                   *(undefined4 *)(iVar9 + 0x20));
              if (iVar7 == 0) {
                bVar2 = true;
                iVar7 = FUN_0043d0ce();
                if (iVar7 << 0x1e < 0) {
                  puStack_d94 = PTR_s_evenhub_ui_page_create__Text_con_004964d8;
                  iStack_d98 = 0x485;
                  FUN_0043d574(3,PTR_s_evenhub_ui_00495e70,DAT_004961a0,_DAT_0049619c);
                }
                iVar7 = FUN_0043d0ce();
                if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
                  compress_log_output(0xc000000,PTR_s__evenhub_ui_evenhub_ui_page_crea_004964dc,
                                      PTR_s__evenhub_ui_evenhub_ui_page_crea_004964dc);
                }
              }
              else {
                iVar7 = FUN_0043d0ce();
                if (iVar7 << 0x1e < 0) {
                  puStack_d94 = PTR_s_evenhub_ui_page_create__failed_t_00495e44;
                  iStack_d98 = 0x487;
                  FUN_0043d574(1,PTR_s_evenhub_ui_00495e70,DAT_004961a0,_DAT_0049619c);
                }
                iVar7 = FUN_0043d0ce();
                if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
                  compress_log_output(0x4000000,PTR_s__evenhub_ui_evenhub_ui_page_crea_00495e48,
                                      PTR_s__evenhub_ui_evenhub_ui_page_crea_00495e48);
                }
              }
            }
          }
          else {
            iVar7 = FUN_0043d0ce();
            if (iVar7 << 0x1e < 0) {
              puStack_d90 = (undefined4 *)(uint)*(byte *)(iVar6 + 8);
              puStack_d94 = PTR_s_evenhub_ui_page_create__unknown_c_004961e0;
              iStack_d98 = 0x4b4;
              FUN_0043d574(2,PTR_s_evenhub_ui_00495e70,DAT_004961a0,_DAT_0049619c);
            }
            iVar7 = FUN_0043d0ce();
            if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
              compress_log_output(0x8400000,PTR_s__evenhub_ui_evenhub_ui_page_crea_004963e8,
                                  PTR_s__evenhub_ui_evenhub_ui_page_crea_004963e8,
                                  *(undefined1 *)(iVar6 + 8));
            }
          }
        }
        if (!bVar2) {
          iVar6 = FUN_0043d0ce();
          if (iVar6 << 0x1e < 0) {
            puStack_d94 = PTR_s_evenhub_ui_page_create__no_conta_00495e64;
            iStack_d98 = 0x4bc;
            FUN_0043d574(2,PTR_s_evenhub_ui_00495e70,DAT_004961a0,_DAT_0049619c);
          }
          iVar6 = FUN_0043d0ce();
          if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
            compress_log_output(0x8000000,PTR_s__evenhub_ui_evenhub_ui_page_crea_00495e68,
                                PTR_s__evenhub_ui_evenhub_ui_page_crea_00495e68);
          }
        }
        FUN_004d9c86(8,*(undefined1 *)(iVar4 + 1),8,6);
        uVar5 = 0;
      }
      else {
        iVar6 = FUN_0043d0ce();
        if (iVar6 << 0x1e < 0) {
          puStack_d94 = PTR_s_evenhub_ui_page_create__create_c_004961bc;
          iStack_d98 = 0x417;
          FUN_0043d574(1,PTR_s_evenhub_ui_00495e70,DAT_004961a0,_DAT_0049619c);
        }
        iVar6 = FUN_0043d0ce();
        if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
          compress_log_output(0x4000000,PTR_s__evenhub_ui_evenhub_ui_page_crea_004961c0,
                              PTR_s__evenhub_ui_evenhub_ui_page_crea_004961c0);
        }
        FUN_004d9c86(8,*(undefined1 *)(iVar4 + 1),8,7);
        uVar5 = 0xffffffff;
      }
    }
  }
  return uVar5;
}

