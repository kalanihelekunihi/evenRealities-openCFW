
void DmConnSetDataLen(byte param_1,ushort param_2,ushort param_3)

{
  ushort *puVar1;
  
  puVar1 = (ushort *)WsfMsgAlloc(8);
  if (puVar1 != (ushort *)0x0) {
    *(undefined1 *)(puVar1 + 1) = 0x24;
    *puVar1 = (ushort)param_1;
    puVar1[2] = param_2;
    puVar1[3] = param_3;
    WsfMsgSend(*(undefined1 *)(DAT_004b6f20 + 0xc),puVar1);
  }
  return;
}

