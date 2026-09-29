
void DmSecCompareRsp(byte param_1,char param_2)

{
  ushort *puVar1;
  
  puVar1 = (ushort *)WsfMsgAlloc(0x16);
  if (puVar1 != (ushort *)0x0) {
    *puVar1 = (ushort)param_1;
    if (param_2 == '\0') {
      SmpScGetCancelMsgWithReattempt(param_1,puVar1,0xc);
    }
    else {
      *(undefined1 *)(puVar1 + 1) = 0x16;
    }
    SmpDmMsgSend(puVar1);
  }
  return;
}

