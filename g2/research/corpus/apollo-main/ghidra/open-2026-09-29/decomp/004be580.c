
undefined4 APP_BleEfsSendDataMsg(undefined4 param_1,ushort param_2)

{
  byte *pbVar1;
  undefined1 uVar2;
  int iVar3;
  ushort *puVar4;
  
  uVar2 = profile_get_conn_state_byte();
  iVar3 = FUN_0043d0ce();
  if (iVar3 << 0x1e < 0) {
    FUN_0043d574(4,DAT_004be6a4,DAT_004be6a0,DAT_004be6d8,0xd5,DAT_004be6d4,DAT_004be6ac[2],uVar2,
                 *DAT_004be6ac);
  }
  iVar3 = FUN_0043d0ce();
  if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
    compress_log_output(0x10c00000,DAT_004be6dc,DAT_004be6dc,DAT_004be6ac[2],uVar2,*DAT_004be6ac);
  }
  pbVar1 = DAT_004be6ac;
  if (*DAT_004be6ac == 0) {
    return 0;
  }
  if (DAT_004be6ac[2] != 1) {
    return 0;
  }
  thread_ble_wsf_wait_tx_ready();
  puVar4 = (ushort *)WsfMsgAlloc(0xc);
  if (puVar4 == (ushort *)0x0) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(1,DAT_004be6a4,DAT_004be6a0,DAT_004be6d8,0xe6,DAT_004be6e8);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_004be6ec,DAT_004be6ec);
    }
    thread_ble_wsf_tx_complete_notify();
    return 0;
  }
  *(undefined1 *)(puVar4 + 1) = 0xaa;
  *puVar4 = (ushort)*pbVar1;
  *(undefined4 *)(puVar4 + 2) = param_1;
  puVar4[4] = param_2;
  iVar3 = FUN_0043d0ce();
  if (iVar3 << 0x1e < 0) {
    FUN_0043d574(4,DAT_004be6a4,DAT_004be6a0,DAT_004be6d8,0xde,DAT_004be6e0,pbVar1[1]);
  }
  iVar3 = FUN_0043d0ce();
  if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_004be6e4,DAT_004be6e4,pbVar1[1]);
  }
  WsfMsgSend(pbVar1[1],puVar4);
  return 0;
}

