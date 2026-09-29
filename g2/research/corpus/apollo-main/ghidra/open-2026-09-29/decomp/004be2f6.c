
longlong APP_BleEssSendDataMsg(undefined4 param_1,ushort param_2,uint param_3)

{
  byte *pbVar1;
  int iVar2;
  ushort *puVar3;
  
  profile_get_conn_state_byte();
  iVar2 = semantic_OtaTransferActive();
  pbVar1 = DAT_004be38c;
  if (iVar2 == 0) {
    if ((*DAT_004be38c == 0) || (DAT_004be38c[2] != 1)) {
      thread_ble_wsf_tx_complete_notify();
    }
    else {
      puVar3 = (ushort *)WsfMsgAlloc(0xc);
      if (puVar3 == (ushort *)0x0) {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          param_3 = 0xe2;
          FUN_0043d574(1,DAT_004be39c,DAT_004be398,DAT_004be394,0xe2,DAT_004be390);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0x4000000,DAT_004be3a0);
        }
        thread_ble_wsf_tx_complete_notify();
      }
      else {
        *(undefined1 *)(puVar3 + 1) = 0xa9;
        *puVar3 = (ushort)*pbVar1;
        *(undefined4 *)(puVar3 + 2) = param_1;
        puVar3[4] = param_2;
        WsfMsgSend(pbVar1[1],puVar3);
      }
    }
  }
  else {
    thread_ble_wsf_tx_complete_notify();
  }
  return (ulonglong)param_3 << 0x20;
}

