
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 FUN_004668ae(int param_1,int param_2,int param_3)

{
  char cVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  
  iVar4 = param_3;
  if (((param_1 == 0) && (param_2 != 0)) && (param_3 != 0)) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      iVar4 = 99;
      FUN_0043d574(4,PTR_s_setting_004672f0,PTR_s_D__01_workspace_s200_ap510b_iar__004672ec,
                   PTR_s_Setting_common_data_handler_004672e8,99,
                   PTR_s_BLE_data_parsing_started_004672e4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10000000,PTR_s__setting_BLE_data_parsing_starte_004672f4,
                          PTR_s__setting_BLE_data_parsing_starte_004672f4);
    }
    uVar3 = _DAT_004672f8;
    cVar1 = setting_parse_data_package(param_2,param_3,_DAT_004672f8);
    if (cVar1 == '\0') {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        iVar4 = 0x67;
        FUN_0043d574(2,PTR_s_setting_004672f0,PTR_s_D__01_workspace_s200_ap510b_iar__004672ec,
                     PTR_s_Setting_common_data_handler_004672e8,0x67,
                     PTR_s_setting_parse_data_package_faile_004672fc);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x8000000,PTR_s__setting_setting_parse_data_pack_004674a8,
                            PTR_s__setting_setting_parse_data_pack_004674a8);
      }
      uVar3 = 0xffffffff;
      goto LAB_00466974;
    }
    FUN_00466976(uVar3);
  }
  else if (param_1 == 5) {
    SVC_Settings_SyncHandler(param_2,param_3);
    iVar4 = param_3;
  }
  uVar3 = 0;
LAB_00466974:
  return CONCAT44(iVar4,uVar3);
}

