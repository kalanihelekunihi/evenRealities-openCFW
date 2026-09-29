
undefined4 APP_PbRxDevCfgFrameDataProcess(int param_1,undefined2 param_2)

{
  undefined4 uVar1;
  char cVar2;
  int iVar3;
  undefined4 uVar4;
  undefined1 auStack_114 [12];
  int local_108;
  undefined1 auStack_104 [16];
  undefined1 auStack_f4 [4];
  undefined2 local_f0;
  char local_e0 [2];
  undefined1 local_de;
  undefined1 auStack_d8 [200];
  
  iVar3 = FUN_0043d0ce();
  if (iVar3 << 0x1e < 0) {
    FUN_0043d574(4,DAT_004d8b88,DAT_004d8b84,DAT_004d8b80,0x2c,DAT_004d8b7c,param_2);
  }
  iVar3 = FUN_0043d0ce();
  if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_004d8b8c,DAT_004d8b8c,param_2);
  }
  if (param_1 == 0) {
    FUN_00439c04(auStack_f4,DAT_004d8b90,0x14);
    local_f0 = 1;
    APP_errorFaultHandler(auStack_f4);
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(1,DAT_004d8b88,DAT_004d8b84,DAT_004d8b80,0x2f,DAT_004d8b94);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_004d8b98,DAT_004d8b98);
    }
    uVar4 = 2;
  }
  else {
    FUN_0048949c(local_e0,0xd0);
    FUN_0048f49c(auStack_104,param_1,param_2);
    FUN_00439c04(auStack_114,auStack_104,0x10);
    cVar2 = FUN_00490120(auStack_114,DAT_004d8b9c,local_e0);
    uVar4 = DAT_004d8bac;
    if (cVar2 == '\0') {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        iVar3 = DAT_004d8ba0;
        if (local_108 != 0) {
          iVar3 = local_108;
        }
        FUN_0043d574(1,DAT_004d8b88,DAT_004d8b84,DAT_004d8b80,0x3b,DAT_004d8ba4,iVar3);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        iVar3 = DAT_004d8ba0;
        if (local_108 != 0) {
          iVar3 = local_108;
        }
        compress_log_output(0x4400000,DAT_004d8ba8,DAT_004d8ba8,iVar3);
      }
      uVar4 = 0x2b;
    }
    else {
      FUN_0043c0e4(DAT_004d8bac,0xd0,0);
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(4,DAT_004d8b88,DAT_004d8b84,DAT_004d8b80,0x42,DAT_004d8bb0,local_e0[0]);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_004d8bb4,DAT_004d8bb4,local_e0[0]);
      }
      if (local_e0[0] == '\x04') {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(4,DAT_004d8b88,DAT_004d8b84,DAT_004d8b80,0x4d,DAT_004d8bb8);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x10000000,DAT_004d8bbc,DAT_004d8bbc);
        }
        iVar3 = PB_RxSecAuth(local_de,auStack_d8);
        if (iVar3 == 0) {
          PB_TxEncodeSecAuth(local_de,DAT_004d8bc0,0x100,uVar4,auStack_d8);
        }
      }
      else if (local_e0[0] == '\x05') {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(4,DAT_004d8b88,DAT_004d8b84,DAT_004d8b80,0x55,DAT_004d8bc4);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x10000000,DAT_004d8bc8,DAT_004d8bc8);
        }
        iVar3 = PB_RxPipeRoleChange(local_de,auStack_d8);
        if (iVar3 == 0) {
          PB_TxEncodePipeRoleChange(local_de,DAT_004d8bc0,0x100,uVar4,auStack_d8);
        }
      }
      else if (local_e0[0] == '\x06') {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(4,DAT_004d8b88,DAT_004d8b84,DAT_004d8b80,0x5d,DAT_004d8bcc);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x10000000,DAT_004d8bd0,DAT_004d8bd0);
        }
        iVar3 = PB_RxRingConnectInfo(local_de,auStack_d8);
        if (iVar3 == 0) {
          PB_TxEncodeRingConnectInfo(local_de,DAT_004d8bc0,0x100,uVar4,auStack_d8);
        }
      }
      else if (local_e0[0] == '\a') {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(4,DAT_004d8b88,DAT_004d8b84,DAT_004d8b80,0x65,DAT_004d8bd4);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x10000000,DAT_004d8bd8,DAT_004d8bd8);
        }
        iVar3 = PB_RxBleConnectParams(local_de,auStack_d8);
        if (iVar3 == 0) {
          PB_TxEncodeBleConnectParams(local_de,DAT_004d8bc0,0x100,uVar4,auStack_d8);
        }
      }
      else if (local_e0[0] == '\b') {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(4,DAT_004d8b88,DAT_004d8b84,DAT_004d8b80,0x6d,DAT_004d8bdc);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x10000000,DAT_004d8da0,DAT_004d8da0);
        }
        iVar3 = PB_RxDisconnectInfo(local_de,auStack_d8);
        if (iVar3 == 0) {
          PB_TxEncodeDisconnectInfo(local_de,DAT_004d8bc0,0x100,uVar4,auStack_d8);
        }
      }
      else if (local_e0[0] == '\t') {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(4,DAT_004d8b88,DAT_004d8b84,DAT_004d8b80,0x75,DAT_004d8da4);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x10000000,DAT_004d8da8,DAT_004d8da8);
        }
        iVar3 = PB_RxUnpairInfo(local_de,auStack_d8);
        if (iVar3 == 0) {
          PB_TxEncodeUnpairInfo(local_de,DAT_004d8bc0,0x100,uVar4,auStack_d8);
        }
      }
      else if (local_e0[0] == '\n') {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(4,DAT_004d8b88,DAT_004d8b84,DAT_004d8b80,0x7d,DAT_004d8dac);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x10000000,DAT_004d8db0,DAT_004d8db0);
        }
        APP_PbRxErrorCode(local_de,auStack_d8);
      }
      else if (local_e0[0] == '\v') {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(4,DAT_004d8b88,DAT_004d8b84,DAT_004d8b80,0x89,DAT_004d8eb0);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x10000000,DAT_004d8eb4,DAT_004d8eb4);
        }
      }
      else if (local_e0[0] == '\f') {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(4,DAT_004d8b88,DAT_004d8b84,DAT_004d8b80,0x83,DAT_004d8db4);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x10000000,DAT_004d8eac,DAT_004d8eac);
        }
      }
      else if (local_e0[0] == '\r') {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(4,DAT_004d8b88,DAT_004d8b84,DAT_004d8b80,0x8f,DAT_004d8eb8);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x10000000,DAT_004d8ebc,DAT_004d8ebc);
        }
        iVar3 = PB_RxRestoreFactory(local_de,auStack_d8);
        if (iVar3 == 0) {
          PB_TxEncodeRestoreFactory(local_de,DAT_004d8bc0,0x100,uVar4,auStack_d8);
        }
      }
      else if (local_e0[0] == '\x0e') {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(4,DAT_004d8b88,DAT_004d8b84,DAT_004d8b80,0x97,DAT_004d8ec0);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x10000000,DAT_004d8ec4,DAT_004d8ec4);
        }
        iVar3 = PB_RxBaseConnHeartBeat(local_de,auStack_d8);
        uVar1 = DAT_004d8ec8;
        if (iVar3 == 0) {
          fw_event_loop_remove_delayed(DAT_004d8ec8);
          fw_event_loop_push_delayed(uVar1,0,30000);
          PB_TxEncodeBaseConnHeartBeat(local_de,DAT_004d8bc0,0x100,uVar4,auStack_d8);
        }
      }
      else if (local_e0[0] == '\x0f') {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(4,DAT_004d8b88,DAT_004d8b84,DAT_004d8b80,0xa1,DAT_004d8ecc);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x10000000,DAT_004d8ed0,DAT_004d8ed0);
        }
        iVar3 = PB_RxQuickRestart(local_de,auStack_d8);
        if (iVar3 == 0) {
          PB_TxEncodeQuickRestart(local_de,DAT_004d8bc0,0x100,uVar4,auStack_d8);
        }
      }
      else if (local_e0[0] == -0x80) {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(4,DAT_004d8b88,DAT_004d8b84,DAT_004d8b80,0xa9,DAT_004d8ed4);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x10000000,DAT_004d8ed8,DAT_004d8ed8);
        }
        iVar3 = PB_RxTimeSyncInfo(local_de,auStack_d8);
        if (iVar3 == 0) {
          PB_TxEncodeTimeSyncInfo(local_de,DAT_004d8bc0,0x100,uVar4,auStack_d8);
        }
      }
      else if (local_e0[0] == -0x7f) {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(4,DAT_004d8b88,DAT_004d8b84,DAT_004d8b80,0xb1,DAT_004d8edc);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x10000000,DAT_004d8ee0,DAT_004d8ee0);
        }
        iVar3 = PB_RxAudControl(local_de,auStack_d8);
        if (iVar3 == 0) {
          PB_TxEncodeAudControl(local_de,DAT_004d8bc0,0x100,uVar4,auStack_d8);
        }
      }
      else {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(4,DAT_004d8b88,DAT_004d8b84,DAT_004d8b80,0xb9,DAT_004d8ee4,local_e0[0]);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x10400000,DAT_004d8ee8,DAT_004d8ee8,local_e0[0]);
        }
        APP_PbTxEncodeErrorCode(1,0x80,local_de,local_e0[0],8);
      }
      uVar4 = 0;
    }
  }
  return uVar4;
}

