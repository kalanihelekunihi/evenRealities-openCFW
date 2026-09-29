
longlong FUN_005f9ff8(undefined4 param_1,undefined4 param_2,undefined2 param_3)

{
  uint unaff_r7;
  
  Thread_SendMsgToRingTaskWithId(param_2,param_3);
  return (ulonglong)unaff_r7 << 0x20;
}

