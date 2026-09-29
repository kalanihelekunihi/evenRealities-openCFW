
undefined4 pt_cmd_43_handler(int param_1,byte param_2,undefined1 *param_3,byte *param_4)

{
  bool bVar1;
  int iVar2;
  undefined4 uVar3;
  float *pfVar4;
  undefined *puVar5;
  uint uVar6;
  byte bVar7;
  undefined4 local_78;
  undefined4 uStack_74;
  undefined4 uStack_70;
  undefined4 local_6c;
  undefined4 uStack_68;
  undefined4 uStack_64;
  float local_60 [9];
  float local_3c [9];
  
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    FUN_0043d574(3,DAT_005747d4,DAT_005747d0,DAT_005747fc,0xa2d,DAT_005747f8);
  }
  iVar2 = FUN_0043d0ce();
  if (-1 < iVar2 << 0x1f) {
    iVar2 = FUN_0043d0ce();
    if (-1 < iVar2 << 0x1d) goto LAB_00574232;
  }
  compress_log_output(0xc000000,DAT_00574800,DAT_00574800);
LAB_00574232:
  if ((((param_3 == (undefined1 *)0x0) || (param_4 == (byte *)0x0)) || (param_1 == 0)) ||
     (param_2 < 4)) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,DAT_005747d4,DAT_005747d0,DAT_005747fc,0xa30,DAT_00574798,DAT_005747fc);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_0057479c,DAT_0057479c,DAT_005747fc);
    }
    uVar3 = 0xffffffff;
  }
  else {
    *param_3 = 0x45;
    param_3[1] = 1;
    param_3[2] = 3;
    param_3[3] = 0xd;
    HUB_IMUCalibParaInit();
    local_6c = 0;
    uStack_68 = 0;
    uStack_64 = 0;
    local_78 = 0;
    uStack_74 = 0;
    uStack_70 = 0;
    FUN_0048949c(local_3c,0x24);
    nvdbSensorCaldataAgRead(&local_6c,&local_78,local_3c);
    FUN_00439c04(local_60,DAT_00574804,0x24);
    bVar1 = true;
    for (iVar2 = 0; iVar2 < 9; iVar2 = iVar2 + 1) {
      if (DAT_00574570 <= ABS((double)(local_3c[iVar2] - local_60[iVar2]))) {
        bVar1 = false;
        break;
      }
    }
    if (bVar1) {
      param_3[4] = 1;
    }
    else {
      param_3[4] = 0;
    }
    bVar7 = 5;
    pfVar4 = (float *)semantic_get_orientation_vector();
    for (uVar6 = 0; uVar6 < 4; uVar6 = uVar6 + 1) {
      param_3[bVar7] = *(undefined1 *)((int)pfVar4 + uVar6);
      bVar7 = bVar7 + 1;
    }
    for (uVar6 = 0; uVar6 < 4; uVar6 = uVar6 + 1) {
      param_3[bVar7] = *(undefined1 *)((int)pfVar4 + uVar6 + 4);
      bVar7 = bVar7 + 1;
    }
    for (uVar6 = 0; uVar6 < 4; uVar6 = uVar6 + 1) {
      param_3[bVar7] = *(undefined1 *)((int)pfVar4 + uVar6 + 8);
      bVar7 = bVar7 + 1;
    }
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      if (bVar1) {
        puVar5 = &DAT_00574578;
      }
      else {
        puVar5 = &DAT_0057457c;
      }
      FUN_0043d574(3,DAT_005747d4,DAT_005747d0,DAT_005747fc,0xa75,DAT_00574f40,puVar5);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      if (bVar1) {
        puVar5 = &DAT_00574578;
      }
      else {
        puVar5 = &DAT_0057457c;
      }
      compress_log_output(0xd000000,DAT_00574f44,DAT_00574f44,puVar5,(double)*pfVar4,
                          (double)pfVar4[1],(double)pfVar4[2]);
    }
    *param_4 = bVar7;
    uVar3 = 0;
  }
  return uVar3;
}

