
void gx8002_audio_input_suspend(void)

{
  gx_audio_in_set_interrupt_enable(0x20007,0);
  gx_audio_in_set_interrupt_enable(0x10000,1);
  return;
}

