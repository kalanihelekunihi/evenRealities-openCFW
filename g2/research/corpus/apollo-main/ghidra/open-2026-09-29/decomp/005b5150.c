
undefined4 FUN_005b5150(undefined4 param_1,short *param_2,undefined4 param_3,undefined4 param_4)

{
  char cVar1;
  int iVar2;
  undefined4 uVar3;
  
  if (param_2 == (short *)0x0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,DAT_005b52d8,DAT_005b52d4,PTR_s_conversate_action_prep_note_list_005b56a8,300,
                   PTR_s_conversate_prep_note_list_data_i_005b56a4,param_3,param_4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__conversate_conversate_prep_note_005b56ac);
    }
    uVar3 = 0xffffffff;
  }
  else {
    if (*param_2 == 0) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(3,DAT_005b52d8,DAT_005b52d4,PTR_s_conversate_action_prep_note_list_005b56a8,
                     0x132,PTR_s_prep_note_list_data_received_cou_005b56b8);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0xc000000,PTR_s__conversate_prep_note_list_data_r_005b56bc,
                            PTR_s__conversate_prep_note_list_data_r_005b56bc);
      }
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(3,DAT_005b52d8,DAT_005b52d4,PTR_s_conversate_action_prep_note_list_005b56a8,
                     0x130,PTR_s_prep_note_list_data_received_cou_005b56b0,*param_2,param_2 + 5);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0xc800000,PTR_s__conversate_prep_note_list_data_r_005b56b4,
                            PTR_s__conversate_prep_note_list_data_r_005b56b4,*param_2,param_2 + 5);
      }
    }
    FUN_005b4378(param_2);
    cVar1 = FUN_005b16d0();
    if (cVar1 == '\0') {
      iVar2 = FUN_0045a568();
      if (iVar2 == 1) {
        FUN_0045a8ee(0xb,0,0,500);
      }
    }
    else if ((*param_2 == 0) && (cVar1 == '\x03')) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(3,DAT_005b52d8,DAT_005b52d4,PTR_s_conversate_action_prep_note_list_005b56a8,
                     0x13f,PTR_s_prep_note_list_empty__skip___sta_005b56c0);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0xc000000,PTR_s__conversate_prep_note_list_empty_005b56c4,
                            PTR_s__conversate_prep_note_list_empty_005b56c4);
      }
      conversate_ui_send_start_request();
      FUN_005b02e4(0xc,0);
    }
    else {
      FUN_005b02e4(2,0);
    }
    uVar3 = 0;
  }
  return uVar3;
}

