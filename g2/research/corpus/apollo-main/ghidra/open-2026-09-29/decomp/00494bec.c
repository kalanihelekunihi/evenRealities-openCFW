
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_00494bec(int param_1,short param_2,undefined4 *param_3)

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
    puStack_d94 = PTR_s_evenhub_ui_page_create_004954ec;
    iStack_d98 = 0x32c;
    FUN_0043d574(4,PTR_s_evenhub_ui_004954f8,PTR_s_D__01_workspace_s200_ap510b_iar__004954f4,
                 PTR_s_evenhub_ui_page_create_004954f0);
  }
  iVar4 = FUN_0043d0ce();
  if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
    compress_log_output(0x10000000,PTR_s__evenhub_ui_evenhub_ui_page_crea_004954fc,
                        PTR_s__evenhub_ui_evenhub_ui_page_crea_004954fc);
  }
  puVar8 = _DAT_00495500;
  *_DAT_00495500 = 0;
  iVar4 = _DAT_00495514;
  if (param_3 == (undefined4 *)0x0) {
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      puStack_d94 = PTR_s_evenhub_ui_page_create_manager_c_00495504;
      iStack_d98 = 0x331;
      FUN_0043d574(1,PTR_s_evenhub_ui_004954f8,PTR_s_D__01_workspace_s200_ap510b_iar__004954f4,
                   PTR_s_evenhub_ui_page_create_004954f0);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__evenhub_ui_evenhub_ui_page_crea_00495508,
                          PTR_s__evenhub_ui_evenhub_ui_page_crea_00495508);
    }
    uVar5 = 0xffffffff;
  }
  else if ((param_1 == 0) || (param_2 == 0)) {
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      puStack_d94 = PTR_s_evenhub_ui_page_create_data_is_N_0049550c;
      iStack_d98 = 0x336;
      FUN_0043d574(1,PTR_s_evenhub_ui_004954f8,PTR_s_D__01_workspace_s200_ap510b_iar__004954f4,
                   PTR_s_evenhub_ui_page_create_004954f0);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__evenhub_ui_evenhub_ui_page_crea_00495510,
                          PTR_s__evenhub_ui_evenhub_ui_page_crea_00495510);
    }
    uVar5 = 0xffffffff;
  }
  else {
    FUN_0043c0e4(_DAT_00495514,0x3758,0);
    FUN_0048f49c(&iStack_d98,param_1,param_2);
    FUN_00439c04(auStack_d88,&iStack_d98,0x10);
    cVar3 = FUN_00490120(auStack_d88,PTR_DAT_00495518,iVar4);
    if (cVar3 == '\0') {
      iVar6 = FUN_0043d0ce();
      if (iVar6 << 0x1e < 0) {
        puStack_d90 = (undefined4 *)PTR_s__none__0049551c;
        if (puStack_d7c != (undefined4 *)0x0) {
          puStack_d90 = puStack_d7c;
        }
        puStack_d94 = PTR_s_evenhub_protobuf_decode_failed____00495520;
        iStack_d98 = 0x33e;
        FUN_0043d574(1,PTR_s_evenhub_ui_004954f8,PTR_s_D__01_workspace_s200_ap510b_iar__004954f4,
                     PTR_s_evenhub_ui_page_create_004954f0);
      }
      iVar6 = FUN_0043d0ce();
      if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
        puVar8 = (undefined4 *)PTR_s__none__0049551c;
        if (puStack_d7c != (undefined4 *)0x0) {
          puVar8 = puStack_d7c;
        }
        compress_log_output(0x4400000,PTR_s__evenhub_ui_evenhub_protobuf_dec_00495524,
                            PTR_s__evenhub_ui_evenhub_protobuf_dec_00495524,puVar8);
      }
      FUN_004d9c86(1,*(undefined1 *)(iVar4 + 1),4,3);
      uVar5 = 0xffffffff;
    }
    else {
      *puVar8 = *(undefined4 *)(iVar4 + 0x3754);
      iVar6 = FUN_0043d0ce();
      if (iVar6 << 0x1e < 0) {
        puStack_d90 = (undefined4 *)*puVar8;
        puStack_d94 = PTR_s_evenhub_ui_page_create__startup_w_00495528;
        iStack_d98 = 0x347;
        FUN_0043d574(3,PTR_s_evenhub_ui_004954f8,PTR_s_D__01_workspace_s200_ap510b_iar__004954f4,
                     PTR_s_evenhub_ui_page_create_004954f0);
      }
      iVar6 = FUN_0043d0ce();
      if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
        compress_log_output(0xc400000,PTR_s__evenhub_ui_evenhub_ui_page_crea_0049552c,
                            PTR_s__evenhub_ui_evenhub_ui_page_crea_0049552c,*puVar8);
      }
      iVar6 = FUN_00493bdc(param_3,iVar4 + 4);
      if (iVar6 == 0) {
        iVar6 = FUN_0043d0ce();
        if (iVar6 << 0x1e < 0) {
          puStack_d90 = (undefined4 *)param_3[3];
          puStack_d94 = PTR_s_evenhub_ui_page_create__containe_00495538;
          iStack_d98 = 0x351;
          FUN_0043d574(3,PTR_s_evenhub_ui_004954f8,PTR_s_D__01_workspace_s200_ap510b_iar__004954f4,
                       PTR_s_evenhub_ui_page_create_004954f0);
        }
        iVar6 = FUN_0043d0ce();
        if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
          compress_log_output(0xc400000,PTR_s__evenhub_ui_evenhub_ui_page_crea_0049553c,
                              PTR_s__evenhub_ui_evenhub_ui_page_crea_0049553c,param_3[3]);
        }
        iVar6 = FUN_0043d0ce();
        if (iVar6 << 0x1e < 0) {
          puStack_d94 = PTR_s_evenhub_ui_page_create__traversi_00495540;
          iStack_d98 = 0x354;
          FUN_0043d574(4,PTR_s_evenhub_ui_004954f8,PTR_s_D__01_workspace_s200_ap510b_iar__004954f4,
                       PTR_s_evenhub_ui_page_create_004954f0);
        }
        iVar6 = FUN_0043d0ce();
        if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
          compress_log_output(0x10000000,PTR_s__evenhub_ui_evenhub_ui_page_crea_00495544,
                              PTR_s__evenhub_ui_evenhub_ui_page_crea_00495544);
        }
        FUN_00493ee6(param_3,PTR_FUN_004940e8_1_00495548,0);
        iVar6 = FUN_0043d0ce();
        if (iVar6 << 0x1e < 0) {
          puStack_d94 = PTR_s_evenhub_ui_page_create__creating_0049554c;
          iStack_d98 = 0x358;
          FUN_0043d574(4,PTR_s_evenhub_ui_004954f8,PTR_s_D__01_workspace_s200_ap510b_iar__004954f4,
                       PTR_s_evenhub_ui_page_create_004954f0);
        }
        iVar6 = FUN_0043d0ce();
        if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
          compress_log_output(0x10000000,PTR_s__evenhub_ui_evenhub_ui_page_crea_00495550,
                              PTR_s__evenhub_ui_evenhub_ui_page_crea_00495550);
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
              puStack_d94 = PTR_s_evenhub_ui_page_create__creating_00495564;
              iStack_d98 = 0x361;
              FUN_0043d574(4,PTR_s_evenhub_ui_004954f8,
                           PTR_s_D__01_workspace_s200_ap510b_iar__004954f4,
                           PTR_s_evenhub_ui_page_create_004954f0);
            }
            iVar7 = FUN_0043d0ce();
            if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
              iStack_d98 = iVar9 + 0x24;
              compress_log_output(0x10800000,PTR_s__evenhub_ui_evenhub_ui_page_crea_00495568,
                                  PTR_s__evenhub_ui_evenhub_ui_page_crea_00495568,
                                  *(undefined4 *)(iVar9 + 0x20));
            }
            FUN_0043c0e4(auStack_548,0x52c,0);
            FUN_00495e84(iVar9,auStack_548);
            puVar8 = (undefined4 *)
                     FUN_004dd510(*param_3,auStack_548,PTR_FUN_004949c0_1_0049556c,param_3);
            if (puVar8 == (undefined4 *)0x0) {
              iVar6 = FUN_0043d0ce();
              if (iVar6 << 0x1e < 0) {
                puStack_d94 = PTR_s_evenhub_ui_page_create__failed_t_0049558c;
                iStack_d98 = 0x38a;
                FUN_0043d574(1,PTR_s_evenhub_ui_004954f8,
                             PTR_s_D__01_workspace_s200_ap510b_iar__004954f4,
                             PTR_s_evenhub_ui_page_create_004954f0);
              }
              iVar6 = FUN_0043d0ce();
              if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
                compress_log_output(0x4000000,PTR_s__evenhub_ui_evenhub_ui_page_crea_00495590,
                                    PTR_s__evenhub_ui_evenhub_ui_page_crea_00495590);
              }
              FUN_004d9c86(1,*(undefined1 *)(iVar4 + 1),4,1);
              return 0xfffffffd;
            }
            *(undefined4 **)(iVar6 + 0x10) = puVar8;
            iVar7 = FUN_0043d0ce();
            if (iVar7 << 0x1e < 0) {
              puStack_d94 = PTR_s_evenhub_ui_page_create__List_con_00495570;
              iStack_d98 = 0x374;
              puStack_d90 = puVar8;
              FUN_0043d574(3,PTR_s_evenhub_ui_004954f8,
                           PTR_s_D__01_workspace_s200_ap510b_iar__004954f4,
                           PTR_s_evenhub_ui_page_create_004954f0);
            }
            iVar7 = FUN_0043d0ce();
            if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
              compress_log_output(0xc400000,PTR_s__evenhub_ui_evenhub_ui_page_crea_00495574,
                                  PTR_s__evenhub_ui_evenhub_ui_page_crea_00495574,puVar8);
            }
            if ((*(int *)(iVar9 + 0x548) == 1) && (!bVar2)) {
              puStack_d94 = (undefined *)0x0;
              iStack_d98 = iVar9 + 0x24;
              puStack_d90 = param_3;
              iVar7 = FUN_004942a4(param_3,puVar8,PTR_FUN_00495f9a_1_00495578,
                                   *(undefined4 *)(iVar9 + 0x20));
              if (iVar7 == 0) {
                bVar2 = true;
                iVar7 = FUN_0043d0ce();
                if (iVar7 << 0x1e < 0) {
                  puStack_d94 = PTR_s_evenhub_ui_page_create__List_con_0049557c;
                  iStack_d98 = 900;
                  FUN_0043d574(3,PTR_s_evenhub_ui_004954f8,
                               PTR_s_D__01_workspace_s200_ap510b_iar__004954f4,
                               PTR_s_evenhub_ui_page_create_004954f0);
                }
                iVar7 = FUN_0043d0ce();
                if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
                  compress_log_output(0xc000000,PTR_s__evenhub_ui_evenhub_ui_page_crea_00495580,
                                      PTR_s__evenhub_ui_evenhub_ui_page_crea_00495580);
                }
              }
              else {
                iVar7 = FUN_0043d0ce();
                if (iVar7 << 0x1e < 0) {
                  puStack_d94 = PTR_s_evenhub_ui_page_create__failed_t_00495584;
                  iStack_d98 = 0x386;
                  FUN_0043d574(1,PTR_s_evenhub_ui_004954f8,
                               PTR_s_D__01_workspace_s200_ap510b_iar__004954f4,
                               PTR_s_evenhub_ui_page_create_004954f0);
                }
                iVar7 = FUN_0043d0ce();
                if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
                  compress_log_output(0x4000000,PTR_s__evenhub_ui_evenhub_ui_page_crea_00495588,
                                      PTR_s__evenhub_ui_evenhub_ui_page_crea_00495588);
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
              iStack_d98 = 0x3cb;
              FUN_0043d574(4,PTR_s_evenhub_ui_004954f8,
                           PTR_s_D__01_workspace_s200_ap510b_iar__004954f4,
                           PTR_s_evenhub_ui_page_create_004954f0);
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
                iStack_d98 = 0x3e0;
                FUN_0043d574(1,PTR_s_evenhub_ui_004954f8,
                             PTR_s_D__01_workspace_s200_ap510b_iar__004954f4,
                             PTR_s_evenhub_ui_page_create_004954f0);
              }
              iVar6 = FUN_0043d0ce();
              if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
                compress_log_output(0x4000000,PTR_s__evenhub_ui_evenhub_ui_page_crea_00495e60,
                                    PTR_s__evenhub_ui_evenhub_ui_page_crea_00495e60);
              }
              FUN_004d9c86(1,*(undefined1 *)(iVar4 + 1),4,1);
              return 0xfffffffd;
            }
            *(undefined4 **)(iVar6 + 0x10) = puVar8;
            iVar7 = FUN_0043d0ce();
            if (iVar7 << 0x1e < 0) {
              puStack_d94 = PTR_s_evenhub_ui_page_create__Image_co_0049555c;
              iStack_d98 = 0x3dc;
              puStack_d90 = puVar8;
              FUN_0043d574(3,PTR_s_evenhub_ui_004954f8,
                           PTR_s_D__01_workspace_s200_ap510b_iar__004954f4,
                           PTR_s_evenhub_ui_page_create_004954f0);
            }
            iVar7 = FUN_0043d0ce();
            if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
              compress_log_output(0xc400000,PTR_s__evenhub_ui_evenhub_ui_page_crea_00495560,
                                  PTR_s__evenhub_ui_evenhub_ui_page_crea_00495560,puVar8);
            }
          }
          else if (bVar1 < 2) {
            iVar9 = *(int *)(iVar6 + 0xc);
            iVar7 = FUN_0043d0ce();
            if (iVar7 << 0x1e < 0) {
              iStack_d8c = iVar9 + 0x24;
              puStack_d90 = *(undefined4 **)(iVar9 + 0x20);
              puStack_d94 = PTR_s_evenhub_ui_page_create__creating_00495594;
              iStack_d98 = 0x396;
              FUN_0043d574(4,PTR_s_evenhub_ui_004954f8,
                           PTR_s_D__01_workspace_s200_ap510b_iar__004954f4,
                           PTR_s_evenhub_ui_page_create_004954f0);
            }
            iVar7 = FUN_0043d0ce();
            if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
              iStack_d98 = iVar9 + 0x24;
              compress_log_output(0x10800000,PTR_s__evenhub_ui_evenhub_ui_page_crea_00495598,
                                  PTR_s__evenhub_ui_evenhub_ui_page_crea_00495598,
                                  *(undefined4 *)(iVar9 + 0x20));
            }
            FUN_0043c0e4(auStack_d5c,0x814,0);
            FUN_00495f1a(iVar9,auStack_d5c);
            puVar8 = (undefined4 *)
                     FUN_004dee96(*param_3,auStack_d5c,PTR_FUN_00494a78_1_0049559c,param_3);
            if (puVar8 == (undefined4 *)0x0) {
              iVar6 = FUN_0043d0ce();
              if (iVar6 << 0x1e < 0) {
                puStack_d94 = PTR_s_evenhub_ui_page_create__failed_t_00495e4c;
                iStack_d98 = 0x3bf;
                FUN_0043d574(1,PTR_s_evenhub_ui_004954f8,
                             PTR_s_D__01_workspace_s200_ap510b_iar__004954f4,
                             PTR_s_evenhub_ui_page_create_004954f0);
              }
              iVar6 = FUN_0043d0ce();
              if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
                compress_log_output(0x4000000,PTR_s__evenhub_ui_evenhub_ui_page_crea_00495e50,
                                    PTR_s__evenhub_ui_evenhub_ui_page_crea_00495e50);
              }
              FUN_004d9c86(1,*(undefined1 *)(iVar4 + 1),4,1);
              return 0xfffffffd;
            }
            *(undefined4 **)(iVar6 + 0x10) = puVar8;
            iVar7 = FUN_0043d0ce();
            if (iVar7 << 0x1e < 0) {
              puStack_d94 = PTR_s_evenhub_ui_page_create__Text_con_004955a0;
              iStack_d98 = 0x3a9;
              puStack_d90 = puVar8;
              FUN_0043d574(3,PTR_s_evenhub_ui_004954f8,
                           PTR_s_D__01_workspace_s200_ap510b_iar__004954f4,
                           PTR_s_evenhub_ui_page_create_004954f0);
            }
            iVar7 = FUN_0043d0ce();
            if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
              compress_log_output(0xc400000,PTR_s__evenhub_ui_evenhub_ui_page_crea_004955a4,
                                  PTR_s__evenhub_ui_evenhub_ui_page_crea_004955a4,puVar8);
            }
            if ((*(int *)(iVar9 + 0x34) == 1) && (!bVar2)) {
              puStack_d94 = (undefined *)0x1;
              iStack_d98 = iVar9 + 0x24;
              puStack_d90 = param_3;
              iVar7 = FUN_004942a4(param_3,puVar8,PTR_FUN_004961e4_1_004955a8,
                                   *(undefined4 *)(iVar9 + 0x20));
              if (iVar7 == 0) {
                bVar2 = true;
                iVar7 = FUN_0043d0ce();
                if (iVar7 << 0x1e < 0) {
                  puStack_d94 = PTR_s_evenhub_ui_page_create__Text_con_004955ac;
                  iStack_d98 = 0x3b9;
                  FUN_0043d574(3,PTR_s_evenhub_ui_004954f8,
                               PTR_s_D__01_workspace_s200_ap510b_iar__004954f4,
                               PTR_s_evenhub_ui_page_create_004954f0);
                }
                iVar7 = FUN_0043d0ce();
                if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
                  compress_log_output(0xc000000,PTR_s__evenhub_ui_evenhub_ui_page_crea_004955b0,
                                      PTR_s__evenhub_ui_evenhub_ui_page_crea_004955b0);
                }
              }
              else {
                iVar7 = FUN_0043d0ce();
                if (iVar7 << 0x1e < 0) {
                  puStack_d94 = PTR_s_evenhub_ui_page_create__failed_t_00495e44;
                  iStack_d98 = 0x3bb;
                  FUN_0043d574(1,PTR_s_evenhub_ui_004954f8,
                               PTR_s_D__01_workspace_s200_ap510b_iar__004954f4,
                               PTR_s_evenhub_ui_page_create_004954f0);
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
              puStack_d94 = PTR_s_evenhub_ui_page_create__unknown_c_00495554;
              iStack_d98 = 0x3e9;
              FUN_0043d574(2,PTR_s_evenhub_ui_004954f8,
                           PTR_s_D__01_workspace_s200_ap510b_iar__004954f4,
                           PTR_s_evenhub_ui_page_create_004954f0);
            }
            iVar7 = FUN_0043d0ce();
            if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
              compress_log_output(0x8400000,PTR_s__evenhub_ui_evenhub_ui_page_crea_00495558,
                                  PTR_s__evenhub_ui_evenhub_ui_page_crea_00495558,
                                  *(undefined1 *)(iVar6 + 8));
            }
          }
        }
        if (!bVar2) {
          iVar6 = FUN_0043d0ce();
          if (iVar6 << 0x1e < 0) {
            puStack_d94 = PTR_s_evenhub_ui_page_create__no_conta_00495e64;
            iStack_d98 = 0x3f1;
            FUN_0043d574(2,PTR_s_evenhub_ui_004954f8,PTR_s_D__01_workspace_s200_ap510b_iar__004954f4
                         ,PTR_s_evenhub_ui_page_create_004954f0);
          }
          iVar6 = FUN_0043d0ce();
          if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
            compress_log_output(0x8000000,PTR_s__evenhub_ui_evenhub_ui_page_crea_00495e68,
                                PTR_s__evenhub_ui_evenhub_ui_page_crea_00495e68);
          }
        }
        FUN_004d9c86(1,*(undefined1 *)(iVar4 + 1),4,0);
        uVar5 = 0;
      }
      else {
        iVar6 = FUN_0043d0ce();
        if (iVar6 << 0x1e < 0) {
          puStack_d94 = PTR_s_evenhub_ui_page_create__create_c_00495530;
          iStack_d98 = 0x34a;
          FUN_0043d574(1,PTR_s_evenhub_ui_004954f8,PTR_s_D__01_workspace_s200_ap510b_iar__004954f4,
                       PTR_s_evenhub_ui_page_create_004954f0);
        }
        iVar6 = FUN_0043d0ce();
        if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
          compress_log_output(0x4000000,PTR_s__evenhub_ui_evenhub_ui_page_crea_00495534,
                              PTR_s__evenhub_ui_evenhub_ui_page_crea_00495534);
        }
        FUN_004d9c86(1,*(undefined1 *)(iVar4 + 1),4,3);
        uVar5 = 0xfffffffe;
      }
    }
  }
  return uVar5;
}

