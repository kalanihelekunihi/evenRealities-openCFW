
void gx8002_i2s_ack(void)

{
  int iVar1;
  undefined1 uStack_5;
  
  iVar1 = iRam10209798;
  *(undefined1 **)(iRam10209798 + 0x10) = &uStack_5;
  uStack_5 = 1;
  *(undefined2 *)(iVar1 + 4) = 0x10f;
  *(undefined1 *)(iVar1 + 7) = 1;
  *(undefined4 *)(iVar1 + 0x18) = 1;
  UartMessageAsyncSend();
  return;
}

