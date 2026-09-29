
undefined4 UartMessageAsyncDone(void)

{
  int iVar1;
  uint uVar2;
  
  uVar2 = 0;
  do {
    iVar1 = gx8002_channel_lookup(uVar2 & 0xff);
    uVar2 = uVar2 + 1;
    if (iVar1 != 0) {
      gx8002_uart_transmit_abort(*(undefined4 *)(iVar1 + 8));
      gx8002_uart_receive_abort(*(undefined4 *)(iVar1 + 8));
      *(undefined4 *)(iVar1 + 0xc) = 0;
    }
  } while (uVar2 != 2);
  gx8002_memset(uRam10208598,0,0x1c0);
  gx8002_memset(uRam1020859c,0,0x14);
  gx8002_memset(uRam102085a0,0,0x2f8);
  return 0;
}

