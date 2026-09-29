
undefined8 FUN_005e5580(char param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  undefined1 uVar1;
  char cVar2;
  int iVar3;
  undefined4 uVar4;
  int iVar5;
  int iVar6;
  
  iVar6 = param_2;
  uVar1 = UX_GetSystemBLEStatus();
  cVar2 = FUN_005e50ea(uVar1);
  if ((param_1 == '\x03') && (((cVar2 == '\x02' || (cVar2 == '\x03')) || (cVar2 == '\x04')))) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      iVar6 = 0x3ab;
      FUN_0043d574(3,PTR_s_terminal_ui_005e6004,PTR_s_D__01_workspace_s200_ap510b_iar__005e6000,
                   PTR_s_terminal_ui_action_session_id_ch_005e5ffc,0x3ab,
                   PTR_s_session_id_changed_while_blocked_005e5ff8,param_4);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0xc000000,PTR_s__terminal_ui_session_id_changed_w_005e6008);
    }
    uVar4 = 4;
  }
  else {
    FUN_005eceb2();
    FUN_005ec268();
    FUN_005ebbc6();
    FUN_005ec770();
    FUN_005ec9c0();
    FUN_005eae2c(4);
    iVar3 = DAT_005e5dd8;
    *(undefined1 *)(DAT_005e5dd8 + 0x27e) = 0;
    if (((param_1 == '\n') && (*(char *)(iVar3 + 0x27f) != '\0')) &&
       (*(int *)(iVar3 + 0x288) == param_2)) {
      FUN_005e583c(10,0);
      FUN_005e5484(4,param_2,0);
      FUN_005e65f8();
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        iVar6 = 0x3bb;
        FUN_0043d574(3,PTR_s_terminal_ui_005e6004,PTR_s_D__01_workspace_s200_ap510b_iar__005e6000,
                     PTR_s_terminal_ui_action_session_id_ch_005e5ffc,0x3bb,
                     PTR_s_session_id_changed_from_notifica_005e600c,param_2);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0xc400000,PTR_s__terminal_ui_session_id_changed_f_005e6010,
                            PTR_s__terminal_ui_session_id_changed_f_005e6010,param_2);
      }
      uVar4 = 8;
    }
    else {
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        iVar6 = 0x3bf;
        FUN_0043d574(3,PTR_s_terminal_ui_005e6004,PTR_s_D__01_workspace_s200_ap510b_iar__005e6000,
                     PTR_s_terminal_ui_action_session_id_ch_005e5ffc,0x3bf,
                     PTR_s_session_id_changed__visible_cont_005e6014,cVar2);
      }
      iVar5 = FUN_0043d0ce();
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        compress_log_output(0xc400000,PTR_s__terminal_ui_session_id_changed__005e6390,
                            PTR_s__terminal_ui_session_id_changed__005e6390,cVar2);
      }
      if (cVar2 == '\x02') {
        FUN_005e522e(param_1,0);
        uVar4 = 4;
      }
      else if (cVar2 == '\x03') {
        FUN_005e5290(param_1,0);
        uVar4 = 4;
      }
      else if (cVar2 == '\x04') {
        FUN_005e52c2(param_1,0);
        uVar4 = 4;
      }
      else if (cVar2 == '\x06') {
        FUN_005e583c(param_1,0);
        uVar4 = 8;
      }
      else if (cVar2 == '\a') {
        FUN_005e641c(param_1,1);
        uVar4 = 10;
      }
      else if (cVar2 == '\x16') {
        FUN_005e6548(param_1,*(undefined4 *)(iVar3 + 0x288));
        uVar4 = 0xb;
      }
      else {
        FUN_005e57c6(param_1,0);
        uVar4 = 3;
      }
    }
  }
  return CONCAT44(iVar6,uVar4);
}

