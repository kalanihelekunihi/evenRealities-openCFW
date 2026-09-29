
undefined4 gx8002_notification_setup(void)

{
  undefined *puVar1;
  undefined1 auStack_18 [16];
  
  gx8002_printf(PTR_s__VC_MESSAGE_NOTIFY_PIN__d_1020974c,2);
  gx_gpio_set_level(2,1);
  gx_gpio_set_direction(2,1);
  gx8002_printf(PTR_s__VC_MESSAGE_MASSAGE_UART__d_10209750,0);
  puVar1 = PTR_s__uartMsgInit_10209754;
  gx8002_printf(uRam10209758,PTR_s__uartMsgInit_10209754,0x1d0);
  UartMessageAsyncDone();
  func_0x10025738(auStack_18,puVar1 + 0x10);
  UartMessageAsyncInit(auStack_18);
  gx8002_app_commands();
  return 0;
}

