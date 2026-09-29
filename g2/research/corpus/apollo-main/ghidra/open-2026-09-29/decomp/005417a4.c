
undefined4 uart_sync_receive_callback(undefined4 param_1,undefined4 param_2)

{
  FUN_0057e05e(*DAT_00541a88,param_1,param_2,&stack0xfffffff8);
  osEventFlagsSet(*DAT_00541a8c,1);
  return 0;
}

