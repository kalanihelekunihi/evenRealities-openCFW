
void DmRemoteConnParamReqReply(byte param_1,undefined4 param_2)

{
  ushort *puVar1;
  
  puVar1 = (ushort *)WsfMsgAlloc(0x10);
  if (puVar1 != (ushort *)0x0) {
    *(undefined1 *)(puVar1 + 1) = 0x22;
    *puVar1 = (ushort)param_1;
    FUN_00439be4(puVar1 + 2,param_2,0xc);
    WsfMsgSend(*(undefined1 *)(DAT_004b6f20 + 0xc),puVar1);
  }
  return;
}

