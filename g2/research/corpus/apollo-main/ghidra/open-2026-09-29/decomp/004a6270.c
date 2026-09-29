
undefined8
DRV_IMUStopRawDataCollection
          (undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 *puVar1;
  int iVar2;
  
  if (*DAT_004a65b8 == '\0') {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_1 = 0x66d;
      param_2 = DAT_004a65dc;
      FUN_0043d574(2,DAT_004a65e8,DAT_004a65e4,DAT_004a65e0,0x66d,DAT_004a65dc,param_3,param_4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_004a65ec,DAT_004a65ec);
    }
  }
  else {
    *DAT_004a65b8 = '\0';
    puVar1 = DAT_004a658c;
    iVar2 = file_close(*DAT_004a658c);
    if (iVar2 == 0) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        param_1 = 0x676;
        param_2 = DAT_004a65f8;
        FUN_0043d574(3,DAT_004a65e8,DAT_004a65e4,DAT_004a65e0,0x676,DAT_004a65f8,*DAT_004a65b4);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0xc400000,PTR_s__sensor_imu__IMU__Stopped_raw_da_004a65fc,
                            PTR_s__sensor_imu__IMU__Stopped_raw_da_004a65fc,*DAT_004a65b4);
      }
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        param_1 = 0x674;
        param_2 = DAT_004a65f0;
        FUN_0043d574(1,DAT_004a65e8,DAT_004a65e4,DAT_004a65e0);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_004a65f4);
      }
    }
    *puVar1 = 0;
    *DAT_004a65d0 = 0;
    *DAT_004a65b4 = 0;
  }
  return CONCAT44(param_2,param_1);
}

