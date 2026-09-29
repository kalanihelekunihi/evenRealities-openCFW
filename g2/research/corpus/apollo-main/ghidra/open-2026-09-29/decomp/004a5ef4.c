
undefined4
DRV_IMUWriteCSVDataLine
          (undefined4 param_1,float *param_2,float *param_3,float *param_4,float *param_5,
          char param_6,char param_7,char param_8)

{
  float fVar1;
  float fVar2;
  float fVar3;
  float fVar4;
  float fVar5;
  float fVar6;
  int iVar7;
  undefined4 uVar8;
  int iVar9;
  float fVar10;
  float fVar11;
  float fVar12;
  undefined1 auStack_110 [256];
  float *pfStack_10;
  
  fVar11 = fRam004a60d4;
  fVar1 = fRam004a60d4;
  fVar2 = fRam004a60d4;
  if (param_8 != '\0') {
    fVar11 = *param_4;
    fVar1 = param_4[1];
    fVar2 = param_4[2];
  }
  fVar12 = fRam004a60d4;
  fVar3 = fRam004a60d4;
  fVar4 = fRam004a60d4;
  if (param_7 != '\0') {
    fVar12 = *param_3;
    fVar3 = param_3[1];
    fVar4 = param_3[2];
  }
  fVar10 = fRam004a60d4;
  fVar5 = fRam004a60d4;
  fVar6 = fRam004a60d4;
  if (param_6 != '\0') {
    fVar10 = *param_2;
    fVar5 = param_2[1];
    fVar6 = param_2[2];
  }
  pfStack_10 = param_4;
  iVar7 = FUN_0044b728(auStack_110,0x100,PTR_s__lu___6f___6f___6f___6f___6f___6_004a659c,param_1,
                       (double)fVar10,(double)fVar5,(double)fVar6,(double)fVar12,(double)fVar3,
                       (double)fVar4,(double)fVar11,(double)fVar1,(double)fVar2,(double)*param_5,
                       (double)param_5[1],(double)param_5[2]);
  if (iVar7 < 0x100) {
    iVar9 = file_write(auStack_110,1,iVar7,*DAT_004a658c);
    if (iVar9 == iVar7) {
      *DAT_004a65b4 = *DAT_004a65b4 + 1;
      uVar8 = 0;
    }
    else {
      iVar7 = FUN_0043d0ce();
      if (iVar7 << 0x1e < 0) {
        FUN_0043d574(1,DAT_004a6268,DAT_004a6264,PTR_s_DRV_IMUWriteCSVDataLine_004a65a4,0x63c,
                     PTR_s__IMU__Failed_to_write_CSV_data_l_004a65ac);
      }
      iVar7 = FUN_0043d0ce();
      if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
        compress_log_output(0x4000000,PTR_s__sensor_imu__IMU__Failed_to_writ_004a65b0,
                            PTR_s__sensor_imu__IMU__Failed_to_writ_004a65b0);
      }
      uVar8 = 0xffffffff;
    }
  }
  else {
    iVar7 = FUN_0043d0ce();
    if (iVar7 << 0x1e < 0) {
      FUN_0043d574(1,DAT_004a6268,DAT_004a6264,PTR_s_DRV_IMUWriteCSVDataLine_004a65a4,0x635,
                   PTR_s__IMU__CSV_line_buffer_overflow_004a65a0);
    }
    iVar7 = FUN_0043d0ce();
    if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__sensor_imu__IMU__CSV_line_buffe_004a65a8,
                          PTR_s__sensor_imu__IMU__CSV_line_buffe_004a65a8);
    }
    uVar8 = 0xffffffff;
  }
  return uVar8;
}

