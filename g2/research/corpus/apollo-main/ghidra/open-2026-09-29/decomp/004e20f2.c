
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_004e20f2(char param_1)

{
  byte bVar1;
  char *pcVar2;
  undefined4 *puVar3;
  undefined1 uVar4;
  int iVar5;
  int iVar6;
  uint uVar7;
  int iVar8;
  undefined4 uStack_38;
  undefined4 uStack_34;
  uint uStack_30;
  undefined4 uStack_2c;
  int iStack_28;
  int iStack_24;
  
  iVar5 = FUN_0043d0ce();
  if (iVar5 << 0x1e < 0) {
    uStack_2c = (uint)*(byte *)(_DAT_004e2c24 + 2);
    uStack_30 = (uint)*(byte *)(_DAT_004e2c24 + 1);
    uStack_34 = PTR_s__even_ai_action_id____d__action__004e2c2c;
    uStack_38 = 0x86;
    FUN_0043d574(3,PTR_s_even_ai_page_004e2a50,PTR_s_D__01_workspace_s200_ap510b_iar__004e2a4c,
                 PTR_s_even_ai_async_update_data_004e2c30);
  }
  iVar5 = FUN_0043d0ce();
  if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
    uStack_38 = (uint)*(byte *)(_DAT_004e2c24 + 2);
    compress_log_output(0xc800000,PTR_s__even_ai_page__even_ai_action_id_004e2c34,
                        PTR_s__even_ai_page__even_ai_action_id_004e2c34,
                        *(undefined1 *)(_DAT_004e2c24 + 1));
  }
  pcVar2 = _DAT_004e2c38;
  iVar5 = _DAT_004e2c24;
  bVar1 = *(byte *)(_DAT_004e2c24 + 1);
  if (bVar1 == 1) {
    bVar1 = *(byte *)(_DAT_004e2c24 + 2);
    if (bVar1 == 1) {
      FUN_004e1fa6();
      FUN_0043c0e4(&uStack_2c,4,0);
      if (((*(char *)(iVar5 + 0x13) == '\0') || (iVar8 = FUN_00443484(), iVar8 != 1)) ||
         (iVar8 = FUN_004434d0(7), iVar8 != 1)) {
        iVar8 = UX_GetSystemBLEStatus();
        if (iVar8 == 1) {
          AUDM_appAcquire(3);
          even_ai_timer_start_all(5000);
        }
        else {
          *(undefined1 *)(iVar5 + 1) = 7;
          *(undefined1 *)(iVar5 + 2) = 2;
          even_ai_timer_start_all(3000);
        }
        even_ai_init_text_stream_service();
        pcVar2 = _DAT_004e2c38;
        if ((*_DAT_004e2c38 == '\x03') || (*_DAT_004e2c38 == '\x04')) {
          even_ai_stop_current_streaming(0);
        }
        else {
          even_ai_stop_current_streaming(1);
        }
        *pcVar2 = *(char *)(iVar5 + 1);
        pcVar2[1] = *(char *)(iVar5 + 2);
        uStack_2c = CONCAT31(uStack_2c._1_3_,3);
      }
      else {
        uStack_2c = CONCAT13((char)((ushort)*(undefined2 *)(iVar5 + 0x14) >> 8),
                             CONCAT12((char)*(undefined2 *)(iVar5 + 0x14),
                                      CONCAT11(*(undefined1 *)(iVar5 + 0x13),8)));
      }
      iVar5 = _DAT_004e2c3c;
      pcVar2 = _DAT_004e2c38;
      _DAT_004e2c38[8] = *(byte *)(_DAT_004e2c3c + 1) & 0xf0;
      pcVar2[9] = *(char *)(iVar5 + 2);
      pcVar2[0xd] = '\0';
      FUN_004e1fbe();
      if (param_1 == '\0') {
        iVar5 = FUN_00443484();
        if ((iVar5 == 1) && (iVar5 = FUN_004434d0(7), iVar5 == 1)) {
          FUN_004e1fd2(1,&uStack_2c,4);
        }
        else {
          FUN_004e1fd2(0,0,0);
        }
      }
    }
    else if (bVar1 != 0) {
      if (bVar1 == 3) {
        *_DAT_004e2c38 = *(char *)(_DAT_004e2c24 + 1);
        pcVar2[1] = *(char *)(iVar5 + 2);
        pcVar2[0xd] = '\0';
        if (param_1 == '\0') {
          FUN_004e1fd2(2,0,0);
        }
      }
      else if (bVar1 < 3) {
        FUN_004e1fa6();
        pcVar2 = _DAT_004e2c38;
        if (_DAT_004e2c38[1] == '\x01') {
          *_DAT_004e2c38 = *(char *)(iVar5 + 1);
          pcVar2[1] = *(char *)(iVar5 + 2);
          even_ai_common_timer_mgr_stop();
          FUN_004e1fbe();
        }
        else {
          even_ai_init_text_stream_service();
          if ((*pcVar2 == '\x03') || (*pcVar2 == '\x04')) {
            even_ai_stop_current_streaming(0);
          }
          else {
            even_ai_stop_current_streaming(1);
          }
          even_ai_common_timer_mgr_stop();
          AUDM_appAcquire(3);
          *pcVar2 = *(char *)(iVar5 + 1);
          pcVar2[1] = *(char *)(iVar5 + 2);
          pcVar2[9] = *(char *)(_DAT_004e2c3c + 2);
          pcVar2[0xd] = '\0';
          FUN_004e1fbe();
          if (param_1 == '\0') {
            iVar5 = FUN_00443484();
            if ((iVar5 == 1) && (iVar5 = FUN_004434d0(7), iVar5 == 1)) {
              uStack_30 = CONCAT31(uStack_30._1_3_,*PTR_DAT_004e2d6c);
              FUN_004e1fd2(1,&uStack_30,1);
            }
            else {
              FUN_004e1fd2(0,0,0);
            }
          }
        }
      }
    }
  }
  else if (bVar1 != 0) {
    if (bVar1 == 3) {
      iVar8 = FUN_0043d0ce();
      if (iVar8 << 0x1e < 0) {
        iStack_28 = iVar5 + 0x18;
        uStack_2c = 3;
        uStack_30 = (uint)*(ushort *)(iVar5 + 0x16);
        uStack_34 = PTR_s_recv_evenai_text_len____d__text___004e2d70;
        uStack_38 = 0x13a;
        FUN_0043d574(3,PTR_s_even_ai_page_004e2a50,PTR_s_D__01_workspace_s200_ap510b_iar__004e2a4c,
                     PTR_s_even_ai_async_update_data_004e2c30);
      }
      iVar8 = FUN_0043d0ce();
      if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
        uStack_34 = (undefined *)(iVar5 + 0x18);
        uStack_38 = 3;
        compress_log_output(0xcc00000,PTR_s__even_ai_page_recv_evenai_text_l_004e2d74,
                            PTR_s__even_ai_page_recv_evenai_text_l_004e2d74,
                            *(undefined2 *)(iVar5 + 0x16));
      }
      FUN_004e1fa6();
      even_ai_timer_start_all(8000);
      pcVar2 = _DAT_004e2c38;
      if ((*_DAT_004e2c38 == '\x01') || (*_DAT_004e2c38 == '\x04')) {
        iVar6 = text_stream_pending_text(*_DAT_004e2d78);
        uVar7 = FUN_0044a43c(iVar6);
        iVar8 = _DAT_004e2d7c;
        if (0x3ff < uVar7) {
          uVar7 = 0x400;
        }
        if ((iVar6 != 0) && (uVar7 != 0)) {
          FUN_0044b5a0(_DAT_004e2d7c,iVar6,uVar7);
          *(undefined1 *)(iVar8 + uVar7) = 0;
        }
      }
      else if (*_DAT_004e2c38 != '\x03') {
        FUN_0043c0e4(_DAT_004e2d7c,0x400,0);
        even_ai_stop_current_streaming(1);
      }
      *pcVar2 = *(char *)(iVar5 + 1);
      pcVar2[0xd] = '\x01';
      *(undefined2 *)(pcVar2 + 0xe) = *(undefined2 *)(iVar5 + 0x16);
      FUN_00439be4(pcVar2 + 0x10,iVar5 + 0x18,*(undefined2 *)(iVar5 + 0x16));
      if (*(ushort *)(pcVar2 + 0xe) < 0x200) {
        pcVar2[*(ushort *)(pcVar2 + 0xe) + 0x10] = '\0';
      }
      iVar6 = _DAT_004e2d80;
      FUN_0043c0e4(_DAT_004e2d80,0x400,0);
      iVar8 = _DAT_004e2d7c;
      uVar7 = FUN_0044a43c(_DAT_004e2d7c);
      if ((uVar7 < 0x3ff) && (uVar7 + *(ushort *)(iVar5 + 0x16) < 0x3ff)) {
        if (uVar7 != 0) {
          FUN_0044b5a0(iVar6,iVar8,uVar7);
        }
      }
      else {
        FUN_0043c0e4(iVar8,0x400,0);
        uVar7 = 0;
      }
      if (*(short *)(iVar5 + 0x16) != 0) {
        FUN_0044b5a0(iVar6 + uVar7,iVar5 + 0x18,*(undefined2 *)(iVar5 + 0x16));
        *(undefined1 *)(iVar6 + uVar7 + *(ushort *)(iVar5 + 0x16)) = 0;
      }
      uVar4 = even_ai_stream_interval_get();
      puVar3 = _DAT_004e2d78;
      uStack_38 = 0;
      text_stream_set_text(*_DAT_004e2d78,iVar6,uVar4,0);
      if (uVar7 != 0) {
        text_stream_copy_bytes(*puVar3,uVar7 & 0xffff,0);
      }
      FUN_004e1fbe();
      if (param_1 == '\0') {
        uStack_34 = (undefined *)CONCAT13(*PTR_DAT_004e2d84,(undefined3)uStack_34);
        FUN_004e1fd2(1,(int)&uStack_34 + 3,1);
      }
    }
    else if (2 < bVar1) {
      if (bVar1 == 5) {
        if (_DAT_004e2c38[0xd] == '\0') {
          iVar5 = FUN_0043d0ce();
          if (iVar5 << 0x1e < 0) {
            uStack_34 = PTR_s_not_asked__not_allow_to_show_rep_004e2d8c;
            uStack_38 = 0x198;
            FUN_0043d574(2,PTR_s_even_ai_page_004e2a50,
                         PTR_s_D__01_workspace_s200_ap510b_iar__004e2a4c,
                         PTR_s_even_ai_async_update_data_004e2c30);
          }
          iVar5 = FUN_0043d0ce();
          if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
            compress_log_output(0x8000000,PTR_s__even_ai_page_not_asked__not_all_004e2d90,
                                PTR_s__even_ai_page_not_asked__not_all_004e2d90);
          }
        }
        else {
          iVar8 = FUN_0043d0ce();
          if (iVar8 << 0x1e < 0) {
            iStack_24 = iVar5 + 0x18;
            iStack_28 = 3;
            uStack_2c = (uint)*(ushort *)(iVar5 + 0x16);
            uStack_30 = (uint)*(byte *)(iVar5 + 0x12);
            uStack_34 = PTR_s_recv_evenai_f_text_end____d__tex_004e2d94;
            uStack_38 = 0x19d;
            FUN_0043d574(3,PTR_s_even_ai_page_004e2a50,
                         PTR_s_D__01_workspace_s200_ap510b_iar__004e2a4c,
                         PTR_s_even_ai_async_update_data_004e2c30);
          }
          iVar8 = FUN_0043d0ce();
          if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
            uStack_30 = iVar5 + 0x18;
            uStack_34 = (undefined *)0x3;
            uStack_38 = (uint)*(ushort *)(iVar5 + 0x16);
            compress_log_output(0xd000000,PTR_s__even_ai_page_recv_evenai_f_text_004e2d98,
                                PTR_s__even_ai_page_recv_evenai_f_text_004e2d98,
                                *(undefined1 *)(iVar5 + 0x12));
          }
          FUN_004e1fa6();
          even_ai_timer_start_all(10000);
          if (*pcVar2 != '\x05') {
            iVar8 = FUN_0043d0ce();
            if (iVar8 << 0x1e < 0) {
              uStack_34 = PTR_s_stop_current_streaming__avoid_te_004e2d9c;
              uStack_38 = 0x1aa;
              FUN_0043d574(3,PTR_s_even_ai_page_004e2a50,
                           PTR_s_D__01_workspace_s200_ap510b_iar__004e2a4c,
                           PTR_s_even_ai_async_update_data_004e2c30);
            }
            iVar8 = FUN_0043d0ce();
            if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
              compress_log_output(0xc000000,PTR_s__even_ai_page_stop_current_strea_004e2da0,
                                  PTR_s__even_ai_page_stop_current_strea_004e2da0);
            }
            even_ai_stop_current_streaming(1);
            FUN_0043c0e4(_DAT_004e2d7c,0x400,0);
          }
          *pcVar2 = *(char *)(iVar5 + 1);
          pcVar2[0xc] = *(char *)(iVar5 + 0x12);
          *(undefined2 *)(pcVar2 + 0xe) = *(undefined2 *)(iVar5 + 0x16);
          if (*(short *)(pcVar2 + 0xe) != 0) {
            FUN_00439be4(pcVar2 + 0x10,iVar5 + 0x18,*(undefined2 *)(iVar5 + 0x16));
            if (*(ushort *)(pcVar2 + 0xe) < 0x200) {
              pcVar2[*(ushort *)(pcVar2 + 0xe) + 0x10] = '\0';
            }
            uVar4 = even_ai_stream_interval_get();
            uStack_38 = 0;
            text_stream_set_text(*_DAT_004e2d78,pcVar2 + 0x10,uVar4,1);
          }
          FUN_004e1fbe();
          if (param_1 == '\0') {
            uStack_34._0_2_ = CONCAT11(*PTR_DAT_004e2da4,(undefined1)uStack_34);
            FUN_004e1fd2(1,(int)&uStack_34 + 1,1);
          }
        }
      }
      else if (bVar1 < 5) {
        FUN_004e1fa6();
        pcVar2 = _DAT_004e2c38;
        *_DAT_004e2c38 = *(char *)(iVar5 + 1);
        pcVar2[0xd] = '\x01';
        FUN_004e1fbe();
        if (param_1 == '\0') {
          uStack_34._0_3_ = CONCAT12(*PTR_DAT_004e2d88,(undefined2)uStack_34);
          FUN_004e1fd2(1,(int)&uStack_34 + 2,1);
        }
      }
      else if (bVar1 == 7) {
        FUN_004e1fa6();
        even_ai_timer_start_all(3000);
        pcVar2 = _DAT_004e2c38;
        if (*_DAT_004e2c38 != '\a') {
          FUN_0043c0e4(_DAT_004e2d7c,0x400,0);
        }
        *pcVar2 = *(char *)(iVar5 + 1);
        pcVar2[1] = *(char *)(iVar5 + 2);
        FUN_004e1fbe();
        if (param_1 == '\0') {
          uStack_38 = CONCAT31(uStack_38._1_3_,*PTR_DAT_004e2dc8);
          FUN_004e1fd2(1,&uStack_38,1);
        }
      }
      else if (bVar1 < 7) {
        if (_DAT_004e2c38[0xd] == '\0') {
          iVar5 = FUN_0043d0ce();
          if (iVar5 << 0x1e < 0) {
            uStack_34 = PTR_s_not_asked__not_allow_to_show_ski_004e2da8;
            uStack_38 = 0x1cf;
            FUN_0043d574(2,PTR_s_even_ai_page_004e2a50,
                         PTR_s_D__01_workspace_s200_ap510b_iar__004e2a4c,
                         PTR_s_even_ai_async_update_data_004e2c30);
          }
          iVar5 = FUN_0043d0ce();
          if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
            compress_log_output(0x8000000,PTR_s__even_ai_page_not_asked__not_all_004e2dac,
                                PTR_s__even_ai_page_not_asked__not_all_004e2dac);
          }
        }
        else {
          iVar8 = FUN_0043d0ce();
          if (iVar8 << 0x1e < 0) {
            uStack_30 = *(uint *)(iVar5 + 0xc);
            uStack_34 = PTR_s_recv_evenai_skill_param____d_004e2db0;
            uStack_38 = 0x1d3;
            FUN_0043d574(3,PTR_s_even_ai_page_004e2a50,
                         PTR_s_D__01_workspace_s200_ap510b_iar__004e2a4c,
                         PTR_s_even_ai_async_update_data_004e2c30);
          }
          iVar8 = FUN_0043d0ce();
          if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
            compress_log_output(0xc400000,PTR_s__even_ai_page_recv_evenai_skill__004e2db4,
                                PTR_s__even_ai_page_recv_evenai_skill__004e2db4,
                                *(undefined4 *)(iVar5 + 0xc));
          }
          iVar8 = FUN_0043d0ce();
          if (iVar8 << 0x1e < 0) {
            iStack_24 = iVar5 + 0x18;
            iStack_28 = 3;
            uStack_2c = (uint)*(ushort *)(iVar5 + 0x16);
            uStack_30 = (uint)*(byte *)(iVar5 + 0x12);
            uStack_34 = PTR_s_recv_evenai_f_text_end____d__tex_004e2d94;
            uStack_38 = 0x1d5;
            FUN_0043d574(3,PTR_s_even_ai_page_004e2a50,
                         PTR_s_D__01_workspace_s200_ap510b_iar__004e2a4c,
                         PTR_s_even_ai_async_update_data_004e2c30);
          }
          iVar8 = FUN_0043d0ce();
          if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
            uStack_30 = iVar5 + 0x18;
            uStack_34 = (undefined *)0x3;
            uStack_38 = (uint)*(ushort *)(iVar5 + 0x16);
            compress_log_output(0xd000000,PTR_s__even_ai_page_recv_evenai_f_text_004e2d98,
                                PTR_s__even_ai_page_recv_evenai_f_text_004e2d98,
                                *(undefined1 *)(iVar5 + 0x12));
          }
          FUN_004e1fa6();
          even_ai_timer_start_all(10000);
          if (*pcVar2 != '\x06') {
            even_ai_stop_current_streaming(1);
            FUN_0043c0e4(_DAT_004e2d7c,0x400,0);
          }
          *pcVar2 = *(char *)(iVar5 + 1);
          pcVar2[1] = *(char *)(iVar5 + 2);
          *(undefined4 *)(pcVar2 + 4) = *(undefined4 *)(iVar5 + 0xc);
          pcVar2[0xc] = *(char *)(iVar5 + 0x12);
          *(undefined2 *)(pcVar2 + 0xe) = *(undefined2 *)(iVar5 + 0x16);
          if ((*(short *)(pcVar2 + 0xe) != 0) &&
             (FUN_00439be4(pcVar2 + 0x10,iVar5 + 0x18,*(undefined2 *)(iVar5 + 0x16)),
             *(ushort *)(pcVar2 + 0xe) < 0x200)) {
            pcVar2[*(ushort *)(pcVar2 + 0xe) + 0x10] = '\0';
          }
          FUN_004e1fbe();
          bVar1 = pcVar2[1];
          if (bVar1 == 1) {
            if (param_1 == '\0') {
              uStack_34 = (undefined *)CONCAT31(uStack_34._1_3_,*PTR_DAT_004e2db8);
              FUN_004e1fd2(1,&uStack_34,1);
            }
          }
          else if (bVar1 != 0) {
            if (bVar1 == 3) {
              if (*(int *)(pcVar2 + 4) == 1) {
                if (param_1 == '\0') {
                  FUN_004e1fd2(2,0,0);
                }
                service_ancc_state_sync(4,500);
              }
              else {
                if (*(int *)(pcVar2 + 4) == 2) {
                  func_0x004973f4(1);
                }
                if (param_1 == '\0') {
                  uStack_38 = CONCAT13(*PTR_DAT_004e2dbc,(undefined3)uStack_38);
                  FUN_004e1fd2(1,(int)&uStack_38 + 3,1);
                }
              }
            }
            else if (2 < bVar1) {
              if (bVar1 != 5) {
                if (bVar1 < 5) {
                  return;
                }
                if ((bVar1 != 7) && (6 < bVar1)) {
                  if (bVar1 != 8) {
                    return;
                  }
                  if (param_1 != '\0') {
                    return;
                  }
                  uStack_38._0_2_ = CONCAT11(*PTR_DAT_004e2dc4,(undefined1)uStack_38);
                  FUN_004e1fd2(1,(int)&uStack_38 + 1,1);
                  return;
                }
              }
              if (*(int *)(pcVar2 + 4) == 0) {
                FUN_004e1fa6();
                uVar4 = even_ai_stream_interval_get();
                uStack_38 = 0;
                text_stream_set_text(*_DAT_004e2d78,pcVar2 + 0x10,uVar4,1);
                FUN_004e1fbe();
                if (param_1 == '\0') {
                  uStack_38._0_3_ = CONCAT12(*PTR_DAT_004e2dc0,(undefined2)uStack_38);
                  FUN_004e1fd2(1,(int)&uStack_38 + 2,1);
                }
              }
            }
          }
        }
      }
    }
  }
  return;
}

