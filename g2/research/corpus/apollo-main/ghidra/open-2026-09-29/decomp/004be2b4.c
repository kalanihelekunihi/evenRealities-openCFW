
longlong essWriteCallback(void)

{
  uint in_r3;
  undefined2 in_stack_00000000;
  undefined4 in_stack_00000004;
  
  FUN_0043dacc(&DAT_004be388,0x10,in_stack_00000004,in_stack_00000000);
  APP_BleEssSendDataMsg(in_stack_00000004,in_stack_00000000);
  return (ulonglong)in_r3 << 0x20;
}

