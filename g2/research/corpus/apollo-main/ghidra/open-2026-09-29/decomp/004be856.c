
undefined4 APP_BleNusSendDataMsg(undefined4 param_1,ushort param_2)

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
      FUN_0043d574(4,DAT_004be9c4,DAT_004be9c0,DAT_004be9e4,0xd2,DAT_004be9ec,DAT_004be9cc[2],uVar2,
                   *DAT_004be9cc);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x10c00000,DAT_004be9f0,DAT_004be9f0,DAT_004be9cc[2],uVar2,*DAT_004be9cc);
    }
    pbVar1 = DAT_004be9cc;
    if ((*DAT_004be9cc != 0) && (DAT_004be9cc[2] == 1)) {
      thread_ble_wsf_wait_tx_ready();
      puVar4 = (ushort *)WsfMsgAlloc(0xc);
      if (puVar4 == (ushort *)0x0) {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(1,DAT_004be9c4,DAT_004be9c0,DAT_004be9e4,0xe3,DAT_004be9fc);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x4000000,DAT_004bea00,DAT_004bea00);
        }
        thread_ble_wsf_tx_complete_notify();
      }
      else {
        *(undefined1 *)(puVar4 + 1) = 0xab;
        *puVar4 = (ushort)*pbVar1;
        *(undefined4 *)(puVar4 + 2) = param_1;
        puVar4[4] = param_2;
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(4,DAT_004be9c4,DAT_004be9c0,DAT_004be9e4,0xdb,DAT_004be9f4,pbVar1[1]);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x10400000,DAT_004be9f8,DAT_004be9f8,pbVar1[1]);
        }
        WsfMsgSend(pbVar1[1],puVar4);
      }
    }
  }
  else {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(4,DAT_004be9c4,DAT_004be9c0,DAT_004be9e4,0xcf,DAT_004be9e0);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_004be9e8);
    }
  }
  return 0;
}

