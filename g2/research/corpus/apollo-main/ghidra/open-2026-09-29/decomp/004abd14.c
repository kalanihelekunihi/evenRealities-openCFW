
undefined8 CB_BLE_STATUS_UnregisterCallback(int param_1)

{
  undefined *puVar1;
  int iVar2;
  undefined4 unaff_r5;
  undefined *unaff_r6;
  
  if (param_1 == 0) {
    iVar2 = FUN_0043d0ce();
    puVar1 = PTR_s_Invalid_callback_function_004abd78;
    if (iVar2 << 0x1e < 0) {
      unaff_r5 = 0x34;
      FUN_0043d574(1,PTR_s_cb_ble_status_004abd84,PTR_s_D__01_workspace_s200_ap510b_iar__004abd80,
                   PTR_s_CB_BLE_STATUS_UnregisterCallback_004abd8c);
      unaff_r6 = puVar1;
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__cb_ble_status_Invalid_callback_f_004abd88,
                          PTR_s__cb_ble_status_Invalid_callback_f_004abd88);
    }
  }
  else {
    CALLBACK_MGR_Unregister(DAT_004abd74,param_1);
  }
  return CONCAT44(unaff_r6,unaff_r5);
}

