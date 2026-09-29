
longlong APP_BleEusDirectSendDataMsg(undefined4 param_1,ushort param_2,uint param_3)

{
  byte *pbVar1;
  int iVar2;
  ushort *puVar3;
  
  iVar2 = semantic_OtaTransferActive();
  pbVar1 = DAT_004be1e0;
  if (iVar2 == 0) {
    if (((*DAT_004be1e0 != 0) && (DAT_004be1e0[2] == 1)) &&
       (puVar3 = (ushort *)WsfMsgAlloc(0xc), puVar3 != (ushort *)0x0)) {
      *(undefined1 *)(puVar3 + 1) = 0xa8;
      *puVar3 = (ushort)*pbVar1;
      *(undefined4 *)(puVar3 + 2) = param_1;
      puVar3[4] = param_2;
      WsfMsgSend(pbVar1[1]);
    }
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_3 = 0xf6;
      FUN_0043d574(4,DAT_004be1d8,DAT_004be1d4,DAT_004be224,0xf6,DAT_004be200);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_004be208,DAT_004be208);
    }
  }
  return (ulonglong)param_3 << 0x20;
}

