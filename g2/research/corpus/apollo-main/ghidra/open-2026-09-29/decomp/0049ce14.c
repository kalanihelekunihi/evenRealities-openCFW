
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_0049ce14(int param_1)

{
  undefined4 *puVar1;
  undefined1 *puVar2;
  uint *puVar3;
  uint *puVar4;
  undefined2 *puVar5;
  ushort *puVar6;
  char cVar7;
  int iVar8;
  undefined4 uVar9;
  int iVar10;
  uint uVar11;
  bool bVar12;
  undefined4 uStack_28;
  
  uStack_28 = 0;
  if (*(char *)(param_1 + 0x14b8) == '\0') {
    if (*(char *)(param_1 + 0x14b9) == '\0') {
      if (*(char *)(param_1 + 0x14b6) == '\0') {
        if (*(char *)(param_1 + 0x14b0) == '\0') {
          if (*(char *)(param_1 + 0x14b3) == '\0') {
            if (*(char *)(param_1 + 0x14b4) == '\0') {
              if (*(char *)(param_1 + 0x14b5) != '\0') {
                iVar8 = FUN_0043d0ce();
                if (iVar8 << 0x1e < 0) {
                  FUN_0043d574(4,PTR_s_dashboard_0049db54,
                               PTR_s_D__01_workspace_s200_ap510b_iar__0049db50,
                               PTR_s_dashboard_async_update_data_0049db4c,0x2e5);
                }
                iVar8 = FUN_0043d0ce();
                if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
                  compress_log_output(0x10000000,PTR_s__dashboard__dashboard_update_dat_0049e424,
                                      PTR_s__dashboard__dashboard_update_dat_0049e424);
                }
                iVar8 = FUN_0043d0ce();
                if (iVar8 << 0x1e < 0) {
                  FUN_0043d574(4,PTR_s_dashboard_0049db54,
                               PTR_s_D__01_workspace_s200_ap510b_iar__0049db50,
                               PTR_s_dashboard_async_update_data_0049db4c,0x2e6,
                               PTR_s_parsed_data_>schedule_authority___0049e428,
                               *(undefined4 *)(param_1 + 0x1474));
                }
                iVar8 = FUN_0043d0ce();
                if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
                  compress_log_output(0x10400000,PTR_s__dashboard_parsed_data_>schedule_0049e42c,
                                      PTR_s__dashboard_parsed_data_>schedule_0049e42c,
                                      *(undefined4 *)(param_1 + 0x1474));
                }
                iVar8 = FUN_0043d0ce();
                if (iVar8 << 0x1e < 0) {
                  FUN_0043d574(4,PTR_s_dashboard_0049db54,
                               PTR_s_D__01_workspace_s200_ap510b_iar__0049db50,
                               PTR_s_dashboard_async_update_data_0049db4c,0x2e7,
                               PTR_s_parsed_data_>schedule_num____d__p_0049e430,
                               *(undefined4 *)(param_1 + 0x147c),*(undefined4 *)(param_1 + 0x1478));
                }
                iVar8 = FUN_0043d0ce();
                if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
                  compress_log_output(0x10800000,PTR_s__dashboard_parsed_data_>schedule_0049e434,
                                      PTR_s__dashboard_parsed_data_>schedule_0049e434,
                                      *(undefined4 *)(param_1 + 0x147c),
                                      *(undefined4 *)(param_1 + 0x1478));
                }
                puVar5 = _DAT_0049e660;
                if (*(int *)(param_1 + 0x1478) == 0) {
                  iVar8 = FUN_0043d0ce();
                  if (iVar8 << 0x1e < 0) {
                    FUN_0043d574(4,PTR_s_dashboard_0049db54,
                                 PTR_s_D__01_workspace_s200_ap510b_iar__0049db50,
                                 PTR_s_dashboard_async_update_data_0049db4c,0x2eb,
                                 PTR_s_dashboard_async_update_data__sch_0049e438);
                  }
                  iVar8 = FUN_0043d0ce();
                  if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
                    compress_log_output(0x10000000,_DAT_0049e650,_DAT_0049e650);
                  }
                  FUN_0049c728();
                  puVar1 = _DAT_0049dc00;
                  osMutexAcquire(*_DAT_0049dc00,0xffffffff);
                  *_DAT_0049e654 = *(undefined4 *)(param_1 + 0x1474);
                  osMutexRelease(*puVar1);
                  cVar7 = FUN_0045a570();
                  if (((cVar7 == '\x01') && (iVar8 = FUN_00443484(), iVar8 == 1)) &&
                     (iVar8 = FUN_004434d0(1), puVar2 = _DAT_0049dd48, iVar8 == 1)) {
                    FUN_0043c0e4(_DAT_0049dd48,0x1000,0);
                    *puVar2 = 2;
                    uVar9 = FUN_00464bb2(1,puVar2,1,0);
                    iVar8 = FUN_0043d0ce();
                    if (iVar8 << 0x1e < 0) {
                      FUN_0043d574(4,PTR_s_dashboard_0049db54,
                                   PTR_s_D__01_workspace_s200_ap510b_iar__0049db50,
                                   PTR_s_dashboard_async_update_data_0049db4c,0x2f8,_DAT_0049e658,
                                   uVar9);
                    }
                    iVar8 = FUN_0043d0ce();
                    if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
                      compress_log_output(0x10400000,_DAT_0049e65c,_DAT_0049e65c,uVar9);
                    }
                  }
                }
                else {
                  *_DAT_0049e660 = (short)*(undefined4 *)(param_1 + 0x1478);
                  *(undefined4 *)(puVar5 + *(int *)(param_1 + 0x147c) * 0x108 + 0x108) =
                       *(undefined4 *)(param_1 + 0x1470);
                  FUN_00439be4(puVar5 + *(int *)(param_1 + 0x147c) * 0x108 + 2,param_1 + 0x1264,0xb0
                              );
                  FUN_00439be4(puVar5 + *(int *)(param_1 + 0x147c) * 0x108 + 0x5a,param_1 + 0x1314,
                               0x11b);
                  FUN_00439be4((int)puVar5 + *(int *)(param_1 + 0x147c) * 0x210 + 0x1cf,
                               param_1 + 0x142f,0x40);
                  if (*(int *)(param_1 + 0x1478) == *(int *)(param_1 + 0x147c) + 1) {
                    osMutexAcquire(*_DAT_0049dc00,0xffffffff);
                    for (uVar11 = 0; puVar6 = _DAT_0049e664, uVar11 < *(uint *)(param_1 + 0x1478);
                        uVar11 = uVar11 + 1) {
                      FUN_00439be4(_DAT_0049e664 + uVar11 * 0x108 + 2,puVar5 + uVar11 * 0x108 + 2,
                                   0xb0);
                      FUN_00439be4(puVar6 + uVar11 * 0x108 + 0x5a,puVar5 + uVar11 * 0x108 + 0x5a,
                                   0x11b);
                      FUN_00439be4((int)puVar6 + uVar11 * 0x210 + 0x1cf,
                                   (int)puVar5 + uVar11 * 0x210 + 0x1cf,0x40);
                      *(undefined4 *)(puVar6 + uVar11 * 0x108 + 0x108) =
                           *(undefined4 *)(puVar5 + uVar11 * 0x108 + 0x108);
                    }
                    *_DAT_0049e664 = (ushort)*(undefined4 *)(param_1 + 0x1478);
                    *(undefined4 *)(puVar6 + 0x842) = *(undefined4 *)(param_1 + 0x1474);
                    osMutexRelease(*_DAT_0049ddb4);
                  }
                  cVar7 = FUN_0045a570();
                  if ((((cVar7 == '\x01') && (iVar8 = FUN_00443484(), iVar8 == 1)) &&
                      (iVar8 = FUN_004434d0(1), puVar2 = _DAT_0049dd48, iVar8 == 1)) &&
                     ((uint)*_DAT_0049e664 == *(int *)(param_1 + 0x147c) + 1U)) {
                    FUN_0043c0e4(_DAT_0049dd48,0x1000,0);
                    *puVar2 = 2;
                    uVar9 = FUN_0045aaca(1,puVar2,1,500);
                    iVar8 = FUN_0043d0ce();
                    if (iVar8 << 0x1e < 0) {
                      FUN_0043d574(4,PTR_s_dashboard_0049e444,
                                   PTR_s_D__01_workspace_s200_ap510b_iar__0049e440,
                                   PTR_s_dashboard_async_update_data_0049e43c,0x317,
                                   PTR_s_dashboard_async_update_data__cal_0049e668,uVar9);
                    }
                    iVar8 = FUN_0043d0ce();
                    if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
                      compress_log_output(0x10400000,PTR_s__dashboard_dashboard_async_updat_0049e66c
                                          ,PTR_s__dashboard_dashboard_async_updat_0049e66c,uVar9);
                    }
                  }
                }
              }
            }
            else {
              iVar8 = FUN_0043d0ce();
              if (iVar8 << 0x1e < 0) {
                FUN_0043d574(4,PTR_s_dashboard_0049db54,
                             PTR_s_D__01_workspace_s200_ap510b_iar__0049db50,
                             PTR_s_dashboard_async_update_data_0049db4c,0x27a,
                             PTR_s_dashboard_update_data_screen_off_0049dd74);
              }
              iVar8 = FUN_0043d0ce();
              if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
                compress_log_output(0x10000000,PTR_s__dashboard__dashboard_update_dat_0049dd78,
                                    PTR_s__dashboard__dashboard_update_dat_0049dd78);
              }
              iVar8 = FUN_0043d0ce();
              if (iVar8 << 0x1e < 0) {
                FUN_0043d574(4,PTR_s_dashboard_0049db54,
                             PTR_s_D__01_workspace_s200_ap510b_iar__0049db50,
                             PTR_s_dashboard_async_update_data_0049db4c,0x27b,
                             PTR_s_parsed_data_>stock_total____d__p_0049dd7c,
                             *(undefined4 *)(param_1 + 0x1258),*(undefined4 *)(param_1 + 0x125c));
              }
              iVar8 = FUN_0043d0ce();
              if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
                compress_log_output(0x10800000,PTR_s__dashboard_parsed_data_>stock_to_0049dd80,
                                    PTR_s__dashboard_parsed_data_>stock_to_0049dd80,
                                    *(undefined4 *)(param_1 + 0x1258),
                                    *(undefined4 *)(param_1 + 0x125c));
              }
              puVar1 = _DAT_0049dc00;
              if (*(int *)(param_1 + 0x1258) == 0) {
                iVar8 = FUN_0043d0ce();
                if (iVar8 << 0x1e < 0) {
                  FUN_0043d574(4,PTR_s_dashboard_0049db54,
                               PTR_s_D__01_workspace_s200_ap510b_iar__0049db50,
                               PTR_s_dashboard_async_update_data_0049db4c,0x27f,
                               PTR_s_dashboard_async_update_data__sto_0049dd84);
                }
                iVar8 = FUN_0043d0ce();
                if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
                  compress_log_output(0x10000000,PTR_s__dashboard_dashboard_async_updat_0049dd88,
                                      PTR_s__dashboard_dashboard_async_updat_0049dd88);
                }
                FUN_0049c668();
                *_DAT_0049dd8c = 0;
                *_DAT_0049dd90 = 0;
                cVar7 = FUN_0045a570();
                if (((cVar7 == '\x01') && (iVar8 = FUN_00443484(), iVar8 == 1)) &&
                   (iVar8 = FUN_004434d0(1), puVar2 = _DAT_0049dd48, iVar8 == 1)) {
                  FUN_0043c0e4(_DAT_0049dd48,0x1000,0);
                  *puVar2 = 4;
                  uVar9 = FUN_00464bb2(1,puVar2,1,0);
                  iVar8 = FUN_0043d0ce();
                  if (iVar8 << 0x1e < 0) {
                    FUN_0043d574(4,PTR_s_dashboard_0049db54,
                                 PTR_s_D__01_workspace_s200_ap510b_iar__0049db50,
                                 PTR_s_dashboard_async_update_data_0049db4c,0x28c,
                                 PTR_s_dashboard_async_update_data__sto_0049dd94,uVar9);
                  }
                  iVar8 = FUN_0043d0ce();
                  if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
                    compress_log_output(0x10400000,PTR_s__dashboard_dashboard_async_updat_0049dd98,
                                        PTR_s__dashboard_dashboard_async_updat_0049dd98,uVar9);
                  }
                }
              }
              else if (*(uint *)(param_1 + 0x125c) < 9) {
                osMutexAcquire(*_DAT_0049dc00,0xffffffff);
                iVar8 = _DAT_0049dda4;
                FUN_00439be4(_DAT_0049dda4,param_1 + 0xe30,0x40);
                FUN_00439be4(iVar8 + 0x40,param_1 + 0xe70,0x40);
                FUN_00439be4(iVar8 + 0x80,param_1 + 0xeb0,0x80);
                uVar9 = *(undefined4 *)(param_1 + 0xf34);
                *(undefined4 *)(iVar8 + 0x100) = *(undefined4 *)(param_1 + 0xf30);
                *(undefined4 *)(iVar8 + 0x104) = uVar9;
                *(undefined4 *)(iVar8 + 0x108) = *(undefined4 *)(param_1 + 0xf38);
                *(undefined4 *)(iVar8 + 0x10c) = *(undefined4 *)(param_1 + 0xf3c);
                *(undefined4 *)(iVar8 + 0x110) = *(undefined4 *)(param_1 + 0xf40);
                *(undefined4 *)(iVar8 + 0x114) = *(undefined4 *)(param_1 + 0xf44);
                *(undefined4 *)(iVar8 + 0x118) = *(undefined4 *)(param_1 + 0xf48);
                uVar9 = *(undefined4 *)(param_1 + 0xf54);
                *(undefined4 *)(iVar8 + 0x120) = *(undefined4 *)(param_1 + 0xf50);
                *(undefined4 *)(iVar8 + 0x124) = uVar9;
                uVar9 = *(undefined4 *)(param_1 + 0xf5c);
                *(undefined4 *)(iVar8 + 0x128) = *(undefined4 *)(param_1 + 0xf58);
                *(undefined4 *)(iVar8 + 300) = uVar9;
                *(undefined4 *)(iVar8 + 0x130) = *(undefined4 *)(param_1 + 0xf60);
                *(undefined4 *)(iVar8 + 0x134) = *(undefined4 *)(param_1 + 0xf64);
                *(undefined4 *)(iVar8 + 0x138) = *(undefined4 *)(param_1 + 0xf68);
                *(undefined4 *)(iVar8 + 0x13c) = *(undefined4 *)(param_1 + 0xf6c);
                iVar10 = FUN_0043d0ce();
                if (iVar10 << 0x1e < 0) {
                  FUN_0043d574(3,PTR_s_dashboard_0049db54,
                               PTR_s_D__01_workspace_s200_ap510b_iar__0049db50,
                               PTR_s_dashboard_async_update_data_0049db4c,0x2aa,
                               PTR_s_parsed_data_>stock_code__s__comp_0049dda8,param_1 + 0xe30,
                               param_1 + 0xeb0,*(undefined4 *)(param_1 + 0xf68));
                }
                iVar10 = FUN_0043d0ce();
                if ((iVar10 << 0x1f < 0) || (iVar10 = FUN_0043d0ce(), iVar10 << 0x1d < 0)) {
                  compress_log_output(0xcc00000,PTR_s__dashboard_parsed_data_>stock_co_0049ddac,
                                      PTR_s__dashboard_parsed_data_>stock_co_0049ddac,
                                      param_1 + 0xe30,param_1 + 0xeb0,
                                      *(undefined4 *)(param_1 + 0xf68));
                }
                iVar10 = FUN_0043d0ce();
                if (iVar10 << 0x1e < 0) {
                  FUN_0043d574(3,PTR_s_dashboard_0049db54,
                               PTR_s_D__01_workspace_s200_ap510b_iar__0049db50,
                               PTR_s_dashboard_async_update_data_0049db4c,0x2ab,
                               PTR_s_day_high__f__day_low__f__dark_pr_0049ddb0,
                               (double)*(float *)(param_1 + 0xf40),
                               (double)*(float *)(param_1 + 0xf44),
                               (double)*(float *)(param_1 + 0xf6c));
                }
                iVar10 = FUN_0043d0ce();
                if ((iVar10 << 0x1f < 0) || (iVar10 = FUN_0043d0ce(), iVar10 << 0x1d < 0)) {
                  compress_log_output(0xcc00000,PTR_s__dashboard_day_high__f__day_low__0049e114,
                                      PTR_s__dashboard_day_high__f__day_low__0049e114);
                }
                iVar10 = FUN_0043d0ce();
                if (iVar10 << 0x1e < 0) {
                  FUN_0043d574(3,PTR_s_dashboard_0049db54,
                               PTR_s_D__01_workspace_s200_ap510b_iar__0049db50,
                               PTR_s_dashboard_async_update_data_0049db4c,0x2ac,
                               PTR_s_price_change_percent__f__current_0049e118,
                               (double)*(float *)(param_1 + 0xf38),
                               (double)*(float *)(param_1 + 0xf3c));
                }
                iVar10 = FUN_0043d0ce();
                if ((iVar10 << 0x1f < 0) || (iVar10 = FUN_0043d0ce(), iVar10 << 0x1d < 0)) {
                  compress_log_output(0xc800000,PTR_s__dashboard_price_change_percent__0049e11c,
                                      PTR_s__dashboard_price_change_percent__0049e11c);
                }
                iVar10 = FUN_0043d0ce();
                if (iVar10 << 0x1e < 0) {
                  FUN_0043d574(3,PTR_s_dashboard_0049db54,
                               PTR_s_D__01_workspace_s200_ap510b_iar__0049db50,
                               PTR_s_dashboard_async_update_data_0049db4c,0x2ad,
                               PTR_s_changing_trend__d__open_price__f_0049e120,
                               *(undefined4 *)(param_1 + 0xf64));
                }
                iVar10 = FUN_0043d0ce();
                if ((iVar10 << 0x1f < 0) || (iVar10 = FUN_0043d0ce(), iVar10 << 0x1d < 0)) {
                  compress_log_output(0xc800000,PTR_s__dashboard_changing_trend__d__op_0049e124,
                                      PTR_s__dashboard_changing_trend__d__op_0049e124,
                                      *(undefined4 *)(param_1 + 0xf64),
                                      (double)*(float *)(param_1 + 0xf48));
                }
                FUN_00439be4(iVar8 + 0x140,param_1 + 0xf70,0x2e4);
                FUN_004e9e32(iVar8,*(undefined4 *)(param_1 + 0x125c),
                             *(undefined4 *)(param_1 + 0x1258));
                osMutexRelease(*puVar1);
                puVar4 = _DAT_0049dd90;
                puVar3 = _DAT_0049dd8c;
                if (*(int *)(param_1 + 0x1258) != 0) {
                  if (*_DAT_0049dd90 == *(uint *)(param_1 + 0x1258)) {
                    if (*_DAT_0049dd90 < *_DAT_0049dd8c) {
                      iVar8 = FUN_0043d0ce();
                      if (iVar8 << 0x1e < 0) {
                        FUN_0043d574(4,PTR_s_dashboard_0049db54,
                                     PTR_s_D__01_workspace_s200_ap510b_iar__0049db50,
                                     PTR_s_dashboard_async_update_data_0049db4c,0x2bf,
                                     PTR_s_Counter_overflow__d__d__force_re_0049e130,*puVar3,*puVar4
                                    );
                      }
                      iVar8 = FUN_0043d0ce();
                      if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
                        compress_log_output(0x10800000,
                                            PTR_s__dashboard_Counter_overflow__d___0049e134,
                                            PTR_s__dashboard_Counter_overflow__d___0049e134,*puVar3,
                                            *puVar4);
                      }
                      *puVar3 = 0;
                    }
                  }
                  else {
                    iVar8 = FUN_0043d0ce();
                    if (iVar8 << 0x1e < 0) {
                      FUN_0043d574(4,PTR_s_dashboard_0049db54,
                                   PTR_s_D__01_workspace_s200_ap510b_iar__0049db50,
                                   PTR_s_dashboard_async_update_data_0049db4c,0x2b9,
                                   PTR_s_Stock_total_changed__d_>_d__rese_0049e128,*puVar4,
                                   *(undefined4 *)(param_1 + 0x1258));
                    }
                    iVar8 = FUN_0043d0ce();
                    if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
                      compress_log_output(0x10800000,PTR_s__dashboard_Stock_total_changed___0049e12c
                                          ,PTR_s__dashboard_Stock_total_changed___0049e12c,*puVar4,
                                          *(undefined4 *)(param_1 + 0x1258));
                    }
                    *puVar4 = *(uint *)(param_1 + 0x1258);
                    *_DAT_0049dd8c = 0;
                  }
                  *puVar4 = *(uint *)(param_1 + 0x1258);
                }
                puVar3 = _DAT_0049dd8c;
                *_DAT_0049dd8c = *_DAT_0049dd8c + 1;
                iVar8 = FUN_0043d0ce();
                if (iVar8 << 0x1e < 0) {
                  FUN_0043d574(4,PTR_s_dashboard_0049db54,
                               PTR_s_D__01_workspace_s200_ap510b_iar__0049db50,
                               PTR_s_dashboard_async_update_data_0049db4c,0x2c7,
                               PTR_s_dashboard_async_received_stock___0049e138,*puVar3,
                               *_DAT_0049dd90);
                }
                iVar8 = FUN_0043d0ce();
                if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
                  compress_log_output(0x10800000,PTR_s__dashboard_dashboard_async_recei_0049e13c,
                                      PTR_s__dashboard_dashboard_async_recei_0049e13c,*puVar3,
                                      *_DAT_0049dd90);
                }
                puVar4 = _DAT_0049dd90;
                bVar12 = *_DAT_0049dd90 <= *puVar3;
                cVar7 = FUN_0045a570();
                if ((((bVar12) && (cVar7 == '\x01')) && (iVar8 = FUN_00443484(), iVar8 == 1)) &&
                   (iVar8 = FUN_004434d0(1), puVar2 = _DAT_0049dd48, iVar8 == 1)) {
                  FUN_0043c0e4(_DAT_0049dd48,0x1000,0);
                  *puVar2 = 4;
                  uVar9 = FUN_00464bb2(1,puVar2,1,0);
                  iVar8 = FUN_0043d0ce();
                  if (iVar8 << 0x1e < 0) {
                    FUN_0043d574(3,PTR_s_dashboard_0049db54,
                                 PTR_s_D__01_workspace_s200_ap510b_iar__0049db50,
                                 PTR_s_dashboard_async_update_data_0049db4c,0x2d8,
                                 PTR_s_Stock_UI_refresh_triggered__ret___0049e140,uVar9);
                  }
                  iVar8 = FUN_0043d0ce();
                  if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
                    compress_log_output(0xc400000,PTR_s__dashboard_Stock_UI_refresh_trig_0049e40c,
                                        PTR_s__dashboard_Stock_UI_refresh_trig_0049e40c,uVar9);
                  }
                }
                else if (!bVar12) {
                  iVar8 = FUN_0043d0ce();
                  if (iVar8 << 0x1e < 0) {
                    FUN_0043d574(4,PTR_s_dashboard_0049db54,
                                 PTR_s_D__01_workspace_s200_ap510b_iar__0049db50,
                                 PTR_s_dashboard_async_update_data_0049db4c,0x2da,
                                 PTR_s_Stock_data_accumulated__waiting_f_0049e410,*puVar3,*puVar4);
                  }
                  iVar8 = FUN_0043d0ce();
                  if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
                    compress_log_output(0x10800000,PTR_s__dashboard_Stock_data_accumulate_0049e414,
                                        PTR_s__dashboard_Stock_data_accumulate_0049e414,*puVar3,
                                        *puVar4);
                  }
                }
                if (bVar12) {
                  iVar8 = FUN_0043d0ce();
                  if (iVar8 << 0x1e < 0) {
                    FUN_0043d574(3,PTR_s_dashboard_0049db54,
                                 PTR_s_D__01_workspace_s200_ap510b_iar__0049db50,
                                 PTR_s_dashboard_async_update_data_0049db4c,0x2df,
                                 PTR_s_All_stocks_received__reset_count_0049e418);
                  }
                  iVar8 = FUN_0043d0ce();
                  if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
                    compress_log_output(0xc000000,PTR_s__dashboard_All_stocks_received__r_0049e41c,
                                        PTR_s__dashboard_All_stocks_received__r_0049e41c);
                  }
                  *puVar3 = 0;
                }
              }
              else {
                iVar8 = FUN_0043d0ce();
                if (iVar8 << 0x1e < 0) {
                  FUN_0043d574(1,PTR_s_dashboard_0049db54,
                               PTR_s_D__01_workspace_s200_ap510b_iar__0049db50,
                               PTR_s_dashboard_async_update_data_0049db4c,0x293,
                               PTR_s_Invalid_stock_num___d__ignore_0049dd9c,
                               *(undefined4 *)(param_1 + 0x125c));
                }
                iVar8 = FUN_0043d0ce();
                if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
                  compress_log_output(0x4400000,PTR_s__dashboard_Invalid_stock_num___d_0049dda0,
                                      PTR_s__dashboard_Invalid_stock_num___d_0049dda0,
                                      *(undefined4 *)(param_1 + 0x125c));
                }
                uStack_28 = 0;
              }
            }
          }
          else {
            iVar8 = FUN_0043d0ce();
            if (iVar8 << 0x1e < 0) {
              FUN_0043d574(4,PTR_s_dashboard_0049db54,
                           PTR_s_D__01_workspace_s200_ap510b_iar__0049db50,
                           PTR_s_dashboard_async_update_data_0049db4c,0x226,
                           PTR_s_dashboard_update_data_screen_off_0049dd64);
            }
            iVar8 = FUN_0043d0ce();
            if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
              compress_log_output(0x10000000,PTR_s__dashboard__dashboard_update_dat_0049dd68,
                                  PTR_s__dashboard__dashboard_update_dat_0049dd68);
            }
            iVar8 = FUN_0043d0ce();
            if (iVar8 << 0x1e < 0) {
              FUN_0043d574(3,PTR_s_dashboard_0049db54,
                           PTR_s_D__01_workspace_s200_ap510b_iar__0049db50,
                           PTR_s_dashboard_async_update_data_0049db4c,0x227,
                           PTR_s_news_protol_has_changed_drop_it__0049dd6c);
            }
            iVar8 = FUN_0043d0ce();
            if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
              compress_log_output(0xc000000,PTR_s__dashboard_news_protol_has_chang_0049dd70,
                                  PTR_s__dashboard_news_protol_has_chang_0049dd70);
            }
            uStack_28 = 2;
          }
        }
        else {
          iVar8 = FUN_0043d0ce();
          if (iVar8 << 0x1e < 0) {
            FUN_0043d574(4,PTR_s_dashboard_0049db54,PTR_s_D__01_workspace_s200_ap510b_iar__0049db50,
                         PTR_s_dashboard_async_update_data_0049db4c,0x20b,
                         PTR_s_dashboard_update_data_screen_off_0049dd54);
          }
          iVar8 = FUN_0043d0ce();
          if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
            compress_log_output(0x10000000,PTR_s__dashboard__dashboard_update_dat_0049dd58,
                                PTR_s__dashboard__dashboard_update_dat_0049dd58);
          }
          puVar1 = _DAT_0049dc00;
          osMutexAcquire(*_DAT_0049dc00,0xffffffff);
          iVar8 = _DAT_0049dc04;
          *(undefined1 *)(_DAT_0049dc04 + 0x20) = 1;
          *(undefined4 *)(iVar8 + 0x24) = *(undefined4 *)(param_1 + 0x24);
          *(undefined2 *)(iVar8 + 0x28) = *(undefined2 *)(param_1 + 0x28);
          *(undefined2 *)(iVar8 + 0x2a) = *(undefined2 *)(param_1 + 0x2a);
          uVar9 = *(undefined4 *)(param_1 + 0x34);
          *(undefined4 *)(iVar8 + 0x30) = *(undefined4 *)(param_1 + 0x30);
          *(undefined4 *)(iVar8 + 0x34) = uVar9;
          FUN_0044b5a0(iVar8 + 0x38,param_1 + 0x38,0x1f);
          *(undefined1 *)(iVar8 + 0x57) = 0;
          *(undefined4 *)(iVar8 + 0x58) = *(undefined4 *)(param_1 + 0x58);
          FUN_0044b5a0(iVar8 + 0x5c,param_1 + 0x5c,0x1f);
          *(undefined1 *)(iVar8 + 0x7b) = 0;
          *(undefined4 *)(iVar8 + 0x7c) = *(undefined4 *)(param_1 + 0x7c);
          FUN_0044b5a0(iVar8 + 0x80,param_1 + 0x80,0x1f);
          *(undefined1 *)(iVar8 + 0x9f) = 0;
          osMutexRelease(*puVar1);
          cVar7 = FUN_0045a570();
          if (((cVar7 == '\x01') && (iVar8 = FUN_00443484(), iVar8 == 1)) &&
             (iVar8 = FUN_004434d0(1), puVar2 = _DAT_0049dd48, iVar8 == 1)) {
            FUN_0043c0e4(_DAT_0049dd48,0x1000,0);
            *puVar2 = 1;
            uVar9 = FUN_00464bb2(1,puVar2,1,0);
            iVar8 = FUN_0043d0ce();
            if (iVar8 << 0x1e < 0) {
              FUN_0043d574(4,PTR_s_dashboard_0049db54,
                           PTR_s_D__01_workspace_s200_ap510b_iar__0049db50,
                           PTR_s_dashboard_async_update_data_0049db4c,0x222,
                           PTR_s_dashboard_update_data_screen_on__0049dd5c,uVar9);
            }
            iVar8 = FUN_0043d0ce();
            if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
              compress_log_output(0x10400000,PTR_s__dashboard_dashboard_update_data_0049dd60,
                                  PTR_s__dashboard_dashboard_update_data_0049dd60,uVar9);
            }
          }
        }
      }
      else {
        iVar8 = FUN_0043d0ce();
        if (iVar8 << 0x1e < 0) {
          FUN_0043d574(4,PTR_s_dashboard_0049db54,PTR_s_D__01_workspace_s200_ap510b_iar__0049db50,
                       PTR_s_dashboard_async_update_data_0049db4c,0x1ed,_DAT_0049dbf8);
        }
        iVar8 = FUN_0043d0ce();
        if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
          compress_log_output(0x10000000,_DAT_0049dbfc,_DAT_0049dbfc);
        }
        puVar1 = _DAT_0049dc00;
        osMutexAcquire(*_DAT_0049dc00,0xffffffff);
        iVar8 = _DAT_0049dc04;
        *(short *)(_DAT_0049dc04 + 10) = (short)*(undefined4 *)(param_1 + 0x1484);
        for (uVar11 = 0; uVar11 < *(uint *)(param_1 + 0x1484); uVar11 = uVar11 + 1) {
          *(ushort *)(iVar8 + uVar11 * 2 + 0xc) = (ushort)*(byte *)(param_1 + uVar11 + 0x1488);
        }
        *(short *)(iVar8 + 0x18) = (short)*(undefined4 *)(param_1 + 0x1494);
        for (uVar11 = 0; uVar11 < *(uint *)(param_1 + 0x1494); uVar11 = uVar11 + 1) {
          *(undefined1 *)(iVar8 + uVar11 + 0x1a) = *(undefined1 *)(param_1 + uVar11 + 0x1498);
        }
        osMutexRelease(*puVar1);
        iVar8 = FUN_00466010();
        *(undefined4 *)(iVar8 + 0x18) = *(undefined4 *)(param_1 + 0x14a4);
        iVar8 = FUN_0043d0ce();
        if (iVar8 << 0x1e < 0) {
          FUN_0043d574(3,PTR_s_dashboard_0049db54,PTR_s_D__01_workspace_s200_ap510b_iar__0049db50,
                       PTR_s_dashboard_async_update_data_0049db4c,0x1fe,_DAT_0049dc08,
                       *(undefined4 *)(param_1 + 0x14a4));
        }
        iVar8 = FUN_0043d0ce();
        if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
          compress_log_output(0xc400000,_DAT_0049dc0c,_DAT_0049dc0c,
                              *(undefined4 *)(param_1 + 0x14a4));
        }
        FUN_00466016();
        cVar7 = FUN_0045a570();
        if (((cVar7 == '\x01') && (iVar8 = FUN_00443484(), iVar8 == 1)) &&
           (iVar8 = FUN_004434d0(1), puVar2 = _DAT_0049dd48, iVar8 == 1)) {
          FUN_0043c0e4(_DAT_0049dd48,0x1000,0);
          *puVar2 = 1;
          uVar9 = FUN_00464bb2(1,puVar2,1,0);
          iVar8 = FUN_0043d0ce();
          if (iVar8 << 0x1e < 0) {
            FUN_0043d574(4,PTR_s_dashboard_0049db54,PTR_s_D__01_workspace_s200_ap510b_iar__0049db50,
                         PTR_s_dashboard_async_update_data_0049db4c,0x206,
                         PTR_s_dashboard_async_update_data__ret_0049dd4c,uVar9);
          }
          iVar8 = FUN_0043d0ce();
          if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
            compress_log_output(0x10400000,PTR_s__dashboard_dashboard_async_updat_0049dd50,
                                PTR_s__dashboard_dashboard_async_updat_0049dd50,uVar9);
          }
        }
      }
    }
    else {
      iVar8 = FUN_0043d0ce();
      if (iVar8 << 0x1e < 0) {
        FUN_0043d574(4,PTR_s_dashboard_0049db54,PTR_s_D__01_workspace_s200_ap510b_iar__0049db50,
                     PTR_s_dashboard_async_update_data_0049db4c,0x1ea,
                     PTR_s_dashboard_update_data_screen_off_0049db48);
      }
      iVar8 = FUN_0043d0ce();
      if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
        compress_log_output(0x10000000,PTR_s__dashboard__dashboard_update_dat_0049db58,
                            PTR_s__dashboard__dashboard_update_dat_0049db58);
      }
      uStack_28 = 0;
    }
  }
  else {
    uStack_28 = 2;
  }
  return uStack_28;
}

