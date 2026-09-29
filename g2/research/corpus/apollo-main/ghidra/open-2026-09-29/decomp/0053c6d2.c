
undefined8 aud_send_codec_control_message(void)

{
  osKernelGetTickCount();
  AUD_SendMessage(&stack0xfffffff0);
  return 3;
}

