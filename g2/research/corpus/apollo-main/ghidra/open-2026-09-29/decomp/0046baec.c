
undefined8
SVC_Settings_UpdateLeftVersion
          (char *param_1,undefined *param_2,undefined4 param_3,undefined4 param_4)

{
  char cVar1;
  int iVar2;
  int iVar3;
  
  iVar2 = DAT_0046bee8;
  if ((param_1 != (char *)0x0) && (*param_1 != '\0')) {
    cVar1 = *(char *)(DAT_0046bee8 + 0x44);
    iVar3 = DAT_0046bee8 + 0x44;
    FUN_0044b5a0(iVar3,param_1,9);
    *(undefined1 *)(iVar2 + 0x4d) = 0;
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_1 = &DAT_00000103;
      param_2 = PTR_s_recv_left_version___s_0046c51c;
      FUN_0043d574(4,DAT_0046bb74,DAT_0046bb70,PTR_s_SVC_Settings_UpdateLeftVersion_0046c520,0x103,
                   PTR_s_recv_left_version___s_0046c51c,iVar3,param_4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10400000,PTR_s__service_settings_recv_left_vers_0046c654,
                          PTR_s__service_settings_recv_left_vers_0046c654,iVar3);
    }
    if (cVar1 == '\0') {
      setting_notify_device_status_to_app();
    }
  }
  return CONCAT44(param_2,param_1);
}

