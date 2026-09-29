
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_004fe318(uint param_1,undefined4 param_2,uint param_3)

{
  short sVar1;
  ushort uVar2;
  byte *pbVar3;
  uint *puVar4;
  undefined4 *puVar5;
  int *piVar6;
  int *piVar7;
  int *piVar8;
  int *piVar9;
  char cVar10;
  bool bVar11;
  int iVar12;
  undefined4 uVar13;
  int iVar14;
  uint uVar15;
  undefined4 uVar16;
  byte *pbVar17;
  uint uVar18;
  uint uStack_a0;
  undefined *puStack_9c;
  uint uStack_98;
  uint auStack_94 [2];
  undefined4 uStack_8c;
  undefined4 uStack_88;
  undefined4 uStack_84;
  undefined4 uStack_80;
  uint uStack_78;
  uint uStack_74;
  undefined1 auStack_70 [12];
  uint uStack_64;
  undefined1 auStack_60 [12];
  uint uStack_54;
  undefined1 auStack_4c [12];
  uint uStack_40;
  undefined1 auStack_38 [20];
  
  if ((param_1 == 0) || (param_3 == 0)) {
    iVar12 = FUN_0043d0ce();
    if (iVar12 << 0x1e < 0) {
      puStack_9c = PTR_s_Invalid_parameters__data__p__par_004fedc4;
      uStack_a0 = 0x1ee;
      uStack_98 = param_1;
      auStack_94[0] = param_3;
      FUN_0043d574(1,PTR_s_dashboard_data_process_004feee8,
                   PTR_s_D__01_workspace_s200_ap510b_iar__004feee4,
                   PTR_s_dashboard_parse_data_package_004feee0);
    }
    iVar12 = FUN_0043d0ce();
    if ((iVar12 << 0x1f < 0) || (iVar12 = FUN_0043d0ce(), iVar12 << 0x1d < 0)) {
      uStack_a0 = param_3;
      compress_log_output(0x4800000,PTR_s__dashboard_data_process_Invalid_p_004fedc8,
                          PTR_s__dashboard_data_process_Invalid_p_004fedc8,param_1);
    }
    uVar13 = 0;
  }
  else {
    func_0x004fd93c(param_3);
    pbVar3 = DAT_004fec84;
    FUN_004fdd6e(DAT_004fec84);
    FUN_0048f49c(&uStack_a0,param_1,param_2);
    FUN_00439c04(auStack_70,&uStack_a0,0x10);
    uVar13 = DAT_004fec88;
    cVar10 = FUN_00490120(auStack_70,DAT_004fec88,pbVar3);
    puVar4 = _DAT_004feef4;
    if (cVar10 == '\0') {
      iVar12 = FUN_0043d0ce();
      if (iVar12 << 0x1e < 0) {
        uStack_98 = DAT_004fec8c;
        if (uStack_64 != 0) {
          uStack_98 = uStack_64;
        }
        puStack_9c = PTR_s_decode_failed___s_004feeec;
        uStack_a0 = 0x1fc;
        FUN_0043d574(1,PTR_s_dashboard_data_process_004feee8,
                     PTR_s_D__01_workspace_s200_ap510b_iar__004feee4,
                     PTR_s_dashboard_parse_data_package_004feee0);
      }
      iVar12 = FUN_0043d0ce();
      if ((iVar12 << 0x1f < 0) || (iVar12 = FUN_0043d0ce(), iVar12 << 0x1d < 0)) {
        uVar18 = DAT_004fec8c;
        if (uStack_64 != 0) {
          uVar18 = uStack_64;
        }
        compress_log_output(0x4400000,PTR_s__dashboard_data_process_decode_f_004feef0,
                            PTR_s__dashboard_data_process_decode_f_004feef0,uVar18);
      }
      uVar13 = 0;
    }
    else {
      *_DAT_004feef4 = (uint)*pbVar3;
      puVar5 = _DAT_004feef8;
      *_DAT_004feef8 = *(undefined4 *)(pbVar3 + 4);
      piVar6 = _DAT_004ff1e4;
      sVar1 = *(short *)(pbVar3 + 8);
      if (sVar1 == 4) {
        *_DAT_004ff1e4 = (int)(pbVar3 + 0x10);
        *_DAT_004ff1e8 = *(undefined4 *)*piVar6;
        piVar9 = _DAT_004ff200;
        piVar8 = _DAT_004ff1f4;
        piVar7 = _DAT_004ff1ec;
        uVar2 = *(ushort *)(*piVar6 + 4);
        if (uVar2 == 2) {
          *_DAT_004ff1ec = *piVar6 + 8;
          piVar6 = _DAT_004ff1f0;
          *_DAT_004ff1f0 = param_3 + 0x1480;
          *(undefined4 *)*piVar6 = *(undefined4 *)*piVar7;
          *(undefined4 *)(*piVar6 + 4) = *(undefined4 *)(*piVar7 + 4);
          *(undefined4 *)(*piVar6 + 0x14) = *(undefined4 *)(*piVar7 + 0x14);
          *(undefined4 *)(*piVar6 + 0x24) = *(undefined4 *)(*piVar7 + 0x24);
          *(undefined4 *)(*piVar6 + 0x28) = *(undefined4 *)(*piVar7 + 0x28);
          FUN_00439be4(*piVar6 + 8,*piVar7 + 10,*(undefined2 *)(*piVar7 + 8));
          FUN_00439be4(*piVar6 + 0x18,*piVar7 + 0x1a,*(undefined2 *)(*piVar7 + 0x18));
          *(undefined1 *)(param_3 + 0x14b6) = 1;
        }
        else if (1 < uVar2) {
          if (uVar2 == 4) {
            *_DAT_004ff200 = *piVar6 + 8;
            *(undefined4 *)(param_3 + 0x14ac) = *(undefined4 *)*piVar9;
            *(undefined1 *)(param_3 + 0x14b7) = 1;
          }
          else if (uVar2 < 4) {
            *_DAT_004ff1f4 = *piVar6 + 8;
            piVar7 = _DAT_004ff1fc;
            piVar6 = _DAT_004ff1f8;
            if (*(short *)*piVar8 == 1) {
              *_DAT_004ff1f8 = *piVar8 + 8;
              func_0x004fda24(*piVar6,param_3);
            }
            else if (*(short *)*piVar8 == 2) {
              *_DAT_004ff1fc = *piVar8 + 8;
              func_0x004fdad4(*piVar7,param_3);
            }
          }
        }
      }
      else if (sVar1 == 7) {
        if (*(int *)(pbVar3 + 0x10) == 1) {
          *(undefined1 *)(param_3 + 0x14b8) = 1;
        }
      }
      else if (sVar1 == 9) {
        if (*puVar4 != 7) {
          iVar12 = FUN_0043d0ce();
          if (iVar12 << 0x1e < 0) {
            puStack_9c = PTR_s_DashboardDataPackage_ReqNewsInfo_004ff08c;
            uStack_a0 = 0x238;
            FUN_0043d574(1,PTR_s_dashboard_data_process_004feee8,
                         PTR_s_D__01_workspace_s200_ap510b_iar__004feee4,
                         PTR_s_dashboard_parse_data_package_004feee0);
          }
          iVar12 = FUN_0043d0ce();
          if ((iVar12 << 0x1f < 0) || (iVar12 = FUN_0043d0ce(), iVar12 << 0x1d < 0)) {
            compress_log_output(0x4000000,PTR_s__dashboard_data_process_Dashboar_004ff090,
                                PTR_s__dashboard_data_process_Dashboar_004ff090);
          }
          return 0;
        }
        *(undefined1 *)(param_3 + 0x14b9) = 1;
        uVar16 = DAT_004fec80;
        iVar14 = 0;
        FUN_0043c0e4(DAT_004fec80,0x100,0);
        FUN_004fdd6e(pbVar3);
        *pbVar3 = 8;
        *(undefined4 *)(pbVar3 + 4) = *puVar5;
        pbVar3[8] = 10;
        pbVar3[9] = 0;
        for (iVar12 = 0; iVar12 < 5; iVar12 = iVar12 + 1) {
          if (*(char *)(_DAT_004fec04 + iVar12 * 0x1ca8) == '\x01') {
            *(undefined4 *)(pbVar3 + iVar12 * 4 + 0x18) =
                 *(undefined4 *)(iVar12 * 0x1ca8 + _DAT_004fec04 + 0x10);
            iVar14 = iVar14 + 1;
          }
        }
        *(short *)(pbVar3 + 0x14) = (short)iVar14;
        *(int *)(pbVar3 + 0x10) = iVar14;
        FUN_004905f4(&uStack_a0,uVar16,0x100);
        FUN_00439c04(auStack_60,&uStack_a0,0x14);
        iVar12 = FUN_00490c32(auStack_60,uVar13,pbVar3);
        if (iVar12 == 0) {
          return 0;
        }
        Thread_MsgPbTxByBle(1,1,uVar16,uStack_54 & 0xffff);
      }
      else if (sVar1 == 0xb) {
        if (*puVar4 != 9) {
          iVar12 = FUN_0043d0ce();
          if (iVar12 << 0x1e < 0) {
            auStack_94[0] = *puVar4;
            uStack_98 = 9;
            puStack_9c = PTR_s_SendNewsData_command_id_mismatch_004ff094;
            uStack_a0 = 0x264;
            FUN_0043d574(1,PTR_s_dashboard_data_process_004feee8,
                         PTR_s_D__01_workspace_s200_ap510b_iar__004feee4,
                         PTR_s_dashboard_parse_data_package_004feee0);
          }
          iVar12 = FUN_0043d0ce();
          if ((iVar12 << 0x1f < 0) || (iVar12 = FUN_0043d0ce(), iVar12 << 0x1d < 0)) {
            uStack_a0 = *puVar4;
            compress_log_output(0x4800000,PTR_s__dashboard_data_process_SendNews_004ff098,
                                PTR_s__dashboard_data_process_SendNews_004ff098,9);
          }
          return 0;
        }
        *(undefined1 *)(param_3 + 0x14b9) = 1;
        pbVar17 = pbVar3 + 0x10;
        uVar18 = 0;
        uStack_80 = *(undefined4 *)pbVar17;
        uStack_84 = *(undefined4 *)(pbVar3 + 0x18);
        uStack_88 = *(undefined4 *)(pbVar3 + 0x1c);
        uStack_8c = *(undefined4 *)(pbVar3 + 0x20);
        if (*(int *)(pbVar3 + 0x14) == 1) {
          iVar12 = FUN_0043d0ce();
          if (iVar12 << 0x1e < 0) {
            puStack_9c = PTR_s_no_news__special_handling_____004ff1c0;
            uStack_a0 = 0x279;
            FUN_0043d574(3,PTR_s_dashboard_data_process_004feee8,
                         PTR_s_D__01_workspace_s200_ap510b_iar__004feee4,
                         PTR_s_dashboard_parse_data_package_004feee0);
          }
          iVar12 = FUN_0043d0ce();
          if ((iVar12 << 0x1f < 0) || (iVar12 = FUN_0043d0ce(), iVar12 << 0x1d < 0)) {
            compress_log_output(0xc000000,PTR_s__dashboard_data_process_no_news__004ff1c4,
                                PTR_s__dashboard_data_process_no_news__004ff1c4);
          }
          iVar12 = FUN_0045a570();
          if (iVar12 == 1) {
            iVar12 = FUN_0043d0ce();
            if (iVar12 << 0x1e < 0) {
              puStack_9c = PTR_s_master_role__send_event_to_UI_ap_004ff1c8;
              uStack_a0 = 0x27b;
              FUN_0043d574(3,PTR_s_dashboard_data_process_004feee8,
                           PTR_s_D__01_workspace_s200_ap510b_iar__004feee4,
                           PTR_s_dashboard_parse_data_package_004feee0);
            }
            iVar12 = FUN_0043d0ce();
            if ((iVar12 << 0x1f < 0) || (iVar12 = FUN_0043d0ce(), iVar12 << 0x1d < 0)) {
              compress_log_output(0xc000000,PTR_s__dashboard_data_process_master_r_004ff1cc,
                                  PTR_s__dashboard_data_process_master_r_004ff1cc);
            }
            iVar12 = FUN_00443484();
            if ((iVar12 == 1) && (iVar12 = FUN_004434d0(1), iVar12 == 1)) {
              FUN_0043c0e4(auStack_94,5,0);
              auStack_94[0] = CONCAT31(auStack_94[0]._1_3_,0xd);
              FUN_00464bb2(1,auStack_94,1,0);
            }
          }
        }
        else if (*(uint *)(pbVar3 + 0x1c) < 5) {
          uVar15 = *(uint *)(pbVar3 + 0x1c);
          if (uVar15 < 5) {
            osMutexAcquire(*_DAT_004ff1d8,0xffffffff);
            iVar12 = _DAT_004fec04;
            if ((*(int *)(_DAT_004fec04 + 4) != *(int *)pbVar17) || (*(int *)(pbVar3 + 0x1c) == 0))
            {
              FUN_0043c0e4(_DAT_004fec04,0x8f48,0);
            }
            *(undefined1 *)(iVar12 + uVar15 * 0x1ca8) = 1;
            *(undefined4 *)(uVar15 * 0x1ca8 + iVar12 + 4) = *(undefined4 *)pbVar17;
            *(undefined4 *)(uVar15 * 0x1ca8 + iVar12 + 8) = *(undefined4 *)(pbVar3 + 0x18);
            *(undefined4 *)(uVar15 * 0x1ca8 + iVar12 + 0xc) = *(undefined4 *)(pbVar3 + 0x1c);
            *(undefined4 *)(uVar15 * 0x1ca8 + iVar12 + 0x10) = *(undefined4 *)(pbVar3 + 0x20);
            iVar14 = uVar15 * 0x1ca8 + iVar12;
            uVar16 = *(undefined4 *)(pbVar3 + 0xac);
            *(undefined4 *)(iVar14 + 0x1ca0) = *(undefined4 *)(pbVar3 + 0xa8);
            *(undefined4 *)(iVar14 + 0x1ca4) = uVar16;
            FUN_0044b5a0(uVar15 * 0x1ca8 + iVar12 + 0x94,pbVar3 + 0x24,0x7f);
            *(undefined1 *)(uVar15 * 0x1ca8 + iVar12 + 0x113) = 0;
            FUN_0044b5a0(uVar15 * 0x1ca8 + iVar12 + 0x14,pbVar3 + 0xb0,0x7f);
            *(undefined1 *)(uVar15 * 0x1ca8 + iVar12 + 0x93) = 0;
            FUN_0044b5a0(uVar15 * 0x1ca8 + iVar12 + 0x114,pbVar3 + 0x130,0x1b89);
            *(undefined1 *)(iVar12 + uVar15 * 0x1ca8 + 0x1c9d) = 0;
            osMutexRelease(*_DAT_004ff1d8);
            bVar11 = true;
            for (iVar14 = 0; iVar14 < 5; iVar14 = iVar14 + 1) {
              if (*(char *)(iVar12 + iVar14 * 0x1ca8) != '\x01') {
                bVar11 = false;
                break;
              }
            }
            if ((bVar11) && (iVar12 = FUN_0045a570(), iVar12 == 1)) {
              iVar12 = FUN_0043d0ce();
              if (iVar12 << 0x1e < 0) {
                puStack_9c = PTR_s_master_role__send_event_to_UI_ap_004ff1c8;
                uStack_a0 = 0x2b3;
                FUN_0043d574(3,PTR_s_dashboard_data_process_004feee8,
                             PTR_s_D__01_workspace_s200_ap510b_iar__004feee4,
                             PTR_s_dashboard_parse_data_package_004feee0);
              }
              iVar12 = FUN_0043d0ce();
              if ((iVar12 << 0x1f < 0) || (iVar12 = FUN_0043d0ce(), iVar12 << 0x1d < 0)) {
                compress_log_output(0xc000000,PTR_s__dashboard_data_process_master_r_004ff1cc,
                                    PTR_s__dashboard_data_process_master_r_004ff1cc);
              }
              FUN_0043c0e4(&puStack_9c,5,0);
              puStack_9c = (undefined *)CONCAT31(puStack_9c._1_3_,0x10);
              FUN_00454b4c(0x32);
              uStack_a0 = 5;
              FUN_00464f76(1,&puStack_9c,1,0);
            }
          }
          else {
            iVar12 = FUN_0043d0ce();
            if (iVar12 << 0x1e < 0) {
              auStack_94[0] = 4;
              uStack_98 = *(uint *)(pbVar3 + 0x1c);
              puStack_9c = PTR_s_session_news_index__d_out_of_ran_004ff1d0;
              uStack_a0 = 0x28e;
              FUN_0043d574(1,PTR_s_dashboard_data_process_004feee8,
                           PTR_s_D__01_workspace_s200_ap510b_iar__004feee4,
                           PTR_s_dashboard_parse_data_package_004feee0);
            }
            iVar12 = FUN_0043d0ce();
            if ((iVar12 << 0x1f < 0) || (iVar12 = FUN_0043d0ce(), iVar12 << 0x1d < 0)) {
              uStack_a0 = 4;
              compress_log_output(0x4800000,PTR_s__dashboard_data_process_session__004ff1d4,
                                  PTR_s__dashboard_data_process_session__004ff1d4,
                                  *(undefined4 *)(pbVar3 + 0x1c));
            }
            uVar18 = 1;
          }
        }
        else {
          iVar12 = FUN_0043d0ce();
          if (iVar12 << 0x1e < 0) {
            auStack_94[0] = 4;
            uStack_98 = *(uint *)(pbVar3 + 0x1c);
            puStack_9c = PTR_s_session_news_index__d_out_of_ran_004ff1d0;
            uStack_a0 = 0x288;
            FUN_0043d574(1,PTR_s_dashboard_data_process_004feee8,
                         PTR_s_D__01_workspace_s200_ap510b_iar__004feee4,
                         PTR_s_dashboard_parse_data_package_004feee0);
          }
          iVar12 = FUN_0043d0ce();
          if ((iVar12 << 0x1f < 0) || (iVar12 = FUN_0043d0ce(), iVar12 << 0x1d < 0)) {
            uStack_a0 = 4;
            compress_log_output(0x4800000,PTR_s__dashboard_data_process_session__004ff1d4,
                                PTR_s__dashboard_data_process_session__004ff1d4,
                                *(undefined4 *)(pbVar3 + 0x1c));
          }
          uVar18 = 1;
        }
        uVar16 = DAT_004fec80;
        FUN_0043c0e4(DAT_004fec80,0x100,0);
        FUN_004fdd6e(pbVar3);
        *pbVar3 = 10;
        *(undefined4 *)(pbVar3 + 4) = *puVar5;
        pbVar3[8] = 0xc;
        pbVar3[9] = 0;
        *(undefined4 *)(pbVar3 + 0x10) = uStack_80;
        *(undefined4 *)(pbVar3 + 0x14) = uStack_84;
        *(undefined4 *)(pbVar3 + 0x18) = uStack_88;
        *(undefined4 *)(pbVar3 + 0x1c) = uStack_8c;
        *(uint *)(pbVar3 + 0x20) = uVar18;
        FUN_004905f4(auStack_38,uVar16,0x100);
        FUN_00439c04(&uStack_84,auStack_38,0x14);
        iVar12 = FUN_00490c32(&uStack_84,uVar13,pbVar3);
        if (iVar12 == 0) {
          iVar12 = FUN_0043d0ce();
          if (iVar12 << 0x1e < 0) {
            uStack_98 = DAT_004fec8c;
            if (uStack_74 != 0) {
              uStack_98 = uStack_74;
            }
            puStack_9c = DAT_004fec90;
            uStack_a0 = 0x2ce;
            FUN_0043d574(1,PTR_s_dashboard_data_process_004feee8,
                         PTR_s_D__01_workspace_s200_ap510b_iar__004feee4,
                         PTR_s_dashboard_parse_data_package_004feee0);
          }
          iVar12 = FUN_0043d0ce();
          if ((iVar12 << 0x1f < 0) || (iVar12 = FUN_0043d0ce(), iVar12 << 0x1d < 0)) {
            uVar18 = DAT_004fec8c;
            if (uStack_74 != 0) {
              uVar18 = uStack_74;
            }
            compress_log_output(0x4400000,PTR_s__dashboard_data_process_SendNews_004fedc0,
                                PTR_s__dashboard_data_process_SendNews_004fedc0,uVar18);
          }
          return 0;
        }
        uVar15 = Thread_MsgPbTxByBle(1,1,uVar16,uStack_78 & 0xffff);
        iVar12 = FUN_0043d0ce();
        if (iVar12 << 0x1e < 0) {
          puStack_9c = _DAT_004ff1dc;
          uStack_a0 = 0x2d4;
          uStack_98 = uVar18;
          auStack_94[0] = uVar15;
          FUN_0043d574(3,PTR_s_dashboard_data_process_004feee8,
                       PTR_s_D__01_workspace_s200_ap510b_iar__004feee4,
                       PTR_s_dashboard_parse_data_package_004feee0);
        }
        iVar12 = FUN_0043d0ce();
        if ((iVar12 << 0x1f < 0) || (iVar12 = FUN_0043d0ce(), iVar12 << 0x1d < 0)) {
          uStack_a0 = uVar15;
          compress_log_output(0xc800000,_DAT_004ff1e0,_DAT_004ff1e0,uVar18);
        }
      }
      else {
        if (sVar1 != 0xf) {
          iVar12 = FUN_0043d0ce();
          if (iVar12 << 0x1e < 0) {
            uStack_98 = (uint)*(ushort *)(pbVar3 + 8);
            puStack_9c = PTR_s_Unsupported_command_type___d_004ff204;
            uStack_a0 = 0x335;
            FUN_0043d574(3,PTR_s_dashboard_data_process_004feee8,
                         PTR_s_D__01_workspace_s200_ap510b_iar__004feee4,
                         PTR_s_dashboard_parse_data_package_004feee0);
          }
          iVar12 = FUN_0043d0ce();
          if ((iVar12 << 0x1f < 0) || (iVar12 = FUN_0043d0ce(), iVar12 << 0x1d < 0)) {
            compress_log_output(0xc400000,PTR_s__dashboard_data_process_Unsuppor_004ff30c,
                                PTR_s__dashboard_data_process_Unsuppor_004ff30c,
                                *(undefined2 *)(pbVar3 + 8));
          }
          return 0;
        }
        if (*puVar4 != 0xd) {
          iVar12 = FUN_0043d0ce();
          if (iVar12 << 0x1e < 0) {
            puStack_9c = _DAT_004feefc;
            uStack_a0 = 0x214;
            FUN_0043d574(1,PTR_s_dashboard_data_process_004feee8,
                         PTR_s_D__01_workspace_s200_ap510b_iar__004feee4,
                         PTR_s_dashboard_parse_data_package_004feee0);
          }
          iVar12 = FUN_0043d0ce();
          if ((iVar12 << 0x1f < 0) || (iVar12 = FUN_0043d0ce(), iVar12 << 0x1d < 0)) {
            compress_log_output(0x4000000,_DAT_004fef00,_DAT_004fef00);
          }
          return 0;
        }
        *(undefined1 *)(param_3 + 0x14b9) = 1;
        uVar16 = DAT_004fec80;
        FUN_0043c0e4(DAT_004fec80,0x100,0);
        FUN_004fdd6e(pbVar3);
        *pbVar3 = 0xe;
        *(undefined4 *)(pbVar3 + 4) = *puVar5;
        pbVar3[8] = 0x10;
        pbVar3[9] = 0;
        pbVar3[0x10] = 1;
        pbVar3[0x11] = 0;
        pbVar3[0x12] = 0;
        pbVar3[0x13] = 0;
        FUN_004905f4(&uStack_a0,uVar16,0x100);
        FUN_00439c04(auStack_4c,&uStack_a0,0x14);
        iVar12 = FUN_00490c32(auStack_4c,uVar13,pbVar3);
        if (iVar12 == 0) {
          return 0;
        }
        Thread_MsgPbTxByBle(1,1,uVar16,uStack_40 & 0xffff);
        iVar12 = FUN_0045a570();
        if (iVar12 == 1) {
          FUN_0043c0e4(&uStack_8c,5,0);
          uStack_8c = CONCAT31(uStack_8c._1_3_,0x11);
          uStack_a0 = 5;
          FUN_00464f76(1,&uStack_8c,1,0);
        }
      }
      uVar13 = 1;
    }
  }
  return uVar13;
}

