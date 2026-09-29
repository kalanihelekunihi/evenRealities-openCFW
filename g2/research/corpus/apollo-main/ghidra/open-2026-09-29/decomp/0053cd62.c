
undefined8 aud_message_loop(void)

{
  int iVar1;
  
  while (iVar1 = osMessageQueueGet(*(undefined4 *)(DAT_0053cea4 + 0xc),&stack0xfffffff0,0,0),
        iVar1 == 0) {
    AUD_MessageProcesser(&stack0xfffffff0);
  }
  return 0;
}

