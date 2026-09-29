
undefined4 UartMessageAsyncInit(uint *param_1)

{
  uint *puVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  undefined *puStack_20;
  undefined *puStack_1c;
  undefined *puStack_18;
  undefined *puStack_14;
  
  if (param_1 != (uint *)0x0) {
    uVar4 = *param_1;
    puVar1 = (uint *)gx8002_channel_lookup(uVar4 & 0xff);
    if ((puVar1 != (uint *)0x0) && ((puVar1[2] = uVar4, puVar1[3] == 0 || (param_1[3] != 0)))) {
      uVar3 = param_1[2];
      if (param_1[2] == 0) {
        uVar3 = uRam1020852c;
      }
      *puVar1 = uVar3;
      puVar1[4] = param_1[1];
      gx8002_uart_transmit_abort(uVar4);
      gx8002_uart_receive_abort(puVar1[2]);
      iVar2 = gx8002_uart_initialize(puVar1[2],puVar1[4]);
      if (iVar2 == 0) {
        iVar2 = gx8002_channel_lookup();
        if (((iVar2 != 0) && (*(int *)(iVar2 + 0xc) == 0)) ||
           ((iVar2 = gx8002_channel_lookup(1), iVar2 != 0 && (*(int *)(iVar2 + 0xc) == 0)))) {
          LvpQueueInit(uRam10208534,uRam10208530,0x100,0x20);
        }
        if (puVar1[3] == 0) {
          LvpQueueInit(puVar1 + 0x57,puVar1 + 0x17,0x100,0x20);
        }
        gx8002_uart_receive_start(puVar1[2],PTR_gx8002_uart_receive_callback_10208538,0);
        puStack_20 = PTR_gx8002_uart_message_suspend_1020853c;
        puStack_1c = PTR_s_UartMessageAsyncSuspend_10208540;
        puStack_18 = PTR_gx8002_uart_message_resume_10208544;
        puStack_14 = PTR_s_UartMessageAsyncResume_10208548;
        gx8002_register_suspend(&puStack_20);
        gx8002_register_resume(&puStack_18);
        gx8002_power_lock_create(puVar1 + 0x5e);
        puVar1[3] = 1;
        return 0;
      }
    }
  }
  return 0xffffffff;
}

