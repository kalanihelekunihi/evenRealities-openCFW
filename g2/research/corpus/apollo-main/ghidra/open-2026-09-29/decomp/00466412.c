
undefined8 FUN_00466412(char *param_1,undefined4 param_2,undefined4 param_3,undefined *param_4)

{
  int iVar1;
  int iVar2;
  undefined4 uStack_18;
  undefined *puStack_14;
  
  uStack_18 = param_3;
  puStack_14 = param_4;
  if ((*param_1 == '\0') && (iVar1 = FUN_0045a568(), iVar2 = DAT_004667ec, iVar1 == 2)) {
    FUN_00439be4(DAT_004667ec,param_1 + 2,0x14);
    FUN_00439be4(iVar2 + 0x14,param_1 + 0x18,0xc);
    FUN_00439be4(iVar2 + 0x20,param_1 + 0x24,0xc);
  }
  else if ((*param_1 == '\x01') && (iVar2 = FUN_0045a568(), iVar2 == 1)) {
    iVar2 = FUN_0046636c(param_1);
    if (iVar2 == 0) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        puStack_14 = PTR_s_Recv_slave_universal_setting_syn_00466840;
        uStack_18 = 0xf2;
        FUN_0043d574(3,DAT_00466800,DAT_004667fc,PTR_s_svc_universal_setting_sync_handl_00466838);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0xc000000,PTR_s__srv_universal_setting_Recv_slav_00466844,
                            PTR_s__srv_universal_setting_Recv_slav_00466844);
      }
      FUN_004661a6();
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        puStack_14 = PTR_s_universal_setting_all_values_mat_00466834;
        uStack_18 = 0xef;
        FUN_0043d574(3,DAT_00466800,DAT_004667fc,PTR_s_svc_universal_setting_sync_handl_00466838);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0xc000000,PTR_s__srv_universal_setting_universal_0046683c,
                            PTR_s__srv_universal_setting_universal_0046683c);
      }
    }
  }
  return CONCAT44(puStack_14,uStack_18);
}

