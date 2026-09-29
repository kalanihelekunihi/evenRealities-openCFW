
void DmPrivSetAddrResEnable(undefined1 param_1)

{
  undefined2 *puVar1;
  
  puVar1 = (undefined2 *)WsfMsgAlloc(0x2c);
  if (puVar1 != (undefined2 *)0x0) {
    *(undefined1 *)(puVar1 + 1) = 0x34;
    *puVar1 = 0;
    *(undefined1 *)(puVar1 + 2) = param_1;
    WsfMsgSend(*(undefined1 *)(DAT_004d2924 + 0xc),puVar1);
  }
  return;
}

