
longlong nusWriteCallback(void)

{
  uint in_r3;
  undefined2 in_stack_00000000;
  undefined4 in_stack_00000004;
  
  FUN_0043dacc(&DAT_004be9b4,8,in_stack_00000004,in_stack_00000000);
  Thread_SendMsgToBleProductionTask(in_stack_00000004,in_stack_00000000);
  fw_event_loop_remove_delayed(DAT_004be9d0);
  return (ulonglong)in_r3 << 0x20;
}

