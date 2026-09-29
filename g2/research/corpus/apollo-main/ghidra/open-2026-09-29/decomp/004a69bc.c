
undefined8
HUB_IMUCollectionHandler(int param_1,undefined4 param_2,undefined4 param_3,undefined *param_4)

{
  int iVar1;
  undefined4 uStack_10;
  undefined4 uStack_c;
  
  iVar1 = FUN_0043d0ce();
  uStack_10 = param_3;
  uStack_c = param_4;
  if (iVar1 << 0x1e < 0) {
    uStack_c = PTR_s_IMU_sensor_collection_004a7364;
    uStack_10 = 0xe1;
    FUN_0043d574(4,DAT_004a6ee0,DAT_004a6edc,PTR_s_HUB_IMUCollectionHandler_004a7368);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10000000,PTR_s__sensor_hub_IMU_sensor_collectio_004a736c,
                        PTR_s__sensor_hub_IMU_sensor_collectio_004a736c);
  }
  if (*(int *)(param_1 + 4) == 1) {
    DRV_IMUStartRawDataCollection();
  }
  else if (*(int *)(param_1 + 4) == 0) {
    DRV_IMUStopRawDataCollection();
  }
  return CONCAT44(uStack_c,uStack_10);
}

