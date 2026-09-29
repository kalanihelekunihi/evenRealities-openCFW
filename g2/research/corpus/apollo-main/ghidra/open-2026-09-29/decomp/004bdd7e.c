
longlong APP_EvenOtaSendDataMsg(undefined4 param_1,ushort param_2,uint param_3)

{
  byte *pbVar1;
  ushort *puVar2;
  int iVar3;
  
  profile_get_conn_state_byte();
  pbVar1 = DAT_004bde14;
  if ((*DAT_004bde14 == 0) || (DAT_004bde14[2] != 1)) goto LAB_004bddf8;
  thread_ble_wsf_wait_tx_ready();
  puVar2 = (ushort *)WsfMsgAlloc(0xc);
  if (puVar2 != (ushort *)0x0) {
    *(undefined1 *)(puVar2 + 1) = 0xa7;
    *puVar2 = (ushort)*pbVar1;
    *(undefined4 *)(puVar2 + 2) = param_1;
    puVar2[4] = param_2;
    WsfMsgSend(pbVar1[1],puVar2);
    goto LAB_004bddf8;
  }
  iVar3 = FUN_0043d0ce();
  if (iVar3 << 0x1e < 0) {
    param_3 = 0x116;
    FUN_0043d574(1,DAT_004bde0c,DAT_004bde08,PTR_s_APP_EvenOtaSendDataMsg_004bde44,0x116,
                 PTR_s_APP_EvenOtaSendDataMsg_WsfMsgAll_004bde40);
  }
  iVar3 = FUN_0043d0ce();
  if (iVar3 << 0x1f < 0) {
LAB_004bdde8:
    compress_log_output(0x4000000,PTR_s__profile_ota_APP_EvenOtaSendData_004bde48);
  }
  else {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1d < 0) goto LAB_004bdde8;
  }
  thread_ble_wsf_tx_complete_notify();
LAB_004bddf8:
  return (ulonglong)param_3 << 0x20;
}

