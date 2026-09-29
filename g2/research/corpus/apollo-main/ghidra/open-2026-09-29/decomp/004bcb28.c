
undefined4 PB_RxUnpairInfo(undefined4 param_1,byte *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  uint uVar3;
  uint local_30;
  uint local_2c;
  uint local_28;
  uint local_24;
  uint local_20;
  uint local_1c;
  uint local_18;
  uint local_14;
  undefined4 uStack_10;
  
  uStack_10 = param_4;
  if (param_2 == (byte *)0x0) {
    FUN_00439c04(&local_30,DAT_004bcff4,0x14);
    local_2c = CONCAT22(local_2c._2_2_,1);
    APP_errorFaultHandler(&local_30);
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      local_2c = DAT_004bcff8;
      local_30 = 0x29b;
      FUN_0043d574(1,DAT_004bcfa4,DAT_004bcfa0,DAT_004bcffc);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_004bd000);
    }
    uVar2 = 2;
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      uVar3 = central_is_ring_owner_side_004a2914();
      iVar1 = FUN_0045a568();
      local_24 = DAT_004bd008;
      if (iVar1 == 1) {
        local_24 = DAT_004bd004;
      }
      local_20 = uVar3 & 0xff;
      local_28 = (uint)*param_2;
      local_2c = DAT_004bd00c;
      local_30 = 0x2a1;
      FUN_0043d574(4,DAT_004bcfa4,DAT_004bcfa0,DAT_004bcffc);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      uVar3 = central_is_ring_owner_side_004a2914();
      iVar1 = FUN_0045a568();
      local_30 = DAT_004bd008;
      if (iVar1 == 1) {
        local_30 = DAT_004bd004;
      }
      local_2c = uVar3 & 0xff;
      compress_log_output(0x10c00000,DAT_004bd010,DAT_004bd010,*param_2);
    }
    if ((*param_2 == 0) || (*param_2 == 2)) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        local_14 = (uint)param_2[4];
        local_18 = (uint)param_2[5];
        local_1c = (uint)param_2[6];
        local_20 = (uint)param_2[7];
        local_24 = (uint)param_2[8];
        local_28 = (uint)param_2[9];
        local_2c = DAT_004bd014;
        local_30 = 0x2a7;
        FUN_0043d574(4,DAT_004bcfa4,DAT_004bcfa0,DAT_004bcffc);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        local_20 = (uint)param_2[4];
        local_24 = (uint)param_2[5];
        local_28 = (uint)param_2[6];
        local_2c = (uint)param_2[7];
        local_30 = (uint)param_2[8];
        compress_log_output(0x11800000,DAT_004bd018,DAT_004bd018,param_2[9]);
      }
      if (*(short *)(param_2 + 2) == 6) {
        FUN_0043dacc(DAT_004bd01c,0x10,param_2 + 4,*(undefined2 *)(param_2 + 2));
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          local_2c = DAT_004bd020;
          local_30 = 0x2ab;
          FUN_0043d574(2,DAT_004bcfa4,DAT_004bcfa0,DAT_004bcffc);
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0x8000000,DAT_004bd024,DAT_004bd024);
        }
        APP_MasterCleanupRingUnpair(param_2 + 4);
      }
      else {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          local_28 = (uint)*(ushort *)(param_2 + 2);
          local_2c = DAT_004bd028;
          local_30 = 0x2af;
          FUN_0043d574(2,DAT_004bcfa4,DAT_004bcfa0,DAT_004bcffc);
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0x8400000,DAT_004bd02c,DAT_004bd02c,*(undefined2 *)(param_2 + 2));
        }
        APP_MasterCleanupRingUnpair(0);
      }
    }
    if (*param_2 == 2) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        local_2c = DAT_004bd030;
        local_30 = 0x2b4;
        FUN_0043d574(4,DAT_004bcfa4,DAT_004bcfa0,DAT_004bcffc);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_004bd034,DAT_004bd034);
      }
      ble_ota_mode_set(1);
      iVar1 = FUN_004b8128();
      if (iVar1 == 3) {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          local_2c = DAT_004bd038;
          local_30 = 0x2b7;
          FUN_0043d574(4,DAT_004bcfa4,DAT_004bcfa0,DAT_004bcffc);
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0x10000000,DAT_004bd03c,DAT_004bd03c);
        }
        APP_BleSlaveDisconnect(0);
      }
      RING_ConnectPolicyReset();
    }
    uVar2 = 0;
  }
  return uVar2;
}

