
undefined8 input_queue_drain(void)

{
  int iVar1;
  
  while (iVar1 = osMessageQueueGet(*(undefined4 *)(DAT_005134b4 + 0xc),&stack0xfffffff0,0,0),
        iVar1 == 0) {
    INP_MessageProcesser(&stack0xfffffff0);
  }
  return 0;
}

