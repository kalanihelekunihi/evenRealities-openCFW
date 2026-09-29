
undefined8 FUN_00511294(undefined4 param_1,undefined4 param_2,undefined *param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  undefined *puVar3;
  
  puVar3 = param_3;
  if ((int)param_3 << 0x1f < 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      param_2 = 0x189;
      puVar3 = PTR_s_VBUS_detected__connected__00511be0;
      FUN_0043d574(4,DAT_00511958,DAT_00511954,PTR_s_vbusin_voltage_callback_00511be4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10000000,PTR_s__npmx_driver_VBUS_detected__conn_00511be8,
                          PTR_s__npmx_driver_VBUS_detected__conn_00511be8);
    }
    uVar2 = FUN_0055ee8c(param_1,0);
    FUN_0055ef02(uVar2,0);
    FUN_004ac130();
  }
  if (-1 < (int)param_3 << 0x1e) goto LAB_00511340;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    param_2 = 400;
    puVar3 = PTR_s_VBUS_removed__disconnected__00511bec;
    FUN_0043d574(4,DAT_00511958,DAT_00511954,PTR_s_vbusin_voltage_callback_00511be4,400,
                 PTR_s_VBUS_removed__disconnected__00511bec,param_4);
  }
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1f < 0) {
LAB_0051132e:
    compress_log_output(0x10000000,PTR_s__npmx_driver_VBUS_removed__disco_00511bf0,
                        PTR_s__npmx_driver_VBUS_removed__disco_00511bf0);
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1d < 0) goto LAB_0051132e;
  }
  FUN_004ac154();
LAB_00511340:
  return CONCAT44(puVar3,param_2);
}

