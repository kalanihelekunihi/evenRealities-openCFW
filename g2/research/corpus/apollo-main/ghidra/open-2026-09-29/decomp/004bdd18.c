
undefined8 APP_EvenOtaDisconnect(void)

{
  byte *pbVar1;
  undefined4 uVar2;
  int iVar3;
  ushort *puVar4;
  undefined4 unaff_r5;
  undefined4 unaff_r6;
  
  iVar3 = FUN_0043d0ce();
  uVar2 = DAT_004bde34;
  if (iVar3 << 0x1e < 0) {
    unaff_r5 = 0xdb;
    FUN_0043d574(4,DAT_004bde0c,DAT_004bde08,DAT_004bde38);
    unaff_r6 = uVar2;
  }
  iVar3 = FUN_0043d0ce();
  if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
    compress_log_output(0x10000000,PTR_s__profile_ota_disconnect_BLE_conn_004bde3c,
                        PTR_s__profile_ota_disconnect_BLE_conn_004bde3c);
  }
  puVar4 = (ushort *)WsfMsgAlloc(0xc);
  if (puVar4 != (ushort *)0x0) {
    *(undefined1 *)(puVar4 + 1) = 0xa1;
    pbVar1 = DAT_004bde14;
    *puVar4 = (ushort)*DAT_004bde14;
    WsfMsgSend(pbVar1[1],puVar4);
  }
  return CONCAT44(unaff_r6,unaff_r5);
}

