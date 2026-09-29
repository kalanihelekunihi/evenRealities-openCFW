
undefined4 gx8002_uart_message_suspend(void)

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
    }
  } while (uVar2 != 2);
  return 0;
}

