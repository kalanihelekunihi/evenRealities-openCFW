
void FUN_0049e486(uint param_1,byte *param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  int iVar2;
  undefined4 uStack_20;
  undefined *puStack_1c;
  uint uStack_18;
  undefined1 uStack_14;
  undefined1 uStack_13;
  undefined1 uStack_12;
  undefined4 uStack_10;
  
  uStack_10 = param_4;
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    puStack_1c = PTR_s_BleConnectStatusNotifyCallback_e_0049ea5c;
    uStack_20 = 0x422;
    uStack_18 = param_1;
    FUN_0043d574(3,PTR_s_dashboard_0049ea68,PTR_s_D__01_workspace_s200_ap510b_iar__0049ea64,
                 PTR_s_BleConnectStatusNotifyCallback_0049ea60);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0xc400000,PTR_s__dashboard_BleConnectStatusNotif_0049ea6c,
                        PTR_s__dashboard_BleConnectStatusNotif_0049ea6c,param_1);
  }
  if (param_1 == 0) {
    bVar1 = *param_2;
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      uStack_18 = (uint)bVar1;
      puStack_1c = PTR_s_BleConnectStatusNotifyCallback___0049ea70;
      uStack_20 = 0x425;
      FUN_0043d574(3,PTR_s_dashboard_0049ea68,PTR_s_D__01_workspace_s200_ap510b_iar__0049ea64,
                   PTR_s_BleConnectStatusNotifyCallback_0049ea60);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0xc400000,PTR_s__dashboard_BleConnectStatusNotif_0049ea74,
                          PTR_s__dashboard_BleConnectStatusNotif_0049ea74,bVar1);
    }
    FUN_0043c0e4(&uStack_20,2,0);
    FUN_0043c0e4(&uStack_20,2,0);
    uStack_20._0_2_ = CONCAT11(bVar1,9);
    FUN_00464bb2(1,&uStack_20,2,0);
  }
  else if (param_1 == 1) {
    bVar1 = *param_2;
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      uStack_18 = (uint)bVar1;
      puStack_1c = PTR_s_BleConnectStatusNotifyCallback___0049ea70;
      uStack_20 = 0x42d;
      FUN_0043d574(3,PTR_s_dashboard_0049ea68,PTR_s_D__01_workspace_s200_ap510b_iar__0049ea64,
                   PTR_s_BleConnectStatusNotifyCallback_0049ea60);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0xc400000,PTR_s__dashboard_BleConnectStatusNotif_0049ea74,
                          PTR_s__dashboard_BleConnectStatusNotif_0049ea74,bVar1);
    }
    FUN_0043c0e4(&uStack_14,3,0);
    FUN_0043c0e4(&uStack_14,3,0);
    uStack_14 = 0x13;
    if (bVar1 == 0) {
      uStack_13 = 0;
    }
    else {
      if (bVar1 != 1) {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          uStack_18 = (uint)bVar1;
          puStack_1c = PTR_s_BleConnectStatusNotifyCallback___0049ea78;
          uStack_20 = 0x436;
          FUN_0043d574(2,PTR_s_dashboard_0049ea68,PTR_s_D__01_workspace_s200_ap510b_iar__0049ea64,
                       PTR_s_BleConnectStatusNotifyCallback_0049ea60);
        }
        iVar2 = FUN_0043d0ce();
        if ((-1 < iVar2 << 0x1f) && (iVar2 = FUN_0043d0ce(), -1 < iVar2 << 0x1d)) {
          return;
        }
        compress_log_output(0x8400000,PTR_s__dashboard_BleConnectStatusNotif_0049ea7c,
                            PTR_s__dashboard_BleConnectStatusNotif_0049ea7c,bVar1);
        return;
      }
      uStack_13 = 1;
    }
    uStack_12 = 0;
    FUN_00464bb2(1,&uStack_14,3,0);
  }
  return;
}

