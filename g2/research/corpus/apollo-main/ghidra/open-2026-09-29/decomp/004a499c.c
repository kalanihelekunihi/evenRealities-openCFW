
/* WARNING: Type propagation algorithm not settling */
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

uint DRV_IMUReadData(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  undefined4 uVar2;
  undefined4 *puVar3;
  char *pcVar4;
  undefined1 *puVar5;
  uint uVar6;
  int iVar7;
  uint uVar8;
  undefined1 auStack_58 [2];
  ushort uStack_56;
  char acStack_54 [8];
  char acStack_4c [7];
  char cStack_45;
  char cStack_40;
  char cStack_3f;
  undefined1 uStack_3c;
  char cStack_3b;
  char cStack_3a;
  char cStack_2e;
  int iStack_2c;
  int iStack_28;
  int iStack_24;
  undefined4 uStack_20;
  
  uStack_20 = param_4;
  FUN_0043c0e4(&uStack_3c,0xf,0);
  uVar1 = DAT_004a5380;
  uStack_56 = 0;
  auStack_58[0] = 0;
  uVar6 = FUN_005065cc(DAT_004a5380,0,&uStack_3c);
  iVar7 = _DAT_004a548c;
  if (uVar6 != 0) {
    iVar7 = FUN_0043d0ce();
    if (iVar7 << 0x1e < 0) {
      FUN_0043d574(1,DAT_004a5378,DAT_004a5374,_DAT_004a5488,0x3aa,DAT_004a5384,_DAT_004a5488,0x3aa)
      ;
    }
    iVar7 = FUN_0043d0ce();
    if ((-1 < iVar7 << 0x1f) && (iVar7 = FUN_0043d0ce(), -1 < iVar7 << 0x1d)) {
      return uVar6;
    }
    compress_log_output(0x4800000,DAT_004a5388,DAT_004a5388,_DAT_004a5488,0x3aa);
    return uVar6;
  }
  if (cStack_3a != '\0') {
    uVar6 = func_0x005061f8(uVar1,_DAT_004a548c);
    uVar2 = _DAT_004a5490;
    if (uVar6 != 0) {
      iVar7 = FUN_0043d0ce();
      if (iVar7 << 0x1e < 0) {
        FUN_0043d574(1,DAT_004a5378,DAT_004a5374,_DAT_004a5488,0x3b1,DAT_004a5384,_DAT_004a5488,
                     0x3b1);
      }
      iVar7 = FUN_0043d0ce();
      if ((-1 < iVar7 << 0x1f) && (iVar7 = FUN_0043d0ce(), -1 < iVar7 << 0x1d)) {
        return uVar6;
      }
      compress_log_output(0x4800000,DAT_004a5388,DAT_004a5388,_DAT_004a5488,0x3b1);
      return uVar6;
    }
    func_0x005066ee(iVar7,_DAT_004a5490);
    func_0x005066ee(iVar7 + 6,uVar2);
    iStack_2c = (int)*(short *)(iVar7 + 6);
    iStack_28 = (int)*(short *)(iVar7 + 8);
    iStack_24 = (int)*(short *)(iVar7 + 10);
  }
  puVar3 = DAT_004a5698;
  if (cStack_3b != '\0') {
    FUN_0043c0e4(DAT_004a5698,0x8cc,0);
    *puVar3 = param_1;
    uVar2 = _DAT_004a569c;
    uVar6 = FUN_00505888(uVar1,_DAT_004a569c,&uStack_56);
    if (uVar6 != 0) {
      iVar7 = FUN_0043d0ce();
      if (iVar7 << 0x1e < 0) {
        FUN_0043d574(1,DAT_004a5378,DAT_004a5374,_DAT_004a5488,0x3cd,DAT_004a5384,_DAT_004a5488,
                     0x3cd);
      }
      iVar7 = FUN_0043d0ce();
      if ((-1 < iVar7 << 0x1f) && (iVar7 = FUN_0043d0ce(), -1 < iVar7 << 0x1d)) {
        return uVar6;
      }
      compress_log_output(0x4800000,DAT_004a5388,DAT_004a5388,_DAT_004a5488,0x3cd);
      return uVar6;
    }
    puVar3[1] = (uint)uStack_56;
    uVar6 = func_0x005058b2(uVar1,uVar2,uStack_56);
    if (uVar6 != 0) {
      iVar7 = FUN_0043d0ce();
      if (iVar7 << 0x1e < 0) {
        FUN_0043d574(1,DAT_004a5378,DAT_004a5374,_DAT_004a5488,0x3d0,DAT_004a5384,_DAT_004a5488,
                     0x3d0);
      }
      iVar7 = FUN_0043d0ce();
      if ((-1 < iVar7 << 0x1f) && (iVar7 = FUN_0043d0ce(), -1 < iVar7 << 0x1d)) {
        return uVar6;
      }
      compress_log_output(0x4800000,DAT_004a5388,DAT_004a5388,_DAT_004a5488,0x3d0);
      return uVar6;
    }
    semantic_postprocess_samples();
  }
  uVar6 = 0;
  if (cStack_2e != '\0') {
    FUN_0043c0e4(acStack_4c,0xe,0);
    uVar6 = func_0x00507b00(uVar1,acStack_4c);
    if (uVar6 == 0) {
      if ((*_DAT_004a56a4 != '\0') && (cStack_45 != '\0')) {
        iVar7 = FUN_0043d0ce();
        if (iVar7 << 0x1e < 0) {
          FUN_0043d574(2,DAT_004a5378,DAT_004a5374,_DAT_004a5488,0x3da,_DAT_004a56a8);
        }
        iVar7 = FUN_0043d0ce();
        if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
          compress_log_output(0x8000000,_DAT_004a56ac,_DAT_004a56ac);
        }
      }
      pcVar4 = _DAT_004a56b0;
      if ((*_DAT_004a56b0 != '\0') && (cStack_3f != '\0')) {
        uVar6 = func_0x00508830(uVar1,0,auStack_58);
        puVar5 = _DAT_004a56b4;
        *_DAT_004a56b4 = auStack_58[0];
        IMU_AIDStatePrint(*puVar5,1);
        IMU_AIDStateUpdate(*puVar5,*_DAT_004a56b8);
      }
      if ((*pcVar4 != '\0') && (cStack_40 != '\0')) {
        uVar8 = func_0x0050880a(uVar1,0,auStack_58);
        puVar5 = _DAT_004a56b8;
        uVar6 = uVar6 | uVar8;
        *_DAT_004a56b8 = auStack_58[0];
        IMU_AIDStatePrint(*puVar5,0);
        IMU_AIDStateUpdate(*_DAT_004a56b4,*puVar5);
      }
      if ((*_DAT_004a56bc != '\0') && (acStack_4c[0] != '\0')) {
        uVar8 = func_0x00507ba2(uVar1,acStack_54);
        uVar6 = uVar6 | uVar8;
        if (uVar6 == 0) {
          if (acStack_54[0] == '\x02') {
            iVar7 = FUN_0043d0ce();
            if (iVar7 << 0x1e < 0) {
              FUN_0043d574(2,DAT_004a5378,DAT_004a5374,_DAT_004a5488,0x3f3,
                           PTR_s_IMU_event__TAP_DOUBLE_004a56c0);
            }
            iVar7 = FUN_0043d0ce();
            if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
              compress_log_output(0x8000000,PTR_s__sensor_imu_IMU_event__TAP_DOUBL_004a56c4,
                                  PTR_s__sensor_imu_IMU_event__TAP_DOUBL_004a56c4);
            }
          }
          else {
            iVar7 = FUN_0043d0ce();
            if (iVar7 << 0x1e < 0) {
              FUN_0043d574(2,DAT_004a5378,DAT_004a5374,_DAT_004a5488,0x3f5,
                           PTR_s_IMU_event__TAP_num____d_004a56c8,acStack_54[0]);
            }
            iVar7 = FUN_0043d0ce();
            if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
              compress_log_output(0x8400000,_DAT_004a5b68,_DAT_004a5b68,acStack_54[0]);
            }
          }
        }
        else {
          iVar7 = FUN_0043d0ce();
          if (iVar7 << 0x1e < 0) {
            FUN_0043d574(1,DAT_004a5378,DAT_004a5374,_DAT_004a5488,0x3f1,DAT_004a5384,_DAT_004a5488,
                         0x3f1);
          }
          iVar7 = FUN_0043d0ce();
          if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
            compress_log_output(0x4800000,DAT_004a5388,DAT_004a5388,_DAT_004a5488,0x3f1);
          }
        }
      }
    }
    else {
      iVar7 = FUN_0043d0ce();
      if (iVar7 << 0x1e < 0) {
        FUN_0043d574(1,DAT_004a5378,DAT_004a5374,_DAT_004a5488,0x3d8,DAT_004a5384,_DAT_004a5488,
                     0x3d8);
      }
      iVar7 = FUN_0043d0ce();
      if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
        compress_log_output(0x4800000,DAT_004a5388,DAT_004a5388,_DAT_004a5488,0x3d8);
      }
    }
  }
  return uVar6;
}

