
undefined8 CB_BLE_STATUS_RegisterCallback(int param_1)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 unaff_r5;
  
  if (param_1 == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      unaff_r5 = 0x29;
      FUN_0043d574(1,PTR_s_cb_ble_status_004abd84,PTR_s_D__01_workspace_s200_ap510b_iar__004abd80,
                   PTR_s_CB_BLE_STATUS_RegisterCallback_004abd7c,0x29,
                   PTR_s_Invalid_callback_function_004abd78);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__cb_ble_status_Invalid_callback_f_004abd88,
                          PTR_s__cb_ble_status_Invalid_callback_f_004abd88);
    }
    uVar2 = 0;
  }
  else {
    uVar2 = CALLBACK_MGR_Register(DAT_004abd74,param_1);
  }
  return CONCAT44(unaff_r5,uVar2);
}

