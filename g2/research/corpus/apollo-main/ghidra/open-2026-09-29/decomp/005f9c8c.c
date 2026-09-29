
longlong FUN_005f9c8c(undefined4 param_1,uint param_2,undefined *param_3,undefined4 param_4)

{
  int iVar1;
  uint uVar2;
  undefined *puVar3;
  
  uVar2 = param_2;
  puVar3 = param_3;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    param_4 = 0x80;
    uVar2 = 0x13;
    puVar3 = PTR_s_SID_UX_DEVICE_SETTINGS_APP_ID_____005f9ec8;
    FUN_0043d574(4,PTR_s_ux_setting_0078c8fb_1_005f9ed4,
                 PTR_s_D__01_workspace_s200_ap510b_iar__005f9ed0,
                 PTR_s_UX_SettingsCommonDataHandler_005f9ecc,0x13,
                 PTR_s_SID_UX_DEVICE_SETTINGS_APP_ID_____005f9ec8,0x80);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10400000,PTR_s__ux_setting_SID_UX_DEVICE_SETTIN_005f9ed8,
                        PTR_s__ux_setting_SID_UX_DEVICE_SETTIN_005f9ed8,0x80,uVar2,puVar3,param_4);
  }
  Thread_MsgRxFromBle(0x80,param_2,(uint)param_3 & 0xffff);
  return (ulonglong)uVar2 << 0x20;
}

