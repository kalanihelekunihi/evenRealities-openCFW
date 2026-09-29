
undefined4
DmRemoteConnParamReqNegReply(byte param_1,undefined1 param_2,undefined4 param_3,undefined4 param_4)

{
  ushort *puVar1;
  
  puVar1 = (ushort *)WsfMsgAlloc(6);
  if (puVar1 != (ushort *)0x0) {
    *(undefined1 *)(puVar1 + 1) = 0x23;
    *puVar1 = (ushort)param_1;
    *(undefined1 *)(puVar1 + 2) = param_2;
    WsfMsgSend(*(undefined1 *)(DAT_004b6f20 + 0xc),puVar1);
  }
  return param_4;
}

