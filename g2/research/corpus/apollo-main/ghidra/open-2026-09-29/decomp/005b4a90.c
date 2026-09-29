
undefined4 FUN_005b4a90(int param_1,int param_2)

{
  byte bVar1;
  int iVar2;
  undefined4 uVar3;
  uint local_30;
  uint local_2c;
  uint local_28;
  uint local_24;
  uint local_20;
  uint local_1c;
  uint local_18;
  
  if (param_2 == 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      local_2c = DAT_005b5418;
      local_30 = 0x7d;
      FUN_0043d574(1,DAT_005b52d8,DAT_005b52d4,DAT_005b541c);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_005b5420);
    }
    return 0xffffffff;
  }
  bVar1 = FUN_005b16d0();
  if (((bVar1 != 0) && (bVar1 != 1)) && (bVar1 != 3)) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      local_24 = FUN_005b16dc(bVar1);
      local_28 = (uint)bVar1;
      local_2c = DAT_005b5424;
      local_30 = 0x84;
      FUN_0043d574(1,DAT_005b52d8,DAT_005b52d4,DAT_005b541c);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      local_30 = FUN_005b16dc(bVar1);
      compress_log_output(0x4800000,DAT_005b55a8,DAT_005b55a8,bVar1);
    }
    return 0xffffffff;
  }
  *DAT_005b5410 = 1;
  if (*(char *)(param_2 + 1) != '\0') {
    FUN_00439be4(param_1 + 1,param_2 + 2,5);
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      local_18 = (uint)*(byte *)(param_1 + 5);
      local_1c = (uint)*(byte *)(param_1 + 4);
      local_20 = (uint)*(byte *)(param_1 + 3);
      local_24 = (uint)*(byte *)(param_1 + 2);
      local_28 = (uint)*(byte *)(param_1 + 1);
      local_2c = DAT_005b55ac;
      local_30 = 0x8d;
      FUN_0043d574(3,DAT_005b52d8,DAT_005b52d4,DAT_005b541c);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      local_24 = (uint)*(byte *)(param_1 + 5);
      local_28 = (uint)*(byte *)(param_1 + 4);
      local_2c = (uint)*(byte *)(param_1 + 3);
      local_30 = (uint)*(byte *)(param_1 + 2);
      compress_log_output(0xd400000,DAT_005b55b0,DAT_005b55b0,*(undefined1 *)(param_1 + 1));
    }
    FUN_005b133c();
    if (*(char *)(param_1 + 4) != '\0') {
      AUDM_appAcquire(4);
    }
  }
  if (*(char *)(param_2 + 7) != '\0') {
    FUN_005b43ee(param_2 + 8);
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      local_24 = *(uint *)(param_2 + 0x8c);
      local_28 = param_2 + 10;
      local_2c = DAT_005b5638;
      local_30 = 0x99;
      FUN_0043d574(4,DAT_005b52d8,DAT_005b52d4,DAT_005b541c);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      local_30 = *(uint *)(param_2 + 0x8c);
      compress_log_output(0x10800000,DAT_005b563c,DAT_005b563c,param_2 + 10);
    }
  }
  FUN_0059619e();
  if (bVar1 == 0) {
    iVar2 = FUN_0045a568();
    if (iVar2 == 1) {
      local_30 = *DAT_005b5640;
      local_2c = DAT_005b5640[1];
      FUN_0048eb32(DAT_005b5644,2,&local_30);
    }
    iVar2 = FUN_0045a568();
    if (iVar2 == 1) {
      FUN_0045a8ee(0xb,0,0,500);
    }
  }
  else if (bVar1 == 1) {
    uVar3 = service_time_current_epoch_get();
    FUN_005b02e4(4,uVar3);
  }
  else {
    FUN_005b02e4(3,0);
  }
  return 0;
}

