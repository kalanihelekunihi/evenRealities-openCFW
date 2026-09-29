
undefined8 aud_send_codec_dma_message(void)

{
  osKernelGetTickCount();
  AUD_SendMessage(&stack0xfffffff0);
  return 2;
}

