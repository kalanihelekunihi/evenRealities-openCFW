
undefined4 DmSecSlaveReq(byte param_1,undefined1 param_2,undefined4 param_3,undefined4 param_4)

{
  ushort *puVar1;
  
  puVar1 = (ushort *)WsfMsgAlloc(6);
  if (puVar1 != (ushort *)0x0) {
    *(undefined1 *)(puVar1 + 1) = 5;
    *puVar1 = (ushort)param_1;
    *(undefined1 *)(puVar1 + 2) = param_2;
    SmpDmMsgSend();
  }
  return param_4;
}

