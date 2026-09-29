
undefined4 gx8002_uart_message_resume(void)

{
  undefined *puVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  
  puVar1 = PTR_gx8002_uart_receive_callback_10207ce8;
  uVar4 = 0;
  do {
    iVar2 = gx8002_channel_lookup(uVar4 & 0xff);
    uVar4 = uVar4 + 1;
    if ((iVar2 != 0) && (*(int *)(iVar2 + 0xc) == 1)) {
      gx8002_uart_transmit_abort(*(undefined4 *)(iVar2 + 8));
      gx8002_uart_receive_abort(*(undefined4 *)(iVar2 + 8));
      iVar3 = gx8002_uart_initialize(*(undefined4 *)(iVar2 + 8),*(undefined4 *)(iVar2 + 0x10));
      if (iVar3 != 0) {
        return 0xffffffff;
      }
      gx8002_uart_receive_start(*(undefined4 *)(iVar2 + 8),puVar1,0);
    }
  } while (uVar4 != 2);
  return 0;
}

