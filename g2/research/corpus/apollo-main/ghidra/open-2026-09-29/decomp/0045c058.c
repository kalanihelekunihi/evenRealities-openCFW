
void FUN_0045c058(undefined4 param_1,undefined *param_2,undefined4 param_3,int param_4)

{
  char cVar1;
  undefined2 uVar2;
  int *piVar3;
  char *pcVar4;
  int iVar5;
  int iVar6;
  short sVar7;
  short sVar8;
  undefined4 uVar9;
  int local_1c;
  
  sVar7 = 0;
  sVar8 = 0;
  local_1c = param_4;
  FUN_0045ba46(0);
  piVar3 = DAT_0045cd18;
  if (*DAT_0045cd18 == 0) {
    iVar5 = osMutexNew(DAT_0045cd1c);
    *piVar3 = iVar5;
    if (*piVar3 == 0) {
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        param_1 = 0x307;
        param_2 = PTR_s_create_DispStartBlocking_mutex_f_0045cd6c;
        FUN_0043d574(1,PTR_s_sync_module_framework_0045cd78,
                     PTR_s_D__01_workspace_s200_ap510b_iar__0045cd74,
                     PTR_s__SyncScheduleManagerThreadHandle_0045cd70,0x307,
                     PTR_s_create_DispStartBlocking_mutex_f_0045cd6c,param_3);
      }
      iVar5 = FUN_0043d0ce();
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        compress_log_output(0x4000000,PTR_s__sync_module_framework_create_Di_0045cd7c,
                            PTR_s__sync_module_framework_create_Di_0045cd7c);
      }
    }
  }
  piVar3 = DAT_0045cd80;
  if (*DAT_0045cd80 == 0) {
    iVar5 = osTimerNew(PTR_FUN_0045bc06_1_0045cd84,0,0,0,param_1,param_2);
    *piVar3 = iVar5;
    if (*piVar3 == 0) {
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        FUN_0043d574(1,PTR_s_sync_module_framework_0045cd78,
                     PTR_s_D__01_workspace_s200_ap510b_iar__0045cd74,
                     PTR_s__SyncScheduleManagerThreadHandle_0045cd70,0x30d,
                     PTR_s_create_DispStartBlocking_timer_f_0045cd88,param_3);
      }
      iVar5 = FUN_0043d0ce();
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        compress_log_output(0x4000000,PTR_s__sync_module_framework_create_Di_0045cd8c,
                            PTR_s__sync_module_framework_create_Di_0045cd8c);
      }
    }
  }
  do {
    while( true ) {
      while( true ) {
        while( true ) {
          while( true ) {
            do {
              local_1c = 0;
              iVar5 = osMessageQueueGet(*DAT_0045cd98,&local_1c,0,0xffffffff);
            } while (iVar5 != 0);
            iVar5 = FUN_0043d0ce();
            if (iVar5 << 0x1e < 0) {
              FUN_0043d574(4,PTR_s_sync_module_framework_0045cd78,
                           PTR_s_D__01_workspace_s200_ap510b_iar__0045cd74,
                           PTR_s__SyncScheduleManagerThreadHandle_0045cd70,0x314,DAT_0045cd9c,
                           local_1c);
            }
            iVar5 = FUN_0043d0ce();
            if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
              compress_log_output(0x10400000,PTR_s__sync_module_framework__pSyncPac_0045ceb0,
                                  PTR_s__sync_module_framework__pSyncPac_0045ceb0,local_1c);
            }
            if (local_1c != 0) break;
            iVar5 = FUN_0043d0ce();
            if (iVar5 << 0x1e < 0) {
              FUN_0043d574(2,PTR_s_sync_module_framework_0045cd78,
                           PTR_s_D__01_workspace_s200_ap510b_iar__0045cd74,
                           PTR_s__SyncScheduleManagerThreadHandle_0045cd70,0x316,
                           PTR_s_schedule_manager_received_null_d_0045cd90);
            }
            iVar5 = FUN_0043d0ce();
            if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
              compress_log_output(0x8000000,PTR_s__sync_module_framework_schedule_m_0045cd94,
                                  PTR_s__sync_module_framework_schedule_m_0045cd94);
            }
          }
          iVar5 = FUN_0043d0ce();
          if (iVar5 << 0x1e < 0) {
            FUN_0043d574(4,PTR_s_sync_module_framework_0045cd78,
                         PTR_s_D__01_workspace_s200_ap510b_iar__0045cd74,
                         PTR_s__SyncScheduleManagerThreadHandle_0045cd70,0x31b,
                         PTR_s_SyncEventType____d_0045ceb4,*(undefined2 *)(local_1c + 4));
          }
          iVar5 = FUN_0043d0ce();
          if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
            compress_log_output(0x10400000,PTR_s__sync_module_framework_SyncEvent_0045ceb8,
                                PTR_s__sync_module_framework_SyncEvent_0045ceb8,
                                *(undefined2 *)(local_1c + 4));
          }
          iVar5 = FUN_0043d0ce();
          if (iVar5 << 0x1e < 0) {
            FUN_0043d574(4,PTR_s_sync_module_framework_0045cd78,
                         PTR_s_D__01_workspace_s200_ap510b_iar__0045cd74,
                         PTR_s__SyncScheduleManagerThreadHandle_0045cd70,0x31c,
                         PTR_s_len____d_0045cebc,*(undefined2 *)(local_1c + 6));
          }
          iVar5 = FUN_0043d0ce();
          if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
            compress_log_output(0x10400000,PTR_s__sync_module_framework_len____d_0045cf60,
                                PTR_s__sync_module_framework_len____d_0045cf60,
                                *(undefined2 *)(local_1c + 6));
          }
          for (iVar5 = 0; iVar5 < (int)(uint)*(ushort *)(local_1c + 6); iVar5 = iVar5 + 1) {
          }
          cVar1 = *(char *)(*(int *)(local_1c + 8) + 1);
          uVar2 = CONCAT11(cVar1,**(undefined1 **)(local_1c + 8));
          iVar5 = FUN_0043d0ce();
          if (iVar5 << 0x1e < 0) {
            FUN_0043d574(4,PTR_s_sync_module_framework_0045cd78,
                         PTR_s_D__01_workspace_s200_ap510b_iar__0045cd74,
                         PTR_s__SyncScheduleManagerThreadHandle_0045cd70,0x322,
                         PTR_s_packet_cmd____d_0045cf64,uVar2);
          }
          iVar5 = FUN_0043d0ce();
          if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
            compress_log_output(0x10400000,PTR_s__sync_module_framework_packet_cm_0045cf68,
                                PTR_s__sync_module_framework_packet_cm_0045cf68,uVar2);
          }
          pcVar4 = DAT_0045cfec;
          if (*DAT_0045cfec == '\0') break;
          if (*DAT_0045cfec == '\x01') {
            if (cVar1 == '\x01') {
              *(undefined2 *)(local_1c + 4) = 2;
              iVar5 = *(int *)(local_1c + 8);
              if (*(short *)(iVar5 + 2) == sVar7) {
                iVar6 = FUN_0043d0ce();
                if (iVar6 << 0x1e < 0) {
                  FUN_0043d574(4,PTR_s_sync_module_framework_0045cd78,
                               PTR_s_D__01_workspace_s200_ap510b_iar__0045cd74,
                               PTR_s__SyncScheduleManagerThreadHandle_0045cd70,0x3b8,
                               PTR_s_start_app_id____d_0045d544,sVar7);
                }
                iVar6 = FUN_0043d0ce();
                if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
                  compress_log_output(0x10400000,PTR_s__sync_module_framework_start_app_0045d548,
                                      PTR_s__sync_module_framework_start_app_0045d548,sVar7);
                }
                iVar6 = FUN_0043d0ce();
                if (iVar6 << 0x1e < 0) {
                  FUN_0043d574(4,PTR_s_sync_module_framework_0045cd78,
                               PTR_s_D__01_workspace_s200_ap510b_iar__0045cd74,
                               PTR_s__SyncScheduleManagerThreadHandle_0045cd70,0x3b9,
                               PTR_s_received_same_app_id____d_drop_i_0045d54c,
                               *(undefined2 *)(iVar5 + 2));
                }
                iVar6 = FUN_0043d0ce();
                if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
                  compress_log_output(0x10400000,PTR_s__sync_module_framework_received_s_0045d550,
                                      PTR_s__sync_module_framework_received_s_0045d550,
                                      *(undefined2 *)(iVar5 + 2));
                }
                file_heap_free(*(undefined4 *)(local_1c + 8));
                file_heap_free(local_1c);
              }
              else {
                iVar6 = FUN_0045bbf4();
                if (iVar6 == 1) {
                  iVar6 = FUN_0043d0ce();
                  if (iVar6 << 0x1e < 0) {
                    FUN_0043d574(3,PTR_s_sync_module_framework_0045cd78,
                                 PTR_s_D__01_workspace_s200_ap510b_iar__0045cd74,
                                 PTR_s__SyncScheduleManagerThreadHandle_0045cd70,0x3bf,DAT_0045cff4,
                                 *(undefined2 *)(iVar5 + 2));
                  }
                  iVar6 = FUN_0043d0ce();
                  if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
                    compress_log_output(0xc400000,DAT_0045d064,DAT_0045d064,
                                        *(undefined2 *)(iVar5 + 2));
                  }
                  file_heap_free(*(undefined4 *)(local_1c + 8));
                  file_heap_free(local_1c);
                }
                else {
                  iVar6 = osMessageQueuePut(*DAT_0045d068,&local_1c,0,2000);
                  if (iVar6 == 0) {
                    if (sVar8 == 0) {
                      sVar8 = 1;
                    }
                    osEventFlagsSet(*DAT_0045d0c8,2);
                    iVar6 = FUN_0043d0ce();
                    if (iVar6 << 0x1e < 0) {
                      FUN_0043d574(4,PTR_s_sync_module_framework_0045cd78,
                                   PTR_s_D__01_workspace_s200_ap510b_iar__0045cd74,
                                   PTR_s__SyncScheduleManagerThreadHandle_0045cd70,0x3cf,
                                   DAT_0045d708,*(undefined2 *)(iVar5 + 2));
                    }
                    iVar6 = FUN_0043d0ce();
                    if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
                      compress_log_output(0x10400000,DAT_0045d70c,DAT_0045d70c,
                                          *(undefined2 *)(iVar5 + 2));
                    }
                  }
                  else {
                    iVar5 = FUN_0043d0ce();
                    if (iVar5 << 0x1e < 0) {
                      FUN_0043d574(2,PTR_s_sync_module_framework_0045cd78,
                                   PTR_s_D__01_workspace_s200_ap510b_iar__0045cd74,
                                   PTR_s__SyncScheduleManagerThreadHandle_0045cd70,0x3c6,
                                   DAT_0045d06c,iVar6);
                    }
                    iVar5 = FUN_0043d0ce();
                    if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
                      compress_log_output(0x8400000,DAT_0045d0c4,DAT_0045d0c4,iVar6);
                    }
                    file_heap_free(*(undefined4 *)(local_1c + 8));
                    file_heap_free(local_1c);
                  }
                }
              }
            }
            else if (cVar1 == '\x03') {
              *(undefined2 *)(local_1c + 4) = 2;
              iVar5 = osMessageQueuePut(*DAT_0045d068,&local_1c,0,2000);
              if (iVar5 == 0) {
                osEventFlagsSet(*DAT_0045d0c8,2);
                iVar5 = FUN_0043d0ce();
                if (iVar5 << 0x1e < 0) {
                  FUN_0043d574(4,PTR_s_sync_module_framework_0045cd78,
                               PTR_s_D__01_workspace_s200_ap510b_iar__0045cd74,
                               PTR_s__SyncScheduleManagerThreadHandle_0045cd70,0x3db,
                               PTR_s_schedule_manager_processing_Refl_0045d7c0);
                }
                iVar5 = FUN_0043d0ce();
                if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
                  compress_log_output(0x10000000,PTR_s__sync_module_framework_schedule_m_0045d7c4,
                                      PTR_s__sync_module_framework_schedule_m_0045d7c4);
                }
              }
              else {
                iVar6 = FUN_0043d0ce();
                if (iVar6 << 0x1e < 0) {
                  FUN_0043d574(2,PTR_s_sync_module_framework_0045cd78,
                               PTR_s_D__01_workspace_s200_ap510b_iar__0045cd74,
                               PTR_s__SyncScheduleManagerThreadHandle_0045cd70,0x3d5,DAT_0045d06c,
                               iVar5);
                }
                iVar6 = FUN_0043d0ce();
                if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
                  compress_log_output(0x8400000,DAT_0045d0c4,DAT_0045d0c4,iVar5);
                }
                file_heap_free(*(undefined4 *)(local_1c + 8));
                file_heap_free(local_1c);
              }
            }
            else if ((cVar1 == '\x05') || (cVar1 == '\x10')) {
              *(undefined2 *)(local_1c + 4) = 2;
              iVar6 = *(int *)(local_1c + 8);
              iVar5 = osMessageQueuePut(*DAT_0045d068,&local_1c,0,2000);
              if (iVar5 == 0) {
                osEventFlagsSet(*DAT_0045d0c8,2);
                if (sVar8 == 0) {
                  iVar5 = FUN_0043d0ce();
                  if (iVar5 << 0x1e < 0) {
                    FUN_0043d574(4,PTR_s_sync_module_framework_0045d7d0,
                                 PTR_s_D__01_workspace_s200_ap510b_iar__0045d7cc,
                                 PTR_s__SyncScheduleManagerThreadHandle_0045d7c8,0x3e9,
                                 PTR_s_received_display_sync_exit_comma_0045d7d4,
                                 *(undefined2 *)(iVar6 + 2));
                  }
                  iVar5 = FUN_0043d0ce();
                  if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
                    compress_log_output(0x10400000,PTR_s__sync_module_framework_received_d_0045d7d8,
                                        PTR_s__sync_module_framework_received_d_0045d7d8,
                                        *(undefined2 *)(iVar6 + 2));
                  }
                  if ((sVar7 == *(short *)(iVar6 + 2)) || (*(short *)(iVar6 + 2) == 0)) {
                    *pcVar4 = '\0';
                    sVar7 = 0;
                  }
                  else {
                    iVar5 = FUN_0043d0ce();
                    if (iVar5 << 0x1e < 0) {
                      FUN_0043d574(2,PTR_s_sync_module_framework_0045d7d0,
                                   PTR_s_D__01_workspace_s200_ap510b_iar__0045d7cc,
                                   PTR_s__SyncScheduleManagerThreadHandle_0045d7c8,0x3ef,
                                   PTR_s_____received_error_display_sync_e_0045d7dc,
                                   *(undefined2 *)(iVar6 + 2));
                    }
                    iVar5 = FUN_0043d0ce();
                    if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
                      compress_log_output(0x8400000,PTR_s__sync_module_framework_____recei_0045d7e0,
                                          PTR_s__sync_module_framework_____recei_0045d7e0,
                                          *(undefined2 *)(iVar6 + 2));
                    }
                  }
                }
                if (sVar8 != 0) {
                  sVar8 = sVar8 + -1;
                }
                iVar5 = FUN_0043d0ce();
                if (iVar5 << 0x1e < 0) {
                  FUN_0043d574(4,PTR_s_sync_module_framework_0045d7d0,
                               PTR_s_D__01_workspace_s200_ap510b_iar__0045d7cc,
                               PTR_s__SyncScheduleManagerThreadHandle_0045d7c8,0x3f6,DAT_0045d9b8);
                }
                iVar5 = FUN_0043d0ce();
                if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
                  compress_log_output(0x10000000,DAT_0045d9bc,DAT_0045d9bc);
                }
              }
              else {
                iVar6 = FUN_0043d0ce();
                if (iVar6 << 0x1e < 0) {
                  FUN_0043d574(2,PTR_s_sync_module_framework_0045d7d0,
                               PTR_s_D__01_workspace_s200_ap510b_iar__0045d7cc,
                               PTR_s__SyncScheduleManagerThreadHandle_0045d7c8,0x3e1,DAT_0045d06c,
                               iVar5);
                }
                iVar6 = FUN_0043d0ce();
                if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
                  compress_log_output(0x8400000,DAT_0045d0c4,DAT_0045d0c4,iVar5);
                }
                file_heap_free(*(undefined4 *)(local_1c + 8));
                file_heap_free(local_1c);
              }
            }
            else if (cVar1 == '\a') {
              *(undefined2 *)(local_1c + 4) = 3;
              FUN_0045baf0(*(undefined4 *)(local_1c + 8));
              iVar5 = *DAT_0045d9c0;
              FUN_0045bb58();
              if (iVar5 == 1) {
                iVar5 = FUN_0043d0ce();
                if (iVar5 << 0x1e < 0) {
                  FUN_0043d574(3,PTR_s_sync_module_framework_0045d7d0,
                               PTR_s_D__01_workspace_s200_ap510b_iar__0045d7cc,
                               PTR_s__SyncScheduleManagerThreadHandle_0045d7c8,0x3ff,DAT_0045d9c4);
                }
                iVar5 = FUN_0043d0ce();
                if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
                  compress_log_output(0xc000000,DAT_0045d9c8,DAT_0045d9c8);
                }
                file_heap_free(*(undefined4 *)(local_1c + 8));
                file_heap_free(local_1c);
              }
              else {
                iVar5 = osMessageQueuePut(*DAT_0045d068,&local_1c,0,2000);
                if (iVar5 == 0) {
                  osEventFlagsSet(*DAT_0045d0c8,2);
                  iVar5 = FUN_0043d0ce();
                  if (iVar5 << 0x1e < 0) {
                    FUN_0043d574(4,PTR_s_sync_module_framework_0045d7d0,
                                 PTR_s_D__01_workspace_s200_ap510b_iar__0045d7cc,
                                 PTR_s__SyncScheduleManagerThreadHandle_0045d7c8,0x40c,
                                 PTR_s_schedule_manager_processing_data_0045da84);
                  }
                  iVar5 = FUN_0043d0ce();
                  if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
                    compress_log_output(0x10000000,PTR_s__sync_module_framework_schedule_m_0045da88,
                                        PTR_s__sync_module_framework_schedule_m_0045da88);
                  }
                  *pcVar4 = '\x01';
                }
                else {
                  iVar6 = FUN_0043d0ce();
                  if (iVar6 << 0x1e < 0) {
                    FUN_0043d574(2,PTR_s_sync_module_framework_0045d7d0,
                                 PTR_s_D__01_workspace_s200_ap510b_iar__0045d7cc,
                                 PTR_s__SyncScheduleManagerThreadHandle_0045d7c8,0x406,DAT_0045d06c,
                                 iVar5);
                  }
                  iVar6 = FUN_0043d0ce();
                  if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
                    compress_log_output(0x8400000,DAT_0045d0c4,DAT_0045d0c4,iVar5);
                  }
                  file_heap_free(*(undefined4 *)(local_1c + 8));
                  file_heap_free(local_1c);
                }
              }
            }
            else if (cVar1 == '\x0e') {
              iVar5 = FUN_0043d0ce();
              if (iVar5 << 0x1e < 0) {
                FUN_0043d574(3,PTR_s_sync_module_framework_0045d7d0,
                             PTR_s_D__01_workspace_s200_ap510b_iar__0045d7cc,
                             PTR_s__SyncScheduleManagerThreadHandle_0045d7c8,0x410,
                             PTR_s_received_page_manager_close_info_0045da8c);
              }
              iVar5 = FUN_0043d0ce();
              if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
                compress_log_output(0xc000000,PTR_s__sync_module_framework_received_p_0045da90,
                                    PTR_s__sync_module_framework_received_p_0045da90);
              }
              file_heap_free(*(undefined4 *)(local_1c + 8));
              file_heap_free(local_1c);
              *pcVar4 = '\0';
              sVar7 = 0;
            }
            else {
              file_heap_free(*(undefined4 *)(local_1c + 8));
              file_heap_free(local_1c);
            }
          }
          else {
            if (*(int *)(local_1c + 8) != 0) {
              file_heap_free(*(undefined4 *)(local_1c + 8));
            }
            file_heap_free(local_1c);
            iVar5 = FUN_0043d0ce();
            if (iVar5 << 0x1e < 0) {
              FUN_0043d574(1,PTR_s_sync_module_framework_0045d7d0,
                           PTR_s_D__01_workspace_s200_ap510b_iar__0045d7cc,
                           PTR_s__SyncScheduleManagerThreadHandle_0045d7c8,0x425,
                           PTR_s_system_disp_status_is_invalid_0045da94);
            }
            iVar5 = FUN_0043d0ce();
            if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
              compress_log_output(0x4000000,DAT_0045dd34,DAT_0045dd34);
            }
          }
        }
        if (cVar1 != '\x01') break;
        iVar5 = SVC_Settings_AppLaunchCheck();
        if ((iVar5 == 1) && (*DAT_0045cff0 == 0)) {
          *(undefined2 *)(local_1c + 4) = 2;
          iVar6 = *(int *)(local_1c + 8);
          iVar5 = FUN_0045bbf4();
          if ((iVar5 == 1) && (*(short *)(iVar6 + 2) != 0x30)) {
            iVar5 = FUN_0043d0ce();
            if (iVar5 << 0x1e < 0) {
              FUN_0043d574(3,PTR_s_sync_module_framework_0045cd78,
                           PTR_s_D__01_workspace_s200_ap510b_iar__0045cd74,
                           PTR_s__SyncScheduleManagerThreadHandle_0045cd70,0x32c,DAT_0045cff4,
                           *(undefined2 *)(iVar6 + 2));
            }
            iVar5 = FUN_0043d0ce();
            if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
              compress_log_output(0xc400000,DAT_0045d064,DAT_0045d064,*(undefined2 *)(iVar6 + 2));
            }
            file_heap_free(*(undefined4 *)(local_1c + 8));
            file_heap_free(local_1c);
          }
          else {
            iVar5 = osMessageQueuePut(*DAT_0045d068,&local_1c,0,2000);
            if (iVar5 == 0) {
              osEventFlagsSet(*DAT_0045d0c8,2);
              sVar7 = *(short *)(iVar6 + 2);
              sVar8 = 0;
              iVar5 = FUN_0043d0ce();
              if (iVar5 << 0x1e < 0) {
                FUN_0043d574(3,PTR_s_sync_module_framework_0045cd78,
                             PTR_s_D__01_workspace_s200_ap510b_iar__0045cd74,
                             PTR_s__SyncScheduleManagerThreadHandle_0045cd70,0x33b,DAT_0045d0cc);
              }
              iVar5 = FUN_0043d0ce();
              if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
                compress_log_output(0xc000000,DAT_0045d138,DAT_0045d138);
              }
              *pcVar4 = '\x01';
              FUN_0045bbd2();
              *DAT_0045d13c = 0;
            }
            else {
              iVar6 = FUN_0043d0ce();
              if (iVar6 << 0x1e < 0) {
                FUN_0043d574(2,PTR_s_sync_module_framework_0045cd78,
                             PTR_s_D__01_workspace_s200_ap510b_iar__0045cd74,
                             PTR_s__SyncScheduleManagerThreadHandle_0045cd70,0x333,DAT_0045d06c,
                             iVar5);
              }
              iVar6 = FUN_0043d0ce();
              if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
                compress_log_output(0x8400000,DAT_0045d0c4,DAT_0045d0c4,iVar5);
              }
              file_heap_free(*(undefined4 *)(local_1c + 8));
              file_heap_free(local_1c);
            }
          }
        }
        else {
          iVar5 = FUN_0043d0ce();
          if (iVar5 << 0x1e < 0) {
            FUN_0043d574(3,PTR_s_sync_module_framework_0045cd78,
                         PTR_s_D__01_workspace_s200_ap510b_iar__0045cd74,
                         PTR_s__SyncScheduleManagerThreadHandle_0045cd70,0x340,DAT_0045d140);
          }
          iVar5 = FUN_0043d0ce();
          if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
            compress_log_output(0xc000000,DAT_0045d144,DAT_0045d144);
          }
          if (*DAT_0045cff0 == 1) {
            iVar5 = FUN_0043d0ce();
            if (iVar5 << 0x1e < 0) {
              FUN_0043d574(3,PTR_s_sync_module_framework_0045cd78,
                           PTR_s_D__01_workspace_s200_ap510b_iar__0045cd74,
                           PTR_s__SyncScheduleManagerThreadHandle_0045cd70,0x342,
                           PTR_s_display_start_blocking_flag_is_1_0045d1b8);
            }
            iVar5 = FUN_0043d0ce();
            if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
              compress_log_output(0xc000000,PTR_s__sync_module_framework_display_s_0045d1bc,
                                  PTR_s__sync_module_framework_display_s_0045d1bc);
            }
          }
          file_heap_free(*(undefined4 *)(local_1c + 8));
          file_heap_free(local_1c);
        }
      }
      if (cVar1 == '\a') break;
      if (cVar1 == '\x0f') {
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          FUN_0043d574(3,PTR_s_sync_module_framework_0045cd78,
                       PTR_s_D__01_workspace_s200_ap510b_iar__0045cd74,
                       PTR_s__SyncScheduleManagerThreadHandle_0045cd70,0x3a1,DAT_0045d4d8);
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          compress_log_output(0xc000000,PTR_s__sync_module_framework_received_p_0045d538,
                              PTR_s__sync_module_framework_received_p_0045d538);
        }
        *pcVar4 = '\x01';
        FUN_0045bbd2();
        sVar7 = CONCAT11(*(undefined1 *)(*(int *)(local_1c + 8) + 3),
                         *(undefined1 *)(*(int *)(local_1c + 8) + 2));
        sVar8 = 0;
        file_heap_free(*(undefined4 *)(local_1c + 8));
        file_heap_free(local_1c);
        *DAT_0045d13c = 0;
      }
      else {
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          FUN_0043d574(2,PTR_s_sync_module_framework_0045cd78,
                       PTR_s_D__01_workspace_s200_ap510b_iar__0045cd74,
                       PTR_s__SyncScheduleManagerThreadHandle_0045cd70,0x3ab,
                       PTR_s_idle_status_unsupport_command_____0045d53c,uVar2);
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          compress_log_output(0x8400000,PTR_s__sync_module_framework_idle_stat_0045d540,
                              PTR_s__sync_module_framework_idle_stat_0045d540,uVar2);
        }
        file_heap_free(*(undefined4 *)(local_1c + 8));
        file_heap_free(local_1c);
      }
    }
    iVar5 = SVC_Settings_AppLaunchCheck();
    if (iVar5 == 1) {
      *(undefined2 *)(local_1c + 4) = 3;
      iVar6 = *(int *)(local_1c + 8);
      iVar5 = FUN_0045bbf4();
      if (iVar5 == 1) {
        if (*(int *)(iVar6 + 4) == 1) {
          iVar5 = FUN_0043d0ce();
          if (iVar5 << 0x1e < 0) {
            FUN_0043d574(3,PTR_s_sync_module_framework_0045cd78,
                         PTR_s_D__01_workspace_s200_ap510b_iar__0045cd74,
                         PTR_s__SyncScheduleManagerThreadHandle_0045cd70,0x34e,
                         PTR_s_received_touch_bar_double_click_e_0045d1c0);
          }
          iVar5 = FUN_0043d0ce();
          if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
            compress_log_output(0xc000000,PTR_s__sync_module_framework_received_t_0045d1c4,
                                PTR_s__sync_module_framework_received_t_0045d1c4);
          }
          file_heap_free(*(undefined4 *)(local_1c + 8));
          file_heap_free(local_1c);
          FUN_00464b2e(0x30,0,0,0);
          sVar7 = 0x30;
          sVar8 = 0;
        }
        else {
          iVar5 = FUN_0043d0ce();
          if (iVar5 << 0x1e < 0) {
            FUN_0043d574(3,PTR_s_sync_module_framework_0045cd78,
                         PTR_s_D__01_workspace_s200_ap510b_iar__0045cd74,
                         PTR_s__SyncScheduleManagerThreadHandle_0045cd70,0x356,
                         PTR_s_terminal_mode_drop_it_input_even_0045d1c8,*(undefined4 *)(iVar6 + 4))
            ;
          }
          iVar5 = FUN_0043d0ce();
          if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
            compress_log_output(0xc400000,PTR_s__sync_module_framework_terminal_m_0045d1cc,
                                PTR_s__sync_module_framework_terminal_m_0045d1cc,
                                *(undefined4 *)(iVar6 + 4));
          }
          file_heap_free(*(undefined4 *)(local_1c + 8));
          file_heap_free(local_1c);
        }
      }
      else if (*(int *)(iVar6 + 4) == 1) {
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          FUN_0043d574(3,PTR_s_sync_module_framework_0045cd78,
                       PTR_s_D__01_workspace_s200_ap510b_iar__0045cd74,
                       PTR_s__SyncScheduleManagerThreadHandle_0045cd70,0x35d,
                       PTR_s_received_touch_bar_double_click_e_0045d1c0);
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          compress_log_output(0xc000000,PTR_s__sync_module_framework_received_t_0045d1c4,
                              PTR_s__sync_module_framework_received_t_0045d1c4);
        }
        file_heap_free(*(undefined4 *)(local_1c + 8));
        file_heap_free(local_1c);
        FUN_00464b2e(1,0,0,0);
        sVar7 = 1;
        sVar8 = 0;
      }
      else if (*(int *)(iVar6 + 4) == 6) {
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          FUN_0043d574(4,PTR_s_sync_module_framework_0045cd78,
                       PTR_s_D__01_workspace_s200_ap510b_iar__0045cd74,
                       PTR_s__SyncScheduleManagerThreadHandle_0045cd70,0x365,
                       PTR_s_received_imu_sensor_lookup_event_0045d1d0);
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          compress_log_output(0x10000000,PTR_s__sync_module_framework_received_i_0045d1d4,
                              PTR_s__sync_module_framework_received_i_0045d1d4);
        }
        file_heap_free(*(undefined4 *)(local_1c + 8));
        file_heap_free(local_1c);
        iVar5 = FUN_0045ba3c();
        if (0 < iVar5) {
          iVar5 = FUN_00442d64();
          if (iVar5 == 0) {
            iVar5 = FUN_0043d0ce();
            if (iVar5 << 0x1e < 0) {
              FUN_0043d574(4,PTR_s_sync_module_framework_0045cd78,
                           PTR_s_D__01_workspace_s200_ap510b_iar__0045cd74,
                           PTR_s__SyncScheduleManagerThreadHandle_0045cd70,0x36a,
                           PTR_s_imu_startup_enable_start_up_dash_0045d1d8);
            }
            iVar5 = FUN_0043d0ce();
            if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
              compress_log_output(0x10000000,PTR_s__sync_module_framework_imu_start_0045d1dc,
                                  PTR_s__sync_module_framework_imu_start_0045d1dc);
            }
            FUN_00464b2e(1,0,0,0);
            sVar7 = 1;
            sVar8 = 0;
          }
          else {
            iVar5 = FUN_0043d0ce();
            if (iVar5 << 0x1e < 0) {
              FUN_0043d574(4,PTR_s_sync_module_framework_0045cd78,
                           PTR_s_D__01_workspace_s200_ap510b_iar__0045cd74,
                           PTR_s__SyncScheduleManagerThreadHandle_0045cd70,0x370,
                           PTR_s_onboarding_is_running_drop_it_0045d1e0);
            }
            iVar5 = FUN_0043d0ce();
            if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
              compress_log_output(0x10000000,PTR_s__sync_module_framework_onboardin_0045d1e4,
                                  PTR_s__sync_module_framework_onboardin_0045d1e4);
            }
          }
        }
      }
      else if (*(int *)(iVar6 + 4) == 3) {
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          FUN_0043d574(4,PTR_s_sync_module_framework_0045cd78,
                       PTR_s_D__01_workspace_s200_ap510b_iar__0045cd74,
                       PTR_s__SyncScheduleManagerThreadHandle_0045cd70,0x376,
                       PTR_s_received_touch_bar_long_press_ev_0045d1e8);
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          compress_log_output(0x10000000,PTR_s__sync_module_framework_received_t_0045d324,
                              PTR_s__sync_module_framework_received_t_0045d324);
        }
        uVar2 = *(undefined2 *)(iVar6 + 2);
        uVar9 = *(undefined4 *)(iVar6 + 4);
        file_heap_free(*(undefined4 *)(local_1c + 8));
        file_heap_free(local_1c);
        iVar5 = FUN_00442ba8(0,uVar2,uVar9);
        iVar6 = FUN_0043d0ce();
        if (iVar6 << 0x1e < 0) {
          FUN_0043d574(4,PTR_s_sync_module_framework_0045cd78,
                       PTR_s_D__01_workspace_s200_ap510b_iar__0045cd74,
                       PTR_s__SyncScheduleManagerThreadHandle_0045cd70,0x37c,
                       PTR_s_startUpAppID____d_0045d328,iVar5);
        }
        iVar6 = FUN_0043d0ce();
        if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
          compress_log_output(0x10400000,PTR_s__sync_module_framework_startUpAp_0045d32c,
                              PTR_s__sync_module_framework_startUpAp_0045d32c,iVar5);
        }
        if (iVar5 == 0) {
          iVar5 = FUN_0043d0ce();
          if (iVar5 << 0x1e < 0) {
            FUN_0043d574(4,PTR_s_sync_module_framework_0045cd78,
                         PTR_s_D__01_workspace_s200_ap510b_iar__0045cd74,
                         PTR_s__SyncScheduleManagerThreadHandle_0045cd70,0x37f,
                         PTR_s_startUpAppID_is_0_drop_it_0045d330);
          }
          iVar5 = FUN_0043d0ce();
          if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
            compress_log_output(0x10000000,PTR_s__sync_module_framework_startUpAp_0045d334,
                                PTR_s__sync_module_framework_startUpAp_0045d334);
          }
        }
        else if (iVar5 == 3) {
          iVar5 = FUN_0043d0ce();
          if (iVar5 << 0x1e < 0) {
            FUN_0043d574(4,PTR_s_sync_module_framework_0045cd78,
                         PTR_s_D__01_workspace_s200_ap510b_iar__0045cd74,
                         PTR_s__SyncScheduleManagerThreadHandle_0045cd70,899,
                         PTR_s_startUpAppID_is_SID_UI_FOREGROUN_0045d338);
          }
          iVar5 = FUN_0043d0ce();
          if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
            compress_log_output(0x10000000,PTR_s__sync_module_framework_startUpAp_0045d33c,
                                PTR_s__sync_module_framework_startUpAp_0045d33c);
          }
          FUN_00460424(0x1e);
          sVar7 = 1;
          FUN_00464b2e(1,0,0,0);
          FUN_00464b2e(3,0,0,0);
          sVar8 = 0;
        }
        else {
          iVar6 = FUN_0043d0ce();
          if (iVar6 << 0x1e < 0) {
            FUN_0043d574(2,PTR_s_sync_module_framework_0045cd78,
                         PTR_s_D__01_workspace_s200_ap510b_iar__0045cd74,
                         PTR_s__SyncScheduleManagerThreadHandle_0045cd70,0x38c,
                         PTR_s_startUpAppID_is_invalid____d_0045d340,iVar5);
          }
          iVar6 = FUN_0043d0ce();
          if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
            compress_log_output(0x8400000,PTR_s__sync_module_framework_startUpAp_0045d344,
                                PTR_s__sync_module_framework_startUpAp_0045d344,iVar5);
          }
        }
      }
      else {
        file_heap_free(*(undefined4 *)(local_1c + 8));
        file_heap_free(local_1c);
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          FUN_0043d574(4,PTR_s_sync_module_framework_0045cd78,
                       PTR_s_D__01_workspace_s200_ap510b_iar__0045cd74,
                       PTR_s__SyncScheduleManagerThreadHandle_0045cd70,0x396,
                       PTR_s_idle_only_support_touch_bar_doub_0045d348);
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          compress_log_output(0x10000000,DAT_0045d4b4,DAT_0045d4b4);
        }
      }
    }
    else {
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        FUN_0043d574(3,PTR_s_sync_module_framework_0045cd78,
                     PTR_s_D__01_workspace_s200_ap510b_iar__0045cd74,
                     PTR_s__SyncScheduleManagerThreadHandle_0045cd70,0x39a,DAT_0045d140);
      }
      iVar5 = FUN_0043d0ce();
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        compress_log_output(0xc000000,DAT_0045d144,DAT_0045d144);
      }
      file_heap_free(*(undefined4 *)(local_1c + 8));
      file_heap_free(local_1c);
    }
  } while( true );
}

