
undefined4 APP_BleEusSendDataMsg(undefined4 param_1,ushort param_2)

{
  byte *pbVar1;
  undefined1 uVar2;
  int iVar3;
  ushort *puVar4;
  
  uVar2 = profile_get_conn_state_byte();
  iVar3 = semantic_OtaTransferActive();
  if (iVar3 == 0) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(4,DAT_004be1d8,DAT_004be1d4,DAT_004be204,0xd8,DAT_004be20c,DAT_004be1e0[2],uVar2,
                   *DAT_004be1e0);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x10c00000,DAT_004be210,DAT_004be210,DAT_004be1e0[2],uVar2,*DAT_004be1e0);
    }
    pbVar1 = DAT_004be1e0;
    if ((*DAT_004be1e0 != 0) && (DAT_004be1e0[2] == 1)) {
      thread_ble_wsf_wait_tx_ready();
      puVar4 = (ushort *)WsfMsgAlloc(0xc);
      if (puVar4 == (ushort *)0x0) {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(1,DAT_004be1d8,DAT_004be1d4,DAT_004be204,0xe9,DAT_004be21c);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x4000000,DAT_004be220,DAT_004be220);
        }
        thread_ble_wsf_tx_complete_notify();
      }
      else {
        *(undefined1 *)(puVar4 + 1) = 0xa8;
        *puVar4 = (ushort)*pbVar1;
        *(undefined4 *)(puVar4 + 2) = param_1;
        puVar4[4] = param_2;
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(4,DAT_004be1d8,DAT_004be1d4,DAT_004be204,0xe1,DAT_004be214,pbVar1[1]);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x10400000,DAT_004be218,DAT_004be218,pbVar1[1]);
        }
        WsfMsgSend(pbVar1[1],puVar4);
      }
    }
  }
  else {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(4,DAT_004be1d8,DAT_004be1d4,DAT_004be204,0xd0,DAT_004be200);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_004be208);
    }
  }
  return 0;
}

