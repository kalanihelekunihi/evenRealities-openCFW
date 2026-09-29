
undefined4
FUN_005b52e0(undefined4 param_1,undefined4 *param_2,undefined4 param_3,undefined4 param_4)

{
  char cVar1;
  int iVar2;
  undefined4 uVar3;
  
  if (param_2 == (undefined4 *)0x0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,PTR_s_conversate_005b56d4,PTR_s_D__01_workspace_s200_ap510b_iar__005b56d0,
                   PTR_s_conversate_action_prep_note_pack_005b56cc,0x153,
                   PTR_s_conversate_prep_note_packet_data_005b56c8,param_3,param_4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__conversate_conversate_prep_note_005b56d8);
    }
    uVar3 = 0xffffffff;
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(3,PTR_s_conversate_005b56d4,PTR_s_D__01_workspace_s200_ap510b_iar__005b56d0,
                   PTR_s_conversate_action_prep_note_pack_005b56cc,0x159,
                   PTR_s_prep_note_packet_data_received_i_005b56dc,*param_2,
                   *(undefined2 *)(param_2 + 1));
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0xc800000,PTR_s__conversate_prep_note_packet_dat_005b56e0,
                          PTR_s__conversate_prep_note_packet_dat_005b56e0,*param_2,
                          *(undefined2 *)(param_2 + 1));
    }
    iVar2 = FUN_005b44d8(param_2);
    if (iVar2 == 0) {
      cVar1 = FUN_005b16d0();
      if ((cVar1 == '\x05') && (iVar2 = FUN_005b476a(), iVar2 != 0)) {
        FUN_005b02e4(7,0);
      }
      uVar3 = 0;
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(1,PTR_s_conversate_005b56d4,PTR_s_D__01_workspace_s200_ap510b_iar__005b56d0,
                     PTR_s_conversate_action_prep_note_pack_005b56cc,0x15d,
                     PTR_s_prep_note_packet_update_failed__i_005b56e4,*param_2);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4400000,PTR_s__conversate_prep_note_packet_upd_005b56e8,
                            PTR_s__conversate_prep_note_packet_upd_005b56e8,*param_2);
      }
      uVar3 = 0xffffffff;
    }
  }
  return uVar3;
}

