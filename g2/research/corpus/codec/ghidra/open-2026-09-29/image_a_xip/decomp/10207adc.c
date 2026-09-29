
undefined4 gx8002_uart_message_start(undefined4 param_1)

{
  int iVar1;
  int iVar2;
  
  iVar1 = gx8002_channel_lookup();
  if (iVar1 != 0) {
    iVar2 = LvpQueueIsEmpty(iVar1 + 0x15c);
    if (iVar2 == 0) {
      *(undefined4 *)(iVar1 + 0x18) = 1;
      LvpQueueGet(iVar1 + 0x15c,iVar1 + 0x3c);
      *(undefined4 *)(iVar1 + 0x174) = 0;
      gx8002_power_lock(*(undefined4 *)(iVar1 + 0x178));
      gx8002_uart_transmit_start
                (*(undefined4 *)(iVar1 + 8),PTR_gx8002_uart_send_callback_10207b34,0);
      return 0;
    }
    *(undefined4 *)(iVar1 + 0x18) = 0;
    gx8002_uart_transmit_stop(param_1);
  }
  return 0xffffffff;
}

