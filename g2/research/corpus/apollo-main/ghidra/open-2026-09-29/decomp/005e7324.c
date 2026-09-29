
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_005e7324(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  bool bVar1;
  undefined1 uVar2;
  byte bVar3;
  char cVar4;
  short sVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  int iVar10;
  undefined4 uVar11;
  undefined4 uVar12;
  char cVar13;
  char cVar14;
  char cVar15;
  char cVar16;
  uint uVar17;
  
  iVar9 = _DAT_005e7e0c;
  iVar6 = td_state_ptr_alias1();
  iVar7 = *(int *)(param_2 + 0x10);
  iVar8 = FUN_0045a568();
  if (iVar8 == 1) {
    iVar8 = FUN_005e72f4(iVar9);
    if (iVar8 == 0) {
      bVar3 = *(byte *)(iVar9 + 0x275);
      if (bVar3 == 2) {
        if (param_1 == 8) {
          iVar9 = UX_GetSystemBLEStatus();
          if (iVar9 == 0) {
            iVar9 = FUN_0043d0ce();
            if (iVar9 << 0x1e < 0) {
              FUN_0043d574(2,PTR_s_terminal_ui_005e7e1c,
                           PTR_s_D__01_workspace_s200_ap510b_iar__005e7e18,
                           PTR_s_terminal_input_event_handler_005e7e14,0x795,
                           PTR_s_ignore_long_press_voice_start__b_005e7e24);
            }
            iVar9 = FUN_0043d0ce();
            if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
              compress_log_output(0x8000000,PTR_s__terminal_ui_ignore_long_press_v_005e7e28,
                                  PTR_s__terminal_ui_ignore_long_press_v_005e7e28);
            }
          }
          else {
            cVar13 = *(char *)(iVar6 + 0xa1d8);
            if (cVar13 == '\x02') {
              terminal_request_display(8,0);
            }
            else {
              iVar9 = FUN_0043d0ce();
              if (iVar9 << 0x1e < 0) {
                FUN_0043d574(2,PTR_s_terminal_ui_005e7e1c,
                             PTR_s_D__01_workspace_s200_ap510b_iar__005e7e18,
                             PTR_s_terminal_input_event_handler_005e7e14,0x79a,
                             PTR_s_ignore_long_press_voice_start__h_005e7e2c,cVar13);
              }
              iVar9 = FUN_0043d0ce();
              if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
                compress_log_output(0x8400000,PTR_s__terminal_ui_ignore_long_press_v_005e7e30,
                                    PTR_s__terminal_ui_ignore_long_press_v_005e7e30,cVar13);
              }
            }
          }
        }
        else if ((param_1 == 0x44) || (param_1 == 0x45)) {
          if ((*(int *)(iVar9 + 4) != 0) && (iVar7 != 0)) {
            uVar11 = FUN_005e4c2c(iVar9,param_1,iVar7);
            uVar2 = FUN_005e4f1a(iVar9,uVar11);
            uVar11 = FUN_005e4f02(uVar11,uVar2);
            if (param_1 == 0x44) {
              uVar12 = 0x24;
            }
            else {
              uVar12 = 0x25;
            }
            terminal_request_display(uVar12,uVar11);
          }
        }
        else if (param_1 == 0x48) {
          uVar11 = FUN_005ecafa();
          terminal_request_display(0x1b,uVar11);
        }
      }
      else if (1 < bVar3) {
        if (bVar3 == 4) {
          if (param_1 == 0x4a) {
            terminal_request_display(9,0);
          }
        }
        else if (bVar3 < 4) {
          if ((param_1 == 0x44) || (param_1 == 0x45)) {
            if ((*(int *)(iVar9 + 4) != 0) &&
               ((iVar7 != 0 && (iVar6 = FUN_0043e0e0(*(undefined4 *)(iVar9 + 4),1), iVar6 == 0)))) {
              uVar11 = FUN_005e4c2c(iVar9,param_1,iVar7);
              uVar2 = FUN_005e4f1a(iVar9,uVar11);
              uVar11 = FUN_005e4f02(uVar11,uVar2);
              if (param_1 == 0x44) {
                uVar12 = 0x24;
              }
              else {
                uVar12 = 0x25;
              }
              terminal_request_display(uVar12,uVar11);
            }
          }
          else if (param_1 == 0x48) {
            terminal_request_display(0x27,0);
          }
        }
        else if (bVar3 == 6) {
          if (param_1 == 0x48) {
            terminal_request_display(0xe,0);
          }
          else if ((param_1 == 0x44) || (param_1 == 0x45)) {
            iVar6 = osKernelGetTickCount();
            if ((*(int *)(iVar9 + 500) != 0) && (iVar7 != 0)) {
              iVar8 = FUN_005e4bde(iVar9,param_1);
              if (iVar8 != 0) {
                if ((uint)(iVar6 - *(int *)(iVar9 + 0x290)) < 300) {
                  return;
                }
                *(int *)(iVar9 + 0x290) = iVar6;
              }
              uVar11 = FUN_005e4bfe(iVar9,param_1,iVar7);
              uVar11 = FUN_005e4e32(iVar9,param_1,uVar11);
              if (param_1 == 0x44) {
                uVar12 = 0x24;
              }
              else {
                uVar12 = 0x25;
              }
              terminal_request_display(uVar12,uVar11);
            }
          }
          else if (param_1 == 10) {
            if (*(char *)(iVar9 + 0x278) == '\0') {
              uVar11 = FUN_005e4e2e(*(undefined1 *)(iVar9 + 0x278));
              terminal_request_display(0xd,uVar11);
            }
            else if (*(char *)(iVar9 + 0x278) == '\x01') {
              uVar11 = FUN_005e4e2e(*(undefined1 *)(iVar9 + 0x278));
              terminal_request_display(0xe,uVar11);
            }
          }
        }
        else if (bVar3 < 6) {
          if (param_1 == 0x48) {
            terminal_request_display(0xe,0);
          }
        }
        else if (bVar3 == 8) {
          if ((param_1 == 0x44) || (param_1 == 0x45)) {
            uVar11 = FUN_005e4eec(param_1);
            iVar9 = FUN_0043d0ce();
            if (iVar9 << 0x1e < 0) {
              FUN_0043d574(3,PTR_s_terminal_ui_005e7e1c,
                           PTR_s_D__01_workspace_s200_ap510b_iar__005e7e18,
                           PTR_s_terminal_input_event_handler_005e7e14,0x7f8,
                           PTR_s_input__interrupt_confirm_scroll_c_005e7e3c,param_1,uVar11);
            }
            iVar9 = FUN_0043d0ce();
            if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
              compress_log_output(0xc800000,PTR_s__terminal_ui_input__interrupt_co_005e7e40,
                                  PTR_s__terminal_ui_input__interrupt_co_005e7e40,param_1,uVar11);
            }
            if (param_1 == 0x44) {
              uVar2 = 0x24;
            }
            else {
              uVar2 = 0x25;
            }
            terminal_request_display(uVar2,uVar11);
          }
          else if (param_1 == 10) {
            if (*(char *)(iVar9 + 0x278) == '\0') {
              iVar6 = FUN_0043d0ce();
              if (iVar6 << 0x1e < 0) {
                FUN_0043d574(3,PTR_s_terminal_ui_005e7e1c,
                             PTR_s_D__01_workspace_s200_ap510b_iar__005e7e18,
                             PTR_s_terminal_input_event_handler_005e7e14,0x7fc,
                             PTR_s_input__interrupt_confirm_clicked_005e7e44);
              }
              iVar6 = FUN_0043d0ce();
              if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
                compress_log_output(0xc000000,PTR_s__terminal_ui_input__interrupt_co_005e7e48,
                                    PTR_s__terminal_ui_input__interrupt_co_005e7e48);
              }
              uVar11 = FUN_005e4e2e(*(undefined1 *)(iVar9 + 0x278));
              terminal_request_display(0x26,uVar11);
            }
            else if (*(char *)(iVar9 + 0x278) == '\x01') {
              iVar6 = FUN_0043d0ce();
              if (iVar6 << 0x1e < 0) {
                FUN_0043d574(3,PTR_s_terminal_ui_005e7e1c,
                             PTR_s_D__01_workspace_s200_ap510b_iar__005e7e18,
                             PTR_s_terminal_input_event_handler_005e7e14,0x7ff,
                             PTR_s_input__interrupt_confirm_clicked_005e7e4c);
              }
              iVar6 = FUN_0043d0ce();
              if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
                compress_log_output(0xc000000,PTR_s__terminal_ui_input__interrupt_co_005e7e50,
                                    PTR_s__terminal_ui_input__interrupt_co_005e7e50);
              }
              uVar11 = FUN_005e4e2e(*(undefined1 *)(iVar9 + 0x278));
              terminal_request_display(0xe,uVar11);
            }
          }
          else if (param_1 == 0x48) {
            uVar11 = FUN_005ecafa();
            terminal_request_display(0x1b,uVar11);
          }
        }
        else if (bVar3 < 8) {
          if ((param_1 == 0x44) || (param_1 == 0x45)) {
            if ((*(int *)(iVar9 + 4) != 0) && (iVar7 != 0)) {
              uVar11 = FUN_005e4c2c(iVar9,param_1,iVar7);
              uVar2 = FUN_005e4f1a(iVar9,uVar11);
              uVar11 = FUN_005e4f02(uVar11,uVar2);
              if (param_1 == 0x44) {
                uVar12 = 0x24;
              }
              else {
                uVar12 = 0x25;
              }
              terminal_request_display(uVar12,uVar11);
            }
          }
          else if (param_1 == 8) {
            iVar9 = FUN_0043d0ce();
            if (iVar9 << 0x1e < 0) {
              FUN_0043d574(3,PTR_s_terminal_ui_005e7e1c,
                           PTR_s_D__01_workspace_s200_ap510b_iar__005e7e18,
                           PTR_s_terminal_input_event_handler_005e7e14,0x7ee,
                           PTR_s_input__agent_processing_long_pre_005e7e34);
            }
            iVar9 = FUN_0043d0ce();
            if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
              compress_log_output(0xc000000,PTR_s__terminal_ui_input__agent_proces_005e7e38,
                                  PTR_s__terminal_ui_input__agent_proces_005e7e38);
            }
            terminal_request_display(0x1a,0);
          }
          else if (param_1 == 0x48) {
            uVar11 = FUN_005ecafa();
            terminal_request_display(0x1b,uVar11);
          }
        }
        else if (bVar3 == 10) {
          if (param_1 == 10) {
            terminal_request_display(0x17,0);
          }
          else if (param_1 == 0x48) {
            terminal_request_display(0x18,0);
          }
        }
        else if (bVar3 < 10) {
          if ((param_1 == 0x44) || (param_1 == 0x45)) {
            bVar1 = false;
            cVar16 = '\0';
            cVar13 = '\0';
            iVar8 = 0;
            uVar11 = 0;
            iVar6 = td_session_struct_ptr();
            if ((*(int *)(iVar9 + 0x214) != 0) && (iVar7 != 0)) {
              uVar17 = CONCAT31((int3)((uint)uVar11 >> 8),*(undefined1 *)(iVar9 + 0x27c));
              cVar15 = *(char *)(iVar9 + 0x279);
              iVar10 = FUN_0044e498(*(undefined4 *)(iVar9 + 0x214));
              if (iVar6 != 0) {
                uVar17 = (uint)CONCAT11((char)*(undefined2 *)(iVar6 + 0x406),(char)uVar17);
              }
              if ((((param_1 == 0x44) && (*(char *)(iVar9 + 0x27c) == '\0')) &&
                  (*(char *)(iVar9 + 0x279) == '\0')) && (0 < iVar10)) {
                bVar1 = true;
              }
              if ((*(char *)(iVar9 + 0x27c) != '\0') ||
                 (((param_1 == 0x44 && (*(char *)(iVar9 + 0x27c) == '\0')) &&
                  ((*(char *)(iVar9 + 0x279) == '\0' && (0 < iVar10)))))) {
                cVar16 = '\x01';
              }
              if ((*(char *)(iVar9 + 0x27c) == '\0') && (!bVar1)) {
                iVar6 = osKernelGetTickCount();
                if ((uint)(iVar6 - *(int *)(iVar9 + 0x290)) < 300) {
                  return;
                }
                *(int *)(iVar9 + 0x290) = iVar6;
              }
              if (cVar16 == '\0') {
                iVar6 = 0;
              }
              else {
                iVar6 = FUN_005e4c56(iVar9,param_1,iVar7);
              }
              if (((*(char *)(iVar9 + 0x27c) != '\0') && (param_1 == 0x45)) &&
                 (iVar8 = FUN_005eb4f6(), iVar8 < iVar6)) {
                iVar6 = iVar8;
              }
              bVar3 = FUN_005e4d10(iVar9,param_1,cVar16,iVar6);
              cVar4 = FUN_005e4d7c(iVar9,param_1,iVar6,iVar8);
              cVar14 = cVar13;
              if (param_1 == 0x44) {
                cVar14 = cVar16;
                if (*(char *)(iVar9 + 0x27c) == '\0') {
                  if (*(char *)(iVar9 + 0x279) == '\0') {
                    cVar14 = cVar13;
                    if (((0 < iVar10) && (cVar16 != '\0')) && (iVar6 < iVar10)) {
                      uVar17 = (uint)bVar3;
                      cVar14 = '\x01';
                    }
                  }
                  else {
                    cVar15 = *(char *)(iVar9 + 0x279) + -1;
                    cVar14 = cVar13;
                  }
                }
              }
              else if (*(char *)(iVar9 + 0x27c) == '\0') {
                bVar3 = (byte)(uVar17 >> 8);
                if ((bVar3 != 0) && ((uint)*(byte *)(iVar9 + 0x279) < bVar3 - 1)) {
                  cVar15 = *(char *)(iVar9 + 0x279) + '\x01';
                  iVar6 = FUN_005eb646(*(char *)(iVar9 + 0x279) + '\x01',1);
                  cVar14 = '\x01';
                }
              }
              else {
                cVar14 = '\x01';
                if (cVar4 != '\0') {
                  uVar17 = 0;
                  cVar15 = '\0';
                  iVar6 = FUN_005eb646(0,1);
                }
              }
              if (cVar14 == '\0') {
                iVar6 = iVar10;
              }
              if ((((uVar17 & 0xff) != (uint)*(byte *)(iVar9 + 0x27c)) ||
                  (cVar15 != *(char *)(iVar9 + 0x279))) || (iVar6 != iVar10)) {
                uVar11 = FUN_005e4cb6(iVar6,cVar14,uVar17 & 0xff,cVar15);
                if (param_1 == 0x44) {
                  uVar12 = 0x24;
                }
                else {
                  uVar12 = 0x25;
                }
                terminal_request_display(uVar12,uVar11);
              }
            }
          }
          else if ((param_1 == 10) && (*(char *)(iVar9 + 0x27c) == '\0')) {
            uVar11 = FUN_005e4cec(*(undefined1 *)(iVar9 + 0x279),*_DAT_005e7e58,*_DAT_005e7e54);
            terminal_request_display(0x19,uVar11);
          }
        }
        else if (bVar3 == 0xc) {
          if (param_1 == 8) {
            cVar13 = *(char *)(iVar6 + 0xa1d8);
            iVar9 = UX_GetSystemBLEStatus();
            if ((iVar9 != 0) && (cVar13 == '\x02')) {
              terminal_request_display(8,0);
            }
          }
          else if (param_1 == 0x48) {
            uVar11 = FUN_005ecafa();
            terminal_request_display(0x1b,uVar11);
          }
        }
        else if (((bVar3 < 0xc) && (*(char *)(iVar9 + 0x27d) == '\0')) &&
                (iVar6 = FUN_005897e0(), iVar6 == 0)) {
          if ((param_1 == 0x44) || (param_1 == 0x45)) {
            sVar5 = func_0x005ed0b8((int)*(short *)(iVar9 + 0x27a),param_1);
            if (sVar5 != *(short *)(iVar9 + 0x27a)) {
              if (param_1 == 0x44) {
                uVar11 = 0x24;
              }
              else {
                uVar11 = 0x25;
              }
              terminal_request_display(uVar11,sVar5);
            }
          }
          else if (param_1 == 10) {
            sVar5 = *(short *)(iVar9 + 0x27a);
            uVar2 = func_0x005ed152((int)sVar5);
            uVar11 = func_0x005eca32(uVar2,(int)sVar5);
            terminal_request_display(0x1d,uVar11);
          }
          else if (param_1 == 0x48) {
            terminal_request_display(0x1e,0);
          }
        }
      }
    }
    else {
      iVar6 = FUN_0043d0ce();
      if (iVar6 << 0x1e < 0) {
        FUN_0043d574(2,PTR_s_terminal_ui_005e7e1c,PTR_s_D__01_workspace_s200_ap510b_iar__005e7e18,
                     PTR_s_terminal_input_event_handler_005e7e14,0x78d,
                     PTR_s_ignore_input_during_session_swit_005e7e10,param_1,
                     *(undefined1 *)(iVar9 + 0x275),param_4);
      }
      iVar6 = FUN_0043d0ce();
      if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
        compress_log_output(0x8800000,PTR_s__terminal_ui_ignore_input_during_005e7e20,
                            PTR_s__terminal_ui_ignore_input_during_005e7e20,param_1,
                            *(undefined1 *)(iVar9 + 0x275));
      }
    }
  }
  return;
}

