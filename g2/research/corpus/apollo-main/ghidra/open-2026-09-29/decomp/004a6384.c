
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void DRV_IMUSaveRawDataToCSV(void)

{
  int iVar1;
  undefined4 in_r3;
  uint uVar2;
  
  if (*DAT_004a65b8 == '\0') {
    return;
  }
  iVar1 = osKernelGetTickCount();
  if (*(uint *)PTR_DAT_004a6600 <= (uint)(iVar1 - *DAT_004a65d0)) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(3,DAT_004a65e8,DAT_004a65e4,PTR_s_DRV_IMUSaveRawDataToCSV_004a6608,0x68d,
                   PTR_s__IMU__Data_collection_time_limit_004a6604);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0xc000000,PTR_s__sensor_imu__IMU__Data_collectio_004a660c,
                          PTR_s__sensor_imu__IMU__Data_collectio_004a660c);
    }
    DRV_IMUStopRawDataCollection();
    return;
  }
  for (uVar2 = 0; uVar2 < *(uint *)(_DAT_004a6610 + 8); uVar2 = uVar2 + 1) {
    DRV_IMUWriteCSVDataLine
              (*(undefined4 *)(_DAT_004a6610 + uVar2 * 0x70 + 0xc),
               uVar2 * 0x70 + _DAT_004a6610 + 0x34,uVar2 * 0x70 + _DAT_004a6610 + 0x40,
               uVar2 * 0x70 + _DAT_004a6610 + 0x4c,uVar2 * 0x70 + _DAT_004a6610 + 0x68,
               *(byte *)(uVar2 * 0x70 + _DAT_004a6610 + 0x10) & 1,
               (*(byte *)(uVar2 * 0x70 + _DAT_004a6610 + 0x10) & 3) >> 1,
               (*(byte *)(uVar2 * 0x70 + _DAT_004a6610 + 0x10) & 0xf) >> 3,in_r3);
  }
  return;
}

