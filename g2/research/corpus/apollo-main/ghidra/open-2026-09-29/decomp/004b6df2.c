
void DmConnReadRssi(byte param_1)

{
  ushort *puVar1;
  
  puVar1 = (ushort *)WsfMsgAlloc(4);
  if (puVar1 != (ushort *)0x0) {
    *(undefined1 *)(puVar1 + 1) = 0x21;
    *puVar1 = (ushort)param_1;
    WsfMsgSend(*(undefined1 *)(DAT_004b6f20 + 0xc),puVar1);
  }
  return;
}

