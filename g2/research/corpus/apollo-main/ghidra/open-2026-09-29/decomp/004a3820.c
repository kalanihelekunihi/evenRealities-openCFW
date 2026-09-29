
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

uint DRV_IMUSetSensorParameters(void)

{
  undefined8 uVar1;
  char *pcVar2;
  undefined4 uVar3;
  char *pcVar4;
  char *pcVar5;
  char *pcVar6;
  char *pcVar7;
  undefined1 *puVar8;
  int *piVar9;
  uint uVar10;
  uint uVar11;
  uint uVar12;
  uint uVar13;
  uint uVar14;
  int iVar15;
  uint uVar16;
  undefined4 in_r3;
  char cVar17;
  uint in_fpscr;
  char acStack_140 [4];
  undefined2 uStack_13c;
  undefined2 uStack_13a;
  undefined1 uStack_138;
  undefined1 uStack_136;
  undefined1 uStack_132;
  undefined1 uStack_130;
  undefined1 uStack_12f;
  undefined1 uStack_12e;
  undefined2 uStack_12c;
  undefined1 uStack_12a;
  undefined1 uStack_129;
  undefined1 uStack_128;
  undefined1 uStack_127;
  undefined1 uStack_126;
  undefined1 uStack_125;
  undefined1 uStack_124;
  undefined1 uStack_123;
  undefined1 auStack_11c [4];
  undefined1 uStack_118;
  undefined1 uStack_117;
  undefined1 uStack_115;
  undefined1 uStack_113;
  undefined1 uStack_110;
  undefined1 uStack_10f;
  uint uStack_10c;
  undefined2 uStack_108;
  undefined1 auStack_104 [4];
  undefined1 uStack_100;
  undefined1 auStack_fc [4];
  undefined1 uStack_f8;
  undefined1 uStack_f7;
  undefined1 uStack_f6;
  undefined1 uStack_ea;
  undefined4 uStack_e8;
  undefined4 uStack_e4;
  undefined1 uStack_e0;
  undefined1 uStack_df;
  undefined4 uStack_dc;
  undefined4 uStack_d8;
  undefined1 uStack_d4;
  undefined1 uStack_d3;
  undefined1 uStack_d0;
  undefined1 auStack_cf [3];
  undefined4 uStack_cc;
  undefined4 uStack_c8;
  undefined4 uStack_28;
  
  uStack_28 = in_r3;
  FUN_0043c0e4(&uStack_10c,8,0);
  FUN_0043c0e4(auStack_11c,0xe,0);
  FUN_0043c0e4(&uStack_f8,0xf,0);
  FUN_0043c0e4(&uStack_13c,0xc,0);
  uVar3 = _DAT_004a457c;
  uVar10 = func_0x00507a9c(_DAT_004a457c);
  uVar11 = func_0x0050832e(uVar3);
  uVar12 = func_0x0050879a(uVar3);
  uVar13 = func_0x005079fe(uVar3);
  uVar14 = func_0x005078d2(uVar3);
  uVar14 = uVar10 | uVar11 | uVar12 | uVar13 | uVar14;
  if (uVar14 == 0) {
    uVar10 = FUN_00505fcc(uVar3,0);
    uVar11 = func_0x00506008(uVar3,0);
    uVar14 = FUN_005062c8(uVar3);
    uVar14 = uVar10 | uVar11 | uVar14;
    if (uVar14 == 0) {
      uVar14 = FUN_005065cc(uVar3,0,&uStack_f8);
      uVar10 = func_0x00507b00(uVar3,auStack_11c);
      uVar14 = uVar14 | uVar10;
      if (uVar14 == 0) {
        iVar15 = FUN_00508954(uVar3);
        if (iVar15 == 0) {
          cVar17 = '\x01';
        }
        else {
          iVar15 = FUN_0043d0ce();
          if (iVar15 << 0x1e < 0) {
            FUN_0043d574(2,PTR_s_sensor_imu_004a458c,PTR_s_D__01_workspace_s200_ap510b_iar__004a4588
                         ,PTR_s_DRV_IMUSetSensorParameters_004a4580,0x1e9,
                         PTR_s_invn_mag_init_error_004a4600);
          }
          iVar15 = FUN_0043d0ce();
          if ((iVar15 << 0x1f < 0) || (iVar15 = FUN_0043d0ce(), iVar15 << 0x1d < 0)) {
            compress_log_output(0x8000000,PTR_s__sensor_imu_invn_mag_init_error_004a4604,
                                PTR_s__sensor_imu_invn_mag_init_error_004a4604);
          }
          cVar17 = '\0';
        }
        uVar14 = func_0x00506794(uVar3,*_DAT_004a4608);
        if (uVar14 == 0) {
          uVar14 = func_0x00506044(uVar3,*_DAT_004a4278);
          pcVar2 = _DAT_004a4280;
          if (*_DAT_004a4280 != '\0') {
            uVar10 = func_0x00506078(uVar3,*_DAT_004a427c);
            uVar14 = uVar14 | uVar10;
          }
          if (uVar14 == 0) {
            if (*pcVar2 == '\0') {
              uVar14 = func_0x005066b6(uVar3,1);
            }
            else {
              uVar14 = func_0x005066b6(uVar3,0);
            }
            if (uVar14 == 0) {
              uVar14 = func_0x00506188(uVar3,0);
              uVar10 = func_0x005061c0(uVar3,0);
              uVar14 = uVar14 | uVar10;
              if (uVar14 == 0) {
                if (*pcVar2 != '\0') {
                  uVar14 = func_0x00506150(uVar3,0);
                  uVar10 = func_0x00506118(uVar3,0);
                  uVar14 = uVar14 | uVar10;
                  if (uVar14 != 0) {
                    iVar15 = FUN_0043d0ce();
                    if (iVar15 << 0x1e < 0) {
                      FUN_0043d574(1,PTR_s_sensor_imu_004a458c,
                                   PTR_s_D__01_workspace_s200_ap510b_iar__004a4588,
                                   PTR_s_DRV_IMUSetSensorParameters_004a4580,0x20b,
                                   PTR_s_IMU_Error__At__s__line__d__004a4584,
                                   PTR_s_DRV_IMUSetSensorParameters_004a4580,0x20b);
                    }
                    iVar15 = FUN_0043d0ce();
                    if ((-1 < iVar15 << 0x1f) && (iVar15 = FUN_0043d0ce(), -1 < iVar15 << 0x1d)) {
                      return uVar14;
                    }
                    compress_log_output(0x4800000,PTR_s__sensor_imu_IMU_Error__At__s__li_004a45fc,
                                        PTR_s__sensor_imu_IMU_Error__At__s__li_004a45fc,
                                        PTR_s_DRV_IMUSetSensorParameters_004a4580,0x20b);
                    return uVar14;
                  }
                }
                uVar14 = func_0x005060ac(uVar3,3);
                if (*pcVar2 != '\0') {
                  uVar10 = func_0x005060e0(uVar3,1);
                  uVar14 = uVar14 | uVar10;
                }
                if (uVar14 == 0) {
                  uVar14 = func_0x005067c8(uVar3);
                  pcVar4 = _DAT_004a496c;
                  if (uVar14 == 0) {
                    if (*_DAT_004a496c != '\0') {
                      uVar14 = func_0x0050839e(uVar3);
                      uVar10 = func_0x00508402(uVar3,&uStack_10c);
                      uVar1 = VectorUnsignedToFloat
                                        ((uint)*_DAT_004a4970,(byte)(in_fpscr >> 0x16) & 3);
                      uVar1 = func_0x00508e58((int)uVar1,(int)((ulonglong)uVar1 >> 0x20));
                      uVar1 = VectorFloatToSignedFixed(uVar1,0x20,0x1e);
                      uStack_10c = (uint)uVar1 & 0xffff;
                      uStack_108 = 2;
                      uVar11 = func_0x0050842e(uVar3,&uStack_10c,0x32);
                      uVar11 = uVar11 | uVar14 | uVar10;
                      if (uVar11 != 0) {
                        iVar15 = FUN_0043d0ce();
                        if (iVar15 << 0x1e < 0) {
                          FUN_0043d574(1,PTR_s_sensor_imu_004a458c,
                                       PTR_s_D__01_workspace_s200_ap510b_iar__004a4588,
                                       PTR_s_DRV_IMUSetSensorParameters_004a4580,0x222,
                                       PTR_s_IMU_Error__At__s__line__d__004a4584,
                                       PTR_s_DRV_IMUSetSensorParameters_004a4580,0x222);
                        }
                        iVar15 = FUN_0043d0ce();
                        if ((-1 < iVar15 << 0x1f) && (iVar15 = FUN_0043d0ce(), -1 < iVar15 << 0x1d))
                        {
                          return uVar11;
                        }
                        compress_log_output(0x4800000,
                                            PTR_s__sensor_imu_IMU_Error__At__s__li_004a45fc,
                                            PTR_s__sensor_imu_IMU_Error__At__s__li_004a45fc,
                                            PTR_s_DRV_IMUSetSensorParameters_004a4580,0x222);
                        return uVar11;
                      }
                    }
                    pcVar5 = _DAT_004a4974;
                    if (*_DAT_004a4974 != '\0') {
                      uVar14 = func_0x005084d8(uVar3,acStack_140);
                      if (acStack_140[0] != '\0') {
                        uVar14 = 0xffffffff;
                      }
                      uVar10 = func_0x00508548(uVar3,&uStack_e8,0);
                      uStack_dc = 0x32;
                      uStack_d8 = 600;
                      uStack_d4 = 7;
                      uStack_d3 = 1;
                      uStack_e8 = 0x15e;
                      uStack_e4 = 0xea6;
                      uStack_e0 = 7;
                      uStack_df = 1;
                      uVar11 = func_0x0050861a(uVar3,&uStack_e8,0);
                      uVar12 = func_0x0050481a(uVar3,3,3,3,0,0);
                      uVar13 = func_0x00504888(uVar3);
                      uVar13 = uVar13 | uVar14 | uVar10 | uVar11 | uVar12;
                      if (uVar13 != 0) {
                        iVar15 = FUN_0043d0ce();
                        if (iVar15 << 0x1e < 0) {
                          FUN_0043d574(1,PTR_s_sensor_imu_004a458c,
                                       PTR_s_D__01_workspace_s200_ap510b_iar__004a4588,
                                       PTR_s_DRV_IMUSetSensorParameters_004a4580,0x23d,
                                       PTR_s_IMU_Error__At__s__line__d__004a4584,
                                       PTR_s_DRV_IMUSetSensorParameters_004a4580,0x23d);
                        }
                        iVar15 = FUN_0043d0ce();
                        if ((-1 < iVar15 << 0x1f) && (iVar15 = FUN_0043d0ce(), -1 < iVar15 << 0x1d))
                        {
                          return uVar13;
                        }
                        compress_log_output(0x4800000,
                                            PTR_s__sensor_imu_IMU_Error__At__s__li_004a45fc,
                                            PTR_s__sensor_imu_IMU_Error__At__s__li_004a45fc,
                                            PTR_s_DRV_IMUSetSensorParameters_004a4580,0x23d);
                        return uVar13;
                      }
                    }
                    pcVar6 = _DAT_004a4978;
                    if (*_DAT_004a4978 != '\0') {
                      uVar14 = func_0x005069cc(uVar3,&uStack_13c);
                      uStack_138 = 0x37;
                      uStack_13a = 400;
                      uStack_13c = 0x578;
                      uStack_136 = 0x14;
                      uStack_132 = 2;
                      uVar10 = func_0x00506b06(uVar3,&uStack_13c);
                      uVar14 = uVar14 | uVar10;
                      if (uVar14 != 0) {
                        iVar15 = FUN_0043d0ce();
                        if (iVar15 << 0x1e < 0) {
                          FUN_0043d574(1,PTR_s_sensor_imu_004a458c,
                                       PTR_s_D__01_workspace_s200_ap510b_iar__004a4588,
                                       PTR_s_DRV_IMUSetSensorParameters_004a4580,0x248,
                                       PTR_s_IMU_Error__At__s__line__d__004a4584,
                                       PTR_s_DRV_IMUSetSensorParameters_004a4580,0x248);
                        }
                        iVar15 = FUN_0043d0ce();
                        if ((-1 < iVar15 << 0x1f) && (iVar15 = FUN_0043d0ce(), -1 < iVar15 << 0x1d))
                        {
                          return uVar14;
                        }
                        compress_log_output(0x4800000,
                                            PTR_s__sensor_imu_IMU_Error__At__s__li_004a45fc,
                                            PTR_s__sensor_imu_IMU_Error__At__s__li_004a45fc,
                                            PTR_s_DRV_IMUSetSensorParameters_004a4580,0x248);
                        return uVar14;
                      }
                    }
                    uVar14 = func_0x0050699a(uVar3,auStack_104);
                    pcVar7 = _DAT_004a497c;
                    if (*_DAT_004a497c == '\0') {
                      uStack_100 = 0;
                    }
                    else {
                      uStack_100 = 1;
                      uVar10 = func_0x0050481a(uVar3,0xd,0xd,0xd,1,0);
                      uVar11 = func_0x00504888(uVar3);
                      uVar14 = uVar14 | uVar10 | uVar11;
                    }
                    uVar10 = func_0x00506a6e(uVar3,auStack_104);
                    uVar14 = uVar14 | uVar10;
                    if (*pcVar5 == '\0' && *pcVar7 == '\0') {
                      uVar10 = func_0x005048ba(uVar3);
                      uVar14 = uVar10 | uVar14;
                    }
                    pcVar7 = _DAT_004a4980;
                    if (*_DAT_004a4980 != '\0') {
                      uVar10 = func_0x00506bd2(uVar3,&uStack_d0);
                      puVar8 = _DAT_004a4984;
                      uStack_cc = *_DAT_004a4284;
                      uStack_d0 = 1;
                      if (cVar17 == '\0') {
                        uStack_c8 = 0;
                      }
                      else {
                        uStack_c8 = 40000;
                      }
                      *_DAT_004a4984 = 0;
                      uVar11 = FUN_005075d6(uVar3,_DAT_004a4988,*puVar8);
                      uVar12 = FUN_00508e5c(uVar3,0xa2a2,1,auStack_cf);
                      uVar13 = func_0x00506eca(uVar3,&uStack_d0);
                      uVar16 = FUN_00507694(uVar3,*pcVar2,cVar17);
                      uVar16 = uVar14 | uVar10 | uVar11 | uVar12 | uVar13 | uVar16;
                      if (uVar16 != 0) {
                        iVar15 = FUN_0043d0ce();
                        if (iVar15 << 0x1e < 0) {
                          FUN_0043d574(1,PTR_s_sensor_imu_004a458c,
                                       PTR_s_D__01_workspace_s200_ap510b_iar__004a4588,
                                       PTR_s_DRV_IMUSetSensorParameters_004a4580,0x26c,
                                       PTR_s_IMU_Error__At__s__line__d__004a4584,
                                       PTR_s_DRV_IMUSetSensorParameters_004a4580,0x26c);
                        }
                        iVar15 = FUN_0043d0ce();
                        if ((-1 < iVar15 << 0x1f) && (iVar15 = FUN_0043d0ce(), -1 < iVar15 << 0x1d))
                        {
                          return uVar16;
                        }
                        compress_log_output(0x4800000,
                                            PTR_s__sensor_imu_IMU_Error__At__s__li_004a45fc,
                                            PTR_s__sensor_imu_IMU_Error__At__s__li_004a45fc,
                                            PTR_s_DRV_IMUSetSensorParameters_004a4580,0x26c);
                        return uVar16;
                      }
                      uVar14 = func_0x00508e8a(uVar3,0x4a0,4,auStack_fc);
                    }
                    uVar10 = FUN_00505fcc(uVar3,2);
                    uVar14 = uVar14 | uVar10;
                    if (uVar14 == 0) {
                      osDelay(10);
                      if (*pcVar2 != '\0') {
                        if (*_DAT_004a498c == '\0') {
                          uVar14 = func_0x00506008(uVar3,3);
                        }
                        else {
                          uVar14 = func_0x00506008(uVar3,2);
                        }
                        if (uVar14 != 0) {
                          iVar15 = FUN_0043d0ce();
                          if (iVar15 << 0x1e < 0) {
                            FUN_0043d574(1,PTR_s_sensor_imu_004a458c,
                                         PTR_s_D__01_workspace_s200_ap510b_iar__004a4588,
                                         PTR_s_DRV_IMUSetSensorParameters_004a4580,0x281,
                                         PTR_s_IMU_Error__At__s__line__d__004a4584,
                                         PTR_s_DRV_IMUSetSensorParameters_004a4580,0x281);
                          }
                          iVar15 = FUN_0043d0ce();
                          if ((-1 < iVar15 << 0x1f) &&
                             (iVar15 = FUN_0043d0ce(), -1 < iVar15 << 0x1d)) {
                            return uVar14;
                          }
                          compress_log_output(0x4800000,
                                              PTR_s__sensor_imu_IMU_Error__At__s__li_004a45fc,
                                              PTR_s__sensor_imu_IMU_Error__At__s__li_004a45fc,
                                              PTR_s_DRV_IMUSetSensorParameters_004a4580,0x281);
                          return uVar14;
                        }
                        osDelay(10);
                      }
                      uVar14 = func_0x00507710(uVar3,DAT_004a4990);
                      if (cVar17 != '\0') {
                        uVar10 = FUN_00507576(uVar3,DAT_004a4994);
                        uVar11 = func_0x00507ace(uVar3);
                        uVar14 = uVar11 | uVar14 | uVar10;
                      }
                      if (uVar14 == 0) {
                        uVar14 = func_0x00508a98(uVar3,0);
                        piVar9 = _DAT_004a4998;
                        if (*_DAT_004a4998 == 0) {
                          uVar10 = func_0x00508b5a(uVar3);
                        }
                        else {
                          uVar10 = func_0x00508ab4(uVar3);
                        }
                        uVar14 = uVar14 | uVar10;
                        FUN_0043c0e4(auStack_11c,0xe,0);
                        if (*pcVar4 != '\0') {
                          uVar10 = func_0x005082d0(uVar3);
                          uVar14 = uVar14 | uVar10;
                          uStack_115 = 1;
                        }
                        if (*pcVar5 != '\0') {
                          uVar10 = func_0x0050872c(uVar3);
                          uVar14 = uVar14 | uVar10;
                          uStack_110 = 1;
                          uStack_10f = 1;
                        }
                        if (*pcVar7 != '\0') {
                          uVar10 = func_0x00507a30(uVar3);
                          uVar10 = uVar14 | uVar10;
                          uVar14 = 0;
                          if (uVar10 != 0) {
                            iVar15 = FUN_0043d0ce();
                            if (iVar15 << 0x1e < 0) {
                              FUN_0043d574(1,PTR_s_sensor_imu_004a458c,
                                           PTR_s_D__01_workspace_s200_ap510b_iar__004a4588,
                                           PTR_s_DRV_IMUSetSensorParameters_004a4580,0x2aa,
                                           PTR_s_IMU_Error__At__s__line__d__004a4584,
                                           PTR_s_DRV_IMUSetSensorParameters_004a4580,0x2aa);
                            }
                            iVar15 = FUN_0043d0ce();
                            if ((-1 < iVar15 << 0x1f) &&
                               (iVar15 = FUN_0043d0ce(), -1 < iVar15 << 0x1d)) {
                              return uVar10;
                            }
                            compress_log_output(0x4800000,
                                                PTR_s__sensor_imu_IMU_Error__At__s__li_004a45fc,
                                                PTR_s__sensor_imu_IMU_Error__At__s__li_004a45fc,
                                                PTR_s_DRV_IMUSetSensorParameters_004a4580,0x2aa);
                            return uVar10;
                          }
                        }
                        if (*pcVar6 != '\0') {
                          uVar10 = func_0x005079bc(uVar3);
                          uVar14 = uVar14 | uVar10;
                          auStack_11c[0] = 1;
                        }
                        FUN_0043c0e4(&uStack_f8,0xf,0);
                        uStack_ea = 1;
                        if (*pcVar7 != '\0') {
                          uStack_f7 = 1;
                        }
                        uStack_f6 = 0;
                        uVar10 = FUN_0050637c(uVar3,0,&uStack_f8);
                        uVar14 = uVar14 | uVar10;
                        if (uVar14 == 0) {
                          if (*piVar9 != 0) {
                            uStack_118 = 1;
                            uStack_117 = 1;
                            uStack_113 = 1;
                          }
                          uVar14 = func_0x00507726(uVar3,auStack_11c);
                          if (uVar14 == 0) {
                            if (*pcVar7 != '\0') {
                              uVar14 = FUN_005059c0(uVar3,&uStack_130);
                              uStack_12a = 2;
                              uStack_129 = 7;
                              uStack_12c = *_DAT_004a4ed0;
                              uStack_12e = 0;
                              uStack_130 = 1;
                              uStack_12f = 1;
                              uStack_128 = 1;
                              uStack_126 = 1;
                              uStack_125 = 1;
                              uStack_123 = 0;
                              uStack_127 = 0;
                              uStack_124 = 1;
                              uVar10 = FUN_00505aa2(uVar3,&uStack_130);
                              uVar10 = uVar10 | uVar14;
                              uVar14 = 0;
                              if (uVar10 != 0) {
                                iVar15 = FUN_0043d0ce();
                                if (iVar15 << 0x1e < 0) {
                                  FUN_0043d574(1,PTR_s_sensor_imu_004a458c,
                                               PTR_s_D__01_workspace_s200_ap510b_iar__004a4588,
                                               PTR_s_DRV_IMUSetSensorParameters_004a4580,0x2de,
                                               PTR_s_IMU_Error__At__s__line__d__004a4584,
                                               PTR_s_DRV_IMUSetSensorParameters_004a4580,0x2de);
                                }
                                iVar15 = FUN_0043d0ce();
                                if ((-1 < iVar15 << 0x1f) &&
                                   (iVar15 = FUN_0043d0ce(), -1 < iVar15 << 0x1d)) {
                                  return uVar10;
                                }
                                compress_log_output(0x4800000,
                                                    PTR_s__sensor_imu_IMU_Error__At__s__li_004a45fc,
                                                    PTR_s__sensor_imu_IMU_Error__At__s__li_004a45fc,
                                                    PTR_s_DRV_IMUSetSensorParameters_004a4580,0x2de)
                                ;
                                return uVar10;
                              }
                            }
                            if (((*pcVar7 != '\0' || *pcVar4 != '\0') || *pcVar5 != '\0') ||
                               (*pcVar6 != '\0')) {
                              uVar10 = func_0x005080fa(uVar3,0,3);
                              uVar11 = func_0x005078a0(uVar3);
                              uVar14 = uVar11 | uVar14 | uVar10;
                            }
                            if (uVar14 != 0) {
                              iVar15 = FUN_0043d0ce();
                              if (iVar15 << 0x1e < 0) {
                                FUN_0043d574(1,PTR_s_sensor_imu_004a458c,
                                             PTR_s_D__01_workspace_s200_ap510b_iar__004a4588,
                                             PTR_s_DRV_IMUSetSensorParameters_004a4580,0x2e9,
                                             PTR_s_IMU_Error__At__s__line__d__004a4584,
                                             PTR_s_DRV_IMUSetSensorParameters_004a4580,0x2e9);
                              }
                              iVar15 = FUN_0043d0ce();
                              if ((iVar15 << 0x1f < 0) ||
                                 (iVar15 = FUN_0043d0ce(), iVar15 << 0x1d < 0)) {
                                compress_log_output(0x4800000,
                                                    PTR_s__sensor_imu_IMU_Error__At__s__li_004a45fc,
                                                    PTR_s__sensor_imu_IMU_Error__At__s__li_004a45fc,
                                                    PTR_s_DRV_IMUSetSensorParameters_004a4580,0x2e9)
                                ;
                              }
                            }
                          }
                          else {
                            iVar15 = FUN_0043d0ce();
                            if (iVar15 << 0x1e < 0) {
                              FUN_0043d574(1,PTR_s_sensor_imu_004a458c,
                                           PTR_s_D__01_workspace_s200_ap510b_iar__004a4588,
                                           PTR_s_DRV_IMUSetSensorParameters_004a4580,0x2c8,
                                           PTR_s_IMU_Error__At__s__line__d__004a4584,
                                           PTR_s_DRV_IMUSetSensorParameters_004a4580,0x2c8);
                            }
                            iVar15 = FUN_0043d0ce();
                            if ((iVar15 << 0x1f < 0) ||
                               (iVar15 = FUN_0043d0ce(), iVar15 << 0x1d < 0)) {
                              compress_log_output(0x4800000,
                                                  PTR_s__sensor_imu_IMU_Error__At__s__li_004a45fc,
                                                  PTR_s__sensor_imu_IMU_Error__At__s__li_004a45fc,
                                                  PTR_s_DRV_IMUSetSensorParameters_004a4580,0x2c8);
                            }
                          }
                        }
                        else {
                          iVar15 = FUN_0043d0ce();
                          if (iVar15 << 0x1e < 0) {
                            FUN_0043d574(1,PTR_s_sensor_imu_004a458c,
                                         PTR_s_D__01_workspace_s200_ap510b_iar__004a4588,
                                         PTR_s_DRV_IMUSetSensorParameters_004a4580,0x2bd,
                                         PTR_s_IMU_Error__At__s__line__d__004a4584,
                                         PTR_s_DRV_IMUSetSensorParameters_004a4580,0x2bd);
                          }
                          iVar15 = FUN_0043d0ce();
                          if ((iVar15 << 0x1f < 0) || (iVar15 = FUN_0043d0ce(), iVar15 << 0x1d < 0))
                          {
                            compress_log_output(0x4800000,
                                                PTR_s__sensor_imu_IMU_Error__At__s__li_004a45fc,
                                                PTR_s__sensor_imu_IMU_Error__At__s__li_004a45fc,
                                                PTR_s_DRV_IMUSetSensorParameters_004a4580,0x2bd);
                          }
                        }
                      }
                      else {
                        iVar15 = FUN_0043d0ce();
                        if (iVar15 << 0x1e < 0) {
                          FUN_0043d574(1,PTR_s_sensor_imu_004a458c,
                                       PTR_s_D__01_workspace_s200_ap510b_iar__004a4588,
                                       PTR_s_DRV_IMUSetSensorParameters_004a4580,0x28d,
                                       PTR_s_IMU_Error__At__s__line__d__004a4584,
                                       PTR_s_DRV_IMUSetSensorParameters_004a4580,0x28d);
                        }
                        iVar15 = FUN_0043d0ce();
                        if ((iVar15 << 0x1f < 0) || (iVar15 = FUN_0043d0ce(), iVar15 << 0x1d < 0)) {
                          compress_log_output(0x4800000,
                                              PTR_s__sensor_imu_IMU_Error__At__s__li_004a45fc,
                                              PTR_s__sensor_imu_IMU_Error__At__s__li_004a45fc,
                                              PTR_s_DRV_IMUSetSensorParameters_004a4580,0x28d);
                        }
                      }
                    }
                    else {
                      iVar15 = FUN_0043d0ce();
                      if (iVar15 << 0x1e < 0) {
                        FUN_0043d574(1,PTR_s_sensor_imu_004a458c,
                                     PTR_s_D__01_workspace_s200_ap510b_iar__004a4588,
                                     PTR_s_DRV_IMUSetSensorParameters_004a4580,0x276,
                                     PTR_s_IMU_Error__At__s__line__d__004a4584,
                                     PTR_s_DRV_IMUSetSensorParameters_004a4580,0x276);
                      }
                      iVar15 = FUN_0043d0ce();
                      if ((iVar15 << 0x1f < 0) || (iVar15 = FUN_0043d0ce(), iVar15 << 0x1d < 0)) {
                        compress_log_output(0x4800000,
                                            PTR_s__sensor_imu_IMU_Error__At__s__li_004a45fc,
                                            PTR_s__sensor_imu_IMU_Error__At__s__li_004a45fc,
                                            PTR_s_DRV_IMUSetSensorParameters_004a4580,0x276);
                      }
                    }
                  }
                  else {
                    iVar15 = FUN_0043d0ce();
                    if (iVar15 << 0x1e < 0) {
                      FUN_0043d574(1,PTR_s_sensor_imu_004a458c,
                                   PTR_s_D__01_workspace_s200_ap510b_iar__004a4588,
                                   PTR_s_DRV_IMUSetSensorParameters_004a4580,0x217,
                                   PTR_s_IMU_Error__At__s__line__d__004a4584,
                                   PTR_s_DRV_IMUSetSensorParameters_004a4580,0x217);
                    }
                    iVar15 = FUN_0043d0ce();
                    if ((iVar15 << 0x1f < 0) || (iVar15 = FUN_0043d0ce(), iVar15 << 0x1d < 0)) {
                      compress_log_output(0x4800000,PTR_s__sensor_imu_IMU_Error__At__s__li_004a45fc,
                                          PTR_s__sensor_imu_IMU_Error__At__s__li_004a45fc,
                                          PTR_s_DRV_IMUSetSensorParameters_004a4580,0x217);
                    }
                  }
                }
                else {
                  iVar15 = FUN_0043d0ce();
                  if (iVar15 << 0x1e < 0) {
                    FUN_0043d574(1,PTR_s_sensor_imu_004a458c,
                                 PTR_s_D__01_workspace_s200_ap510b_iar__004a4588,
                                 PTR_s_DRV_IMUSetSensorParameters_004a4580,0x213,
                                 PTR_s_IMU_Error__At__s__line__d__004a4584,
                                 PTR_s_DRV_IMUSetSensorParameters_004a4580,0x213);
                  }
                  iVar15 = FUN_0043d0ce();
                  if ((iVar15 << 0x1f < 0) || (iVar15 = FUN_0043d0ce(), iVar15 << 0x1d < 0)) {
                    compress_log_output(0x4800000,PTR_s__sensor_imu_IMU_Error__At__s__li_004a45fc,
                                        PTR_s__sensor_imu_IMU_Error__At__s__li_004a45fc,
                                        PTR_s_DRV_IMUSetSensorParameters_004a4580,0x213);
                  }
                }
              }
              else {
                iVar15 = FUN_0043d0ce();
                if (iVar15 << 0x1e < 0) {
                  FUN_0043d574(1,PTR_s_sensor_imu_004a458c,
                               PTR_s_D__01_workspace_s200_ap510b_iar__004a4588,
                               PTR_s_DRV_IMUSetSensorParameters_004a4580,0x205,
                               PTR_s_IMU_Error__At__s__line__d__004a4584,
                               PTR_s_DRV_IMUSetSensorParameters_004a4580,0x205);
                }
                iVar15 = FUN_0043d0ce();
                if ((iVar15 << 0x1f < 0) || (iVar15 = FUN_0043d0ce(), iVar15 << 0x1d < 0)) {
                  compress_log_output(0x4800000,PTR_s__sensor_imu_IMU_Error__At__s__li_004a45fc,
                                      PTR_s__sensor_imu_IMU_Error__At__s__li_004a45fc,
                                      PTR_s_DRV_IMUSetSensorParameters_004a4580,0x205);
                }
              }
            }
            else {
              iVar15 = FUN_0043d0ce();
              if (iVar15 << 0x1e < 0) {
                FUN_0043d574(1,PTR_s_sensor_imu_004a458c,
                             PTR_s_D__01_workspace_s200_ap510b_iar__004a4588,
                             PTR_s_DRV_IMUSetSensorParameters_004a4580,0x200,
                             PTR_s_IMU_Error__At__s__line__d__004a4584,
                             PTR_s_DRV_IMUSetSensorParameters_004a4580,0x200);
              }
              iVar15 = FUN_0043d0ce();
              if ((iVar15 << 0x1f < 0) || (iVar15 = FUN_0043d0ce(), iVar15 << 0x1d < 0)) {
                compress_log_output(0x4800000,PTR_s__sensor_imu_IMU_Error__At__s__li_004a45fc,
                                    PTR_s__sensor_imu_IMU_Error__At__s__li_004a45fc,
                                    PTR_s_DRV_IMUSetSensorParameters_004a4580,0x200);
              }
            }
          }
          else {
            iVar15 = FUN_0043d0ce();
            if (iVar15 << 0x1e < 0) {
              FUN_0043d574(1,PTR_s_sensor_imu_004a458c,
                           PTR_s_D__01_workspace_s200_ap510b_iar__004a4588,
                           PTR_s_DRV_IMUSetSensorParameters_004a4580,0x1f8,
                           PTR_s_IMU_Error__At__s__line__d__004a4584,
                           PTR_s_DRV_IMUSetSensorParameters_004a4580,0x1f8);
            }
            iVar15 = FUN_0043d0ce();
            if ((iVar15 << 0x1f < 0) || (iVar15 = FUN_0043d0ce(), iVar15 << 0x1d < 0)) {
              compress_log_output(0x4800000,PTR_s__sensor_imu_IMU_Error__At__s__li_004a45fc,
                                  PTR_s__sensor_imu_IMU_Error__At__s__li_004a45fc,
                                  PTR_s_DRV_IMUSetSensorParameters_004a4580,0x1f8);
            }
          }
        }
        else {
          iVar15 = FUN_0043d0ce();
          if (iVar15 << 0x1e < 0) {
            FUN_0043d574(1,PTR_s_sensor_imu_004a458c,PTR_s_D__01_workspace_s200_ap510b_iar__004a4588
                         ,PTR_s_DRV_IMUSetSensorParameters_004a4580,0x1f1,
                         PTR_s_IMU_Error__At__s__line__d__004a4584,
                         PTR_s_DRV_IMUSetSensorParameters_004a4580,0x1f1);
          }
          iVar15 = FUN_0043d0ce();
          if ((iVar15 << 0x1f < 0) || (iVar15 = FUN_0043d0ce(), iVar15 << 0x1d < 0)) {
            compress_log_output(0x4800000,PTR_s__sensor_imu_IMU_Error__At__s__li_004a45fc,
                                PTR_s__sensor_imu_IMU_Error__At__s__li_004a45fc,
                                PTR_s_DRV_IMUSetSensorParameters_004a4580,0x1f1);
          }
        }
      }
      else {
        iVar15 = FUN_0043d0ce();
        if (iVar15 << 0x1e < 0) {
          FUN_0043d574(1,PTR_s_sensor_imu_004a458c,PTR_s_D__01_workspace_s200_ap510b_iar__004a4588,
                       PTR_s_DRV_IMUSetSensorParameters_004a4580,0x1e6,
                       PTR_s_IMU_Error__At__s__line__d__004a4584,
                       PTR_s_DRV_IMUSetSensorParameters_004a4580,0x1e6);
        }
        iVar15 = FUN_0043d0ce();
        if ((iVar15 << 0x1f < 0) || (iVar15 = FUN_0043d0ce(), iVar15 << 0x1d < 0)) {
          compress_log_output(0x4800000,PTR_s__sensor_imu_IMU_Error__At__s__li_004a45fc,
                              PTR_s__sensor_imu_IMU_Error__At__s__li_004a45fc,
                              PTR_s_DRV_IMUSetSensorParameters_004a4580,0x1e6);
        }
      }
    }
    else {
      iVar15 = FUN_0043d0ce();
      if (iVar15 << 0x1e < 0) {
        FUN_0043d574(1,PTR_s_sensor_imu_004a458c,PTR_s_D__01_workspace_s200_ap510b_iar__004a4588,
                     PTR_s_DRV_IMUSetSensorParameters_004a4580,0x1e1,
                     PTR_s_IMU_Error__At__s__line__d__004a4584,
                     PTR_s_DRV_IMUSetSensorParameters_004a4580,0x1e1);
      }
      iVar15 = FUN_0043d0ce();
      if ((iVar15 << 0x1f < 0) || (iVar15 = FUN_0043d0ce(), iVar15 << 0x1d < 0)) {
        compress_log_output(0x4800000,PTR_s__sensor_imu_IMU_Error__At__s__li_004a45fc,
                            PTR_s__sensor_imu_IMU_Error__At__s__li_004a45fc,
                            PTR_s_DRV_IMUSetSensorParameters_004a4580,0x1e1);
      }
    }
  }
  else {
    iVar15 = FUN_0043d0ce();
    if (iVar15 << 0x1e < 0) {
      FUN_0043d574(1,PTR_s_sensor_imu_004a458c,PTR_s_D__01_workspace_s200_ap510b_iar__004a4588,
                   PTR_s_DRV_IMUSetSensorParameters_004a4580,0x1d8,
                   PTR_s_IMU_Error__At__s__line__d__004a4584,
                   PTR_s_DRV_IMUSetSensorParameters_004a4580,0x1d8);
    }
    iVar15 = FUN_0043d0ce();
    if ((iVar15 << 0x1f < 0) || (iVar15 = FUN_0043d0ce(), iVar15 << 0x1d < 0)) {
      compress_log_output(0x4800000,PTR_s__sensor_imu_IMU_Error__At__s__li_004a45fc,
                          PTR_s__sensor_imu_IMU_Error__At__s__li_004a45fc,
                          PTR_s_DRV_IMUSetSensorParameters_004a4580,0x1d8);
    }
  }
  return uVar14;
}

