
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int FUN_004fec98(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined1 uVar2;
  uint uStack_118;
  undefined1 auStack_114 [256];
  undefined4 uStack_14;
  
  uStack_118 = 0x100;
  uStack_14 = param_4;
  if (*_DAT_004feef4 == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(2,PTR_s_dashboard_data_process_004feee8,
                   PTR_s_D__01_workspace_s200_ap510b_iar__004feee4,
                   PTR_s_dashboard_respond_to_app_seriali_004ff20c,0x367,
                   PTR_s_dashboard_respond_to_app_seriali_004ff208);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8000000,PTR_s__dashboard_data_process_dashboar_004ff210,
                          PTR_s__dashboard_data_process_dashboar_004ff210);
    }
    iVar1 = 1;
  }
  else {
    FUN_0043c0e4(auStack_114,0x100,0);
    uVar2 = param_1 != 0;
    if (param_1 == 2) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(3,PTR_s_dashboard_data_process_004feee8,
                     PTR_s_D__01_workspace_s200_ap510b_iar__004feee4,
                     PTR_s_dashboard_respond_to_app_seriali_004ff20c,0x373,_DAT_004ff278);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0xc000000,_DAT_004ff27c,_DAT_004ff27c);
      }
      uVar2 = 2;
    }
    iVar1 = FUN_004fec14(uVar2,auStack_114,&uStack_118);
    if (iVar1 == 0) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(1,PTR_s_dashboard_data_process_004feee8,
                     PTR_s_D__01_workspace_s200_ap510b_iar__004feee4,
                     PTR_s_dashboard_respond_to_app_seriali_004ff20c,0x37c,_DAT_004ff2b4);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x4000000,PTR_s__dashboard_data_process_dashboar_004ff310,
                            PTR_s__dashboard_data_process_dashboar_004ff310);
      }
      iVar1 = 2;
    }
    else {
      iVar1 = Thread_MsgPbTxByBle(1,1,auStack_114,uStack_118 & 0xffff);
      if (iVar1 == 0) {
        FUN_0043c0e4(auStack_114,0x100,0);
        iVar1 = 0;
      }
    }
  }
  return iVar1;
}

