
void DRV_IMUStartRawDataCollection(void)

{
  int *piVar1;
  char *pcVar2;
  int iVar3;
  undefined4 uVar4;
  undefined1 auStack_2c [32];
  
  pcVar2 = DAT_004a65b8;
  if (*DAT_004a65b8 != '\0') {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(2,DAT_004a6268,DAT_004a6264,DAT_004a65c0,0x64a,DAT_004a65bc);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_004a65c4,DAT_004a65c4);
    }
    DRV_IMUStopRawDataCollection();
  }
  FUN_0043c0e4(auStack_2c,0x20,0);
  semantic_build_raw_csv_path(auStack_2c,0x20);
  piVar1 = DAT_004a658c;
  iVar3 = file_open(auStack_2c,&DAT_004a6364);
  *piVar1 = iVar3;
  if (*piVar1 == 0) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(1,DAT_004a6268,DAT_004a6264,DAT_004a65c0,0x655,DAT_004a65c8,auStack_2c);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_004a65cc,DAT_004a65cc,auStack_2c);
    }
  }
  else {
    iVar3 = DRV_IMUWriteCSVHeader();
    if (iVar3 == 0) {
      *pcVar2 = '\x01';
      *DAT_004a65b4 = 0;
      uVar4 = osKernelGetTickCount();
      *DAT_004a65d0 = uVar4;
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(3,DAT_004a6268,DAT_004a6264,DAT_004a65c0,0x664,DAT_004a65d4,auStack_2c);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0xc400000,DAT_004a65d8,DAT_004a65d8,auStack_2c);
      }
    }
    else {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(1,DAT_004a6268,DAT_004a6264,DAT_004a65c0,0x65b,DAT_004a6590);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x4000000,PTR_s__sensor_imu__IMU__Failed_to_writ_004a6598,
                            PTR_s__sensor_imu__IMU__Failed_to_writ_004a6598);
      }
      file_close(*piVar1);
    }
  }
  return;
}

