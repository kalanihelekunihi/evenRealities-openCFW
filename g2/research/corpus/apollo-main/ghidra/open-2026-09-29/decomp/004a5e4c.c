
undefined8
DRV_IMUWriteCSVHeader(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  undefined4 uVar4;
  
  uVar4 = DAT_004a6588;
  uVar1 = FUN_0044a43c(DAT_004a6588);
  iVar2 = file_write(uVar4,1,uVar1,*DAT_004a658c,param_2,param_3,param_4);
  iVar3 = FUN_0044a43c(uVar4);
  if (iVar2 == iVar3) {
    uVar4 = 0;
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_2 = 0x60f;
      FUN_0043d574(1,DAT_004a6268,DAT_004a6264,DAT_004a6594,0x60f,DAT_004a6590);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__sensor_imu__IMU__Failed_to_writ_004a6598,
                          PTR_s__sensor_imu__IMU__Failed_to_writ_004a6598);
    }
    uVar4 = 0xffffffff;
  }
  return CONCAT44(param_2,uVar4);
}

