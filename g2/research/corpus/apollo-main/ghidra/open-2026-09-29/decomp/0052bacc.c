
undefined4
DmSecPairRsp(byte param_1,undefined1 param_2,undefined1 param_3,undefined4 param_4,byte param_5)

{
  ushort *puVar1;
  
  puVar1 = (ushort *)WsfMsgAlloc(8);
  if (puVar1 != (ushort *)0x0) {
    *(undefined1 *)(puVar1 + 1) = 2;
    *puVar1 = (ushort)param_1;
    *(undefined1 *)(puVar1 + 2) = param_2;
    *(undefined1 *)((int)puVar1 + 5) = param_3;
    *(byte *)(puVar1 + 3) = (byte)param_4 & 7;
    *(byte *)((int)puVar1 + 7) = param_5 & 7;
    SmpDmMsgSend();
  }
  return param_4;
}

