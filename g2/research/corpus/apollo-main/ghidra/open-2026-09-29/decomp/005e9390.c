
undefined4
terminal_action_agent_content
          (char *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  char cVar1;
  char cVar2;
  char cVar3;
  undefined4 uVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  uint uVar8;
  char cVar9;
  uint uVar10;
  char cVar11;
  int iVar12;
  bool bVar13;
  bool bVar14;
  bool bVar15;
  char cVar16;
  char local_34;
  char local_32;
  undefined2 local_2c [2];
  undefined4 uStack_28;
  
  local_34 = '\0';
  local_2c[0] = 0xffff;
  uVar8 = 0;
  iVar12 = 0;
  cVar16 = '\0';
  cVar9 = '\0';
  local_32 = '\0';
  if (param_1 == (char *)0x0) {
    uVar4 = 0xffffffff;
  }
  else {
    uStack_28 = param_4;
    iVar5 = terminal_message_session_matches(*(undefined4 *)(param_1 + 0x210),DAT_005e9ec4);
    if (iVar5 == 0) {
      uVar4 = 0;
    }
    else {
      iVar5 = *(int *)(param_1 + 0x208);
      bVar13 = *(short *)(param_1 + 2) != 0;
      if (bVar13) {
        local_34 = terminal_data_append_agent_content(param_1,local_2c);
        if (local_34 == '\0') {
          iVar6 = FUN_0043d0ce();
          if (iVar6 << 0x1e < 0) {
            FUN_0043d574(2,PTR_s_terminal_pb_005e9f68,
                         PTR_s_D__01_workspace_s200_ap510b_iar__005e9f64,
                         PTR_s_terminal_action_agent_content_005e9f60,0x215,
                         PTR_s_ignore_terminal_agent_text_conte_005e9f5c,param_1[0x204],iVar5,
                         *(undefined2 *)(param_1 + 2));
          }
          iVar6 = FUN_0043d0ce();
          if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
            compress_log_output(0x8c00000,PTR_s__terminal_pb_ignore_terminal_age_005e9f6c,
                                PTR_s__terminal_pb_ignore_terminal_age_005e9f6c,param_1[0x204],iVar5
                                ,*(undefined2 *)(param_1 + 2));
          }
        }
        else {
          uVar4 = FUN_005e5166(local_34,local_2c[0]);
          terminal_request_display(0x12,uVar4);
          cVar9 = '\x01';
        }
      }
      else {
        iVar6 = FUN_0043d0ce();
        if (iVar6 << 0x1e < 0) {
          FUN_0043d574(4,PTR_s_terminal_pb_005e9f68,PTR_s_D__01_workspace_s200_ap510b_iar__005e9f64,
                       PTR_s_terminal_action_agent_content_005e9f60,0x21d,
                       PTR_s_skip_terminal_agent_text_append__005e9f70,param_1[0x204],iVar5,*param_1
                       ,param_1[0x20c]);
        }
        iVar6 = FUN_0043d0ce();
        if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
          compress_log_output(0x11000000,DAT_005ea000,DAT_005ea000,param_1[0x204],iVar5,*param_1,
                              param_1[0x20c]);
        }
      }
      iVar6 = DAT_005ea01c;
      cVar1 = param_1[0x20c];
      cVar2 = param_1[0x20c];
      bVar14 = param_1[0x20c] == '\x04';
      if ((param_1[0x20c] == '\x03') || (((bVar13 && (*param_1 == '\0')) && (!bVar14)))) {
        cVar11 = '\x01';
      }
      else {
        cVar11 = '\0';
      }
      bVar15 = *(char *)(DAT_005ea01c + 0x275) == '\a';
      cVar3 = *(char *)(DAT_005ea01c + 0x294);
      if (bVar15) {
        if (bVar14) {
          *(undefined1 *)(DAT_005ea01c + 0x294) = 0;
        }
        if (cVar2 == '\x02') {
          uVar8 = 2;
        }
        if (bVar14) {
          iVar12 = osKernelGetTickCount();
          uVar8 = uVar8 | 9;
          *(int *)(iVar6 + 0x298) = iVar12;
          cVar16 = '\x01';
        }
        if (cVar11 != '\0') {
          uVar8 = uVar8 | 4;
          if (*(char *)(iVar6 + 0x294) == '\0') {
            *(undefined1 *)(iVar6 + 0x294) = 1;
          }
          else {
            iVar7 = FUN_0043d0ce();
            if (iVar7 << 0x1e < 0) {
              FUN_0043d574(4,PTR_s_terminal_pb_005e9f68,
                           PTR_s_D__01_workspace_s200_ap510b_iar__005e9f64,
                           PTR_s_terminal_action_agent_content_005e9f60,0x23d,DAT_005ea020,iVar5);
            }
            iVar7 = FUN_0043d0ce();
            if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
              compress_log_output(0x10400000,DAT_005ea024,DAT_005ea024,iVar5);
            }
          }
        }
        if (cVar1 == '\x01') {
          iVar7 = osKernelGetTickCount();
          if (*(int *)(iVar6 + 0x298) == 0) {
            uVar10 = 2000;
          }
          else {
            uVar10 = iVar7 - *(int *)(iVar6 + 0x298);
          }
          if ((*(int *)(iVar6 + 0x298) == 0) || (1999 < uVar10)) {
            bVar14 = true;
          }
          else {
            bVar14 = false;
          }
          if (bVar14) {
            *(int *)(iVar6 + 0x298) = iVar7;
            uVar8 = uVar8 | 1;
          }
          else {
            iVar7 = FUN_0043d0ce();
            if (iVar7 << 0x1e < 0) {
              FUN_0043d574(4,PTR_s_terminal_pb_005e9f68,
                           PTR_s_D__01_workspace_s200_ap510b_iar__005e9f64,
                           PTR_s_terminal_action_agent_content_005e9f60,0x24a,
                           PTR_s_drop_tool_start_within_2s__id__l_005ea154,iVar5,uVar10);
            }
            iVar7 = FUN_0043d0ce();
            if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
              compress_log_output(0x10800000,PTR_s__terminal_pb_drop_tool_start_wit_005ea158,
                                  PTR_s__terminal_pb_drop_tool_start_wit_005ea158,iVar5,uVar10);
            }
          }
        }
        if (uVar8 != 0) {
          if ((cVar16 == '\0') && (iVar12 = iVar5, iVar5 == 0)) {
            iVar12 = osKernelGetTickCount();
          }
          uVar4 = FUN_005e51b0(uVar8,iVar12);
          terminal_request_display(0x13,uVar4);
          local_32 = '\x01';
        }
      }
      else if ((param_1[0x20c] != '\0') || (cVar11 != '\0')) {
        iVar7 = FUN_0043d0ce();
        if (iVar7 << 0x1e < 0) {
          FUN_0043d574(4,PTR_s_terminal_pb_005e9f68,PTR_s_D__01_workspace_s200_ap510b_iar__005e9f64,
                       PTR_s_terminal_action_agent_content_005e9f60,599,
                       PTR_s_drop_content_trigger_event_in_no_005ea15c,
                       *(undefined1 *)(iVar6 + 0x275),param_1[0x20c],*param_1);
        }
        iVar7 = FUN_0043d0ce();
        if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
          compress_log_output(0x10c00000,PTR_s__terminal_pb_drop_content_trigge_005ea160,
                              PTR_s__terminal_pb_drop_content_trigge_005ea160,
                              *(undefined1 *)(iVar6 + 0x275),param_1[0x20c],*param_1);
        }
      }
      iVar7 = FUN_0043d0ce();
      if (iVar7 << 0x1e < 0) {
        FUN_0043d574(3,PTR_s_terminal_pb_005e9f68,PTR_s_D__01_workspace_s200_ap510b_iar__005e9f64,
                     PTR_s_terminal_action_agent_content_005e9f60,0x25e,
                     PTR_s_recv_terminal_agent_content__op__005ea164,param_1[0x204],iVar5,local_34,
                     local_2c[0],*param_1,param_1[0x20c],bVar15,cVar3 != '\0',
                     *(char *)(iVar6 + 0x294) != '\0',cVar11,uVar8,iVar12,
                     *(undefined2 *)(param_1 + 2),cVar9,local_32);
      }
      iVar7 = FUN_0043d0ce();
      if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
        compress_log_output(uVar8 << 0x16 | 0xc000000,
                            PTR_s__terminal_pb_recv_terminal_agent_005ea168,
                            PTR_s__terminal_pb_recv_terminal_agent_005ea168,param_1[0x204],iVar5,
                            local_34,local_2c[0],*param_1,param_1[0x20c],bVar15,cVar3 != '\0',
                            *(char *)(iVar6 + 0x294) != '\0',cVar11,uVar8,iVar12,
                            *(undefined2 *)(param_1 + 2),cVar9,local_32);
      }
      iVar12 = FUN_0043d0ce();
      if (iVar12 << 0x1e < 0) {
        FUN_0043d574(3,PTR_s_terminal_pb_005e9f68,PTR_s_D__01_workspace_s200_ap510b_iar__005e9f64,
                     PTR_s_terminal_action_agent_content_005e9f60,0x25f,
                     PTR_s_len___d__text___s_005ea16c,*(undefined2 *)(param_1 + 2),param_1 + 4);
      }
      iVar12 = FUN_0043d0ce();
      if ((iVar12 << 0x1f < 0) || (iVar12 = FUN_0043d0ce(), iVar12 << 0x1d < 0)) {
        compress_log_output(0xc800000,PTR_s__terminal_pb_len___d__text___s_005ea170,
                            PTR_s__terminal_pb_len___d__text___s_005ea170,
                            *(undefined2 *)(param_1 + 2),param_1 + 4);
      }
      if (cVar9 == '\0' && local_32 == '\0') {
        if (bVar13) {
          uVar4 = 0xffffffff;
        }
        else {
          uVar4 = 0;
        }
      }
      else {
        uVar4 = 0;
      }
    }
  }
  return uVar4;
}

