
void DmConnClose(undefined1 param_1,ushort param_2,undefined1 param_3)

{
  ushort *puVar1;
  
  puVar1 = (ushort *)WsfMsgAlloc(0x24);
  if (puVar1 != (ushort *)0x0) {
    *(undefined1 *)(puVar1 + 1) = 0x19;
    *puVar1 = param_2 & 0xff;
    *(undefined1 *)(puVar1 + 2) = param_3;
    *(char *)((int)puVar1 + 3) = (char)puVar1[2];
    *(undefined1 *)((int)puVar1 + 5) = param_1;
    WsfMsgSend(*(undefined1 *)(DAT_004b6f20 + 0xc),puVar1);
  }
  return;
}

