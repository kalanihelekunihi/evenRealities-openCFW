
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int FUN_004fedcc(int param_1)

{
  undefined1 *puVar1;
  int iVar2;
  undefined4 uStack_138;
  undefined *puStack_134;
  uint uStack_12c;
  undefined1 auStack_124 [20];
  undefined1 auStack_110 [256];
  
  if (*_DAT_004feef4 == 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      puStack_134 = PTR_s_dashboard_respond_to_app_seriali_004ff208;
      uStack_138 = 0x398;
      FUN_0043d574(2,PTR_s_dashboard_data_process_004feee8,
                   PTR_s_D__01_workspace_s200_ap510b_iar__004feee4,
                   PTR_s_dashboard_respond_NewsInfo_to_ap_004ff314);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x8000000,PTR_s__dashboard_data_process_dashboar_004ff210,
                          PTR_s__dashboard_data_process_dashboar_004ff210);
    }
    iVar2 = 1;
  }
  else {
    FUN_0043c0e4(auStack_110,0x100,0);
    puVar1 = DAT_004ff318;
    FUN_004fdd6e(DAT_004ff318);
    *puVar1 = 6;
    *(undefined4 *)(puVar1 + 4) = *_DAT_004feef8;
    *(undefined2 *)(puVar1 + 8) = 8;
    if (param_1 == 2) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        puStack_134 = _DAT_004ff278;
        uStack_138 = 0x3a5;
        FUN_0043d574(3,PTR_s_dashboard_data_process_004feee8,
                     PTR_s_D__01_workspace_s200_ap510b_iar__004feee4,
                     PTR_s_dashboard_respond_NewsInfo_to_ap_004ff314);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0xc000000,_DAT_004ff27c,_DAT_004ff27c);
      }
    }
    *(undefined4 *)(puVar1 + 0x10) = 0x55aa;
    FUN_004905f4(auStack_124,auStack_110,0x100);
    FUN_00439c04(&uStack_138,auStack_124,0x14);
    iVar2 = FUN_00490c32(&uStack_138,DAT_004ff494,puVar1);
    if (iVar2 == 0) {
      iVar2 = 0;
    }
    else {
      iVar2 = Thread_MsgPbTxByBle(1,1,auStack_110,uStack_12c & 0xffff);
      if (iVar2 == 0) {
        FUN_0043c0e4(auStack_110,0x100,0);
        iVar2 = 0;
      }
    }
  }
  return iVar2;
}

